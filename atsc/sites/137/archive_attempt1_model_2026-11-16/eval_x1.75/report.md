# RQ1 evaluation: strengths and weaknesses by traffic condition (137, validation weekdays, DEMAND SCALED x1.75: a sensitivity experiment on the real profile, not real traffic)

120 clean hours on 5 days x 1 simulation seeds (seed-averaged per hour). Y = sum of critical flow ratios from the field counts. Intervals: 95 % day-bootstrap. **Limitations (137, 2026-11-16):** uncalibrated driver model; GDOT timing not yet field-validated; WB through from the upstream signal 138; EB/WB right turns run as through; P2/P6 stop-bar presence added in the model; coordinated corridor site (138 at ~260 m) modelled isolated; no pedestrian timing (atsc/sites/137/README.md). Main tables: learnt controllers at one training seed (lstdq_v2_s0 = LSTDQ, qlearn_s0, ars_s0); all training seeds of every learner are in the training-seed tables (simulation seed 1).

Hours per condition: light (Y < 0.15) 18, moderate (0.15-0.30) 13, busy (0.30-0.40) 6, heavy (Y >= 0.40) 83

## Overall mean delay, vehicle-weighted (s/veh)

| Controller | mean delay (95 % interval) |
|---|---|
| gdot | 280.5 (93.7 to 509.1) |
| actuated | 169.4 (52.3 to 334.0) |
| webster | 1822.6 (1213.0 to 2481.6) |
| maxpressure | 150.1 (45.6 to 291.5) |
| ars_s0 | 293.4 (78.4 to 594.1) |
| lstdq_v2_s0 | 243.1 (68.2 to 417.9) |
| qlearn_s0 | 223.6 (57.8 to 444.9) |

## Mean delay (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 200.8 (70.5 to 365.3) | 11.6 (11.0 to 12.1) | 12.5 (11.3 to 13.7) | 16.0 (13.4 to 19.0) | 285.4 (97.1 to 516.5) |
| actuated | 124.1 (40.0 to 249.0) | 11.6 (11.0 to 12.1) | 12.5 (11.3 to 13.8) | 15.5 (13.0 to 18.9) | 173.0 (52.4 to 348.6) |
| webster | 1262.3 (896.8 to 1627.8) | 18.9 (18.0 to 19.8) | 29.7 (18.9 to 48.3) | 67.3 (24.3 to 149.4) | 1818.1 (1265.3 to 2371.0) |
| maxpressure | 112.3 (36.8 to 222.1) | 17.4 (16.1 to 18.8) | 14.9 (12.3 to 17.9) | 17.3 (14.0 to 21.6) | 154.2 (45.6 to 308.6) |
| ars_s0 | 215.9 (57.2 to 445.8) | 13.5 (12.6 to 14.3) | 14.2 (11.6 to 17.0) | 23.6 (13.8 to 34.6) | 303.8 (75.9 to 626.8) |
| lstdq_v2_s0 | 176.3 (50.2 to 305.8) | 14.4 (14.0 to 14.8) | 14.0 (12.0 to 16.1) | 19.8 (13.2 to 26.3) | 249.3 (66.2 to 432.4) |
| qlearn_s0 | 163.3 (44.7 to 328.3) | 13.8 (13.2 to 14.4) | 14.0 (12.3 to 15.9) | 18.8 (13.7 to 23.8) | 228.7 (58.4 to 460.3) |

## Gain vs Webster (%, negative = less delay than Webster)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 70.4 (-72.9 to 336.8) | -38.6 (-42.0 to -35.5) | -44.6 (-53.5 to -38.3) | -49.3 (-61.7 to -33.5) | 117.0 (-84.5 to 492.3) |
| actuated | 34.2 (-76.9 to 243.7) | -38.6 (-42.0 to -35.5) | -44.4 (-53.5 to -38.2) | -51.4 (-62.5 to -37.7) | 65.5 (-90.3 to 361.2) |
| webster | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| maxpressure | 27.2 (-71.2 to 209.7) | -7.3 (-14.6 to -0.4) | -35.3 (-43.3 to -28.2) | -46.6 (-59.0 to -30.3) | 46.9 (-89.4 to 305.4) |
| ars_s0 | 163.1 (-72.5 to 550.6) | -28.6 (-32.6 to -24.4) | -39.2 (-48.1 to -30.7) | -34.0 (-52.3 to 0.3) | 245.8 (-89.1 to 796.4) |
| lstdq_v2_s0 | 102.5 (-72.7 to 322.7) | -23.6 (-27.2 to -19.2) | -38.4 (-45.7 to -31.7) | -34.7 (-61.4 to 10.5) | 161.2 (-89.5 to 475.0) |
| qlearn_s0 | 56.0 (-72.7 to 292.0) | -26.2 (-29.0 to -21.5) | -37.7 (-46.8 to -31.8) | -39.7 (-61.5 to -6.2) | 92.0 (-88.5 to 426.4) |

