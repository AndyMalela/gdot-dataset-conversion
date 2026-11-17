"""137 analysis for the research questions, on evaluate.py's outputs (eval/, eval_x<k>/) and the archived first-pass
model (archive_attempt1_model_2026-11-16/eval/).

    uv run python atsc/sites/137/analyze.py      -> eval/analysis.md, eval/analysis_*.csv

RQ1  ranking by condition: saturation Y (real days, and the demand sweep labelled by peak X_c), time of day,
     within-hour variability (cv of the 5-min totals); per hour the vehicle-weighted delay, learners pooled over their
     training seeds (mean over seeds per hour)
RQ2  controller behaviour by saturation (eval/mech.csv): cycle length, cycles per hour, and per phase group the green
     per service, the share of cycles it is served (1 - skip rate) and the share of its greens ended at max green
RQ3  robustness: (a) detector-count error = first-pass model (GDOT counts as reported) vs corrected model, same days;
     (b) spread over training seeds; (c) worst-served movement (95th-percentile delay of the worst movement in the hour)
TOST equivalence with actuated per controller over the validation days (daily vehicle-weighted delay, margin
max(2 s/veh, 5 %), fixed 2026-11-16 before any result was read), two one-sided paired t-tests at 5 %.
"""
import csv
import math
import os
import statistics as st
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
E = HERE / os.environ.get("ATSC_EVAL_DIR", "eval")         # eval_test: final evaluation (TEST_PLAN.md)
SET = os.environ.get("ATSC_SET", "validation")
OLD = HERE / "archive_attempt1_model_2026-11-16" / "eval"
RULES = ["actuated", "maxpressure", "gdot", "webster"]
LEARN = {"LSTDQ": "lstdq_v2_s", "Q-learning": "qlearn_s", "ARS": "ars_s"}
NAMES = {"actuated": "Actuated", "maxpressure": "MaxPressure", "gdot": "GDOT plan", "webster": "Webster"}
ORDER = ["Actuated", "MaxPressure", "LSTDQ", "Q-learning", "ARS", "GDOT plan", "Webster"]
ADAPTIVE = ["Actuated", "MaxPressure", "LSTDQ", "Q-learning", "ARS"]


def method_of(c):
    if c in NAMES:
        return NAMES[c]
    for m, p in LEARN.items():
        if c.startswith(p):
            return m
    return None


def load_hours(folder):
    """{(date, hour, method): [delay sum, vehicles]} pooled over training seeds (mean of per-seed hour delays,
    vehicle-weighted by the hour's vehicles); also per controller for seed spreads."""
    per_ctrl = defaultdict(lambda: [0.0, 0])
    worst = defaultdict(float)
    for r in csv.DictReader(open(folder / "hour_mv.csv")):
        k = (r["date"], int(r["hour"]), r["controller"])
        per_ctrl[k][0] += float(r["mean_s"]) * int(r["veh"])
        per_ctrl[k][1] += int(r["veh"])
        worst[k] = max(worst[k], float(r["p95_s"]))
    pooled = defaultdict(list)
    pw = defaultdict(list)
    for (d, h, c), (s, n) in per_ctrl.items():
        m = method_of(c)
        if m and n:
            pooled[(d, h, m)].append((s / n, n))
            pw[(d, h, m)].append(worst[(d, h, c)])
    out = {k: (st.mean(x for x, _ in v), max(n for _, n in v)) for k, v in pooled.items()}
    return out, per_ctrl, {k: st.mean(v) for k, v in pw.items()}


def conditions(folder):
    return {(r["date"], int(r["hour"])): r for r in csv.DictReader(open(folder / "conditions.csv"))}


def wmean(hours, D, m):
    s = sum(D[(*dh, m)][0] * D[(*dh, m)][1] for dh in hours)
    n = sum(D[(*dh, m)][1] for dh in hours)
    return s / n if n else float("nan")


