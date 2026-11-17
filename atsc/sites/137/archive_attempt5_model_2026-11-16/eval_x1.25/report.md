# RQ1 evaluation: strengths and weaknesses by traffic condition (137, validation weekdays, DEMAND SCALED x1.25: a sensitivity experiment on the real profile, not real traffic)

120 clean hours on 5 days x 1 simulation seeds (seed-averaged per hour). Y = sum of critical flow ratios from the field counts. Intervals: 95 % day-bootstrap. **Limitations (137, 2026-11-16):** uncalibrated driver model; GDOT timing not yet field-validated; WB through from the upstream signal 138; EB/WB right turns run as through; P2/P6 stop-bar presence added in the model; coordinated corridor site (138 at ~260 m) modelled isolated; no pedestrian timing (atsc/sites/137/README.md). Main tables: learnt controllers at one training seed (lstdq_v2_s0 = LSTDQ, qlearn_s0, ars_s0); all training seeds of every learner are in the training-seed tables (simulation seed 1).

Hours per condition: light (Y < 0.15) 27, moderate (0.15-0.30) 10, busy (0.30-0.40) 4, heavy (Y >= 0.40) 79

## Overall mean delay, vehicle-weighted (s/veh)

| Controller | mean delay (95 % interval) |
|---|---|
| gdot | 69.3 (35.6 to 107.3) |
| actuated | 46.0 (30.5 to 62.8) |
| webster | 237.9 (76.1 to 399.7) |
| maxpressure | 51.8 (31.6 to 76.7) |
| ars_s0 | 75.3 (39.4 to 125.4) |
| lstdq_v2_s0 | 65.0 (34.9 to 104.2) |
| qlearn_s0 | 173.5 (62.8 to 303.2) |

## Mean delay (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 51.0 (28.8 to 78.8) | 11.1 (9.5 to 12.9) | 15.4 (12.6 to 17.8) | 17.7 (16.4 to 20.3) | 69.0 (37.5 to 107.4) |
| actuated | 34.4 (25.1 to 43.8) | 11.1 (9.5 to 12.9) | 15.1 (12.5 to 17.1) | 16.9 (15.8 to 18.3) | 45.0 (31.7 to 58.3) |
| webster | 177.3 (63.4 to 288.6) | 22.9 (22.2 to 23.7) | 85.2 (24.2 to 173.8) | 28.4 (25.2 to 34.2) | 244.7 (82.2 to 407.2) |
| maxpressure | 38.3 (26.3 to 52.1) | 13.3 (10.8 to 15.9) | 16.5 (12.8 to 19.4) | 14.1 (12.6 to 16.3) | 50.0 (32.9 to 69.7) |
| ars_s0 | 55.3 (31.9 to 91.7) | 12.2 (10.2 to 14.5) | 17.2 (12.4 to 23.5) | 16.0 (15.3 to 16.7) | 74.6 (40.8 to 125.1) |
| lstdq_v2_s0 | 48.1 (30.0 to 69.9) | 16.2 (13.0 to 19.7) | 21.0 (17.3 to 23.9) | 19.3 (17.8 to 20.8) | 62.7 (36.2 to 95.7) |
| qlearn_s0 | 128.4 (48.2 to 233.8) | 11.4 (9.4 to 13.6) | 17.2 (13.1 to 22.0) | 15.0 (13.8 to 16.3) | 182.4 (67.4 to 328.0) |

## Gain vs Webster (%, negative = less delay than Webster)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | -26.9 (-57.0 to -1.0) | -51.2 (-58.5 to -44.6) | -50.1 (-63.5 to -35.6) | -35.7 (-50.2 to -22.0) | -17.0 (-58.0 to 19.7) |
| actuated | -49.4 (-65.6 to -36.7) | -51.2 (-58.5 to -44.6) | -51.2 (-64.9 to -36.1) | -38.9 (-49.7 to -29.5) | -49.4 (-70.2 to -32.7) |
| webster | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| maxpressure | -44.0 (-63.8 to -26.9) | -41.2 (-52.9 to -29.7) | -49.2 (-60.9 to -35.7) | -48.6 (-60.8 to -37.3) | -44.6 (-69.6 to -23.5) |
| ars_s0 | -28.3 (-55.2 to -0.8) | -45.9 (-55.4 to -36.7) | -42.7 (-64.9 to -12.4) | -42.1 (-51.7 to -35.9) | -22.2 (-58.6 to 19.4) |
| lstdq_v2_s0 | -29.5 (-55.7 to -6.3) | -28.7 (-42.8 to -14.5) | -33.1 (-50.5 to -12.9) | -30.4 (-42.1 to -21.1) | -30.0 (-64.3 to 1.7) |
| qlearn_s0 | 71.9 (-39.1 to 242.3) | -49.8 (-58.9 to -41.2) | -43.5 (-61.3 to -18.4) | -45.9 (-54.8 to -37.5) | 123.4 (-35.2 to 366.9) |

