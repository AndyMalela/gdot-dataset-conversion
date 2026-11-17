# RQ1 evaluation: strengths and weaknesses by traffic condition (137, validation weekdays, DEMAND SCALED x2.5: a sensitivity experiment on the real profile, not real traffic)

120 clean hours on 5 days x 1 simulation seeds (seed-averaged per hour). Y = sum of critical flow ratios from the field counts. Intervals: 95 % day-bootstrap. **Limitations (137, 2026-11-16):** uncalibrated driver model; GDOT timing not yet field-validated; WB through from the upstream signal 138; EB/WB right turns run as through; P2/P6 stop-bar presence added in the model; coordinated corridor site (138 at ~260 m) modelled isolated; no pedestrian timing (atsc/sites/137/README.md). Main tables: learnt controllers at one training seed (lstdq_v2_s0 = LSTDQ, qlearn_s0, ars_s0); all training seeds of every learner are in the training-seed tables (simulation seed 1).

Hours per condition: light (Y < 0.15) 10, moderate (0.15-0.30) 17, busy (0.30-0.40) 4, heavy (Y >= 0.40) 89

## Overall mean delay, vehicle-weighted (s/veh)

| Controller | mean delay (95 % interval) |
|---|---|
| gdot | 5261.0 (4954.0 to 5567.9) |
| actuated | 5004.9 (4700.3 to 5309.6) |
| webster | 5662.9 (5531.6 to 5797.8) |
| maxpressure | 5284.8 (4578.1 to 5991.5) |
| ars_s0 | 5361.1 (5173.0 to 5516.8) |
| lstdq_v2_s0 | 5361.7 (5073.0 to 5647.9) |
| qlearn_s0 | 7441.3 (7176.7 to 7812.4) |

## Mean delay (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 3595.5 (3401.9 to 3776.8) | 11.2 (9.8 to 12.6) | 14.5 (12.5 to 16.8) | 20.4 (14.8 to 29.4) | 4844.8 (4543.0 to 5086.3) |
| actuated | 3417.0 (3217.9 to 3591.7) | 11.2 (9.8 to 12.6) | 14.5 (12.5 to 16.8) | 19.1 (14.8 to 25.5) | 4603.8 (4325.9 to 4832.8) |
| webster | 3897.2 (3807.2 to 4010.9) | 24.1 (22.7 to 25.8) | 27.6 (25.5 to 29.5) | 315.1 (29.9 to 880.8) | 5227.0 (5095.8 to 5372.4) |
| maxpressure | 3722.5 (3304.4 to 4113.0) | 12.3 (9.6 to 15.0) | 19.5 (13.4 to 26.4) | 33.2 (14.5 to 68.2) | 5021.9 (4435.2 to 5608.7) |
| ars_s0 | 3614.8 (3455.9 to 3782.5) | 11.6 (10.1 to 13.0) | 31.5 (12.8 to 66.1) | 35.4 (15.2 to 75.1) | 4861.5 (4691.4 to 5044.3) |
| lstdq_v2_s0 | 3694.7 (3513.8 to 3851.7) | 14.2 (12.0 to 17.2) | 30.2 (16.9 to 47.5) | 204.7 (19.6 to 574.5) | 4962.3 (4720.1 to 5167.0) |
| qlearn_s0 | 4992.3 (4612.1 to 5305.1) | 10.9 (9.2 to 12.5) | 25.6 (12.2 to 49.0) | 30.7 (14.4 to 62.3) | 6714.6 (6343.2 to 7059.3) |

