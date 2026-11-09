# RQ1 analysis: paired tests, mechanism, learnt rule (SIG 7065, validation weekdays)

471 clean hours on 20 days. Learners pooled over training x simulation seeds; rule controllers over 3 simulation seeds. Runs per controller: Field plan 3, Webster 3, Actuated 3, MaxPressure 3, LSTDQ v1 11, LSTDQ v2 10, LSTDQ v2f 10, Q-learning 10, ARS 10, NFQ 9, NFQ (registered, short horizon) 5.

**Limitations (every result):** isolated model of a signal in GDOT's coordinated Peachtree group; the simulation is not yet accepted by its own validation (VALIDATION.md: V1 split, V2 gap-outs, V5 overflow days fail, mostly the left-turn phases); P2 count suspect; right turns uncounted.

## 1. Difference from MaxPressure, paired by hour (s/veh; negative = less delay than MaxPressure)

Mean over days of the daily mean difference (95 % day-bootstrap), Wilcoxon signed-rank p over days. **Bold** = interval excludes 0 and p < 0.05 (no multiple-test correction; 45 tests in this table).

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| Field plan | **+11.8** (+10.4 to +13.6), p=0.000 | **+3.2** (+2.9 to +3.4), p=0.000 | **+5.0** (+4.2 to +5.7), p=0.000 | **+12.8** (+12.4 to +13.3), p=0.000 | **+28.4** (+21.9 to +36.1), p=0.000 |
| Webster | **+7.2** (+6.8 to +7.7), p=0.000 | **+15.2** (+14.1 to +16.1), p=0.000 | **+2.2** (+1.9 to +2.5), p=0.000 | **+3.7** (+2.9 to +4.4), p=0.000 | **+7.5** (+5.6 to +9.9), p=0.000 |
| Actuated | **+4.9** (+4.2 to +5.4), p=0.000 | **+1.3** (+1.0 to +1.6), p=0.000 | **+4.7** (+3.8 to +5.2), p=0.000 | **+6.9** (+6.4 to +7.2), p=0.000 | **+6.1** (+3.5 to +8.1), p=0.001 |
| LSTDQ v1 | **+1.0** (+0.3 to +1.6), p=0.012 | +0.1 (-0.2 to +0.4), p=0.349 | +0.6 (-0.2 to +1.0), p=0.001 | **+1.8** (+1.3 to +2.2), p=0.000 | +0.8 (-2.2 to +3.2), p=0.012 |
| LSTDQ v2 | **+1.7** (+1.3 to +2.2), p=0.000 | **+5.0** (+4.6 to +5.4), p=0.000 | **+2.1** (+1.6 to +2.9), p=0.000 | **+0.6** (+0.0 to +1.3), p=0.001 | -1.4 (-3.9 to +0.8), p=0.622 |
| LSTDQ v2f | +0.5 (-0.1 to +1.0), p=0.017 | **+3.4** (+3.0 to +3.7), p=0.000 | +0.6 (-0.1 to +1.1), p=0.001 | -0.1 (-0.5 to +0.2), p=0.430 | **-2.6** (-5.5 to -0.5), p=0.003 |
| Q-learning | **+6.7** (+1.2 to +15.4), p=0.000 | **+0.2** (+0.0 to +0.4), p=0.036 | +2.7 (-0.6 to +8.1), p=0.017 | **+3.6** (+1.0 to +7.6), p=0.000 | **+23.1** (+4.3 to +50.1), p=0.000 |
| ARS | +0.0 (-0.2 to +0.3), p=0.869 | -0.1 (-0.3 to +0.1), p=0.475 | -0.3 (-0.8 to +0.0), p=0.330 | +0.0 (-0.1 to +0.1), p=0.596 | +0.5 (-0.5 to +1.9), p=0.729 |
| NFQ | **+17.2** (+15.8 to +19.3), p=0.000 | **+16.8** (+16.5 to +17.1), p=0.000 | **+12.5** (+11.7 to +13.0), p=0.000 | **+14.7** (+14.3 to +15.1), p=0.000 | **+26.5** (+20.0 to +34.9), p=0.000 |

## 2. Top learners against each other (row - column, all hours, s/veh)

