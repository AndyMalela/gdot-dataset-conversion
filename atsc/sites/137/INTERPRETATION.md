# 137: what the results mean (v2, 2026-11-18, revised after an independent critique)

Sources: `eval/analysis.md` (20 validation days, sim seed 1), `eval_test/analysis.md` (7 test days, sim seeds 1–5),
per-movement delay from `eval*/hour_mv.csv`, isolation runs `eval_iso_oldw/`, `eval_iso_last/`. All after
amendment 1 (TEST_PLAN.md). Ratio = delay / actuated, geometric mean over days. Everything below is interpretation of
the registered results; numbers not in the registered analysis are marked **post hoc**.

v1 of this file was checked claim by claim by a separate reviewer (every headline ratio reproduced). Claims it
overturned are listed in §9 so the change is visible.

## 0. Headline numbers

| | Validation ratio | Test ratio (95 % CI) | Test verdict |
|---|---|---|---|
| LSTDQ | 0.958 | 1.014 (0.95–1.08) | equivalent |
| MaxPressure | 1.003 | 1.037 (0.89–1.20) | inconclusive |
| Q-learning | 1.098 | 1.190 (0.95–1.49) | inconclusive |
| ARS | 1.144 | 1.192 (1.00–1.42) | inconclusive |
| GDOT plan | 1.186 | 1.239 | worse |
| Webster | 2.48 | 4.35 | worse |

## 1. Equal average delay is a transfer, not a gain

Mean delay per movement (s/veh), test days; validation in brackets:

| movement | share of veh | actuated | LSTDQ | MaxPressure | Q-learning | ARS |
|---|---|---|---|---|---|---|
| EB through (W Paces Ferry) | 31 % | 25.0 (25.2) | 17.9 (17.9) | 19.0 (19.2) | 24.8 (25.4) | 30.7 (30.7) |
| WB through | 16 % | 27.3 (30.7) | 22.7 (28.2) | 21.4 (37.4) | 22.8 (39.2) | 28.6 (70.6) |
| SB through (side) | 7.5 % | 38.4 (36.8) | 54.3 (44.3) | 75.0 (62.6) | 84.3 (70.4) | 63.5 (49.0) |
| SB left (side) | 8.6 % | 31.4 (31.1) | 49.4 (43.5) | 48.0 (41.4) | 51.1 (50.8) | 38.4 (34.3) |
| NB left (side) | 3.9 % | 33.4 (27.3) | 47.8 (36.6) | 35.2 (30.0) | 70.9 (32.4) | 61.0 (31.7) |

- **Robust:** every LSTDQ seed has higher side-street delay than actuated on 7/7 test days and 19–20/20 validation
  days. Vehicle-weighted, LSTDQ saves 3.3 s/veh on the main street and adds 3.6 s/veh on the side street on the
  test days (net +0.4; validation net −0.7). It is close to one-for-one.
- **HCM view (post hoc, control delay per movement):** SB through actuated 38 s (LOS D), LSTDQ 54 (D), MaxPressure
  75 (E), Q-learning 84 (F). Same average, different level of service for the side street.
- Worst-served movement (95th-percentile delay) is lowest for actuated in every saturation band on both day sets.
- **Two causes, both to state:**
  1. *Objective.* All learners are trained on a vehicle-weighted signal (LSTDQ/Q-learning reward = minus
     vehicles × slowdown, `rl/agent.py`; ARS = minus window delay in s/veh), and MaxPressure weighs queues by vehicle
     count. 58 % of vehicles are on W Paces Ferry, so serving it is cheap per vehicle.
  2. *Detector layout (likely the larger part).* Main-street throughs have Wavetronix Advance count zones at 79 m;
     side-street throughs and all lefts have only ~12 m stop-bar zones (`detectors.json`). The queue estimate that
     feeds MaxPressure and the learners' state therefore sees only the first 1–2 vehicles of a side queue. The
     controllers cannot weigh what they cannot see. *To test:* log estimated vs true queue per phase.
