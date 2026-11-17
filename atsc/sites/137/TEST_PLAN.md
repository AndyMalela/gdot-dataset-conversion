# 137 final evaluation on the locked test days — analysis plan

Registered 2026-11-17, before any test-day value was read (user: "yes do it all", after the pipeline was laid out).
Committed to git before the test-day charts and counts are read, so the commit time is the registration time.
Nothing here is changed after the test results are seen; anything added afterwards is labelled post hoc.

## 1. What is frozen

| Part | Frozen state |
|---|---|
| World model | Attempt 7 (VALIDATION.md, accepted): network, `sim.json` (impatience 0.5, train-fitted passage), `signal.json` plans and phase settings incl. floating force-off P1/P5, 138 upstream under its field timing (`neighbours.json`) |
| Demand | `intersections/137/counts/tmc_137_5min_estimated.csv` as built (presence factors from train days only; WB through from 138) |
| Controllers (7 methods, 19 controllers) | gdot (plan mode), actuated (free), webster (own plans, train-day design), maxpressure, LSTDQ v2 seeds 0–4 and Q-learning seeds 0–4 (trained on attempt 7, 2026-11-17), ARS seeds 0–4 (trained on attempt 6; its environment is unchanged by attempt 7: free mode, no behaviour policy) |
| Code | this commit; `analyze.py` comparison section as in §5 |

No learner is retrained, no parameter retuned, and no controller is added or dropped after this point.

## 2. Test days

- Locked window 2026-05-18 .. 05-29 (`split.json`), weekdays only.
- **2026-05-25 (Memorial Day, US federal holiday) excluded**: not a typical weekday. Train and validation contain no
  federal holiday, so the rule is the same one every other set already follows. Added to `split.json` `holidays`.
- 2026-05-21 and 05-27 are absent from GDOT's 137 report: not filled, not substituted.
- Day quality as for every other set (`demand.day_quality`: complete or usable); hours with an outage bin are
  left out (`evaluate.py conditions`).
- Expected: up to 7 days (05-18, 19, 20, 22, 26, 28, 29). The number actually used is reported.

## 3. Test-day signal timing

The field program changed inside the validation period (plans E/F/G on some days, A–D on others); dated and
canonical schedules agree on only 62.9 % of validation-day minutes. So the test days' time-of-day schedules are
read from GDOT's Split Monitor exactly as for every other day (`test_schedule.py`, rules in its docstring):
plans matched to frozen plans by cycle + splits; an unmatched verified plan is added for plan mode only (phase
settings unchanged); the validated timing sources are restored byte-identical. Only plan bands and programmed
splits are read — no split statistics or other performance data of the test days.

## 4. Runs

- Every controller on every test day, **simulation seeds 1–5** (fixed now; the simulation-seed check on the
  validation days, `debug/simseed_check.sh`, is reported for interpretation and does not change this).
- Full day 00:00–24:00, as in the validation evaluation. Output: `eval_test/` (`ATSC_SET=test
  ATSC_EVAL_DIR=eval_test ATSC_FINAL_TEST=1`, `debug/final_test.sh`).
- A run with teleports or a failed run is reported, never silently dropped or rerun with another seed.

## 5. Analysis (`analyze.py` with `ATSC_SET=test ATSC_EVAL_DIR=eval_test`)

Measure: daily vehicle-weighted delay (s/veh) over the clean hours. Learners: mean over their 5 training seeds and
5 simulation seeds per hour; other controllers: mean over the 5 simulation seeds. Unit of analysis: the day.

Six comparisons, each method against actuated (the strongest rule-based controller on the validation days):

| Role | Test | Verdict |
|---|---|---|
| Equivalence (H1, margin fixed by the user 2026-11-16) | paired TOST, margin per day max(2 s/veh, 5 % of actuated), t distribution, α = 0.05 | "equivalent" if p_TOST < 0.05 |
| Primary difference | paired t-test on the daily log ratio ln(delay / actuated), two-sided, Holm-adjusted over the six | otherwise "better" / "worse" if p_Holm < 0.05 (direction = sign of the mean log ratio), else "inconclusive" |
| Effect size | geometric-mean ratio with 95 % t interval | — |
| Secondary (no verdict) | mean and median difference (s/veh), days won, Wilcoxon signed-rank | — |

Why the log ratio: on the validation days one surge day (Apr 28) dominated mean differences in s/veh while the
median pointed the other way; the ratio scale weights every day by its relative change. With 7 days the Wilcoxon
test cannot go below p = 0.016 two-sided, so after a correction for six comparisons it has almost no power: reported only.
The TOST normal approximation used before 2026-11-17 is replaced by the t distribution (anti-conservative at n = 7);
the validation analysis was regenerated with the same code so both sets use one method.

Descriptive, no tests: RQ1 tables (saturation, time of day, variability), RQ2 mechanism, RQ3 seed spread and
worst-served movement, per-training-seed ratios and days won, simulation-seed spread.

## 6. Reporting

- Every number above is reported whatever it shows; the validation-day results stay as the development evidence.
- The test is run once. If a bug is found afterwards, the fix is documented and both results are reported.
- Known limitations carried with every result: V3 skips 19/35 (the model serves arrows more often than the field;
  permissive-left share 0.73–0.75 vs 0.85–0.88); ARS trained on attempt 6 (environment unchanged); one site.

## Results (run once, 2026-11-17 14:04–16:29 JST; `eval_test/analysis.md`, `eval_test/report.md`)

