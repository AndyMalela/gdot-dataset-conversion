# RQ1 evaluation: strengths and weaknesses by traffic condition (137, validation weekdays, DEMAND SCALED x1.5: a sensitivity experiment on the real profile, not real traffic)

120 clean hours on 5 days x 1 simulation seeds (seed-averaged per hour). Y = sum of critical flow ratios from the field counts. Intervals: 95 % day-bootstrap. **Limitations (137, 2026-11-16):** uncalibrated driver model; GDOT timing not yet field-validated; WB through from the upstream signal 138; EB/WB right turns run as through; P2/P6 stop-bar presence added in the model; coordinated corridor site (138 at ~260 m) modelled isolated; no pedestrian timing (atsc/sites/137/README.md). Main tables: learnt controllers at one training seed (lstdq_v2_s0 = LSTDQ, qlearn_s0, ars_s0); all training seeds of every learner are in the training-seed tables (simulation seed 1).

Hours per condition: light (Y < 0.15) 24, moderate (0.15-0.30) 8, busy (0.30-0.40) 7, heavy (Y >= 0.40) 81

## Overall mean delay, vehicle-weighted (s/veh)

| Controller | mean delay (95 % interval) |
|---|---|
| gdot | 303.0 (92.4 to 553.8) |
| actuated | 208.1 (57.9 to 385.7) |
| webster | 951.8 (462.1 to 1494.5) |
| maxpressure | 313.4 (152.1 to 503.3) |
| ars_s0 | 358.4 (126.4 to 590.4) |
| lstdq_v2_s0 | 299.9 (103.1 to 526.5) |
| qlearn_s0 | 949.9 (429.8 to 1471.9) |

## Mean delay (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 216.5 (67.8 to 407.7) | 11.2 (10.0 to 12.4) | 14.1 (11.9 to 16.4) | 19.7 (17.5 to 22.4) | 309.6 (95.1 to 576.6) |
| actuated | 150.4 (43.8 to 289.2) | 11.2 (10.0 to 12.4) | 14.3 (11.9 to 16.6) | 18.9 (17.2 to 21.9) | 212.8 (58.9 to 408.6) |
| webster | 672.4 (367.7 to 1011.9) | 22.7 (22.2 to 23.2) | 48.4 (23.8 to 96.4) | 183.6 (26.2 to 481.1) | 985.0 (506.4 to 1559.3) |
| maxpressure | 216.6 (110.6 to 346.9) | 14.2 (11.4 to 17.1) | 15.8 (11.4 to 21.0) | 22.3 (17.2 to 27.4) | 306.6 (156.5 to 489.4) |
| ars_s0 | 254.6 (89.0 to 423.2) | 13.3 (10.9 to 15.7) | 17.1 (12.4 to 23.5) | 42.7 (17.7 to 89.0) | 370.1 (120.7 to 619.4) |
| lstdq_v2_s0 | 213.4 (76.4 to 379.4) | 16.6 (13.2 to 19.8) | 21.5 (15.7 to 27.1) | 26.8 (22.6 to 31.5) | 302.8 (106.3 to 536.8) |
| qlearn_s0 | 685.5 (304.7 to 1066.0) | 11.4 (10.0 to 12.9) | 114.2 (12.5 to 311.5) | 213.3 (18.4 to 584.4) | 980.3 (440.5 to 1504.5) |

## Gain vs Webster (%, negative = less delay than Webster)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 62.7 (-62.6 to 284.7) | -50.7 (-54.7 to -46.8) | -49.4 (-62.0 to -37.1) | -43.4 (-70.9 to -20.6) | 108.5 (-70.6 to 422.6) |
| actuated | 35.4 (-68.5 to 231.0) | -50.7 (-54.7 to -46.8) | -49.2 (-61.8 to -37.1) | -45.9 (-72.0 to -22.5) | 69.3 (-79.3 to 346.2) |
| webster | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| maxpressure | 0.3 (-50.3 to 62.8) | -37.7 (-48.8 to -26.5) | -41.5 (-65.7 to -15.6) | -39.5 (-69.5 to -13.2) | 15.1 (-56.9 to 106.6) |
| ars_s0 | 63.3 (-43.1 to 247.1) | -41.9 (-50.7 to -33.2) | -36.4 (-59.7 to -3.3) | 42.1 (-67.7 to 225.0) | 102.6 (-56.5 to 364.7) |
| lstdq_v2_s0 | 39.6 (-51.3 to 203.2) | -27.2 (-40.1 to -14.4) | -22.9 (-52.7 to 7.0) | -26.5 (-63.5 to 7.2) | 65.0 (-65.7 to 299.0) |
| qlearn_s0 | 284.9 (1.2 to 652.1) | -49.8 (-54.7 to -44.8) | 389.0 (-63.0 to 1258.8) | 807.8 (-63.1 to 2466.5) | 289.9 (20.3 to 563.4) |

## Gain vs actuated (%, negative = less delay than actuated)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 43.9 (32.0 to 56.7) | 0.0 (0.0 to 0.0) | -0.7 (-1.7 to 0.0) | 3.8 (0.5 to 8.8) | 65.2 (46.5 to 85.4) |
| actuated | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| webster | 927.1 (653.2 to 1259.4) | 110.2 (94.2 to 127.1) | 192.5 (65.7 to 408.6) | 968.5 (32.0 to 2718.0) | 1279.8 (874.2 to 1873.1) |
| maxpressure | 131.3 (48.5 to 253.1) | 24.7 (12.3 to 37.0) | 9.9 (-13.2 to 41.7) | 19.8 (-3.1 to 52.4) | 178.7 (57.6 to 348.7) |
| ars_s0 | 134.3 (27.7 to 325.4) | 15.9 (8.1 to 23.3) | 15.3 (1.7 to 38.4) | 99.4 (2.1 to 275.4) | 196.7 (27.8 to 508.5) |
| lstdq_v2_s0 | 68.5 (33.6 to 108.2) | 45.1 (29.9 to 59.6) | 46.5 (25.5 to 69.2) | 42.9 (29.8 to 61.5) | 80.1 (29.7 to 139.2) |
| qlearn_s0 | 817.9 (323.1 to 1657.8) | 1.9 (-2.8 to 7.9) | 732.5 (-4.4 to 2186.1) | 1111.1 (6.2 to 3254.9) | 1015.0 (471.4 to 1900.4) |

