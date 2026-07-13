"""Rebuild the two figures from the committed metric CSVs (results_metrics/).
Needs matplotlib (not installed in the training env -- run on your workstation:
`pip install matplotlib`). Pure-stdlib + numpy + matplotlib.

  python3 plot_metrics.py            # writes both PNGs into results_metrics/
Figures:
  ci_delay_vs_scale.png   median peak total delay vs demand scale, per variant,
                          with 95% bootstrap CI bands, plus the fixed-time line.
  cumulative_reward.png   cumulative training reward vs episode (per-seed faint
                          lines + per-variant mean), one panel per variant.
"""
import csv
import os
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
MET = os.path.join(HERE, "results_metrics")
SCALES = [0.5, 0.8, 1.0, 1.3, 1.8]
VARIANTS = ["pg_raw", "pg_norm", "pg_elapsed"]
LABEL = {"pg_raw": "PG-raw", "pg_norm": "PG-norm", "pg_elapsed": "PG-elapsed"}
COLOR = {"pg_raw": "#1f77b4", "pg_norm": "#2ca02c", "pg_elapsed": "#d62728"}
RNG = np.random.default_rng(0)


def boot_median_ci(x, b=10000):
    x = np.asarray(x, float)
    idx = RNG.integers(0, len(x), size=(b, len(x)))
    d = np.median(x[idx], axis=1)
    return np.median(x), *np.percentile(d, [2.5, 97.5])


# ---- load ----------------------------------------------------------------
delays = defaultdict(list)     # (variant, scale) -> [delay,...]
fixed = {}
for r in csv.DictReader(open(os.path.join(MET, "ci_delays.csv"))):
    sc = float(r["scale"]); d = float(r["peak_total_delay_s"])
    if r["variant"] == "fixed":
        fixed[sc] = d
    else:
        delays[(r["variant"], sc)].append(d)

curves = defaultdict(dict)     # variant -> seed -> {episode: cum_reward}
for r in csv.DictReader(open(os.path.join(MET, "training_curves.csv"))):
    curves[r["variant"]].setdefault(int(r["seed"]), {})[int(r["episode"])] = \
        float(r["cumulative_reward"])

# ---- figure 1: CI delay vs scale -----------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
for v in VARIANTS:
    med, lo, hi = [], [], []
    for sc in SCALES:
        m, l, h = boot_median_ci(delays[(v, sc)])
        med.append(m); lo.append(l); hi.append(h)
    ax.plot(SCALES, med, "-o", color=COLOR[v], label=LABEL[v])
    ax.fill_between(SCALES, lo, hi, color=COLOR[v], alpha=0.18)
ax.plot(SCALES, [fixed[s] for s in SCALES], "k--s", label="fixed-time (Webster)")
ax.set_yscale("log")
ax.set_xlabel("demand scale (v/c: 0.5x=0.62 ... 1.8x=1.66)")
ax.set_ylabel("peak total delay (s), median + 95% CI")
ax.set_title("EXP-003c-stat: delay vs load, n=20 (day 0508)")
ax.legend(); ax.grid(True, which="both", alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(MET, "ci_delay_vs_scale.png"), dpi=130)
print("wrote ci_delay_vs_scale.png")

# ---- figure 2: cumulative reward -----------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), sharey=True)
for ax, v in zip(axes, VARIANTS):
    eps = sorted({e for sd in curves[v].values() for e in sd})
    allc = []
    for seed, sd in curves[v].items():
        y = [sd.get(e, np.nan) for e in eps]
        ax.plot(eps, y, color=COLOR[v], alpha=0.20, lw=0.8)
        allc.append(y)
    mean = np.nanmean(np.array(allc, float), axis=0)
    ax.plot(eps, mean, color=COLOR[v], lw=2.5, label=f"mean (n={len(curves[v])})")
    ax.set_title(LABEL[v]); ax.set_xlabel("episode")
    ax.legend(); ax.grid(True, alpha=0.3)
axes[0].set_ylabel("cumulative training reward")
fig.suptitle("Cumulative reward over training (per-seed faint, mean bold). "
             "NB: reward not comparable across episodes (random day x scale).")
fig.tight_layout()
fig.savefig(os.path.join(MET, "cumulative_reward.png"), dpi=130)
print("wrote cumulative_reward.png")
