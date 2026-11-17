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
