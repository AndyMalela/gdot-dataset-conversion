# EXP-004 — Reward alignment, realistic baselines, and the capacity envelope

**Date:** 2026-07-14 → 07-15
**Status:** ✅ Positive. **The selected (deployed) policy beats every baseline —
including the strongest real-world actuated controller — at 4 of 5 demand
scales, including the 1.3× target.**
**One-line:** three theory-directed changes, isolated by a strategy race —
(1) a reward that counts the *hidden* insertion-backlog queue, (2) always-
visible cross-approach features, (3) a *demand-proportioned* max-green
envelope — plus the paper's own validation-selection protocol, take the linear
LSTDQ controller from "Webster parity at best" to **507 s vs tuned-actuated's
677 s at 1.3×** on held-out day 0508.

Goal (user/professor bar): "marginal vs Webster is not acceptable — decisively
better at 1.3×, against a real-world-grade baseline."

---

## 1. Stronger baselines first (the bar had to move up honestly)

Webster pretimed is the weakest legitimate baseline; the real SIG#7065 cabinet
is actuated. Implemented the paper's own Appendix A **passage-time (gap-out)
controller** on the twin (detectors 30 m upstream, 4 m long, gap-out 3 s, min
green 8 s), in two versions (raw evidence: `data/actuated_run.log`,
`data/actuated_tuned_run.log`):

| peak 15–18h total delay (s), 0508 | 0.5× | 0.8× | 1.0× | 1.3× | 1.8× |
|---|---|---|---|---|---|
| Webster pretimed | 43 | 63 | 230 | 912 | 4878 |
| Actuated, uniform 30 s max | 42 | 339 | 590 | 1634 | 4063 |
| **Actuated, tuned maxes** (Webster×1.25 = [14.8, 92.3, 30, 70.3]) | 38 | 373 | 652 | **677** | **1979** |
| Max-pressure, cyclic (same maxes; added later) | 40 | 614 | 1764 | 5212 | 10168 |

- **Tuned-actuated is the strongest baseline at saturation** (677 at 1.3×,
  2.5× better than Webster at 1.8×): at high v/c it degenerates into a
  *well-proportioned* long-cycle plan (minimal lost time, splits ∝ flow
  ratios) while still gap-adapting off-peak. This became the number to beat.
- Neither actuated variant beats Webster at 0.8–1.0× (gap-out thrashes there)
  — no baseline dominates everywhere.
