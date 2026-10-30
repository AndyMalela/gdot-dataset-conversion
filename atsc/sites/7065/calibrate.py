"""Phase 1.5: discharge calibration of the SUMO driver model on train weekdays (PM plan C, 15:30-19:00).

GDOT's count zones sit near the stop line (Matrix radar), so a count is a vehicle the real intersection
served. Criterion: the least generous driver parameters (one vType for every approach) with which the
simulation, under GDOT's own plans, also serves the counted Piedmont-N through flow (P8, the critical
movement). Reported against the field: P8 discharge per lane of green per 15-min quarter.

    uv run python atsc/sites/7065/calibrate.py            # grid -> calibration/grid.csv, calibration/quarters.csv
"""
import csv
import itertools
import json
import sys
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
from atsc.sim.demand import day_quality, day_set, load_counts, schedule  # noqa: E402

BEGIN, END = 15.5, 19.0
# (vType attributes, step length s). tau < step length is not collision-free in SUMO's Krauss model.
GRID = ([({"sigma": s, "tau": 1.0}, 1.0) for s in (0.5, 0.3, 0.2, 0.1, 0.0)]
        + [({"sigma": 0.2, "tau": 1.0, "minGap": g}, 1.0) for g in (2.0, 1.5)]
        + [({"sigma": 0.2, "tau": t}, 0.5) for t in (1.0, 0.8, 0.7)]
        + [({"sigma": s, "tau": t}, 0.5) for s, t in ((0.5, 0.9), (0.5, 0.8), (0.3, 0.9), (0.3, 0.8), (0.2, 0.9))])
LANES8 = 2


def days(set_name="train"):
    split = json.loads((HERE / "split.json").read_text())
    cnt = load_counts(HERE)
    return [d for d in sorted(cnt) if day_set(split, d) == set_name and d.weekday() < 5
            and str(d) not in split["holidays"] and day_quality(cnt[d])[0] == "complete"]


def plan_c_quarters(date):
    sig = json.loads((HERE / "signal.json").read_text())
    sch = schedule(sig, date)
    name = lambda t: [n for t0, n in sch if t0 <= t][-1]
    return [q for q in range(int(BEGIN * 3600), int(END * 3600), 900) if name(q) == "C" and name(q + 899) == "C"]


def job(args):
    from atsc.sim.episode import run_window
    from atsc.sim.signal import ActuatedPolicy
    date, vt, step = args
    r = run_window(HERE, str(date), BEGIN, END, ActuatedPolicy(2.0), vtype=vt, step=step)
    tag = {**vt, "step": step}
    g8 = [(g["start"], g["end"]) for g in r["greens"] if g["phase"] == 8]
    rows = []
    for q in plan_c_quarters(date):
        served = sum(q <= t < q + 900 for t in r["crossings"].get("EB_T", []))
        green = sum(max(0.0, min(e, q + 900) - max(s, q)) for s, e in g8)
        rows.append({"date": date, **tag, "quarter": q, "served": served, "green_s": round(green, 1)})
    d8 = r["delay"]["EB_T"]
    summ = {"date": date, **tag, "delay_all_s": round(r["delay_all_s"], 1),
            "delay_EB_T_s": round(d8["mean_s"], 1), "EB_T_veh": d8["veh"], "EB_T_unfinished": d8["unfinished"],
            "backlog_EB_T": r["backlog_max"].get("EB_T", 0), "teleports": r["teleports"],
            **{f"delay_{c}_s": round(v["mean_s"], 1) for c, v in r["delay"].items() if c != "EB_T" and v["mean_s"] is not None}}
    return summ, rows


def field_quarters(ds):
    cnt = load_counts(HERE)
    out = []
    for d in ds:
        by = {b.t: b for b in cnt[d]}
        for q in plan_c_quarters(d):
            bs = [by.get(q + 300 * k) for k in range(3)]
            if all(b is not None and b.status == "ok" for b in bs):
                out.append({"date": d, "quarter": q, "count": sum(b.counts["EB_T"] for b in bs)})
    return out


def main():
    ds = days("train")
    out = HERE / "calibration"
    out.mkdir(exist_ok=True)
    done = set()
    if (out / "grid.csv").exists():                 # resume: keep finished runs
        old = list(csv.DictReader(open(out / "grid.csv")))
        done = {(r["date"], r["sigma"], r["tau"], r.get("minGap") or "", r["step"]) for r in old}
    key = lambda d, vt, st: (str(d), str(vt["sigma"]), str(vt["tau"]), str(vt.get("minGap", "")), str(st))
    grid = [(d, vt, st) for d, (vt, st) in itertools.product(ds, GRID) if key(d, vt, st) not in done]
    print(f"{len(ds)} train weekdays x {len(GRID)} parameter sets = {len(grid)} runs")
    with Pool(22) as pool:
        res = pool.map(job, grid, chunksize=1)
    summ = [s for s, _ in res]
    quarters = [r for _, rows in res for r in rows]
    if done:
        summ = old + summ
        quarters = list(csv.DictReader(open(out / "quarters.csv"))) + quarters
    for name, rows in [("grid.csv", summ), ("quarters.csv", quarters), ("field_quarters.csv", field_quarters(ds))]:
        keys = list(dict.fromkeys(k for r in rows for k in r))
        with open(out / name, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(rows)
    print(f"wrote {out}/grid.csv, quarters.csv, field_quarters.csv")


if __name__ == "__main__":
    main()
