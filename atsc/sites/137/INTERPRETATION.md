# 137: what the results mean (v3, 2026-11-18: all comparisons in seconds)

**How to read the numbers.** Unless a table says otherwise, every number is **delay per vehicle in seconds
(s/veh), lower is better**: the time each vehicle loses compared with driving freely, including time spent waiting
to enter the network, averaged over all vehicles (each vehicle counts once). Learners are averaged over their 5
training seeds. "Difference to actuated" = method minus actuated, so **negative = less delay than actuated
(better)**. "Days won" = days on which the method had less delay than actuated, **higher is better**.

**Day sets.** Validation = 20 weekdays 04-20..05-15 (simulation seed 1). Test = 7 held-back weekdays 05-18..05-29
(simulation seeds 1–5). All results are from the attempt-8 model (TEST_PLAN.md amendment 1).

**Statistics.** The registered tests (TEST_PLAN.md) were run on the daily ratio delay / actuated delay. This file
quotes only their verdicts and p-values; every number shown is in seconds. Numbers outside the registered analysis
are marked **post hoc**.

**Sources.** `eval/analysis.md` (validation), `eval_test/analysis.md` (test), per-day delays `eval*/runs.csv`,
per-movement and per-hour delays `eval*/hour_mv.csv`, controller behaviour `eval*/mech.csv`, isolation runs
`eval_iso_oldw/`, `eval_iso_last/`, demand sweep `eval_x*/`. v1 was checked claim by claim by a separate reviewer;
overturned claims are listed in §9.

## 0. Headline numbers

Delay per vehicle (s/veh), lower is better. Last three columns: test days only.

| method | validation (20 days) | test (7 days) | test: mean daily difference to actuated (lower is better) | test: days won vs actuated (higher is better) | test verdict (registered) |
|---|---|---|---|---|---|
| actuated (free) | 25.3 | 24.9 | reference | reference | reference |
| LSTDQ | 24.6 | 25.3 | +0.4 | 4 of 7 | **equivalent** (within the 2 s/veh margin, p TOST 0.026) |
| MaxPressure | 27.6 | 26.1 | +1.3 | 4 of 7 | not settled |
| ARS | 36.5 | 30.4 | +5.5 | 1 of 7 | not settled |
| Q-learning | 31.5 | 30.6 | +5.7 | 2 of 7 | not settled |
| GDOT plan (deployed) | 34.3 | 31.2 | +6.4 | 0 of 7 | worse (p Holm 0.046) |
| Webster | 122.0 | 117.7 | +91.8 | 0 of 7 | worse (p Holm 0.001) |

- "Equivalent" = shown statistically to be within the margin fixed before any result: per day max(2 s/veh, 5 % of
  actuated), which is 2 s/veh on every test day (2.3 s/veh on one validation day). "Not settled" = the day-to-day spread is too large to call either a tie
  or a difference.
- Validation (registered): LSTDQ is equivalent to actuated and also has significantly less delay (mean daily
  difference −0.7 s/veh, 19 of 20 days won, p Holm 0.021). GDOT plan and Webster are worse; MaxPressure,
  Q-learning and ARS are not settled.

## 1. Who gets served: against free actuated a transfer, against the deployed plan a side-street gain

Main street = EB/WB lefts and throughs (W Paces Ferry, 58 % of vehicles on test); side = all NB/SB movements.

Delay per vehicle (s/veh), lower is better. Test days (validation in brackets):

| | main street | side street |
|---|---|---|
| GDOT plan (deployed) | 18.2 (18.7) | 49.6 (56.8) |
| LSTDQ | 19.2 (20.9) | 33.8 (30.0) |
| MaxPressure | 19.2 (24.3) | 35.9 (32.4) |
| Q-learning | 22.8 (28.2) | 41.5 (36.1) |
| ARS | 27.7 (41.2) | 34.2 (29.5) |
| actuated (free) | 24.7 (25.9) | 25.1 (24.5) |