| | LSTDQ v2 | ARS | LSTDQ v1 |
|---|---|---|---|
| LSTDQ v2f | **-1.2** (-1.7 to -0.8), p=0.000 | +0.5 (-0.0 to +0.9), p=0.048 | **-0.5** (-0.8 to -0.2), p=0.001 |
| LSTDQ v2 |  | **+1.7** (+1.2 to +2.2), p=0.000 | **+0.7** (+0.2 to +1.3), p=0.009 |
| ARS |  |  | **-1.0** (-1.5 to -0.3), p=0.014 |

## 3. Rank by condition (mean delay; ties within 0.5 s/veh share a rank)

| Controller | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|
| Field plan | 6 (29.9) | 8 (36.0) | 9 (46.0) | 10 (68.7) |
| Webster | 9 (41.9) | 5 (33.2) | 6 (37.0) | 7 (47.4) |
| Actuated | 5 (27.9) | 8 (35.7) | 8 (40.1) | 6 (46.5) |
| MaxPressure | 1 (26.7) | 1 (31.0) | 1 (33.3) | 3 (40.3) |
| LSTDQ v1 | 1 (26.8) | 3 (31.6) | 5 (35.1) | 5 (41.3) |
| LSTDQ v2 | 8 (31.7) | 5 (33.1) | 4 (33.9) | 2 (39.1) |
| LSTDQ v2f | 6 (30.0) | 3 (31.6) | 1 (33.2) | 1 (37.8) |
| Q-learning | 1 (26.9) | 7 (33.9) | 6 (36.5) | 8 (66.8) |
| ARS | 1 (26.6) | 1 (30.7) | 1 (33.3) | 3 (40.7) |
| NFQ | 10 (43.4) | 10 (43.5) | 10 (47.9) | 9 (67.6) |

## 4. Mechanism by condition (simulation seed 2)

Cycle = mean cycle length (s). Max-out = share of greens ended at max green. Then mean green (s) and greens per cycle (1.00 = served every cycle; lower = skipped) for the two critical phases at peak: P8 Piedmont-N through and P5 Peachtree-NE left.

| Controller | light: cycle / max-out / P8 green, per cycle / P5 green, per cycle | moderate: cycle / max-out / P8 green, per cycle / P5 green, per cycle | busy: cycle / max-out / P8 green, per cycle / P5 green, per cycle | heavy: cycle / max-out / P8 green, per cycle / P5 green, per cycle |
|---|---|---|---|---|
| Field plan | 121 / 0 % / 39 s, 1.00 / 11 s, 0.71 | 130 / 0 % / 45 s, 1.00 / 13 s, 0.96 | 156 / 0 % / 52 s, 1.00 / 16 s, 1.00 | 173 / 0 % / 51 s, 1.00 / 20 s, 1.00 |
| Webster | 125 / 0 % / 38 s, 1.00 / 7 s, 1.00 | 111 / 0 % / 38 s, 0.99 / 7 s, 1.00 | 112 / 0 % / 40 s, 1.00 / 7 s, 1.00 | 112 / 0 % / 40 s, 1.00 / 7 s, 1.00 |
| Actuated | 109 / 3 % / 44 s, 1.00 / 11 s, 0.67 | 129 / 10 % / 51 s, 1.00 / 13 s, 0.95 | 137 / 16 % / 52 s, 1.00 / 16 s, 1.00 | 139 / 19 % / 53 s, 1.00 / 18 s, 1.00 |
| MaxPressure | 103 / 0 % / 42 s, 1.00 / 8 s, 0.66 | 110 / 0 % / 43 s, 1.00 / 8 s, 0.95 | 112 / 0 % / 42 s, 1.00 / 8 s, 0.99 | 113 / 1 % / 44 s, 1.00 / 8 s, 1.00 |
| LSTDQ v1 | 106 / 3 % / 43 s, 1.00 / 8 s, 0.67 | 115 / 2 % / 45 s, 1.00 / 8 s, 0.95 | 122 / 6 % / 47 s, 1.00 / 10 s, 0.99 | 124 / 7 % / 47 s, 1.00 / 12 s, 1.00 |
| LSTDQ v2 | 126 / 14 % / 46 s, 0.99 / 8 s, 0.74 | 123 / 5 % / 49 s, 1.00 / 8 s, 0.95 | 119 / 2 % / 47 s, 1.00 / 8 s, 0.99 | 121 / 5 % / 49 s, 1.01 / 9 s, 1.00 |
| LSTDQ v2f | 120 / 12 % / 47 s, 1.00 / 8 s, 0.71 | 118 / 3 % / 47 s, 1.01 / 8 s, 0.94 | 116 / 2 % / 45 s, 1.00 / 8 s, 0.99 | 118 / 4 % / 48 s, 1.00 / 9 s, 1.00 |
| Q-learning | 103 / 3 % / 42 s, 1.00 / 8 s, 0.63 | 111 / 1 % / 44 s, 1.00 / 8 s, 0.95 | 112 / 0 % / 42 s, 1.00 / 8 s, 0.99 | 115 / 1 % / 44 s, 1.00 / 9 s, 1.00 |
| ARS | 101 / 1 % / 41 s, 0.99 / 8 s, 0.62 | 110 / 0 % / 43 s, 1.01 / 8 s, 0.92 | 111 / 0 % / 42 s, 1.00 / 8 s, 0.99 | 110 / 0 % / 42 s, 1.00 / 8 s, 1.00 |
| NFQ | 152 / 47 % / 48 s, 0.99 / 28 s, 0.72 | 148 / 30 % / 51 s, 1.00 / 17 s, 0.97 | 149 / 32 % / 50 s, 1.00 / 15 s, 1.00 | 158 / 40 % / 51 s, 1.00 / 17 s, 1.00 |

