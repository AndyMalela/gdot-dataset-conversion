"""Phase 2 baselines on the validated simulation: every controller runs on the same NEMA engine, detectors,
demand and driver model, so differences come from the decision only.

    uv run python atsc/sites/7065/baselines.py design      # Webster plans from TRAIN weekdays -> baselines/webster.json
    uv run python atsc/sites/7065/baselines.py run         # validation weekdays, full day -> baselines/runs.csv, hourly.csv
    uv run python atsc/sites/7065/baselines.py report      # tables -> baselines/report.md

Controllers
  gdot      GDOT's own time-of-day plans (coordinated-actuated: fixed force-offs, side phases gap out)
  actuated  fully actuated, no cycle: gap-out, max green = the largest green any GDOT plan gives the phase
  webster   pretimed Webster plans per GDOT time-of-day period (design hour from train days), no skipping
"""
import csv
import json
import statistics as st
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
from atsc.sim.demand import day_quality, day_set, load_counts  # noqa: E402

OUT = HERE / "baselines"
PERIODS = [("00:00", "E"), ("06:15", "A"), ("13:30", "B"), ("15:30", "C"), ("19:00", "B2"), ("19:30", "D"), ("21:45", "E2")]
CONTROLLERS = ("gdot", "actuated", "webster")


def hhmm(t):
    return int(t[:2]) * 3600 + int(t[3:]) * 60


def days(set_name):
    split = json.loads((HERE / "split.json").read_text())
    cnt = load_counts(HERE)
    return [d for d in sorted(cnt) if day_set(split, d) == set_name and d.weekday() < 5
            and str(d) not in split["holidays"] and day_quality(cnt[d])[0] in ("complete", "usable")]


def design():
    from atsc.sim.webster import design as webster
    sig = json.loads((HERE / "signal.json").read_text())
    mv = json.loads((HERE / "movements.json").read_text())["movements"]
    cal = json.loads((HERE / "sim.json").read_text())
    s_lane = 1950                           # calibrated discharge per lane of green (CALIBRATION.md)
    cnt = load_counts(HERE)
    ds = days("train")
    # median over train weekdays of each movement's 5-min count
    prof = defaultdict(list)
    for d in ds:
        for b in cnt[d]:
            if b.status == "ok":
                for c, n in b.counts.items():
                    prof[(b.t, c)].append(n)
    med = {k: st.median(v) for k, v in prof.items()}
    bounds = [hhmm(t) for t, _ in PERIODS] + [86400]
    plans, notes = [], {}
    for i, (t0, name) in enumerate(PERIODS):
        a, b = bounds[i], bounds[i + 1]
        # design hour: the busiest rolling hour (all movements) inside the period, or the whole period if shorter
        starts = range(a, max(a + 1, b - 3600 + 1), 300)
        def tot(s):
            return sum(med.get((t, c), 0) for t in range(s, min(s + 3600, b), 300) for c in mv)
        s_best = max(starts, key=tot)
        span = min(3600, b - s_best)
        flow = defaultdict(float)
        for c, m in mv.items():
            q = sum(med.get((t, c), 0) for t in range(s_best, s_best + span, 300)) * 3600 / span
            flow[m["phases"][0]] += q
        lanes = {m["phases"][0]: m["lanes"] for m in mv.values()}
        plan, info = webster(sig, dict(flow), lanes, s_lane, name=f"W-{name}")
        plans.append({"start": t0, "name": plan.name, "cycle": plan.cycle, "splits": plan.splits,
                      "design_hour_start": f"{s_best // 3600:02d}:{s_best % 3600 // 60:02d}", **info,
                      "flow_veh_h": {p: round(v) for p, v in sorted(flow.items())}})
        print(f"{plan.name:5s} from {t0}: cycle {plan.cycle:5.1f}  Y {info['Y']:.2f}  C0 {info['C0']:5.1f}  "
              f"splits {plan.splits}")
    OUT.mkdir(exist_ok=True)
    (OUT / "webster.json").write_text(json.dumps({
        "source": f"designed from {len(ds)} train weekdays (median 5-min counts), s = {s_lane} veh/h/lane "
                  "(calibrated), GDOT clearances and minimum services incl. pedestrian walk + FDW every cycle",
        "vtype": cal["vtype"], "plans": plans}, indent=1))


def webster_schedule():
    from atsc.sim.nema import Plan
    w = json.loads((OUT / "webster.json").read_text())
    return [(hhmm(p["start"]), Plan(p["name"], p["cycle"], {int(k): v for k, v in p["splits"].items()}, ()))
            for p in w["plans"]]