- **Against the deployed controller (GDOT plan), the learners mainly help the side street.** The coordinated plan
  favours the arterial (its coordinated phases take the cycle's spare time), and the side street waits 49.6 s.
  LSTDQ keeps nearly the same main-street delay (+1.0 s) and cuts side-street delay by 15.8 s.
- **Against free actuated, it is a transfer.** Free actuated reaches about the same overall delay as LSTDQ by
  spreading it evenly (main 24.7, side 25.1). Compared with free actuated, LSTDQ's main street is 5.5 s/veh lower and
  its side street 8.7 s/veh higher. Weighted by how many vehicles use each, that is −3.2 s/veh (main) and +3.6 s/veh
  (side) on test, net +0.4; on validation −3.0 and +2.3, net −0.7.
- Overall, test days: GDOT plan 31.2, LSTDQ 25.3, free actuated 24.9 s/veh. LSTDQ, MaxPressure and free actuated
  have less delay than the GDOT plan on 7 of 7 test days (Q-learning, ARS 5 of 7); LSTDQ and actuated on 20 of 20
  validation days. Descriptive: the registered comparisons are against free actuated, not the GDOT plan.
- Free actuated is a what-if: the deployed controller's fitted detector settings run without its cycle. The field
  does this only at night (in every night hour the two give identical delay, checked). Its daytime behaviour is not
  validated directly.

Delay per movement (s/veh), lower is better. Test days (validation in brackets); "share" = share of all vehicles:

| movement | share | GDOT plan | actuated | LSTDQ | MaxPressure | Q-learning | ARS |
|---|---|---|---|---|---|---|---|
| EB through (W Paces Ferry) | 31 % | 18.9 (19.4) | 25.0 (25.2) | 17.9 (17.9) | 19.0 (19.2) | 24.8 (25.4) | 30.7 (30.7) |
| WB through | 16 % | 18.0 (19.2) | 27.3 (30.7) | 22.7 (28.2) | 21.4 (37.4) | 22.8 (39.2) | 28.6 (70.6) |
| SB through (side) | 7.5 % | 75.7 (112.1) | 38.4 (36.8) | 54.3 (44.3) | 75.0 (62.6) | 84.3 (70.4) | 63.5 (49.0) |
| SB left (side) | 8.6 % | 75.6 (98.0) | 31.4 (31.1) | 49.4 (43.5) | 48.0 (41.4) | 51.1 (50.8) | 38.4 (34.3) |
| NB left (side) | 3.9 % | 103.7 (54.5) | 33.4 (27.3) | 47.8 (36.6) | 35.2 (30.0) | 70.9 (32.4) | 61.0 (31.7) |

- **Robust (against free actuated):** every LSTDQ seed has more side-street delay than actuated on 7 of 7 test days
  and 19–20 of 20 validation days.
- **HCM view (post hoc; simulated delay used as control delay; level of service A = best … F = worst), SB through on
  test:** actuated 38 s (D), LSTDQ 54 s (D), MaxPressure 75 s (E), GDOT plan 76 s (E), Q-learning 84 s (F). The
  same overall average can mean a different level of service for the side street.
- Worst-served movement (95th-percentile delay of the worst movement in the hour, lower is better) is lowest for
  actuated in every traffic-level band on both day sets (caveat on this metric in §10).
- **Two likely causes (neither tested yet), both to state:**
  1. *Objective.* All learners are trained on a vehicle-weighted signal (LSTDQ/Q-learning reward = minus
     vehicles × slowdown, `rl/agent.py`; ARS = minus window delay in s/veh), and MaxPressure weighs queues by vehicle
     count. 58 % of vehicles are on W Paces Ferry, so serving it is cheap per vehicle.
  2. *Detector layout (likely the larger part).* Main-street throughs have Wavetronix Advance count zones at 79 m;
     side-street throughs and all lefts have only ~12 m stop-bar zones (`detectors.json`). The queue estimate that
     feeds MaxPressure and the learners' state therefore sees only the first 1–2 vehicles of a side queue. The
     controllers cannot weigh what they cannot see. *To test:* log estimated vs true queue per phase.
- Actuated's even split is not "no objective": it is the deployed controller's detector settings (passage times
  fitted to GDOT's field gap-out shares, P4 4 s, P8 8 s) without the cycle and split limits, so a side-street green
  can run as long as cars keep coming. The field itself, under the coordinated plan, serves the side street worst
  (tables above).
- **Domain reading:** for an adaptive controller, *what the detectors can see* and *what the objective counts* decide
  who gets served. Equal average delay is not equal service; HCM rates each approach separately.

## 2. Heavy traffic: cycle length helps, but surge response decides

Heavy hours = hours with Y ≥ 0.6 (Y = traffic vs capacity, the sum of critical flow ratios from the field counts;
higher = busier). Delay per vehicle (s/veh), lower is better; cycle length (s) is descriptive:

| heavy hours | actuated | LSTDQ | MaxPressure | Q-learning | ARS | GDOT plan |
|---|---|---|---|---|---|---|
| validation delay (110 hours) | 31.5 | **31.3** | 39.0 | 48.5 | 62.0 | 50.6 |
| test delay (40 hours) | **29.3** | 31.1 | 31.5 | 41.1 | 42.4 | 38.7 |
| validation cycle | 99 | 96 | 73 | 74 | 74 | 133 |
| test cycle | 96 | 96 | 72 | 73 | 73 | 133 |

- On validation, actuated and LSTDQ lengthen the cycle with demand and do best; MaxPressure, Q-learning and ARS
  stay near 72–74 s and lose. Each switch costs yellow + all-red + start-up (~5–6 s), which Webster's formula
  charges and MaxPressure's theory treats as free.
- **On test, cycle length does not explain it:** LSTDQ runs the same 96 s cycle as actuated and still has 1.8 s/veh
  more delay; MaxPressure (72 s) is about the same as LSTDQ (31.5 vs 31.1). Q-learning's heavy-hour greens are
  almost the same as MaxPressure's (main-street throughs 32.0/30.4 s vs 32.5/30.7 s per service), yet its delay is
  41.1 vs 31.5. The difference is how each reacts to sudden side-street surges (§5), not its average timing.
- GDOT's coordinated plan runs 130–133 s in busy and heavy hours (shared cycle with 138) and has more delay than
  actuated at 137: busy hours +3.5 (validation) / +5.0 (test) s/veh, heavy hours +19.1 / +9.4 s/veh. That is the
  local cost of corridor coordination, whose wider benefit is outside the model.

## 3. Light traffic: LSTDQ fails at night, where Q-learning and ARS do not

Delay per vehicle (s/veh), lower is better. Night = 00–06 h, outside every learner's training windows; hours 6 and
22 are at the edges of the training windows (06–10, 19:30–23):

| | actuated | LSTDQ | Q-learning | ARS | MaxPressure | GDOT plan |
|---|---|---|---|---|---|---|
| night 00–06, validation | **9.2** | 12.4 | 9.8 | 10.1 | 13.8 | **9.2** |
| night 00–06, test | 8.2 | 11.6 | **8.1** | 8.5 | 11.2 | 8.2 |
| hour 6, validation | **17.1** | 19.7 | 35.2 | 30.6 | 34.0 | 28.2 |
| hour 6, test | **14.9** | 15.9 | **14.9** | 15.2 | 15.2 | 20.2 |
| hour 22, validation | 15.3 | 16.6 | **15.1** | 15.9 | **15.1** | 15.6 |
| hour 22, test | **19.9** | 22.3 | 23.3 | 27.7 | 21.2 | 20.5 |

- **At night LSTDQ has 3.2–3.4 s/veh more delay than actuated; Q-learning and ARS are within 0.9 s of it.** None of
  the three learners was trained on 23–06 h, so lack of night training data alone does not explain LSTDQ's loss.
- In light-traffic hours (Y < 0.3) all 5 LSTDQ seeds run long cycles (108–146 s on test; actuated 91 s), and their
  side-street through greens end at their maximum in 43 % (P4) and 54 % (P8) of services (actuated 0 %).
- The state is not blind: it contains stop-bar occupancy, time since the last detection (gap) and arrival rate per
  phase — the same information actuated uses. Since Q-learning and ARS use the same state and match actuated at
  night, the likely cause is LSTDQ's learned weights in a regime that costs little delay during training (light
  hours carry few vehicles, so errors there barely move the training objective). Inference, not tested.
- **Hours 6 and 22 do not single out LSTDQ:** there every learner is often behind actuated, and Q-learning and ARS
  by more (hour 6 validation: +18.1 and +13.5 s/veh; hour 22 test: +3.4 and +7.8 s/veh; LSTDQ +1.0 to +2.6).
- MaxPressure's light-traffic problem is mechanical: one waiting side vehicle seen at a 12 m stop-bar zone rarely
  out-pressures the main street's trickle, so the main street holds to its maximum (main-through greens end at max
  in 25–27 % of services; 118 s cycle in light hours on test).
