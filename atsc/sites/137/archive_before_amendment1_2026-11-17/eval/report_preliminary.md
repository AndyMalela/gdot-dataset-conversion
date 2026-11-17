# RQ1 evaluation: strengths and weaknesses by traffic condition (137, validation weekdays)

120 clean hours on 5 days x 1 simulation seeds (seed-averaged per hour). Y = sum of critical flow ratios from the field counts. Intervals: 95 % day-bootstrap. **Limitations (137, 2026-11-16):** uncalibrated driver model; GDOT timing not yet field-validated; WB through from the upstream signal 138; EB/WB right turns run as through; P2/P6 stop-bar presence added in the model; coordinated corridor site (138 at ~260 m) modelled isolated; no pedestrian timing (atsc/sites/137/README.md). Main tables: learnt controllers at one training seed (lstdq_v2_s0 = LSTDQ, qlearn_s0, ars_s0); all training seeds of every learner are in the training-seed tables (simulation seed 1).

Hours per condition: light (Y < 0.15) 30, moderate (0.15-0.30) 11, busy (0.30-0.40) 4, heavy (Y >= 0.40) 75

## Overall mean delay, vehicle-weighted (s/veh)

| Controller | mean delay (95 % interval) |
|---|---|
| gdot | 28.5 (26.1 to 31.2) |
| actuated | 25.2 (24.4 to 26.4) |
| webster | 74.5 (31.0 to 160.4) |
| maxpressure | 22.9 (21.9 to 24.2) |
| ars_s0 | 44.2 (24.5 to 81.0) |
| lstdq_v2_s0 | 32.5 (24.4 to 44.0) |
| qlearn_s0 | 35.4 (23.9 to 53.8) |

## Mean delay (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 24.0 (22.2 to 25.8) | 12.5 (11.5 to 13.8) | 17.5 (15.9 to 20.1) | 20.9 (18.0 to 24.1) | 29.5 (27.4 to 31.5) |
| actuated | 21.6 (20.9 to 22.5) | 12.5 (11.5 to 13.8) | 16.7 (15.3 to 18.3) | 17.9 (16.7 to 19.0) | 26.1 (25.6 to 27.0) |
| webster | 64.1 (29.2 to 133.3) | 24.2 (23.7 to 24.9) | 26.6 (25.4 to 27.8) | 32.1 (28.0 to 36.2) | 80.9 (31.7 to 178.2) |
| maxpressure | 20.6 (19.6 to 21.4) | 14.6 (12.5 to 17.0) | 17.2 (14.5 to 19.9) | 19.0 (15.7 to 22.2) | 23.4 (22.5 to 24.5) |
| ars_s0 | 35.9 (21.7 to 63.1) | 13.9 (13.1 to 15.0) | 18.0 (16.1 to 20.7) | 19.5 (17.8 to 21.3) | 45.6 (25.4 to 83.9) |
| lstdq_v2_s0 | 26.8 (22.2 to 33.0) | 16.1 (14.1 to 18.2) | 18.6 (17.0 to 20.5) | 20.9 (17.8 to 25.8) | 32.3 (25.1 to 42.2) |
| qlearn_s0 | 28.4 (21.1 to 40.5) | 12.6 (11.6 to 14.0) | 16.2 (14.5 to 18.9) | 27.2 (16.9 to 45.3) | 35.4 (24.5 to 52.9) |

## Gain vs Webster (%, negative = less delay than Webster)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | -24.5 (-31.1 to -18.9) | -48.0 (-52.9 to -41.9) | -33.4 (-41.6 to -20.3) | -34.2 (-45.8 to -26.6) | -13.3 (-21.9 to -6.4) |
| actuated | -30.3 (-35.0 to -26.3) | -48.0 (-52.9 to -41.9) | -36.9 (-43.6 to -27.4) | -43.6 (-49.7 to -37.5) | -21.5 (-27.8 to -17.7) |
| webster | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| maxpressure | -33.0 (-38.3 to -28.0) | -38.9 (-48.3 to -28.4) | -34.5 (-46.7 to -22.4) | -38.4 (-56.3 to -20.6) | -30.2 (-35.8 to -26.1) |
| ars_s0 | -22.5 (-26.9 to -16.8) | -42.2 (-45.8 to -37.0) | -31.6 (-40.4 to -17.7) | -37.9 (-46.4 to -25.5) | -13.5 (-19.1 to -5.3) |
| lstdq_v2_s0 | -17.6 (-30.4 to 0.7) | -32.6 (-41.7 to -23.5) | -29.4 (-37.6 to -18.5) | -32.6 (-50.4 to -13.6) | -9.2 (-28.0 to 19.3) |
| qlearn_s0 | -27.4 (-33.2 to -21.9) | -47.4 (-52.3 to -40.9) | -38.2 (-47.1 to -24.4) | -8.9 (-53.2 to 61.1) | -18.9 (-26.3 to -10.3) |

