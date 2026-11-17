# RQ1 evaluation: strengths and weaknesses by traffic condition (137, validation weekdays, DEMAND SCALED x2.5: a sensitivity experiment on the real profile, not real traffic)

120 clean hours on 5 days x 1 simulation seeds (seed-averaged per hour). Y = sum of critical flow ratios from the field counts. Intervals: 95 % day-bootstrap. **Limitations (137, 2026-11-16):** uncalibrated driver model; GDOT timing not yet field-validated; WB through from the upstream signal 138; EB/WB right turns run as through; P2/P6 stop-bar presence added in the model; coordinated corridor site (138 at ~260 m) modelled isolated; no pedestrian timing (atsc/sites/137/README.md). Main tables: learnt controllers at one training seed (lstdq_v2_s0 = LSTDQ, qlearn_s0, ars_s0); all training seeds of every learner are in the training-seed tables (simulation seed 1).

Hours per condition: light (Y < 0.15) 10, moderate (0.15-0.30) 17, busy (0.30-0.40) 4, heavy (Y >= 0.40) 89

## Overall mean delay, vehicle-weighted (s/veh)

| Controller | mean delay (95 % interval) |
|---|---|
| gdot | 6256.8 (5735.3 to 6797.6) |
| actuated | 5949.6 (5428.3 to 6478.4) |
| webster | 8441.7 (8082.7 to 8800.6) |
| maxpressure | 7655.0 (7067.4 to 8242.6) |
| ars_s0 | 7368.9 (6842.5 to 7881.1) |
| lstdq_v2_s0 | 6676.0 (6102.4 to 7250.5) |
| qlearn_s0 | 6396.1 (5953.7 to 6844.8) |

## Mean delay (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 4585.4 (4219.5 to 4956.8) | 9.5 (7.2 to 11.9) | 13.0 (11.3 to 15.4) | 339.0 (16.2 to 983.1) | 6164.7 (5621.6 to 6707.7) |
| actuated | 4353.3 (3985.4 to 4721.3) | 9.5 (7.2 to 11.9) | 13.0 (11.3 to 15.4) | 337.8 (16.2 to 979.6) | 5852.1 (5309.5 to 6394.7) |
| webster | 6135.7 (5875.9 to 6391.8) | 25.0 (23.2 to 27.1) | 28.5 (26.4 to 30.5) | 482.3 (32.1 to 1378.4) | 8239.8 (7825.6 to 8654.0) |
| maxpressure | 5597.3 (5143.9 to 6031.0) | 11.6 (8.8 to 14.4) | 26.0 (13.0 to 42.0) | 494.3 (16.7 to 1448.9) | 7517.3 (6852.3 to 8159.2) |
| ars_s0 | 5413.6 (5047.6 to 5773.8) | 10.7 (8.5 to 13.1) | 16.1 (12.0 to 22.3) | 482.1 (16.0 to 1412.1) | 7272.3 (6724.7 to 7822.8) |
| lstdq_v2_s0 | 4830.9 (4414.3 to 5242.3) | 11.3 (9.1 to 13.5) | 14.7 (12.5 to 17.3) | 345.2 (16.4 to 1002.5) | 6497.5 (5880.6 to 7114.4) |
| qlearn_s0 | 4652.0 (4346.6 to 4962.2) | 9.5 (7.4 to 11.9) | 30.2 (11.9 to 62.8) | 345.9 (15.9 to 1005.3) | 6249.4 (5786.3 to 6722.6) |

