# Experiment log — RL signal control on SIG#7065

Running lab notebook for the RL-agent work (`rlagent/`). Each experiment is
a dated, self-contained record: motivation, exact architecture/action-space/
training config, results (including failures), diagnosis, and what it led to
next. **Failures and missteps are recorded deliberately** — they are the
"experimentation" narrative for the graduation progress report, not noise to
be cleaned away.

This folder is expected to grow. Add a new `EXP-NNN_<slug>/` per experiment;
keep raw result snapshots under each experiment's `data/` so the numbers
quoted in a `report.md` can always be traced back.

## Conventions

- **Fidelity policy** (project-wide, see `/CLAUDE.md`): never rescale/smooth/
  invent numbers to match an expectation; report what the system actually did,
  including when it fails. Every metric here is copied from a real run.
- **Metrics** (from SUMO `tripinfo`, via `metrics.py`):
  - *throughput* = number of trips **completed** within the drained sim.
  - *delay* = mean **total delay = `timeLoss` + `departDelay`** (s) over trips.
    `timeLoss` is in-network delay; `departDelay` is time spent unable to enter
    (insertion backlog = spillback to source). **Both matter** — under
    oversaturation a controller can keep `timeLoss` low by holding vehicles out
    of the network, dumping the delay into `departDelay`. Reporting `timeLoss`
    only (the original bug, fixed 2026-07-12) hides this; see EXP-002 §3.4.
    Also: when trips don't complete (gridlock), completed-trip averages are
    survivorship-biased, so low delay next to low throughput is *worse*.
  - *halts* = mean `waitingCount` (distinct stops) over completed trips.
- **"drain"**: the eval runs demand for the 24 h day, then keeps simulating
  with no new arrivals until the network clears (to 30 h), so trips still en
  route at midnight are counted honestly rather than truncated.
- **Held-out day**: 0508 is never used in training; it is the generalization
  test. Training days: 0505, 0506, 0507.

## Index

| ID | Title | Outcome |
|----|-------|---------|
| [EXP-001](EXP-001_ordered-actuated-extend-advance/report.md) | Realistic ordered-actuated action space (binary extend/advance) + linear FA | **Negative** — degenerate policy, gridlocks at all demand levels incl. 0.5×. Root cause: representation under-expressiveness (lane weights shared across phases). |
| [EXP-002](EXP-002_phase-gated-features/report.md) | Phase-gated lane features (restore per-phase×lane expressiveness) | **Mixed / corrected.** Fixes the gridlock/degeneracy (real representation bug); throughput 100% at all scales. But on **total delay (incl. insertion backlog)**, RL beats fixed-time **only at 0.5× (v/c 0.62)**; from ~v/c 0.7 up it is worse (+98% to +440%, worst near capacity). Matches the paper. Also fixed a metrics bug (timeLoss-only undercounted oversaturated delay). **High-saturation performance is the open problem.** |
| [EXP-003](EXP-003_spillback-features/report.md) | Spillback-aware features (normalized occupancy + phase-gated elapsed) + norm-only ablation + multi-seed (003b) + **n=20 CIs over 0.5–1.8× (003c-stat, §4e)** | **Final (n=20, proper CIs):** PG-raw & PG-norm **significantly beat fixed-time at 0.5×** and are **indistinguishable from it at 0.8–1.8×** — never worse (the earlier "much worse at saturation" was a single-seed artifact); the added **elapsed-time feature makes it significantly worse** from 1.0× up (robust at 1.3×/1.8×) and less stable (35% vs 21% collapse); **no variant separable** from another after Holm. Bottleneck = training-seed variance, not mean delay. (Interim single-seed §4b "v3 is best" was overturned.) |

