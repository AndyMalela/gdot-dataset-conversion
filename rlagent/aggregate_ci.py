"""Aggregate all available seeds (existing + newly trained) into per-variant
CI tables vs the fixed-time baseline. Reads every seed's tripinfo through the
canonical peak-delay pipeline, so old and new seeds are measured identically.

Runs on whatever seeds have completed so far -> usable partial results at any
point during the batch (n grows as workers finish). Pure numpy.
"""
from __future__ import annotations

import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
import sys
sys.path.insert(0, os.path.join(
    HERE, "experiments", "EXP-003_spillback-features", "data"))
from peak_delay import peak_total_delay  # noqa: E402

SCALES = (0.5, 0.8, 1.0, 1.3, 1.8)
FIXED = {0.5: 43.1, 0.8: 63.1, 1.0: 230., 1.3: 912., 1.8: 4878.}  # Webster (det.)
MAXSEED = int(os.environ.get("MAXSEED", "19"))
B, RNG = 10000, np.random.default_rng(0)

# where each seed's RL tripinfos live (existing seeds in place; new under ci/)
def locs(variant, existing):
    m = dict(existing)
    reldir = {"pg_raw": "ci/pg_raw", "pg_norm": "ci/pg_norm",
              "pg_elapsed": "ci/pg_elapsed"}[variant]
    for s in range(0, MAXSEED + 1):
        m.setdefault(s, os.path.join(reldir, f"s{s}"))
    return m

# Paths are relative to HERE (rlagent/): existing seeds live under results/,
# newly trained seeds under ci/. (Earlier bug: a single results/ prefix sent
# the ci/ dirs to results/ci/... which don't exist, hiding all new seeds.)
LOC = {
    "pg_raw":     locs("pg_raw",     {0: "results/exp002_phasegated"}),
    "pg_norm":    locs("pg_norm",    {0: "results/exp003_norm"}),
    "pg_elapsed": locs("pg_elapsed", {0: "results/exp003b_v3/s0",
                                      1: "results/exp003b_v3/s1",
                                      2: "results/exp003b_v3/s2",
                                      3: "results/exp003b_v3/s3",
                                      4: "results/exp003b_v3/s4"}),
}


def delay(variant, seed, scale):
    ti = os.path.join(HERE, LOC[variant][seed], f"ti_heldout_rl_x{scale}.xml")
    if not os.path.exists(ti):
        return None
    try:                       # a worker may be mid-write -> incomplete XML
        return peak_total_delay(ti)[1]
    except Exception:
        return None            # skip until the file is fully written


def boot_ci(x, stat, b=B):
    x = np.asarray(x, float)
    idx = RNG.integers(0, len(x), size=(b, len(x)))
    d = stat(x[idx], axis=1)
    lo, hi = np.percentile(d, [2.5, 97.5])
    return stat(x), lo, hi


def wilson(k, n):
    from math import sqrt
    if n == 0:
        return float("nan"), float("nan"), float("nan")
    z = 1.959963984540054
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return p, c - h, c + h


print("=" * 78)
print("EXP-003c-stat: multi-seed peak total delay (s), day 0508, vs fixed-time")
print("=" * 78)
med = lambda a, axis=None: np.median(a, axis=axis)
for variant in ("pg_raw", "pg_norm", "pg_elapsed"):
    print(f"\n### {variant}")
    for scale in SCALES:
        vals = [delay(variant, s, scale) for s in range(0, MAXSEED + 1)]
        vals = [v for v in vals if v is not None]
        n = len(vals)
        fx = FIXED[scale]
        if n < 2:
            got = f"{vals[0]:.0f}" if n == 1 else "-"
            print(f"  {scale:.1f}x  n={n:<2}  delay={got:>8}  (need n>=2 for CI)")
            continue
        m, mlo, mhi = boot_ci(vals, med)
        dm, dlo, dhi = boot_ci(np.array(vals) - fx, med)
        verd = ("WORSE" if dlo > 0 else "BETTER" if dhi < 0 else "n.s.")
        print(f"  {scale:.1f}x  n={n:<2}  median={m:7.0f} [{mlo:6.0f},{mhi:6.0f}]"
              f"  vs fixed {fx:>5.0f}: {dm:+7.0f} [{dlo:+7.0f},{dhi:+7.0f}] {verd}")
    # parking-collapse rate at 1.3x (delay > 3000 s ~ a parked seed)
    v13 = [delay(variant, s, 1.3) for s in range(0, MAXSEED + 1)]
    v13 = [v for v in v13 if v is not None]
    if v13:
        k = sum(1 for v in v13 if v > 3000)
        p, plo, phi = wilson(k, len(v13))
        print(f"  parking@1.3x (>3000s): {k}/{len(v13)} = {p:.0%} "
              f"[{plo:.0%},{phi:.0%}]")
print("\n" + "=" * 78)
print("n.s. = not distinguishable from fixed (95% CI of paired diff straddles 0)")
print("=" * 78)
