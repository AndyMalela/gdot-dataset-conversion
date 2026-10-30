"""Phase 1.6 (and the train-day passage fit): simulate whole days under GDOT's plans and compare with GDOT's
Split Monitor statistics. Criteria: VALIDATION.md.

    uv run python atsc/sites/7065/validate.py fit-passage        # train days, passage grid -> validation/passage_fit.csv
    uv run python atsc/sites/7065/validate.py run                # validation days, sim.json passage -> validation/*.csv
    uv run python atsc/sites/7065/validate.py score              # V1-V5 from validation/*.csv
"""
import csv
import json
import statistics as st
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
from atsc.sim.demand import day_quality, day_set, load_counts, schedule  # noqa: E402

OUT = HERE / "validation"
SCORED = (1, 3, 4, 5, 7, 8)
WEEKDAY_PLANS = ("A", "B", "C", "D", "E")
PASSAGES = (2.0, 3.0, 4.0, 6.0, 8.0)
RECALL_FORCE_PCT, RECALL_SKIP_PCT = 90.0, 1.0      # max-recall rule (CONTROLLER.md)
G8_C = 55 - 3.6 - 3.0


def days(set_name):
    split = json.loads((HERE / "split.json").read_text())
    cnt = load_counts(HERE)
    return [d for d in sorted(cnt) if day_set(split, d) == set_name and d.weekday() < 5
            and str(d) not in split["holidays"] and day_quality(cnt[d])[0] in ("complete", "usable")]


def field_rows():
    f = REPO / "intersections/7065/timing/splitstats_7065.csv"
    return [r for r in csv.DictReader(open(f)) if r["check"] == "ok"]


def plan_of(sig, date, hhmm):
    t = int(hhmm[:2]) * 3600 + int(hhmm[3:]) * 60
    sch = schedule(sig, date)
    return [n for t0, n in sch if t0 <= t + 300][-1]           # band edges are read to ~1 min


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
    from atsc.sim.metrics import split_stats
    from atsc.sim.signal import ActuatedPolicy, actuated_from_site
    date, spec, bands = args
    sig = json.loads((HERE / "signal.json").read_text())
    pol = actuated_from_site(HERE) if spec is None else ActuatedPolicy(spec["passage"], spec["max_recall"])
    passage = "site" if spec is None else spec["passage"]
    r = run_window(HERE, str(date), 0.0, 24.0, pol, warmup_s=0)
    ph = {int(k): (v["yellow"], v["red"]) for k, v in sig["phases"].items()}
    stats = split_stats(r["greens"], r["cycle_starts"], ph, bands)
    rows = [{"date": str(date), "passage": passage, "band_start": b0, "band_end": b1, "plan": plan_of(sig, date, b0),
             "phase": p, **{k: (round(v, 2) if isinstance(v, float) else v) for k, v in s.items()}}
            for (b0, b1, p), s in stats.items()]
    # P8 discharge per plan-C quarter and PM P8-through delay (V4, V5)
    sch = schedule(sig, date)
    name = lambda t: [n for t0, n in sch if t0 <= t][-1]
    quarters = [{"date": str(date), "quarter": q,
                 "served": sum(q <= t < q + 900 for t in r["crossings"].get("EB_T", []))}
                for q in range(int(15.5 * 3600), 19 * 3600, 900) if name(q) == "C" and name(q + 899) == "C"]
    return rows, quarters, {"date": str(date), "passage": passage, "teleports": r["teleports"],
                            "delay_all_s": round(r["delay_all_s"], 1)}


def pm_delay_job(date):
    from atsc.sim.episode import run_window
    from atsc.sim.signal import actuated_from_site
    r = run_window(HERE, str(date), 15.5, 19.0, actuated_from_site(HERE))
    return {"date": str(date), "pm_delay_EB_T_s": round(r["delay"]["EB_T"]["mean_s"], 1),
            "pm_delay_all_s": round(r["delay_all_s"], 1), "teleports": r["teleports"]}


def bands_by_date(rows):
    b = defaultdict(set)
    for r in rows:
        b[r["date"]].add((r["band_start"], r["band_end"]))
    return {d: sorted(v) for d, v in b.items()}