## Regret: delay above the best controller in the same hour (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 122.8 (27.4 to 269.4) | 0.5 (0.3 to 0.6) | 0.9 (0.0 to 1.8) | 1.6 (0.6 to 2.3) | 177.3 (41.2 to 382.1) |
| actuated | 56.7 (3.5 to 155.4) | 0.5 (0.3 to 0.6) | 1.0 (0.1 to 2.1) | 0.8 (0.2 to 1.5) | 80.5 (5.1 to 219.3) |
| webster | 578.7 (284.5 to 931.6) | 12.0 (11.1 to 12.8) | 35.1 (9.3 to 83.5) | 165.5 (6.8 to 463.4) | 852.7 (380.8 to 1432.1) |
| maxpressure | 122.9 (38.2 to 233.2) | 3.5 (1.8 to 5.2) | 2.5 (0.0 to 6.7) | 4.2 (1.1 to 8.9) | 174.3 (55.5 to 328.8) |
| ars_s0 | 160.9 (19.1 to 315.8) | 2.5 (1.3 to 3.8) | 3.8 (1.0 to 8.3) | 24.6 (1.4 to 67.7) | 237.8 (24.0 to 457.5) |
| lstdq_v2_s0 | 119.7 (33.4 to 239.8) | 5.9 (3.6 to 8.0) | 8.3 (4.9 to 11.7) | 8.7 (6.7 to 11.2) | 170.5 (47.5 to 338.5) |
| qlearn_s0 | 591.8 (235.9 to 949.9) | 0.7 (0.2 to 1.5) | 100.9 (1.0 to 297.2) | 195.2 (2.2 to 566.5) | 848.0 (345.0 to 1358.0) |

## Worst-off movement: highest 95th-percentile delay of any movement in the hour (s)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 900.7 (398.3 to 1556.0) | 44.6 (42.3 to 46.4) | 53.5 (50.1 to 56.6) | 94.0 (74.8 to 113.7) | 1290.8 (569.1 to 2205.5) |
| actuated | 626.6 (214.1 to 1053.1) | 44.6 (42.3 to 46.4) | 55.0 (51.0 to 58.8) | 70.7 (67.3 to 73.8) | 894.0 (294.5 to 1493.5) |
| webster | 2289.7 (1327.3 to 3364.2) | 60.1 (59.3 to 60.9) | 218.1 (59.3 to 533.3) | 993.2 (76.9 to 1934.3) | 3303.2 (1731.1 to 5144.2) |
| maxpressure | 1491.8 (837.7 to 2298.7) | 101.8 (95.1 to 107.2) | 119.1 (97.0 to 150.6) | 177.7 (107.7 to 292.7) | 2107.7 (1193.4 to 3232.2) |
| ars_s0 | 855.6 (433.1 to 1279.5) | 81.7 (68.8 to 96.2) | 90.1 (64.3 to 132.6) | 327.0 (84.7 to 709.5) | 1213.5 (567.6 to 1859.5) |
| lstdq_v2_s0 | 1272.5 (579.6 to 2010.2) | 116.2 (107.3 to 124.2) | 151.0 (115.6 to 199.1) | 198.9 (140.2 to 288.1) | 1805.6 (818.5 to 2841.4) |
| qlearn_s0 | 2271.8 (1340.4 to 3189.1) | 46.7 (40.6 to 54.3) | 414.6 (68.1 to 1075.0) | 754.6 (128.9 to 1826.5) | 3237.7 (1927.2 to 4536.7) |

## Hours with a queue reaching the leg end (share of hours with >= 10 vehicles unable to enter)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 0.62 (0.59 to 0.64) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.92 (0.86 to 0.96) |
| actuated | 0.57 (0.51 to 0.64) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.84 (0.75 to 0.94) |
| webster | 0.68 (0.62 to 0.72) | 0.00 (0.00 to 0.00) | 0.10 (0.00 to 0.30) | 0.30 (0.00 to 0.70) | 0.96 (0.94 to 0.99) |
| maxpressure | 0.58 (0.53 to 0.63) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.86 (0.80 to 0.92) |
| ars_s0 | 0.66 (0.64 to 0.67) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.30 (0.00 to 0.70) | 0.95 (0.92 to 0.99) |
| lstdq_v2_s0 | 0.61 (0.55 to 0.67) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.90 (0.80 to 0.97) |
| qlearn_s0 | 0.66 (0.62 to 0.70) | 0.00 (0.00 to 0.00) | 0.10 (0.00 to 0.30) | 0.10 (0.00 to 0.30) | 0.95 (0.91 to 0.99) |

## How often each controller is best in an hour

| Controller | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|
| gdot | 29 % | 38 % | 14 % | 4 % |
| actuated | 29 % | 25 % | 43 % | 56 % |
| webster | 0 % | 0 % | 0 % | 9 % |
| maxpressure | 12 % | 38 % | 29 % | 16 % |
| ars_s0 | 8 % | 25 % | 0 % | 7 % |
| lstdq_v2_s0 | 4 % | 0 % | 0 % | 7 % |
| qlearn_s0 | 46 % | 0 % | 14 % | 1 % |
