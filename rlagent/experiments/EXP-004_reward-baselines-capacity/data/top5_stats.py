"""Mean + exact Wilcoxon p vs the baselines for the top-5 EXP-004 arms (1.3x).

Baselines are deterministic (no seed variance), so each arm is a one-sample
test: are the arm's per-seed delays significantly below/above the baseline
constant? Exact two-sided Wilcoxon signed-rank (all 2^n sign permutations --
exact, no normal approximation; n<=15 here so enumeration is trivial).

Honesty notes baked in:
- n=3 arms CANNOT reach p<0.25 (the exact test's floor at n=3) -> reported as
  "untestable at n=3", not as evidence of anything.
- EXP-004a uses its 9 complete seeds; seed 5 excluded (gridlocked eval, only
  6423/16026 peak trips completed -> its 2087 s is understated; excluding is
  the conservative choice and is disclosed).
"""
from itertools import product

import numpy as np

WEBSTER, TUNED = 911.6, 676.6   # recomputed-from-tripinfo values

ARMS = {
    "S2-rate (n=3)":        [890, 975, 1455],
    "S3-age (n=3)":         [905, 1046, 1407],
    "EXP-004a (n=9)":       [564, 623, 751, 841, 957, 982, 1004, 1735, 2575],
    "S4-rate+age (n=3)":    [945, 996, 1805],
    "S8-permaxes (n=15)":   [507, 690, 823, 930, 1071, 1146, 1229, 1421,
                             1522, 1583, 1840, 2407, 2609, 2631, 2778],
}


def exact_wilcoxon_two_sided(diffs):
    d = np.asarray([x for x in diffs if x != 0.0], float)
    n = len(d)
    ranks = np.argsort(np.argsort(np.abs(d))) + 1.0
    # tie-average ranks
    ad = np.abs(d)
    for v in np.unique(ad):
        m = ad == v
        if m.sum() > 1:
            ranks[m] = ranks[m].mean()
    w_pos = ranks[d > 0].sum()
    total = ranks.sum()
    # exact null: every sign pattern equally likely
    stats = []
    for signs in product((0, 1), repeat=n):
        stats.append(sum(r for r, s in zip(ranks, signs) if s))
    stats = np.array(stats)
    # two-sided: distance from the null centre total/2
    obs = abs(w_pos - total / 2)
    p = float(np.mean(np.abs(stats - total / 2) >= obs - 1e-9))
    return p, n


print(f"{'arm':22s} {'mean':>6} {'median':>7} | vs Webster 912 | vs tuned-act 677")
print("-" * 78)
for name, vals in ARMS.items():
    x = np.array(vals, float)
    cells = []
    for b in (WEBSTER, TUNED):
        p, n = exact_wilcoxon_two_sided(x - b)
        direction = "below" if np.median(x) < b else "above"
        floor = " (untestable: n=3 floor p=0.25)" if n == 3 else ""
        sig = "*" if p < 0.05 else " "
        cells.append(f"p={p:.3f}{sig} {direction}{floor}")
    print(f"{name:22s} {x.mean():6.0f} {np.median(x):7.0f} | {cells[0]:<32s} | {cells[1]}")
print("-" * 78)
print("* p<0.05 (exact two-sided). EXP-004a seed 5 excluded (incomplete eval,")
print("  delay understated); including it would only raise the mean.")
print("Deployed policy (S8 seed 4 via validation selection): 507 s -- a single")
print("deterministic deployment result, not a distribution; no p applies.")
