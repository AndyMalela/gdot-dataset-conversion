"""Engine rule tests (no SUMO).  uv run python -m pytest atsc/tests -q"""
import math

from atsc.sim.nema import NemaEngine, Phase, Plan

RINGS = {1: ((2, 1), (3, 4)), 2: ((5, 6), (7, 8))}          # 7065 service order: P2 leads P1
Y = {1: 4.5, 2: 3.1, 3: 3.7, 4: 3.6, 5: 4.2, 6: 3.3, 7: 3.0, 8: 3.6}
R = {1: 2.8, 2: 2.6, 3: 2.9, 4: 3.0, 5: 3.0, 6: 3.0, 7: 3.2, 8: 3.0}
PLAN_A = Plan("A", 160, {1: 35, 2: 50, 3: 25, 4: 50, 5: 33, 6: 52, 7: 15, 8: 60})


def phases(max_green=math.inf):
    return {p: Phase(min_green=5, yellow=Y[p], red=R[p], max_green=max_green, recall=p in (2, 4, 6, 8))
            for p in range(1, 9)}


def run(eng, seconds, calls=lambda t: set(range(1, 9)), ends=lambda t, e: set(), dt=0.1):
    t, log = 0.0, []
    while t <= seconds + 1e-9:
        log.append((t, eng.tick(t, calls(t), ends(t, eng))))
        t = round(t + dt, 6)
    return log


def conflicts(disp):
    """phases shown green together must be in different rings and the same barrier group."""
    g = [p for p, c in disp.items() if c == "G"]
    grp = lambda p: 0 if p in (1, 2, 5, 6) else 1
    ring = lambda p: 1 if p <= 4 else 2
    return len(g) == 2 and (ring(g[0]) == ring(g[1]) or grp(g[0]) != grp(g[1]))


def test_coordinated_all_called_reproduces_splits():
    eng = NemaEngine(RINGS, phases(), PLAN_A)
    log = run(eng, 3 * 160)
    assert not any(conflicts(d) for _, d in log)
    full = [g for g in eng.greens if g.start >= 160 and g.end <= 320]       # one whole cycle
    got = {g.phase: round(g.green + Y[g.phase] + R[g.phase], 1) for g in full}
    assert got == {p: float(s) for p, s in PLAN_A.splits.items()}, got
    assert all(g.how == "force" for g in full)
    starts = eng.cycle_starts
    assert all(abs((b - a) - 160) < 0.15 for a, b in zip(starts[1:], starts[2:]))


def test_coordinated_phase_never_gaps_out():
    eng = NemaEngine(RINGS, phases(), PLAN_A)
    run(eng, 400, ends=lambda t, e: {1, 2})                                    # always asking to end
    for g in eng.greens:
        if g.phase in (2, 6):
            assert g.how in ("force", "rest-end", "gap") and g.green > 20, g


def test_gap_out_gives_time_to_next_phase_and_cycle_stays_fixed():
    eng = NemaEngine(RINGS, phases(), PLAN_A)
    # P3 (ring 1 leading left) asks to end as soon as allowed
    run(eng, 4 * 160, ends=lambda t, e: {1} if 1 in e.r and e.r[1].phase == 3 else set())
    p3 = [g for g in eng.greens if g.phase == 3 and g.start > 160]
    p4 = [g for g in eng.greens if g.phase == 4 and g.start > 160]
    assert all(abs(g.green - 5) < 0.15 and g.how == "gap" for g in p3)
    assert all(g.green > 50 - Y[4] - R[4] + 10 for g in p4)                    # P4 absorbs P3's time
    starts = eng.cycle_starts
    assert all(abs((b - a) - 160) < 0.15 for a, b in zip(starts[1:], starts[2:]))


def test_uncalled_left_is_skipped_and_partner_holds_to_group_end():
    eng = NemaEngine(RINGS, phases(), PLAN_A)
    run(eng, 3 * 160, calls=lambda t: {2, 3, 4, 5, 6, 7, 8})                  # P1 never called
    assert not any(g.phase == 1 for g in eng.greens)
    p2 = [g for g in eng.greens if g.phase == 2 and g.start >= 160 and g.end <= 320]
    assert abs(p2[0].green - (85 - Y[2] - R[2])) < 0.15, p2


def test_free_mode_max_out_and_min_green_with_peds():
    ph = phases(max_green=30)
    ph[4].ped_min = 7 + 29.9
    eng = NemaEngine(RINGS, ph, None)
    run(eng, 600, ends=lambda t, e: {1, 2})                                    # always asking to end
    p4 = [g for g in eng.greens if g.phase == 4]
    assert p4 and all(g.green >= 36.9 - 0.15 for g in p4)                      # ped minimum wins
    assert all(g.green <= max(30, ph[g.phase].min_service()) + 0.15 for g in eng.greens if g.how == "max")
    eng2 = NemaEngine(RINGS, phases(max_green=30), None)
    run(eng2, 600)                                                             # never asks: max-out
    assert all(abs(g.green - 30) < 0.15 for g in eng2.greens if g.how == "max")
    assert any(g.how == "max" for g in eng2.greens)


def test_clearance_follows_every_green():
    eng = NemaEngine(RINGS, phases(), PLAN_A)
    log = run(eng, 2 * 160)
    for p in range(1, 9):
        shown = [d.get(p) for _, d in log]
        for i in range(1, len(shown)):
            if shown[i - 1] == "G" and shown[i] not in ("G", None):
                assert shown[i] == "y"
            if shown[i - 1] == "G" and shown[i] is None:
                raise AssertionError(f"P{p} went G -> dark without yellow at step {i}")


def test_zero_split_phase_is_never_served_even_fixed_time():
    plan_e = Plan("E", 120, {1: 20, 2: 50, 3: 0, 4: 50, 5: 20, 6: 50, 7: 0, 8: 50})
    eng = NemaEngine(RINGS, phases(), plan_e, skip_uncalled=False)
    log = run(eng, 3 * 120)
    assert not any(g.phase in (3, 7) for g in eng.greens)
    assert not any(conflicts(d) for _, d in log)
    full = [g for g in eng.greens if g.start >= 120 and g.end <= 240]
    got = {g.phase: round(g.green + Y[g.phase] + R[g.phase], 1) for g in full}
    assert got == {1: 20.0, 2: 50.0, 4: 50.0, 5: 20.0, 6: 50.0, 8: 50.0}, got


def test_late_start_with_ped_min_filling_split_keeps_cycle():
    # 7065 plan B: P4's split (43) is exactly its ped minimum + clearance; with 0.5/1 s steps P4 starts
    # late after a full P3, and the cycle must still be 160 s (regression: it used to double to 320 s)
    plan_b = Plan("B", 160, {1: 33, 2: 60, 3: 24, 4: 43, 5: 37, 6: 56, 7: 15, 8: 52})
    for step in (0.5, 1.0):
        ph = phases()
        ph[4].ped_min = 43 - Y[4] - R[4]
        eng = NemaEngine(RINGS, ph, plan_b)
        run(eng, 6 * 160, dt=step)
        starts = eng.cycle_starts
        assert all(abs((b - a) - 160) <= step + 1e-6 for a, b in zip(starts[1:], starts[2:])), starts
        p4 = [g for g in eng.greens if g.phase == 4 and g.start > 160]
        assert all(g.green >= ph[4].ped_min - 1e-6 for g in p4)
