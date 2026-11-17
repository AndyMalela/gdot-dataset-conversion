# RQ1 evaluation: strengths and weaknesses by traffic condition (137, validation weekdays)

120 clean hours on 5 days x 1 simulation seeds (seed-averaged per hour). Y = sum of critical flow ratios from the field counts. Intervals: 95 % day-bootstrap. **Limitations (137, 2026-11-16):** uncalibrated driver model; GDOT timing not yet field-validated; WB through from the upstream signal 138; EB/WB right turns run as through; P2/P6 stop-bar presence added in the model; coordinated corridor site (138 at ~260 m) modelled isolated; no pedestrian timing (atsc/sites/137/README.md). Main tables: learnt controllers at one training seed (lstdq_v2_s0 = LSTDQ, qlearn_s0, ars_s0); all training seeds of every learner are in the training-seed tables (simulation seed 1).

Hours per condition: light (Y < 0.15) 30, moderate (0.15-0.30) 13, busy (0.30-0.40) 18, heavy (Y >= 0.40) 59

## Overall mean delay, vehicle-weighted (s/veh)

| Controller | mean delay (95 % interval) |
|---|---|
| gdot | 20.9 (19.7 to 22.1) |
| actuated | 17.0 (16.5 to 17.7) |
| webster | 67.2 (23.2 to 153.8) |
| maxpressure | 17.8 (17.4 to 18.4) |
| ars_s0 | 18.3 (17.8 to 19.0) |
| lstdq_v2_s0 | 17.5 (16.9 to 18.2) |
| qlearn_s0 | 17.1 (16.6 to 17.7) |

## Mean delay (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 18.4 (17.6 to 19.3) | 11.6 (11.2 to 12.0) | 13.2 (11.8 to 14.9) | 22.4 (18.1 to 27.7) | 22.5 (20.8 to 24.7) |
| actuated | 15.5 (15.2 to 16.0) | 11.6 (11.2 to 12.0) | 12.6 (11.7 to 13.7) | 15.8 (14.7 to 17.0) | 18.1 (17.5 to 18.8) |
| webster | 57.1 (22.0 to 126.2) | 18.6 (17.6 to 20.0) | 20.7 (19.0 to 23.1) | 24.0 (22.7 to 25.6) | 73.6 (23.7 to 171.1) |
| maxpressure | 17.5 (17.2 to 17.8) | 17.4 (16.2 to 18.8) | 14.2 (13.3 to 15.1) | 16.2 (15.6 to 16.8) | 18.6 (18.0 to 19.3) |
| ars_s0 | 16.9 (16.6 to 17.3) | 13.2 (12.8 to 13.5) | 13.5 (12.5 to 15.1) | 17.1 (16.6 to 17.7) | 19.4 (18.8 to 20.1) |
| lstdq_v2_s0 | 16.4 (16.0 to 16.9) | 14.1 (13.5 to 14.5) | 12.9 (11.0 to 15.2) | 16.2 (15.1 to 17.3) | 18.4 (17.5 to 19.4) |
| qlearn_s0 | 16.2 (15.8 to 16.6) | 13.9 (13.6 to 14.3) | 13.4 (12.6 to 14.7) | 16.3 (15.7 to 17.2) | 17.9 (17.3 to 18.4) |

## Gain vs Webster (%, negative = less delay than Webster)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | -21.1 (-29.6 to -14.8) | -37.0 (-39.7 to -34.3) | -35.4 (-38.5 to -31.5) | -5.0 (-20.5 to 9.8) | -12.0 (-24.4 to -2.8) |
| actuated | -33.1 (-37.6 to -29.9) | -37.0 (-39.7 to -34.3) | -38.4 (-41.5 to -35.2) | -32.3 (-36.0 to -30.2) | -29.2 (-36.6 to -24.5) |
| webster | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| maxpressure | -22.9 (-29.3 to -17.5) | -4.7 (-12.0 to 4.9) | -30.3 (-34.3 to -25.1) | -30.4 (-32.6 to -28.2) | -27.3 (-34.7 to -22.3) |
| ars_s0 | -27.0 (-32.3 to -23.1) | -28.3 (-31.7 to -25.0) | -33.9 (-37.8 to -29.9) | -26.6 (-28.4 to -24.8) | -23.9 (-32.1 to -18.4) |
| lstdq_v2_s0 | -28.8 (-34.4 to -24.9) | -23.5 (-27.4 to -19.7) | -37.1 (-42.7 to -31.8) | -30.7 (-34.5 to -28.5) | -28.5 (-36.1 to -24.4) |
| qlearn_s0 | -29.3 (-34.0 to -25.6) | -23.9 (-29.9 to -18.0) | -34.0 (-36.8 to -31.5) | -29.8 (-31.8 to -28.4) | -30.0 (-37.4 to -25.0) |

