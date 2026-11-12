| Phase | Plan | days | avg split sim − field (s) | % gap-outs sim − field | % skips sim − field |
|---|---|---|---|---|---|
| P1 | A | 24 | +0.6 | +18 | +0 |
| P1 | B | 38 | +0.7 | +23 | +0 |
| P1 | C | 21 | +0.7 | +40 | +0 |
| P1 | D | 18 | +0.5 | +29 | +0 |
| P1 | E | 39 | +0.4 | -2 | +3 |
| P3 | A | 19 | -0.4 | +32 | +11 |
| P3 | B | 38 | -3.8 | +60 | +13 |
| P3 | C | 22 | -5.6 | +56 | +15 |
| P3 | D | 22 | -0.5 | -18 | +10 |
| P3 | E | 51 | — | +0 | +0 |
| P4 | A | 24 | +0.8 | +0 | +0 |
| P4 | B | 37 | +5.0 | +0 | +0 |
| P4 | C | 23 | +7.4 | +0 | +0 |
| P4 | D | 23 | +0.3 | +16 | +0 |
| P4 | E | 50 | +2.7 | -12 | +0 |
| P5 | A | 24 | -4.8 | +24 | +1 |
| P5 | B | 33 | -7.6 | +29 | -2 |
| P5 | C | 18 | -10.0 | +40 | -1 |
| P5 | D | 22 | -3.4 | +18 | +0 |
| P5 | E | 49 | +1.1 | -5 | +1 |
| P7 | A | 18 | -1.2 | +0 | +24 |
| P7 | B | 38 | -1.0 | -9 | +19 |
| P7 | C | 23 | -0.9 | -4 | +21 |
| P7 | D | 19 | -1.0 | +10 | +20 |
| P7 | E | 51 | — | +0 | +0 |
| P8 | A | 24 | +2.9 | +0 | +0 |
| P8 | B | 37 | +2.3 | +0 | +0 |
| P8 | C | 22 | +2.8 | +0 | +0 |
| P8 | D | 23 | +2.6 | -3 | +0 |
| P8 | E | 51 | +2.7 | -14 | +0 |

- **V1 average split:** 20/28 pairs within 3 s, worst 10.0 s → **FAIL**
- **V2 % gap-outs:** 17/30 pairs within 15 points, worst 60 → **FAIL**
- **V3 % skips:** 25/30 pairs within 15 points → **PASS** (reported)
- **V4 P8 discharge:** sim median 1941 vs field 1934 veh/h per lane of nominal green (+0.4 %) → **PASS**
- **V5 health:** 0 teleports; overflow days outside flagged days: 2026-09-14, 2026-09-23, 2026-09-25, 2026-09-28 → **FAIL**
