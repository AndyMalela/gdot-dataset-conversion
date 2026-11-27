# Critical flow ratio Y: 137 vs 7111 (train days only)

Written by `atsc/sites/y_compare.py` (2026-11-27). Y = sum of the critical phases' flow ratios v/s
(Webster; HCM). s = 1,900 veh/h/lane, the HCM base saturation flow with no adjustments (standard constant,
flagged). Simplifications, the same at both sites: protected-permissive lefts counted as fully protected,
right turns on red not deducted, shared through-right lanes as counted. Y near 1 = the intersection cannot
serve its demand even with no lost time; with lost time L per cycle the practical limit is about 1 - L/C.

## 137 — as reported (WB through from 138)

Train days used: 31 (2026-03-02 .. 2026-04-17); counts `intersections/137/counts/tmc_137_5min_upstream.csv`.

| hour | Y | critical phases | entering veh/h (counted movements) | days |
|---|---|---|---|---|
| 00 | 0.07 | P1-P2-P7-P8 | 269 | 31 |
| 01 | 0.05 | P1-P2-P7-P8 | 159 | 31 |
| 02 | 0.03 | P1-P2-P7-P8 | 119 | 31 |
| 03 | 0.03 | P1-P2-P7-P8 | 115 | 31 |
| 04 | 0.04 | P1-P2-P7-P8 | 133 | 31 |
| 05 | 0.10 | P1-P2-P7-P8 | 312 | 31 |
| 06 | 0.23 | P1-P2-P3-P4 | 754 | 31 |
| 07 | 0.41 | P1-P2-P3-P4 | 1,421 | 31 |
| 08 | 0.47 | P1-P2-P7-P8 | 1,674 | 30 |
| 09 | 0.45 | P1-P2-P7-P8 | 1,550 | 30 |
| 10 | 0.42 | P1-P2-P7-P8 | 1,445 | 30 |
| 11 | 0.40 | P1-P2-P7-P8 | 1,413 | 31 |
| 12 | 0.41 | P1-P2-P7-P8 | 1,402 | 31 |
| 13 | 0.41 | P1-P2-P7-P8 | 1,446 | 30 |
| 14 | 0.43 | P1-P2-P7-P8 | 1,482 | 30 |
| 15 | 0.43 | P1-P2-P7-P8 | 1,520 | 30 |
| 16 | 0.44 | P1-P2-P7-P8 | 1,520 | 31 |
| 17 | 0.46 | P1-P2-P7-P8 | 1,551 | 31 |
| 18 | 0.46 | P1-P2-P7-P8 | 1,519 | 31 |
| 19 | 0.44 | P1-P2-P7-P8 | 1,409 | 31 |
| 20 | 0.39 | P1-P2-P7-P8 | 1,257 | 31 |
| 21 | 0.40 | P1-P2-P7-P8 | 1,241 | 31 |
| 22 | 0.36 | P1-P2-P7-P8 | 1,103 | 30 |
| 23 | 0.20 | P1-P2-P7-P8 | 693 | 30 |

Peak hour Y: **0.47** at 08:00 (critical P1-P2-P7-P8).

## 137 — with presence-zone undercount estimate (model input, attempt 8)

Train days used: 31 (2026-03-02 .. 2026-04-17); counts `intersections/137/counts/tmc_137_5min_estimated.csv`.

| hour | Y | critical phases | entering veh/h (counted movements) | days |
|---|---|---|---|---|
| 00 | 0.07 | P1-P2-P7-P8 | 269 | 31 |
| 01 | 0.05 | P1-P2-P7-P8 | 159 | 31 |
| 02 | 0.03 | P1-P2-P7-P8 | 119 | 31 |
| 03 | 0.03 | P1-P2-P7-P8 | 115 | 31 |
| 04 | 0.04 | P1-P2-P7-P8 | 133 | 31 |
| 05 | 0.10 | P1-P2-P7-P8 | 312 | 31 |
| 06 | 0.28 | P1-P2-P3-P4 | 974 | 31 |
| 07 | 0.50 | P1-P2-P3-P4 | 1,821 | 31 |
| 08 | 0.57 | P1-P2-P3-P4 | 2,230 | 30 |
| 09 | 0.55 | P1-P2-P7-P8 | 2,075 | 30 |
| 10 | 0.52 | P1-P2-P7-P8 | 1,995 | 30 |
| 11 | 0.51 | P1-P2-P7-P8 | 1,988 | 31 |
| 12 | 0.54 | P1-P2-P7-P8 | 2,049 | 31 |
| 13 | 0.53 | P1-P2-P7-P8 | 2,083 | 30 |
| 14 | 0.53 | P1-P2-P7-P8 | 2,054 | 30 |
| 15 | 0.55 | P1-P2-P3-P4 | 2,111 | 30 |
| 16 | 0.56 | P1-P2-P3-P4 | 2,098 | 31 |
| 17 | 0.58 | P1-P2-P3-P4 | 2,129 | 31 |
| 18 | 0.55 | P1-P2-P3-P4 | 2,019 | 31 |
| 19 | 0.51 | P1-P2-P7-P8 | 1,806 | 31 |
| 20 | 0.47 | P1-P2-P7-P8 | 1,639 | 31 |
| 21 | 0.48 | P1-P2-P7-P8 | 1,622 | 31 |
| 22 | 0.36 | P1-P2-P7-P8 | 1,103 | 30 |
| 23 | 0.20 | P1-P2-P7-P8 | 693 | 30 |