## Gain vs actuated (%, negative = less delay than actuated)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 17.0 (11.0 to 23.2) | 0.0 (0.0 to 0.0) | 5.1 (-3.1 to 11.9) | 39.9 (22.8 to 60.7) | 24.0 (15.8 to 32.7) |
| actuated | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| webster | 243.3 (46.9 to 630.4) | 61.3 (53.5 to 69.0) | 64.7 (55.5 to 72.5) | 53.0 (46.3 to 59.7) | 312.4 (35.1 to 861.2) |
| maxpressure | 16.1 (13.1 to 19.7) | 51.2 (42.8 to 62.7) | 13.0 (6.5 to 19.6) | 3.0 (-0.5 to 6.0) | 2.8 (2.1 to 3.7) |
| ars_s0 | 9.4 (8.0 to 11.0) | 14.1 (10.6 to 16.9) | 7.3 (4.9 to 9.7) | 8.8 (4.7 to 13.0) | 7.4 (6.5 to 8.4) |
| lstdq_v2_s0 | 7.2 (5.7 to 8.9) | 21.9 (20.2 to 23.8) | 2.5 (-8.4 to 12.5) | 2.5 (1.6 to 3.8) | 1.3 (-0.2 to 2.9) |
| qlearn_s0 | 6.1 (4.6 to 7.1) | 20.9 (15.6 to 24.9) | 7.1 (5.5 to 8.6) | 3.6 (1.4 to 6.2) | -1.2 (-1.9 to -0.3) |

## Regret: delay above the best controller in the same hour (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 3.4 (2.4 to 4.3) | 0.1 (0.0 to 0.1) | 1.3 (1.0 to 1.7) | 6.9 (3.6 to 11.1) | 5.0 (3.5 to 6.7) |
| actuated | 0.4 (0.3 to 0.6) | 0.1 (0.0 to 0.1) | 0.7 (0.1 to 1.5) | 0.3 (0.2 to 0.4) | 0.6 (0.5 to 0.8) |
| webster | 42.0 (7.2 to 110.9) | 7.1 (6.1 to 8.1) | 8.8 (8.0 to 9.8) | 8.5 (7.6 to 9.2) | 56.1 (6.7 to 153.3) |
| maxpressure | 2.4 (2.1 to 2.8) | 5.9 (4.9 to 7.1) | 2.3 (1.5 to 3.0) | 0.7 (0.3 to 1.1) | 1.1 (0.9 to 1.4) |
| ars_s0 | 1.8 (1.6 to 2.0) | 1.6 (1.3 to 2.0) | 1.7 (1.0 to 2.3) | 1.6 (1.2 to 2.1) | 2.0 (1.8 to 2.1) |
| lstdq_v2_s0 | 1.3 (1.1 to 1.5) | 2.5 (2.4 to 2.7) | 1.1 (0.2 to 1.9) | 0.7 (0.5 to 0.9) | 0.9 (0.6 to 1.2) |
| qlearn_s0 | 1.1 (1.0 to 1.2) | 2.4 (1.8 to 2.8) | 1.6 (1.1 to 2.2) | 0.8 (0.6 to 1.1) | 0.4 (0.2 to 0.5) |

## Worst-off movement: highest 95th-percentile delay of any movement in the hour (s)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 102.7 (96.9 to 108.8) | 33.2 (30.4 to 36.5) | 92.7 (78.9 to 104.3) | 145.3 (113.0 to 189.9) | 130.4 (123.5 to 136.8) |
| actuated | 64.1 (59.3 to 71.0) | 33.2 (30.4 to 36.5) | 51.5 (48.3 to 55.2) | 67.0 (65.0 to 70.4) | 81.9 (74.3 to 89.4) |
| webster | 172.7 (66.5 to 374.1) | 49.5 (45.3 to 55.6) | 69.1 (58.5 to 82.1) | 94.3 (63.1 to 140.9) | 223.8 (73.5 to 508.0) |
| maxpressure | 82.2 (78.3 to 86.0) | 90.8 (87.0 to 94.5) | 94.9 (85.9 to 102.9) | 72.1 (62.3 to 85.8) | 79.2 (72.1 to 85.0) |
| ars_s0 | 77.3 (73.5 to 81.1) | 52.1 (45.0 to 59.9) | 82.7 (77.1 to 87.3) | 90.8 (76.6 to 105.0) | 87.2 (81.7 to 91.8) |
| lstdq_v2_s0 | 79.6 (76.0 to 83.1) | 47.0 (44.3 to 49.5) | 72.6 (69.2 to 78.0) | 84.8 (76.4 to 93.1) | 96.1 (90.3 to 101.9) |
| qlearn_s0 | 62.0 (57.6 to 68.4) | 46.2 (41.5 to 51.0) | 48.2 (46.8 to 49.8) | 61.4 (57.7 to 66.7) | 73.8 (66.8 to 80.9) |

## Hours with a queue reaching the leg end (share of hours with >= 10 vehicles unable to enter)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 0.05 (0.01 to 0.09) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.12 (0.02 to 0.24) |
| actuated | 0.02 (0.00 to 0.06) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.06 (0.00 to 0.12) |
| webster | 0.14 (0.05 to 0.25) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.05 (0.00 to 0.15) | 0.26 (0.10 to 0.42) |
| maxpressure | 0.02 (0.00 to 0.03) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.05 (0.00 to 0.11) |
| ars_s0 | 0.05 (0.01 to 0.11) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.08 (0.02 to 0.16) |
| lstdq_v2_s0 | 0.02 (0.00 to 0.03) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.03 (0.00 to 0.06) |
| qlearn_s0 | 0.01 (0.00 to 0.02) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.01 (0.00 to 0.04) |

## How often each controller is best in an hour

| Controller | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|
| gdot | 83 % | 8 % | 0 % | 0 % |
| actuated | 83 % | 46 % | 44 % | 27 % |
| webster | 0 % | 0 % | 0 % | 0 % |
| maxpressure | 0 % | 0 % | 17 % | 7 % |
| ars_s0 | 10 % | 8 % | 0 % | 2 % |
| lstdq_v2_s0 | 0 % | 38 % | 22 % | 19 % |
| qlearn_s0 | 7 % | 0 % | 17 % | 46 % |
