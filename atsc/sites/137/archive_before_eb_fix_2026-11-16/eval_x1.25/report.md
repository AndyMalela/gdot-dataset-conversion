# RQ1 evaluation: strengths and weaknesses by traffic condition (137, validation weekdays, DEMAND SCALED x1.25: a sensitivity experiment on the real profile, not real traffic)

120 clean hours on 5 days x 1 simulation seeds (seed-averaged per hour). Y = sum of critical flow ratios from the field counts. Intervals: 95 % day-bootstrap. **Limitations (137, 2026-11-16):** uncalibrated driver model; lanes inferred from detector zones, not verified; EB through demand rebuilt from the advance count zone (Approach Volume - EB left); WB left uncounted (no demand); WB/EB right turns routed as through; coordinated site modelled isolated. Main tables: learnt controllers at one training seed (lstdq = v1 seed 0); all training seeds of every learner are in the training-seed tables (simulation seed 1).

Hours per condition: light (Y < 0.15) 27, moderate (0.15-0.30) 14, busy (0.30-0.40) 2, heavy (Y >= 0.40) 77

## Overall mean delay, vehicle-weighted (s/veh)

| Controller | mean delay (95 % interval) |
|---|---|
| gdot | 33.7 (24.9 to 42.8) |
| actuated | 22.0 (20.2 to 24.8) |
| webster | 252.7 (69.1 to 457.9) |
| maxpressure | 795.1 (154.2 to 1448.6) |
| ars_s0 | 27.2 (22.0 to 34.2) |
| lstdq_v2_s0 | 33.4 (25.4 to 46.5) |
| qlearn_s0 | 1814.3 (1053.8 to 2667.8) |

## Mean delay (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 27.0 (21.5 to 33.1) | 11.8 (11.1 to 12.6) | 13.7 (12.4 to 14.9) | 17.3 (15.3 to 19.3) | 34.5 (26.8 to 42.5) |
| actuated | 19.2 (18.1 to 21.1) | 11.8 (11.1 to 12.6) | 13.2 (12.0 to 14.3) | 14.6 (14.6 to 14.6) | 22.7 (21.2 to 25.3) |
| webster | 183.1 (57.1 to 318.1) | 20.1 (18.4 to 22.6) | 43.9 (26.5 to 63.0) | 95.4 (30.4 to 160.3) | 258.9 (70.6 to 449.7) |
| maxpressure | 561.4 (111.3 to 1011.6) | 17.3 (16.2 to 18.2) | 45.2 (14.6 to 104.9) | 33.5 (16.2 to 50.9) | 828.6 (164.7 to 1478.5) |
| ars_s0 | 22.9 (19.9 to 27.4) | 12.4 (11.2 to 13.7) | 15.4 (12.6 to 18.2) | 14.3 (13.6 to 14.9) | 27.6 (22.9 to 34.1) |
| lstdq_v2_s0 | 27.5 (22.4 to 36.5) | 13.3 (12.5 to 14.5) | 15.2 (13.9 to 16.8) | 17.6 (17.2 to 18.0) | 34.2 (26.9 to 46.7) |
| qlearn_s0 | 1290.4 (798.8 to 1872.4) | 14.5 (13.9 to 14.9) | 100.1 (36.2 to 168.9) | 1088.2 (765.2 to 1411.2) | 1956.9 (1162.7 to 2907.6) |

