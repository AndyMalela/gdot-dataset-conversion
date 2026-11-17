# RQ1 evaluation: strengths and weaknesses by traffic condition (137, validation weekdays, DEMAND SCALED x2.5: a sensitivity experiment on the real profile, not real traffic)

120 clean hours on 5 days x 1 simulation seeds (seed-averaged per hour). Y = sum of critical flow ratios from the field counts. Intervals: 95 % day-bootstrap. **Limitations (137, 2026-11-16):** uncalibrated driver model; GDOT timing not yet field-validated; WB through from the upstream signal 138; EB/WB right turns run as through; P2/P6 stop-bar presence added in the model; coordinated corridor site (138 at ~260 m) modelled isolated; no pedestrian timing (atsc/sites/137/README.md). Main tables: learnt controllers at one training seed (lstdq_v2_s0 = LSTDQ, qlearn_s0, ars_s0); all training seeds of every learner are in the training-seed tables (simulation seed 1).

Hours per condition: light (Y < 0.15) 10, moderate (0.15-0.30) 17, busy (0.30-0.40) 4, heavy (Y >= 0.40) 89

## Overall mean delay, vehicle-weighted (s/veh)

| Controller | mean delay (95 % interval) |
|---|---|
| gdot | 3243.6 (2612.9 to 3888.1) |
| actuated | 2991.6 (2322.9 to 3676.5) |
| webster | 5235.0 (5046.6 to 5440.2) |
| maxpressure | 3799.6 (2900.0 to 4699.2) |
| ars_s0 | 4688.7 (4143.3 to 5278.0) |
| lstdq_v2_s0 | 4505.0 (3945.0 to 5189.2) |
| qlearn_s0 | 3509.8 (2713.8 to 4335.8) |

## Mean delay (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 2235.1 (1858.0 to 2617.2) | 12.1 (11.1 to 13.2) | 13.3 (12.4 to 14.3) | 147.3 (13.8 to 412.6) | 3010.5 (2472.7 to 3554.9) |
| actuated | 2111.5 (1713.8 to 2515.3) | 12.1 (11.1 to 13.2) | 13.3 (12.4 to 14.3) | 18.4 (13.8 to 25.8) | 2854.3 (2280.4 to 3460.2) |
| webster | 3572.5 (3311.5 to 3802.3) | 18.8 (18.4 to 19.2) | 82.6 (22.1 to 199.5) | 84.6 (26.0 to 198.1) | 4783.4 (4523.7 to 5029.6) |
| maxpressure | 2704.4 (2146.6 to 3267.0) | 15.0 (13.2 to 16.2) | 17.0 (14.5 to 19.4) | 24.2 (15.0 to 41.2) | 3655.3 (2856.2 to 4514.9) |
| ars_s0 | 3236.3 (2996.5 to 3465.3) | 12.7 (11.8 to 13.5) | 16.8 (13.6 to 19.9) | 86.9 (14.6 to 229.7) | 4357.2 (3992.9 to 4688.7) |
| lstdq_v2_s0 | 3261.5 (2929.9 to 3589.8) | 14.0 (13.1 to 14.6) | 14.9 (13.5 to 16.8) | 306.5 (14.2 to 890.3) | 4377.9 (3918.1 to 4877.3) |
| qlearn_s0 | 2625.0 (2099.0 to 3151.1) | 14.1 (12.9 to 15.3) | 14.5 (13.4 to 15.7) | 142.5 (14.6 to 396.8) | 3538.5 (2793.5 to 4306.4) |

