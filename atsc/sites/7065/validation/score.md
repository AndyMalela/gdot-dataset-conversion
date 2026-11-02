| Phase | Plan | days | avg split sim − field (s) | % gap-outs sim − field | % skips sim − field |
|---|---|---|---|---|---|
| P1 | A | 24 | +0.7 | +24 | +0 |
| P1 | B | 38 | +0.8 | +27 | +0 |
| P1 | C | 21 | +0.6 | +36 | +0 |
| P1 | D | 18 | +0.6 | +35 | +0 |
| P1 | E | 39 | +0.3 | -0 | +3 |
| P3 | A | 19 | -0.6 | +35 | +10 |
| P3 | B | 38 | -3.6 | +58 | +15 |
| P3 | C | 22 | -5.7 | +58 | +16 |
| P3 | D | 22 | -0.5 | -18 | +10 |
| P3 | E | 51 | — | +0 | +0 |
| P4 | A | 24 | +0.7 | +0 | +0 |
| P4 | B | 37 | +4.9 | +0 | +0 |
| P4 | C | 23 | +7.7 | +0 | +0 |
| P4 | D | 23 | +0.6 | +21 | +0 |
| P4 | E | 50 | +2.7 | -13 | +0 |
| P5 | A | 24 | -4.7 | +21 | +1 |
| P5 | B | 33 | -7.4 | +31 | -2 |
| P5 | C | 18 | -10.1 | +39 | -1 |
| P5 | D | 22 | -3.2 | +15 | +0 |
| P5 | E | 49 | +1.1 | -4 | -0 |
| P7 | A | 18 | -1.3 | +0 | +24 |
| P7 | B | 38 | -1.0 | -9 | +20 |
| P7 | C | 23 | -0.9 | -4 | +23 |
| P7 | D | 19 | -1.1 | +14 | +19 |
| P7 | E | 51 | — | +0 | +0 |
| P8 | A | 24 | +3.0 | +0 | +0 |
| P8 | B | 37 | +2.1 | +0 | +0 |
| P8 | C | 22 | +2.8 | +0 | +0 |
| P8 | D | 23 | +2.4 | -5 | +0 |
| P8 | E | 51 | +2.7 | -13 | +0 |

- **V1 average split:** 19/28 pairs within 3 s, worst 10.1 s → **FAIL**
- **V2 % gap-outs:** 18/30 pairs within 15 points, worst 58 → **FAIL**
- **V3 % skips:** 24/30 pairs within 15 points → **PASS** (reported)
- **V4 P8 discharge:** sim median 1949 vs field 1934 veh/h per lane of nominal green (+0.8 %) → **PASS**
- **V5 health:** 4 teleports; overflow days outside flagged days: 2026-09-03, 2026-09-14, 2026-09-23, 2026-09-28 → **FAIL**