- **Domain reading:** the passage-time rule needs no training data for any regime; it is the robust default.
  A learned controller needs either weight on light-traffic errors in training, or a fallback to gap-out logic.

## 4. Fixed-time: designed to the median, it fails on half the days

- Webster's evening plan (20:00–22:00, 84.3 s cycle) gives EB through 24.4 s of green on one shared lane: about
  630 veh/h of capacity. EB through demand at 21:00: validation median 458 veh/h, test median 637, test maximum 908.
- 60 % of Webster's total test delay falls in hours 20–23. Over the whole test day, 81 % of its delay is on EB
  through, which averages 303 s/veh (1,116 s/veh in hours 20–23).
- Root cause: `baselines.py` designs to the **median** 5-min counts with X_max 0.9, so the plan is built to
  saturate on roughly half the days; late-May evening demand is higher still.
- The amendment did not change the evening plans (84.5 → 84.3 s cycle); Webster's larger test delay comes from F2
  (vehicles that never got in are now scored: up to 153 per run on test, 560 on validation).
- **Domain reading:** this is the retiming argument. A fixed plan has no slack for day-to-day and seasonal
  variation; the design percentile (median vs 85th / peak 15 min) matters more than the formula.

## 5. Validation → test: a holiday week and side-street surges, not "learner drift"

