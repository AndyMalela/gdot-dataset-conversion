# RQ1 evaluation: strengths and weaknesses by traffic condition (7065, validation weekdays)

471 clean hours on 20 days x 3 simulation seeds (seed-averaged per hour). Y = sum of critical flow ratios from the field counts. Intervals: 95 % day-bootstrap. **Limitations:** isolated model of a signal in GDOT's coordinated Peachtree group (field plan charged coordination's cost without its benefit); P2 count suspect (~half its neighbours'); right turns uncounted. Main tables: learnt controllers at one training seed (lstdq = v1 seed 0); all training seeds of every learner are in the training-seed tables (simulation seed 1).

Hours per condition: light (Y < 0.15) 128, moderate (0.15-0.30) 72, busy (0.30-0.40) 186, heavy (Y >= 0.40) 85

## Overall mean delay, vehicle-weighted (s/veh)

| Controller | mean delay (95 % interval) |
|---|---|
| gdot | 50.3 (47.5 to 53.8) |
| actuated | 40.8 (39.8 to 41.9) |
| webster | 40.0 (38.1 to 42.1) |
| maxpressure | 34.8 (33.4 to 36.5) |
| lstdq | 36.5 (35.4 to 37.8) |

## Learners over training seeds (overall vehicle-weighted delay, simulation seed 1, s/veh)

| Learner | training seeds | median | min | max | per seed |
|---|---|---|---|---|---|
| ars | 5 | 34.9 | 34.7 | 35.1 | ars_s0 34.9, ars_s1 34.8, ars_s2 34.9, ars_s3 34.7, ars_s4 35.1 |
| lstdq v1 | 5 | 36.0 | 34.2 | 36.9 | lstdq 36.3, lstdq_s1 36.9, lstdq_s2 35.5, lstdq_s3 36.0, lstdq_s4 34.2 |
| lstdq v2 | 5 | 34.9 | 34.5 | 37.4 | lstdq_v2_s0 34.9, lstdq_v2_s1 34.5, lstdq_v2_s2 37.4, lstdq_v2_s3 35.2, lstdq_v2_s4 34.5 |
| lstdq v2f | 5 | 34.1 | 33.5 | 35.3 | lstdq_v2f_s0 34.1, lstdq_v2f_s1 33.9, lstdq_v2f_s2 33.5, lstdq_v2f_s3 35.3, lstdq_v2f_s4 34.2 |
| nfq | 5 | 69.9 | 66.6 | 75.0 | nfq_s0 68.0, nfq_s1 70.6, nfq_s2 75.0, nfq_s3 69.9, nfq_s4 66.6 |
| nfq_conv | 5 | 49.3 | 47.3 | 66.4 | nfq_conv_s0 49.3, nfq_conv_s1 47.3, nfq_conv_s2 66.4, nfq_conv_s3 52.6, nfq_conv_s4 49.2 |
| qlearn | 5 | 39.3 | 36.9 | 64.1 | qlearn_s0 38.2, qlearn_s1 36.9, qlearn_s2 45.3, qlearn_s3 64.1, qlearn_s4 39.3 |
| maxpressure (reference) | - | 34.5 | | | |
| webster (reference) | - | 40.1 | | | |
| actuated (reference) | - | 40.8 | | | |

## Learners over training seeds by condition (mean delay, s/veh, simulation seed 1; median, min to max)

| Learner | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|
| ars | 26.6 (26.5 to 26.7) | 30.7 (30.6 to 30.8) | 33.3 (33.2 to 33.3) | 40.6 (40.2 to 41.3) |
| lstdq v1 | 26.9 (26.5 to 27.4) | 31.5 (31.1 to 32.0) | 35.2 (33.7 to 36.0) | 40.9 (37.9 to 42.4) |
| lstdq v2 | 31.1 (30.2 to 34.7) | 32.9 (32.3 to 34.9) | 33.9 (33.4 to 34.8) | 37.8 (37.5 to 43.0) |
| lstdq v2f | 30.7 (27.5 to 31.4) | 31.4 (30.6 to 32.5) | 33.0 (32.8 to 34.2) | 37.3 (37.2 to 39.0) |
| nfq | 42.7 (40.8 to 51.4) | 55.4 (53.0 to 55.8) | 61.4 (61.0 to 63.5) | 94.9 (86.1 to 108.8) |
| nfq_conv | 44.6 (33.7 to 49.1) | 42.7 (36.1 to 52.6) | 45.6 (39.8 to 60.4) | 64.2 (58.3 to 89.6) |
| qlearn | 26.6 (26.4 to 28.1) | 30.9 (30.5 to 46.3) | 34.6 (33.2 to 44.9) | 52.9 (47.9 to 111.2) |
| maxpressure | 26.6 | 31.0 | 33.1 | 39.6 |
| webster | 42.3 | 33.1 | 37.2 | 47.5 |
| actuated | 27.7 | 35.7 | 40.1 | 46.5 |

471 clean hours run by every controller with simulation seed 1.

## Learners over training seeds by condition (worst-off movement p95 delay, s, simulation seed 1; median, min to max)

| Learner | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|
| ars | 95.4 (94.7 to 95.4) | 107.2 (105.8 to 109.0) | 126.4 (125.7 to 127.4) | 192.2 (191.5 to 193.4) |
| lstdq v1 | 96.9 (95.2 to 101.7) | 103.1 (102.3 to 105.2) | 110.4 (110.0 to 113.4) | 136.6 (130.7 to 147.2) |
| lstdq v2 | 118.7 (112.2 to 134.5) | 110.1 (107.7 to 149.8) | 107.7 (107.4 to 127.7) | 134.0 (127.9 to 197.0) |
| lstdq v2f | 118.6 (101.8 to 119.3) | 106.0 (101.7 to 108.2) | 105.6 (104.2 to 114.3) | 133.6 (126.9 to 144.3) |
| nfq | 143.3 (139.3 to 159.8) | 160.0 (157.0 to 161.5) | 190.2 (183.0 to 197.2) | 300.6 (270.3 to 339.2) |
| nfq_conv | 137.6 (107.4 to 161.3) | 145.7 (115.6 to 156.2) | 147.2 (141.5 to 196.5) | 245.4 (191.5 to 291.4) |
| qlearn | 95.5 (95.1 to 100.1) | 101.0 (99.8 to 165.7) | 120.6 (117.9 to 160.2) | 209.0 (195.2 to 366.8) |
| maxpressure | 95.3 | 110.3 | 122.3 | 199.8 |
| webster | 163.6 | 128.1 | 213.9 | 331.5 |
| actuated | 98.3 | 111.3 | 117.5 | 145.8 |

471 clean hours run by every controller with simulation seed 1.

## Mean delay (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 44.3 (42.5 to 46.6) | 29.8 (29.4 to 30.3) | 36.0 (35.6 to 36.5) | 46.0 (45.6 to 46.7) | 68.9 (60.1 to 79.0) |
| actuated | 37.3 (36.7 to 38.0) | 27.9 (27.5 to 28.4) | 35.6 (35.2 to 36.0) | 40.1 (39.9 to 40.3) | 46.6 (43.5 to 49.8) |
| webster | 39.7 (38.6 to 40.9) | 41.9 (40.8 to 43.0) | 33.2 (32.6 to 34.1) | 36.9 (35.9 to 38.0) | 48.0 (42.9 to 54.0) |
| maxpressure | 32.4 (31.6 to 33.5) | 26.7 (26.3 to 27.2) | 31.0 (30.4 to 31.8) | 33.3 (32.8 to 33.9) | 40.5 (36.5 to 45.0) |
| lstdq | 33.7 (33.0 to 34.5) | 26.6 (26.3 to 26.9) | 31.5 (31.2 to 31.9) | 35.4 (35.2 to 35.6) | 42.4 (39.1 to 46.0) |

## Gain vs Webster (%, negative = less delay than Webster)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 14.0 (11.7 to 17.1) | -27.0 (-29.0 to -24.5) | 8.9 (7.1 to 10.4) | 27.2 (25.3 to 29.3) | 49.7 (40.9 to 62.0) |
| actuated | -2.2 (-3.0 to -1.3) | -31.3 (-33.3 to -28.7) | 8.4 (6.3 to 10.1) | 11.2 (9.5 to 12.8) | 3.1 (-0.3 to 6.1) |
| webster | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| maxpressure | -16.2 (-16.8 to -15.7) | -34.9 (-36.4 to -32.9) | -6.4 (-7.1 to -5.6) | -8.4 (-9.4 to -7.3) | -14.1 (-16.8 to -11.7) |
| lstdq | -12.0 (-12.9 to -11.1) | -34.9 (-36.7 to -32.7) | -4.1 (-6.0 to -2.6) | -1.9 (-3.3 to -0.5) | -6.8 (-9.7 to -3.8) |

## Gain vs actuated (%, negative = less delay than actuated)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 16.3 (14.3 to 18.8) | 7.2 (6.3 to 8.0) | 1.2 (-0.1 to 2.4) | 14.7 (13.5 to 15.9) | 45.9 (36.7 to 56.9) |
| actuated | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| webster | 9.8 (8.4 to 11.3) | 52.1 (47.2 to 56.0) | -6.7 (-8.8 to -4.0) | -8.2 (-10.5 to -5.7) | -0.1 (-4.0 to 4.4) |
| maxpressure | -12.7 (-13.6 to -11.6) | -4.2 (-5.2 to -3.1) | -13.0 (-14.4 to -10.8) | -17.2 (-18.0 to -16.1) | -15.3 (-17.9 to -12.0) |
| lstdq | -9.4 (-9.7 to -9.0) | -4.6 (-5.4 to -3.7) | -11.4 (-11.9 to -11.0) | -11.8 (-12.0 to -11.5) | -9.5 (-10.7 to -8.1) |

## Regret: delay above the best controller in the same hour (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 12.6 (11.3 to 14.2) | 3.8 (3.5 to 4.0) | 5.4 (5.0 to 5.8) | 13.1 (12.6 to 13.6) | 30.6 (24.1 to 37.8) |
| actuated | 5.6 (5.5 to 5.8) | 1.9 (1.7 to 2.1) | 5.0 (4.8 to 5.3) | 7.2 (7.0 to 7.3) | 8.2 (7.5 to 8.9) |
| webster | 8.0 (7.2 to 8.7) | 15.8 (14.6 to 16.9) | 2.6 (2.0 to 3.5) | 4.0 (3.1 to 4.9) | 9.7 (6.6 to 13.4) |
| maxpressure | 0.7 (0.2 to 1.4) | 0.6 (0.4 to 0.9) | 0.4 (0.0 to 1.0) | 0.3 (0.0 to 0.7) | 2.1 (0.1 to 4.9) |
| lstdq | 2.0 (1.8 to 2.2) | 0.5 (0.4 to 0.7) | 1.0 (0.8 to 1.1) | 2.4 (2.3 to 2.6) | 4.0 (3.1 to 5.0) |

## Worst-off movement: highest 95th-percentile delay of any movement in the hour (s)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 149.6 (141.0 to 159.6) | 111.2 (109.8 to 112.9) | 118.1 (116.8 to 119.6) | 143.8 (139.7 to 149.5) | 246.2 (204.5 to 292.7) |
| actuated | 121.1 (116.7 to 126.1) | 103.4 (102.5 to 104.3) | 114.4 (113.7 to 115.1) | 120.2 (118.6 to 122.7) | 154.7 (133.4 to 177.0) |
| webster | 231.0 (214.5 to 249.5) | 173.2 (164.6 to 185.2) | 141.4 (125.3 to 166.0) | 237.6 (218.1 to 257.6) | 382.4 (322.4 to 452.9) |
| maxpressure | 141.8 (129.6 to 154.3) | 99.0 (96.2 to 103.9) | 112.7 (102.7 to 129.7) | 138.9 (126.3 to 152.8) | 239.8 (187.7 to 293.9) |
| lstdq | 115.7 (110.9 to 121.1) | 100.8 (100.1 to 101.7) | 105.2 (104.3 to 106.2) | 112.8 (111.2 to 115.1) | 152.2 (128.1 to 177.8) |

## Hours with a queue reaching the leg end (share of hours with >= 10 vehicles unable to enter)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 0.13 (0.10 to 0.16) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.04 (0.02 to 0.06) | 0.64 (0.49 to 0.78) |
| actuated | 0.03 (0.01 to 0.06) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.01 (0.00 to 0.02) | 0.16 (0.07 to 0.26) |
| webster | 0.05 (0.02 to 0.07) | 0.00 (0.00 to 0.00) | 0.01 (0.00 to 0.04) | 0.04 (0.01 to 0.07) | 0.16 (0.08 to 0.24) |
| maxpressure | 0.03 (0.01 to 0.05) | 0.00 (0.00 to 0.00) | 0.01 (0.00 to 0.04) | 0.01 (0.00 to 0.03) | 0.14 (0.06 to 0.24) |
| lstdq | 0.03 (0.01 to 0.05) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.01 (0.00 to 0.02) | 0.15 (0.06 to 0.25) |

## How often each controller is best in an hour

| Controller | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|
| gdot | 0 % | 0 % | 0 % | 0 % |
| actuated | 9 % | 0 % | 0 % | 0 % |
| webster | 0 % | 3 % | 1 % | 1 % |
| maxpressure | 47 % | 76 % | 96 % | 89 % |
| lstdq | 44 % | 21 % | 3 % | 9 % |