## Gain vs Webster (%, negative = less delay than Webster)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | -48.1 (-64.1 to -33.6) | -40.0 (-42.0 to -37.8) | -48.9 (-55.3 to -43.4) | -68.8 (-88.0 to -49.7) | -49.5 (-75.1 to -26.4) |
| actuated | -57.0 (-67.5 to -47.6) | -40.0 (-42.0 to -37.8) | -51.3 (-59.0 to -45.2) | -71.5 (-90.9 to -52.0) | -63.2 (-80.3 to -48.5) |
| webster | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| maxpressure | 184.0 (76.5 to 291.5) | -11.3 (-18.4 to -4.3) | -22.3 (-49.5 to 21.2) | -57.5 (-68.3 to -46.7) | 284.6 (137.0 to 432.3) |
| ars_s0 | -53.9 (-64.8 to -43.5) | -37.5 (-40.7 to -33.6) | -45.0 (-57.5 to -37.3) | -72.9 (-90.7 to -55.1) | -60.7 (-78.8 to -45.2) |
| lstdq_v2_s0 | -46.9 (-60.4 to -36.6) | -32.7 (-34.8 to -30.1) | -43.8 (-53.9 to -35.2) | -66.1 (-88.8 to -43.4) | -51.6 (-73.0 to -35.1) |
| qlearn_s0 | 1235.5 (592.3 to 1991.7) | -25.7 (-30.9 to -20.8) | 162.2 (4.0 to 324.3) | 1597.5 (780.1 to 2414.8) | 1922.3 (896.4 to 3204.3) |

## Gain vs actuated (%, negative = less delay than actuated)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 28.2 (15.3 to 41.3) | 0.0 (0.0 to 0.0) | 4.3 (1.5 to 6.7) | 18.7 (4.9 to 32.5) | 42.1 (22.9 to 61.3) |
| actuated | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| webster | 633.2 (194.0 to 1110.7) | 70.2 (61.9 to 79.8) | 218.3 (99.6 to 373.5) | 554.5 (108.4 to 1000.5) | 889.9 (218.9 to 1651.7) |
| maxpressure | 2153.8 (400.7 to 3974.2) | 47.9 (36.1 to 61.9) | 209.6 (16.1 to 593.1) | 130.1 (11.2 to 249.1) | 3202.8 (608.1 to 6028.6) |
| ars_s0 | 13.9 (10.2 to 18.4) | 5.2 (-0.6 to 10.5) | 14.4 (2.0 to 26.7) | -2.3 (-6.5 to 2.0) | 15.8 (7.7 to 25.7) |
| lstdq_v2_s0 | 32.7 (22.2 to 51.6) | 13.1 (9.0 to 17.4) | 14.9 (9.0 to 20.2) | 20.6 (17.9 to 23.2) | 41.8 (25.7 to 68.9) |
| qlearn_s0 | 5756.1 (3643.9 to 8404.3) | 23.8 (18.5 to 27.8) | 622.9 (152.5 to 1163.2) | 7363.8 (5142.0 to 9585.7) | 8691.3 (5395.3 to 13082.8) |

## Regret: delay above the best controller in the same hour (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 8.7 (3.7 to 14.0) | 0.4 (0.3 to 0.5) | 0.8 (0.4 to 1.3) | 3.2 (1.7 to 4.7) | 12.7 (5.6 to 19.9) |
| actuated | 0.8 (0.2 to 2.0) | 0.4 (0.3 to 0.5) | 0.3 (0.1 to 0.5) | 0.5 (0.0 to 0.9) | 0.9 (0.1 to 2.6) |
| webster | 164.7 (39.2 to 299.1) | 8.7 (7.4 to 10.5) | 31.1 (13.8 to 50.8) | 81.3 (16.8 to 145.8) | 237.1 (49.4 to 427.0) |
| maxpressure | 543.1 (93.3 to 992.9) | 5.9 (4.8 to 7.2) | 32.3 (2.3 to 91.9) | 19.4 (2.6 to 36.3) | 806.8 (143.5 to 1456.5) |
| ars_s0 | 4.5 (2.0 to 8.3) | 1.0 (0.5 to 1.7) | 2.6 (0.6 to 4.5) | 0.1 (0.0 to 0.3) | 5.8 (1.7 to 11.5) |
| lstdq_v2_s0 | 9.1 (4.5 to 17.4) | 1.9 (1.4 to 2.4) | 2.3 (1.6 to 3.1) | 3.5 (3.4 to 3.6) | 12.4 (5.8 to 23.9) |
| qlearn_s0 | 1272.0 (780.7 to 1854.2) | 3.1 (2.5 to 3.6) | 87.2 (23.7 to 156.4) | 1074.1 (751.5 to 1396.6) | 1935.1 (1141.4 to 2885.7) |

