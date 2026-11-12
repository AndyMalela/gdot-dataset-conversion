"""Stage 1 of the demand correction (OPEN_ISSUES.md B2): does the simulation carry the corrected Peachtree demand?

    uv run python atsc/sites/7065/load_check.py            -> debug/load_check.csv, printed table

Full days, rule controllers only (no training needed), corrected counts and the report as exported side by side.
Per run: vehicles, mean delay, teleports, vehicles unfinished at the end, most vehicles waiting to enter per
movement (backlog), wall time.
"""
import csv, os, sys, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2])); sys.path.insert(0, str(HERE))
DAYS = ["2026-09-14", "2026-09-16", "2026-09-23"]
CTRL = ["gdot", "actuated", "maxpressure"]

def job(a):
    counts, date, ctrl = a
    if counts == "report":
        os.environ["ATSC_COUNTS"] = "report"
    else:
        os.environ.pop("ATSC_COUNTS", None)
    from evaluate import policy
    from atsc.sim.episode import run_window
    t0 = time.time()
    pol, kw = policy(ctrl)
    r = run_window(HERE, date, 0.0, 24.0, pol, seed=1, warmup_s=0, **kw)
    row = {"counts": counts, "date": date, "controller": ctrl, "veh": r["vehicles"], "delay_s": round(r["delay_all_s"], 1),
           "teleports": r["teleports"], "unfinished": sum(m["unfinished"] for m in r["delay"].values()), "wall_s": round(time.time() - t0)}
    for c, m in r["delay"].items():
        row[c + "_delay"] = round(m["mean_s"], 1) if m["mean_s"] is not None else ""
        row[c + "_backlog"] = r["backlog_max"].get(c, 0)
    return row

if __name__ == "__main__":
    jobs = [(k, d, c) for k in ("upstream", "report") for d in DAYS for c in CTRL]
    with ProcessPoolExecutor(18) as pool:
        rows = list(pool.map(job, jobs))
    out = HERE / "debug"; out.mkdir(exist_ok=True)
    with open(out / "load_check.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    for r in rows:
        print({k: v for k, v in r.items()})