Peak hour Y: **0.58** at 17:00 (critical P1-P2-P3-P4).

## 7111 — as reported

Train days used: 26 (2026-08-31 .. 2026-10-09); counts `intersections/7111/counts/tmc_7111_5min.csv`.

| hour | Y | critical phases | entering veh/h (counted movements) | days |
|---|---|---|---|---|
| 00 | 0.05 | P1-P2-P8 | 371 | 25 |
| 01 | 0.03 | P1-P2-P8 | 244 | 25 |
| 02 | 0.02 | P1-P2-P8 | 162 | 25 |
| 03 | 0.02 | P1-P2-P8 | 128 | 24 |
| 04 | 0.04 | P1-P2-P8 | 180 | 24 |
| 05 | 0.16 | P1-P2-P8 | 554 | 26 |
| 06 | 0.31 | P1-P2-P3-P4 | 1,279 | 26 |
| 07 | 0.44 | P1-P2-P8 | 2,458 | 26 |
| 08 | 0.46 | P1-P2-P8 | 2,794 | 26 |
| 09 | 0.40 | P1-P2-P8 | 2,495 | 26 |
| 10 | 0.37 | P1-P2-P8 | 2,233 | 26 |
| 11 | 0.34 | P1-P2-P8 | 2,216 | 25 |
| 12 | 0.37 | P1-P2-P8 | 2,461 | 26 |
| 13 | 0.39 | P1-P2-P8 | 2,550 | 26 |
| 14 | 0.44 | P1-P2-P8 | 2,716 | 26 |
| 15 | 0.46 | P1-P2-P8 | 2,867 | 26 |
| 16 | 0.47 | P5-P6-P8 | 2,846 | 26 |
| 17 | 0.45 | P1-P2-P8 | 2,918 | 26 |
| 18 | 0.45 | P1-P2-P8 | 2,982 | 26 |
| 19 | 0.41 | P1-P2-P8 | 2,547 | 26 |
| 20 | 0.25 | P1-P2-P8 | 1,745 | 26 |
| 21 | 0.18 | P1-P2-P8 | 1,298 | 26 |
| 22 | 0.14 | P1-P2-P8 | 964 | 26 |
| 23 | 0.10 | P1-P2-P8 | 710 | 26 |

Peak hour Y: **0.47** at 16:00 (critical P5-P6-P8).

## Summary

| site / counts | peak Y | hour | hours with Y >= 0.6 | hours with Y >= 0.8 |
|---|---|---|---|---|
| 137 — as reported (WB through from 138) | 0.47 | 08:00 | 0 | 0 |
| 137 — with presence-zone undercount estimate (model input, attempt 8) | 0.58 | 17:00 | 0 | 0 |
| 7111 — as reported | 0.47 | 16:00 | 0 | 0 |
## Second measure: how often phases run to their limit (GDOT Split Monitor, train days)

Share of cycles where the phase ended by force-off or max-out, and share skipped; non-coordinated
phases, plan bands inside 06:00-20:30, readings marked ok, weighted by band length. More force-offs and
fewer skips = demand fills the green GDOT gives. Note: it also depends on how generous GDOT's splits are.

| site | phase | force-off + max-out % | skip % |
|---|---|---|---|
| 137 | P1 | 28 | 58 |
| 137 | P3 | 50 | 37 |
| 137 | P4 | 21 | 5 |
| 137 | P5 | 37 | 43 |
| 137 | P7 | 52 | 26 |
| 137 | P8 | 15 | 8 |
| 7111 | P1 | 62 | 8 |
| 7111 | P3 | 69 | 1 |
| 7111 | P4 | 38 | 5 |
| 7111 | P5 | 49 | 31 |
| 7111 | P8 | 76 | 1 |

