# EXP-003 — Spillback-aware state features (normalized occupancy + elapsed time)

**Date:** 2026-07-12
**Status:** ⚠️ Partial / promising but unproven. Normalization = clean win;
elapsed-time feature = big gains at some scales but **unstable at n=1 seed**.
**One-line:** Adding spillback-aware features narrows the high-saturation gap
EXP-002 exposed — normalization does so *reliably* (monotonic), and adding
phase-gated elapsed time does so *more* at 3 of 5 saturated scales — but the
elapsed-time variant is non-monotonic across load (a 1.3× anomaly), so with a
single training seed we cannot yet claim it as a robust improvement.

---

## 1. Motivation (from EXP-002)

EXP-002 showed the base method fails at saturation: it under-proportions green,
the heavy approach backs up, and delay explodes into insertion backlog
(spillback). The agent's state (raw per-lane counts) couldn't cleanly signal
"this approach is near its storage limit / about to spill." EXP-003 adds
features that make that visible, and fixes feature scaling so LSTDQ can use them.

## 1b. Naming key (avoid the "v3 ≡ EXP-003" confusion)

EXP-003 introduces **two** feature configs — an ablation and the treatment — so
"EXP-003" is not a single controller. The code `feature_mode` strings are
load-bearing and unchanged; use the display labels on slides:

| code `feature_mode` | display label | role | seeds on disk |
|---|---|---|---|
| `phase_gated` | **PG-raw** | EXP-002 baseline for this experiment | 1 |
| `phase_gated_norm` | **PG-norm** | EXP-003 **ablation** (normalization only, *no new feature*) | 1 |
| `phase_gated_v3` | **PG-elapsed** ("v3") | EXP-003 **treatment** (norm + phase-gated elapsed) | 5 (0–4) |

"v3" = **version 3** of the phase-gated layout (v1 = PG-raw counts, v2 = PG-norm,
v3 = + elapsed); only v3 carries the number in code. PG-norm lives under EXP-003
because it is EXP-003's ablation *control*, even though it adds no new feature —
that is deliberate, not a misfiling. **Only PG-elapsed is multi-seeded (§4b);
PG-raw and PG-norm are still n=1**, which is why only PG-elapsed has a CI (§4d).

## 2. What changed (state features only; everything else fixed)

Same action space, reward, LSTDQ, γ, ridge, ε, training regime as EXP-002.
Two new `feature_mode`s in `sumo_env.py`:

- **`phase_gated_norm`** (ablation): EXP-002's phase-gated features, but counts
  normalized to **occupancy = count / lane-storage ∈ [0,1]** (storage =
  lane_length / 7.5 m, a *fixed* denominator so features stay stationary as the
  policy shifts). Occupancy per lane *is* the queue-to-storage / spillback-risk
  ratio — delivered via normalization, not a redundant feature. 132-dim.
- **`phase_gated_v3`** (EXP-003): `phase_gated_norm` **+ phase-gated normalized
  elapsed time** (`phase_elapsed / MAX_GREEN`), a commitment / max-green signal
  the paper's state omitted. 136-dim (272 params).

Rationale for scaling: LSTDQ solves `w=(A+λI)⁻¹b`; mismatched feature scales
ill-condition `A` and make the single ridge `λ` regularize features unequally,
so small-scale features (a 0–1 ratio next to 0–50 counts) get crushed.
Normalizing everything to ~[0,1] fixes this (see the scaling discussion behind
this experiment).

## 3. Results — peak-window total delay (day 0508, incl. insertion backlog)

Lower is better. `data/peak_total_delay_comparison.txt`.

| scale | v/c | EXP-002 | norm-only | v3 | FIXED |
|---|---|---|---|---|---|
| 0.5× | 0.62 | 26 s | **18 s** | 21 s | 43 s |
| 0.8× | 0.82 | 596 s | 435 s | **166 s** | 63 s |
| 1.0× | 0.92 | 1,291 s | 1,119 s | **786 s** | 230 s |
| 1.3× | 1.20 | 3,709 s | **2,747 s** | 8,910 s ⚠ | 912 s |
| 1.5× | 1.38 | 6,226 s | **5,040 s** | 7,729 s | 2,087 s |
| 1.8× | 1.66 | 10,388 s | 9,355 s | **7,149 s** | 4,878 s |

