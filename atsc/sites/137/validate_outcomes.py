"""Outcome-level validation O1-O5 (VALIDATION.md, attempt 9 registration): simulated vs GDOT ATSPM numbers per
timing-plan band, on the validation days.

    uv run python atsc/sites/137/validate_outcomes.py run      # simulate validation days -> validation/outcomes_sim.csv
    uv run python atsc/sites/137/validate_outcomes.py score    # O1-O5 table -> validation/outcomes_score.md

Field: intersections/137/atspm/<metric>.csv (tools/atspm_charts.py --plan-bands). A chart belongs to the approach
in its title; only a phase's OWN approach chart is compared (the approach whose protected phase is the chart's
phase; permissive-left charts drawn under a through phase are skipped). Simulated: atsc/sim/atspm_sim.py with the
phase's modelled stop-bar zones and advance detectors, in the same plan-band windows.
"""
import csv
import difflib
import json
import random
import statistics as st
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tools"))
OUT = HERE / "validation"
ATSPM = REPO / "intersections/137/atspm"
FIELDS = {"SplitFail": ["split_failures"], "WaitTime": ["avg_wait_s"], "PCD": ["aog_pct"],
          "ApproachDelay": ["delay_per_veh_s"]}
O = {"O1": ("SplitFail", "sf_pct"), "O2": ("WaitTime", "avg_wait_s"), "O3": ("PCD", "aog_pct"),
     "O4": ("ApproachDelay", "delay_per_veh_s")}


def approaches():
    out = {}
    for r in csv.DictReader(open(REPO / "intersections/137/config/approaches.csv")):
        out[r["Description"].replace(" ", "").lower()] = int(r["Protected Phase"])
    return out


def own_chart(title, phase, appr):
    key = title.replace(" ", "").lower()
    m = difflib.get_close_matches(key, list(appr), n=1, cutoff=0.6)
    return bool(m) and appr[m[0]] == int(phase)


def bands(date):
    import atspm_charts as C
    import datetime as dt
    return list(C.plan_windows("137", [dt.date.fromisoformat(date)]))


def sim_job(date):
    from atsc.sim import atspm_sim as A
    from atsc.sim.atspm_compare import offsets
    from atsc.sim.episode import run_window
    from atsc.sim.signal import actuated_from_site
    res = run_window(HERE, date, 0.0, 24.0, actuated_from_site(HERE), mode="plan", seed=1, warmup_s=0,
                     record_events=True)
    g, ev = res["greens"], res["events"]
    off = offsets(HERE, "137")
    rows = []
    for start, minutes in bands(date):
        t0 = start.hour * 3600 + start.minute * 60
        t1 = t0 + minutes * 60
        for p in sorted(ev["phases"]):
            sf = A.split_failures(g, ev, p, t0, t1)
            wt = A.wait_time(g, ev, p, t0, t1)
            r = {"date": date, "start": f"{start:%H:%M}", "minutes": minutes, "phase": p,
                 "split_failures": sf["split_failures"], "cycles": sf["cycles"], "sf_pct": sf["sf_pct"],
                 "avg_wait_s": wt["avg_wait_s"]}
            if p in off:
                r["aog_pct"] = A.pcd(g, ev, p, t0, t1, off[p])["aog_pct"]
                r["delay_per_veh_s"] = A.approach_delay(g, ev, p, t0, t1, off[p])["delay_per_veh_s"]
            rows.append(r)
    return rows


def run():
    from validate import days
    ds = [str(d) for d in days("validation")]
    with Pool(22) as pool:
        rows = [r for rs in pool.map(sim_job, ds, chunksize=1) for r in rs]
    OUT.mkdir(exist_ok=True)
    with open(OUT / "outcomes_sim.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} rows -> {OUT / 'outcomes_sim.csv'}")


def field_table(metric, appr, sim_cycles):
    """{(date, start, phase): value}; split failures turned into % of the band's simulated... no: field cycles are
    not printed, so O1 compares split-failure COUNTS per band (same band length both sides)."""
    p = ATSPM / f"{metric}.csv"
    out = {}
    if not p.exists():
        return out
    for r in csv.DictReader(open(p)):
        if r["ocr_ok"] != "1" or not r["phase"] or not own_chart(r["title"], r["phase"], appr):
            continue
        col = FIELDS[metric][0]
        if r[col] != "":
            out[(r["date"], r["start"], int(r["phase"]))] = float(r[col])
    return out


def score():
    appr = approaches()
    sim = list(csv.DictReader(open(OUT / "outcomes_sim.csv")))
    sig = json.loads((HERE / "signal.json").read_text())
    plan_at = {}
    for d, bl in sig["schedule_by_date"].items():
        for b0, name in bl:
            plan_at[(d, b0)] = name
    lines = ["# Outcome validation (O1-O4), attempt 9", "",
             "Per phase x plan: median over validation days of (sim - field), field day-to-day IQR, pass if inside.", ""]
    total_pass = total = 0
    for o, (metric, simcol) in O.items():
        fcol = FIELDS[metric][0]
        ft = field_table(metric, appr, None)
        if not ft:
            lines.append(f"## {o} {metric}: no field data yet\n")
            continue
        diffs, fvals = defaultdict(list), defaultdict(list)
        for s in sim:
            k = (s["date"], s["start"], int(s["phase"]))
            if k not in ft:
                continue
            sv = s.get("split_failures" if o == "O1" else simcol)
            if sv in (None, ""):
                continue
            plan = plan_at.get((s["date"], s["start"]), "?")
            diffs[(int(s["phase"]), plan)].append(float(sv) - ft[k])
            fvals[(int(s["phase"]), plan)].append(ft[k])
        lines += [f"## {o} {metric} ({fcol})", "", "| phase | plan | days | median sim - field | field IQR | pass |",
                  "|---|---|---|---|---|---|"]
        cases = []
        for key in sorted(diffs):
            if len(diffs[key]) < 5:
                continue
            fv = sorted(fvals[key])
            iqr = fv[3 * len(fv) // 4] - fv[len(fv) // 4]
            md = st.median(diffs[key])
            ok = abs(md) <= max(iqr / 2, 1e-9) if iqr > 0 else md == 0
            cases.append((key, diffs[key], iqr))
            lines.append(f"| P{key[0]} | {key[1]} | {len(diffs[key])} | {md:+.1f} | {iqr:.1f} | {'yes' if ok else 'no'} |")
            total += 1
            total_pass += ok
        if cases:
            rng = random.Random(1)
            hits = 0
            for _ in range(1000):
                n_ok = 0
                for _, dv, iqr in cases:
                    smp = [rng.choice(dv) for _ in dv]
                    n_ok += abs(st.median(smp)) <= iqr / 2 if iqr > 0 else st.median(smp) == 0
                hits += n_ok >= 0.8 * len(cases)
            lines += ["", f"Bootstrap over days: >= 80 % of cases pass in {hits / 10:.1f} % of 1,000 resamples.", ""]
    lines.append(f"Total: {total_pass}/{total} cases inside the field's day-to-day spread.")
    (OUT / "outcomes_score.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    {"run": run, "score": score}[sys.argv[1]]()
