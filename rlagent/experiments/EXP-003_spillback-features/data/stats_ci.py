"""Bootstrap confidence intervals for the RL-vs-fixed comparison (EXP-003).

Pure numpy (scipy/matplotlib not installed). Computes, per demand scale:
  - bootstrap CI (percentile method) on the MEDIAN and MEAN peak total delay
    across TRAINING seeds -- the resampling unit is the independent training
    run, NOT per-trip delays (that would measure the wrong variance; see
    experiments/README methodology / the stats discussion).
  - the paired difference vs the fixed-time baseline: bootstrap CI on
    (median seed delay - fixed). If that CI lies entirely > 0 the variant is
    distinguishably WORSE than fixed; entirely < 0, distinguishably better;
    straddling 0, not distinguishable at this n.
  - Wilson score CI on the parking-collapse RATE (a binomial proportion).

IMPORTANT (n): only phase_gated_v3 has multiple training seeds (n=5, seeds
0-4). phase_gated (EXP-002) and phase_gated_norm each have n=1 on disk, so
NO training-seed CI can be formed for them yet -- they need the multi-seed
retrain (EXP-003c-stat) before they can appear here. This script reports what
is honestly computable now (v3) and leaves the others as pending.

n=5 gives coarse, wide intervals -- reported honestly, not smoothed. Bump the
seed count (n>=10) to narrow them; B (bootstrap iters) does NOT narrow a CI,
it only sharpens the percentile estimate.
"""

import numpy as np

RNG = np.random.default_rng(0)
B = 10000          # bootstrap iterations (resamples of the existing seeds)
ALPHA = 0.05       # 95% CI

# --- data on disk: peak-window TOTAL delay (s), day 0508 --------------------
# phase_gated_v3, per TRAINING seed (data/multiseed_per_seed_delay.txt)
V3 = {
    1.0: np.array([786., 489., 185., 575., 430.]),
    1.3: np.array([8910., 1403., 4420., 1855., 1673.]),
    1.8: np.array([7149., 5899., 5842., 6899., 3042.]),
}
# Webster fixed-time baseline, single deterministic plan (point value per scale)
FIXED = {1.0: 230., 1.3: 912., 1.8: 4878.}
# single-seed variants (n=1) -- point values only, cannot CI yet
NORM_1SEED = {1.0: 1119., 1.3: 2747., 1.8: 9355.}
EXP2_1SEED = {1.0: 1291., 1.3: 3709., 1.8: 10388.}


def boot_ci(x, stat, b=B, alpha=ALPHA):
    x = np.asarray(x, float)
    idx = RNG.integers(0, len(x), size=(b, len(x)))
    dist = stat(x[idx], axis=1)
    lo, hi = np.percentile(dist, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return stat(x), lo, hi


def wilson_ci(k, n, alpha=ALPHA):
    """Wilson score interval for a binomial proportion k/n."""
    from math import sqrt
    z = 1.959963984540054  # normal 0.975 quantile (hardcoded; no scipy)
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, centre - half, centre + half


print("=" * 74)
print("EXP-003  bootstrap 95% CIs -- peak total delay (s), day 0508")
print(f"B={B} resamples over TRAINING seeds; n=5 (v3 only)")
print("=" * 74)

for scale in (1.0, 1.3, 1.8):
    v3 = V3[scale]
    fx = FIXED[scale]
    med, mlo, mhi = boot_ci(v3, lambda a, axis=None: np.median(a, axis=axis))
    mean, alo, ahi = boot_ci(v3, lambda a, axis=None: np.mean(a, axis=axis))
    # paired difference vs fixed (fixed is constant -> shift of the median CI)
    dmed, dlo, dhi = boot_ci(v3 - fx,
                             lambda a, axis=None: np.median(a, axis=axis))
    if dlo > 0:
        verdict = "WORSE than fixed (CI excludes 0, >0)"
    elif dhi < 0:
        verdict = "BETTER than fixed (CI excludes 0, <0)"
    else:
        verdict = "NOT distinguishable from fixed (CI straddles 0)"
    print(f"\n--- {scale:.1f}x  (fixed baseline = {fx:.0f} s) ---")
    print(f"  v3 seeds:            {np.sort(v3).astype(int).tolist()}")
    print(f"  v3 median delay:     {med:7.0f} s   95% CI [{mlo:6.0f}, {mhi:6.0f}]")
    print(f"  v3 mean   delay:     {mean:7.0f} s   95% CI [{alo:6.0f}, {ahi:6.0f}]")
    print(f"  v3 - fixed (median): {dmed:+7.0f} s   95% CI [{dlo:+6.0f}, {dhi:+6.0f}]")
    print(f"  verdict:  v3 is {verdict}")
    print(f"  (norm n=1: {NORM_1SEED[scale]:.0f} s;  exp2 n=1: {EXP2_1SEED[scale]:.0f} s "
          f"-- no CI until multi-seed)")

# --- parking-collapse rate (the headline robustness metric) ----------------
k, n = 2, 5   # 2 of 5 v3 seeds parked (seed0, seed2)
p, plo, phi = wilson_ci(k, n)
print("\n" + "=" * 74)
print("v3 parking-collapse RATE (binomial, Wilson 95% CI)")
print(f"  {k}/{n} seeds parked  ->  p = {p:.0%}   95% CI [{plo:.0%}, {phi:.0%}]")
print("  (very wide at n=5 -- exactly why more seeds are needed to pin the rate)")
print("=" * 74)