Mean daily difference to actuated (s/veh, method minus actuated; lower is better; registered secondary measure).
Change = test minus validation (positive = fell further behind actuated):

| | validation | test | change |
|---|---|---|---|
| LSTDQ | −0.74 | +0.41 | +1.15 |
| MaxPressure | +2.10 | +1.31 | −0.79 |
| Q-learning | +5.76 | +5.74 | −0.02 |
| ARS | +10.44 | +5.46 | −4.98 |
| GDOT plan | +8.57 | +6.36 | −2.21 |

- **No sign that learners drift more than rule controllers.** In seconds, only LSTDQ's gap to actuated grows; the
  others shrink or stay. A few validation days with very large delays for some controllers (GDOT plan up to
  115 s/veh above actuated on one day) inflate their validation averages. On the daily-ratio scale every adaptive
  controller moves slightly against actuated, by similar amounts (none significant, p 0.08–0.71). Either way, v1's
  claim that learners drift more is **not supported**.
- **Post hoc: six side-street surge hours** (05-20 17h, 05-26 13/17/18h, 05-29 17/18h). Delay per vehicle (s/veh),
  lower is better, test days:

| | all test hours | without the 6 surge hours | the 6 surge hours only |
|---|---|---|---|
| actuated | 24.9 | 24.0 | **39.1** |
| LSTDQ | 25.3 | 23.1 | 58.0 |
| MaxPressure | 26.1 | **23.0** | 74.8 |
| Q-learning | 30.6 | 25.2 | 114.5 |
| ARS | 30.4 | 26.2 | 95.7 |
| GDOT plan | 31.2 | 27.7 | 85.4 |

  Without those hours, LSTDQ and MaxPressure are 0.9–1.0 s/veh below actuated, as on the validation days.