## Gain vs Webster (%, negative = less delay than Webster)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 26.7 (-19.8 to 81.4) | -53.4 (-58.6 to -47.4) | -46.0 (-52.1 to -39.1) | -58.2 (-73.0 to -50.5) | 52.6 (-7.1 to 123.5) |
| actuated | -3.1 (-22.7 to 23.2) | -53.4 (-58.6 to -47.4) | -46.0 (-52.1 to -39.1) | -58.2 (-73.2 to -50.5) | 12.7 (-11.0 to 46.8) |
| webster | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| maxpressure | 88.8 (-6.6 to 228.4) | -48.6 (-59.4 to -36.7) | -27.9 (-48.6 to -6.0) | -37.9 (-57.8 to -11.7) | 129.3 (4.9 to 310.0) |
| ars_s0 | 12.1 (-13.7 to 38.0) | -51.8 (-57.7 to -46.1) | 12.9 (-49.6 to 128.0) | -55.2 (-62.9 to -49.1) | 16.8 (-8.3 to 45.8) |
| lstdq_v2_s0 | 77.2 (-9.6 to 226.9) | -40.2 (-50.1 to -24.6) | 11.8 (-34.2 to 68.0) | -31.0 (-41.7 to -16.8) | 103.8 (-7.6 to 299.4) |
| qlearn_s0 | 105.6 (5.8 to 213.9) | -54.7 (-61.0 to -47.7) | -7.9 (-54.0 to 70.1) | -48.7 (-55.1 to -39.3) | 146.6 (16.1 to 299.9) |

## Gain vs actuated (%, negative = less delay than actuated)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 10.8 (3.5 to 20.7) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 6.7 (0.0 to 20.2) | 14.1 (4.7 to 27.3) |
| actuated | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| webster | 127.4 (34.5 to 298.5) | 118.7 (93.2 to 143.6) | 102.7 (77.6 to 128.0) | 1505.6 (102.0 to 4310.7) | 40.7 (18.1 to 75.1) |
| maxpressure | 50.4 (29.8 to 76.5) | 8.8 (-2.2 to 20.8) | 26.5 (4.4 to 52.3) | 49.2 (-13.9 to 148.8) | 56.9 (32.6 to 92.4) |
| ars_s0 | 30.1 (8.9 to 57.5) | 3.8 (-5.3 to 13.3) | 77.1 (1.5 to 217.5) | 80.2 (-5.3 to 243.1) | 13.6 (4.0 to 24.7) |
| lstdq_v2_s0 | 85.6 (21.0 to 176.1) | 27.0 (14.6 to 41.8) | 84.7 (34.3 to 146.3) | 935.8 (19.1 to 2756.1) | 30.8 (5.8 to 68.7) |
| qlearn_s0 | 77.4 (48.6 to 112.8) | -2.9 (-10.4 to 2.1) | 49.7 (-4.1 to 144.2) | 46.4 (-8.3 to 150.1) | 86.7 (55.5 to 136.8) |

## Regret: delay above the best controller in the same hour (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 1086.5 (973.3 to 1213.8) | 0.6 (0.2 to 1.2) | 1.1 (0.7 to 1.3) | 2.2 (0.4 to 4.0) | 1468.5 (1297.5 to 1678.5) |
| actuated | 907.9 (807.4 to 1016.7) | 0.6 (0.2 to 1.2) | 1.1 (0.7 to 1.3) | 0.9 (0.0 to 2.4) | 1227.5 (1076.1 to 1407.0) |
| webster | 1388.2 (1260.5 to 1515.3) | 13.5 (11.3 to 14.9) | 14.2 (11.9 to 16.4) | 296.9 (15.5 to 855.3) | 1850.6 (1675.7 to 2022.8) |
| maxpressure | 1213.4 (803.9 to 1623.0) | 1.7 (0.8 to 2.9) | 6.1 (2.1 to 10.5) | 15.0 (0.0 to 42.8) | 1645.6 (1069.3 to 2242.2) |
| ars_s0 | 1105.8 (953.6 to 1246.6) | 1.0 (0.5 to 1.7) | 18.1 (1.4 to 49.8) | 17.3 (0.8 to 49.6) | 1485.2 (1278.2 to 1677.2) |
| lstdq_v2_s0 | 1185.6 (1099.4 to 1312.4) | 3.7 (2.0 to 5.3) | 16.8 (5.7 to 31.5) | 186.6 (5.2 to 549.0) | 1585.9 (1462.2 to 1773.5) |
| qlearn_s0 | 2483.2 (2190.2 to 2733.0) | 0.3 (0.0 to 0.6) | 12.2 (0.8 to 33.2) | 12.6 (0.0 to 36.8) | 3338.3 (3009.0 to 3637.7) |

