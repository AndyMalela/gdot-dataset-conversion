# RQ1 evaluation: strengths and weaknesses by traffic condition (137, validation weekdays, DEMAND SCALED x2: a sensitivity experiment on the real profile, not real traffic)

120 clean hours on 5 days x 1 simulation seeds (seed-averaged per hour). Y = sum of critical flow ratios from the field counts. Intervals: 95 % day-bootstrap. **Limitations (137, 2026-11-16):** uncalibrated driver model; GDOT timing not yet field-validated; WB through from the upstream signal 138; EB/WB right turns run as through; P2/P6 stop-bar presence added in the model; coordinated corridor site (138 at ~260 m) modelled isolated; no pedestrian timing (atsc/sites/137/README.md). Main tables: learnt controllers at one training seed (lstdq_v2_s0 = LSTDQ, qlearn_s0, ars_s0); all training seeds of every learner are in the training-seed tables (simulation seed 1).

Hours per condition: light (Y < 0.15) 15, moderate (0.15-0.30) 15, busy (0.30-0.40) 3, heavy (Y >= 0.40) 87

## Overall mean delay, vehicle-weighted (s/veh)

| Controller | mean delay (95 % interval) |
|---|---|
| gdot | 1032.7 (410.8 to 1638.7) |
| actuated | 703.6 (201.6 to 1216.0) |
| webster | 2819.9 (2388.4 to 3316.5) |
| maxpressure | 656.3 (167.7 to 1196.0) |
| ars_s0 | 1417.5 (645.4 to 2243.9) |
| lstdq_v2_s0 | 956.9 (331.4 to 1572.3) |
| qlearn_s0 | 942.7 (491.2 to 1394.1) |

## Mean delay (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 755.9 (311.0 to 1183.5) | 11.8 (10.8 to 12.7) | 13.0 (12.0 to 14.1) | 270.4 (17.6 to 771.9) | 1031.9 (430.2 to 1598.8) |
| actuated | 508.5 (144.6 to 873.6) | 11.8 (10.8 to 12.7) | 13.0 (12.0 to 14.1) | 45.7 (17.7 to 97.7) | 693.8 (197.0 to 1190.6) |
| webster | 1918.6 (1665.3 to 2129.7) | 20.7 (18.6 to 22.9) | 47.8 (19.6 to 99.1) | 30.8 (19.9 to 38.1) | 2630.4 (2305.1 to 2931.6) |
| maxpressure | 481.4 (120.6 to 885.9) | 16.2 (14.8 to 17.9) | 17.4 (14.3 to 20.5) | 19.5 (17.4 to 22.1) | 653.2 (161.5 to 1187.5) |
| ars_s0 | 1052.0 (497.2 to 1605.3) | 14.2 (12.5 to 16.3) | 15.9 (13.4 to 18.6) | 607.9 (19.2 to 1709.6) | 1421.1 (677.7 to 2158.6) |
| lstdq_v2_s0 | 694.5 (242.9 to 1137.5) | 14.6 (13.9 to 15.6) | 17.1 (13.0 to 23.4) | 196.6 (16.8 to 552.1) | 943.6 (329.8 to 1555.6) |
| qlearn_s0 | 686.8 (364.9 to 1007.3) | 13.6 (12.9 to 14.1) | 14.6 (13.1 to 16.7) | 39.2 (12.8 to 86.8) | 940.5 (499.2 to 1367.8) |

