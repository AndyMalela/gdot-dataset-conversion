"""Gate check after stage 2 (OPEN_ISSUES.md B2): are the Webster / MaxPressure collapses on corrected demand caused
by where vehicles are inserted? Same days and controllers with departLane "random" (current) and "sorted"
(a random lane among those that lead to the vehicle's movement without a lane change).

    uv run python atsc/sites/7065/lane_check.py            -> debug/lane_check.csv, printed table
"""
import csv, os, sys, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2])); sys.path.insert(0, str(HERE))
DAYS = ["2026-09-16", "2026-09-23"]
CTRL = ["gdot", "actuated", "webster", "maxpressure"]

def job(a):
    lane, date, ctrl = a
    os.environ["ATSC_DEPART_LANE"] = lane
    from evaluate import policy
    from atsc.sim.episode import run_window
    t0 = time.time()
    pol, kw = policy(ctrl)
    r = run_window(HERE, date, 0.0, 24.0, pol, seed=1, warmup_s=0, **kw)
    row = {"depart_lane": lane, "date": date, "controller": ctrl, "veh": r["vehicles"], "delay_s": round(r["delay_all_s"], 1),
           "teleports": r["teleports"], "wall_s": round(time.time() - t0)}
    for c, m in r["delay"].items():
        row[c + "_delay"] = round(m["mean_s"], 1) if m["mean_s"] is not None else ""
        row[c + "_backlog"] = r["backlog_max"].get(c, 0)
    return row

if __name__ == "__main__":
    jobs = [(k, d, c) for k in ("random", "sorted") for d in DAYS for c in CTRL]
    with ProcessPoolExecutor(16) as pool:
        rows = list(pool.map(job, jobs))
    out = HERE / "debug"; out.mkdir(exist_ok=True)
    with open(out / "lane_check.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    mv = ["NB_L", "NB_T", "SB_L", "SB_T", "EB_L", "EB_T", "WB_L", "WB_T"]
    for r in rows:
        print(f"{r['depart_lane']:6} {r['date']} {r['controller']:11} delay {r['delay_s']:6} tele {r['teleports']:3} | " +
              " ".join(f"{m}:{r[m + '_delay']:.0f}/{r[m + '_backlog']}" for m in mv))
