| Phase | Plan | days | avg split sim − field (s) | % gap-outs sim − field | % skips sim − field |
|---|---|---|---|---|---|
| P1 | A | 24 | +0.7 | +23 | +0 |
| P1 | B | 38 | +0.7 | +24 | +0 |
| P1 | C | 21 | +0.6 | +40 | +0 |
| P1 | D | 18 | +0.5 | +34 | +0 |
| P1 | E | 39 | +0.2 | -1 | +3 |
| P3 | A | 19 | -0.2 | +28 | +8 |
| P3 | B | 38 | -3.4 | +54 | +11 |
| P3 | C | 22 | -5.0 | +60 | +14 |
| P3 | D | 22 | -0.5 | -18 | +6 |
| P3 | E | 51 | — | +0 | +0 |
| P4 | A | 24 | -0.1 | +0 | +0 |
| P4 | B | 37 | +3.8 | +0 | +0 |
| P4 | C | 23 | +6.7 | +0 | +0 |
| P4 | D | 23 | +0.2 | +18 | +0 |
| P4 | E | 50 | +2.5 | -13 | +0 |
| P5 | A | 24 | -4.8 | +22 | +1 |
| P5 | B | 33 | -7.7 | +29 | -2 |
| P5 | C | 18 | -10.1 | +39 | -1 |
| P5 | D | 22 | -3.3 | +21 | +0 |
| P5 | E | 49 | +1.1 | -4 | +0 |
| P7 | A | 18 | -1.3 | +0 | +25 |
| P7 | B | 38 | -1.0 | -9 | +23 |
| P7 | C | 23 | -0.9 | -4 | +23 |
| P7 | D | 19 | -1.1 | +12 | +19 |
| P7 | E | 51 | — | +0 | +0 |
| P8 | A | 24 | +3.1 | +0 | +0 |
| P8 | B | 37 | +2.4 | +0 | +0 |
| P8 | C | 22 | +2.9 | +0 | +0 |
| P8 | D | 23 | +2.8 | -4 | +0 |
| P8 | E | 51 | +2.5 | -9 | +0 |

- **V1 average split:** 19/28 pairs within 3 s, worst 10.1 s → **FAIL**
- **V2 % gap-outs:** 17/30 pairs within 15 points, worst 60 → **FAIL**
- **V3 % skips:** 26/30 pairs within 15 points → **PASS** (reported)
- **V4 P8 discharge:** sim median 1952 vs field 1934 veh/h per lane of nominal green (+1.0 %) → **PASS**
- **V5 health:** 0 teleports; overflow days outside flagged days: 2026-09-14, 2026-09-23, 2026-09-28 → **FAIL**