## Gain vs Webster (%, negative = less delay than Webster)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 338.3 (-51.7 to 1055.3) | -41.4 (-46.1 to -36.7) | -46.8 (-57.6 to -38.9) | 1232.2 (-48.8 to 3788.6) | 449.8 (-53.0 to 1370.7) |
| actuated | 179.9 (-76.2 to 640.9) | -41.4 (-46.1 to -36.7) | -46.8 (-57.6 to -38.9) | 100.2 (-48.3 to 392.2) | 266.2 (-87.5 to 907.8) |
| webster | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| maxpressure | 160.5 (-72.7 to 563.4) | -18.9 (-29.3 to -7.9) | -31.4 (-44.5 to -17.7) | -32.1 (-49.3 to -4.9) | 236.3 (-88.7 to 805.2) |
| ars_s0 | 612.0 (-47.4 to 1860.0) | -30.1 (-37.6 to -19.7) | -38.3 (-49.9 to -31.2) | 2872.4 (-44.1 to 8512.5) | 773.8 (-52.9 to 2338.0) |
| lstdq_v2_s0 | 304.7 (-70.7 to 996.4) | -26.8 (-34.2 to -19.4) | -35.0 (-51.7 to -19.7) | 861.6 (-51.0 to 2681.2) | 410.8 (-82.5 to 1322.2) |
| qlearn_s0 | 227.4 (-54.4 to 745.1) | -32.7 (-37.5 to -27.9) | -41.2 (-53.3 to -33.1) | 14.8 (-47.6 to 127.5) | 333.8 (-62.8 to 1066.8) |

## Gain vs actuated (%, negative = less delay than actuated)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 155.5 (39.1 to 336.1) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 229.7 (-1.0 to 690.0) | 210.1 (41.7 to 473.5) |
| actuated | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| webster | 1183.6 (315.5 to 2139.8) | 76.2 (59.2 to 93.7) | 234.4 (65.0 to 554.9) | 30.1 (-79.7 to 93.5) | 1561.2 (410.9 to 2748.9) |
| maxpressure | 7.0 (-6.4 to 19.9) | 38.1 (27.3 to 49.8) | 30.2 (14.0 to 44.8) | -26.7 (-80.7 to 2.5) | -1.5 (-17.1 to 13.6) |
| ars_s0 | 323.3 (113.6 to 576.6) | 20.4 (11.3 to 31.8) | 18.9 (10.8 to 27.2) | 665.6 (8.1 to 1649.6) | 413.8 (112.2 to 747.2) |
| lstdq_v2_s0 | 67.0 (14.1 to 140.9) | 24.3 (16.1 to 32.5) | 25.7 (5.9 to 58.3) | 152.0 (-5.2 to 465.0) | 77.5 (9.1 to 181.9) |
| qlearn_s0 | 163.8 (55.3 to 272.3) | 15.5 (11.3 to 19.7) | 11.0 (5.9 to 17.7) | 72.0 (-86.9 to 301.6) | 219.0 (70.5 to 367.7) |

## Regret: delay above the best controller in the same hour (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 510.9 (202.6 to 802.5) | 0.0 (0.0 to 0.0) | 0.2 (0.0 to 0.4) | 253.6 (0.7 to 759.1) | 698.7 (284.0 to 1105.5) |
| actuated | 263.5 (27.1 to 507.8) | 0.0 (0.0 to 0.0) | 0.2 (0.0 to 0.4) | 28.9 (0.8 to 84.9) | 360.5 (37.8 to 685.2) |
| webster | 1673.6 (1398.9 to 1840.7) | 8.9 (7.1 to 10.8) | 34.9 (8.0 to 85.3) | 14.0 (7.0 to 17.5) | 2297.1 (1931.0 to 2543.5) |
| maxpressure | 236.4 (12.2 to 531.8) | 4.4 (3.3 to 5.9) | 4.6 (2.3 to 6.8) | 2.7 (0.6 to 6.1) | 319.9 (15.3 to 716.3) |
| ars_s0 | 807.0 (350.9 to 1263.1) | 2.4 (1.3 to 3.9) | 3.0 (1.7 to 4.6) | 591.1 (2.4 to 1696.8) | 1087.9 (485.4 to 1692.9) |
| lstdq_v2_s0 | 449.4 (134.5 to 764.3) | 2.8 (1.9 to 3.7) | 4.2 (1.2 to 9.6) | 179.8 (0.0 to 539.3) | 610.4 (183.6 to 1040.5) |
| qlearn_s0 | 441.7 (256.5 to 627.0) | 1.8 (1.4 to 2.1) | 1.8 (0.9 to 2.9) | 22.4 (0.0 to 66.0) | 607.2 (352.9 to 859.2) |

