| Phase | Plan | days | avg split sim − field (s) | % gap-outs sim − field | % skips sim − field |
|---|---|---|---|---|---|
| P1 | A | 24 | +0.5 | +17 | +0 |
| P1 | B | 38 | +0.7 | +20 | +0 |
| P1 | C | 21 | +0.7 | +39 | +0 |
| P1 | D | 18 | +0.5 | +29 | +0 |
| P1 | E | 39 | +0.4 | -3 | +3 |
| P3 | A | 19 | -0.3 | +32 | +10 |
| P3 | B | 38 | -3.8 | +60 | +13 |
| P3 | C | 22 | -5.5 | +57 | +16 |
| P3 | D | 22 | -0.5 | -18 | +10 |
| P3 | E | 51 | — | +0 | +0 |
| P4 | A | 24 | +0.7 | +0 | +0 |
| P4 | B | 37 | +5.0 | +0 | +0 |
| P4 | C | 23 | +7.4 | +0 | +0 |
| P4 | D | 23 | +0.5 | +16 | +0 |
| P4 | E | 50 | +2.7 | -12 | +0 |
| P5 | A | 24 | -4.2 | +20 | +0 |
| P5 | B | 33 | -6.7 | +29 | -2 |
| P5 | C | 18 | -8.8 | +32 | -1 |
| P5 | D | 22 | -3.0 | +16 | +0 |
| P5 | E | 49 | +1.1 | -5 | +1 |
| P7 | A | 18 | -1.2 | +0 | +24 |
| P7 | B | 38 | -1.0 | -9 | +20 |
| P7 | C | 23 | -0.9 | -4 | +23 |
| P7 | D | 19 | -1.0 | +11 | +20 |
| P7 | E | 51 | — | +0 | +0 |
| P8 | A | 24 | +3.0 | +0 | +0 |
| P8 | B | 37 | +2.3 | +0 | +0 |
| P8 | C | 22 | +2.9 | +0 | +0 |
| P8 | D | 23 | +2.6 | -2 | +0 |
| P8 | E | 51 | +2.7 | -14 | +0 |

- **V1 average split:** 21/28 pairs within 3 s, worst 8.8 s → **FAIL**
- **V2 % gap-outs:** 17/30 pairs within 15 points, worst 60 → **FAIL**
- **V3 % skips:** 25/30 pairs within 15 points → **PASS** (reported)
- **V4 P8 discharge:** sim median 1949 vs field 1934 veh/h per lane of nominal green (+0.8 %) → **PASS**
- **V5 health:** 8 teleports; overflow days outside flagged days: 2026-09-14, 2026-09-23, 2026-09-25, 2026-09-28 → **FAIL**
