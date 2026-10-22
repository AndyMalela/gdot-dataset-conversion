# Signal 7065 timing plans — from ATSPM Split Monitor (May 6–8, 2026)

> Hand-checked reference. The script `tools-timing/atspm_plans.py` now produces the same
> plans automatically (`timing_plan_7065.md`, letters A–E = plans 12, 32, 39, 34, 17/37
> below) and was validated against this file. This file keeps what the script can't read:
> the controller's plan numbers.

Source: GDOT ATSPM **Split Monitor** (MetricTypeID 2, `GetSplitMonitorMetric`), one
full-day request per date. The chart labels each plan band with its plan number and
draws the controller's **programmed split** per phase (orange line). Charts:
`split_monitor/<date>/Phase_<n>.jpg` (re-pulled with the y axis pinned at 0–200 s).

## Schedule (identical on 05-06, 05-07, 05-08)

| Time | Plan | Cycle (s) |
|---|---|---|
| ~00:00 – 06:15 | 17 (or 37, see note) | 120 |
| 06:15 – 13:30 | 12 | 160 |
| 13:30 – 15:30 | 32 | 160 |
| 15:30 – 19:00 | 39 | 180 |
| 19:00 – 19:30 | 32 | 160 |
| 19:30 – 21:45 | 34 | 130 |
| 21:45 – ~00:00 | 37 | 120 |

## Programmed splits (s, green + yellow + red clearance)

Ring 1 = P1 P2 | P3 P4, ring 2 = P5 P6 | P7 P8. Coordinated phases P2/P6.

| Plan | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 | Ring 1 Σ | Ring 2 Σ |
|---|---|---|---|---|---|---|---|---|---|---|
| 17 / 37 | 20 | 50 | – | 50 | 20 | 50 | – | 50 | 120 | 120 |
| 12 | 35 | 50 | 25 | 50 | 33 | 52 | 15 | 60 | 160 | 160 |
| 32 | 33 | 60 | 24 | 43 | 37 | 56 | 15 | 52 | 160 | 160 |
| 39 | 25 | 85 | 27 | 43 | 43 | 67 | 15 | 55 | 180 | 180 |
| 34 | 25 | 45 | 15 | 45 | 30 | 40 | 16 | 44 | 130 | 130 |

`–` = phase not served in that plan (100 % skips; P3/P7 omitted overnight).

## How the values were read, and how sure they are

- Read from chart pixels: the modal row of the orange programmed-split line or of the
  force-off dots (in coordinated plans non-coordinated phases are forced off exactly at
  their split), within each plan band, on all 3 days, cross-checked by eye. Vertical
  resolution 0.1–0.45 s/px depending on the chart's axis; raw reads were within ±0.7 s
  of the integers above (e.g. P2 plan 39 read 85.7, P6 plan 34 read 38.7–40.0).
- Integers were chosen so that **every plan closes exactly**: both rings sum to the
  same cycle, and both barrier groups match (P1+P2 = P5+P6, P3+P4 = P7+P8). Every
  plan passes both checks with these integers.
- Independent check: cycle lengths match the Timing & Actuation green-to-green
  estimates in `tod_7065.csv` (119.7 / 159.8 / 159.8 / 179.9 / 129.9 / 119.7 s at
  03:00 / 07:00 / 14:00 / 17:00 / 20:30 / 23:00 on 05-08).
- The 19:00–19:30 band's label is truncated on full-day charts; the zoomed pull reads
  "Plan 32" with the same splits (P2 60.0).

## What this does *not* give

- **Offsets** (not shown on Split Monitor). Irrelevant for a single-intersection twin.
- **Min green, max green, passage time, ped timing** — Timing & Actuation windows or
  the controller database would be needed. Yellow / red clearance are in
  `tod_7065.csv` (5-min window at 14:00).
- **Night plan number is not consistent**: 05-08 runs 37 until ~00:10 then 17;
  05-07 shows 17 from 00:00; 05-06 shows 37 all night. 17 and 37 have identical splits.
- **Missing phase data, left unfilled**: 05-06 00:00–04:15 has no cycles (same window
  as the TMC sensor outage). 05-07 00:00–05:00 also has no cycles on Split Monitor,
  although the TMC export has 4,016 vehicles counted in that window — unexplained;
  phase events missing while detector counts were logged.