### 3.1 Normalization alone: clean, reliable improvement
`norm-only` beats EXP-002 **monotonically at every scale** (~15–30% lower peak
delay). Fixing feature scaling reliably helps — it lets the occupancy /
spillback signal actually influence the linear fit. This is the trustworthy
part of EXP-003 and directly confirms the feature-scaling concern.

### 3.2 Elapsed-time (v3): big gains at some scales, but UNSTABLE
v3 improves substantially at 0.8× (596→166 s), 1.0× (1291→786 s), 1.8×
(10388→7149 s) — e.g. the vs-fixed penalty at 0.8× fell from +247% (EXP-002) to
+163%, and at 1.8× from +98% to +47%. **But v3 is non-monotonic:** at 1.3× it
is 8,910 s — *worse than EXP-002 and worse than its own 1.5× and 1.8×.* Delay
must rise with load; a 1.3× spike exceeding 1.8× is not physical for a stable
policy — it's the signature of a noisy policy, not a clean trend.

### 3.3 Nothing beats fixed-time in saturation yet
All variants remain worse than pretimed fixed-time from ~v/c 0.8 up (positive
penalties). Normalization narrows the gap reliably; v3 narrows it further where
it's stable. (Reminder: "fixed-time" here = *pretimed Webster*, the weaker of
the two standard baselines; the real signal is actuated — see experiments
README backlog.)

## 4. Critical caveat — single seed (the paper used n = 8)

We trained **one seed per config**. Sahachaiseree trained **8 independent
agents** and reported means/CIs *precisely because single RL runs are noisy*.
So both v3's gains and its 1.3× spike could be partly seed variance — we cannot
conclude robustly at n=1. The 1.3× anomaly is the clearest evidence that a
single seed is insufficient here.

## 4b. EXP-003b — multi-seed (resolves the §4 caveat)

Trained v3 on 5 seeds (0–4) and evaluated each; also probed behavior. This
overturns the pessimistic single-seed read and quantifies the real story.

**Behavior probe @ 1.3× (does the policy park?):** 2 of 5 seeds collapse into
"parking" a low-demand phase at high load (seed 0 → NS_LEFT 8,233 s; seed 2 →
NS_THRU 8,341 s; both jam EB to its max queue of 60). The other 3 seeds cycle
healthily and serve the heavy EB through (EB max ~46–57). The parked phase
*varies*, so it's a general collapse susceptibility, not a specific-phase bug.

**Peak total delay per seed (s):**

| scale | seed0 | seed1 | seed2 | seed3 | seed4 | **median** | mean | norm | fixed |
|---|---|---|---|---|---|---|---|---|---|
| 1.0× | 786 | 489 | 185 | 575 | 430 | **489** | 493 | 1119 | 230 |
| 1.3× | 8910 | 1403 | 4420 | 1855 | 1673 | **1855** | 3652 | 2747 | 912 |
| 1.8× | 7149 | 5899 | 5842 | 6899 | 3042 | **5899** | 5766 | 9355 | 4878 |

**Findings:**
- **v3 is the best RL variant so far, on the median** — beats norm *and*
  EXP-002 at every scale (1.3×: 1855 vs 2747 vs 3709). The earlier "v3 worse at
  1.3×" was purely an artifact of headlining seed 0 (the worst draw).
- **High variance is the real weakness** — ~40% of seeds hit the parking
  collapse, inflating the mean well above the median. The spillback features
  help a lot *when they work*, but the representation isn't robust.
- **Still short of fixed-time at saturation** (1.3×: median 1855 vs 912) — but
  the gap is much smaller than EXP-002, and the remaining gap is likely the
  reward (EXP-004), not the state.
- **No code bug** — features/normalization/eval verified correct; the failure
  is a learned-policy collapse.

**Root cause (mechanism):** phase-gating zeros the *other* phases' lane blocks,
so a parked agent cannot see the queue it is starving (e.g. EB) when deciding
whether to advance — partial observability for the advance decision. The
`−queue` reward is hugely negative from that invisible queue, but the only
feature varying while parked is the elapsed-time signal, so LSTDQ can
misattribute the aliased reward and (in ~40% of seeds) learn a self-reinforcing
"extend" in the parked phase. EXP-002/norm lack the varying signal, so they
don't develop it — but they're not structurally immune either.