## Gain vs Webster (%, negative = less delay than Webster)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | -36.6 (-38.9 to -34.2) | -62.1 (-69.7 to -54.5) | -53.0 (-58.7 to -45.8) | -47.2 (-51.6 to -40.5) | -30.3 (-33.0 to -28.3) |
| actuated | -38.9 (-41.0 to -36.9) | -62.1 (-69.7 to -54.5) | -53.0 (-58.7 to -45.8) | -47.3 (-51.6 to -40.6) | -33.5 (-35.9 to -31.6) |
| webster | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| maxpressure | -8.2 (-19.4 to 10.7) | -53.0 (-64.3 to -39.4) | -7.1 (-51.1 to 42.6) | -19.7 (-52.8 to 41.8) | -5.5 (-12.5 to 7.0) |
| ars_s0 | -23.2 (-26.5 to -18.4) | -57.0 (-65.6 to -48.4) | -42.5 (-55.7 to -24.0) | -39.1 (-50.3 to -16.8) | -16.0 (-17.6 to -14.5) |
| lstdq_v2_s0 | -31.9 (-33.6 to -29.8) | -54.8 (-63.2 to -46.5) | -46.8 (-55.4 to -38.1) | -46.9 (-54.9 to -36.8) | -26.2 (-29.4 to -24.1) |
| qlearn_s0 | -21.7 (-35.4 to 3.3) | -62.2 (-69.3 to -55.2) | 4.4 (-56.5 to 110.1) | -35.3 (-56.5 to -0.8) | -26.6 (-28.7 to -22.8) |

## Gain vs actuated (%, negative = less delay than actuated)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 3.3 (3.1 to 3.6) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.1 (0.0 to 0.2) | 4.4 (4.1 to 4.9) |
| actuated | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| webster | 92.3 (76.0 to 115.2) | 183.1 (121.2 to 257.7) | 134.8 (103.3 to 165.3) | 93.6 (75.8 to 106.7) | 72.8 (62.9 to 88.3) |
| maxpressure | 56.5 (34.8 to 87.8) | 24.5 (-0.3 to 49.3) | 74.5 (14.4 to 136.0) | 54.6 (-2.5 to 163.3) | 52.1 (35.4 to 78.8) |
| ars_s0 | 26.2 (21.3 to 31.0) | 14.4 (6.8 to 23.0) | 17.1 (5.7 to 33.0) | 13.5 (-1.4 to 39.0) | 28.5 (25.4 to 31.4) |
| lstdq_v2_s0 | 15.5 (9.8 to 21.3) | 21.3 (11.9 to 33.7) | 13.7 (7.7 to 24.3) | 0.7 (-6.8 to 7.5) | 15.2 (9.6 to 20.7) |
| qlearn_s0 | 29.1 (7.8 to 64.3) | 0.4 (-3.2 to 4.9) | 84.6 (2.8 to 223.2) | 25.4 (-10.1 to 84.3) | 14.7 (7.5 to 22.7) |

## Regret: delay above the best controller in the same hour (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 484.6 (440.4 to 557.8) | 0.3 (0.0 to 0.5) | 0.4 (0.2 to 0.6) | 1.8 (0.2 to 3.5) | 652.7 (597.3 to 746.5) |
| actuated | 252.5 (187.7 to 327.7) | 0.3 (0.0 to 0.5) | 0.4 (0.2 to 0.6) | 0.7 (0.0 to 1.8) | 340.1 (253.6 to 436.7) |
| webster | 2034.9 (1873.1 to 2202.7) | 15.8 (13.9 to 17.7) | 15.9 (13.5 to 18.2) | 145.2 (16.2 to 398.8) | 2727.8 (2516.3 to 2944.0) |
| maxpressure | 1496.5 (1323.3 to 1653.3) | 2.3 (0.4 to 4.3) | 13.3 (2.2 to 27.1) | 157.1 (0.7 to 469.3) | 2005.4 (1775.3 to 2215.0) |
| ars_s0 | 1312.8 (1234.0 to 1399.5) | 1.5 (1.1 to 1.8) | 3.5 (1.2 to 7.2) | 145.0 (0.0 to 432.5) | 1760.4 (1652.6 to 1872.3) |
| lstdq_v2_s0 | 730.1 (598.0 to 835.6) | 2.0 (1.6 to 2.5) | 2.1 (1.3 to 3.4) | 8.0 (0.5 to 22.9) | 985.5 (802.5 to 1138.8) |
| qlearn_s0 | 551.2 (464.6 to 638.6) | 0.2 (0.0 to 0.4) | 17.6 (0.9 to 47.9) | 8.8 (0.0 to 25.7) | 737.4 (622.2 to 851.1) |