## Worst-off movement: highest 95th-percentile delay of any movement in the hour (s)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 134.4 (113.9 to 157.0) | 35.6 (31.8 to 39.4) | 81.0 (68.4 to 94.3) | 101.3 (69.7 to 132.9) | 178.6 (152.0 to 205.4) |
| actuated | 83.5 (77.2 to 92.1) | 35.6 (31.8 to 39.4) | 56.1 (49.7 to 62.8) | 62.4 (54.9 to 69.9) | 105.5 (98.2 to 114.4) |
| webster | 468.9 (204.3 to 772.8) | 56.1 (47.3 to 71.8) | 209.2 (119.9 to 303.7) | 391.8 (93.9 to 689.6) | 641.6 (240.6 to 1089.6) |
| maxpressure | 1300.0 (358.1 to 2241.9) | 93.2 (88.9 to 96.9) | 217.0 (90.6 to 457.6) | 215.6 (80.1 to 351.0) | 1874.9 (504.6 to 3241.6) |
| ars_s0 | 102.4 (94.6 to 112.6) | 58.3 (49.0 to 67.5) | 118.4 (90.7 to 146.1) | 89.5 (79.1 to 100.0) | 113.4 (96.9 to 130.4) |
| lstdq_v2_s0 | 118.3 (103.8 to 136.2) | 46.0 (37.3 to 57.0) | 101.2 (79.2 to 123.6) | 105.7 (102.5 to 108.8) | 146.3 (129.4 to 170.0) |
| qlearn_s0 | 3034.4 (2016.5 to 4111.4) | 40.8 (37.0 to 44.6) | 412.6 (146.4 to 678.8) | 3032.7 (2378.1 to 3687.3) | 4546.7 (2896.8 to 6346.0) |

## Hours with a queue reaching the leg end (share of hours with >= 10 vehicles unable to enter)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 0.10 (0.03 to 0.17) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.15 (0.06 to 0.24) |
| actuated | 0.06 (0.00 to 0.12) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.08 (0.00 to 0.18) |
| webster | 0.44 (0.32 to 0.57) | 0.00 (0.00 to 0.00) | 0.15 (0.00 to 0.35) | 0.50 (0.00 to 1.00) | 0.64 (0.45 to 0.83) |
| maxpressure | 0.52 (0.42 to 0.62) | 0.00 (0.00 to 0.00) | 0.05 (0.00 to 0.15) | 0.50 (0.00 to 1.00) | 0.78 (0.66 to 0.92) |
| ars_s0 | 0.13 (0.07 to 0.20) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.20 (0.12 to 0.29) |
| lstdq_v2_s0 | 0.12 (0.05 to 0.22) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.19 (0.08 to 0.31) |
| qlearn_s0 | 0.64 (0.61 to 0.67) | 0.00 (0.00 to 0.00) | 0.25 (0.05 to 0.45) | 1.00 (1.00 to 1.00) | 0.94 (0.88 to 0.99) |

## How often each controller is best in an hour

| Controller | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|
| gdot | 59 % | 43 % | 0 % | 3 % |
| actuated | 59 % | 50 % | 50 % | 75 % |
| webster | 0 % | 0 % | 0 % | 0 % |
| maxpressure | 0 % | 0 % | 0 % | 0 % |
| ars_s0 | 37 % | 29 % | 50 % | 17 % |
| lstdq_v2_s0 | 4 % | 0 % | 0 % | 0 % |
| qlearn_s0 | 0 % | 0 % | 0 % | 5 % |
