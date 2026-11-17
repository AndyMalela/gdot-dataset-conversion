# RQ1 evaluation: strengths and weaknesses by traffic condition (137, validation weekdays, DEMAND SCALED x2: a sensitivity experiment on the real profile, not real traffic)

120 clean hours on 5 days x 1 simulation seeds (seed-averaged per hour). Y = sum of critical flow ratios from the field counts. Intervals: 95 % day-bootstrap. **Limitations (137, 2026-11-16):** uncalibrated driver model; GDOT timing not yet field-validated; WB through from the upstream signal 138; EB/WB right turns run as through; P2/P6 stop-bar presence added in the model; coordinated corridor site (138 at ~260 m) modelled isolated; no pedestrian timing (atsc/sites/137/README.md). Main tables: learnt controllers at one training seed (lstdq_v2_s0 = LSTDQ, qlearn_s0, ars_s0); all training seeds of every learner are in the training-seed tables (simulation seed 1).

Hours per condition: light (Y < 0.15) 15, moderate (0.15-0.30) 15, busy (0.30-0.40) 2, heavy (Y >= 0.40) 88

## Overall mean delay, vehicle-weighted (s/veh)

| Controller | mean delay (95 % interval) |
|---|---|
| gdot | 2512.5 (1963.4 to 3057.9) |
| actuated | 2244.6 (1682.7 to 2806.4) |
| webster | 2773.4 (2576.4 to 2967.3) |
| maxpressure | 2613.5 (2239.6 to 3013.5) |
| ars_s0 | 2554.2 (2182.1 to 2928.4) |
| lstdq_v2_s0 | 2444.1 (1863.5 to 3026.3) |
| qlearn_s0 | 4417.4 (4175.1 to 4659.7) |

## Mean delay (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 1756.0 (1456.3 to 2062.4) | 11.5 (10.2 to 12.3) | 14.2 (12.6 to 16.2) | 753.2 (17.4 to 1488.9) | 2377.8 (1948.6 to 2857.0) |
| actuated | 1561.0 (1207.8 to 1940.7) | 11.5 (10.2 to 12.3) | 14.2 (12.6 to 16.2) | 132.7 (20.6 to 244.7) | 2127.1 (1631.4 to 2693.9) |
| webster | 1845.0 (1690.2 to 2015.3) | 24.1 (22.8 to 26.1) | 26.2 (24.7 to 28.3) | 35.8 (22.5 to 49.1) | 2506.4 (2272.8 to 2729.5) |
| maxpressure | 1800.7 (1498.3 to 2104.7) | 14.7 (11.5 to 17.8) | 19.1 (12.6 to 25.7) | 51.0 (35.9 to 66.2) | 2453.8 (2014.9 to 2898.3) |
| ars_s0 | 1804.1 (1582.1 to 2050.0) | 12.6 (11.1 to 14.0) | 22.1 (13.5 to 37.5) | 872.8 (15.1 to 1730.4) | 2439.4 (2107.1 to 2811.5) |
| lstdq_v2_s0 | 1693.4 (1302.1 to 2107.3) | 18.2 (13.6 to 24.4) | 29.4 (17.5 to 42.5) | 264.2 (17.7 to 510.8) | 2301.4 (1741.2 to 2913.1) |
| qlearn_s0 | 2856.8 (2666.2 to 3052.4) | 12.2 (10.1 to 14.6) | 21.6 (12.2 to 31.5) | 21.3 (11.9 to 30.8) | 3891.7 (3633.8 to 4150.1) |

