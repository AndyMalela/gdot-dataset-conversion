# RQ1 evaluation: strengths and weaknesses by traffic condition (137, validation weekdays, DEMAND SCALED x1.75: a sensitivity experiment on the real profile, not real traffic)

120 clean hours on 5 days x 1 simulation seeds (seed-averaged per hour). Y = sum of critical flow ratios from the field counts. Intervals: 95 % day-bootstrap. **Limitations (137, 2026-11-16):** uncalibrated driver model; GDOT timing not yet field-validated; WB through from the upstream signal 138; EB/WB right turns run as through; P2/P6 stop-bar presence added in the model; coordinated corridor site (138 at ~260 m) modelled isolated; no pedestrian timing (atsc/sites/137/README.md). Main tables: learnt controllers at one training seed (lstdq_v2_s0 = LSTDQ, qlearn_s0, ars_s0); all training seeds of every learner are in the training-seed tables (simulation seed 1).

Hours per condition: light (Y < 0.15) 18, moderate (0.15-0.30) 13, busy (0.30-0.40) 3, heavy (Y >= 0.40) 86

## Overall mean delay, vehicle-weighted (s/veh)

| Controller | mean delay (95 % interval) |
|---|---|
| gdot | 1137.2 (616.0 to 1658.4) |
| actuated | 894.0 (363.6 to 1460.6) |
| webster | 3456.5 (2805.9 to 4157.0) |
| maxpressure | 1623.2 (1216.3 to 2035.7) |
| ars_s0 | 1291.4 (841.7 to 1784.3) |
| lstdq_v2_s0 | 2454.3 (2102.1 to 2806.5) |
| qlearn_s0 | 1664.7 (1262.8 to 2056.2) |

## Mean delay (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 832.3 (457.1 to 1207.5) | 9.3 (7.4 to 11.0) | 31.3 (10.0 to 71.6) | 282.0 (74.5 to 489.5) | 1137.3 (628.0 to 1639.5) |
| actuated | 651.8 (254.8 to 1072.7) | 9.3 (7.4 to 11.0) | 44.2 (10.0 to 110.4) | 64.0 (25.9 to 102.0) | 888.2 (356.2 to 1442.2) |
| webster | 2542.2 (2093.3 to 3002.7) | 23.5 (22.4 to 25.0) | 107.4 (24.7 to 271.9) | 1250.5 (1050.4 to 1450.7) | 3476.8 (2902.0 to 4120.9) |
| maxpressure | 1178.8 (897.6 to 1477.6) | 13.9 (10.4 to 17.3) | 61.0 (10.8 to 156.4) | 325.3 (268.1 to 382.4) | 1605.5 (1257.2 to 1986.5) |
| ars_s0 | 953.3 (606.3 to 1324.5) | 10.6 (8.6 to 12.3) | 95.1 (10.4 to 261.2) | 164.0 (106.0 to 222.0) | 1296.2 (842.4 to 1771.8) |
| lstdq_v2_s0 | 1758.3 (1518.9 to 2003.6) | 10.8 (9.1 to 12.1) | 57.9 (10.8 to 149.4) | 616.8 (388.9 to 844.8) | 2413.0 (2099.4 to 2726.5) |
| qlearn_s0 | 1221.2 (950.5 to 1488.6) | 9.2 (7.3 to 10.8) | 59.9 (9.8 to 152.0) | 668.9 (383.5 to 954.3) | 1653.9 (1269.5 to 1993.3) |