def write(name, rows):
    OUT.mkdir(exist_ok=True)
    with open(OUT / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
        w.writeheader()
        w.writerows(rows)


def run(set_name, specs):
    bands = bands_by_date(field_rows())
    ds = [d for d in days(set_name) if str(d) in bands]
    jobs = [(d, sp, bands[str(d)]) for d in ds for sp in specs]
    print(f"{set_name}: {len(ds)} days x {len(specs)} controller settings = {len(jobs)} full-day runs")
    with Pool(22) as pool:
        res = [x for x in pool.map(safe_job, jobs, chunksize=1) if x is not None]
    return [r for rs, _, _ in res for r in rs], [q for _, qs, _ in res for q in qs], [h for _, _, h in res]


def compare(sim, field, plans=WEEKDAY_PLANS):
    """-> {(phase, plan): {"n", "split_diff", "gap_diff", "skip_diff"}} medians over days of sim - field."""
    fi = {(r["date"], r["band_start"], int(r["phase"])): r for r in field}
    d = defaultdict(lambda: defaultdict(list))
    for s in sim:
        f = fi.get((s["date"], s["band_start"], int(s["phase"])))
        if f is None or s["plan"] not in plans or int(s["phase"]) not in SCORED:
            continue
        key = (int(s["phase"]), s["plan"])
        # a phase the field never served in the band (skip 100 %) has no average split: the chart prints 0.0
        if s["avg_split_s"] not in (None, "") and f["avg_split_s"] and float(f["skip_pct"]) < 99.5:
            d[key]["split"].append(float(s["avg_split_s"]) - float(f["avg_split_s"]))
        d[key]["gap"].append(float(s["gap_pct"]) - float(f["gap_pct"]))
        d[key]["skip"].append(float(s["skip_pct"]) - float(f["skip_pct"]))
    return {k: {"n": len(v["gap"]), **{f"{q}_diff": st.median(v[q]) if v[q] else None for q in ("split", "gap", "skip")}}
            for k, v in d.items()}


def main():
    cmd = sys.argv[1]
    if cmd == "fit-passage":
        fit_controller()
    elif cmd == "run":
        sim, quarters, health = run("validation", [None])
        with Pool(22) as pool:
            pm = pool.map(pm_delay_job, days("validation"), chunksize=1)
        write("sim_splitstats.csv", sim)
        write("sim_p8_quarters.csv", quarters)
        write("health.csv", [{**h, **next((x for x in pm if x["date"] == h["date"]), {})} for h in health])
    elif cmd == "score":
        score()


def infer_recall(field, train):
    """max recall in a plan: median force-off share on train days >= 90 % and median skip share <= 1 %."""
    sig = json.loads((HERE / "signal.json").read_text())
    agg = defaultdict(lambda: defaultdict(list))
    for r in field:
        if r["date"] in train:
            pl = plan_of(sig, __import__("datetime").date.fromisoformat(r["date"]), r["band_start"])
            agg[(pl, int(r["phase"]))]["force"].append(float(r["force_pct"]))
            agg[(pl, int(r["phase"]))]["skip"].append(float(r["skip_pct"]))
    rec = defaultdict(list)
    for (pl, p), v in sorted(agg.items()):
        if p in SCORED and st.median(v["force"]) >= RECALL_FORCE_PCT and st.median(v["skip"]) <= RECALL_SKIP_PCT:
            rec[pl].append(p)
    return dict(rec)


def fit_controller():
    """train days only: max recall by rule, then the passage time per phase from PASSAGES."""
    field = field_rows()
    train = {str(d) for d in days("train")}
    recall = infer_recall(field, train)
    print("max recall (train-day rule):", recall)
    sim, _, _ = run("train", [{"passage": p, "max_recall": recall} for p in PASSAGES])
    write("passage_runs.csv", sim)
    tf = [r for r in field if r["date"] in train]
    err = {}
    for p in PASSAGES:
        c = compare([s for s in sim if float(s["passage"]) == p], tf)
        for (ph, pl), v in c.items():
            if v["n"] >= 5 and ph not in recall.get(pl, []):
                err.setdefault(ph, {}).setdefault(p, []).append((abs(v["gap_diff"]), abs(v["split_diff"] or 0)))
    rows, best = [], {}
    for ph in sorted(err):
        for p, e in sorted(err[ph].items()):
            rows.append({"phase": ph, "passage_s": p, "plans": len(e), "mean_abs_gap_diff_pts": round(st.mean(x for x, _ in e), 1),
                         "mean_abs_split_diff_s": round(st.mean(y for _, y in e), 2)})
        best[ph] = min(err[ph], key=lambda p: (st.mean(x for x, _ in err[ph][p]), st.mean(y for _, y in err[ph][p])))
    write("passage_fit.csv", rows)
    for r in rows:
        print(r)
    cal = json.loads((HERE / "sim.json").read_text())
    cal["controller"] = {"source": "fitted on train weekdays (validate.py fit-passage, CONTROLLER.md)",
                         "max_recall": recall, "passage_s": {str(k): v for k, v in best.items()}}
    (HERE / "sim.json").write_text(json.dumps(cal, indent=1) + "\n")
    print("wrote sim.json controller:", cal["controller"])


def score():
    sim = list(csv.DictReader(open(OUT / "sim_splitstats.csv")))
    vdays = {s["date"] for s in sim}
    field = [r for r in field_rows() if r["date"] in vdays]
    c = {k: v for k, v in compare(sim, field).items() if v["n"] >= 5}
    L = ["| Phase | Plan | days | avg split sim − field (s) | % gap-outs sim − field | % skips sim − field |",
         "|---|---|---|---|---|---|"]
    for (p, pl), v in sorted(c.items()):
        f = lambda x, n: "—" if x is None else f"{x:+.{n}f}"
        L.append(f"| P{p} | {pl} | {v['n']} | {f(v['split_diff'], 1)} | {f(v['gap_diff'], 0)} | {f(v['skip_diff'], 0)} |")
    sp = [abs(v["split_diff"]) for v in c.values() if v["split_diff"] is not None]
    gp = [abs(v["gap_diff"]) for v in c.values()]
    kp = [abs(v["skip_diff"]) for v in c.values()]
    v1 = sum(x <= 3 for x in sp) / len(sp) >= 0.8 and max(sp) <= 6
    v2 = sum(x <= 15 for x in gp) / len(gp) >= 0.8 and max(gp) <= 30
    v3 = sum(x <= 15 for x in kp) / len(kp) >= 0.8
    # V4
    q = list(csv.DictReader(open(OUT / "sim_p8_quarters.csv")))
    sim_rate = sorted(int(r["served"]) / (2 * 5 * G8_C) * 3600 for r in q)
    cnt = load_counts(HERE)
    fr = []
    for r in q:
        d = __import__("datetime").date.fromisoformat(r["date"])
        by = {b.t: b for b in cnt[d]}
        bs = [by.get(int(r["quarter"]) + 300 * k) for k in range(3)]
        if all(b is not None and b.status == "ok" for b in bs):
            fr.append(sum(b.counts["EB_T"] for b in bs) / (2 * 5 * G8_C) * 3600)
    sm, fm = st.median(sim_rate), st.median(fr)
    v4 = abs(sm / fm - 1) <= 0.05
    # V5
    h = list(csv.DictReader(open(OUT / "health.csv")))
    flagged = {r["date"] for r in csv.DictReader(open(HERE / "demand_audit/flagged_bins.csv"))}
    tele = sum(int(r["teleports"]) for r in h)
    over = [r["date"] for r in h if float(r["pm_delay_EB_T_s"]) > 100 and r["date"] not in flagged]
    v5 = tele == 0 and len(over) <= 2
    L += ["", f"- **V1 average split:** {sum(x <= 3 for x in sp)}/{len(sp)} pairs within 3 s, worst {max(sp):.1f} s → **{'PASS' if v1 else 'FAIL'}**",
          f"- **V2 % gap-outs:** {sum(x <= 15 for x in gp)}/{len(gp)} pairs within 15 points, worst {max(gp):.0f} → **{'PASS' if v2 else 'FAIL'}**",
          f"- **V3 % skips:** {sum(x <= 15 for x in kp)}/{len(kp)} pairs within 15 points → **{'PASS' if v3 else 'FAIL'}** (reported)",
          f"- **V4 P8 discharge:** sim median {sm:.0f} vs field {fm:.0f} veh/h per lane of nominal green ({100 * (sm / fm - 1):+.1f} %) → **{'PASS' if v4 else 'FAIL'}**",
          f"- **V5 health:** {tele} teleports; overflow days outside flagged days: {', '.join(over) or 'none'} → **{'PASS' if v5 else 'FAIL'}**"]
    print("\n".join(L))
    (OUT / "score.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
