# RQ1 evaluation: strengths and weaknesses by traffic condition (137, validation weekdays, DEMAND SCALED x1.75: a sensitivity experiment on the real profile, not real traffic)

120 clean hours on 5 days x 1 simulation seeds (seed-averaged per hour). Y = sum of critical flow ratios from the field counts. Intervals: 95 % day-bootstrap. **Limitations (137, 2026-11-16):** uncalibrated driver model; GDOT timing not yet field-validated; WB through from the upstream signal 138; EB/WB right turns run as through; P2/P6 stop-bar presence added in the model; coordinated corridor site (138 at ~260 m) modelled isolated; no pedestrian timing (atsc/sites/137/README.md). Main tables: learnt controllers at one training seed (lstdq_v2_s0 = LSTDQ, qlearn_s0, ars_s0); all training seeds of every learner are in the training-seed tables (simulation seed 1).

Hours per condition: light (Y < 0.15) 18, moderate (0.15-0.30) 13, busy (0.30-0.40) 3, heavy (Y >= 0.40) 86

## Overall mean delay, vehicle-weighted (s/veh)

| Controller | mean delay (95 % interval) |
|---|---|
| gdot | 1123.3 (630.5 to 1616.1) |
| actuated | 880.6 (380.1 to 1381.1) |
| webster | 1794.9 (1428.6 to 2218.6) |
| maxpressure | 1484.6 (1214.0 to 1667.2) |
| ars_s0 | 1029.6 (601.6 to 1457.5) |
| lstdq_v2_s0 | 1099.7 (579.9 to 1618.1) |
| qlearn_s0 | 2749.6 (2505.1 to 2988.1) |

## Mean delay (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 808.0 (458.0 to 1144.8) | 11.7 (10.2 to 12.9) | 58.1 (11.0 to 150.1) | 288.9 (72.5 to 505.3) | 1101.2 (632.9 to 1550.5) |
| actuated | 623.4 (266.9 to 979.9) | 11.7 (10.2 to 12.9) | 45.9 (11.0 to 113.6) | 80.7 (24.1 to 137.4) | 851.3 (373.5 to 1316.5) |
| webster | 1204.3 (981.8 to 1428.5) | 23.1 (21.9 to 24.6) | 25.2 (24.3 to 26.3) | 27.4 (22.5 to 32.3) | 1672.7 (1365.2 to 1980.2) |
| maxpressure | 1040.5 (862.4 to 1181.1) | 13.4 (11.1 to 15.6) | 15.8 (10.4 to 21.3) | 150.3 (17.5 to 283.1) | 1431.7 (1216.2 to 1593.8) |
| ars_s0 | 736.8 (433.1 to 1035.8) | 12.3 (11.1 to 13.5) | 60.6 (10.8 to 152.9) | 106.7 (102.7 to 110.8) | 1003.8 (596.9 to 1407.3) |
| lstdq_v2_s0 | 777.6 (420.7 to 1128.5) | 16.0 (12.7 to 18.8) | 17.8 (13.9 to 22.2) | 229.7 (19.8 to 439.6) | 1061.4 (568.7 to 1515.9) |
| qlearn_s0 | 1922.6 (1783.9 to 2044.5) | 11.8 (10.2 to 13.1) | 18.2 (10.7 to 26.0) | 208.0 (16.9 to 399.1) | 2666.7 (2490.7 to 2781.5) |