## Gain vs Webster (%, negative = less delay than Webster)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | -64.8 (-72.3 to -57.4) | -59.9 (-68.9 to -51.8) | -56.6 (-65.3 to -45.2) | -79.3 (-92.2 to -66.3) | -66.9 (-78.7 to -55.1) |
| actuated | -70.3 (-76.6 to -62.1) | -59.9 (-68.9 to -51.8) | -55.5 (-63.4 to -44.6) | -94.0 (-94.9 to -93.0) | -74.4 (-85.2 to -61.8) |
| webster | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| maxpressure | -47.0 (-55.1 to -38.9) | -39.8 (-56.5 to -23.2) | -39.0 (-57.6 to -16.4) | -70.4 (-73.6 to -67.1) | -50.4 (-60.7 to -40.9) |
| ars_s0 | -58.6 (-64.4 to -53.5) | -54.5 (-63.4 to -46.7) | -47.2 (-59.1 to -33.3) | -86.2 (-87.6 to -84.7) | -61.0 (-68.1 to -52.4) |
| lstdq_v2_s0 | -34.7 (-41.4 to -27.6) | -53.4 (-61.0 to -46.6) | -50.1 (-60.7 to -39.7) | -14.0 (-73.2 to 45.2) | -30.4 (-38.2 to -19.1) |
| qlearn_s0 | -46.3 (-54.0 to -37.3) | -60.6 (-69.5 to -53.3) | -40.7 (-61.5 to -7.1) | 3.6 (-73.6 to 80.7) | -48.4 (-59.9 to -38.6) |

## Gain vs actuated (%, negative = less delay than actuated)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 83.9 (18.9 to 154.4) | 0.0 (0.0 to 0.0) | -2.6 (-7.7 to 0.0) | 288.4 (197.1 to 379.7) | 109.0 (24.4 to 203.2) |
| actuated | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| webster | 929.9 (356.3 to 1557.0) | 182.2 (122.2 to 262.9) | 146.3 (103.3 to 183.3) | 2713.0 (1321.6 to 4104.3) | 1123.1 (398.1 to 1974.0) |
| maxpressure | 329.3 (101.4 to 615.1) | 46.0 (29.0 to 63.1) | 33.2 (9.2 to 66.6) | 618.5 (274.8 to 962.2) | 412.5 (113.3 to 801.2) |
| ars_s0 | 156.2 (46.7 to 315.6) | 15.1 (6.6 to 23.9) | 18.8 (4.9 to 41.7) | 219.2 (117.6 to 320.9) | 200.3 (52.6 to 413.1) |
| lstdq_v2_s0 | 594.7 (226.7 to 965.2) | 20.8 (11.5 to 31.9) | 14.4 (5.3 to 23.6) | 1732.8 (281.1 to 3184.5) | 747.7 (300.7 to 1194.8) |
| qlearn_s0 | 374.8 (113.5 to 654.6) | -1.2 (-3.7 to 0.4) | 21.7 (-1.7 to 50.6) | 1930.6 (275.8 to 3585.4) | 428.0 (99.9 to 788.3) |

## Regret: delay above the best controller in the same hour (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 236.8 (125.5 to 365.4) | 0.4 (0.2 to 0.7) | 0.3 (0.1 to 0.6) | 218.0 (48.6 to 387.4) | 322.6 (175.8 to 497.3) |
| actuated | 56.3 (4.3 to 146.2) | 0.4 (0.2 to 0.7) | 13.3 (0.3 to 39.0) | 0.0 (0.0 to 0.0) | 73.5 (6.1 to 193.1) |
| webster | 1946.6 (1638.8 to 2215.3) | 14.6 (12.4 to 16.8) | 76.5 (11.9 to 201.4) | 1186.6 (1024.5 to 1348.6) | 2662.1 (2237.6 to 3029.9) |
| maxpressure | 583.2 (403.9 to 849.1) | 5.0 (3.1 to 7.2) | 30.1 (1.1 to 84.9) | 261.3 (242.2 to 280.4) | 790.8 (549.0 to 1144.1) |
| ars_s0 | 357.8 (229.8 to 482.2) | 1.7 (1.1 to 2.3) | 64.1 (0.9 to 189.7) | 100.0 (80.1 to 120.0) | 481.5 (314.7 to 646.8) |
| lstdq_v2_s0 | 1162.7 (1061.4 to 1268.7) | 1.9 (1.5 to 2.3) | 27.0 (0.9 to 78.1) | 552.8 (286.8 to 818.8) | 1598.3 (1446.7 to 1749.9) |
| qlearn_s0 | 625.7 (479.2 to 798.9) | 0.3 (0.1 to 0.5) | 29.0 (0.2 to 80.6) | 604.9 (281.4 to 928.4) | 839.2 (638.2 to 1071.3) |

