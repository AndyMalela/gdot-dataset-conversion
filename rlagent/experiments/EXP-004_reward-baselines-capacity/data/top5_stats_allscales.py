"""Mean + exact Wilcoxon p vs baselines, top-5 EXP-004 arms, at
0.5x / 0.8x / 1.0x / 1.3x (per user request -- 1.8x dropped, it's
extrapolation-only for these arms and was never the target).

Reads every seed's tripinfo directly through the canonical peak-delay
pipeline (no hand-transcribed numbers -- avoids the earlier rate/seed7
placeholder mistake). A seed is auto-excluded from a given scale's summary
if its completed-peak-trip count is >10% below that scale's known-good
reference (gridlock/incomplete-eval signature), and the exclusion is
reported explicitly, not silently dropped.
"""
import os
import sys

import numpy as np
from itertools import product

HERE = os.path.dirname(os.path.abspath(__file__))
RLAGENT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(
    RLAGENT, "experiments", "EXP-003_spillback-features", "data"))
from peak_delay import peak_total_delay  # noqa: E402

SCALES = [0.5, 0.8, 1.0, 1.3]
# known-good peak-trip counts per scale (seen consistently across every
# healthy run to date) -- <90% of this signals gridlock/incomplete eval.
REF_N = {0.5: 6209, 0.8: 9859, 1.0: 12322, 1.3: 16026}

BASELINE_TI = {
    "Webster":       "results/exp002_phasegated/ti_heldout_fixed_x{s}.xml",
    "tuned-actuated": "results/actuated/ti_actuated_tuned_x{s}.xml",
}

# (label, dir-pattern, n_seeds)
ARMS = [
    ("EXP-004a",   "ci/exp004a/s{n}",     10),
    ("S2-rate",    "ci/race/rate/s{n}",   10),
    ("S3-age",     "ci/race/age/s{n}",    10),
    ("S4-rate+age", "ci/race/rateage/s{n}", 10),
    ("S8-permaxes", "ci/race/ratemg/s{n}", 15),
]


def delay_at(path, scale):
    ti = path.format(s=scale) if "{s}" in path else path
    ti = os.path.join(RLAGENT, ti)
    if not os.path.exists(ti):
        return None
    n, d = peak_total_delay(ti)
    ref = REF_N[scale]
    ok = n >= 0.9 * ref
    return d, n, ok


def exact_wilcoxon_two_sided(diffs):
    d = np.asarray([x for x in diffs if x != 0.0], float)
    n = len(d)
    if n == 0:
        return float("nan"), 0
    ranks = np.argsort(np.argsort(np.abs(d))) + 1.0
    ad = np.abs(d)
    for v in np.unique(ad):
        m = ad == v
        if m.sum() > 1:
            ranks[m] = ranks[m].mean()
    total = ranks.sum()
    w_pos = ranks[d > 0].sum()
    if n <= 15:
        stats = np.array([sum(r for r, s in zip(ranks, signs) if s)
                          for signs in product((0, 1), repeat=n)])
        obs = abs(w_pos - total / 2)
        p = float(np.mean(np.abs(stats - total / 2) >= obs - 1e-9))
    else:
        mu, sd = n * (n + 1) / 4, (n * (n + 1) * (2 * n + 1) / 24) ** 0.5
        from math import erf, sqrt
        z = (w_pos - mu) / sd
        p = 2 * (1 - 0.5 * (1 + erf(abs(z) / sqrt(2))))
    return p, n


# ---- baselines, all 4 scales ------------------------------------------
base = {}
for name, pat in BASELINE_TI.items():
    base[name] = {}
    for s in SCALES:
        r = delay_at(pat, s)
        base[name][s] = r[0] if r else None

print("BASELINES (peak total delay, s):")
print(f"  {'':14s}" + "".join(f"  x{s:<6}" for s in SCALES))
for name in base:
    print(f"  {name:14s}" + "".join(f" {base[name][s]:7.1f}" for s in SCALES))

# ---- arms ---------------------------------------------------------------
# A seed is judged degenerate/untrustworthy using the ALREADY-ESTABLISHED
# criterion at 1.3x (the report's own disclosed standard: <90% of that
# scale's peak-trip count = gridlock/incomplete). That verdict is then
# applied to ALL 4 scales for that seed -- not re-derived per scale --
# because a degenerate policy can still "pass" a completion check at low
# load (no insertion backlog forms when demand is trivial) while still
# producing catastrophic per-vehicle delay (confirmed: rate/seed3 completes
# 100% of trips at 0.5x/0.8x yet reports 5605s/11222s -- an order of
# magnitude above every healthy seed). Re-deriving the check independently
# per scale would silently let exactly this contamination back in.
for label, pat, n_seeds in ARMS:
    excluded_seeds = {}   # seed -> reason, decided once at 1.3x
    for n in range(n_seeds):
        ti = os.path.join(RLAGENT, pat.format(n=n), "ti_heldout_rl_x1.3.xml")
        if not os.path.exists(ti):
            excluded_seeds[n] = "no 1.3x eval"
            continue
        npk, _ = peak_total_delay(ti)
        if npk < 0.9 * REF_N[1.3]:
            excluded_seeds[n] = f"gridlocked at 1.3x ({npk}/{REF_N[1.3]} peak trips)"

    print(f"\n{'='*100}\n{label}"
          + (f"   [seeds excluded from ALL scales: {excluded_seeds}]"
             if excluded_seeds else "") + f"\n{'='*100}")
    print(f"  {'scale':>6} {'n':>3} {'mean':>7} {'median':>7} {'min':>6} {'max':>6} "
          f"| vs Webster | vs tuned-actuated")
    for s in SCALES:
        vals, excluded = [], []
        for n in range(n_seeds):
            if n in excluded_seeds:
                excluded.append((n, excluded_seeds[n]))
                continue
            sdir = os.path.join(RLAGENT, pat.format(n=n))
            ti = os.path.join(sdir, f"ti_heldout_rl_x{s}.xml")
            if not os.path.exists(ti):
                excluded.append((n, "no eval at this scale"))
                continue
            npk, d = peak_total_delay(ti)
            vals.append(d)
        if not vals:
            print(f"  x{s:<5} -- no valid seeds --")
            continue
        x = np.array(vals)
        cells = []
        for bname in ("Webster", "tuned-actuated"):
            b = base[bname][s]
            p, n = exact_wilcoxon_two_sided(x - b)
            direction = "below" if np.median(x) < b else "above"
            sig = "*" if (p == p and p < 0.05) else " "
            cells.append(f"p={p:.4f}{sig} {direction}" if n else "n/a")
        exc_note = f"  [excl: {excluded}]" if excluded else ""
        print(f"  x{s:<5} {len(vals):>3} {x.mean():7.0f} {np.median(x):7.0f} "
              f"{x.min():6.0f} {x.max():6.0f} | {cells[0]:<16s} | {cells[1]}{exc_note}")

print(f"\n{'='*100}")
print("* p<0.05 (exact two-sided Wilcoxon signed-rank, full enumeration n<=15,")
print("  normal approx n>15). Exclusions: a seed's tripinfo with <90% of that")
print("  scale's known-good peak-trip count signals gridlock/incomplete eval")
print("  (same disclosure standard as EXP-004a seed 5 / rate seed 3 in the report).")