- **05-26 is the Tuesday after Memorial Day** and the day with the largest gap to actuated for every adaptive
  controller. Delay that day (s/veh, lower is better): actuated 25.0, LSTDQ 29.1 (+4.1), MaxPressure 36.3 (+11.3),
  ARS 37.5 (+12.5), Q-learning 46.2 (+21.3). Its 13h counts look anomalous: EB through 265 veh vs 549–624 on the
  other test days, SB through 305 vs 132–214. Flagged under the fidelity rule (not corrected, not dropped).
- **Domain reading:** the hard cases for adaptive control are sudden side-street surges (holiday-week traffic,
  diversions), where actuated's gap logic reacts at once and the learned / pressure controllers, seeing short
  side queues (§1), react late.

## 6. What drives LSTDQ's result (isolation, validation days)

Delay per vehicle (s/veh), lower is better. Each row is a separate set of runs on the 20 validation days, with the
actuated delay of the same runs for reference:

| LSTDQ version | actuated in same runs | LSTDQ, 5 seeds | seed 0 | seed 1 | seed 2 | seed 3 | seed 4 |
|---|---|---|---|---|---|---|---|
| old weights, engine before fix | 25.8 | 26.7 | 25.0 | 30.2 | 25.8 | 26.3 | 26.2 |
| old weights, fixed engine | 25.3 | 26.3 | 24.7 | 29.3 | 25.2 | 25.8 | 26.6 |
| retrained, last iterate | 25.3 | 25.8 | 27.2 | 26.2 | 23.3 | 26.4 | 25.7 |
| retrained, selected iterate (registered) | 25.3 | **24.6** | 23.8 | 24.2 | 24.7 | 24.5 | 25.7 |

- Fixing the engine alone does not help the old policy (gap to actuated +0.9 → +1.0 s/veh).
- Retraining (old weights → last iterate, same engine) is mixed per seed: +2.5, −3.1, −1.9, +0.6, −0.9 s/veh
  (5 seeds together −0.5): within seed noise.
- Selecting the iterate on train days (last → selected): −3.4, −2.0, +1.4, −1.9, 0.0 s/veh (seed 4 selected its last
  iterate). Three seeds better, one worse (seed 2), one unchanged.
- The selection signal is weak: for seed 3, iterates 4 and 5 differ by 0.2 s/veh on the train-day selection windows
  (25.5 vs 25.7) but by 1.9 s/veh on validation (24.5 vs 26.4).
- Confound: "old weights, fixed engine" changes the engine (F1), the queue-feature scale (F3) and actuated's refit
  at once.
- **Methods insight:** for all three learners, *which iterate is deployed* moves the result as much as the
  algorithm; small differences between LSTDQ seeds and iterates are not interpretable individually.

## 7. The three learners: one detector state, three ways to learn

All three share the v2 state (per-phase occupancy, gap, arrival rate, queue estimate, phase timing), the same
training windows (06–10, 11–15, 15:30–19:30, 19:30–23) and train days, and a delay-based training signal. They
differ in what is learned and how. Delay rows: s/veh, lower is better; days won: higher is better.

