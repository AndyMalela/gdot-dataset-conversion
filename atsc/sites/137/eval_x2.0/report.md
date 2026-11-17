# RQ1 evaluation: strengths and weaknesses by traffic condition (137, validation weekdays, DEMAND SCALED x2: a sensitivity experiment on the real profile, not real traffic)

120 clean hours on 5 days x 1 simulation seeds (seed-averaged per hour). Y = sum of critical flow ratios from the field counts. Intervals: 95 % day-bootstrap. **Limitations (137, 2026-11-16):** uncalibrated driver model; GDOT timing not yet field-validated; WB through from the upstream signal 138; EB/WB right turns run as through; P2/P6 stop-bar presence added in the model; coordinated corridor site (138 at ~260 m) modelled isolated; no pedestrian timing (atsc/sites/137/README.md). Main tables: learnt controllers at one training seed (lstdq_v2_s0 = LSTDQ, qlearn_s0, ars_s0); all training seeds of every learner are in the training-seed tables (simulation seed 1).

Hours per condition: light (Y < 0.15) 15, moderate (0.15-0.30) 15, busy (0.30-0.40) 2, heavy (Y >= 0.40) 88

## Overall mean delay, vehicle-weighted (s/veh)

| Controller | mean delay (95 % interval) |
|---|---|
| gdot | 2689.3 (1993.7 to 3384.9) |
| actuated | 2417.7 (1705.2 to 3130.3) |
| webster | 4936.9 (4461.8 to 5412.1) |
| maxpressure | 3504.7 (2924.2 to 4158.3) |
| ars_s0 | 2951.0 (2498.9 to 3464.1) |
| lstdq_v2_s0 | 3896.9 (3399.6 to 4394.1) |
| qlearn_s0 | 3004.2 (2346.4 to 3661.9) |

## Mean delay (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 2012.7 (1517.0 to 2490.0) | 9.4 (7.7 to 10.7) | 12.9 (11.4 to 14.6) | 1944.0 (1926.6 to 1961.4) | 2698.1 (2019.1 to 3353.5) |
| actuated | 1787.9 (1260.8 to 2311.7) | 9.4 (7.7 to 10.7) | 12.9 (11.4 to 14.6) | 1513.4 (1100.4 to 1926.3) | 2403.5 (1690.6 to 3112.8) |
| webster | 3594.4 (3263.5 to 3907.3) | 24.9 (23.3 to 27.4) | 27.2 (25.9 to 29.1) | 1594.5 (1248.8 to 1940.2) | 4858.9 (4399.3 to 5318.4) |
| maxpressure | 2509.1 (2061.9 to 2993.0) | 13.7 (11.6 to 15.3) | 23.3 (14.8 to 31.9) | 883.3 (698.7 to 1067.9) | 3394.9 (2779.4 to 4023.5) |
| ars_s0 | 2183.1 (1834.5 to 2533.0) | 10.5 (8.4 to 12.0) | 14.1 (12.0 to 16.9) | 1474.4 (1020.0 to 1928.7) | 2939.4 (2470.9 to 3391.7) |
| lstdq_v2_s0 | 2778.8 (2431.2 to 3171.0) | 11.2 (9.0 to 13.2) | 14.2 (13.0 to 15.5) | 922.4 (728.6 to 1116.2) | 3767.1 (3279.2 to 4265.6) |
| qlearn_s0 | 2195.5 (1711.1 to 2678.0) | 9.9 (7.7 to 11.8) | 20.6 (11.1 to 35.3) | 1453.4 (978.6 to 1928.2) | 2958.0 (2303.8 to 3599.2) |

