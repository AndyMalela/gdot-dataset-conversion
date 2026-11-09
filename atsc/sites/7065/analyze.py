"""RQ1 analysis on top of evaluate.py's runs: paired tests, mechanism, figures, and what LSTDQ learnt.

    uv run python atsc/sites/7065/analyze.py      -> eval/analysis.md; results/ (tidy CSVs + figures, see
                                                     results/README.md) for diagrams and the thesis

Learners are pooled over training seeds and simulation seeds: per (day, hour) the delay of a learner is the mean
over all its runs (5 training seeds x 3 simulation seeds when complete). Rule controllers: 3 simulation seeds.
Clean hours only (evaluate.py conditions), and only hours every compared controller has.

1. Paired comparison with MaxPressure (the best rule): per hour, delay(controller) - delay(MaxPressure); per
   traffic condition, the mean over days of the daily mean difference, a 95 % day-bootstrap interval, and a
   Wilcoxon signed-rank test over the 20 days (two-sided). Same for the top learners against each other.
2. Mechanism, simulation seed 2: cycle length, green per phase, share of greens ended at max green, phase
   service rate (greens per cycle), by condition.
3. LSTDQ v2f's learnt rule: q(end) - q(extend) = d . x, d = w_end - w_extend, per serving phase, averaged over
   training seeds (with how many of the 5 seeds agree in sign).
"""
import csv
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
sys.path.insert(0, str(HERE))
from evaluate import OUT, Y_BINS, boot_ci  # noqa: E402

RULES = ("gdot", "webster", "actuated", "maxpressure")
RES = HERE / "results"
FIG = RES / "figures"
FAMILY = {"gdot": ("rule", "fixed field plan (GDOT time-of-day, coordinated cycle)"),
          "webster": ("rule", "fixed time, Webster splits per plan period"),
          "actuated": ("rule", "fully actuated gap-out, field passage times"),
          "maxpressure": ("rule", "MaxPressure on detector queue estimates, cyclic"),
          "lstdq v1": ("learnt, linear", "LSTDQ / LSPI, base state and reward"),
          "lstdq v2": ("learnt, linear", "LSTDQ, + queue estimate + other ring, delay reward (LSTDQ_V2.md)"),
          "lstdq v2f": ("learnt, linear", "LSTDQ v2 + waiting-time fairness term (LSTDQ_V2.md)"),
          "qlearn": ("learnt, linear", "online linear Q-learning, v2 state (METHODS.md)"),
          "ars": ("learnt, linear", "augmented random search, linear policy, v2 state (METHODS.md)"),
          "nfq_conv": ("learnt, neural", "neural fitted Q iterated to convergence, v2 state (METHODS.md amendment 1)"),
          "nfq": ("learnt, neural", "neural fitted Q as registered: 25 backups, short horizon (METHODS.md)")}
LABEL = {"gdot": "Field plan", "webster": "Webster", "actuated": "Actuated", "maxpressure": "MaxPressure",
         "lstdq v1": "LSTDQ v1", "lstdq v2": "LSTDQ v2", "lstdq v2f": "LSTDQ v2f", "qlearn": "Q-learning",
         "ars": "ARS", "nfq_conv": "NFQ", "nfq": "NFQ (registered, short horizon)"}
ORDER = list(LABEL)
PHASE_NAME = {1: "P1 Peachtree-SW left", 2: "P2 Peachtree-NE through", 3: "P3 Piedmont-N left",
              4: "P4 Piedmont-S through", 5: "P5 Peachtree-NE left", 6: "P6 Peachtree-SW through",
              7: "P7 Piedmont-S left", 8: "P8 Piedmont-N through"}


def group(c):
    if c.startswith("lstdq"):
        return "lstdq " + next((x for x in c.split("_") if x in ("v2", "v2f")), "v1")
    return c.rsplit("_", 1)[0] if c.rsplit("_", 1)[-1][:1] == "s" and c.rsplit("_", 1)[-1][1:].isdigit() else c


def short(lab):
    return lab.split(" (")[0]