## Worst-off movement: highest 95th-percentile delay of any movement in the hour (s)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 1902.5 (937.4 to 2842.2) | 38.9 (32.6 to 45.1) | 50.6 (44.6 to 56.9) | 982.2 (77.3 to 2723.8) | 2583.7 (1291.6 to 3825.9) |
| actuated | 1448.3 (616.8 to 2279.8) | 38.9 (32.6 to 45.1) | 50.6 (44.6 to 56.9) | 304.4 (69.4 to 744.3) | 1972.0 (845.6 to 3095.0) |
| webster | 5233.8 (4515.8 to 5710.7) | 70.4 (50.0 to 102.2) | 201.4 (54.4 to 467.2) | 185.9 (46.0 to 307.4) | 7153.9 (6213.4 to 7797.2) |
| maxpressure | 1923.8 (869.2 to 2978.3) | 89.0 (77.7 to 100.3) | 115.8 (92.7 to 136.4) | 121.5 (104.0 to 148.7) | 2607.7 (1169.9 to 4045.4) |
| ars_s0 | 2410.4 (1720.4 to 3106.6) | 61.4 (45.1 to 80.7) | 97.5 (84.6 to 117.5) | 1589.5 (119.8 to 3626.0) | 3234.6 (2344.6 to 4138.6) |
| lstdq_v2_s0 | 1961.0 (1095.9 to 2783.0) | 60.9 (50.8 to 71.8) | 85.9 (60.9 to 128.7) | 744.2 (87.9 to 2025.7) | 2652.0 (1482.9 to 3751.6) |
| qlearn_s0 | 4894.6 (3377.1 to 6356.3) | 41.7 (37.2 to 47.1) | 65.8 (47.6 to 94.4) | 510.1 (46.3 to 1364.8) | 6717.8 (4628.8 to 8752.2) |

## Hours with a queue reaching the leg end (share of hours with >= 10 vehicles unable to enter)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 0.68 (0.64 to 0.71) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.33 (0.00 to 1.00) | 0.92 (0.87 to 0.97) |
| actuated | 0.68 (0.64 to 0.71) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.33 (0.00 to 1.00) | 0.92 (0.87 to 0.97) |
| webster | 0.71 (0.62 to 0.78) | 0.00 (0.00 to 0.00) | 0.20 (0.00 to 0.40) | 0.33 (0.00 to 1.00) | 0.93 (0.81 to 1.00) |
| maxpressure | 0.66 (0.63 to 0.68) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.91 (0.86 to 0.94) |
| ars_s0 | 0.71 (0.68 to 0.73) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 1.00 (1.00 to 1.00) | 0.94 (0.91 to 0.98) |
| lstdq_v2_s0 | 0.67 (0.63 to 0.71) | 0.00 (0.00 to 0.00) | 0.10 (0.00 to 0.30) | 0.33 (0.00 to 1.00) | 0.90 (0.86 to 0.93) |
| qlearn_s0 | 0.69 (0.67 to 0.72) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.33 (0.00 to 1.00) | 0.94 (0.90 to 0.99) |

## How often each controller is best in an hour

| Controller | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|
| gdot | 100 % | 60 % | 0 % | 9 % |
| actuated | 100 % | 60 % | 0 % | 22 % |
| webster | 0 % | 0 % | 0 % | 9 % |
| maxpressure | 0 % | 7 % | 0 % | 46 % |
| ars_s0 | 0 % | 0 % | 0 % | 5 % |
| lstdq_v2_s0 | 0 % | 20 % | 67 % | 5 % |
| qlearn_s0 | 0 % | 13 % | 33 % | 5 % |