## Gain vs Webster (%, negative = less delay than Webster)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | -46.0 (-52.5 to -40.9) | -61.8 (-68.6 to -55.8) | -52.0 (-56.9 to -45.0) | 27.7 (1.1 to 54.3) | -43.9 (-54.0 to -36.3) |
| actuated | -51.7 (-59.4 to -44.0) | -61.8 (-68.6 to -55.8) | -52.0 (-56.9 to -45.0) | 5.5 (-43.3 to 54.3) | -51.0 (-62.1 to -40.0) |
| webster | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| maxpressure | -27.8 (-32.7 to -21.7) | -43.9 (-52.7 to -35.1) | -15.8 (-45.9 to 18.1) | -44.5 (-45.0 to -44.1) | -26.9 (-32.6 to -21.2) |
| ars_s0 | -41.2 (-43.1 to -38.8) | -57.4 (-65.5 to -50.6) | -47.3 (-54.5 to -36.3) | 3.5 (-47.4 to 54.4) | -38.4 (-42.3 to -34.5) |
| lstdq_v2_s0 | -31.0 (-36.2 to -26.3) | -54.5 (-62.9 to -45.8) | -47.0 (-50.5 to -41.8) | -42.1 (-42.5 to -41.7) | -23.9 (-32.4 to -17.8) |
| qlearn_s0 | -37.0 (-42.6 to -30.5) | -59.6 (-68.1 to -51.4) | -25.1 (-57.3 to 30.9) | 2.4 (-49.6 to 54.4) | -37.2 (-43.2 to -31.1) |

## Gain vs actuated (%, negative = less delay than actuated)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 15.2 (5.7 to 26.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 39.1 (0.0 to 78.2) | 19.6 (7.0 to 34.6) |
| actuated | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| webster | 169.4 (137.7 to 202.0) | 188.8 (138.6 to 247.0) | 126.2 (101.8 to 147.5) | 20.6 (-35.2 to 76.3) | 175.8 (122.9 to 228.6) |
| maxpressure | 70.1 (45.4 to 96.2) | 47.8 (39.0 to 56.5) | 63.8 (20.0 to 103.9) | -33.3 (-63.7 to -3.0) | 76.7 (49.7 to 103.7) |
| ars_s0 | 32.8 (13.0 to 52.5) | 12.9 (6.0 to 21.5) | 8.2 (3.7 to 13.6) | -3.6 (-7.3 to 0.1) | 40.8 (14.8 to 66.8) |
| lstdq_v2_s0 | 70.0 (47.1 to 94.9) | 21.1 (15.8 to 26.9) | 12.1 (8.7 to 16.0) | -30.4 (-62.2 to 1.4) | 90.2 (61.3 to 123.2) |
| qlearn_s0 | 34.3 (16.6 to 54.8) | 5.1 (-0.3 to 11.5) | 38.6 (-5.2 to 105.5) | -5.5 (-11.1 to 0.1) | 37.9 (20.6 to 55.3) |

## Regret: delay above the best controller in the same hour (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 396.2 (269.4 to 512.8) | 0.2 (0.1 to 0.4) | 0.5 (0.3 to 0.7) | 1105.3 (982.8 to 1227.9) | 513.8 (348.5 to 673.6) |
| actuated | 171.4 (44.8 to 301.9) | 0.2 (0.1 to 0.4) | 0.5 (0.3 to 0.7) | 674.7 (121.8 to 1227.6) | 219.2 (57.9 to 380.5) |
| webster | 1977.9 (1785.4 to 2252.6) | 15.8 (13.7 to 18.5) | 14.7 (12.4 to 16.7) | 755.9 (550.1 to 961.6) | 2674.6 (2397.1 to 3019.6) |
| maxpressure | 892.6 (745.8 to 1045.1) | 4.6 (3.9 to 5.5) | 10.9 (3.6 to 18.2) | 44.7 (0.0 to 89.3) | 1210.6 (1034.4 to 1402.7) |
| ars_s0 | 566.6 (470.6 to 715.7) | 1.4 (0.7 to 2.1) | 1.7 (0.8 to 2.8) | 635.7 (41.4 to 1230.0) | 755.1 (627.8 to 953.6) |
| lstdq_v2_s0 | 1162.3 (1076.8 to 1240.2) | 2.0 (1.5 to 3.0) | 1.8 (1.3 to 2.2) | 83.8 (29.9 to 137.6) | 1582.8 (1481.3 to 1688.2) |
| qlearn_s0 | 579.0 (495.1 to 662.9) | 0.8 (0.3 to 1.5) | 8.1 (0.0 to 21.2) | 614.7 (0.0 to 1229.5) | 773.7 (671.0 to 873.4) |