def table_by(L, title, groups, D, methods):
    L += [f"### {title}", "", "| condition | hours | " + " | ".join(methods) + " | ranking (adaptive) |",
          "|---|---|" + "---|" * len(methods) + "---|"]
    rows = []
    for g, hs in groups:
        if not hs:
            continue
        m = {x: wmean(hs, D, x) for x in methods}
        rank = sorted([x for x in methods if x in ADAPTIVE], key=m.get)
        L.append(f"| {g} | {len(hs)} | " + " | ".join(f"{m[x]:.1f}" for x in methods) + " | " + " > ".join(rank) + " |")
        rows.append({"condition": g, "hours": len(hs), **{x: round(m[x], 2) for x in methods}})
    L.append("")
    return rows


def tost(diffs, margins):
    """paired TOST on daily differences d_i (controller - actuated) with per-day margins, t distribution with n - 1 df
    (TEST_PLAN.md; the normal approximation used before 2026-11-17 is anti-conservative for n = 7);
    returns (mean, p_max, equivalent)"""
    from scipy import stats as ss
    n = len(diffs)
    mu = st.mean(diffs)
    sd = st.stdev(diffs) if n > 1 else 0.0
    se = sd / math.sqrt(n) if sd > 0 else 1e-9
    delta = st.mean(margins)
    t1, t2 = (mu + delta) / se, (delta - mu) / se            # H0: mu <= -delta ; H0: mu >= delta
    pm = max(ss.t.sf(t1, n - 1), ss.t.sf(t2, n - 1))
    return mu, pm, pm < 0.05


def holm(ps):
    """Holm step-down adjusted p-values (family = the six comparisons with actuated)"""
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, run = [0.0] * len(ps), 0.0
    for k, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - k) * ps[i]))
        adj[i] = run
    return adj


