# 7111 corridor (7112 – 7111 – 7110): day split and locked test set

**Written 2026-11-27, before any model, Split Monitor, outcome or Timing & Actuation analysis of the study
period.** Pass criteria for the simulation will be added here before the first validation run, without changing
the split.

## Days (`split.json`)

Study period: weekdays 2026-08-31 to 2026-11-20 (the data pulled on 2026-11-22). Chronological split:

| Set | Days | Use |
|---|---|---|
| Train | 2026-08-31 .. 10-09 (29 weekdays after holidays) | demand and turning-split estimation, controller-setting fits, RL training |
| Validation | 2026-10-13 .. 11-06 (19 weekdays) | simulation validation, all evaluation before the final test |
| **Test (locked)** | **2026-11-09 .. 11-20 (9 weekdays)** | final evaluation only — never read before the final run |

- **Holidays.** US federal holidays are excluded from every set, the same rule as 137: 09-07 Labor Day, 10-12
  Columbus Day, 11-11 Veterans Day.
- **Usable day.** A day is used in an analysis only if every signal that analysis needs has count status `ok`, or
  `partial` with ≤ 10 % outage bins (`intersections/<id>/counts/daily_summary.csv`).
  - Completeness of all days was read for this rule. Test days: all `ok` at all three signals.
- **Files on disk contain test-day rows.** The pull covered every day: the turning-movement counts, plans and
  Split Monitor statistics of 7111, 7110 and 7112 all include them. Every script must drop the test days via
  `split.json` before reading values.

## Exposure before the split (disclosed)

Site screening (2026-11-22, `intersections/7111/SCREENING.md`), before any model existed, read the following for
2026-11-02 .. 11-13:
- daily turning-movement totals at 7111, 7110 and 7112;
- Approach Volume daily totals at 7111 and 7110;
- one 5-minute Timing & Actuation window at 7111 (2026-11-11 17:00, now a holiday and outside every set).

So daily count totals of test days 11-09, 11-10, 11-12 and 11-13 were seen. They were used only to compare count
quality between candidate sites. No Split Monitor statistic, outcome report or simulation of any test day has
been read.

On 2026-11-27, count-only flow-balance checks used train and validation days (Sep 1 – Nov 6). Counts are model
inputs on those days, not validation targets.