def load():
    cond = {(r["date"], int(r["hour"])): r for r in csv.DictReader(open(OUT / "conditions.csv"))}
    acc = defaultdict(lambda: [0.0, 0])               # (date, hour, controller, seed) -> delay sum, vehicles
    p95 = defaultdict(list)
    for r in csv.DictReader(open(OUT / "hour_mv.csv")):
        k = (r["date"], int(r["hour"]), r["controller"], r["seed"])
        acc[k][0] += float(r["mean_s"]) * int(r["veh"])
        acc[k][1] += int(r["veh"])
        p95[k].append(float(r["p95_s"]))
    runs = defaultdict(list)                            # (date, hour, group) -> per-run delays
    worst = defaultdict(list)
    runs_of = defaultdict(set)
    for (d, h, c, s), (tot, n) in acc.items():
        if n and (d, h) in cond:
            g = group(c)
            runs[(d, h, g)].append(tot / n)
            worst[(d, h, g)].append(max(p95[(d, h, c, s)]))
            runs_of[g].add((c, s))
    D = {k: st.mean(v) for k, v in runs.items()}
    W = {k: st.mean(v) for k, v in worst.items()}
    groups = [g for g in ORDER if g in runs_of]
    ybin = {dh: next(lab for lo, hi, lab in Y_BINS if lo <= float(r["Y"]) < hi) for dh, r in cond.items()}
    return cond, D, W, groups, ybin, runs_of


def paired(D, ybin, a, b, hours):
    """per bin: mean daily difference a - b, 95 % interval, Wilcoxon p, days."""
    from scipy.stats import wilcoxon
    out = {}
    for sel in [None] + [lab for _, _, lab in Y_BINS]:
        per_day = defaultdict(list)
        for dh in hours:
            if (sel is None or ybin[dh] == sel) and (*dh, a) in D and (*dh, b) in D:
                per_day[dh[0]].append(D[(*dh, a)] - D[(*dh, b)])
        per_day = {d: st.mean(v) for d, v in per_day.items()}
        if len(per_day) < 5:
            out[sel] = None
            continue
        lo, hi = boot_ci(per_day)
        p = wilcoxon(list(per_day.values())).pvalue if any(per_day.values()) else 1.0
        out[sel] = (st.mean(per_day.values()), lo, hi, p, len(per_day))
    return out


def fmt_pair(x):
    if x is None:
        return "-"
    m, lo, hi, p, n = x
    star = "**" if p < 0.05 and (lo > 0 or hi < 0) else ""
    return f"{star}{m:+.1f}{star} ({lo:+.1f} to {hi:+.1f}), p={p:.3f}"


def mechanism(groups, ybin, cond):
    """per (group, bin): mean cycle (s), mean green per phase (s), max-out share, greens per cycle, sim seed 2."""
    f = OUT / "mech.csv"
    if not f.exists():
        return {}
    agg = defaultdict(lambda: [0, 0.0, 0])            # (group, bin, phase) -> n, total, n_max
    for r in csv.DictReader(open(f)):
        dh = (r["date"], int(r["hour"]))
        if r["seed"] != "2" or dh not in cond:
            continue
        a = agg[(group(r["controller"]), ybin[dh], r["phase"])]
        a[0] += int(r["n"])
        a[1] += float(r["total_s"])
        a[2] += int(r["n_max"])
    return agg


# slide figures: validated colour-blind-safe palettes (dataviz skill validator, light mode); colour follows the
# controller; MaxPressure (blue) and LSTDQ v2f (orange) keep their colours in every figure
COL_A = {"maxpressure": "#2a78d6", "lstdq v2f": "#eb6834", "actuated": "#1baf7a", "webster": "#eda100",
         "gdot": "#6250d6"}
COL_B = {"lstdq v1": "#e87ba4", "lstdq v2": "#6250d6", "lstdq v2f": "#eb6834", "ars": "#1baf7a", "qlearn": "#008300"}
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"


def _axes(ax, title, ylabel, bins):
    ax.set_title(title, loc="left", fontsize=11, color=INK)
    ax.set_ylabel(ylabel, color=INK2)
    ax.set_xticks(range(len(bins)), [b.split(" (")[0] + "\n" + b.split(" (")[1].rstrip(")") for b in bins])
    ax.tick_params(colors=INK2, length=0)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(GRID)


