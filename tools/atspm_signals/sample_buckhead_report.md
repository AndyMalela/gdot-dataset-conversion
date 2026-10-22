# Stratified sample — buckhead

Seed `20261004` · 1 per cell · source `screening_buckhead.csv`

## Eligibility

- Screened: 24
- Eligible: 21
- Excluded, no data returned: 2
- Excluded, fewer than 3 approaches detected: 1
- Rejected after selection (replaced): 0

Peak-hour volume tertile cuts: low < 1965 ≤ med < 4102 ≤ high (veh/h)

## Cells (frame → selected)

| complexity \ volume | low | med | high |
|---|---|---|---|
| simple | 1 → 1 | 0 → 0 | 0 → 0 |
| standard | 2 → 1 | 0 → 0 | 0 → 0 |
| complex | 4 → 1 | 7 → 1 | 7 → 1 |

**Short cells** (fewer than 1 available): med/simple, high/simple, med/standard, high/standard. Screen more signals, merge with a neighbouring cell, or move the cut points.

## Balance (medians): frame vs sample

| variable | frame | sample |
|---|---|---|
| peak_hour_volume | 2.96e+03 | 800 |
| hourly_volume | 2.35e+03 | 655 |
| left_share | 0.087 | 0.208 |
| major_share | 0.834 | 0.727 |
| n_approaches | 4 | 4 |
| n_movements | 8 | 5 |
| daytime_valid_pct | 100 | 100 |

## Selected sites

| cell | rank | signal | name | weight |
|---|---|---|---|---|
| high/complex | 1 | 7069 | SR 141 @ Bolling Way | 7.0 |
| low/complex | 1 | 7071 | SR 237 @ Tower Place Drive | 4.0 |
| low/simple | 1 | 136 | E. Paces Ferry Rd @ Grandview Ave | 1.0 |
| low/standard | 1 | 7075 | SR 237 @ Piedmont Center | 2.0 |
| med/complex | 1 | 7065 | SR 141 @ SR 237 | 7.0 |

Weight = eligible signals in the cell / selected in the cell. Use it to turn per-cell results into city-wide estimates.
To replace a site: add `signal_id,reason` to `rejections_buckhead.csv` and re-run.
