# RQ1 evaluation: strengths and weaknesses by traffic condition (137, validation weekdays, DEMAND SCALED x1.5: a sensitivity experiment on the real profile, not real traffic)

120 clean hours on 5 days x 1 simulation seeds (seed-averaged per hour). Y = sum of critical flow ratios from the field counts. Intervals: 95 % day-bootstrap. **Limitations (137, 2026-11-16):** uncalibrated driver model; GDOT timing not yet field-validated; WB through from the upstream signal 138; EB/WB right turns run as through; P2/P6 stop-bar presence added in the model; coordinated corridor site (138 at ~260 m) modelled isolated; no pedestrian timing (atsc/sites/137/README.md). Main tables: learnt controllers at one training seed (lstdq_v2_s0 = LSTDQ, qlearn_s0, ars_s0); all training seeds of every learner are in the training-seed tables (simulation seed 1).

Hours per condition: light (Y < 0.15) 24, moderate (0.15-0.30) 9, busy (0.30-0.40) 8, heavy (Y >= 0.40) 79

## Overall mean delay, vehicle-weighted (s/veh)

| Controller | mean delay (95 % interval) |
|---|---|
| gdot | 81.6 (33.0 to 135.3) |
| actuated | 46.0 (25.0 to 79.3) |
| webster | 859.1 (308.1 to 1465.1) |
| maxpressure | 39.1 (25.9 to 57.1) |
| ars_s0 | 45.4 (26.4 to 76.0) |
| lstdq_v2_s0 | 48.9 (25.3 to 85.3) |
| qlearn_s0 | 57.1 (25.0 to 90.3) |

## Mean delay (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 60.6 (27.4 to 99.9) | 11.7 (11.2 to 12.1) | 13.4 (12.3 to 14.6) | 15.4 (13.7 to 17.5) | 83.0 (35.3 to 137.8) |
| actuated | 35.8 (21.4 to 59.4) | 11.7 (11.2 to 12.1) | 13.2 (11.9 to 14.7) | 15.0 (13.3 to 16.6) | 46.4 (26.1 to 79.4) |
| webster | 626.3 (249.3 to 1046.3) | 20.4 (17.9 to 24.8) | 30.1 (19.9 to 40.6) | 279.4 (41.5 to 657.5) | 919.8 (333.2 to 1606.1) |
| maxpressure | 32.1 (23.3 to 44.4) | 17.5 (15.8 to 19.2) | 15.3 (14.1 to 16.6) | 18.7 (14.7 to 23.5) | 39.1 (26.7 to 56.5) |
| ars_s0 | 36.1 (23.0 to 57.9) | 13.4 (12.7 to 14.0) | 14.9 (13.2 to 16.6) | 18.9 (15.4 to 23.1) | 45.9 (27.3 to 76.6) |
| lstdq_v2_s0 | 38.6 (22.4 to 64.7) | 14.2 (13.4 to 15.1) | 16.5 (14.3 to 18.7) | 19.3 (14.3 to 26.4) | 49.2 (26.3 to 85.7) |
| qlearn_s0 | 43.4 (22.0 to 67.2) | 14.2 (13.7 to 14.7) | 15.0 (14.4 to 15.8) | 17.0 (13.8 to 21.0) | 56.8 (26.0 to 90.2) |

## Gain vs Webster (%, negative = less delay than Webster)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | -24.8 (-64.4 to 42.9) | -38.7 (-43.0 to -35.2) | -45.5 (-54.3 to -37.4) | -61.5 (-81.0 to -42.4) | -18.7 (-78.0 to 77.8) |
| actuated | -49.5 (-70.6 to -13.6) | -38.7 (-43.0 to -35.2) | -46.5 (-54.6 to -39.4) | -62.9 (-81.8 to -44.0) | -54.1 (-86.5 to -2.9) |
| webster | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| maxpressure | -51.3 (-63.8 to -34.6) | -7.1 (-19.5 to 5.6) | -36.9 (-49.6 to -25.1) | -59.9 (-81.0 to -37.7) | -67.1 (-86.7 to -41.3) |
| ars_s0 | -46.8 (-67.6 to -12.0) | -30.2 (-36.1 to -25.1) | -39.8 (-48.9 to -31.5) | -58.5 (-79.4 to -37.6) | -53.9 (-86.0 to -3.8) |
| lstdq_v2_s0 | -43.3 (-67.3 to -1.6) | -25.3 (-29.0 to -21.4) | -31.0 (-51.7 to -9.1) | -61.4 (-79.1 to -44.1) | -50.6 (-86.6 to 7.9) |
| qlearn_s0 | -43.6 (-67.7 to -4.2) | -24.8 (-29.4 to -21.2) | -37.7 (-49.5 to -27.0) | -62.3 (-81.3 to -43.3) | -50.6 (-86.2 to 4.1) |

## Gain vs actuated (%, negative = less delay than actuated)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 38.8 (20.3 to 59.2) | 0.0 (0.0 to 0.0) | 1.9 (-0.7 to 6.4) | 3.3 (0.6 to 5.9) | 57.8 (30.3 to 88.4) |
| actuated | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| webster | 2018.6 (920.3 to 3656.6) | 74.0 (57.0 to 99.8) | 116.4 (65.8 to 180.4) | 1708.0 (154.2 to 4194.7) | 2939.0 (1156.4 to 5671.3) |
| maxpressure | 12.7 (6.0 to 19.5) | 51.3 (38.2 to 64.4) | 16.7 (9.6 to 23.8) | 23.8 (6.3 to 54.0) | 0.1 (-5.2 to 5.3) |
| ars_s0 | 7.4 (4.4 to 9.4) | 14.8 (12.9 to 16.8) | 12.9 (10.0 to 15.7) | 23.7 (12.7 to 34.7) | 2.9 (0.3 to 5.2) |
| lstdq_v2_s0 | 9.0 (5.5 to 11.6) | 22.2 (18.1 to 26.8) | 26.6 (4.6 to 55.5) | 27.9 (0.4 to 73.1) | 2.6 (-0.4 to 5.5) |
| qlearn_s0 | 17.5 (4.4 to 36.1) | 22.9 (21.6 to 24.1) | 14.5 (7.2 to 23.3) | 13.7 (1.0 to 37.8) | 16.9 (-0.9 to 42.1) |