def main():
    D, per_ctrl, W = load_hours(E)
    C = conditions(E)
    methods = [m for m in ORDER if any(k[2] == m for k in D)]
    hours = sorted({(d, h) for d, h, _ in D if (d, h) in C and all((d, h, m) in D for m in methods)})
    L = [f"# 137 analysis: when and why each method wins (corrected-demand model, {SET} weekdays)", "",
         f"{len({d for d, _ in hours})} days, {len(hours)} clean hours, learners pooled over training seeds. "
         "Model: attempt 7 (VALIDATION.md: + floating force-off P1/P5; V1 34/35, V2 29/35, V5 pass: accepted; V3 skips 19/35 reported).", ""]

    # ---------------- RQ1
    L += ["## RQ1: how the ranking changes", ""]
    yb = [("light, Y < 0.3", 0, 0.3), ("moderate, 0.3–0.45", 0.3, 0.45), ("busy, 0.45–0.6", 0.45, 0.6), ("heavy, Y ≥ 0.6", 0.6, 9)]
    r1 = table_by(L, "By saturation Y (sum of critical flow ratios, field counts)",
                  [(g, [dh for dh in hours if lo <= float(C[dh]["Y"]) < hi]) for g, lo, hi in yb], D, methods)
    tod = [("night 00–06", 0, 6), ("AM peak 06–10", 6, 10), ("midday 10–15", 10, 15), ("PM peak 15–19", 15, 19), ("evening 19–24", 19, 24)]
    r2 = table_by(L, "By time of day", [(g, [dh for dh in hours if a <= dh[1] < b]) for g, a, b in tod], D, methods)
    cvb = [("steady, cv < 0.15", 0, 0.15), ("variable, 0.15–0.25", 0.15, 0.25), ("very variable, cv ≥ 0.25", 0.25, 9)]
    vol = {dh: float(C[dh]["volume"]) for dh in hours}
    r3 = table_by(L, "By within-hour variability (cv of the twelve 5-min totals)",
                  [(g, [dh for dh in hours if lo <= float(C[dh]["cv5"] or 0) < hi]) for g, lo, hi in cvb], D, methods)
    for g, lo, hi in cvb:
        hs = [dh for dh in hours if lo <= float(C[dh]["cv5"] or 0) < hi]
        if hs:
            L.append(f"- {g}: mean volume {st.mean(vol[dh] for dh in hs):.0f} veh/h")
    L += ["", "Variability and volume move together (quiet hours are the most variable), so this split is not independent "
          "of saturation.", ""]
    # sweep
    sweep = sorted(HERE.glob("eval_x*"), key=lambda p: float(p.name[6:])) if SET == "validation" else []
    if sweep:
        L += ["### Demand sweep (real profile × k, same 5 days, seed 0 learners): vehicle-weighted delay, s/veh", "",
              "| scale | " + " | ".join(methods) + " | ranking (adaptive) |", "|---|" + "---|" * len(methods) + "---|"]
        for f in [E] + sweep:
            runs = list(csv.DictReader(open(f / "runs.csv"))) if (f / "runs.csv").exists() else []
            acc = defaultdict(lambda: [0.0, 0])
            for r in runs:
                m = method_of(r["controller"])
                if m and r["delay_all_s"] and (f != E or r["controller"].endswith(("_s0",)) or r["controller"] in NAMES):
                    if f == E and r["date"] not in {"2026-04-20", "2026-04-24", "2026-04-30", "2026-05-06", "2026-05-12"}:
                        continue
                    acc[m][0] += float(r["delay_all_s"]) * int(r["vehicles"])
                    acc[m][1] += int(r["vehicles"])
            if not acc:
                continue
            mm = {m: acc[m][0] / acc[m][1] for m in acc}
            rank = sorted([x for x in methods if x in ADAPTIVE and x in mm], key=mm.get)
            k = "1" if f == E else f.name[6:]
            L.append(f"| ×{k} | " + " | ".join(f"{mm[m]:.1f}" if m in mm else "-" for m in methods) + " | " + " > ".join(rank) + " |")
        L.append("")

    # ---------------- RQ2
    L += ["## RQ2: what the controllers do (by saturation)", "",
          "Per controller: cycle length; per phase group: average green per service, share of cycles served "
          "(100 % − skips), share of greens ended at max green. Learners: training seed 0.", ""]
    M = defaultdict(lambda: [0, 0.0, 0])
    for r in csv.DictReader(open(E / "mech.csv")):
        M[(r["date"], int(r["hour"]), r["controller"], r["phase"])] = [int(r["n"]), float(r["total_s"]), int(r["n_max"])]
    G = {"main through P2/P6": ["2", "6"], "side through P4/P8": ["4", "8"], "main lefts P1/P5": ["1", "5"], "side lefts P3/P7": ["3", "7"]}
    mech_rows = []
    ctrls2 = ["actuated", "maxpressure", "lstdq_v2_s0", "qlearn_s0", "ars_s0", "gdot"]
    for g, lo, hi in yb:
        hs = [dh for dh in hours if lo <= float(C[dh]["Y"]) < hi]
        if not hs:
            continue
        L += [f"### {g} ({len(hs)} hours)", "", "| controller | cycle s | " + " | ".join(G) + " |", "|---|---|" + "---|" * len(G)]
        for c in ctrls2:
            nc = sum(M[(*dh, c, "cycle")][0] for dh in hs)
            tc = sum(M[(*dh, c, "cycle")][1] for dh in hs)
            cells, row = [], {"condition": g, "controller": c, "cycle_s": round(tc / nc, 1) if nc else None}
            for k, ps in G.items():
                n = sum(M[(*dh, c, p)][0] for dh in hs for p in ps)
                t = sum(M[(*dh, c, p)][1] for dh in hs for p in ps)
                mx = sum(M[(*dh, c, p)][2] for dh in hs for p in ps)
                gs, served, mxs = (t / n if n else 0), (100 * n / (len(ps) * nc) if nc else 0), (100 * mx / n if n else 0)
                cells.append(f"{gs:.1f} s · {served:.0f} % · max {mxs:.0f} %")
                row.update({f"{k} green_s": round(gs, 1), f"{k} served_pct": round(served), f"{k} maxout_pct": round(mxs)})
            mech_rows.append(row)
            L.append(f"| {method_of(c)} | {tc / nc if nc else 0:.0f} | " + " | ".join(cells) + " |")
        L.append("")

    # ---------------- RQ3
    L += ["## RQ3: does the ranking hold?", ""]
    if SET == "validation" and (OLD / "hour_mv.csv").exists():
        Do, _, _ = load_hours(OLD)
        days = sorted({d for d, _ in hours})
        hs_old = sorted({(d, h) for d, h, _ in Do if d in days and all((d, h, m) in Do for m in methods)})
        L += ["### (a) Detector-count error: GDOT counts as reported vs corrected side-street demand (same days)", "",
              "| model | " + " | ".join(methods) + " | ranking (adaptive) |", "|---|" + "---|" * len(methods) + "---|"]
        for name, DD, hs in [("first pass (reported counts)", Do, hs_old), ("corrected counts (attempt 7 model)", D, hours)]:
            m = {x: wmean(hs, DD, x) for x in methods}
            rank = sorted([x for x in methods if x in ADAPTIVE], key=m.get)
            L.append(f"| {name} | " + " | ".join(f"{m[x]:.1f}" for x in methods) + " | " + " > ".join(rank) + " |")
        L += ["", "The two models differ in the counted side-street and EB-left demand (and in pedestrians, passage "
              "times and left-turn calibration); the ranking change is the effect of the whole correction.", ""]
    # seeds
    L += ["### (b) Training seeds: overall vehicle-weighted delay per seed (s/veh)", "", "| learner | per seed | median | spread |", "|---|---|---|---|"]
    for m, p in LEARN.items():
        vals = []
        for s in range(5):
            c = f"{p}{s}"
            tot = [(per_ctrl[(*dh, c)][0], per_ctrl[(*dh, c)][1]) for dh in hours if (*dh, c) in per_ctrl]
            if tot:
                vals.append(sum(a for a, _ in tot) / sum(b for _, b in tot))
        if vals:
            L.append(f"| {m} | " + ", ".join(f"{v:.1f}" for v in vals) + f" | {st.median(vals):.1f} | {max(vals) - min(vals):.1f} |")
    L.append("")
    # worst movement
    L += ["### (c) Worst-served movement: 95th-percentile delay of the worst movement in the hour (s), by saturation", "",
          "| condition | " + " | ".join(methods) + " |", "|---|" + "---|" * len(methods)]
    for g, lo, hi in yb:
        hs = [dh for dh in hours if lo <= float(C[dh]["Y"]) < hi]
        if hs:
            L.append(f"| {g} | " + " | ".join(f"{st.mean(W[(*dh, x)] for dh in hs):.0f}" for x in methods) + " |")
    L.append("")

    # ---------------- comparison with actuated (TEST_PLAN.md, registered 2026-11-17 before the test days were read)
    from scipy import stats as ss
    days = sorted({d for d, _ in hours})
    daily = {}
    for m in methods:
        for d in days:
            daily[(d, m)] = wmean([dh for dh in hours if dh[0] == d], D, m)
    L += [f"## Comparison with actuated, daily vehicle-weighted delay over the {SET} days ({len(days)} days)", "",
          "Pre-registered (TEST_PLAN.md). Primary: paired t-test on the daily log ratio ln(delay / actuated delay), "
          "Holm-adjusted over the six comparisons; ratio = geometric mean with its 95 % t interval. Equivalence (H1, "
          "margin per day max(2 s/veh, 5 % of actuated), fixed 2026-11-16): paired TOST at 5 %, t distribution. "
          "Secondary (reported, no verdict): mean and median difference, days won, Wilcoxon signed-rank ("
          f"its smallest possible two-sided p is {2 / 2 ** len(days):.3g} with {len(days)} days). Learners: mean over training seeds and simulation seeds per "
          "hour; other controllers: mean over simulation seeds.", "",
          "| method | ratio to actuated (95 % CI) | p primary | p Holm | p TOST | mean diff (s/veh) | median diff | days won | p Wilcoxon | verdict |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    comp = [m for m in methods if m != "Actuated"]
    res = {}
    for m in comp:
        diffs = [daily[(d, m)] - daily[(d, "Actuated")] for d in days]
        lr = [math.log(daily[(d, m)] / daily[(d, "Actuated")]) for d in days]
        margins = [max(2.0, 0.05 * daily[(d, "Actuated")]) for d in days]
        mu, p_eq, eq = tost(diffs, margins)
        n = len(lr)
        se = st.stdev(lr) / math.sqrt(n)
        tq = ss.t.ppf(0.975, n - 1)
        p1 = ss.ttest_1samp(lr, 0.0).pvalue
        try:
            pw = ss.wilcoxon(diffs).pvalue
        except ValueError:
            pw = float("nan")
        res[m] = dict(diffs=diffs, lr=st.mean(lr), lo=st.mean(lr) - tq * se, hi=st.mean(lr) + tq * se, p1=p1,
                      p_eq=p_eq, eq=eq, mu=mu, pw=pw)
    for m, pa in zip(comp, holm([res[m]["p1"] for m in comp])):
        r = res[m]
        if r["eq"]:
            verdict = "equivalent"
        elif pa < 0.05:
            verdict = "better" if r["lr"] < 0 else "worse"
        else:
            verdict = "inconclusive"
        won = sum(x < 0 for x in r["diffs"])
        L.append(f"| {m} | {math.exp(r['lr']):.3f} ({math.exp(r['lo']):.3f}–{math.exp(r['hi']):.3f}) | {r['p1']:.4f} | "
                 f"{pa:.4f} | {r['p_eq']:.3f} | {r['mu']:+.2f} | {st.median(r['diffs']):+.2f} | {won}/{len(days)} | "
                 f"{r['pw']:.4f} | {verdict} |")
    L.append("")
    # per training seed (robustness, descriptive): each trained agent on its own against actuated
    L += ["### Per training seed against actuated (descriptive)", "",
          "| learner seed | delay (s/veh) | ratio to actuated (geometric mean) | days won |", "|---|---|---|---|"]
    act = {d: daily[(d, "Actuated")] for d in days}
    for m, pfx in LEARN.items():
        for s_ in range(5):
            c = f"{pfx}{s_}"
            per_day = {}
            for d in days:
                hs = [dh for dh in hours if dh[0] == d and (*dh, c) in per_ctrl and per_ctrl[(*dh, c)][1]]
                if hs:
                    per_day[d] = sum(per_ctrl[(*dh, c)][0] for dh in hs) / sum(per_ctrl[(*dh, c)][1] for dh in hs)
            if len(per_day) == len(days):
                tot = sum(per_ctrl[(*dh, c)][0] for dh in hours if (*dh, c) in per_ctrl)
                veh = sum(per_ctrl[(*dh, c)][1] for dh in hours if (*dh, c) in per_ctrl)
                g = math.exp(st.mean(math.log(per_day[d] / act[d]) for d in days))
                L.append(f"| {c} | {tot / veh:.1f} | {g:.3f} | {sum(per_day[d] < act[d] for d in days)}/{len(days)} |")
    L.append("")

    (E / "analysis.md").write_text("\n".join(L) + "\n")
    for name, rows in [("rq1_saturation", r1), ("rq1_time_of_day", r2), ("rq1_variability", r3), ("rq2_mechanism", mech_rows)]:
        if rows:
            with open(E / f"analysis_{name}.csv", "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0]))
                w.writeheader()
                w.writerows(rows)
    print("\n".join(L))


if __name__ == "__main__":
    main()