## Gain vs Webster (%, negative = less delay than Webster)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 455.7 (39.4 to 1026.0) | -48.9 (-55.7 to -42.2) | 161.0 (-55.9 to 584.8) | 1158.7 (169.9 to 2147.4) | 587.7 (40.3 to 1349.6) |
| actuated | 340.5 (-35.8 to 876.1) | -48.9 (-55.7 to -42.2) | 104.7 (-55.9 to 415.7) | 244.3 (-22.3 to 510.9) | 458.9 (-39.0 to 1168.8) |
| webster | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| maxpressure | 255.0 (59.9 to 514.0) | -41.0 (-52.4 to -30.1) | -39.2 (-58.1 to -15.7) | 451.6 (-22.0 to 925.2) | 349.7 (74.4 to 727.3) |
| ars_s0 | 395.2 (-0.5 to 968.9) | -46.2 (-52.6 to -39.7) | 171.1 (-56.4 to 595.3) | 277.2 (197.8 to 356.6) | 519.2 (-3.2 to 1266.1) |
| lstdq_v2_s0 | 346.4 (15.9 to 759.3) | -29.7 (-44.3 to -15.1) | -30.2 (-45.7 to -12.9) | 673.1 (-11.9 to 1358.2) | 462.1 (-1.1 to 1076.5) |
| qlearn_s0 | 500.0 (286.6 to 713.5) | -48.1 (-55.5 to -40.8) | -27.1 (-56.7 to 6.0) | 583.7 (-24.9 to 1192.2) | 693.5 (398.5 to 982.8) |

## Gain vs actuated (%, negative = less delay than actuated)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 76.2 (17.8 to 135.9) | 0.0 (0.0 to 0.0) | 2.4 (0.0 to 7.1) | 238.8 (209.6 to 267.9) | 97.4 (19.4 to 177.7) |
| actuated | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| webster | 268.5 (112.0 to 443.2) | 104.8 (76.4 to 135.7) | 97.2 (59.5 to 135.7) | -25.2 (-83.6 to 33.2) | 341.1 (116.0 to 577.3) |
| maxpressure | 312.2 (138.0 to 484.8) | 13.5 (4.2 to 24.1) | 9.7 (-6.2 to 29.2) | 507.2 (-87.2 to 1101.7) | 400.8 (187.6 to 654.8) |
| ars_s0 | 69.9 (13.2 to 152.9) | 5.3 (-0.8 to 11.4) | 16.1 (-2.0 to 42.9) | 160.7 (-25.3 to 346.6) | 83.3 (16.6 to 188.4) |
| lstdq_v2_s0 | 97.9 (50.0 to 147.2) | 33.9 (20.8 to 50.1) | 28.3 (16.3 to 40.3) | 824.8 (-85.6 to 1735.2) | 83.4 (37.5 to 134.0) |
| qlearn_s0 | 629.8 (180.5 to 1151.6) | 1.4 (-3.2 to 6.1) | 11.9 (-5.8 to 42.8) | 735.7 (-87.7 to 1559.1) | 834.7 (253.0 to 1513.3) |

## Regret: delay above the best controller in the same hour (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 434.0 (219.9 to 643.5) | 0.7 (0.5 to 0.9) | 46.0 (0.3 to 136.8) | 268.5 (48.5 to 488.5) | 583.8 (301.1 to 861.7) |
| actuated | 249.3 (33.3 to 505.4) | 0.7 (0.5 to 0.9) | 33.9 (0.3 to 100.3) | 60.2 (0.0 to 120.5) | 333.9 (46.4 to 674.1) |
| webster | 830.2 (602.5 to 966.3) | 12.1 (10.1 to 14.3) | 13.2 (10.6 to 15.4) | 6.9 (5.6 to 8.2) | 1155.3 (837.8 to 1373.6) |
| maxpressure | 666.4 (515.0 to 839.9) | 2.4 (1.3 to 3.6) | 3.7 (0.2 to 7.5) | 129.8 (0.7 to 259.0) | 914.3 (723.5 to 1125.2) |
| ars_s0 | 362.7 (161.6 to 563.8) | 1.3 (0.8 to 1.8) | 48.5 (0.6 to 139.5) | 86.3 (85.8 to 86.7) | 486.4 (220.7 to 752.2) |
| lstdq_v2_s0 | 403.5 (187.1 to 650.2) | 5.0 (3.2 to 7.1) | 5.8 (3.8 to 7.8) | 209.2 (2.9 to 415.5) | 544.0 (241.7 to 873.6) |
| qlearn_s0 | 1548.5 (1355.2 to 1741.8) | 0.8 (0.4 to 1.5) | 6.1 (0.5 to 11.7) | 187.5 (0.0 to 375.1) | 2149.3 (1884.6 to 2412.3) |