def _label_ends(ax, items, x):
    """direct labels at the line ends, nudged apart vertically."""
    lo, hi = ax.get_ylim()
    gap = 0.045 * (hi - lo)
    placed = []
    for y, text, col in sorted(items):
        y2 = max([y] + [q + gap for q in placed])
        placed.append(y2)
        ax.annotate(text, (x, y), xytext=(x + 0.12, y2), textcoords="data", va="center", fontsize=9, color=INK,
                    arrowprops=dict(arrowstyle="-", color=col, lw=0.8) if abs(y2 - y) > 1e-9 else None)


def figures(D, W, groups, ybin, cond, hours, agg):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    bins = [lab for _, _, lab in Y_BINS]
    xs = np.arange(len(bins))
    n_by = {b: sum(ybin[dh] == b for dh in hours) for b in bins}

    # A: rule-based controllers vs LSTDQ v2f
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    for ax, M, title, yl in [(axes[0], D, "Mean delay", "s per vehicle"),
                             (axes[1], W, "Worst-off movement (95th-percentile delay)", "s")]:
        ends = []
        for g, col in COL_A.items():
            ys = [st.mean(M[(*dh, g)] for dh in hours if ybin[dh] == b) for b in bins]
            ax.plot(xs, ys, color=col, lw=2, marker="o", ms=7, mec="white", mew=1.5, zorder=3)
            ends.append((ys[-1], LABEL[g], col))
        _axes(ax, title, yl, bins)
        ax.set_xlim(-0.3, len(bins) - 1 + 0.9)
        _label_ends(ax, ends, len(bins) - 1)
    fig.suptitle("Rule-based controllers vs LSTDQ v2f, by degree of saturation Y (20 validation weekdays, "
                 f"hours per bin: {', '.join(str(n_by[b]) for b in bins)})", fontsize=11, color=INK, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(FIG / "rules_vs_lstdq.png", dpi=180)
    plt.close(fig)

    # B: learners minus MaxPressure, paired by hour, 95 % day-bootstrap interval
    learners = [g for g in COL_B if g in groups]
    fig, ax = plt.subplots(figsize=(12, 4.6))
    w = 0.14
    for i, g in enumerate(learners):
        r = paired(D, ybin, g, "maxpressure", hours)
        off = (i - (len(learners) - 1) / 2) * w
        for j, b in enumerate(bins):
            if r[b] is None:
                continue
            m, lo, hi, _, _ = r[b]
            ax.plot([j + off, j + off], [lo, hi], color=COL_B[g], lw=2, solid_capstyle="round", zorder=3)
            ax.plot(j + off, m, "o", color=COL_B[g], ms=8, mec="white", mew=1.5, zorder=4,
                    label=LABEL[g] if j == 0 else None)
    ax.axhline(0, color="#2a78d6", lw=1.5, zorder=2)
    ax.text(-0.45, 0.15, "MaxPressure = 0", color=INK2, fontsize=9, ha="left", va="bottom")
    _axes(ax, "Learnt controllers minus MaxPressure (paired by hour; below 0 = less delay than MaxPressure; "
              "bars = 95 % day-bootstrap interval)", "s per vehicle", bins)
    ax.set_ylim(min(-5, ax.get_ylim()[0]), min(12, ax.get_ylim()[1]))
    ax.legend(frameon=False, ncol=len(learners), loc="upper left", fontsize=9)
    top = ax.get_ylim()[1]
    clipped = []
    for g in learners:
        r = paired(D, ybin, g, "maxpressure", hours)
        clipped += [f"{LABEL[g]} {b.split(' (')[0]} {r[b][0]:+.1f} ({r[b][1]:+.1f} to {r[b][2]:+.1f})"
                    for b in bins if r[b] and r[b][2] > top]
    nfq = paired(D, ybin, "nfq_conv", "maxpressure", hours) if "nfq_conv" in groups else None
    note = "Learners pooled over 5 training seeds x simulation seeds."
    if clipped:
        note += " Cut off at the top: " + "; ".join(clipped) + "."
    if nfq:
        note += " NFQ off the scale: " + ", ".join(f"{b.split(' (')[0]} {nfq[b][0]:+.0f}" for b in bins if nfq[b]) + " s/veh."
    ax.text(0, -0.2, note, transform=ax.transAxes, fontsize=8.5, color=INK2)
    fig.tight_layout()
    fig.savefig(FIG / "learners_vs_maxpressure.png", dpi=180)
    plt.close(fig)

    # C: mechanism (simulation seed 2): cycle length and green of the critical left P5
    if agg:
        show = COL_A
        fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
        for ax, key, title, yl in [(axes[0], "cycle", "Mean cycle length", "s"),
                                   (axes[1], "5", "P5 Peachtree-NE left: mean green", "s")]:
            ends = []
            for g, col in show.items():
                ys = [agg[(g, b, key)][1] / agg[(g, b, key)][0] if agg[(g, b, key)][0] else np.nan for b in bins]
                if np.all(np.isnan(ys)):
                    continue
                ax.plot(xs, ys, color=col, lw=2, marker="o", ms=7, mec="white", mew=1.5, zorder=3)
                ends.append((ys[-1], LABEL[g], col))
            _axes(ax, title, yl, bins)
            ax.set_xlim(-0.3, len(bins) - 1 + 0.9)
            _label_ends(ax, ends, len(bins) - 1)
        fig.suptitle("How they do it (simulation seed 2)", fontsize=11, color=INK, x=0.01, ha="left")
        fig.tight_layout()
        fig.savefig(FIG / "mechanism.png", dpi=180)
        plt.close(fig)


def readout():
    """LSTDQ v2f: d = w_end - w_extend per serving phase, mean over training seeds, sign agreement."""
    from atsc.rl.agent import PHASES, dims
    from train_lstdq import out_dir
    per, block, m = dims("v2f")
    ds = []
    for s in range(5):
        f = out_dir(s, "v2f") / "w_it5.npy"
        if f.exists():
            w = np.load(f).reshape(2, m)
            ds.append((w[1] - w[0]).reshape(len(PHASES), block))
    ds = np.array(ds)                                   # seeds x serving phase x block
    # scale: each feature's standard deviation over the states where its phase serves, from LSTDQ v2f seed 0's
    # own decisions on two training windows (AM and PM peak); cached
    f = OUT / "v2f_feature_std.npy"
    if not f.exists():
        from atsc.rl.agent import LSTDQPolicy
        from atsc.sim.episode import run_window
        from train_lstdq import train_days
        X = []
        for date, win in [(train_days()[3], (6.0, 10.0)), (train_days()[3], (15.5, 19.5))]:
            pol = LSTDQPolicy(HERE, w=np.load(out_dir(0, "v2f") / "w_it5.npy"), record=True, version="v2f")
            run_window(HERE, str(date), *win, pol, mode="free", seed=1)
            X.append(pol.samples()[0])
        X = np.concatenate(X).reshape(-1, len(PHASES), block)
        serving = np.abs(X).sum(2) > 0                  # rows x phase: the block in use
        np.save(f, np.array([X[serving[:, i], i].std(0) for i in range(len(PHASES))]))
    sd = np.load(f)                                     # serving phase x block
    raw = ds.copy()
    ds = ds * sd
    names = []
    for p in PHASES:
        names += [f"occ P{p}", f"gap P{p}", f"rate P{p}", f"queue P{p}"]
    names += [f"other ring phase {i + 1}" for i in range(4)] + ["other ring elapsed", "own elapsed", "bias"]
    return ds, names, raw


def _write(name, rows):
    with open(RES / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def export(cond, D, W, groups, ybin, hours, agg, ds, names, raw):
    """tidy tables for diagrams: one row per observation, plain column names, units in the names."""
    bins = [lab for _, _, lab in Y_BINS]
    short_bin = {b: b.split(" (")[0] for b in bins}
    _write("controllers.csv", [{"controller": g, "label": LABEL[g], "family": FAMILY[g][0], "description": FAMILY[g][1],
                                "in_main_comparison": g != "nfq"} for g in groups])
    _write("conditions_by_hour.csv", [{"date": d, "hour": h, "condition": short_bin[ybin[(d, h)]],
                                       **{k: cond[(d, h)][k] for k in ("volume", "Y", "cv5", "imbalance", "left_share")}}
                                      for d, h in hours])
    _write("delay_by_hour.csv", [{"date": d, "hour": h, "condition": short_bin[ybin[(d, h)]], "Y": cond[(d, h)]["Y"],
                                  "controller": g, "label": LABEL[g], "mean_delay_s_per_veh": round(D[(d, h, g)], 2),
                                  "worst_movement_p95_delay_s": round(W[(d, h, g)], 1)}
                                 for d, h in hours for g in groups if (d, h, g) in D])
    rows = []
    for g in groups:
        for sel in [None] + bins:
            hs = [dh for dh in hours if (sel is None or ybin[dh] == sel) and (*dh, g) in D]
            if not hs:
                continue
            row = {"controller": g, "label": LABEL[g], "condition": "all" if sel is None else short_bin[sel],
                   "hours": len(hs)}
            for col, M in [("mean_delay_s_per_veh", D), ("worst_movement_p95_delay_s", W)]:
                per_day = defaultdict(list)
                for dh in hs:
                    per_day[dh[0]].append(M[(*dh, g)])
                per_day = {d: st.mean(v) for d, v in per_day.items()}
                lo, hi = boot_ci(per_day)
                row.update({col: round(st.mean(per_day.values()), 2), col + "_ci_low": round(lo, 2),
                            col + "_ci_high": round(hi, 2)})
            rows.append(row)
    _write("summary_by_condition.csv", rows)
    rows = []
    for g in groups:
        if g == "maxpressure":
            continue
        r = paired(D, ybin, g, "maxpressure", hours)
        for sel in [None] + bins:
            if r[sel]:
                m, lo, hi, pv, n = r[sel]
                rows.append({"controller": g, "label": LABEL[g], "condition": "all" if sel is None else short_bin[sel],
                             "diff_vs_maxpressure_s_per_veh": round(m, 2), "ci_low": round(lo, 2), "ci_high": round(hi, 2),
                             "wilcoxon_p": round(pv, 4), "days": n,
                             "significant": bool(pv < 0.05 and (lo > 0 or hi < 0))})
    _write("paired_vs_maxpressure.csv", rows)
    # every run: overall vehicle-weighted delay over the clean hours (training seed x simulation seed spread)
    acc = defaultdict(lambda: [0.0, 0])
    hs = set(hours)
    for r in csv.DictReader(open(OUT / "hour_mv.csv")):
        if (r["date"], int(r["hour"])) in hs:
            k = (r["controller"], r["seed"])
            acc[k][0] += float(r["mean_s"]) * int(r["veh"])
            acc[k][1] += int(r["veh"])
    rows = []
    for (c, sd), (tot, n) in sorted(acc.items()):
        g = group(c)
        if g not in LABEL:
            continue
        tail = c.rsplit("_", 1)[-1]
        rows.append({"controller": g, "label": LABEL[g], "run": c,
                     "training_seed": int(tail[1:]) if tail[:1] == "s" and tail[1:].isdigit() else (0 if g.startswith("lstdq") else ""),
                     "simulation_seed": int(sd), "vehicles": n, "overall_delay_s_per_veh": round(tot / n, 2)})
    _write("runs_overall.csv", rows)
    if agg:
        rows = []
        for g in groups:
            for b in bins:
                c = agg[(g, b, "cycle")]
                if not c[0]:
                    continue
                for ph in range(1, 9):
                    a = agg[(g, b, str(ph))]
                    rows.append({"controller": g, "label": LABEL[g], "condition": short_bin[b], "phase": ph,
                                 "phase_name": PHASE_NAME[ph], "mean_cycle_s": round(c[1] / c[0], 1),
                                 "mean_green_s": round(a[1] / a[0], 1) if a[0] else "",
                                 "greens_per_cycle": round(a[0] / c[0], 3),
                                 "share_ended_at_max_green": round(a[2] / a[0], 3) if a[0] else ""})
        _write("mechanism_by_condition.csv", rows)
    if len(ds):
        from atsc.rl.agent import PHASES
        rows = []
        for i, p in enumerate(PHASES):
            for k, nm in enumerate(names):
                vals = raw[:, i, k] if nm == "bias" else ds[:, i, k]
                if not np.any(vals):
                    continue
                mean = vals.mean()
                rows.append({"serving_phase": p, "serving_phase_name": PHASE_NAME[p], "feature": nm,
                             "effect_toward_ending_mean": round(float(mean), 4),
                             **{f"seed{s}": round(float(v), 4) for s, v in enumerate(vals)},
                             "seeds_agreeing_in_sign": int((np.sign(raw[:, i, k]) == np.sign(raw[:, i, k].mean())).sum())})
        _write("lstdq_v2f_learnt_rule.csv", rows)


def main():
    cond, D, W, groups, ybin, runs_of = load()
    FIG.mkdir(parents=True, exist_ok=True)
    compare = [g for g in groups if g != "nfq"]
    hours = sorted({(d, h) for d, h, _ in D if all((d, h, g) in D for g in compare)})
    bins = [lab for _, _, lab in Y_BINS]
    L = ["# RQ1 analysis: paired tests, mechanism, learnt rule (SIG 7065, validation weekdays)", "",
         f"{len(hours)} clean hours on {len({d for d, _ in hours})} days. Learners pooled over training x simulation "
         "seeds; rule controllers over 3 simulation seeds. Runs per controller: "
         + ", ".join(f"{LABEL[g]} {len(runs_of[g])}" for g in groups) + ".", "",
         "**Limitations (every result):** isolated model of a signal in GDOT's coordinated Peachtree group; the "
         "simulation is not yet accepted by its own validation (VALIDATION.md: V1 split, V2 gap-outs, V5 overflow "
         "days fail, mostly the left-turn phases); P2 count suspect; right turns uncounted.", ""]
    # 1. paired vs MaxPressure
    L += ["## 1. Difference from MaxPressure, paired by hour (s/veh; negative = less delay than MaxPressure)", "",
          "Mean over days of the daily mean difference (95 % day-bootstrap), Wilcoxon signed-rank p over days. "
          "**Bold** = interval excludes 0 and p < 0.05 (no multiple-test correction; "
          f"{(len(compare) - 1) * (len(bins) + 1)} tests in this table).", "",
          "| Controller | all hours | " + " | ".join(bins) + " |", "|---|---|" + "---|" * len(bins)]
    for g in compare:
        if g == "maxpressure":
            continue
        r = paired(D, ybin, g, "maxpressure", hours)
        L.append(f"| {LABEL[g]} | " + " | ".join(fmt_pair(r[s]) for s in [None] + bins) + " |")
    L.append("")
    # top learners against each other
    top = [g for g in ("lstdq v2f", "lstdq v2", "ars", "lstdq v1") if g in groups]
    L += ["## 2. Top learners against each other (row - column, all hours, s/veh)", "",
          "| | " + " | ".join(LABEL[g] for g in top[1:]) + " |", "|---|" + "---|" * (len(top) - 1)]
    for i, a in enumerate(top[:-1]):
        L.append(f"| {LABEL[a]} | " + " | ".join("" if j <= i else fmt_pair(paired(D, ybin, a, b, hours)[None])
                                                   for j, b in enumerate(top[1:], 1)) + " |")
    L.append("")
    # ranks per bin
    L += ["## 3. Rank by condition (mean delay; ties within 0.5 s/veh share a rank)", "",
          "| Controller | " + " | ".join(bins) + " |", "|---|" + "---|" * len(bins)]
    means = {(g, b): st.mean(D[(*dh, g)] for dh in hours if ybin[dh] == b) for g in compare for b in bins}
    for g in compare:
        cells = []
        for b in bins:
            rank = 1 + sum(means[(o, b)] < means[(g, b)] - 0.5 for o in compare)
            cells.append(f"{rank} ({means[(g, b)]:.1f})")
        L.append(f"| {LABEL[g]} | " + " | ".join(cells) + " |")
    L.append("")
    # 4. mechanism
    agg = mechanism(groups, ybin, cond)
    if agg:
        L += ["## 4. Mechanism by condition (simulation seed 2)", "",
              "Cycle = mean cycle length (s). Max-out = share of greens ended at max green. Then mean green (s) "
              "and greens per cycle (1.00 = served every cycle; lower = skipped) for the two critical phases at "
              "peak: P8 Piedmont-N through and P5 Peachtree-NE left.", "",
              "| Controller | " + " | ".join(f"{b.split(' (')[0]}: cycle / max-out / P8 green, per cycle / P5 green, per cycle"
                                          for b in bins) + " |", "|---|" + "---|" * len(bins)]
        for g in compare:
            cells = []
            for b in bins:
                c = agg[(g, b, "cycle")]
                if not c[0]:
                    cells.append("-")
                    continue
                tot = [agg[(g, b, str(p))] for p in range(1, 9)]
                mx = sum(t[2] for t in tot) / max(1, sum(t[0] for t in tot))
                p8, p5 = agg[(g, b, "8")], agg[(g, b, "5")]
                cells.append(f"{c[1] / c[0]:.0f} / {100 * mx:.0f} % / {p8[1] / max(1, p8[0]):.0f} s, {p8[0] / c[0]:.2f}"
                             f" / {p5[1] / max(1, p5[0]):.0f} s, {p5[0] / c[0]:.2f}")
            L.append(f"| {LABEL[g]} | " + " | ".join(cells) + " |")
        L.append("")
    figures(D, W, compare, ybin, cond, hours, agg)
    L += ["Figures and tidy data: `results/` (README.md there).", ""]
    # 5. learnt rule
    ds, names, raw = readout()
    if len(ds):
        L += ["## 5. What LSTDQ v2f learnt: when it ends a green", "",
              f"d = w(end) - w(extend) per serving phase, mean over {len(ds)} training seeds; the controller ends "
              "the green when d . x > 0. Each weight is multiplied by its feature's standard deviation in the "
              "states where that phase serves (LSTDQ v2f's own decisions, AM and PM peak of one training day), so "
              "a value is the push towards ending (+) or extending (-) from a typical change in that feature. "
              "Bias: the raw weight. Positive gap = a longer gap since the last vehicle pushes towards ending "
              "(as gap-out does). (n/5) = training seeds agreeing in sign.", "",
              "| Serving phase | own gap | own queue | own occupancy | own rate | own elapsed | bias | strongest other-phase terms |",
              "|---|---|---|---|---|---|---|---|"]
        from atsc.rl.agent import PHASES
        mean, agree = ds.mean(0), (np.sign(raw) == np.sign(raw.mean(0))).sum(0)      # sign: sd > 0 keeps it
        ds_raw_bias = raw[:, :, -1].mean(0)
        for i, p in enumerate(PHASES):
            if not np.any(mean[i]):
                continue
            j = PHASES.index(p) * 4
            cell = lambda k: f"{mean[i, k]:+.2f} ({agree[i, k]}/{len(ds)})"  # noqa: E731
            mean[i, len(names) - 1] = ds_raw_bias[i]
            others = [k for k in range(len(PHASES) * 4) if k // 4 != PHASES.index(p) and k % 4 in (1, 3)]
            others = sorted(others, key=lambda k: -abs(mean[i, k]))[:3]
            L.append(f"| {PHASE_NAME[p]} | {cell(j + 1)} | {cell(j + 3)} | {cell(j)} | {cell(j + 2)} | "
                     f"{cell(len(names) - 2)} | {cell(len(names) - 1)} | "
                     + ", ".join(f"{names[k]} {cell(k)}" for k in others) + " |")
        L.append("")
    export(cond, D, W, groups, ybin, hours, agg, *readout())
    (OUT / "analysis.md").write_text("\n".join(L) + "\n")
    (RES / "analysis.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
