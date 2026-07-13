"""Final CI + significance analysis for EXP-003c-stat (run once the batch is at
n=20 for all three variants). Pure numpy (no scipy).

Produces, at a fixed equal n:
  1. per-variant peak total delay: median [bootstrap 95% CI], paired diff vs the
     fixed-time baseline [CI] + verdict, parking rate [Wilson CI];
  2. variant-vs-variant comparisons -- these are SEED-PAIRED (pg_raw sN, pg_norm
     sN, pg_elapsed sN share the same training rng seed N, so demand sampling is
     matched), so we use the paired median difference [bootstrap CI] + a paired
     Wilcoxon signed-rank p-value, Holm-corrected across the whole family of
     comparisons (controls family-wise error -- the multiple-comparison guard).

Writes the tables to experiments/EXP-003_spillback-features/data/ci_final.txt.
"""
from __future__ import annotations

import os
from math import erf, sqrt

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.insert(0, os.path.join(
    HERE, "experiments", "EXP-003_spillback-features", "data"))
from peak_delay import peak_total_delay  # noqa: E402

SCALES = (0.5, 0.8, 1.0, 1.3, 1.8)
FIXED = {0.5: 43.1, 0.8: 63.1, 1.0: 230., 1.3: 912., 1.8: 4878.}
N = int(os.environ.get("N", "20"))          # equal n (seeds 0..N-1)
B, RNG = 10000, np.random.default_rng(0)
VARIANTS = ("pg_raw", "pg_norm", "pg_elapsed")


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


_CACHE = {}


def delay(variant, seed, scale):
    key = (variant, seed, scale)
    if key in _CACHE:                      # memoize: parse each 20-40MB XML once
        return _CACHE[key]
    ti = os.path.join(HERE, LOC[variant][seed], f"ti_heldout_rl_x{scale}.xml")
    val = None
    if os.path.exists(ti):
        try:
            val = peak_total_delay(ti)[1]
        except Exception:                  # worker may be mid-write
            val = None
    _CACHE[key] = val
    return val


def series(variant, scale):
    """Return dict seed->delay for seeds 0..N-1 that have a value."""
    return {s: delay(variant, s, scale) for s in range(N)
            if delay(variant, s, scale) is not None}


def boot_ci(x, stat):
    x = np.asarray(x, float)
    idx = RNG.integers(0, len(x), size=(B, len(x)))
    d = stat(x[idx], axis=1)
    return stat(x), *np.percentile(d, [2.5, 97.5])


def wilson(k, n):
    if n == 0:
        return (float("nan"),) * 3
    z = 1.959963984540054
    p, den = k / n, 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return p, c - h, c + h


def _phi(z):
    return 0.5 * (1 + erf(z / sqrt(2)))


def wilcoxon_p(diffs):
    """Two-sided paired Wilcoxon signed-rank p (normal approx, tie/zero-safe)."""
    d = np.asarray([v for v in diffs if v != 0], float)
    n = len(d)
    if n < 6:
        return float("nan"), n
    order = np.argsort(np.abs(d))
    ranks = np.empty(n)
    ranks[order] = np.arange(1, n + 1)
    # average ranks for ties in |d|
    ad = np.abs(d)
    for v in np.unique(ad):
        m = ad == v
        if m.sum() > 1:
            ranks[m] = ranks[m].mean()
    Wp = ranks[d > 0].sum()
    mu, sd = n * (n + 1) / 4, sqrt(n * (n + 1) * (2 * n + 1) / 24)
    z = (Wp - mu) / sd
    return 2 * (1 - _phi(abs(z))), n


def holm(pvals):
    """Holm-Bonferroni: return dict key->(p_raw, p_adj, reject@0.05)."""
    items = [(k, p) for k, p in pvals.items() if p == p]  # drop nan
    items.sort(key=lambda kv: kv[1])
    m, out, running = len(items), {}, 0.0
    for i, (k, p) in enumerate(items):
        adj = min(1.0, max(running, (m - i) * p))
        running = adj
        out[k] = (p, adj, adj < 0.05)
    for k, p in pvals.items():
        out.setdefault(k, (p, float("nan"), False))
    return out


med = lambda a, axis=None: np.median(a, axis=axis)
lines = []


def emit(s=""):
    print(s)
    lines.append(s)


emit("=" * 80)
emit(f"EXP-003c-stat FINAL: peak total delay (s), day 0508, equal n={N}")
emit("=" * 80)

# per-variant vs fixed
avail = {}
for v in VARIANTS:
    emit(f"\n### {v}")
    for sc in SCALES:
        ser = series(v, sc)
        avail[(v, sc)] = ser
        vals = list(ser.values())
        n = len(vals)
        fx = FIXED[sc]
        if n < 2:
            emit(f"  {sc:.1f}x  n={n}  (insufficient)")
            continue
        m, lo, hi = boot_ci(vals, med)
        dm, dlo, dhi = boot_ci(np.array(vals) - fx, med)
        verd = "WORSE" if dlo > 0 else "BETTER" if dhi < 0 else "n.s."
        emit(f"  {sc:.1f}x  n={n:<2} median={m:7.0f} [{lo:6.0f},{hi:6.0f}]"
             f"  vs fixed {fx:>4.0f}: {dm:+7.0f} [{dlo:+7.0f},{dhi:+7.0f}] {verd}")
    v13 = list(series(v, 1.3).values())
    k = sum(1 for x in v13 if x > 3000)
    p, plo, phi = wilson(k, len(v13))
    emit(f"  catastrophic-seed rate @1.3x (>3000s): {k}/{len(v13)} = {p:.0%} "
         f"[{plo:.0%},{phi:.0%}]")

# seed-paired variant-vs-variant, Holm-corrected
emit("\n" + "=" * 80)
emit("PAIRED variant-vs-variant (median diff [bootstrap CI]; Wilcoxon p, "
     "Holm-corrected)")
emit("=" * 80)
pairs = [("pg_norm", "pg_raw"), ("pg_norm", "pg_elapsed"),
         ("pg_raw", "pg_elapsed")]
raw_p, rows = {}, {}
for a, b in pairs:
    for sc in SCALES:
        sa, sb = series(a, sc), series(b, sc)
        common = sorted(set(sa) & set(sb))
        if len(common) < 6:
            continue
        d = np.array([sa[s] - sb[s] for s in common])
        mdiff, dlo, dhi = boot_ci(d, med)
        p, nz = wilcoxon_p(d)
        key = f"{a} vs {b} @ {sc:.1f}x"
        raw_p[key] = p
        rows[key] = (len(common), mdiff, dlo, dhi)
adj = holm(raw_p)
for key in rows:
    n, mdiff, dlo, dhi = rows[key]
    p, padj, rej = adj[key]
    star = "*" if rej else " "
    emit(f"  {key:<28} n={n:<2} med_diff={mdiff:+7.0f} [{dlo:+7.0f},{dhi:+7.0f}]"
         f"  p={p:.3f} p_holm={padj:.3f} {star}")
emit("\n  '*' = significant after Holm at 0.05. med_diff<0 => first variant lower"
     " (better) delay.")
emit("=" * 80)

out = os.path.join(HERE, "experiments", "EXP-003_spillback-features", "data",
                   "ci_final.txt")
open(out, "w").write("\n".join(lines) + "\n")
print(f"\nwritten: {out}")