| | LSTDQ (LSPI) | Q-learning | ARS |
|---|---|---|---|
| What is learned | linear Q(extend), Q(end): 624 weights | the same linear Q | a 312-weight threshold rule: end when θ·x > 0 (no value function) |
| How | least-squares (ridge) solve of the Bellman fixed point per round, on all data so far | online TD (Watkins) with a constant normalised step that never decays | random search: 11 directions × 2 per iteration on the 4-h window delay |
| Training budget of the deployed iterate | 44–110 window-episodes | 22–44 (seed 3 = iterate 1, learnt only from actuated + 20 % random data) | 220–1,100 |
| Training behaviour | stable after round 1 | best at round 1–2 in every seed; weight size grows in later rounds in 4 of 5 seeds (seed 0: 28 → 189) | noisy: 2–6 s/veh between saved iterates, no trend |
| Test delay (actuated 24.9) | **25.3** | 30.6 | 30.4 |
| Test days won vs actuated | **4 of 7** | 2 of 7 | 1 of 7 |
| Night delay, test (actuated 8.2) | 11.6 | **8.1** | 8.5 |
| Heavy-hour delay, validation / test (actuated 31.5 / 29.3) | **31.3 / 31.1** | 48.5 / 41.1 | 62.0 / 42.4 |
| Signature behaviour (test, all seeds) | longer main-street greens than actuated in heavy hours (46–49 vs 36–39 s per service); long light-traffic cycles | left-turn greens close to their 6.0 s minimum in heavy hours (7.1–9.1 s, like MaxPressure's); seed 3 runs an 88 s cycle vs 72–73 s for the other seeds | greens end at max for P5 47 % and P7 35 % of services in heavy hours, P1/P3 0–1 % |

- **Q-learning (same model as LSTDQ, online solver).** Off-policy data, function approximation and bootstrapping
  are shared with LSTDQ, so the "deadly triad" alone does not separate them; the difference is the solver: a
  closed-form least-squares solve per round vs a stochastic update with a step that never decays, whose weights
  mostly keep growing. It is only usable when stopped early, and what is then deployed is a simple near-minimum
  policy: good in light traffic (best night result), worst under heavy load. **Insight:** with the same linear
  model, the solver decides whether the controller is deployable (Lagoudakis & Parr 2003's argument for LSPI,
  reproduced on a real NEMA intersection).
- **ARS (policy search, no Bellman structure).** 10× the simulation budget of LSTDQ and still 5.1 s/veh more delay
  on test (30.4 vs 25.3). θ starts at 0, i.e. "never end" = hold every phase to max; phase blocks that the search
  barely moves keep that default, which fits the P5/P7 max-outs (hypothesis, to test: ‖θ‖ per phase block). With
  312 weights and 11 directions per step, random search is sample-starved, and phases that matter little to window
  delay are never tuned. **Insight:** direct optimisation of the true objective (the appeal of policy search,
  Ault 2020) does not compensate for ignoring the step-by-step structure on a NEMA action space with 4-h episodes.
- **What the comparison gives that one learner could not:** the night result separates training coverage from
  learned bias (§3); Q-learning separates model from solver; ARS separates value-based from direct policy search.
  Among the learners, Q-learning is best at night and in light traffic (ARS close behind), LSTDQ in busy and heavy
  hours.

## 8. What is robust and what is not

Robust (same direction on validation and test, all seeds): every optimising controller has more side-street delay
than free actuated, and LSTDQ and MaxPressure have less side-street delay than the GDOT plan (§1); actuated has the
lowest worst-movement delay; actuated and gap logic are best at night and in surges; Webster's evening collapse;
Q-learning's weight growth and ARS's max-out signature.

Not robust: rankings inside a condition band when controllers are a few s/veh apart (heavy hours: validation
LSTDQ 31.3 vs actuated 31.5, test actuated 29.3 vs LSTDQ 31.1; PM peak: validation MaxPressure best at 23.5 vs
actuated 26.0, test actuated best at 27.8 vs MaxPressure 32.0); individual seed or iterate differences (§6);
"learners drift more" (§5).

Caveats with everything: one site; few heavy hours (Y ≥ 0.6), beyond that only the demand sweep (learners trained
on real demand only); V3 (the model serves left arrows more often than the field); side-street demand corrected
from presence-zone counts (residual bias of unknown sign); the test days were run twice (amendment 1); learners
never trained on 23–06 h; delay is scored at 137 only, so the corridor benefit of coordination is not counted.

## 9. What changed from earlier versions

| earlier claim | status |
|---|---|
| "queue-based state is blind at night, needs gap features" | **wrong**: the state has gap, occupancy and rate; Q-learning and ARS use it and match actuated at night |
| "learners lose more under drift" | **not supported** (§5: in seconds only LSTDQ's gap grows; surge hours and 05-26 explain the test loss) |
| "F3 shortened Webster and caused the collapse" | **wrong**: evening plans unchanged; median design + F2 scoring |
| presence-zone undercount means side penalty understated | **sign unknown** (demand already corrected) |
| "retraining gave a little" | **within seed noise** (§6) |
| short cycles explain heavy-hour losses | **half**: holds on validation, not on test (§2) |
| Q-learning "every green at minimum"; ARS "same linear Q, ~600 weights"; deadly triad separates the learners | **corrected** in §7 |
| "actuated is fairer because it has no objective" | **reframed**: it is the deployed controller's settings without the cycle limits; detector layout is the other likely cause |
| (v2) "equal average delay is a transfer to the side street" | **relative to free actuated only**: against the deployed GDOT plan, LSTDQ cuts side-street delay by 15.8 s at +1.0 s main street (§1) |
| (v2) "LSTDQ also loses at hours 6 and 22, inside its training windows" | **not specific to LSTDQ**: Q-learning and ARS lose more there (§3); the night result alone carries the argument |
| (v2) "81 % of Webster's evening delay is EB through (303 s/veh)" | **misread**: 81 % and 303 s/veh are whole-day figures; in hours 20–23 EB through is 96 % of Webster's delay at 1,116 s/veh (§4) |
| (v2) Q-learning "|w| grows 28 → 189" | **seed 0 only**; growth in 4 of 5 seeds (§7) |
| (v2) 05-26 EB through "vs 557–624 on other days" | **549–624** (§5) |

## 10. Open analyses (ranked)

1. Cheap: day-hour decomposition validation vs test, with and without surge hours; data check of 05-26 13h.
2. Short runs: log the queue estimate vs true halting vehicles per phase (tests the detector-layout cause of §1).
3. Cheap: per-approach HCM LOS table and residual side queue (`backlog_max`) as a phase-failure proxy.
4. Cheap, learner-specific: Q-learning weight size and greedy delay per iterate; ARS ‖θ‖ per phase block and share
   of states with θ·x ≤ 0 for P5/P7; LSTDQ Q(end) − Q(extend) on light-traffic states.
5. Runs: Webster designed to the 85th percentile / peak 15 min.

Fixes to the analysis outputs (no effect on the registered comparison): headers say "attempt 7" (now attempt 8);
the RQ2 mechanism tables in `analysis.md` use training seed 0 and, on test, keep one simulation seed per hour (the
behaviour numbers in this file are recomputed over all seeds from `mech.csv`); the worst-movement metric has no
minimum-volume filter and takes the max over 5 simulation seeds on test vs 1 on validation; the Y bands use the HCM
1,900 veh/h (`evaluate.py` S_LANE; its docstring says 1,950) rather than the measured saturation flow;
`evaluate.py` docstring still describes 7065.

## 11. Demand sweep on the amendment-1 model (post hoc, run 2026-11-18 00:20–04:10, `debug/after_amendment1.sh`)

Same 5 validation days as stage 2 (04-20, 04-24, 04-30, 05-06, 05-12), every 5-min count × k, simulation seed 1.
×1.25 and ×1.5: all 5 seeds per learner; ×1.75–2.5: seed 0 only (marked \*). Learners trained on real demand
(×1) only, so this tests robustness to unseen demand (Chen 2025 / Song 2026 design), not learned control at
saturation. Per-seed table: `eval/scale_summary.md`.

Delay per vehicle (s/veh), lower is better; the 5 days together:

| | ×1 | ×1.25 | ×1.5 | ×1.75 | ×2 | ×2.5 |
|---|---|---|---|---|---|---|
| actuated | 24.5 | **45.0** | **204.5** | **916** | **2,439** | **5,967** |
| LSTDQ | 23.3 | 51.7 | 323.8 | 2,464\* | 3,910\* | 6,688\* |
| MaxPressure | **22.8** | 51.3 | 303.0 | 1,643 | 3,528 | 7,675 |
| Q-learning | 26.7 | 76.9 | 398.2 | 1,680\* | 3,023\* | 6,409\* |
| ARS | 27.3 | 100.4 | 573.4 | 1,308\* | 2,970\* | 7,385\* |
| GDOT plan | 27.4 | 63.1 | 280.6 | 1,155 | 2,709 | 6,276 |
| Webster | 124.4 | 902.6 | 2,167.3 | 3,470 | 4,950 | 8,450 |

Mean cycle length (s), descriptive (no better/worse):

| | ×1 | ×1.25 | ×1.5 | ×1.75 | ×2 | ×2.5 |
|---|---|---|---|---|---|---|
| actuated | 89 | 97 | 110 | 120 | 128 | 133 |
| LSTDQ | 98 | 105 | 118 | 115\* | 121\* | 130\* |
| MaxPressure | 82 | 85 | 92 | 98 | 107 | 120 |
| Q-learning | 75 | 81 | 92 | 98\* | 116\* | 124\* |
| ARS | 77 | 78 | 81 | 94\* | 99\* | 113\* |
| GDOT plan | 114 | 111 | 111 | 111 | 114 | 115 |

\* seed 0 only (cycle at ×1.75–2.5 for learners: seed 0 only).

Hours with a queue reaching the end of the modelled road (out of 120): actuated 39 at ×1.25, 68 at ×1.5, 83 at
×1.75; at ×1.25 the other adaptive methods and the GDOT plan 26–53, Webster 80. From ×1.5 every controller is unstable for much of the day, so delay there
depends on how long the simulation runs and is not a fair ranking (Song 2026). The meaningful range is ×1 to ×1.25.

- **The ranking flips as soon as demand leaves the training range.** At ×1, LSTDQ (23.3) and MaxPressure (22.8)
  have less delay than actuated (24.5) on these days. At ×1.25 (+25 %) every adaptive method has more: actuated
  45.0, MaxPressure 51.3, LSTDQ 51.7, Q-learning 76.9, ARS 100.4 s/veh. Same direction as Sahachaiseree's
  up-scaling test (agents trained on low demand struggled at higher demand).
- **Cycle length vs lost time shows up clearly here.** Actuated lengthens its cycle with demand (89 → 97 → 110 s);
  Q-learning (81 s) and ARS (78 s) stay short at ×1.25 and lose most. LSTDQ does lengthen (105 s) and still loses,
  which points to its side-street transfer relative to free actuated (§1): under higher demand the side queue it
  under-serves grows instead of clearing.
- **Under oversaturation the long fixed cycle moves up the ranking.** At ×1.25 the GDOT plan is fourth (63.1, behind
  actuated, MaxPressure and LSTDQ); from ×1.5 on it is second only to actuated at every level. When every phase is
  maxing out, the best a controller can do is run long cycles that minimise lost time, which actuated (up to
  ~130 s) and the long fixed plan (111–115 s) both do. Adaptivity has little value left when there is no spare time
  to allocate (HCM / Webster: oversaturated signals should maximise capacity).
- Webster has the most delay at every level; it is already gridlocked at ×1.25 (902.6 s/veh).
- **Seed spread explodes outside the training range:** at ×1.5, LSTDQ seeds range 235–625 s/veh, ARS 263–850,
  Q-learning 269–510. A learned controller's behaviour outside its training range is not reliable from one seed,
  which is why ×1.75 and above (seed 0 only) are indicative at best; LSTDQ seed 0 is its worst seed at ×1.5.
- Differs from the stage-2 sweep on the attempt-1 model (MaxPressure best at ×1.5): that model had the engine bug,
  uncorrected side-street demand and the old EB geometry; not comparable.
