# RQ1 evaluation: strengths and weaknesses by traffic condition (137, validation weekdays)

120 clean hours on 5 days x 1 simulation seeds (seed-averaged per hour). Y = sum of critical flow ratios from the field counts. Intervals: 95 % day-bootstrap. **Limitations (137, 2026-11-16):** uncalibrated driver model; lanes inferred from detector zones, not verified; EB through demand rebuilt from the advance count zone (Approach Volume - EB left); WB left uncounted (no demand); WB/EB right turns routed as through; coordinated site modelled isolated. Main tables: learnt controllers at one training seed (lstdq = v1 seed 0); all training seeds of every learner are in the training-seed tables (simulation seed 1).

Hours per condition: light (Y < 0.15) 30, moderate (0.15-0.30) 13, busy (0.30-0.40) 18, heavy (Y >= 0.40) 59

## Overall mean delay, vehicle-weighted (s/veh)

| Controller | mean delay (95 % interval) |
|---|---|
| gdot | 21.5 (20.2 to 22.6) |
| actuated | 17.6 (17.0 to 18.6) |
| webster | 80.1 (24.9 to 189.2) |
| maxpressure | 73.4 (28.3 to 138.5) |
| ars_s0 | 17.9 (17.1 to 18.7) |
| lstdq_v2_s0 | 21.8 (20.7 to 23.3) |
| qlearn_s0 | 252.1 (65.2 to 525.5) |

## Mean delay (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 18.8 (17.9 to 19.6) | 11.5 (11.2 to 11.9) | 13.5 (12.2 to 15.2) | 21.8 (18.4 to 26.4) | 23.5 (21.5 to 26.2) |
| actuated | 16.0 (15.5 to 16.7) | 11.5 (11.2 to 11.9) | 12.8 (12.2 to 13.6) | 16.0 (15.2 to 16.8) | 18.9 (18.1 to 19.8) |
| webster | 65.3 (23.4 to 148.5) | 18.7 (17.9 to 19.8) | 21.2 (19.3 to 23.7) | 25.4 (24.1 to 26.6) | 85.6 (25.7 to 202.8) |
| maxpressure | 55.3 (24.6 to 101.8) | 17.5 (16.2 to 18.7) | 14.2 (13.0 to 15.6) | 18.8 (18.5 to 19.2) | 92.8 (31.9 to 157.9) |
| ars_s0 | 16.3 (15.9 to 16.9) | 12.2 (11.7 to 12.9) | 13.1 (11.7 to 14.7) | 17.3 (15.6 to 19.7) | 19.0 (18.1 to 20.1) |
| lstdq_v2_s0 | 19.4 (18.7 to 20.3) | 13.3 (12.6 to 14.1) | 13.8 (12.0 to 15.8) | 18.9 (17.0 to 21.2) | 24.1 (22.4 to 26.2) |
| qlearn_s0 | 179.1 (47.2 to 376.9) | 14.4 (14.1 to 14.7) | 16.5 (15.5 to 17.7) | 37.5 (20.8 to 60.8) | 304.3 (91.8 to 557.8) |

## Gain vs Webster (%, negative = less delay than Webster)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | -24.3 (-32.5 to -18.1) | -37.7 (-39.5 to -35.3) | -35.2 (-37.0 to -32.3) | -11.3 (-26.1 to 2.8) | -16.0 (-29.0 to -7.0) |
| actuated | -35.2 (-40.2 to -32.2) | -37.7 (-39.5 to -35.3) | -38.3 (-41.9 to -33.7) | -34.5 (-39.6 to -31.1) | -32.5 (-40.5 to -27.6) |
| webster | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| maxpressure | 30.9 (2.9 to 60.9) | -5.6 (-11.7 to 1.7) | -31.7 (-34.9 to -26.5) | -23.8 (-27.8 to -19.9) | 112.4 (18.9 to 262.7) |
| ars_s0 | -33.6 (-39.3 to -30.1) | -34.3 (-36.4 to -32.4) | -37.8 (-40.2 to -35.4) | -30.2 (-34.0 to -25.3) | -32.1 (-40.0 to -27.4) |
| lstdq_v2_s0 | -22.3 (-29.1 to -17.8) | -28.5 (-31.9 to -25.1) | -34.2 (-38.4 to -30.0) | -23.5 (-32.3 to -17.2) | -14.5 (-25.1 to -8.3) |
| qlearn_s0 | 298.7 (75.6 to 521.9) | -22.2 (-25.5 to -18.5) | -19.8 (-26.2 to -9.2) | 44.0 (-14.4 to 112.7) | 608.3 (242.8 to 964.8) |

## Gain vs actuated (%, negative = less delay than actuated)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 15.8 (10.4 to 21.4) | 0.0 (0.0 to 0.0) | 5.6 (-3.4 to 13.5) | 34.9 (20.9 to 55.6) | 23.6 (15.4 to 32.0) |
| actuated | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| webster | 263.5 (52.2 to 682.5) | 62.4 (55.7 to 67.3) | 65.4 (52.4 to 76.5) | 59.0 (49.6 to 71.3) | 341.8 (41.5 to 935.8) |
| maxpressure | 193.1 (53.4 to 401.7) | 52.0 (40.9 to 64.6) | 11.6 (1.1 to 19.1) | 17.8 (12.2 to 22.7) | 348.0 (73.4 to 642.5) |
| ars_s0 | 2.8 (1.3 to 4.0) | 5.9 (3.4 to 8.4) | 1.8 (-7.3 to 8.3) | 7.5 (-1.0 to 15.9) | 0.8 (0.0 to 1.9) |
| lstdq_v2_s0 | 20.0 (18.9 to 21.6) | 15.2 (11.4 to 18.6) | 7.3 (-4.9 to 16.4) | 17.2 (11.7 to 25.2) | 26.7 (23.1 to 32.2) |
| qlearn_s0 | 810.1 (161.3 to 1756.4) | 24.9 (22.5 to 26.7) | 29.6 (23.9 to 36.9) | 137.7 (25.9 to 298.4) | 1398.8 (400.1 to 2578.2) |