## Regret: delay above the best controller in the same hour (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 35.2 (7.0 to 68.8) | 0.0 (0.0 to 0.1) | 0.4 (0.0 to 0.9) | 0.7 (0.4 to 1.2) | 51.3 (10.8 to 98.4) |
| actuated | 10.4 (1.1 to 28.3) | 0.0 (0.0 to 0.1) | 0.1 (0.0 to 0.3) | 0.3 (0.0 to 0.6) | 14.8 (1.6 to 40.1) |
| webster | 600.9 (225.5 to 1021.5) | 8.8 (6.5 to 12.8) | 17.0 (8.0 to 26.9) | 264.7 (27.8 to 642.6) | 888.2 (299.6 to 1573.9) |
| maxpressure | 6.7 (2.8 to 13.4) | 5.9 (4.5 to 7.5) | 2.3 (1.5 to 3.2) | 4.0 (1.1 to 8.5) | 7.4 (1.9 to 17.3) |
| ars_s0 | 10.7 (2.3 to 27.0) | 1.7 (1.5 to 2.0) | 1.8 (1.3 to 2.4) | 4.2 (2.1 to 6.8) | 14.2 (2.3 to 37.4) |
| lstdq_v2_s0 | 13.2 (2.0 to 33.7) | 2.6 (2.1 to 3.1) | 3.4 (0.8 to 6.6) | 4.6 (0.6 to 11.4) | 17.5 (1.9 to 46.3) |
| qlearn_s0 | 18.0 (1.6 to 36.0) | 2.6 (2.4 to 2.8) | 1.9 (1.2 to 2.7) | 2.3 (0.4 to 6.0) | 25.1 (1.6 to 50.4) |

## Worst-off movement: highest 95th-percentile delay of any movement in the hour (s)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 266.1 (162.9 to 391.8) | 37.1 (31.9 to 42.3) | 58.6 (46.1 to 77.8) | 103.2 (94.3 to 114.0) | 369.4 (224.3 to 539.8) |
| actuated | 151.4 (95.8 to 211.3) | 37.1 (31.9 to 42.3) | 50.8 (46.3 to 55.2) | 77.7 (67.0 to 94.5) | 202.1 (124.3 to 284.3) |
| webster | 1719.8 (798.7 to 2740.7) | 67.7 (46.2 to 106.8) | 155.6 (67.4 to 244.9) | 855.4 (209.8 to 1705.0) | 2499.9 (1039.6 to 4201.5) |
| maxpressure | 185.0 (135.9 to 234.1) | 94.0 (89.6 to 99.0) | 89.1 (78.2 to 97.5) | 158.8 (106.0 to 251.1) | 225.5 (158.0 to 293.0) |
| ars_s0 | 169.8 (122.0 to 224.0) | 55.8 (44.1 to 68.1) | 82.1 (70.6 to 94.4) | 139.2 (96.7 to 181.7) | 214.9 (148.5 to 290.1) |
| lstdq_v2_s0 | 192.0 (140.7 to 250.8) | 54.5 (49.3 to 58.2) | 82.2 (61.4 to 103.0) | 167.8 (90.6 to 265.6) | 247.4 (176.4 to 326.7) |
| qlearn_s0 | 363.3 (149.7 to 591.1) | 49.8 (46.8 to 53.7) | 50.8 (45.4 to 56.3) | 111.3 (66.9 to 189.7) | 508.3 (202.6 to 825.6) |

## Hours with a queue reaching the leg end (share of hours with >= 10 vehicles unable to enter)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 0.44 (0.35 to 0.56) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.67 (0.53 to 0.81) |
| actuated | 0.37 (0.25 to 0.48) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.55 (0.39 to 0.72) |
| webster | 0.65 (0.61 to 0.68) | 0.00 (0.00 to 0.00) | 0.10 (0.00 to 0.30) | 0.40 (0.10 to 0.70) | 0.94 (0.88 to 0.99) |
| maxpressure | 0.42 (0.28 to 0.58) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.63 (0.42 to 0.84) |
| ars_s0 | 0.43 (0.33 to 0.57) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.65 (0.50 to 0.82) |
| lstdq_v2_s0 | 0.37 (0.27 to 0.52) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.55 (0.41 to 0.75) |
| qlearn_s0 | 0.32 (0.19 to 0.48) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.48 (0.29 to 0.69) |

## How often each controller is best in an hour

| Controller | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|
| gdot | 92 % | 56 % | 12 % | 0 % |
| actuated | 92 % | 56 % | 62 % | 13 % |
| webster | 0 % | 0 % | 0 % | 3 % |
| maxpressure | 0 % | 0 % | 0 % | 18 % |
| ars_s0 | 0 % | 0 % | 0 % | 6 % |
| lstdq_v2_s0 | 4 % | 11 % | 25 % | 22 % |
| qlearn_s0 | 4 % | 22 % | 0 % | 39 % |