## Gain vs Webster (%, negative = less delay than Webster)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 136.2 (2.2 to 337.8) | -51.8 (-56.1 to -48.7) | -45.2 (-50.8 to -36.5) | 1454.1 (-22.8 to 2931.1) | 174.4 (4.9 to 474.2) |
| actuated | 154.3 (-18.3 to 449.8) | -51.8 (-56.1 to -48.7) | -45.2 (-50.8 to -36.5) | 194.9 (-8.3 to 398.2) | 229.2 (-15.5 to 649.0) |
| webster | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| maxpressure | 141.8 (-7.7 to 412.5) | -38.2 (-51.6 to -24.6) | -30.2 (-49.2 to -11.0) | 83.6 (-26.8 to 194.1) | 209.4 (-2.1 to 588.7) |
| ars_s0 | 219.9 (33.7 to 489.9) | -47.0 (-52.4 to -41.6) | -14.3 (-48.0 to 47.3) | 1694.9 (-32.8 to 3422.6) | 277.5 (31.1 to 683.1) |
| lstdq_v2_s0 | 181.2 (5.2 to 505.3) | -23.3 (-42.2 to 2.5) | 10.0 (-30.6 to 63.4) | 459.1 (-21.5 to 939.8) | 246.1 (-12.3 to 715.5) |
| qlearn_s0 | 95.7 (29.7 to 220.0) | -48.7 (-56.9 to -39.3) | -21.4 (-50.8 to 17.4) | -42.2 (-46.9 to -37.4) | 146.2 (50.6 to 324.1) |

## Gain vs actuated (%, negative = less delay than actuated)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 51.9 (6.6 to 108.6) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 246.3 (-15.8 to 508.4) | 64.6 (9.5 to 140.3) |
| actuated | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| webster | 78.1 (58.3 to 106.4) | 116.5 (98.0 to 138.0) | 94.1 (69.3 to 108.4) | -35.4 (-79.9 to 9.1) | 71.2 (36.9 to 117.1) |
| maxpressure | 113.2 (69.1 to 171.4) | 25.8 (5.1 to 51.4) | 25.2 (-2.2 to 54.4) | 67.7 (-85.3 to 220.8) | 145.6 (83.5 to 223.4) |
| ars_s0 | 73.8 (27.8 to 122.4) | 9.9 (3.3 to 14.5) | 39.2 (5.2 to 101.3) | 290.2 (-26.7 to 607.1) | 85.9 (28.0 to 147.2) |
| lstdq_v2_s0 | 39.3 (25.9 to 52.8) | 56.0 (28.2 to 103.1) | 85.5 (32.6 to 138.4) | 47.2 (-14.3 to 108.7) | 28.1 (12.7 to 48.4) |
| qlearn_s0 | 115.5 (68.7 to 162.3) | 6.3 (-5.0 to 22.2) | 37.0 (-3.6 to 82.2) | -64.8 (-87.4 to -42.1) | 151.3 (90.4 to 212.3) |

## Regret: delay above the best controller in the same hour (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 885.7 (674.9 to 1090.2) | 0.6 (0.4 to 0.9) | 0.9 (0.6 to 1.2) | 731.8 (5.4 to 1458.2) | 1192.7 (886.3 to 1499.2) |
| actuated | 690.8 (420.8 to 962.1) | 0.6 (0.4 to 0.9) | 0.9 (0.6 to 1.2) | 111.3 (8.7 to 214.0) | 942.0 (568.7 to 1336.6) |
| webster | 974.8 (769.6 to 1222.6) | 13.3 (11.9 to 15.2) | 12.9 (9.8 to 15.6) | 14.5 (10.6 to 18.4) | 1321.3 (1056.0 to 1639.8) |
| maxpressure | 930.4 (698.9 to 1170.6) | 3.8 (1.4 to 6.6) | 5.9 (1.0 to 11.5) | 29.7 (5.2 to 54.2) | 1268.7 (952.8 to 1589.6) |
| ars_s0 | 933.9 (764.7 to 1111.0) | 1.7 (1.2 to 2.2) | 8.8 (1.8 to 21.8) | 851.4 (3.2 to 1699.6) | 1254.3 (1015.0 to 1493.6) |
| lstdq_v2_s0 | 823.1 (504.1 to 1142.2) | 7.4 (3.9 to 12.8) | 16.1 (5.9 to 26.8) | 242.9 (5.7 to 480.0) | 1116.3 (672.7 to 1574.5) |
| qlearn_s0 | 1986.6 (1795.8 to 2253.2) | 1.4 (0.3 to 3.1) | 8.3 (0.5 to 16.5) | 0.0 (0.0 to 0.0) | 2706.6 (2432.4 to 3039.2) |

