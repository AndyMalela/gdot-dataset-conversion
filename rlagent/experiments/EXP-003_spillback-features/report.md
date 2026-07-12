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
