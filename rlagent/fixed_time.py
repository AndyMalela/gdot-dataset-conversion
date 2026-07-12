"""Webster fixed-time baseline (paper Appendix A.1) for the 7065 twin.

Pretimed plan over the real 4-phase ring-barrier cycle
EW_LEFT -> EW_THRU -> NS_LEFT -> NS_THRU (stages.PHASES, in that order),
with delay-optimised cycle time C = (1.5 L + 5) / (1 - rho)  [Webster 1958].

This is the correct comparator for the redesigned action space: it runs on
the *same* env, so it inherits the same realistic phases (FYA permissive
lefts, protected right overlaps) and the same selective interstage
clearance the RL agent sees -- the two controllers differ only in *when*
they advance, which is exactly the thing under study. A fixed-time plan and
an actuated one share the phase hardware; only the timing policy differs.

Assumptions (documented, same spirit as the paper's Appendix A):
  saturation flow 1800 veh/h/lane; per-cycle lost time L is computed from
  the phases that ACTUALLY clear (2 s start-up per phase + the real
  yellow+all-red on each barrier crossing - 2 s of yellow utilised) rather
  than assuming all four transitions clear -- with selective clearance only
  the two THRU->LEFT barrier crossings insert an interstage, the two
  lead-left->through transitions insert none (see stages.transition). Cycle
  capped to [40, 180] s (urban practice) since Webster diverges as rho -> 1
  -- and this intersection's PM peak really does approach that.

Volumes come from the same portal data.txt that built the demand (peak
rolling hour within the evaluated window), so baseline and demand are
consistent by construction.
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "sumodemand"))
import portal_report  # noqa: E402

import metrics  # noqa: E402
import stages as st  # noqa: E402
from sumo_env import Sig7065Env  # noqa: E402

SAT_FLOW = 1800.0    # veh/h/lane
STARTUP_LOST = 2.0   # start-up lost time per phase
YELLOW_USED = 2.0    # seconds of yellow effectively used as green
FIXED_PHASES = [0, 1, 2, 3]  # EW_LEFT, EW_THRU, NS_LEFT, NS_THRU (cycle order)
# lanes serving each phase's critical movements (from stages.LINKS)
PHASE_LANES = {
    0: [("eb", "left", 2), ("wb", "left", 2)],
    1: [("eb", "thru", 3), ("wb", "thru", 3)],
    2: [("nb", "left", 1), ("sb", "left", 1)],
    3: [("nb", "thru", 2), ("sb", "thru", 2)],
}


def cycle_clearance() -> float:
    """Total interstage (yellow+all-red) seconds the env inserts over one
    full cycle -- only transitions that actually clear count (barrier
    crossings), matching stages.transition / the RL env exactly."""
    return sum(
        st.INTERSTAGE
        for i in range(st.N_PHASES)
        if st.transition(i, (i + 1) % st.N_PHASES) is not None
    )


def cycle_lost_time() -> float:
    """Webster L: start-up loss on every phase + clearance loss (all-red +
    the unused part of yellow) on each clearing transition."""
    clearing = sum(
        1 for i in range(st.N_PHASES)
        if st.transition(i, (i + 1) % st.N_PHASES) is not None
    )
    return (STARTUP_LOST * st.N_PHASES
            + clearing * (st.ALL_RED + (st.YELLOW - YELLOW_USED)))


def peak_hour_volumes(date: str, begin: int, end: int):
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rep = portal_report.parse_report(
        portal_report.Path(f"{repo}/data/7065/{date}data.txt"))
    out = {}
    for (a, mv), bins in rep.counts.items():
        times = sorted(t for t in bins if begin <= t < end)
        best = 0
        for i, t in enumerate(times):
            if i + 12 <= len(times):
                best = max(best, sum(bins[times[j]] for j in range(i, i + 12)))
        out[(a, mv)] = best
    return out


def webster_plan(date: str, begin: int, end: int):
    vol = peak_hour_volumes(date, begin, end)
    y = {}
    for ph, movements in PHASE_LANES.items():
        y[ph] = max(vol[(a, mv)] / (SAT_FLOW * lanes) for a, mv, lanes in movements)
    L = cycle_lost_time()
    rho = sum(y.values())
    if rho <= 0.0:
        raise ValueError(
            f"degenerate Webster plan (rho=0): no full peak hour of volume in "
            f"[{begin},{end}) -- the rolling-hour calc needs >=12 five-min bins. "
            f"Use a window of at least ~1 h.")
    if rho >= 0.95:
        cycle = 180.0
    else:
        cycle = (1.5 * L + 5.0) / (1.0 - rho)
    cycle = min(max(cycle, 40.0), 180.0)
    green_budget = cycle - cycle_clearance()
    greens = {ph: max(5.0, green_budget * y[ph] / rho) for ph in FIXED_PHASES}
    return cycle, rho, greens


def run_fixed(rou_xml: str, greens: dict, begin: int, end: int,
              tripinfo: str, seed: int = 42,
              scale: float = 1.0) -> metrics.TripMetrics:
    """Drive the fixed cycle by holding each phase for its Webster green then
    advancing. The env starts in phase 0 with min green already served, so
    phase_elapsed is the natural clock; advancing wraps 0->1->2->3->0.
    `scale` multiplies demand (must be forwarded for scaled evals -- omitting
    it silently runs at 1.0x regardless of the caller's intent)."""
    env = Sig7065Env(rou_xml, begin=begin, end=end, seed=seed,
                     label="fixed", tripinfo=tripinfo, scale=scale)
    env.reset()
    done = False
    while not done:
        target = greens[env.phase]
        while not done and env.phase_elapsed < target:
            res = env.step(st.EXTEND)
            done = res.done
        if not done:
            res = env.step(st.ADVANCE)
            done = res.done
    env.close()
    return metrics.read_tripinfo(tripinfo)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--date", default="0507")
    p.add_argument("--begin", type=int, default=25200)   # 07:00
    p.add_argument("--end", type=int, default=32400)     # 09:00
    p.add_argument("--out", default="results")
    args = p.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(f"{here}/{args.out}", exist_ok=True)
    rou = f"{here}/../sumodemand/{args.date}.rou.xml"

    cycle, rho, greens = webster_plan(args.date, args.begin, args.end)
    print(f"Webster plan ({args.date}, window {args.begin}-{args.end}): "
          f"rho={rho:.3f}  cycle={cycle:.1f}s")
    for ph, g in greens.items():
        print(f"  {st.PHASE_NAMES[ph]:8s} green {g:5.1f}s")

    ti = f"{here}/{args.out}/tripinfo_fixed_{args.date}.xml"
    m = run_fixed(rou, greens, args.begin, args.end, ti)
    print(f"fixed-time result: {m.row()}")