## Gain vs Webster (%, negative = less delay than Webster)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | -23.3 (-44.4 to 8.5) | -35.6 (-39.3 to -31.1) | -51.9 (-67.2 to -41.1) | -16.6 (-48.1 to 45.3) | -15.9 (-43.0 to 23.3) |
| actuated | -16.1 (-41.1 to 15.4) | -35.6 (-39.3 to -31.1) | -51.9 (-67.2 to -41.1) | -57.3 (-77.0 to -46.9) | -3.3 (-39.0 to 40.5) |
| webster | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| maxpressure | 54.9 (-20.2 to 152.2) | -19.6 (-28.6 to -13.1) | -40.4 (-56.4 to -29.6) | -48.0 (-56.7 to -42.4) | 87.4 (-11.8 to 212.9) |
| ars_s0 | 15.5 (-3.8 to 39.5) | -32.1 (-35.4 to -28.8) | -43.8 (-60.0 to -33.1) | -27.0 (-45.4 to 8.1) | 35.0 (8.7 to 67.4) |
| lstdq_v2_s0 | 37.5 (-16.2 to 92.4) | -25.1 (-27.8 to -22.4) | -47.4 (-62.8 to -34.6) | 39.0 (-49.4 to 211.6) | 60.6 (-9.4 to 130.7) |
| qlearn_s0 | 114.5 (17.0 to 212.1) | -24.2 (-29.3 to -17.8) | -47.9 (-64.4 to -34.5) | -12.3 (-46.4 to 53.2) | 166.1 (34.2 to 297.9) |

## Gain vs actuated (%, negative = less delay than actuated)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 31.0 (-2.4 to 94.6) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 644.8 (0.0 to 1934.4) | -1.8 (-4.8 to 1.4) |
| actuated | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| webster | 207.6 (119.9 to 353.1) | 56.8 (45.6 to 66.0) | 439.0 (78.1 to 1137.9) | 332.7 (88.4 to 817.1) | 137.0 (116.1 to 162.7) |
| maxpressure | 60.6 (21.3 to 123.9) | 25.7 (10.7 to 40.7) | 25.2 (16.3 to 34.1) | 20.3 (5.9 to 46.4) | 71.6 (22.3 to 154.7) |
| ars_s0 | 60.2 (47.2 to 73.7) | 5.6 (0.4 to 9.9) | 22.6 (9.6 to 35.5) | 330.1 (5.2 to 979.1) | 52.8 (25.4 to 75.4) |
| lstdq_v2_s0 | 122.7 (32.4 to 263.1) | 16.6 (7.6 to 24.6) | 10.9 (4.9 to 17.1) | 1431.3 (-2.4 to 4293.2) | 64.4 (36.0 to 108.8) |
| qlearn_s0 | 143.5 (67.6 to 213.5) | 17.6 (8.3 to 25.8) | 8.7 (2.3 to 17.0) | 613.0 (3.3 to 1829.8) | 146.5 (42.3 to 270.5) |

## Regret: delay above the best controller in the same hour (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 758.5 (511.2 to 1060.1) | 0.2 (0.1 to 0.3) | 0.2 (0.0 to 0.5) | 129.4 (0.0 to 387.9) | 1022.3 (681.5 to 1446.6) |
| actuated | 634.8 (381.1 to 969.6) | 0.2 (0.1 to 0.3) | 0.2 (0.0 to 0.5) | 0.5 (0.0 to 1.1) | 866.1 (508.1 to 1351.8) |
| webster | 2095.8 (1755.4 to 2371.5) | 6.9 (6.1 to 7.5) | 69.5 (9.7 to 185.2) | 66.8 (12.2 to 173.4) | 2795.2 (2398.1 to 3126.3) |
| maxpressure | 1227.8 (799.0 to 1714.8) | 3.2 (1.5 to 4.8) | 3.9 (2.3 to 5.8) | 6.3 (1.2 to 16.5) | 1667.0 (1064.0 to 2378.7) |
| ars_s0 | 1759.7 (1650.3 to 1841.9) | 0.8 (0.3 to 1.3) | 3.7 (1.4 to 5.9) | 69.0 (0.8 to 205.0) | 2369.0 (2219.2 to 2499.1) |
| lstdq_v2_s0 | 1784.8 (1560.7 to 2008.9) | 2.1 (1.2 to 2.9) | 1.8 (1.1 to 2.5) | 288.7 (0.0 to 865.6) | 2389.6 (2080.3 to 2694.3) |
| qlearn_s0 | 1148.4 (743.9 to 1576.0) | 2.2 (1.2 to 3.2) | 1.4 (0.7 to 2.3) | 124.6 (0.8 to 372.1) | 1550.3 (991.0 to 2160.0) |

