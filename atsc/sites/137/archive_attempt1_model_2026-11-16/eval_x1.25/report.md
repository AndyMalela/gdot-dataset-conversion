# RQ1 evaluation: strengths and weaknesses by traffic condition (137, validation weekdays, DEMAND SCALED x1.25: a sensitivity experiment on the real profile, not real traffic)

120 clean hours on 5 days x 1 simulation seeds (seed-averaged per hour). Y = sum of critical flow ratios from the field counts. Intervals: 95 % day-bootstrap. **Limitations (137, 2026-11-16):** uncalibrated driver model; GDOT timing not yet field-validated; WB through from the upstream signal 138; EB/WB right turns run as through; P2/P6 stop-bar presence added in the model; coordinated corridor site (138 at ~260 m) modelled isolated; no pedestrian timing (atsc/sites/137/README.md). Main tables: learnt controllers at one training seed (lstdq_v2_s0 = LSTDQ, qlearn_s0, ars_s0); all training seeds of every learner are in the training-seed tables (simulation seed 1).

Hours per condition: light (Y < 0.15) 27, moderate (0.15-0.30) 14, busy (0.30-0.40) 2, heavy (Y >= 0.40) 77

## Overall mean delay, vehicle-weighted (s/veh)

| Controller | mean delay (95 % interval) |
|---|---|
| gdot | 32.2 (23.9 to 42.5) |
| actuated | 21.5 (19.7 to 24.5) |
| webster | 135.7 (47.4 to 284.1) |
| maxpressure | 22.0 (20.3 to 24.5) |
| ars_s0 | 22.4 (20.9 to 24.5) |
| lstdq_v2_s0 | 21.5 (19.8 to 23.7) |
| qlearn_s0 | 22.3 (19.4 to 25.4) |

## Mean delay (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 25.8 (20.7 to 31.6) | 11.4 (10.8 to 12.0) | 13.6 (12.6 to 14.6) | 17.5 (14.8 to 20.2) | 32.9 (25.7 to 41.4) |
| actuated | 18.7 (17.5 to 20.8) | 11.4 (10.8 to 12.0) | 13.1 (12.3 to 14.0) | 14.9 (14.5 to 15.3) | 22.2 (20.7 to 24.9) |
| webster | 99.0 (40.6 to 197.3) | 20.0 (18.2 to 22.9) | 28.6 (21.1 to 36.3) | 69.9 (25.9 to 113.9) | 132.4 (48.7 to 271.0) |
| maxpressure | 20.3 (19.2 to 21.9) | 16.8 (15.9 to 17.8) | 15.4 (14.0 to 16.8) | 15.0 (14.2 to 15.7) | 22.4 (20.9 to 24.7) |
| ars_s0 | 19.9 (19.0 to 21.3) | 13.3 (12.5 to 14.1) | 15.2 (13.3 to 17.3) | 16.4 (16.2 to 16.6) | 23.0 (21.7 to 25.0) |
| lstdq_v2_s0 | 19.4 (18.4 to 20.9) | 14.4 (13.9 to 14.9) | 14.7 (13.6 to 16.1) | 14.9 (14.7 to 15.1) | 21.9 (20.6 to 24.0) |
| qlearn_s0 | 19.6 (17.8 to 21.5) | 13.4 (12.9 to 13.8) | 14.4 (13.8 to 15.0) | 16.4 (16.0 to 16.9) | 22.6 (20.1 to 25.2) |

## Gain vs Webster (%, negative = less delay than Webster)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | -37.7 (-48.9 to -26.6) | -41.1 (-44.9 to -37.8) | -43.2 (-48.8 to -37.8) | -62.6 (-82.3 to -42.9) | -34.2 (-53.3 to -15.1) |
| actuated | -47.8 (-54.2 to -41.4) | -41.1 (-44.9 to -37.8) | -45.2 (-52.5 to -38.0) | -65.4 (-86.6 to -44.2) | -49.9 (-61.2 to -38.3) |
| webster | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| maxpressure | -40.2 (-46.8 to -34.9) | -12.5 (-19.6 to -5.3) | -37.3 (-45.0 to -27.6) | -65.7 (-86.2 to -45.2) | -49.5 (-60.6 to -38.3) |
| ars_s0 | -42.9 (-49.7 to -36.3) | -31.8 (-36.3 to -27.9) | -38.4 (-47.5 to -28.3) | -61.5 (-85.5 to -37.5) | -47.0 (-58.7 to -35.1) |
| lstdq_v2_s0 | -43.7 (-50.0 to -37.9) | -25.6 (-30.6 to -21.2) | -38.8 (-50.0 to -27.6) | -65.0 (-86.7 to -43.3) | -50.2 (-61.5 to -38.8) |
| qlearn_s0 | -45.2 (-51.3 to -39.5) | -30.6 (-36.6 to -26.7) | -39.2 (-47.8 to -29.9) | -60.3 (-86.0 to -34.7) | -50.7 (-61.5 to -39.5) |