- Actuated's balance is not "no objective": its side-street passage times were fitted to GDOT's field gap-out
  shares (P4 4 s, P8 8 s), so it carries the field's practice of serving the side street.
- **Domain reading:** for an adaptive controller, *what the detectors can see* and *what the objective counts* decide
  who gets served. "Equivalent average delay" is not equivalent service; HCM rates each approach separately.

## 2. Heavy traffic: cycle length helps, but surge response decides

- Validation heavy hours (Y ≥ 0.6): LSTDQ 31.3, actuated 31.5, MaxPressure 39.0, Q-learning 48.5, ARS 62.0 s/veh.
  Actuated (96 s) and LSTDQ (92 s) lengthen the cycle with demand; MaxPressure (~72 s) does not. Each switch costs
  yellow + all-red + start-up (~5–6 s), which Webster's formula charges and MaxPressure's theory treats as free.
- **But on the test days cycle length does not explain it:** LSTDQ (92 s) loses as much as MaxPressure (72 s),
  31.1 vs 31.5; Q-learning's pooled greens are almost the same as MaxPressure's, yet 41.1 vs 31.5 s/veh. The
  difference is how each reacts to sudden side-street surges (§5), not its average timing.
- GDOT's coordinated plan runs 127–133 s in busy/heavy hours (shared cycle with 138) and pays ~20–24 % delay at
  137 for corridor coordination whose wider benefit is outside the model.

## 3. Light traffic: learned policies fail where training rarely cost anything

- Night (00–06), test: actuated 8.2, Q-learning 8.1, ARS 8.5, GDOT 8.2 vs LSTDQ 11.6, MaxPressure 11.2 s/veh.
- LSTDQ also loses at hours that *are* in its training windows: hour 22 1.09 (val) / 1.12 (test), hour 6 1.15
  (val). All 5 seeds run long light-traffic cycles (108–146 s), holding side-through greens to max (47 % max-out).
- The state is not blind: it contains stop-bar occupancy, time since the last detection (gap) and arrival rate per
  phase — the same information actuated uses. Q-learning and ARS, with the same state and the same training windows
  (no 23–06 h), match actuated at night. So the cause is LSTDQ's learned weights in a light-traffic regime that
  costs little delay during training (light hours carry few vehicles, so errors there barely move the objective).
- MaxPressure's night problem is mechanical: one waiting side vehicle seen at a 12 m stop-bar zone rarely
  out-pressures the main street's trickle, so the main street holds to max (25 % max-outs, 117 s cycle).
- **Domain reading:** the passage-time rule needs no training data for any regime; it is the robust default.
  A learned controller needs either weight on light-traffic errors in training, or a fallback to gap-out logic.

## 4. Fixed-time: designed to the median, it fails on half the days

- Webster's evening plans (84 s cycle) give EB through ~24 s of green on one shared lane: ~630 veh/h capacity.
  EB through at 21:00: validation median 458 veh/h, test median 637, test max 908. 60 % of Webster's test delay
  is in hours 20–23, 81 % of it on EB through (303 s/veh).
- Root cause: `baselines.py` designs to the **median** 5-min counts with X_max 0.9, so the plan is built to
  saturate on roughly half the days; late-May evening demand is higher still.
- The amendment did not change the evening plans (84.5 → 84.3 s); Webster's larger test number comes from F2
  (vehicles that never got in are now scored: up to 153 per run on test, 560 on validation).
- **Domain reading:** this is the retiming argument. A fixed plan has no slack for day-to-day and seasonal
  variation; the design percentile (median vs 85th / peak-15-min) matters more than the formula.

## 5. Validation → test: a holiday week and side-street surges, not "learner drift"

- All adaptive controllers lose a little from validation to test, learners and rule controllers by similar amounts
  (log-ratio change: LSTDQ +0.056, Q-learning +0.080, ARS +0.041, MaxPressure +0.033, GDOT +0.043; none
  significant, p 0.08–0.71). v1's claim that learners drift more is **not supported**.