- **Max-pressure (added post-hoc, `maxpressure_baseline.py`): fine at 0.5×,
  collapses at saturation (5212 at 1.3×).** Not a bug — a diagnosable
  violation of its assumptions: MP's throughput-optimality guarantee requires
  *fully observable, unbounded* upstream queues, but the twin's short
  approaches cap the visible queue (EB shows ~60 veh while thousands sit in
  insertion backlog). At saturation every approach's pressure signal
  saturates flat, the argmax loses discrimination, and cyclic MP degrades
  toward early-terminating round-robin (insertion delay 2739 s vs
  tuned-actuated's 582 s at 1.3×). **This is the same
  observability/backlog-blindness limit that made the paper's queue reward
  gameable (§2)** — a unifying thread: any controller (learned or
  theory-optimal) that reads only stop-line-visible queues fails here; the
  RL wins precisely because its reward was re-aligned to count the backlog.
  Same min-green (8 s) and max-green envelope as tuned-actuated → pure
  decision-rule comparison. Raw: `data/maxpressure_run.log`.
- Misstep (recorded): the first "tuned" run silently used max-greens
  [8,8,8,8] — iterating the Webster `greens` **dict** yields its *keys*.
  Caught because the results were catastrophically bad; fixed, reran.

## 2. EXP-004a — reward alignment (control arm, n=10)

`reward_mode="system"`: R = −(lane queues **+ insertion backlog**)
(`sumo_env.py`). The paper's Eq. 13 queue-only reward is *gameable* under
oversaturation — once an entry lane fills, overflow piles up as SUMO insertion
backlog, invisible to the reward, so the agent is *rewarded* for clogging the
entrances (the EXP-002 §3.4 pathology, previously fixed in the metric but not
the reward). By Little's law, integrating vehicles-waiting-anywhere over time
∝ **total delay** — the evaluation metric — so reward and metric now agree.

Result (PG-norm features, otherwise unchanged, 10 seeds, 1.3×):
9 healthy seeds = {564, 623, 751, 841, 957, 982, 1004, 1735, 2575},
**mean 1115, median 957** — vs the old PG-norm mean ≈ 2290: **the reward fix
alone halved mean delay** and reached Webster parity (Wilcoxon vs 912:
p = 0.86, indistinguishable; vs 677: p = 0.03, still above).
**Anomaly (disclosed):** seed 5 collapsed — its tripinfo holds only 6,423 of
16,026 peak trips (gridlock; its nominal 2087 s is *understated* because
uncompleted trips can't be counted). 004a = 9/10 healthy + 1 collapse.

## 3. Strategy race (3 seeds each — screening, no CIs by design)

7 strategies on the common chassis (system reward + hard max-green 30 s +
training scale range widened to [0.5, **1.6**] so 1.3× is interior):

| strategy | features | 1.3× seeds | mean | collapses |
|---|---|---|---|---|
| **rate** | glob + per-approach occupancy Δ/decision | 890, 975, 1455 | **1107** | 0 |
| **age** | glob + time-since-served per phase | 905, 1046, 1407 | **1119** | 0 |
| rate+age | both | 946, 996, 1805 | 1249 | 0 |
| spill+multi | glob+spill ind., multi-objective reward | 882, 1800, 3278 | 1987 | 1 |
| spill | glob + entry-edge spillover indicator | 885, 1266, 8636 | 3596 | 1 |
| glob alone | visibility block only | 1619, 3851, 5446 | 3639 | 2 |
| ridge 1e-2 | glob, higher ridge | 1003, 1708, 9517 | 4076 | 1 |

- **rate/age = the stabilizers** at n=3: 0 collapses in 6 seeds; `rate` beat
  Webster at 1.8× on *every* seed (2847–3927 vs 4878) — the wider training
  range works.
- Raising ridge alone does **not** stabilize (kills the "just regularize
  harder" hypothesis from EXP-003 §4c).
- The multi-objective spillover reward did not beat the plain system reward.
- **Every strategy floored at ~880–900 s** at 1.3× — Webster parity, not 677.
- **n=3 caveat (resolved in §3b):** the exact Wilcoxon test cannot reach
  p < 0.25 at n=3 — these rankings were a screen, not a conclusion.

## 3b. rate / age / rate+age extended to n=10 (the powered re-test)

n=3 is statistically untestable, so rate/age/rate+age were extended to n=10
(pooling the original s0–2 with new s3–9, same config). This is where a real
statistical test — not a screen — was finally possible.

**Misstep (disclosed):** the extension batch was launched detached; a session
boundary killed its `xargs` parent mid-run. 8/21 seeds had already finished
cleanly; 2 (`age`/s8, `rateage`/s8) were caught as genuinely empty (0-byte log,
zero episodes — verified before touching anything) and restarted; the rest
resumed from checkpoint. No seed was silently lost or duplicated.

**Result — mean ± exact Wilcoxon p vs both baselines (`data/top5_stats_n10.py`
→ `data/top5_stats_n10.txt`):**

| arm | n | mean | median | min | max | vs Webster 912 | vs tuned-act 677 |
|---|---|---|---|---|---|---|---|
| S2-rate | 9\* | 1084 | 1204 | 675 | 1455 | p=0.074 (above) | p=0.008\*\* (above) |
| S3-age | 10 | 1560 | 1414 | 779 | 3153 | **p=0.027\*\* (above)** | p=0.002\*\* (above) |
| S4-rate+age | 10 | 1292 | 1163 | 521 | 2544 | p=0.106 (above) | p=0.010\*\* (above) |

\* `rate` seed 3 **excluded**: gridlocked (only 58,213/67,124 total demand
completed at 1.3×, max single-vehicle wait 13.3 h, and its delay is
*non-monotone in scale* — 11555→10085→9289 as scale rises — the exact
survivorship-bias signature already seen in EXP-004a seed 5; identical
disclosure/exclusion treatment, not cherry-picking). \*\* p<0.05.

**This overturns the n=3 screen's apparent ranking:**
- **`age`'s n=3 mean (1119) looked as good as `rate`'s — at n=10 it is
  significantly *worse* than Webster (p=0.027) and nearly 50% higher (1560
  vs 1084).** Three of its seven new seeds (2608, 3153, 1893) are exactly the
  kind of high seeds the n=3 draw happened to miss.
- **`rate` remains the best-behaved arm** (mean 1084, only 1/10 seeds
  collapsed — better than `age`'s implicit rate) but is **still not
  significantly different from Webster** (p=0.074) — a trend, not a result.
- **None of the three arms' averages beat either baseline.** All three are
  significantly *worse* than tuned-actuated; only `rate` and `rate+age`
  fail to separate from Webster (parity, like EXP-004a), while `age` is
  significantly worse than Webster too.
- **Practical lesson:** n=3 screening is good for *eliminating* clearly bad
  configs (glob-alone, spill, ridge, spill+multi all stayed bad) but **cannot
  rank the surviving good-looking ones** — `age` only revealed its true
  (worse) character at n=10. Screening picks a shortlist; it does not crown
  a winner.

## 3c. Full load range (0.5× / 0.8× / 1.0× / 1.3×) for the top-5 arms

The n=10 re-test (§3b) only covered 1.3×. Extended every top-5 arm (EXP-004a,
rate, age, rate+age, S8) with 0.5×/0.8× evals on the already-trained weights
(no retraining — `eval_extra_scales.py`), giving the same mean+exact-Wilcoxon
treatment across the whole target range
(`data/top5_stats_allscales.py` → `data/top5_stats_allscales.txt`).

**Exclusion methodology, tightened by a real finding:** `rate` seed 3 (already
disclosed as gridlocked at 1.3× — §3b) turned out to report **5605 s at 0.5×**
and **11222 s at 0.8×** despite *completing 100% of trips* at both scales — no
insertion backlog forms at trivial demand, so the completion-count filter that
caught it at 1.3× doesn't fire at low load, even though the underlying policy
is the same broken one. **Fix:** a seed's exclusion verdict is now decided
once, from the established 1.3× completion criterion, and applied to *all*
scales for that seed — re-deriving the check independently per scale is
exactly what let this contamination through the first time.

**Baselines, all 4 scales:**

| | 0.5× | 0.8× | 1.0× | 1.3× |
|---|---|---|---|---|
| Webster | 43.1 | 63.1 | 229.9 | 911.6 |
| tuned-actuated | 37.9 | 372.9 | 651.8 | 676.6 |

**Mean peak delay (s) per arm, per scale, vs both baselines (exact Wilcoxon;**
**\* = p<0.05):**

| arm | 0.5× | 0.8× | 1.0× | 1.3× |
|---|---|---|---|---|
| EXP-004a (n=9) | 23, **below\* / below\*** | 59, below / below\* | 209, below / below\* | 1115, above / above\* |
| S2-rate (n=9) | 21, **below\* / below\*** | 55, below / below\* | 259, below / below\* | 1084, above / above\* |
| S3-age (n=10) | 86, below / below | 249, above / below | 527, above / below | 1560, **above\* / above\*** |
| S4-rate+age (n=10) | 28, below / below | 109, below / below\* | 353, below / below\* | 1292, above / above\* |
| S8-permaxes (n=15) | 83, below / below | 236, above / below | 467, above / below | 1546, **above\* / above\*** |

(cell = mean; "below/above" = below or above that baseline's mean; \* = exact
Wilcoxon p<0.05 for that comparison — see `data/top5_stats_allscales.txt` for
every p-value.)

**Reading, consistent with §3b and not overturned by it:**
- **0.5×: EXP-004a and `rate` are significantly *better* than both baselines**
  (p<0.01) — the low-load win the base method has shown since EXP-002 holds
  for these arms too. `age`/`rate+age`/S8 trend better but aren't significant
  at this n.
- **0.8×–1.0×: mixed, mostly non-significant** — arms trend below Webster
  (adaptive timing has some slack to exploit) but at/above tuned-actuated,
  with few comparisons reaching significance either way.
- **1.3×: the target scale, and the one place the ordering sharpens** — `age`
  and `S8` are significantly *worse* than both baselines; `EXP-004a`/`rate`/
  `rate+age` are worse than tuned-actuated but not distinguishable from
  Webster (parity).
- **No arm's mean beats tuned-actuated at any scale** — confirms §3b/§4's
  conclusion holds across the full range, not just at 1.3×: the "beats every
  baseline" result is specific to the validation-selected deployed policy
  (§5), never to an arm average.

## 4. S8 — the capacity envelope (the decisive change)

Diagnosis of the floor: our *uniform 30 s* hard max-green forbids the critical
EW-through phase more than ~35% of the cycle — but tuned-actuated's entire
advantage is its **92 s** EW-thru max (>50% cycle share). We had
capacity-capped the agent below the baseline we were chasing.

**S8 = rate features + per-phase max-greens [15, 92, 30, 70]** (the same
envelope as tuned-actuated — the agent gets *equal*, not more, capacity).
15 seeds, held-out 1.3×:

```
507, 690, 823, 930, 1071, 1146, 1229, 1421, 1522, 1583,
1840, 2407, 2609, 2631, 2778        mean 1546 · median 1421
```

- **The envelope raised the ceiling dramatically** — best seeds 507/690/823
  smash the old 880 floor; 4 seeds beat Webster; **seed 4 (507 s) beats
  tuned-actuated (677)**.
- **Unselected, S8 is honestly *worse* on the mean** (1546; Wilcoxon vs 912
  p = 0.008 *above*) — the bigger envelope also widens the failure tail. The
  capability exists in the hypothesis class; finding it per-seed is the
  residual (LSTDQ ill-conditioning, cf. EXP-003 §4c).

## 5. Validation selection (the paper's own protocol) → deployed policy

Sahachaiseree Table 6 reports the **best-performing agent of 16** — selection
across seeds is the base method's own deployment protocol. Ours, kept honest
(`val_select.py`, raw: `data/valsel_final.log`):
validate every seed on **training day 0507** @1.3× → argmin → report that one
policy's **held-out 0508** numbers. 0508 never touches selection.

- **Spearman ρ(val, heldout) = 0.87 (n=15)** — validation rank strongly
  predicts held-out rank; the top-3 by validation are the top-3 held-out.
- **Selected: seed 4** (val 191 s).

**Deployed-policy result (S8/seed 4, held-out 0508) vs the full baseline
ladder:**

| peak total delay (s) | 0.5× | 0.8× | 1.0× | 1.3× | 1.8×* |
|---|---|---|---|---|---|
| **RL (selected)** | **20** | **26** | **103** | **507** | 2942 |
| tuned-actuated | 38 | 373 | 652 | 677 | **1979** |
| Webster | 43 | 63 | 230 | 912 | 4878 |
| max-pressure (cyclic) | 40 | 614 | 1764 | 5212 | 10168 |
| vs best baseline | **−47%** | **−59%** | **−55%** | **−25%** | +49% |

\* 1.8× is extrapolation beyond the trained range (≤1.6) for RL.

**Beats every baseline at 4 of 5 loads, including the 1.3× target (507 vs
677, −25%); the only loss is 1.8× extrapolation vs tuned-actuated** (still
−40% vs Webster there).

## 6. Sanity review (all headline numbers re-verified)

1. Baselines recomputed from raw tripinfos: 911.6 / 1634.3 / 676.6 ✓.
2. Seed 4 completes **67,124 trips = 100% of demand** (identical to
   fixed-time) → no survivorship bias behind 507 s ✓.
3. Val day (0507) ≠ test day (0508), distinct files (md5) ✓; 0507 is a
   training day → selection is legal ✓.
4. **Fresh re-run of the selected policy from its weights file reproduces
   507.1 s exactly** (+ produced the 0.5×/0.8× row above);
   `data/repro_s4.log` ✓.
5. RL's envelope = tuned-actuated's envelope (no capacity advantage) ✓.
6. Anomaly caught & disclosed: 004a seed 5's incomplete tripinfo (§2).

## 7. Conclusions & open items

- **Decomposition (each step isolated by an arm/race):** reward alignment
  −50% mean → rate/age features kill the collapse at 30 s caps (n=3) → capacity
  envelope unlocks sub-677 policies → validation selection makes one of them
  the deployed controller. All three changes are traffic-theory-motivated,
  none are reward/metric hacks (reward now *equals* the honest metric).
- **No arm's AVERAGE beats either baseline, at any n tested (§2, §3b, §4).**
  EXP-004a and `rate` reach *parity* with Webster (p≈0.9, p≈0.1 — genuinely
  indistinguishable); `age`, `rate+age`, and unselected S8 are significantly
  *worse* than Webster; all five are significantly worse than tuned-actuated.
  **The entire "beats every baseline" result lives in validation selection
  (§5), not in any arm's mean** — stated plainly, not implied.
- **n=3 screening picks a shortlist, not a winner (§3b):** `age` looked as
  good as `rate` at n=3 (1119 vs 1107) and turned out significantly *worse*
  than Webster at n=10 (1560, p=0.027) — three of its seven new seeds were
  simply higher than the lucky first three. Use small-n races only to cut
  clearly-bad configs; re-test survivors before ranking them.
- **Open:** per-seed reliability (mean 1546 vs selected 507) — the residual
  is the LSTDQ solve's seed sensitivity (EXP-003 §4c). Candidates: refit
  schedule, experience curation, warm-starting from the selected policy.
  This is also the honest motivation for the DQN comparison (EXP-005+).
- **Infra note:** LSPI refit-after-every-episode is O(k²) in episodes — late
  episodes are refit-dominated (~40 of 54 min for one 20-episode run at
  141-dim). Refit-every-N would cut wall time ~3× for future sweeps.
- Per the current reporting decision: **means + Wilcoxon p, no CIs** for
  these arms; the selected-policy row is a deterministic deployment result.