## 4c. Numerical diagnosis — the LSTDQ solve is ill-conditioned (explains the variance)

Prompted by "are we seeing matrix-inversion instability / counter-intuitive
weight signs?" Both checked directly (`data/diag_conditioning.py`,
`data/diag_weight_signs.py`); both point to the same root cause behind the
parking variance.

**(a) The solve is ill-conditioned.** Building `A = Σ x(x−γx′)ᵀ` from a real
batch:

| feature mode | cond(A) | cond(A+1e-4·I) | ridge-sensitivity* | sym-part min eig |
|---|---|---|---|---|
| phase_gated | ∞ (singular) | 1.9×10¹⁰ | 0.27 | −2.8×10³ |
| phase_gated_norm | ∞ (singular) | 8.9×10⁸ | 1.48 | −1.3×10² |
| phase_gated_v3 | ~10⁶⁹ | 3.7×10⁸ | 1.50 | −1.2×10² |

\*fractional change in `w` when ridge goes 1e-4→1e-2.

- `A` is **rank-deficient** (singular) — the ridge term is load-bearing, not
  optional. Even regularized, `cond ≈ 10⁸–10¹⁰`.
- The solution is **ridge-sensitive** (~150% change for norm/v3) → *the data
  doesn't determine the weights; the regularizer does.* Poorly-determined
  weights ⇒ large seed-to-seed variance ⇒ a direct contributor to the parking
  lottery (§4b).
- `A` is **not positive-definite** (negative symmetric-part eigenvalue) — the
  known off-policy LSTD non-contraction issue.
- **Normalization helps ~20×** (1.9e10→8.9e8), consistent with the scaling
  argument, but doesn't fix it.
- **Root cause is structural, not a bug:** phase-gated blocks are sparse (zero
  unless their phase is active), the phase one-hot is collinear with them, and
  elapsed only varies while dwelling — so many feature directions are
  under-determined and `A` collapses to rank-deficient.

**(b) Weight signs: occupancy intuitive, elapsed counter-intuitive.**
EXTEND-preference = `w_EXTEND − w_ADVANCE` (>0 ⇒ "keep extending"):
- **Occupancy weights are sensible** — high queue on the served phase → extend,
  strongest for EW_THRU (≈1200–1600 across seeds). No wrong-sign problem.
- **Elapsed-time weight is counter-intuitive** — positive extend-preference in
  most seeds (*"the longer I've sat, the more I want to stay"*), backwards from
  the soft max-green the feature was meant to provide. Largest in exactly the
  parked phase of the parked seeds (seed 0 → NS_LEFT; seed 2 → NS_THRU).

**The two connect:** ill-conditioning leaves the (sparse) elapsed weight
under-determined, so the solve fills it with a ridge-dependent, sign-unstable
value; most seeds land on a *positive* (self-parking) sign, and combined with
the partial-observability (a parked agent can't see the queue it starves,
§4b) ~40% tip into the collapse. Ill-conditioning → under-determined elapsed →
wrong/unstable sign → parking variance.

**Fix candidates (for EXP-003c / 003d):**
1. Tune/raise ridge (currently 1e-4, in the ridge-sensitive regime) or
   cross-validate it — cheapest stabilizer.
2. Cut collinearity — drop the redundant phase one-hot; use one global elapsed
   feature instead of 4 phase-gated ones.
3. Stabler solver — truncated-SVD / pseudo-inverse (`lstsq`) instead of `solve`
   on a singular `A`.
4. Enforce max-green in the env instead of *learning* it via elapsed — removes
   the wrongly-signed feature entirely and hard-bounds the parking. Given the
   elapsed weight is the destabilizer, likely the cleanest fix.

## 4d. Confidence intervals vs the fixed-time baseline (bootstrap) — n=5, SUPERSEDED by §4e

> **Superseded:** this section reports the *interim* n=5 read (v3 only, before
> PG-raw/PG-norm were multi-seeded). It is kept for the experimentation trail.
> The final, equal-n=20 result — which **overturns several conclusions here** —
> is in §4e. Read §4e for the numbers to cite.