- **Post hoc:** the test loss sits in six side-street surge hours (05-20 17h, 05-26 13/17/18h, 05-29 17/18h).
  Without them, LSTDQ 0.966 and MaxPressure 0.962, back at validation level.
- **05-26 is the Tuesday after Memorial Day**, the worst day for every adaptive controller (LSTDQ 1.165,
  MaxPressure 1.453, Q-learning 1.851). Its 13h counts look anomalous: EB through 265 vs 557–624 on the other test
  days, SB through 305 vs 132–214. Flagged under the fidelity rule (not corrected, not dropped).
- **Domain reading:** the hard cases for adaptive control are sudden side-street surges (holiday-week traffic,
  diversions), where actuated's gap logic reacts at once and the learned / pressure controllers, seeing short
  side queues (§1), react late.

## 6. What drives LSTDQ's result (isolation, validation days)

| | ratio | per seed |
|---|---|---|
| old weights, buggy engine | 1.022 | |
| old weights, fixed engine | 1.025 | 0.974 1.109 0.987 1.018 1.040 |
| retrained, last snapshot | 1.001 | 1.032 1.025 0.919 1.013 1.020 |
| retrained, selected snapshot | 0.958 | 0.926 0.945 0.944 0.951 1.020 |

- Fixing the engine alone does not help the old policy. Retraining: mixed per seed (+0.058 … −0.084), i.e. within
  seed noise. Selection: 3 seeds better, 1 worse (seed 2), 1 unchanged.
- The selection signal is weak: seed 3's it4 vs it5 differ by 0.8 % on the train windows but 6 % on validation.
- Confound: "old weights, fixed engine" changes the engine (F1), the queue-feature scale (F3) and actuated's refit
  at once.
- **Methods insight:** for all three learners, *which iterate is deployed* moves the result as much as the
  algorithm; small differences between LSTDQ seeds and iterates are not interpretable individually.

## 7. The three learners: one detector state, three ways to learn

All three share the v2 state (per-phase occupancy, gap, arrival rate, queue estimate, phase timing), the same
training windows (06–10, 11–15, 15:30–19:30, 19:30–23) and train days, and a delay-based training signal. They
differ in what is learned and how:

| | LSTDQ (LSPI) | Q-learning | ARS |
|---|---|---|---|
| What is learned | linear Q(extend), Q(end): 624 weights | the same linear Q | a 312-weight threshold rule: end when θ·x > 0 (no value function) |
| How | least-squares (ridge) solve of the Bellman fixed point per round, on all data so far | online TD (Watkins) with a constant normalised step that never decays | random search: 11 directions × 2 per iteration on the 4-h window delay |
| Data / budget of deployed iterate | 44–110 window-episodes | 22–44 (seed 3 = iterate 1, learnt only from actuated + 20 % random data) | 220–1,100 |
| Training behaviour | stable after round 1 | best at round 1–2, then |w| grows 28 → 189 and delay rises | noisy (±2–6 s/veh between iterates), no trend |
| Test ratio / days won | 1.014 / 4 of 7 | 1.190 / 2 of 7 | 1.192 / 1 of 7 |
| Night (test, actuated 8.2) | 11.6 | **8.1** | **8.5** |
| Heavy (val / test; actuated 31.5 / 29.3) | **31.3 / 31.1** | 48.5 / 41.1 | 62.0 / 42.4 |
| Signature behaviour | long main green (40–45 s busy/heavy), long light-traffic cycles | lefts at about their minimum (7.1–7.7 s vs 6.0), MaxPressure-like greens; seed spread large (seed 3 runs a 98 s cycle) | phase-specific max-outs: P5 47 %, P7 35 % in heavy hours, P1/P3 ~0 % |

- **Q-learning (same model as LSTDQ, online solver).** Off-policy data, function approximation and bootstrapping
  are shared with LSTDQ, so the "deadly triad" alone does not separate them; the difference is the solver: a
  closed-form least-squares solve per round vs a stochastic update with a step that never decays, whose weights
  grow without bound. It is only usable when stopped early, and what is then deployed is a simple near-minimum
  policy: good in light traffic (best night result), worst under heavy load. **Insight:** with the same linear
  model, the solver decides whether the controller is deployable (Lagoudakis & Parr 2003's argument for LSPI,
  reproduced on a real NEMA intersection).