## Worst-off movement: highest 95th-percentile delay of any movement in the hour (s)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 8509.1 (8089.0 to 8960.6) | 43.9 (40.2 to 49.1) | 55.4 (52.2 to 58.6) | 94.6 (58.0 to 163.8) | 11455.1 (10800.2 to 12041.4) |
| actuated | 8427.8 (8069.1 to 8832.2) | 43.9 (40.2 to 49.1) | 55.4 (52.2 to 58.6) | 99.7 (58.0 to 179.0) | 11339.4 (11054.5 to 11796.5) |
| webster | 9870.0 (8954.8 to 10480.9) | 65.6 (60.2 to 76.2) | 77.6 (66.1 to 89.1) | 680.8 (76.7 to 1863.6) | 13257.5 (11978.6 to 14254.7) |
| maxpressure | 14771.1 (13878.1 to 15922.8) | 100.0 (89.6 to 108.9) | 150.2 (114.6 to 185.8) | 250.4 (116.6 to 487.0) | 19857.3 (18675.7 to 21181.2) |
| ars_s0 | 9475.9 (8934.2 to 10017.7) | 69.3 (56.2 to 80.9) | 193.6 (71.9 to 406.2) | 767.4 (62.6 to 2149.8) | 12680.6 (11857.9 to 13500.3) |
| lstdq_v2_s0 | 9656.4 (9303.1 to 10018.7) | 101.3 (93.2 to 110.4) | 224.4 (122.3 to 350.8) | 657.9 (147.0 to 1641.8) | 12934.8 (12339.1 to 13684.9) |
| qlearn_s0 | 11340.8 (10917.9 to 11759.7) | 46.7 (41.5 to 51.1) | 144.2 (56.0 to 299.0) | 308.8 (59.8 to 786.6) | 15247.7 (14490.0 to 16158.4) |

## Hours with a queue reaching the leg end (share of hours with >= 10 vehicles unable to enter)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 0.73 (0.72 to 0.75) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.99 (0.97 to 1.00) |
| actuated | 0.74 (0.72 to 0.75) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 1.00 (1.00 to 1.00) |
| webster | 0.78 (0.76 to 0.79) | 0.00 (0.00 to 0.00) | 0.18 (0.04 to 0.34) | 0.33 (0.00 to 1.00) | 0.99 (0.97 to 1.00) |
| maxpressure | 0.72 (0.68 to 0.77) | 0.00 (0.00 to 0.00) | 0.04 (0.00 to 0.12) | 0.17 (0.00 to 0.50) | 0.95 (0.91 to 1.00) |
| ars_s0 | 0.78 (0.75 to 0.81) | 0.00 (0.00 to 0.00) | 0.08 (0.00 to 0.24) | 0.33 (0.00 to 1.00) | 1.00 (1.00 to 1.00) |
| lstdq_v2_s0 | 0.77 (0.73 to 0.80) | 0.00 (0.00 to 0.00) | 0.08 (0.00 to 0.24) | 0.33 (0.00 to 1.00) | 0.99 (0.97 to 1.00) |
| qlearn_s0 | 0.76 (0.73 to 0.78) | 0.00 (0.00 to 0.00) | 0.08 (0.00 to 0.24) | 0.33 (0.00 to 1.00) | 0.98 (0.96 to 1.00) |

## How often each controller is best in an hour

| Controller | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|
| gdot | 20 % | 35 % | 25 % | 8 % |
| actuated | 20 % | 35 % | 50 % | 31 % |
| webster | 0 % | 0 % | 0 % | 10 % |
| maxpressure | 30 % | 41 % | 25 % | 27 % |
| ars_s0 | 10 % | 6 % | 0 % | 7 % |
| lstdq_v2_s0 | 0 % | 0 % | 0 % | 8 % |
| qlearn_s0 | 40 % | 18 % | 25 % | 9 % |