Prompted by the "point estimates aren't enough — need CIs/p-values" review bar.
Computed with `data/stats_ci.py` (pure numpy, B=10000 percentile bootstrap).
**The resampling unit is the independent training run, not per-trip delays** —
resampling trips would measure only within-run noise (thousands of samples →
deceptively tight intervals) and ignore the training-seed variance that actually
dominates here (§4b). A CI on the **paired difference** `v3 − fixed` is used, so
it doubles as the significance test (interval excludes 0 ⇒ distinguishable).

**Only PG-elapsed (v3) has multi-seed data (n=5).** PG-raw and PG-norm are n=1,
so they get **no CI** until the multi-seed retrain — a CI'd v3 must **not** be
ranked against their single-seed point values (that is the underpowered version
of the exact mistake the CI is meant to prevent).

Peak total delay, day 0508:

| scale | v3 median [95% CI] | v3 − fixed (median) [95% CI] | verdict |
|---|---|---|---|
| 1.0× | 489 s [185, 786] | +259 s [−45, +556] | **not distinguishable** from fixed |
| 1.3× | 1855 s [1403, 8910] | +943 s [+491, +7998] | **worse** than fixed (CI excludes 0) |
| 1.8× | 5899 s [3042, 7149] | +1021 s [−1836, +2271] | **not distinguishable** from fixed |

Fixed baseline point values: 1.0× = 230, 1.3× = 912, 1.8× = 4878 s.
**Parking-collapse rate:** 2/5 seeds → 40%, Wilson 95% CI **[12%, 77%]**.

**Reading:** the only statistically firm claim at n=5 is **"v3 is worse than
fixed at 1.3×."** At 1.0× and 1.8× the difference is not distinguishable — we
can claim neither better nor worse. The intervals are huge (1.3× spans
1403–8910 s; the parking rate 12–77%) precisely because n=5 and the delay is
bimodal (parking). That width is not a flaw in the method — it is direct
evidence that **n=5 is too few for fine claims**; n≥10 (ideally ~20) is needed
to narrow them. (B only sharpens the percentile estimate; it does *not* narrow
a CI — only more seeds do.)

## 4e. FINAL multi-seed CIs — n=20, all three variants (EXP-003c-stat)

All three variants retrained to **n=20 independent seeds** (seeds 0–19; the 8
existing seeds reused, 53 new runs on `libsumo`, 20-wide parallel). Every seed —
old and new — is scored through the single canonical peak-delay pipeline
(`data/peak_delay.py`, verified to reproduce the recorded numbers to <1%).
Analysis in `data/finalize_ci.py`; full output in `data/ci_final.txt`.

Two test families:
- **vs fixed-time**: bootstrap 95% CI (B=10000) on the median paired difference
  `variant − fixed`. Fixed-time is deterministic (zero seed variance), so this
  has power even against the bimodal variant distributions.
- **variant vs variant**: these are **seed-paired** (PG-raw sN, PG-norm sN,
  PG-elapsed sN share the same training RNG seed → matched demand sampling), so
  a paired **Wilcoxon signed-rank** test, **Holm-corrected** across the 9-test
  family (the multiple-comparison guard).

**Median paired difference vs fixed-time (s), day 0508, n=20** (negative = RL
better; "n.s." = 95% CI straddles 0):

| variant | 0.5× | 0.8× | 1.0× | 1.3× | 1.8× | collapse@1.3× |
|---|---|---|---|---|---|---|
| **PG-raw** | −26 **BETTER** | −8 n.s. | +143 n.s. | +261 n.s. | +999 n.s. | 21% [9,43] |
| **PG-norm** | −27 **BETTER** | −13 n.s. | +113 n.s. | +394 n.s. | +7 n.s. | 21% [9,43] |
| **PG-elapsed** | −26 **BETTER** | +2 n.s. | +229 **WORSE** | +1259 **WORSE** | +1745 **WORSE** | 35% [18,57] |

(v/c: 0.5×≈0.62, 0.8×≈0.82, 1.0×≈0.92, 1.3×≈1.20, 1.8×≈1.66. Fixed-time point
values: 43 / 63 / 230 / 912 / 4878 s. RL medians e.g. PG-norm: 16/50/343/1306/
4885 s. vs-fixed CIs are *uncorrected* 95% — see robustness note below.)