## Gain vs actuated (%, negative = less delay than actuated)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 23.0 (10.9 to 39.3) | 0.0 (0.0 to 0.0) | 1.7 (-1.9 to 6.9) | 4.3 (-1.2 to 10.1) | 33.6 (16.9 to 56.2) |
| actuated | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| webster | 399.9 (135.0 to 811.8) | 119.2 (92.7 to 155.0) | 462.2 (68.9 to 1002.9) | 68.5 (42.7 to 102.9) | 498.3 (148.5 to 1051.6) |
| maxpressure | 7.2 (1.1 to 13.4) | 17.8 (7.7 to 27.1) | 8.9 (-2.2 to 22.7) | -16.9 (-22.9 to -10.8) | 4.2 (-1.6 to 9.7) |
| ars_s0 | 32.6 (12.0 to 62.0) | 9.2 (3.4 to 13.5) | 9.6 (-1.4 to 28.6) | -5.0 (-10.0 to 0.6) | 43.4 (11.9 to 87.4) |
| lstdq_v2_s0 | 31.1 (20.6 to 46.2) | 43.1 (29.6 to 55.4) | 39.2 (33.0 to 46.0) | 14.0 (10.4 to 18.5) | 26.2 (12.1 to 47.6) |
| qlearn_s0 | 172.5 (41.9 to 326.6) | 2.0 (-3.9 to 6.1) | 11.2 (2.8 to 22.0) | -11.3 (-14.0 to -9.1) | 254.0 (59.9 to 471.5) |

## Regret: delay above the best controller in the same hour (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 18.8 (5.5 to 37.8) | 0.6 (0.3 to 0.9) | 1.0 (0.3 to 1.7) | 3.7 (3.0 to 4.4) | 26.9 (8.0 to 53.4) |
| actuated | 2.2 (1.6 to 3.3) | 0.6 (0.3 to 0.9) | 0.7 (0.3 to 1.1) | 2.9 (2.1 to 3.8) | 2.9 (2.2 to 4.3) |
| webster | 145.1 (35.0 to 258.4) | 12.4 (10.6 to 14.5) | 70.8 (10.4 to 159.1) | 14.4 (9.9 to 21.2) | 202.6 (45.8 to 368.0) |
| maxpressure | 6.1 (2.7 to 11.0) | 2.8 (1.8 to 3.8) | 2.1 (0.5 to 3.7) | 0.1 (0.0 to 0.4) | 7.9 (3.0 to 14.6) |
| ars_s0 | 23.2 (6.4 to 52.6) | 1.7 (1.3 to 2.1) | 2.8 (0.3 to 7.5) | 2.0 (0.6 to 3.1) | 32.5 (8.4 to 74.2) |
| lstdq_v2_s0 | 15.9 (6.7 to 28.8) | 5.6 (4.0 to 7.3) | 6.6 (5.1 to 8.1) | 5.3 (4.6 to 6.2) | 20.6 (6.7 to 40.3) |
| qlearn_s0 | 96.2 (24.5 to 193.2) | 0.9 (0.5 to 1.3) | 2.8 (0.9 to 5.9) | 1.0 (0.2 to 2.2) | 140.3 (36.5 to 274.2) |

## Worst-off movement: highest 95th-percentile delay of any movement in the hour (s)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 260.9 (177.3 to 365.9) | 43.7 (41.1 to 46.0) | 67.1 (51.4 to 86.0) | 106.0 (76.0 to 131.8) | 361.2 (245.1 to 502.0) |
| actuated | 152.1 (96.5 to 222.6) | 43.7 (41.1 to 46.0) | 58.2 (50.4 to 62.5) | 64.9 (60.9 to 70.0) | 202.7 (122.2 to 307.1) |
| webster | 608.6 (249.0 to 968.2) | 60.2 (59.8 to 60.5) | 312.3 (60.6 to 651.6) | 106.6 (79.2 to 157.0) | 839.9 (335.7 to 1344.1) |
| maxpressure | 277.7 (184.5 to 385.3) | 102.1 (95.7 to 109.4) | 134.6 (101.6 to 184.2) | 81.2 (74.5 to 90.3) | 360.9 (231.8 to 512.0) |
| ars_s0 | 213.5 (148.6 to 306.0) | 82.5 (73.1 to 90.7) | 98.4 (62.1 to 149.9) | 69.3 (64.5 to 74.3) | 272.9 (184.0 to 404.5) |
| lstdq_v2_s0 | 349.5 (212.7 to 513.2) | 113.6 (105.3 to 122.7) | 154.2 (119.9 to 188.5) | 124.5 (121.9 to 126.5) | 458.7 (263.3 to 701.1) |
| qlearn_s0 | 524.6 (246.2 to 834.9) | 45.2 (38.2 to 52.7) | 107.1 (77.4 to 136.6) | 60.5 (55.3 to 65.6) | 746.2 (347.0 to 1171.8) |

## Hours with a queue reaching the leg end (share of hours with >= 10 vehicles unable to enter)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 0.37 (0.28 to 0.50) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.55 (0.43 to 0.72) |
| actuated | 0.33 (0.22 to 0.48) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.50 (0.33 to 0.70) |
| webster | 0.54 (0.44 to 0.64) | 0.00 (0.00 to 0.00) | 0.23 (0.00 to 0.50) | 0.25 (0.00 to 0.75) | 0.77 (0.64 to 0.91) |
| maxpressure | 0.24 (0.18 to 0.33) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.36 (0.29 to 0.48) |
| ars_s0 | 0.45 (0.36 to 0.55) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.68 (0.54 to 0.82) |
| lstdq_v2_s0 | 0.31 (0.25 to 0.41) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.46 (0.39 to 0.59) |
| qlearn_s0 | 0.45 (0.37 to 0.57) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.68 (0.56 to 0.82) |

## How often each controller is best in an hour

| Controller | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|
| gdot | 41 % | 10 % | 0 % | 1 % |
| actuated | 41 % | 40 % | 0 % | 28 % |
| webster | 0 % | 0 % | 0 % | 1 % |
| maxpressure | 19 % | 10 % | 75 % | 48 % |
| ars_s0 | 15 % | 10 % | 25 % | 16 % |
| lstdq_v2_s0 | 0 % | 0 % | 0 % | 3 % |
| qlearn_s0 | 26 % | 40 % | 0 % | 3 % |