## Regret: delay above the best controller in the same hour (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 3.3 (2.4 to 4.1) | 0.3 (0.2 to 0.4) | 1.4 (0.7 to 2.0) | 6.1 (3.3 to 9.8) | 5.0 (3.4 to 7.0) |
| actuated | 0.4 (0.3 to 0.5) | 0.3 (0.2 to 0.4) | 0.7 (0.2 to 1.4) | 0.3 (0.0 to 0.6) | 0.5 (0.4 to 0.6) |
| webster | 49.8 (8.2 to 132.3) | 7.5 (6.6 to 8.2) | 9.0 (7.9 to 10.3) | 9.7 (8.6 to 10.9) | 67.2 (8.0 to 183.8) |
| maxpressure | 39.8 (9.3 to 85.7) | 6.2 (5.0 to 7.5) | 2.1 (1.5 to 2.8) | 3.1 (2.2 to 3.6) | 74.3 (14.3 to 138.8) |
| ars_s0 | 0.8 (0.7 to 0.9) | 1.0 (0.7 to 1.3) | 1.0 (0.4 to 1.4) | 1.6 (0.5 to 2.9) | 0.6 (0.4 to 0.8) |
| lstdq_v2_s0 | 3.9 (3.5 to 4.2) | 2.0 (1.7 to 2.4) | 1.7 (0.8 to 2.5) | 3.2 (1.9 to 4.6) | 5.7 (4.7 to 7.0) |
| qlearn_s0 | 163.6 (31.9 to 360.7) | 3.1 (2.9 to 3.4) | 4.4 (3.3 to 6.1) | 21.8 (4.6 to 45.8) | 285.8 (74.1 to 538.8) |

## Worst-off movement: highest 95th-percentile delay of any movement in the hour (s)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 102.9 (96.8 to 107.9) | 32.6 (30.4 to 34.8) | 90.6 (77.6 to 101.6) | 134.3 (107.8 to 167.8) | 135.2 (128.4 to 142.1) |
| actuated | 64.7 (62.2 to 68.7) | 32.6 (30.4 to 34.8) | 49.0 (47.4 to 50.4) | 65.4 (61.3 to 69.6) | 84.0 (79.7 to 88.2) |
| webster | 195.6 (68.0 to 438.6) | 48.7 (45.5 to 53.1) | 68.7 (57.3 to 83.1) | 93.0 (68.0 to 130.3) | 258.9 (76.8 to 602.5) |
| maxpressure | 175.3 (100.2 to 283.7) | 91.1 (88.3 to 94.0) | 94.3 (86.9 to 99.1) | 78.2 (68.3 to 95.5) | 269.2 (114.0 to 424.4) |
| ars_s0 | 80.8 (76.2 to 84.4) | 50.6 (47.1 to 54.3) | 88.3 (75.9 to 103.8) | 120.9 (81.3 to 160.5) | 88.0 (81.7 to 93.2) |
| lstdq_v2_s0 | 99.0 (92.8 to 104.8) | 46.0 (35.0 to 57.1) | 84.9 (74.7 to 99.2) | 121.0 (101.1 to 154.0) | 123.2 (120.4 to 125.9) |
| qlearn_s0 | 432.1 (156.3 to 820.1) | 42.7 (41.6 to 44.0) | 57.1 (45.0 to 72.9) | 168.0 (65.8 to 275.8) | 736.6 (262.7 to 1243.5) |

## Hours with a queue reaching the leg end (share of hours with >= 10 vehicles unable to enter)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 0.02 (0.00 to 0.06) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.08 (0.00 to 0.21) |
| actuated | 0.01 (0.00 to 0.02) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.01 (0.00 to 0.04) |
| webster | 0.07 (0.01 to 0.14) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.14 (0.02 to 0.27) |
| maxpressure | 0.18 (0.08 to 0.29) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.38 (0.19 to 0.57) |
| ars_s0 | 0.01 (0.00 to 0.02) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.01 (0.00 to 0.04) |
| lstdq_v2_s0 | 0.02 (0.00 to 0.06) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.06 (0.00 to 0.12) |
| qlearn_s0 | 0.33 (0.17 to 0.53) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.15 (0.00 to 0.38) | 0.61 (0.41 to 0.82) |

## How often each controller is best in an hour

| Controller | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|
| gdot | 63 % | 15 % | 0 % | 0 % |
| actuated | 63 % | 46 % | 44 % | 47 % |
| webster | 0 % | 0 % | 0 % | 0 % |
| maxpressure | 0 % | 0 % | 6 % | 0 % |
| ars_s0 | 37 % | 31 % | 50 % | 53 % |
| lstdq_v2_s0 | 0 % | 8 % | 0 % | 0 % |
| qlearn_s0 | 0 % | 0 % | 0 % | 0 % |