## Gain vs actuated (%, negative = less delay than actuated)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 27.5 (11.9 to 50.0) | 0.0 (0.0 to 0.0) | 4.0 (0.1 to 8.0) | 17.2 (2.3 to 32.1) | 41.4 (18.4 to 74.3) |
| actuated | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| webster | 281.4 (124.5 to 519.8) | 74.8 (63.5 to 91.4) | 114.5 (66.1 to 168.8) | 362.0 (79.2 to 644.8) | 363.1 (125.4 to 704.0) |
| maxpressure | 14.1 (10.0 to 18.4) | 48.9 (39.3 to 61.5) | 18.7 (8.6 to 32.4) | 0.5 (-1.9 to 2.9) | 1.8 (0.8 to 3.2) |
| ars_s0 | 9.3 (7.4 to 10.8) | 16.6 (14.4 to 19.1) | 14.8 (8.1 to 20.3) | 10.1 (8.3 to 11.9) | 5.4 (4.1 to 6.8) |
| lstdq_v2_s0 | 7.5 (5.7 to 10.1) | 27.2 (22.0 to 35.3) | 13.0 (7.1 to 17.1) | 0.3 (-1.1 to 1.6) | -0.3 (-1.3 to 0.6) |
| qlearn_s0 | 6.4 (2.7 to 12.1) | 17.8 (13.8 to 21.2) | 10.6 (6.7 to 13.3) | 10.7 (4.3 to 17.0) | 1.6 (-2.8 to 9.3) |

## Regret: delay above the best controller in the same hour (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 8.0 (3.8 to 13.6) | 0.0 (0.0 to 0.1) | 0.9 (0.3 to 1.4) | 2.8 (0.6 to 5.1) | 12.0 (5.8 to 20.3) |
| actuated | 0.9 (0.6 to 1.6) | 0.0 (0.0 to 0.1) | 0.3 (0.1 to 0.6) | 0.2 (0.2 to 0.3) | 1.4 (0.8 to 2.3) |
| webster | 81.2 (23.5 to 178.1) | 8.6 (7.1 to 11.1) | 15.9 (8.6 to 23.2) | 55.3 (11.7 to 98.8) | 111.6 (29.1 to 248.4) |
| maxpressure | 2.5 (2.1 to 2.9) | 5.4 (4.4 to 6.6) | 2.7 (1.3 to 4.6) | 0.3 (0.0 to 0.6) | 1.6 (1.2 to 2.1) |
| ars_s0 | 2.2 (1.9 to 2.4) | 1.9 (1.6 to 2.2) | 2.5 (1.4 to 3.4) | 1.7 (1.4 to 2.0) | 2.1 (1.8 to 2.5) |
| lstdq_v2_s0 | 1.6 (1.4 to 1.9) | 3.0 (2.6 to 3.6) | 2.0 (1.1 to 2.6) | 0.3 (0.0 to 0.5) | 1.1 (0.8 to 1.5) |
| qlearn_s0 | 1.9 (0.8 to 3.4) | 2.0 (1.6 to 2.3) | 1.7 (1.1 to 2.2) | 1.8 (0.8 to 2.7) | 1.8 (0.4 to 3.9) |

## Worst-off movement: highest 95th-percentile delay of any movement in the hour (s)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 133.6 (113.1 to 156.2) | 34.6 (29.3 to 39.8) | 83.7 (70.9 to 96.5) | 99.7 (69.3 to 130.1) | 177.7 (150.7 to 205.9) |
| actuated | 81.2 (76.5 to 89.0) | 34.6 (29.3 to 39.8) | 55.6 (50.5 to 61.5) | 59.1 (58.9 to 59.3) | 102.6 (96.2 to 110.9) |
| webster | 362.2 (160.7 to 723.1) | 58.5 (47.1 to 79.0) | 147.7 (83.2 to 212.2) | 325.7 (62.5 to 588.9) | 481.2 (185.4 to 1000.3) |
| maxpressure | 103.2 (89.5 to 116.8) | 91.4 (88.3 to 95.7) | 104.5 (77.7 to 141.4) | 59.7 (59.1 to 60.2) | 108.4 (93.0 to 123.9) |
| ars_s0 | 95.1 (87.0 to 103.5) | 56.3 (47.3 to 66.7) | 96.9 (87.8 to 108.4) | 85.7 (75.4 to 96.0) | 108.0 (97.5 to 117.1) |
| lstdq_v2_s0 | 108.7 (98.1 to 120.1) | 54.5 (47.6 to 61.3) | 92.7 (77.7 to 117.4) | 90.5 (75.9 to 105.1) | 130.6 (116.1 to 145.1) |
| qlearn_s0 | 105.7 (77.3 to 137.3) | 41.2 (37.7 to 43.8) | 65.0 (56.9 to 72.9) | 71.4 (55.3 to 87.5) | 134.5 (95.3 to 180.7) |

## Hours with a queue reaching the leg end (share of hours with >= 10 vehicles unable to enter)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 0.18 (0.12 to 0.27) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.28 (0.19 to 0.38) |
| actuated | 0.13 (0.07 to 0.22) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.20 (0.11 to 0.32) |
| webster | 0.42 (0.32 to 0.53) | 0.00 (0.00 to 0.00) | 0.10 (0.00 to 0.30) | 0.50 (0.00 to 1.00) | 0.63 (0.45 to 0.81) |
| maxpressure | 0.18 (0.09 to 0.30) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.28 (0.14 to 0.44) |
| ars_s0 | 0.21 (0.09 to 0.36) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.31 (0.14 to 0.52) |
| lstdq_v2_s0 | 0.12 (0.05 to 0.20) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.18 (0.08 to 0.28) |
| qlearn_s0 | 0.09 (0.02 to 0.17) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.14 (0.04 to 0.25) |

## How often each controller is best in an hour

| Controller | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|
| gdot | 89 % | 36 % | 0 % | 1 % |
| actuated | 89 % | 50 % | 0 % | 17 % |
| webster | 0 % | 0 % | 0 % | 0 % |
| maxpressure | 0 % | 7 % | 50 % | 18 % |
| ars_s0 | 0 % | 7 % | 0 % | 9 % |
| lstdq_v2_s0 | 4 % | 14 % | 50 % | 18 % |
| qlearn_s0 | 7 % | 7 % | 0 % | 36 % |