| [EXP-004](EXP-004_reward-baselines-capacity/report.md) | Reward alignment (+backlog), realistic baselines (actuated ×2 + cyclic max-pressure), strategy race (n=3 → n=10 re-test), per-phase max-green envelope, validation selection | **Positive — deployed (selected) policy beats every baseline at 4/5 loads incl. the 1.3× target** (507 s vs tuned-actuated 677, Webster 912; −25%/−55%/−59%/−47% at 1.3/1.0/0.8/0.5×; loses only 1.8× extrapolation), via paper-style validation selection (ρ_val↔test = 0.87, n=15). **But no arm's average beats either baseline at any n or scale (0.5–1.3×, §3c)** — EXP-004a/`rate` reach Webster *parity* at 1.3× and *significantly beat both baselines* at 0.5× (p<0.01); `age`/`rate+age`/unselected-S8 are significantly worse at 1.3×. n=3 screening picked `age` as tied with `rate`; at n=10 `age` turned out significantly worse (1560 vs 1084, p=0.027) — screening shortlists, it doesn't crown a winner. Per-seed reliability (not mean performance) is the open problem. |

| [EXP-005](EXP-005_oct2-real-timing/report.md) | 7065 on the newer data (Oct 2): real GDOT timing (calibrated NEMA) vs Webster vs tuned-actuated vs the EXP-004 RL policy, 1.0× unscaled, single run, per period | **Preliminary (v4, §2c).** **Found: the count report's direction labels are GDOT road-based (EB/WB = Piedmont, NB/SB = Peachtree), not compass — every earlier 7065 demand file, incl. the May training/test demand of EXP-001–004, had the four directions rotated.** On corrected demand (Poisson arrivals, default drivers): tuned-actuated 20.9, Webster 23.7, real timing 98.7, RL 188.3 s/veh whole day; the RL (trained on rotated demand) collapses at the PM peak on Peachtree SB — must be retrained. Real timing's PM peak is one movement at capacity (Piedmont from N), a twin-capacity calibration item. Also found & fixed: actuated baseline never detected SB/WB (short twin edges) — **EXP-004's tuned-actuated numbers are invalid**. Scaling method still to be tested. |
| [EXP-006](EXP-006_retrain-corrected-demand/) | RL retrained on corrected-direction demand (4-day and Sep-29-only, 8 seeds each) | **Stopped / superseded by EXP-007** at episode 1–7 of 20: it trained on the old `stages.py` phase model (permissive Peachtree dual lefts, no left→through clearance — capacity GDOT's controller doesn't have) and on the short twin. |
| [EXP-007](EXP-007_corrected-phase-model/report.md) | Baselines on corrected phases + extended twin, Oct 2 (Webster designed Sep 29) | **Done (baselines).** Real GDOT timing 51.2 (actuated, P1 forced to lead — SUMO limitation) / 51.5 (fixed-time, GDOT's exact order). Like-for-like Webster on GDOT's dual ring with pedestrian minimums: 39.0. (Webster without ped minimums 33.1 and 4-stage Webster 39.3 are not valid comparators.) RL on the simplified 4-stage model failed / was stopped → EXP-008. Caveats: counted volumes as demand, Poisson arrivals, extension fitted on test day. |
| [EXP-008](EXP-008_dualring-rl/report.md) | Linear-FA + LSTDQ RL on GDOT's 8-phase dual ring (`rlagent/dualring_env.py`): exact ring order, measured clearances/min greens, ped minimums, GDOT max greens; 1 seed, 10 episodes, Sep 29 at 1.0×; tested Oct 2 | **Preliminary (1 seed, 1 day).** RL 36.6 s/veh whole day Oct 2 vs Webster dual ring + peds 39.0 vs real 51.2/51.5; all served, 0 teleports; constraints verified by monitor. Not yet repeated over seeds/days. |
| [EXP-009](EXP-009_significance/report.md) | Significance test on the 90-day dataset (7065): train Jul 10–Aug 31, validation Sep 1–16, test Sep 17–Oct 2 (10 weekdays × 10 reps), Saturdays separate; real GDOT timing vs Webster (dual ring + ped minimums) vs dual-ring LSTDQ (5 seeds); `matrix.py` launcher | **Done (v4: SUMO 1.27.1 pinned, fixed lane lengths, driver sigma 0.2 → ~1,920 veh/h/lane; audited).** LSTDQ beats Webster on 10/10 test weekdays (34.9 vs 38.6 s/veh, day-level Holm p = 0.0059) and 12/12 Saturdays (32.8 vs 36.7, p = 0.0015); 4 of 5 seeds win every day. Margin depends on the capacity calibration (sigma 0.5 gave 38.1 vs 47.2). Real timing: valid only on Saturdays (43.4, loses 12/12); weekdays still over the twin's capacity on Piedmont-N through. v1–v3 archived. **Replicated on an independently built OSM network** ([report_7065osm.md](EXP-009_significance/report_7065osm.md); 3 documented lane/speed tag fixes on the Piedmont north leg): RL beats Webster 36.3 vs 38.5 s/veh weekdays (9/10 days, Holm p = 0.0059, but significant for only 2 of 5 seeds; all seeds lose on Sep 24) and 12/12 Saturdays; real timing loses 12/12 Saturdays on both networks. |

## Planned / backlog (not yet started)

- **EXP-003c — robustness fix.** The parking variance has two compounding
  causes (see EXP-003 §4b/§4c): (i) partial observability — phase-gating hides
  the starved approaches from the advance decision; (ii) an **ill-conditioned
  LSTDQ solve** (`A` singular; `cond(A+ridge·I)`≈1e8–1e10; ridge-sensitive ~1.5;
  non-PD) that leaves the elapsed-time weight under-determined and
  counter-intuitively signed. Candidate fixes: (a) non-gated global per-approach
  queue summary; (b) raise/cross-validate ridge; (c) drop the redundant phase
  one-hot / use one global elapsed feature; (d) SVD/pseudo-inverse solver;
  (e) enforce max-green in the env instead of learning it via elapsed (removes
  the destabilizing feature, hard-bounds parking).
- **EXP-003c-stat — multi-seed confidence intervals. ✅ DONE (n=20).** All three
  variants retrained to 20 seeds; equal-n bootstrap CIs vs fixed + seed-paired
  Holm-corrected pairwise tests (EXP-003 §4e, `data/finalize_ci.py`,
  `data/ci_final.txt`). **Result overturns the single-seed narrative:** PG-raw
  and PG-norm are **statistically indistinguishable from fixed-time at every
  scale** (the old "+247–440% worse" was one unlucky seed each); **PG-elapsed is
  significantly *worse* than fixed** (1.3×/1.8× robust) with a 35% collapse rate
  vs 21% for the others; **no variant separable from another** after Holm. The
  bottleneck is training-seed variance (21–35% collapse), not mean delay.
- **EXP-004 — reward redesign.** The `−queue` reward is gameable under
  oversaturation (RL sheds delay into insertion backlog; see EXP-002 §3.4).
  Try a throughput- / total-delay-aware reward that penalizes insertion
  backlog. EXP-003 lets the agent *see* spillback; the reward may be needed to
  make it *act* on it.
- **Stronger baselines (deferred until real signal data is available).** Our
  current baseline is *pretimed Webster* — the weaker of the paper's two
  baselines. The real SIG#7065 signal is **actuated** (gap-out records in
  ATSPM) + time-of-day. Planned: (a) a passage-time / gap-out **actuated
  baseline** (paper Appendix A), and (b) comparison vs the **real timing plan**
  if the ATSPM phase-switching data can be extracted. Report RL vs both.
- **DRL / other adaptive baselines (EXP-005/006+).** Compare the linear-FA
  method against deep RL (DQN, etc.) and other adaptive controllers — the
  interpretability-vs-performance trade-off is the point.

## Cross-cutting: infrastructure notes

- **Simulation backend**: headless training/eval uses `libsumo` (in-process),
  ~5.5× faster than the TraCI socket here (12 s → 2.2 s for a 1 h window);
  GUI (`watch.py`) uses TraCI. Selected automatically by `sumo_env.py`.
- **Reproducibility / failsafe**: `train_random.py` checkpoints weights +
  accumulated experience + RNG state every episode (atomic write); `--resume`
  continues bit-exactly (verified: a resumed episode was byte-identical to the
  uninterrupted run).
- **Baseline**: Webster fixed-time (`fixed_time.py`) runs on the *same* env
  and the *same* 4-phase cycle, so RL-vs-fixed differ only in *when* they
  advance — a fair, apples-to-apples comparison.
