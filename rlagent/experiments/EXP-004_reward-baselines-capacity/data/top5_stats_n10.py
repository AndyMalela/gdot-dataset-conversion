"""Mean + exact Wilcoxon p vs baselines, rate/age/rate+age extended to n=10
(pooled s0-2 from the original race + s3-9 from the n=10 extension).
rate seed3 EXCLUDED: gridlocked (58213/67124 trips completed, max wait 13.3h,
delay non-monotone in scale 11555->10085->9289 = survivorship-bias signature)
-- disclosed, not silently dropped. n=9 for rate as a result.
"""
import numpy as np
from itertools import product

WEBSTER, TUNED = 911.6, 676.6

ARMS = {
    "S2-rate (n=9, s3 excl.)": [975, 890, 1455, 1228, 1212, 1422 if False else None],  # placeholder overwritten below
}

# explicit pooled values (1.3x), from race.log (s0-2) + race6.log (s3-9)
RATE = {0:1455, 1:975, 2:890, 3:None, 4:1212, 5:1228, 6:675, 7:862, 8:1252, 9:1204}
AGE  = {0:1407, 1:905, 2:1046, 3:1539, 4:2608, 5:1422, 6:779, 7:3153, 8:844, 9:1893}
RATEAGE = {0:1805, 1:945, 2:996, 3:521, 4:2544, 5:1330, 6:1739, 7:643, 8:1540, 9:854}
EXP004A_9 = [564, 623, 751, 841, 957, 982, 1004, 1735, 2575]   # seed5 excluded (incomplete eval)
S8_15 = [507, 690, 823, 930, 1071, 1146, 1229, 1421, 1522, 1583,
         1840, 2407, 2609, 2631, 2778]

ARMS = {
    "S2-rate (n=9)":      [v for v in RATE.values() if v is not None],
    "S3-age (n=10)":      list(AGE.values()),
    "S4-rate+age (n=10)": list(RATEAGE.values()),
    "EXP-004a (n=9)":     EXP004A_9,
    "S8-permaxes (n=15)": S8_15,
}


def exact_wilcoxon_two_sided(diffs):
    d = np.asarray([x for x in diffs if x != 0.0], float)
    n = len(d)
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
        mu, sd = n*(n+1)/4, (n*(n+1)*(2*n+1)/24)**0.5
        from math import erf, sqrt
        z = (w_pos - mu) / sd
        p = 2*(1 - 0.5*(1+erf(abs(z)/sqrt(2))))
    return p, n


print(f"{'arm':22s} {'mean':>6} {'median':>7} {'min':>6} {'max':>6} | vs Webster 912 | vs tuned-act 677")
print("-" * 95)
for name, vals in ARMS.items():
    x = np.array(vals, float)
    cells = []
    for b in (WEBSTER, TUNED):
        p, n = exact_wilcoxon_two_sided(x - b)
        direction = "below" if np.median(x) < b else "above"
        sig = "*" if p < 0.05 else " "
        cells.append(f"p={p:.4f}{sig} {direction}")
    print(f"{name:22s} {x.mean():6.0f} {np.median(x):7.0f} {x.min():6.0f} {x.max():6.0f} | {cells[0]:<28s} | {cells[1]}")
print("-" * 95)
print("* p<0.05 (exact two-sided Wilcoxon, enumeration for n<=15).")
print("rate seed 3 EXCLUDED: gridlocked (only 58213/67124 total trips completed,")
print("  max wait 13.3h, non-monotone-in-scale delay -- survivorship-bias signature,")
print("  identical treatment to EXP-004a seed 5). n=9 for rate as a result.")
print("EXP-004a seed 5 EXCLUDED: incomplete eval (6423/16026 peak trips). n=9.")
