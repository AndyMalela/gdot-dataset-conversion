"""How 137's left-turners leave the stop bar: on their own arrow, on the flashing yellow (permissive), or other.
Field (GDOT Timing & Actuation detector events, train days) vs simulation (same days and 5-min windows, GDOT's plan).
Attempt 5 of VALIDATION.md: calibration target for SUMO's permissive left-turn behaviour, independent of the
Split Monitor statistics used for validation.

    uv run python tools/lanecheck/left_turn_clearance_137.py field            -> table
    uv run python tools/lanecheck/left_turn_clearance_137.py sim [vtype-json] -> table (simulated, same windows)

An activation of a left-turn stop-bar zone ends:
  protected   while the left's own phase is green
  permissive  while its permissive phase (phase_map.json: P1, P5 -> P2; P3 -> P8; P7 -> P4) is green, or within
              6 s after it ends (yellow + red clearance: vehicles finishing the turn; reported separately as
              "after the green")
  other       otherwise (e.g. the vehicle left during red: not expected; JPEG / reading error)
Activations still on at the window end are not classified.
"""
import datetime as dt
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, "tools/lanecheck")
sys.path.insert(0, "tools")

LEFT = {"01.jpg": ("WB_L", 1, 2), "03.jpg": ("NB_L", 3, 8), "05.jpg": ("EB_L", 5, 2), "07.jpg": ("SB_L", 7, 4)}
CH = {1: "ch1", 3: "ch9", 5: "ch19", 7: "ch29"}
PERM = {1: 2, 3: 8, 5: 2, 7: 4}
CLEAR = 6.0
TEST0, TEST1 = "2026-05-18", "2026-05-29"


def classify(off, own, perm):
    if any(a <= off <= b for a, b in own):
        return "protected"
    if any(a <= off <= b for a, b in perm):
        return "permissive"
    if any(b < off <= b + CLEAR for a, b in perm):
        return "permissive_after"
    return "other"


TRAIN1 = "20260417"   # last train weekday (atsc/sites/137/split.json): calibration target from train days only


def windows():
    # the cache also holds validation-day windows fetched for neighbour138/offset_138.py: left out here
    return sorted(d for d in Path("tools/cache/tna_events").glob("137_*_5m_p12345678") if d.name.split("_")[1] <= TRAIN1)


def field():
    from tna_events import read
    tot = defaultdict(Counter)
    for d in windows():
        st0 = dt.datetime.strptime(d.name.split("_")[1] + d.name.split("_")[2], "%Y%m%d%H%M")
        assert not TEST0 <= f"{st0:%Y-%m-%d}" <= TEST1
        greens = {}
        for p in range(1, 9):
            f = d / f"{p:02d}.jpg"
            if f.exists():
                greens[p] = read(f, st0)["green"]
        for f, (col, own, perm) in LEFT.items():
            if not (d / f).exists():
                continue
            r = read(d / f, st0)
            det = [x for x in r["rows"] if x["kind"] == "det"]
            if not det:
                continue
            offs = [o for o in det[0]["off"] if o < 299.0]
            for o in offs:
                tot[col][classify(o, greens.get(own, []), greens.get(perm, []))] += 1
    return tot


def sim(vtype=None):
    sys.path.insert(0, ".")
    from atsc.sim.episode import run_window
    from atsc.sim.signal import ActuatedPolicy, actuated_from_site
    import os
    S = os.environ.get("ATSC_SITE", "atsc/sites/137")
    base = actuated_from_site(S)
    days = defaultdict(list)
    for d in windows():
        st0 = dt.datetime.strptime(d.name.split("_")[1] + d.name.split("_")[2], "%Y%m%d%H%M")
        days[f"{st0:%Y-%m-%d}"].append(st0.hour * 3600 + st0.minute * 60)
    tot = defaultdict(Counter)

    class Rec(ActuatedPolicy):
        def __init__(self):
            super().__init__(base.passage, {k: list(v) for k, v in base.max_recall.items()})
            self.log = []

        def end_requests(self, sig):
            disp = sig.engine.display()
            occ = {p: sig.conn.lanearea.getLastStepVehicleNumber(ch) > 0 for p, ch in CH.items()}
            self.log.append((sig.now, {p for p, v in disp.items() if v == "G"}, occ))
            return super().end_requests(sig)

    for day, starts in sorted(days.items()):
        pol = Rec()
        run_window(S, day, 6.5, 21.0, pol, mode="plan", seed=1, vtype=vtype, drain_s=0)
        log = pol.log
        for p, ch in CH.items():
            col = {1: "WB_L", 3: "NB_L", 5: "EB_L", 7: "SB_L"}[p]
            prev = False
            perm_end = -1e9
            for t, green, occ in log:
                if PERM[p] in green:
                    perm_end = t
                if prev and not occ[p] and any(s <= t < s + 299 for s in starts):
                    if p in green:
                        tot[col]["protected"] += 1
                    elif PERM[p] in green:
                        tot[col]["permissive"] += 1
                    elif t - perm_end <= CLEAR:
                        tot[col]["permissive_after"] += 1
                    else:
                        tot[col]["other"] += 1
                prev = occ[p]
    return tot


def show(tot, label):
    print(f"{label}: activations ending ... (share)")
    print("| left turn | n | protected | permissive | of which after the green (<= 6 s) | other | permissive share |")
    print("|---|---|---|---|---|---|---|")
    for col in ("WB_L", "EB_L", "NB_L", "SB_L"):
        c = tot[col]
        n = sum(c.values())
        if n:
            pm = c['permissive'] + c['permissive_after']
            print(f"| {col} | {n} | {c['protected'] / n:.0%} | {pm / n:.0%} | {c['permissive_after'] / n:.0%} | "
                  f"{c['other'] / n:.0%} | {pm / max(pm + c['protected'], 1):.2f} |")


if __name__ == "__main__":
    if sys.argv[1] == "field":
        show(field(), "field")
    else:
        vt = json.loads(sys.argv[2]) if len(sys.argv) > 2 else None
        show(sim(vt), f"simulation {vt or 'site vtype'}")