**The arc across load:** at **0.5× all three variants significantly beat
fixed-time** (RL ~16–18 s vs 43 s — the low-load regime is where adaptive timing
has slack to exploit, matching the paper). **0.8× is the crossover** (all n.s.).
From **1.0× up**, PG-raw/PG-norm stay indistinguishable from fixed while
PG-elapsed turns significantly worse.

**Variant-vs-variant (seed-paired Wilcoxon, Holm-corrected): every pair, every
scale is n.s. (all p_holm = 1.000).** Median differences trend PG-norm ≈ PG-raw
< PG-elapsed (e.g. norm−elapsed @1.8× = −1611 s), but none survive correction.

**What the n=20 data establishes (and what it overturns):**

1. **The "base method is much worse at saturation" headline was a single-seed
   artifact.** PG-raw and PG-norm **significantly beat fixed-time at 0.5×** and
   are **statistically indistinguishable from it at 0.8–1.8×** (all n.s.) — never
   significantly worse at any scale. The old EXP-002 §3.4 "+247% to +440% worse"
   came from *one unlucky seed each* (PG-raw 3709, PG-norm 2747 at 1.3×); the
   medians are ~1173 / ~1306 vs fixed's 912, well within noise. **This is the
   headline correction.**
2. **The elapsed-time feature backfired.** PG-elapsed is **significantly worse
   than fixed** and carries the **highest collapse rate (35% vs 21%)**. This
   *reverses* the interim §4b claim that "v3 is the best variant on the median"
   — that was an unfair n=5-vs-n=1 comparison. With equal n, adding elapsed
   time **hurts** (consistent with the §4c ill-conditioning / wrong-sign
   diagnosis: the feature the solve can't determine is actively destabilizing).
3. **The three variants cannot be statistically separated from each other** at
   n=20 (all pairwise n.s. after Holm). Only comparisons against the
   zero-variance fixed baseline have the power to conclude anything; the seed
   variance is too large to rank the variants head-to-head. Honest limit.
4. **Instability is not unique to the elapsed feature** — even PG-raw/PG-norm
   have a **21%** catastrophic-seed rate at 1.3× (a ~1/5 chance a training run
   blows up near saturation). The elapsed feature worsens it to 35%, it doesn't
   create it. The robustness problem is the base method's, not just v3's.

**Robustness caveat (stated, not hidden):** the vs-fixed CIs above are
uncorrected 95%. The PG-elapsed "WORSE" verdicts at **1.3× and 1.8× are robust**
(paired-diff lower bounds +398 and +743, far from 0 — they survive a
multiple-comparison correction); the **1.0× verdict is marginal** (lower bound
+69) and should not be leaned on. PG-raw/PG-norm being n.s. only strengthens
under correction.

**Defensible one-line for the slide:** *"At n=20 with proper CIs, the base
linear-FA controller significantly beats Webster fixed-time at low load (0.5×)
and is statistically indistinguishable from it through saturation (0.8–1.8×) —
never significantly worse; the added elapsed-time feature makes it significantly
worse from 1.0× up and less stable; and no variant can be separated from the
others — the remaining bottleneck is training-seed variance (a ~21–35% collapse
rate), not mean performance."*

## 5. Conclusion & next step

- **Normalization: adopt it** — clean, monotonic improvement; also the correct
  thing numerically. Fold into the standard feature set.
- **Elapsed-time / v3: promising but unproven** — big gains at 3/5 saturated
  scales, but unstable at n=1.
- **EXP-003b: done (see §4b).** Multi-seed showed v3 is the best RL variant on
  the median but suffers a ~40% parking-collapse rate → high variance.
- **Next (EXP-003c): robustness fix.** Add a *non-gated* global per-approach
  queue summary (always visible, alongside the phase-gated block) so the agent
  can see the approaches it is starving when deciding to advance. Targets the
  partial-observability mechanism behind the parking collapse; goal is to cut
  the ~40% failure rate, not just pick a lucky seed.
- Still-open: **no variant beats fixed-time in saturation** — likely needs the
  reward redesign (EXP-004: penalize insertion backlog), since the state now
  *shows* spillback but the `−queue` reward may not make the agent *act* on it.