- **ARS (policy search, no Bellman structure).** 10× the simulation of LSTDQ and still ~19 % worse. θ starts at 0,
  i.e. "never end" = hold every phase to max; phase blocks that the search barely moves keep that default, which
  fits the P5/P7 max-outs (hypothesis, to test: ‖θ‖ per phase block). With 312 weights and 11 directions per step,
  random search is sample-starved, and phases that matter little to window delay are never tuned. **Insight:**
  direct optimisation of the true objective (the appeal of policy search, Ault 2020) does not compensate for
  ignoring the step-by-step structure on a NEMA action space with 4-h episodes.
- **What the comparison gives that one learner could not:** the night result separates training coverage from
  learned bias (§3); Q-learning separates model from solver; ARS separates value-based from direct policy search.
  Each learner is best somewhere: Q-learning and ARS in light traffic, LSTDQ in busy and heavy hours.

## 8. What is robust and what is not

Robust (same direction on validation and test, all seeds): side-street penalty of every optimising controller
(§1); actuated best on worst movement; actuated and gap logic best in light traffic and surges; Webster's evening
collapse; Q-learning's divergence and ARS's max-out signature.

Not robust: rankings inside a condition band when controllers are within ~5 % (heavy hours: validation LSTDQ >
actuated, test actuated > LSTDQ; PM peak: validation MaxPressure best, test actuated best); individual seed or
iterate differences (§6); "learners drift more" (§5).

Caveats with everything: one site; Y ≥ 0.6 only in a few hours, beyond that only the demand sweep (learners trained
at ×1); V3 (the model serves left arrows more often than the field); side-street demand corrected from
presence-zone counts (residual bias of unknown sign); second look at the test days (amendment 1); learners never
trained on 23–06 h.

## 9. What changed from v1 after the critique

| v1 claim | status |
|---|---|
| "queue-based state is blind at night, needs gap features" | **wrong**: the state has gap, occupancy and rate; Q-learning and ARS use it and match actuated at night |
| "learners lose more under drift" | **not supported** (similar change for rule controllers; surge hours and 05-26 explain it) |
| "F3 shortened Webster and caused the collapse" | **wrong**: evening plans unchanged; median design + F2 scoring |
| presence-zone undercount means side penalty understated | **sign unknown** (demand already corrected) |
| "retraining gave a little" | **within seed noise** |
| short cycles explain heavy-hour losses | **half**: holds on validation, not on test |
| Q-learning "every green at minimum"; ARS "same linear Q, ~600 weights"; deadly triad separates the learners | **corrected** in §7 |
| "actuated is fairer because it has no objective" | **reframed**: its side passage times are fitted to field practice; detector layout is the other cause |

## 10. Open analyses (ranked)

1. Cheap: day-hour decomposition validation vs test, with and without surge hours; data check of 05-26 13h.
2. Short runs: log the queue estimate vs true halting vehicles per phase (tests the detector-layout cause of §1).
3. Cheap: per-approach HCM LOS table and residual side queue (`backlog_max`) as a phase-failure proxy.
4. Cheap, learner-specific: Q-learning |w| and greedy delay per iterate, green minus minimum per phase over all
   seeds; ARS ‖θ‖ per phase block and share of states with θ·x ≤ 0 for P5/P7; LSTDQ Q(end) − Q(extend) on
   light-traffic states.
5. Runs: Webster designed to the 85th percentile / peak 15 min.

Fixes to the analysis outputs (no effect on the registered comparison): headers say "attempt 7" (now attempt 8);
RQ2 mech tables use training seed 0 and, on test, keep one simulation seed per hour; the worst-movement metric
has no minimum-volume filter and takes the max over 5 simulation seeds on test vs 1 on validation; Y bands use
1,950 veh/h rather than the measured saturation flow; `evaluate.py` docstring still describes 7065.