## Worst-off movement: highest 95th-percentile delay of any movement in the hour (s)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 2993.6 (1988.5 to 3998.6) | 42.3 (38.5 to 46.6) | 181.2 (48.6 to 442.3) | 2434.7 (898.9 to 3970.4) | 4050.1 (2721.9 to 5378.3) |
| actuated | 2272.6 (1220.0 to 3325.2) | 42.3 (38.5 to 46.6) | 256.1 (48.6 to 667.1) | 776.3 (79.2 to 1473.5) | 3077.4 (1676.6 to 4478.2) |
| webster | 8164.4 (6900.4 to 9428.4) | 62.0 (59.4 to 65.3) | 351.1 (61.7 to 927.5) | 5267.5 (4391.0 to 6144.0) | 11127.6 (9380.8 to 12874.4) |
| maxpressure | 7083.4 (5499.5 to 8529.4) | 109.8 (93.4 to 126.9) | 413.2 (98.2 to 1026.7) | 3322.9 (2429.1 to 4216.6) | 9596.1 (7590.0 to 11397.2) |
| ars_s0 | 3658.8 (2933.9 to 4291.4) | 55.2 (49.7 to 62.3) | 348.5 (51.6 to 931.3) | 1108.0 (1040.8 to 1175.1) | 4958.6 (4106.4 to 5711.1) |
| lstdq_v2_s0 | 10083.1 (8740.9 to 11361.1) | 51.5 (46.8 to 59.6) | 346.0 (51.9 to 931.9) | 5204.4 (4216.6 to 6192.1) | 13793.5 (12006.0 to 15542.9) |
| qlearn_s0 | 5984.4 (4926.7 to 7029.1) | 43.7 (37.8 to 51.9) | 385.8 (55.5 to 989.9) | 5204.4 (4216.6 to 6192.1) | 8037.5 (6549.1 to 9488.6) |

## Hours with a queue reaching the leg end (share of hours with >= 10 vehicles unable to enter)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 0.70 (0.68 to 0.71) | 0.00 (0.00 to 0.00) | 0.07 (0.00 to 0.20) | 0.75 (0.50 to 1.00) | 0.94 (0.94 to 0.94) |
| actuated | 0.69 (0.65 to 0.72) | 0.00 (0.00 to 0.00) | 0.07 (0.00 to 0.20) | 0.50 (0.00 to 1.00) | 0.94 (0.91 to 0.98) |
| webster | 0.75 (0.75 to 0.75) | 0.00 (0.00 to 0.00) | 0.07 (0.00 to 0.20) | 1.00 (1.00 to 1.00) | 1.00 (1.00 to 1.00) |
| maxpressure | 0.72 (0.71 to 0.74) | 0.00 (0.00 to 0.00) | 0.07 (0.00 to 0.20) | 1.00 (1.00 to 1.00) | 0.96 (0.94 to 0.99) |
| ars_s0 | 0.71 (0.68 to 0.73) | 0.00 (0.00 to 0.00) | 0.07 (0.00 to 0.20) | 0.75 (0.50 to 1.00) | 0.95 (0.94 to 0.98) |
| lstdq_v2_s0 | 0.72 (0.71 to 0.73) | 0.00 (0.00 to 0.00) | 0.07 (0.00 to 0.20) | 1.00 (1.00 to 1.00) | 0.95 (0.94 to 0.98) |
| qlearn_s0 | 0.72 (0.71 to 0.74) | 0.00 (0.00 to 0.00) | 0.07 (0.00 to 0.20) | 1.00 (1.00 to 1.00) | 0.96 (0.94 to 0.99) |

## How often each controller is best in an hour

| Controller | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|
| gdot | 28 % | 38 % | 33 % | 14 % |
| actuated | 28 % | 31 % | 67 % | 69 % |
| webster | 0 % | 0 % | 0 % | 1 % |
| maxpressure | 0 % | 0 % | 0 % | 7 % |
| ars_s0 | 6 % | 0 % | 0 % | 5 % |
| lstdq_v2_s0 | 11 % | 23 % | 0 % | 3 % |
| qlearn_s0 | 56 % | 38 % | 0 % | 1 % |