## Gain vs actuated (%, negative = less delay than actuated)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 8.6 (4.9 to 11.5) | 0.0 (0.0 to 0.0) | 5.1 (-1.1 to 11.5) | 16.3 (4.9 to 26.6) | 11.9 (6.7 to 15.9) |
| actuated | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| webster | 187.1 (42.9 to 465.3) | 100.4 (80.1 to 118.6) | 61.9 (41.6 to 78.3) | 79.6 (60.1 to 99.2) | 220.7 (24.1 to 610.4) |
| maxpressure | -1.9 (-4.6 to 0.8) | 16.0 (7.0 to 25.3) | 3.8 (-9.8 to 20.3) | 7.0 (-13.2 to 27.3) | -10.7 (-12.7 to -8.9) |
| ars_s0 | 53.0 (3.9 to 148.0) | 12.7 (8.7 to 16.9) | 7.3 (4.1 to 11.8) | 10.2 (-4.1 to 24.4) | 69.1 (-1.0 to 203.4) |
| lstdq_v2_s0 | 21.4 (7.0 to 42.5) | 27.8 (19.4 to 36.7) | 11.9 (7.5 to 17.0) | 17.2 (-1.2 to 40.3) | 19.6 (-2.1 to 51.1) |
| qlearn_s0 | 21.9 (0.1 to 58.0) | 1.0 (-0.8 to 3.0) | -3.3 (-7.8 to 2.8) | 56.3 (-7.0 to 168.4) | 28.5 (-4.7 to 81.6) |

## Regret: delay above the best controller in the same hour (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 4.6 (3.7 to 5.3) | 0.7 (0.4 to 0.9) | 2.5 (1.6 to 3.5) | 4.4 (3.1 to 6.4) | 6.4 (5.2 to 7.5) |
| actuated | 2.2 (2.0 to 2.5) | 0.7 (0.4 to 0.9) | 1.6 (1.0 to 2.2) | 1.4 (0.4 to 2.6) | 3.0 (2.7 to 3.4) |
| webster | 44.7 (9.9 to 113.1) | 12.4 (10.5 to 14.0) | 11.6 (8.6 to 14.1) | 15.6 (11.0 to 20.3) | 57.8 (9.1 to 154.2) |
| maxpressure | 1.2 (0.8 to 1.5) | 2.8 (1.7 to 3.9) | 2.2 (0.6 to 4.2) | 2.6 (0.0 to 5.2) | 0.3 (0.1 to 0.4) |
| ars_s0 | 16.5 (2.8 to 42.9) | 2.1 (1.6 to 2.7) | 3.0 (1.9 to 4.0) | 3.1 (0.6 to 5.6) | 22.5 (2.9 to 59.8) |
| lstdq_v2_s0 | 7.4 (3.2 to 13.7) | 4.3 (3.3 to 5.3) | 3.6 (3.0 to 4.2) | 4.5 (1.4 to 8.9) | 9.2 (2.6 to 19.0) |
| qlearn_s0 | 9.0 (2.3 to 20.5) | 0.8 (0.7 to 0.9) | 1.2 (0.5 to 2.0) | 10.8 (1.0 to 28.7) | 12.3 (2.1 to 28.7) |

## Worst-off movement: highest 95th-percentile delay of any movement in the hour (s)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 125.5 (113.5 to 136.6) | 42.2 (39.4 to 44.8) | 88.1 (70.0 to 108.0) | 109.9 (76.1 to 138.4) | 165.0 (151.5 to 177.1) |
| actuated | 73.1 (70.1 to 76.1) | 42.2 (39.4 to 44.8) | 57.9 (55.3 to 61.4) | 58.8 (56.8 to 61.5) | 88.2 (85.0 to 91.1) |
| webster | 186.5 (86.5 to 377.1) | 62.7 (60.6 to 64.6) | 73.0 (69.1 to 78.0) | 133.7 (85.3 to 206.4) | 237.8 (96.8 to 506.0) |
| maxpressure | 114.8 (106.4 to 124.0) | 98.5 (93.0 to 105.0) | 124.1 (85.9 to 174.6) | 101.5 (77.8 to 124.8) | 119.9 (108.9 to 132.4) |
| ars_s0 | 130.4 (83.1 to 213.0) | 66.5 (63.3 to 69.0) | 74.8 (62.6 to 91.1) | 77.2 (58.8 to 107.4) | 158.8 (92.1 to 275.1) |
| lstdq_v2_s0 | 175.3 (129.0 to 229.7) | 101.6 (97.8 to 105.3) | 117.3 (105.9 to 130.7) | 122.5 (93.6 to 168.5) | 212.8 (143.4 to 299.0) |
| qlearn_s0 | 136.5 (101.9 to 171.6) | 45.3 (42.9 to 47.6) | 76.7 (57.7 to 97.7) | 227.8 (65.5 to 519.5) | 173.0 (123.5 to 223.6) |

## Hours with a queue reaching the leg end (share of hours with >= 10 vehicles unable to enter)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 0.10 (0.03 to 0.17) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.15 (0.06 to 0.25) |
| actuated | 0.07 (0.02 to 0.13) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.11 (0.04 to 0.19) |
| webster | 0.24 (0.13 to 0.36) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.50 (0.00 to 1.00) | 0.35 (0.19 to 0.51) |
| maxpressure | 0.02 (0.00 to 0.06) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.04 (0.00 to 0.08) |
| ars_s0 | 0.21 (0.11 to 0.37) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.32 (0.18 to 0.53) |
| lstdq_v2_s0 | 0.07 (0.01 to 0.15) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.11 (0.01 to 0.22) |
| qlearn_s0 | 0.13 (0.07 to 0.18) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.25 (0.00 to 0.75) | 0.20 (0.11 to 0.28) |

## How often each controller is best in an hour

| Controller | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|
| gdot | 30 % | 9 % | 0 % | 4 % |
| actuated | 30 % | 9 % | 25 % | 4 % |
| webster | 0 % | 0 % | 0 % | 0 % |
| maxpressure | 20 % | 36 % | 50 % | 65 % |
| ars_s0 | 13 % | 0 % | 25 % | 7 % |
| lstdq_v2_s0 | 7 % | 0 % | 0 % | 3 % |
| qlearn_s0 | 30 % | 45 % | 0 % | 17 % |
