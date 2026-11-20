# Progress

Live status, newest first. Plan and framing: [PLAN.md](PLAN.md). Site details and deviations: [atsc/sites/137/README.md](atsc/sites/137/README.md).

## Now (2026-11-20): v3 tools — ATSPM chart reader, simulated ATSPM metrics, parameter registry, direct measurements

Plan: `atsc/PIPELINE_PLAN.md`. Portal probe: `atsc/probe_2026-11-20/README.md`.
- `tools/atspm_charts.py`: exact Split Failure / Approach Delay / PCD / Wait Time / Ped Delay numbers per window
  (header OCR). Pull for every 137 study weekday running in the background (`debug/pull_atspm_137.sh`, ~19 h).
- `atsc/sim/atspm_sim.py`: the same metrics from the simulation's own events (`run_window(record_events=True)`).
- `atsc/registry.py` -> `atsc/sites/137/REGISTRY.md`: every model setting with status; 43 non-measured rows.
- `atsc/measure.py` -> `atsc/sites/137/measured.json`: settings read directly from the 72 cached T&A windows.

**Findings (exploration on train day 2026-03-10 07-09 and the cached train-day windows; model unchanged):**
1. **Passage times measured directly are ~2 s (left arrows) and ~3.4 s (side throughs), not the fitted 6-8 s.**
   The train-day fit to gap-out share pushed passage up to compensate for something else (plan weakness W2/W3).