## Worst-off movement: highest 95th-percentile delay of any movement in the hour (s)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 5990.4 (5415.8 to 6543.2) | 40.1 (30.5 to 53.9) | 49.8 (44.7 to 54.6) | 722.2 (69.9 to 2012.2) | 8028.3 (7204.5 to 8841.9) |
| actuated | 5646.9 (4842.6 to 6372.8) | 40.1 (30.5 to 53.9) | 49.8 (44.7 to 54.6) | 115.0 (69.9 to 190.4) | 7614.1 (6439.5 to 8741.6) |
| webster | 8368.6 (7879.8 to 8857.4) | 50.9 (46.0 to 55.8) | 361.3 (63.3 to 913.9) | 380.6 (88.6 to 951.2) | 11156.8 (10572.3 to 11708.3) |
| maxpressure | 9162.5 (8250.0 to 10078.6) | 82.2 (71.0 to 91.7) | 116.6 (92.3 to 147.1) | 169.3 (95.4 to 297.6) | 12337.1 (11011.1 to 13711.2) |
| ars_s0 | 6641.7 (6375.7 to 6857.3) | 53.8 (44.0 to 61.0) | 105.6 (86.6 to 124.6) | 420.1 (86.7 to 1051.1) | 8908.3 (8529.6 to 9222.4) |
| lstdq_v2_s0 | 7499.9 (6889.6 to 8110.2) | 61.4 (46.3 to 74.5) | 75.5 (66.3 to 84.7) | 690.1 (96.7 to 1868.1) | 10045.5 (9230.3 to 10860.7) |
| qlearn_s0 | 8329.1 (7834.3 to 8823.9) | 62.6 (42.1 to 83.3) | 56.5 (49.5 to 63.4) | 506.2 (58.5 to 1378.1) | 11191.4 (10424.6 to 11950.8) |

## Hours with a queue reaching the leg end (share of hours with >= 10 vehicles unable to enter)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 0.68 (0.65 to 0.70) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.17 (0.00 to 0.50) | 0.90 (0.87 to 0.93) |
| actuated | 0.72 (0.69 to 0.74) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.97 (0.94 to 0.99) |
| webster | 0.77 (0.73 to 0.81) | 0.00 (0.00 to 0.00) | 0.16 (0.00 to 0.36) | 0.33 (0.00 to 1.00) | 0.97 (0.94 to 0.99) |
| maxpressure | 0.72 (0.69 to 0.74) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.17 (0.00 to 0.50) | 0.95 (0.92 to 0.99) |
| ars_s0 | 0.71 (0.68 to 0.73) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.33 (0.00 to 1.00) | 0.93 (0.90 to 0.97) |
| lstdq_v2_s0 | 0.72 (0.71 to 0.74) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.33 (0.00 to 1.00) | 0.95 (0.94 to 0.98) |
| qlearn_s0 | 0.75 (0.75 to 0.75) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.33 (0.00 to 1.00) | 0.99 (0.96 to 1.00) |

## How often each controller is best in an hour

| Controller | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|
| gdot | 70 % | 59 % | 50 % | 24 % |
| actuated | 70 % | 59 % | 50 % | 30 % |
| webster | 0 % | 0 % | 0 % | 11 % |
| maxpressure | 0 % | 6 % | 25 % | 13 % |
| ars_s0 | 30 % | 6 % | 0 % | 7 % |
| lstdq_v2_s0 | 0 % | 24 % | 25 % | 1 % |
| qlearn_s0 | 0 % | 6 % | 0 % | 13 % |