## Worst-off movement: highest 95th-percentile delay of any movement in the hour (s)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 5941.7 (5045.6 to 6837.8) | 41.6 (40.1 to 43.4) | 52.6 (49.5 to 56.3) | 6247.0 (4474.3 to 8019.6) | 7923.8 (6706.2 to 9141.5) |
| actuated | 5564.6 (4878.3 to 6235.3) | 41.6 (40.1 to 43.4) | 52.6 (49.5 to 56.3) | 6247.0 (4474.3 to 8019.6) | 7412.8 (6478.6 to 8332.6) |
| webster | 10440.3 (9323.5 to 11486.6) | 67.5 (61.4 to 77.3) | 74.0 (64.3 to 92.3) | 6194.9 (4369.8 to 8020.0) | 14103.6 (12542.7 to 15630.3) |
| maxpressure | 12366.4 (11185.7 to 13547.0) | 106.9 (97.4 to 120.2) | 189.7 (115.5 to 255.4) | 6247.0 (4474.3 to 8019.6) | 16672.0 (15024.8 to 18319.2) |
| ars_s0 | 7592.7 (6653.2 to 8693.8) | 51.9 (48.1 to 54.7) | 63.1 (54.0 to 72.4) | 6247.0 (4474.3 to 8019.6) | 10176.6 (9008.0 to 11601.0) |
| lstdq_v2_s0 | 13558.9 (12574.1 to 14518.6) | 47.2 (40.4 to 54.9) | 65.6 (57.7 to 74.3) | 6247.0 (4474.3 to 8019.6) | 18353.9 (16862.6 to 19845.2) |
| qlearn_s0 | 8268.2 (7562.2 to 8974.2) | 46.8 (39.2 to 55.5) | 139.2 (52.1 to 272.9) | 6247.0 (4474.3 to 8019.6) | 11077.0 (10171.4 to 11958.3) |

## Hours with a queue reaching the leg end (share of hours with >= 10 vehicles unable to enter)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 0.73 (0.72 to 0.75) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 1.00 (1.00 to 1.00) | 0.98 (0.95 to 1.00) |
| actuated | 0.73 (0.72 to 0.75) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 1.00 (1.00 to 1.00) | 0.98 (0.95 to 1.00) |
| webster | 0.76 (0.75 to 0.78) | 0.00 (0.00 to 0.00) | 0.10 (0.00 to 0.30) | 1.00 (1.00 to 1.00) | 1.00 (1.00 to 1.00) |
| maxpressure | 0.73 (0.72 to 0.75) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 1.00 (1.00 to 1.00) | 0.98 (0.95 to 1.00) |
| ars_s0 | 0.74 (0.72 to 0.75) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 1.00 (1.00 to 1.00) | 0.99 (0.96 to 1.00) |
| lstdq_v2_s0 | 0.72 (0.71 to 0.73) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 1.00 (1.00 to 1.00) | 0.95 (0.94 to 0.98) |
| qlearn_s0 | 0.76 (0.72 to 0.80) | 0.00 (0.00 to 0.00) | 0.10 (0.00 to 0.30) | 1.00 (1.00 to 1.00) | 0.99 (0.96 to 1.00) |

## How often each controller is best in an hour

| Controller | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|
| gdot | 40 % | 27 % | 0 % | 10 % |
| actuated | 40 % | 27 % | 0 % | 60 % |
| webster | 0 % | 0 % | 0 % | 6 % |
| maxpressure | 0 % | 13 % | 50 % | 12 % |
| ars_s0 | 13 % | 7 % | 0 % | 2 % |
| lstdq_v2_s0 | 7 % | 7 % | 0 % | 9 % |
| qlearn_s0 | 40 % | 47 % | 50 % | 0 % |