## Worst-off movement: highest 95th-percentile delay of any movement in the hour (s)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 2865.0 (1967.2 to 3762.8) | 45.6 (42.2 to 48.4) | 234.9 (54.5 to 594.0) | 2182.9 (859.9 to 3505.9) | 3865.9 (2675.8 to 5056.0) |
| actuated | 2245.8 (1281.3 to 3210.4) | 45.6 (42.2 to 48.4) | 267.9 (54.5 to 693.1) | 883.6 (73.3 to 1693.8) | 3044.4 (1766.6 to 4322.1) |
| webster | 4303.6 (3492.6 to 5056.7) | 59.9 (58.8 to 61.8) | 64.8 (60.7 to 71.8) | 114.6 (75.0 to 154.2) | 5981.3 (4843.0 to 7026.3) |
| maxpressure | 6485.7 (5453.7 to 7421.5) | 96.3 (88.6 to 103.1) | 129.7 (102.9 to 156.4) | 1416.3 (100.5 to 2732.1) | 8885.4 (7579.5 to 9953.1) |
| ars_s0 | 2712.2 (2065.3 to 3298.9) | 69.8 (64.1 to 75.4) | 270.7 (73.3 to 616.0) | 726.9 (687.8 to 766.0) | 3664.7 (2858.0 to 4381.3) |
| lstdq_v2_s0 | 3876.8 (2421.2 to 5332.4) | 112.1 (96.8 to 133.4) | 144.7 (116.4 to 177.8) | 1635.7 (148.4 to 3123.1) | 5258.3 (3234.8 to 7281.8) |
| qlearn_s0 | 5591.2 (5393.1 to 5905.5) | 50.3 (45.5 to 58.4) | 120.1 (50.7 to 192.0) | 2496.4 (82.0 to 4910.9) | 7650.7 (7320.5 to 7988.8) |

## Hours with a queue reaching the leg end (share of hours with >= 10 vehicles unable to enter)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 0.70 (0.68 to 0.71) | 0.00 (0.00 to 0.00) | 0.07 (0.00 to 0.20) | 0.75 (0.50 to 1.00) | 0.94 (0.94 to 0.94) |
| actuated | 0.68 (0.65 to 0.71) | 0.00 (0.00 to 0.00) | 0.07 (0.00 to 0.20) | 0.50 (0.00 to 1.00) | 0.93 (0.91 to 0.94) |
| webster | 0.63 (0.57 to 0.70) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.88 (0.81 to 0.95) |
| maxpressure | 0.68 (0.65 to 0.72) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.50 (0.00 to 1.00) | 0.93 (0.90 to 0.97) |
| ars_s0 | 0.70 (0.68 to 0.71) | 0.00 (0.00 to 0.00) | 0.07 (0.00 to 0.20) | 0.75 (0.50 to 1.00) | 0.94 (0.94 to 0.94) |
| lstdq_v2_s0 | 0.69 (0.67 to 0.71) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.50 (0.00 to 1.00) | 0.94 (0.94 to 0.94) |
| qlearn_s0 | 0.69 (0.67 to 0.71) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.50 (0.00 to 1.00) | 0.94 (0.94 to 0.94) |

## How often each controller is best in an hour

| Controller | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|
| gdot | 39 % | 38 % | 0 % | 6 % |
| actuated | 39 % | 38 % | 67 % | 55 % |
| webster | 0 % | 0 % | 0 % | 8 % |
| maxpressure | 28 % | 46 % | 0 % | 12 % |
| ars_s0 | 11 % | 0 % | 0 % | 12 % |
| lstdq_v2_s0 | 0 % | 0 % | 0 % | 6 % |
| qlearn_s0 | 22 % | 15 % | 33 % | 2 % |