## Gain vs actuated (%, negative = less delay than actuated)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 83.4 (32.8 to 145.4) | 0.0 (0.0 to 0.0) | -0.2 (-0.7 to 0.0) | 3.9 (0.8 to 6.9) | 123.0 (46.2 to 217.4) |
| actuated | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| webster | 2344.3 (1579.8 to 3118.1) | 64.2 (55.8 to 73.7) | 126.5 (63.5 to 242.2) | 264.6 (71.5 to 603.8) | 3325.8 (2283.4 to 4453.0) |
| maxpressure | 10.5 (3.2 to 17.6) | 51.4 (41.8 to 60.9) | 17.5 (8.4 to 26.7) | 11.0 (2.7 to 16.6) | -0.3 (-10.6 to 10.3) |
| ars_s0 | 51.3 (13.7 to 107.4) | 16.3 (13.6 to 18.0) | 11.6 (1.1 to 22.4) | 41.9 (6.5 to 77.2) | 65.7 (7.5 to 152.9) |
| lstdq_v2_s0 | 67.2 (9.2 to 177.4) | 24.3 (17.2 to 32.5) | 12.1 (3.7 to 18.9) | 24.8 (1.8 to 62.7) | 90.1 (4.7 to 254.0) |
| qlearn_s0 | 43.8 (15.6 to 72.1) | 20.0 (15.0 to 25.8) | 12.4 (6.5 to 17.6) | 19.1 (4.3 to 41.0) | 56.0 (15.8 to 96.3) |

## Regret: delay above the best controller in the same hour (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 146.7 (38.0 to 296.4) | 0.0 (0.0 to 0.0) | 0.1 (0.0 to 0.3) | 0.6 (0.3 to 0.9) | 211.8 (56.0 to 421.3) |
| actuated | 69.9 (3.0 to 190.6) | 0.0 (0.0 to 0.0) | 0.2 (0.1 to 0.3) | 0.1 (0.0 to 0.2) | 99.4 (4.5 to 269.7) |
| webster | 1208.2 (837.9 to 1578.4) | 7.4 (6.6 to 8.3) | 17.3 (7.5 to 34.9) | 51.9 (9.7 to 130.6) | 1744.5 (1184.5 to 2304.6) |
| maxpressure | 58.2 (4.4 to 160.3) | 5.9 (4.7 to 7.0) | 2.5 (1.2 to 4.2) | 1.9 (0.6 to 3.0) | 80.6 (4.4 to 224.8) |
| ars_s0 | 161.7 (13.5 to 393.7) | 1.9 (1.5 to 2.2) | 1.9 (0.4 to 3.4) | 8.2 (0.9 to 16.1) | 230.2 (18.0 to 557.5) |
| lstdq_v2_s0 | 122.2 (6.6 to 254.6) | 2.8 (2.1 to 3.6) | 1.7 (0.8 to 2.5) | 4.4 (0.3 to 10.4) | 175.8 (8.3 to 362.7) |
| qlearn_s0 | 109.1 (12.3 to 266.5) | 2.3 (1.7 to 2.9) | 1.6 (0.9 to 2.3) | 3.3 (0.9 to 6.8) | 155.2 (17.3 to 376.7) |

## Worst-off movement: highest 95th-percentile delay of any movement in the hour (s)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 681.2 (288.3 to 1172.9) | 41.2 (36.1 to 46.3) | 50.3 (45.3 to 57.1) | 107.2 (85.5 to 119.8) | 963.0 (397.8 to 1675.9) |
| actuated | 428.8 (161.1 to 762.8) | 41.2 (36.1 to 46.3) | 50.3 (45.3 to 57.1) | 75.4 (69.1 to 84.7) | 598.8 (213.4 to 1081.2) |
| webster | 3380.1 (2718.7 to 4041.5) | 51.2 (46.5 to 55.8) | 141.7 (49.8 to 304.5) | 339.2 (94.7 to 821.8) | 4830.2 (3795.2 to 5865.2) |
| maxpressure | 507.2 (248.1 to 766.3) | 91.0 (81.5 to 98.8) | 108.0 (96.6 to 127.1) | 119.1 (98.8 to 139.4) | 692.7 (316.7 to 1068.8) |
| ars_s0 | 660.0 (280.3 to 1147.1) | 53.7 (43.5 to 63.6) | 86.2 (75.9 to 102.2) | 211.0 (91.2 to 330.7) | 911.9 (356.9 to 1596.9) |
| lstdq_v2_s0 | 698.2 (315.9 to 1052.6) | 60.2 (51.2 to 71.7) | 65.7 (60.3 to 71.1) | 141.9 (85.1 to 242.6) | 983.6 (427.9 to 1516.8) |
| qlearn_s0 | 1383.8 (452.9 to 2575.1) | 42.7 (36.1 to 49.8) | 60.9 (48.6 to 78.3) | 114.7 (68.4 to 172.9) | 1974.9 (636.6 to 3642.1) |

## Hours with a queue reaching the leg end (share of hours with >= 10 vehicles unable to enter)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 0.59 (0.54 to 0.63) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.86 (0.79 to 0.93) |
| actuated | 0.57 (0.50 to 0.64) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.82 (0.72 to 0.93) |
| webster | 0.64 (0.57 to 0.71) | 0.00 (0.00 to 0.00) | 0.05 (0.00 to 0.15) | 0.38 (0.00 to 0.75) | 0.89 (0.80 to 0.96) |
| maxpressure | 0.62 (0.59 to 0.67) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.91 (0.84 to 0.96) |
| ars_s0 | 0.57 (0.51 to 0.65) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.83 (0.73 to 0.94) |
| lstdq_v2_s0 | 0.55 (0.47 to 0.64) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.80 (0.67 to 0.93) |
| qlearn_s0 | 0.47 (0.38 to 0.57) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.68 (0.55 to 0.81) |

## How often each controller is best in an hour

| Controller | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|
| gdot | 89 % | 69 % | 17 % | 1 % |
| actuated | 89 % | 62 % | 33 % | 30 % |
| webster | 0 % | 0 % | 0 % | 6 % |
| maxpressure | 0 % | 8 % | 0 % | 28 % |
| ars_s0 | 11 % | 8 % | 33 % | 11 % |
| lstdq_v2_s0 | 0 % | 8 % | 0 % | 8 % |
| qlearn_s0 | 0 % | 8 % | 17 % | 16 % |