Figures and tidy data: `results/` (README.md there).

## 5. What LSTDQ v2f learnt: when it ends a green

d = w(end) - w(extend) per serving phase, mean over 5 training seeds; the controller ends the green when d . x > 0. Each weight is multiplied by its feature's standard deviation in the states where that phase serves (LSTDQ v2f's own decisions, AM and PM peak of one training day), so a value is the push towards ending (+) or extending (-) from a typical change in that feature. Bias: the raw weight. Positive gap = a longer gap since the last vehicle pushes towards ending (as gap-out does). (n/5) = training seeds agreeing in sign.

| Serving phase | own gap | own queue | own occupancy | own rate | own elapsed | bias | strongest other-phase terms |
|---|---|---|---|---|---|---|---|
| P1 Peachtree-SW left | +0.00 (3/5) | -0.01 (3/5) | -0.17 (5/5) | -0.04 (5/5) | +0.07 (5/5) | -1.24 (4/5) | queue P6 -0.29 (5/5), gap P7 -0.29 (4/5), gap P3 -0.28 (4/5) |
| P2 Peachtree-NE through | +0.03 (5/5) | -0.52 (5/5) | -0.06 (5/5) | +0.02 (5/5) | -0.03 (4/5) | -0.18 (3/5) | gap P8 -0.16 (4/5), queue P5 -0.08 (4/5), queue P3 +0.07 (5/5) |
| P3 Piedmont-N left | -0.04 (4/5) | -0.20 (4/5) | +0.01 (3/5) | -0.01 (3/5) | +0.09 (5/5) | +0.02 (4/5) | gap P7 -0.26 (5/5), queue P7 -0.19 (3/5), queue P4 +0.14 (5/5) |
| P4 Piedmont-S through | +0.05 (5/5) | -0.14 (5/5) | +0.06 (5/5) | +0.00 (3/5) | +0.22 (5/5) | -2.03 (5/5) | queue P2 +0.24 (5/5), queue P6 +0.16 (5/5), gap P8 +0.14 (5/5) |
| P5 Peachtree-NE left | +0.01 (4/5) | -0.55 (3/5) | -0.61 (5/5) | +0.15 (5/5) | -0.05 (5/5) | +0.79 (2/5) | gap P7 -1.02 (2/5), gap P3 +0.44 (2/5), queue P2 +0.11 (4/5) |
| P6 Peachtree-SW through | +0.09 (5/5) | -0.09 (5/5) | -0.12 (3/5) | +0.05 (5/5) | +0.17 (4/5) | -0.62 (5/5) | queue P1 -0.27 (5/5), queue P8 +0.21 (5/5), gap P3 -0.14 (5/5) |
| P7 Piedmont-S left | -0.01 (3/5) | -0.12 (5/5) | -0.02 (1/5) | -0.00 (3/5) | +0.06 (5/5) | -0.99 (5/5) | queue P8 +0.24 (5/5), gap P3 -0.23 (5/5), queue P3 -0.09 (5/5) |
| P8 Piedmont-N through | +0.13 (5/5) | -0.69 (5/5) | -0.41 (5/5) | -0.15 (4/5) | +0.09 (4/5) | -0.65 (5/5) | queue P2 +0.40 (5/5), queue P4 -0.26 (5/5), queue P6 +0.21 (5/5) |

