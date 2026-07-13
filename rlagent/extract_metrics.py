"""Extract compact, commit-friendly metric CSVs from the (huge, git-ignored)
tripinfo XMLs and per-seed training logs, so the CI graph and the cumulative-
reward diagram can be rebuilt on any machine without the ~50 GB of raw sim
artifacts.

Outputs (under rlagent/results_metrics/):
  ci_delays.csv       one row per (variant, seed, scale): peak total delay (s).
                      Plus 'fixed' rows (seed=-1) = Webster baseline per scale.
                      -> everything needed to bootstrap the CI graph.
  training_curves.csv one row per (variant, seed, episode): total_reward and
                      cumulative reward (+ day/scale/decisions/switches/wall).
                      -> the cumulative-reward-over-time diagram.
"""
from __future__ import annotations

import csv
import glob
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.insert(0, os.path.join(
    HERE, "experiments", "EXP-003_spillback-features", "data"))
from peak_delay import peak_total_delay  # noqa: E402

OUT = os.path.join(HERE, "results_metrics")
os.makedirs(OUT, exist_ok=True)

SCALES = (0.5, 0.8, 1.0, 1.3, 1.8)
FIXED = {0.5: 43.1, 0.8: 63.1, 1.0: 230., 1.3: 912., 1.8: 4878.}
N = 20

# tripinfo dir per (variant, seed): existing seeds under results/, new under ci/
def _locs(reldir, existing):
    m = dict(existing)
    for s in range(N):
        m.setdefault(s, f"{reldir}/s{s}")
    return m

LOC = {
    "pg_raw":     _locs("ci/pg_raw",     {0: "results/exp002_phasegated"}),
    "pg_norm":    _locs("ci/pg_norm",    {0: "results/exp003_norm"}),
    "pg_elapsed": _locs("ci/pg_elapsed", {0: "results/exp003b_v3/s0",
                                          1: "results/exp003b_v3/s1",
                                          2: "results/exp003b_v3/s2",
                                          3: "results/exp003b_v3/s3",
                                          4: "results/exp003b_v3/s4"}),
}


# ---- 1. CI delays --------------------------------------------------------
rows = []
for v in LOC:
    for s in range(N):
        for sc in SCALES:
            ti = os.path.join(HERE, LOC[v][s], f"ti_heldout_rl_x{sc}.xml")
            if not os.path.exists(ti):
                continue
            try:
                n_peak, d = peak_total_delay(ti)
            except Exception:
                continue
            rows.append((v, s, sc, round(d, 1), n_peak))
for sc in SCALES:                    # baseline rows
    rows.append(("fixed", -1, sc, FIXED[sc], ""))

with open(os.path.join(OUT, "ci_delays.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["variant", "seed", "scale", "peak_total_delay_s", "n_peak_trips"])
    w.writerows(sorted(rows, key=lambda r: (str(r[0]), r[2], r[1])))
print(f"ci_delays.csv: {len(rows)} rows "
      f"({sum(1 for r in rows if r[0]!='fixed')} RL + {len(SCALES)} fixed)")


# ---- 2. Training curves (cumulative reward) ------------------------------
# gather every per-seed training log; tag variant+seed from its path
TRAIN_GLOBS = {
    "pg_raw":     ["ci/pg_raw/s*/train_random_s*.csv",
                   "results/exp002_phasegated/train_random_s0.csv"],
    "pg_norm":    ["ci/pg_norm/s*/train_random_s*.csv",
                   "results/exp003_norm/train_random_s0.csv"],
    "pg_elapsed": ["ci/pg_elapsed/s*/train_random_s*.csv",
                   "results/exp003_v3/train_random_s0.csv"],
}
tc_rows, covered = [], {}
for v, patterns in TRAIN_GLOBS.items():
    seen = set()
    for pat in patterns:
        for path in glob.glob(os.path.join(HERE, pat)):
            m = re.search(r"train_random_s(\d+)\.csv$", path)
            if not m:
                continue
            seed = int(m.group(1))
            if seed in seen:
                continue
            seen.add(seed)
            cum = 0.0
            with open(path) as fh:
                for r in csv.DictReader(fh):
                    rew = float(r["total_reward"])
                    cum += rew
                    tc_rows.append((v, seed, int(r["episode"]), r["date"],
                                    r["scale"], f"{rew:.0f}", f"{cum:.0f}",
                                    r["decisions"], r["switches"], r["wall_s"]))
    covered[v] = sorted(seen)

with open(os.path.join(OUT, "training_curves.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["variant", "seed", "episode", "day", "scale", "reward",
                "cumulative_reward", "decisions", "switches", "wall_s"])
    w.writerows(sorted(tc_rows, key=lambda r: (r[0], r[1], r[2])))
print(f"training_curves.csv: {len(tc_rows)} rows")
for v, seeds in covered.items():
    print(f"  {v}: {len(seeds)} seeds with training logs {seeds}")
