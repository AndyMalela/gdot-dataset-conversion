"""Webster fixed-time baseline (paper Appendix A.1) for the 7065 twin.

Pretimed plan over the four concurrent stages EW_THRU / EW_LEFT / NS_THRU /
NS_LEFT (the single-approach stages are an RL-only flexibility), with
delay-optimised cycle time C = (1.5 L + 5) / (1 - rho)  [Webster 1958].

Assumptions (documented, same spirit as the paper's Appendix A):
  saturation flow 1800 veh/h/lane; lost time per stage = 2 s start-up +
  yellow + all-red - 2 s of yellow utilised = 7 s -> L = 28 s/cycle;
  cycle capped to [40, 180] s (urban practice) since Webster diverges as
  rho -> 1 -- and this intersection's AM peak really does approach that.

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

SAT_FLOW = 1800.0  # veh/h/lane
LOST_PER_STAGE = 7.0
FIXED_STAGES = [0, 1, 4, 5]  # EW_THRU, EW_LEFT, NS_THRU, NS_LEFT
# lanes serving each stage's critical movements (from stages.LINKS)
STAGE_LANES = {
    0: [("eb", "thru", 3), ("wb", "thru", 3)],
    1: [("eb", "left", 2), ("wb", "left", 2)],
    4: [("nb", "thru", 2), ("sb", "thru", 2)],
    5: [("nb", "left", 1), ("sb", "left", 1)],
}


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
    for stg, movements in STAGE_LANES.items():
        y[stg] = max(vol[(a, mv)] / (SAT_FLOW * lanes) for a, mv, lanes in movements)
    L = LOST_PER_STAGE * len(FIXED_STAGES)
    rho = sum(y.values())
    if rho >= 0.95:
        cycle = 180.0
    else:
        cycle = (1.5 * L + 5.0) / (1.0 - rho)
    cycle = min(max(cycle, 40.0), 180.0)
    green_budget = cycle - len(FIXED_STAGES) * st.INTERSTAGE
    greens = {stg: max(5.0, green_budget * y[stg] / rho) for stg in FIXED_STAGES}
    return cycle, rho, greens


def run_fixed(rou_xml: str, greens: dict, begin: int, end: int,
              tripinfo: str, seed: int = 42) -> metrics.TripMetrics:
    env = Sig7065Env(rou_xml, begin=begin, end=end, seed=seed,
                     label="fixed", tripinfo=tripinfo)
    env.reset()
    done = False
    idx = 0
    while not done:
        stg = FIXED_STAGES[idx % len(FIXED_STAGES)]
        # extend current stage to its green duration (env min-green counts
        # as the first 3 s), then move on
        elapsed = st.MIN_GREEN if env.stage == stg else 0.0
        if env.stage != stg:
            res = env.step(stg)          # change (interstage + min green)
            done = res.done
            elapsed = st.MIN_GREEN
        while not done and elapsed < greens[stg]:
            res = env.step(stg)          # extend 1 s
            done = res.done
            elapsed += st.DELTA
        idx += 1
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
    for stg, g in greens.items():
        print(f"  {st.STAGE_NAMES[stg]:8s} green {g:5.1f}s")

    ti = f"{here}/{args.out}/tripinfo_fixed_{args.date}.xml"
    m = run_fixed(rou, greens, args.begin, args.end, ti)
    print(f"fixed-time result: {m.row()}")