## Worst-off movement: highest 95th-percentile delay of any movement in the hour (s)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 5308.7 (4691.2 to 5926.2) | 45.8 (42.1 to 51.4) | 57.7 (54.0 to 62.6) | 2806.9 (98.6 to 5515.1) | 7151.7 (6332.8 to 7970.6) |
| actuated | 5037.0 (4563.5 to 5465.1) | 45.8 (42.1 to 51.4) | 57.7 (54.0 to 62.6) | 802.7 (119.0 to 1486.4) | 6823.3 (6208.7 to 7337.2) |
| webster | 5949.8 (5258.5 to 6614.3) | 65.7 (59.7 to 74.5) | 71.8 (61.5 to 91.5) | 251.4 (58.7 to 444.2) | 8089.1 (7080.6 to 8900.7) |
| maxpressure | 9985.7 (8956.4 to 10861.8) | 111.3 (95.1 to 129.6) | 136.3 (105.8 to 166.1) | 589.6 (288.5 to 890.8) | 13576.2 (12054.7 to 14745.8) |
| ars_s0 | 5525.4 (5105.0 to 5962.7) | 81.5 (75.7 to 87.6) | 144.1 (75.5 to 271.1) | 2839.3 (80.4 to 5598.2) | 7418.8 (6820.2 to 7954.5) |
| lstdq_v2_s0 | 6337.1 (5566.5 to 7194.2) | 130.5 (105.8 to 168.3) | 239.1 (142.8 to 339.7) | 1029.3 (96.2 to 1962.5) | 8552.6 (7468.6 to 9656.3) |
| qlearn_s0 | 7857.9 (7463.6 to 8312.7) | 53.1 (41.7 to 70.4) | 128.7 (55.2 to 211.2) | 118.9 (32.8 to 205.0) | 10695.1 (10050.5 to 11455.9) |

## Hours with a queue reaching the leg end (share of hours with >= 10 vehicles unable to enter)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 0.72 (0.67 to 0.75) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.50 (0.00 to 1.00) | 0.97 (0.92 to 1.00) |
| actuated | 0.69 (0.66 to 0.71) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.50 (0.00 to 1.00) | 0.93 (0.91 to 0.94) |
| webster | 0.72 (0.69 to 0.74) | 0.00 (0.00 to 0.00) | 0.10 (0.00 to 0.30) | 0.50 (0.00 to 1.00) | 0.95 (0.92 to 0.99) |
| maxpressure | 0.70 (0.68 to 0.71) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.50 (0.00 to 1.00) | 0.94 (0.94 to 0.94) |
| ars_s0 | 0.75 (0.72 to 0.79) | 0.00 (0.00 to 0.00) | 0.10 (0.00 to 0.30) | 0.50 (0.00 to 1.00) | 0.99 (0.96 to 1.00) |
| lstdq_v2_s0 | 0.71 (0.67 to 0.74) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.50 (0.00 to 1.00) | 0.95 (0.92 to 0.99) |
| qlearn_s0 | 0.70 (0.66 to 0.74) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.95 (0.91 to 1.00) |

## How often each controller is best in an hour

| Controller | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|
| gdot | 40 % | 33 % | 0 % | 6 % |
| actuated | 40 % | 33 % | 0 % | 42 % |
| webster | 0 % | 0 % | 0 % | 9 % |
| maxpressure | 13 % | 47 % | 0 % | 22 % |
| ars_s0 | 7 % | 0 % | 0 % | 5 % |
| lstdq_v2_s0 | 0 % | 0 % | 0 % | 8 % |
| qlearn_s0 | 40 % | 20 % | 100 % | 9 % |