Test days used: 7 (05-18, 19, 20, 22, 26, 28, 29), 168 clean hours; 665 runs (19 controllers × 7 days × 5 simulation
seeds), 0 failed, 0 teleports. Timing: `test_schedule.py` matched every band to a frozen plan except one 1-h plan
(K, 05-22, added as T1); **05-22 fell back to 05-20's schedule** under the registered rule (two short "transition"
bands count as a failed read, as in `make_signal.py`), although the field ran A–D that day: GDOT plan and 138's
timing on 05-22 use the E/G program. The same rule already gave 05-14 and 05-15 (validation) the 05-13 schedule.

Overall vehicle-weighted delay (s/veh): actuated 25.2, MaxPressure 26.1, ARS 30.8, LSTDQ 30.6, GDOT plan 31.3,
Q-learning 35.3, Webster 94.0.

| method | ratio to actuated (95 % CI) | p Holm | p TOST | days won | verdict |
|---|---|---|---|---|---|
| MaxPressure | 1.025 (0.912–1.151) | 0.626 | 0.212 | 4/7 | inconclusive |
| LSTDQ | 1.198 (1.052–1.363) | 0.057 | 0.949 | 1/7 | inconclusive |
| Q-learning | 1.328 (0.997–1.768) | 0.103 | 0.939 | 1/7 | inconclusive |
| ARS | 1.196 (1.019–1.403) | 0.101 | 0.926 | 1/7 | inconclusive |
| GDOT plan | 1.227 (1.070–1.406) | 0.053 | 0.965 | 0/7 | inconclusive |
| Webster | 3.167 (1.748–5.738) | 0.019 | 0.993 | 0/7 | worse |

No method is shown equivalent to or better than actuated; only Webster is significantly worse after Holm. Webster's
94 s/veh comes from its train-day evening plan (20:00–22:00): EB through backs up to ~550 vehicles on 05-19
(hour 22 mean 1,361 s), so late-May evening demand exceeds what that fixed plan serves; the residual queue also
drives its "light" and "very variable" hour figures.

Post hoc (labelled, not part of the registered analysis), without 05-22: same directions; ratios MaxPressure 1.038,
LSTDQ 1.210, Q-learning 1.366, ARS 1.209, GDOT plan 1.251, Webster 2.905; no Holm p < 0.05 (6 days).

## Amendment 1 — post-test bug-fix pass (registered 2026-11-17 ~17:30, before any of it is run)

Trigger: an independent review after the test (user: "this result isn't acceptable for a research I feel like";
review asked to find errors, not better numbers). Fixes are justified by NEMA controller rules, a scoring error, and
site measurements on train days — not by the test results. The original test results above stay the registered
result; everything below is reported next to them, labelled **post-test bug fix (amendment 1)**. The test days have
now been seen once, so the second test run is not a clean held-out test; no change is made after it.

Fixes:

- **F1 engine (`atsc/sim/nema.py`), every controller.** Found: with no call on the side street, the engine still
  crossed the barrier and started each ring's first side phase (P3/P7) uncalled, every cycle (≈18 s of needless
  main-street red per cycle at night; likely part of the V3 skip mismatch). NEMA rules implemented instead:
  (a) the barrier is crossed only when a phase of the other group is called (otherwise the resting phases stay
  green); (b) the last phase of a group is not maxed out (free mode) or forced off (plan mode) without a call in the
  other group — in plan mode a coordinated phase then dwells and yields at its next fixed force-off point (one
  yield point per cycle, coordination kept); (c) dual entry: a ring with no call in the entered group serves its
  through phase (P2/P6/P4/P8) while the other ring serves its call — ASSUMPTION (GDOT's dual-entry setting is not
  visible on the portal; standard practice). Fixed-time (Webster, skip_uncalled off) is unchanged.
- **F2 scoring (`atsc/sim/episode.py`).** Vehicles that never enter the network were not scored (only Webster,
  1 validation and 5 test runs). `--tripinfo-output.write-undeparted true`: they are scored with their waiting time.
- **F3 saturation flow, 137.** The queue estimate used by MaxPressure and LSTDQ v2 assumed 1,950 veh/h/lane
  (7065's calibration) and Webster was designed at 1,900 (HCM base, mislabelled "calibrated"). Both use 137's
  simulated saturation discharge instead, measured per phase on train days (`sat_flow.py`: stop-line departure
  headways of queued vehicles from the 5th onward during the phase's own protected green, GDOT plan, train weekdays
  15:30–19:30), stored in `sim.json`. 7065 keeps its value.
- **F4 learner iterate (every learner).** Q-learning's weights diverged (|w| 27 → 182, training delay rising) and
  the final-iterate rule kept the diverged policy. For LSTDQ v2, Q-learning and ARS alike, the evaluated iterate is
  the saved iterate with the lowest greedy, vehicle-weighted delay on fixed train-day selection windows
  (`select_iterate.py`); train days only, chosen before any evaluation.

Order: (1) validation attempt 8 = attempt 7 + F1–F3, controller refit on train days as before, same criteria
(V1 + V2 + V5); reported whatever the outcome; (2) Webster redesigned (F3); (3) LSTDQ v2, Q-learning, ARS
retrained, 5 seeds each, on the attempt-8 model; (4) iterate selection (F4); (5) every controller evaluated on the
validation days (simulation seed 1) and the test days (seeds 1–5) with the registered analysis (§5) unchanged.
If attempt 8 is not accepted, its methods results are still reported, labelled "model not accepted".
Not changed (reviewed, judged not to reorder results or to be method design): delay at 138 counted in 137's score;
learner training windows without 23–06 h; Q-learning's step size; demand.