## Worst-off movement: highest 95th-percentile delay of any movement in the hour (s)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 9797.8 (9241.4 to 10354.2) | 43.3 (38.6 to 48.1) | 53.2 (49.6 to 57.6) | 811.8 (64.3 to 2304.7) | 13149.3 (12338.8 to 13919.9) |
| actuated | 9643.8 (9077.6 to 10210.0) | 43.3 (38.6 to 48.1) | 53.2 (49.6 to 57.6) | 811.8 (64.3 to 2304.7) | 12938.7 (12182.8 to 13694.5) |
| webster | 13573.5 (12456.7 to 14477.4) | 67.2 (61.0 to 77.7) | 78.3 (68.1 to 88.0) | 846.2 (79.6 to 2357.9) | 18249.2 (16702.9 to 19689.6) |
| maxpressure | 17701.5 (17019.4 to 18607.1) | 89.3 (74.0 to 100.5) | 216.6 (106.2 to 350.5) | 939.5 (104.8 to 2593.7) | 23748.3 (22953.8 to 24819.6) |
| ars_s0 | 12536.4 (11827.7 to 13308.7) | 55.1 (51.0 to 59.2) | 87.9 (57.1 to 137.5) | 812.3 (61.4 to 2305.7) | 16812.3 (16074.8 to 17715.3) |
| lstdq_v2_s0 | 14994.4 (14632.8 to 15370.4) | 48.3 (44.1 to 52.6) | 67.9 (58.6 to 78.7) | 841.9 (63.8 to 2357.5) | 20161.5 (19487.4 to 20990.9) |
| qlearn_s0 | 12688.1 (12380.9 to 13011.0) | 44.5 (40.7 to 49.0) | 180.7 (60.2 to 394.3) | 889.0 (57.9 to 2470.9) | 17002.2 (16588.2 to 17416.1) |

## Hours with a queue reaching the leg end (share of hours with >= 10 vehicles unable to enter)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 0.75 (0.75 to 0.75) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.17 (0.00 to 0.50) | 1.00 (1.00 to 1.00) |
| actuated | 0.75 (0.75 to 0.75) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.17 (0.00 to 0.50) | 1.00 (1.00 to 1.00) |
| webster | 0.78 (0.76 to 0.79) | 0.00 (0.00 to 0.00) | 0.14 (0.00 to 0.34) | 0.33 (0.00 to 1.00) | 1.00 (1.00 to 1.00) |
| maxpressure | 0.78 (0.75 to 0.81) | 0.00 (0.00 to 0.00) | 0.08 (0.00 to 0.24) | 0.33 (0.00 to 1.00) | 1.00 (1.00 to 1.00) |
| ars_s0 | 0.77 (0.75 to 0.78) | 0.00 (0.00 to 0.00) | 0.04 (0.00 to 0.12) | 0.33 (0.00 to 1.00) | 1.00 (1.00 to 1.00) |
| lstdq_v2_s0 | 0.74 (0.72 to 0.75) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.17 (0.00 to 0.50) | 0.99 (0.96 to 1.00) |
| qlearn_s0 | 0.78 (0.75 to 0.81) | 0.00 (0.00 to 0.00) | 0.08 (0.00 to 0.24) | 0.33 (0.00 to 1.00) | 1.00 (1.00 to 1.00) |

## How often each controller is best in an hour

| Controller | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|
| gdot | 40 % | 41 % | 25 % | 11 % |
| actuated | 40 % | 41 % | 50 % | 48 % |
| webster | 0 % | 0 % | 0 % | 2 % |
| maxpressure | 10 % | 6 % | 0 % | 0 % |
| ars_s0 | 0 % | 0 % | 25 % | 0 % |
| lstdq_v2_s0 | 0 % | 6 % | 0 % | 29 % |
| qlearn_s0 | 50 % | 47 % | 25 % | 9 % |