def safe_job(args):
    """a failed day is reported and skipped instead of stopping the whole pool."""
    try:
        return job(args)
    except Exception as e:                      # noqa: BLE001
        import traceback
        print(f"FAILED {args[:2]}: {e}\n{traceback.format_exc()}", file=sys.stderr, flush=True)
        return None


def job(args):
    from atsc.sim.episode import run_window
    from atsc.sim.signal import FixedPolicy, actuated_from_site
    date, ctrl = args
    kw = {"warmup_s": 0}
    if ctrl == "gdot":
        r = run_window(HERE, str(date), 0.0, 24.0, actuated_from_site(HERE), mode="plan", **kw)
    elif ctrl == "actuated":        # same fitted passage times; no plan, so no recall
        r = run_window(HERE, str(date), 0.0, 24.0, actuated_from_site(HERE), mode="free", **kw)
    else:
        r = run_window(HERE, str(date), 0.0, 24.0, FixedPolicy(), mode="schedule", schedule=webster_schedule(),
                       skip_uncalled=False, **kw)
    row = {"date": str(date), "controller": ctrl, "vehicles": r["vehicles"], "delay_all_s": round(r["delay_all_s"], 2),
           "teleports": r["teleports"], **{f"delay_{c}_s": round(v["mean_s"], 1) for c, v in r["delay"].items()},
           **{f"backlog_{c}": v for c, v in r["backlog_max"].items()}}
    hourly = [{"date": str(date), "controller": ctrl, "hour": h, "delay_sum_s": round(v[0], 1), "vehicles": v[1]}
              for h, v in r["delay_by_hour"].items()]
    return row, hourly


def write(name, rows):
    OUT.mkdir(exist_ok=True)
    with open(OUT / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
        w.writeheader()
        w.writerows(rows)


def run():
    jobs = [(d, c) for d in days("validation") for c in CONTROLLERS]
    print(f"{len(jobs)} full-day runs")
    with Pool(22) as pool:
        res = [x for x in pool.map(safe_job, jobs, chunksize=1) if x is not None]
    write("runs.csv", [r for r, _ in res])
    write("hourly.csv", [h for _, hs in res for h in hs])


def report():
    runs = list(csv.DictReader(open(OUT / "runs.csv")))
    ctrls = [c for c in CONTROLLERS + ("lstdq",) if any(r["controller"] == c for r in runs)]
    hourly = list(csv.DictReader(open(OUT / "hourly.csv")))
    flagged = {r["date"] for r in csv.DictReader(open(HERE / "demand_audit/flagged_bins.csv"))}
    L = ["# Baselines on validation weekdays (full day)", "",
         "Mean delay per vehicle (s/veh): signal delay + queueing + waiting to enter. Median over days; "
         "days with flagged count bins marked separately.", "",
         "| Controller | all days median | IQR | days without flagged bins, median | P8 through (Piedmont-N) median | teleports |",
         "|---|---|---|---|---|---|"]
    for c in ctrls:
        rs = [r for r in runs if r["controller"] == c]
        v = sorted(float(r["delay_all_s"]) for r in rs)
        clean = [float(r["delay_all_s"]) for r in rs if r["date"] not in flagged]
        p8 = [float(r["delay_EB_T_s"]) for r in rs]
        L.append(f"| {c} | {st.median(v):.1f} | {v[len(v) // 4]:.1f}–{v[3 * len(v) // 4]:.1f} | {st.median(clean):.1f} | "
                 f"{st.median(p8):.1f} | {sum(int(r['teleports']) for r in rs)} |")
    # by period
    per = [("night 00–06", 0, 6), ("AM 06–10", 6, 10), ("midday 10–15", 10, 15), ("PM 15–19", 15, 19), ("evening 19–24", 19, 24)]
    L += ["", "Mean delay by time of day (s/veh, all validation weekdays pooled):", "",
          "| Controller | " + " | ".join(p for p, _, _ in per) + " |", "|---|" + "---|" * len(per)]
    for c in ctrls:
        cells = []
        for _, a, b in per:
            hs = [h for h in hourly if h["controller"] == c and a <= int(h["hour"]) < b]
            cells.append(f"{sum(float(h['delay_sum_s']) for h in hs) / max(1, sum(int(h['vehicles']) for h in hs)):.1f}")
        L.append(f"| {c} | " + " | ".join(cells) + " |")
    (OUT / "report.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    {"design": design, "run": run, "report": report}[sys.argv[1]]()