2. **P1 clearance measured: yellow 3.2 s, red 2.3 s** (model assumes P5's 2.9 / 2.9). Other phases' clearances
   re-measured on Mar-Apr windows match the model within 0.2 s (P2/P6 display reading unreliable, not used).
3. **Closed-loop count check (sim stop-bar activations vs GDOT's raw presence counts, 07-09):** SB_L 58 vs 252,
   SB_T 116 vs 197, NB_T 57 vs 84, NB_L 75 vs 53, EB_L 195 vs 175. The simulated E. Andrews left zone sits under
   a standing queue (few long activations): the corrected SB_L demand (x1.73 -> 435 veh vs 252 raw) and/or
   permissive clearing is wrong. Same picture in the ATSPM-style metrics: P7 split failures 17 sim vs 8 field,
   max wait ~1,000 s vs 96 s; field skips P7 in 32 % of cycles, the sim serves it almost every cycle.
4. Main street matches well: arrivals on green 66/60 % sim vs 66/64 % field; approach delay 9.6/10.3 s vs 8/9 s.

Next: calibrate the undercount factors so simulated activations match GDOT's raw counts per movement (closed
loop, train days), adopt measured passage and P1 clearance, then calibrate discharge — in that order.

## Now (2026-11-17 16:30 JST): FINAL TEST done (locked days 05-18..29, run once, TEST_PLAN.md)

7 test days x 19 controllers x 5 simulation seeds = 665 runs, 0 failed, 0 teleports. `atsc/sites/137/eval_test/`.
Delay (s/veh): actuated 25.2, MaxPressure 26.1, LSTDQ 30.6, ARS 30.8, GDOT plan 31.3, Q-learning 35.3, Webster 94.0.
Pre-registered verdicts vs actuated (log-ratio t-test, Holm; TOST 5 %/2 s): all inconclusive except Webster worse
(ratio 3.17, p_Holm 0.019). Ratios: MaxPressure 1.025, LSTDQ 1.198 (p_Holm 0.057), Q-learning 1.328, ARS 1.196,
GDOT plan 1.227 (0.053). Learners generalise worse than on validation (LSTDQ 1.02 -> 1.20; seed 1 41.4 s/veh);
actuated is the most robust. 05-22 ran on 05-20's schedule (registered fallback rule; disclosed).
Results section appended to TEST_PLAN.md.

## Now (2026-11-17 12:10 JST): every method on the validated attempt-7 model

Attempt 7 = attempt 6 + floating force-off for P1/P5 (GDOT's Split Monitor: the lead lefts never exceed their split on
train days; `force_off_mode.py`). V1 34/35, V2 29/35, V5 pass -> accepted; V3 skips 19/35 (reported: arrows served
more often than in the field). `atsc/sites/137/VALIDATION.md`.
Methods: gdot + actuated rerun on attempt 7; LSTDQ v2 and Q-learning RETRAINED on attempt 7 (5 seeds each; both use
the actuated controller as behaviour policy, `debug/attempt7_retrain.sh`, done 12:08) and re-evaluated; ARS,
MaxPressure, Webster runs from attempt 6 stand (they use neither changed setting). 380 runs, 0 teleports.
`eval/analysis.md`, `eval/report.md`; attempt-6 evaluation and learner weights archived in `archive_attempt6_model_2026-11-17/`.
Delay (s/veh, seeds pooled): actuated 25.8, MaxPressure 26.7, LSTDQ 26.7 (before retrain 27.5), GDOT plan 34.1, ARS 35.5,
Q-learning 37.6 (before 37.3), Webster 60.9. Seed medians: LSTDQ 26.2 (25.0-30.2), Q-learning 37.8 (36.3-38.3).
vs actuated: MaxPressure median -2.06, 17/20 days, Wilcoxon p 0.076; LSTDQ median -0.26, 12/20, p 0.73; Q-learning,
ARS inconclusive; GDOT plan, Webster worse (0/20 days).
Apr 28 surge: actuated 45.3, LSTDQ 52.3, MaxPressure 87.3, GDOT plan 152, Q-learning 160, ARS 166 s/veh.
Without Apr 28 (post hoc): MaxPressure 23.3, actuated 24.7, LSTDQ 25.3, GDOT plan 27.5, ARS 28.2, Q-learning 30.7.

Simulation-seed check (validation days, seeds 1-4, actuated / MaxPressure / LSTDQ s0; `debug/simseed_summary.py`):
within-day seed SD ~0.2-0.3 s/veh (max 1.9 / 8.1 / 2.9 on a surge day) vs between-day SD 4.4-12.5; log-ratio seed SD
0.015 vs between-day 0.04-0.18; overall ratios to actuated 0.973 -> 0.983 (MaxPressure), 0.969 -> 0.974 (LSTDQ s0).
Seed noise is small next to day-to-day variation; the seed-1 validation conclusions stand.
Final test: plan registered in `atsc/sites/137/TEST_PLAN.md` (commit 908f6298); NOT run yet: reading the locked
test days needs the user's explicit unlock (the timing fetch was blocked).

## Earlier (2026-11-16 20:10 JST): methods rerun on the attempt-6 model (superseded by attempt 7)

Model: attempt 6 (estimated presence-zone demand, measured pedestrians, train-fitted passage, impatience 0.5, signal 138
upstream under its field timing). Validation NOT accepted (V1 splits 26/35, V2 left-turn gap-outs 23/35, V5 pass):
every result below is preliminary. 5 training seeds x 20 validation days x 1 simulation seed, 380 runs, 0 teleports.
Full tables: `atsc/sites/137/eval/analysis.md` (RQ1-RQ3 + tests), `eval/report.md`. Attempt-5 results archived in
`atsc/sites/137/archive_attempt5_model_2026-11-16/eval/`.

Vehicle-weighted delay (s/veh), seeds pooled: actuated 25.9, MaxPressure 26.7, LSTDQ 27.5, GDOT plan 34.6, ARS 35.5,
Q-learning 37.3, Webster 60.9 (attempt 5: 25.2 / 26.7 / 27.5 / 34.3 / 32.2 / 36.1 / 59.8; same ranking).
vs actuated (paired by day): MaxPressure mean +0.58, median -2.43, 17/20 days won, Wilcoxon p 0.064 (attempt 5: 0.040),
TOST inconclusive; LSTDQ, Q-learning, ARS inconclusive; GDOT plan and Webster worse (0/20 days).
Apr 28 surge (X_c 1.26): actuated 41.2, LSTDQ 56.8, MaxPressure 87.3, Q-learning 160, ARS 166 s/veh.
Without Apr 28 (post hoc, alongside only): MaxPressure 23.3, actuated 25.1, LSTDQ 25.9, ARS 28.2, Q-learning 30.4.
RQ1: actuated best in light (Y<0.3), moderate and heavy (Y>=0.6) hours and at night/AM/midday; MaxPressure best in
busy hours (0.45-0.6: 22.1 vs 24.9) and in the PM peak and evening. RQ2: MaxPressure shorter cycles near capacity
(71-76 s vs actuated 87-100 s, minor phases ~6-12 s, never max-out) but 93 s cycles holding the main street at light
load; LSTDQ 102-112 s cycles. RQ3: worst-movement p95 MaxPressure 103-190 s vs actuated 46-106 s; seed spread LSTDQ
5.7, Q-learning 3.8, ARS 15.7 s/veh.

## Earlier (2026-11-16 ~04:00 JST, attempt-1 model, superseded)

| Run | State | Output |
|---|---|---|
| 137 stage 1B: preliminary methods comparison (1 training seed, 5 pre-chosen validation days) | **done 04:32** (summary below) | `atsc/sites/137/eval/report_preliminary.md` |
| 137 stage 1C: full (5 training seeds, 20 validation days) | **done 06:48** (summary below) | `atsc/sites/137/eval/report.md` |
| 137 stage 2: demand-scale sweep x1.25-2.5 | **done 06:05** (summary below) | `atsc/sites/137/eval/scale_summary.md` |
| 137 GDOT-timing validation (Split Monitor statistics, as 7065's VALIDATION.md) | **failed, 2 registered attempts** | `atsc/sites/137/VALIDATION.md` |

Log: `atsc/sites/137/debug/stage1.log`, `stage2.log`. The first attempt (before the two fixes below) is archived unread in
`atsc/sites/137/archive_before_eb_fix_2026-11-16/`.

Preliminary result (seed 0, 5 days, 1 simulation seed, Y up to ~0.7; not yet tested formally): overall vehicle-weighted
delay actuated 17.0, Q-learning 17.1, LSTDQ 17.5, MaxPressure 17.8, ARS 18.3, GDOT plan 20.9, Webster 67.2 s/veh
(Webster: one Friday evening oversaturated its fixed 60-63 s plans, 580-1,780 s/veh in 20:00-23:00; 23-25 s/veh on
the other days). Every adaptive controller is within 2 s/veh of actuated on every one of the 5 days (H1 direction).
In light traffic MaxPressure is the worst adaptive controller (17.4 vs 11.6 s/veh for actuated).

Full run (5 training seeds, 20 validation days, 1 simulation seed, 380 runs, 0 teleports). Vehicle-weighted delay,
median over seeds (range): actuated 17.1, LSTDQ 17.4 (16.8-20.8), ARS 18.6 (17.2-24.1), MaxPressure 19.0,
GDOT plan 20.9, Q-learning 21.1 (19.8-148.9; seed 3 degenerate on every day), Webster 48.5 s/veh.
One day drives most of the differences: **Apr 28 09:00-11:00**, westbound arrivals from 138 jump from ~35 to ~95 per
5 min at exactly 09:00 (Y 0.84, the only real hour at capacity). Actuated, LSTDQ and GDOT's plan absorb it;
MaxPressure (+23 s/veh that day), Q-learning and ARS (+4 to +118) build a WB queue. Unverified whether the surge is
real traffic or a 138 detector event (no source outside ATSPM). Without Apr 28 (post hoc, reported alongside, never
instead): 4 of 5 seeds of every learner and MaxPressure are within the H1 margin of actuated on every day.
`atsc/sites/137/eval/report.md`.

Demand sweep (same 5 days and controllers, learners trained at x1 only; peak-hour X_c = Y C/(C-L), s = 1,900):
x1 (X_c 0.87) and x1.25 (1.09): adaptive controllers within ~1 s/veh of each other. x1.5 (1.31): they separate,
MaxPressure 40.1 vs actuated 48.0 and learners 47.3-58.5 s/veh. x1.75 and above: every controller oversaturated
(queues at the leg end in more than half the hours), delay comparisons not meaningful (Song). `eval/scale_summary.md`.

Fixed 04:00, both found before any result was read:
1. EB approach: two lanes the whole way, left-only from ~65 m (user check); OSM had one lane upstream of the last 40 m.
2. P2 stop-bar zone was dropped from the queue estimator (its note contained "right"), so MaxPressure and the v2
   learners saw no EB queue (MaxPressure 707-846 s/veh on Mar 4 PM, 22.4 after the fix).

## Methods compared (one version each, same engine, detectors, demand; learners share the v2 state and reward)

| Method | Pair / factor | Precedent |
|---|---|---|
| Webster | pretimed floor | every paper |
| GDOT field plan | coordination constraints | Sahachaiseree |
| Actuated gap-out | the real practice baseline | Ault 2020, El-Tantawy |
| MaxPressure | learning vs rule, same information | Schreiber, LibSignal, Song |
| LSTDQ | main learner | Sahachaiseree |
| Linear Q-learning | batch vs online, same model | Lagoudakis & Parr; El-Tantawy |
| ARS | value-based vs policy search | Ault 2020 (CMA-ES) |
| DQN | linear vs neural | Schreiber, Ault 2020, RESCO — **held until after the midterm** |

Dropped: LSTDQ v1/v2f (variants of one method), NFQ (time), PPO (Ault 2020, RESCO: unstable), SARSA/traces (El-Tantawy: null).

## Done

- **2026-11-16** 137 built on the atsc pipeline. Study period moved to Mar–May (all ten movements counted there).
  WB through taken from upstream signal 138 (137's zone 1.4–2.8× too high). Lanes partly user-checked. Per-day plans
  for all 56 train/validation days. Audit: 49 usable days, no bin above the physical bound. Engine fix: plans that
  omit a phase.
- **2026-11-16** 7088 screened and rejected (Peachtree through and NB not counted).
- **2026-11-15** Research questions reframed around when/why adaptive control pays off, with mechanism counterfactuals (PLAN.md §1).
- **2026-11-13** 7065 dropped as primary site (validation not passed, coordinated, main-street counts rebuilt); its
  stage-3 results kept as first-site record.

## Decisions (2026-11-16, user)

- H1 equivalence margin: **within 5 % of delay or 2 s/veh, paired by day** (fixed before any result was read).
- 137 test set **locked: 2026-05-18..05-29**. (The count script printed per-day WB totals for those days once — demand only; it no longer does.)
- Lanes: W Paces Ferry left + through/right each way, EB left lane continuous, left-only from ~65 m; E Andrews and Slaton R/T/L.
- Methods: LSTDQ, Q-learning, ARS + four rule controllers now; DQN after the midterm; NFQ dropped.

## Open

- **Full run on the attempt-5 model done 14:00** (`atsc/sites/137/eval/analysis.md`, 380 runs, 0 teleports): MaxPressure
  beats actuated on 17/20 days (median −2.65 s/veh, Wilcoxon p = 0.04) but collapses on the Apr 28 surge morning
  (+63.6 s/veh that day: its queue estimate loses the WB queue once it backs past the 79 m advance zone; actuated
  extends WB to max green and clears it), so the mean difference is not significant (+1.2). Learners: inconclusive
  vs actuated, seed spread up to 6 s/veh, all collapse on Apr 28. Ranking flips with saturation and time of day:
  actuated at night/light traffic, MaxPressure in busy hours. TOST equivalence not shown for any method.
- **Attempt 5 (calibrated permissive left turns, impatience 0.5): V1 27/35 (one short), V2 20/35: not accepted.**
  Driver settings cannot create the gaps that 138's platoons give in the field; attempt 6 = model 138 upstream.
  Methods evaluation rerunning on the attempt-5 model since 11:41 (old results archived).
- **Attempt 4 (estimated side-street demand): V1 split PASSES (29/35, worst 4.5 s); V2 gap-outs still fails (19/35)**,
  almost entirely on the left-turn phases (permissive left-turn behaviour). Site configuration = attempt 4.
- Attempts 1–3 failed V1 (split) and V2 (gap-outs); V5 (health) passes. Attempt 3
  (measured pedestrians, train-fitted 8 s passage) is the best so far: V1 20/35, worst 5.9 s; V2 18/35 (pass needs 28/35).
  The site configuration is now attempt 3; **`eval/` results are from the attempt-1 model** and need a rerun.
  Main-street lefts behave as if GDOT delays their calls (unpublished); side-street throughs clear faster than the field
  (driver model uncalibrated). Next principled step: discharge calibration, then a third attempt. **(decide)**
- **Demand sweep scope**: learners trained at x1 only, so the sweep tests robustness to unseen demand, not learned
  control at saturation. H2 proper needs training at the scaled level (after the midterm).

- **137 side-street counts undercount (found 09:30)**: NB/SB all movements and EB left are counted by stop-bar
  presence zones (report = zone activations; a discharging queue counts as one vehicle), as at 7065's Peachtree.
  Side-street demand in every 137 result is a lower bound in busy periods; explains the side-street validation
  misfit. Correction would be a model-based estimate **(decide)**. `atsc/sites/137/VALIDATION.md`.

## Known limits (state with every result)

Uncalibrated, simulation not validated (VALIDATION.md); not isolated (138 at ~260 m, random arrivals); EB/WB rights as through; P2/P6
stop-bar presence added; no pedestrian timing; 1 simulation seed; real days peak at Y ≈ 0.5 (H1 region only).
