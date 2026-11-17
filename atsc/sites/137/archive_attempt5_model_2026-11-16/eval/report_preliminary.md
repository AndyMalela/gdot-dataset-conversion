# RQ1 evaluation: strengths and weaknesses by traffic condition (137, validation weekdays)

120 clean hours on 5 days x 1 simulation seeds (seed-averaged per hour). Y = sum of critical flow ratios from the field counts. Intervals: 95 % day-bootstrap. **Limitations (137, 2026-11-16):** uncalibrated driver model; GDOT timing not yet field-validated; WB through from the upstream signal 138; EB/WB right turns run as through; P2/P6 stop-bar presence added in the model; coordinated corridor site (138 at ~260 m) modelled isolated; no pedestrian timing (atsc/sites/137/README.md). Main tables: learnt controllers at one training seed (lstdq_v2_s0 = LSTDQ, qlearn_s0, ars_s0); all training seeds of every learner are in the training-seed tables (simulation seed 1).

Hours per condition: light (Y < 0.15) 30, moderate (0.15-0.30) 11, busy (0.30-0.40) 4, heavy (Y >= 0.40) 75

## Overall mean delay, vehicle-weighted (s/veh)

| Controller | mean delay (95 % interval) |
|---|---|
| gdot | 28.6 (26.6 to 30.6) |
| actuated | 25.0 (24.0 to 26.3) |
| webster | 73.6 (30.1 to 159.3) |
| maxpressure | 21.9 (21.0 to 22.9) |
| ars_s0 | 25.2 (23.2 to 27.9) |
| lstdq_v2_s0 | 27.4 (25.1 to 29.9) |
| qlearn_s0 | 34.0 (23.4 to 49.5) |

## Mean delay (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 23.6 (21.9 to 24.9) | 11.0 (9.8 to 12.4) | 16.0 (14.5 to 18.0) | 19.8 (16.2 to 23.0) | 29.8 (28.0 to 31.2) |
| actuated | 21.0 (20.3 to 22.0) | 11.0 (9.8 to 12.4) | 15.0 (13.6 to 17.1) | 17.6 (15.9 to 19.2) | 25.9 (25.2 to 27.1) |
| webster | 63.1 (28.1 to 132.2) | 22.6 (22.2 to 22.9) | 25.0 (23.9 to 25.9) | 31.4 (27.7 to 35.1) | 80.1 (30.9 to 177.5) |
| maxpressure | 19.4 (18.6 to 20.0) | 13.0 (11.2 to 15.2) | 15.7 (13.3 to 18.1) | 20.2 (14.8 to 26.3) | 22.4 (21.6 to 23.1) |
| ars_s0 | 21.3 (20.3 to 23.1) | 11.8 (10.7 to 13.4) | 15.6 (13.5 to 19.1) | 19.1 (14.7 to 25.1) | 25.8 (23.9 to 28.2) |
| lstdq_v2_s0 | 23.9 (22.5 to 25.3) | 15.1 (12.6 to 17.9) | 20.1 (18.2 to 22.8) | 25.2 (18.3 to 32.5) | 27.6 (25.7 to 29.8) |
| qlearn_s0 | 26.9 (20.3 to 37.0) | 11.2 (9.9 to 12.8) | 14.8 (12.9 to 18.1) | 24.6 (15.6 to 39.3) | 34.0 (24.2 to 48.4) |

## Gain vs Webster (%, negative = less delay than Webster)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | -23.1 (-29.8 to -17.0) | -51.3 (-56.5 to -45.2) | -35.6 (-43.3 to -25.2) | -36.3 (-50.9 to -24.0) | -9.1 (-19.1 to -1.5) |
| actuated | -30.4 (-34.7 to -26.8) | -51.3 (-56.5 to -45.2) | -39.4 (-46.9 to -28.1) | -43.1 (-51.9 to -33.4) | -20.1 (-26.2 to -16.5) |
| webster | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| maxpressure | -34.5 (-40.2 to -29.9) | -42.1 (-50.6 to -33.3) | -36.9 (-47.6 to -26.1) | -32.9 (-57.5 to -8.3) | -31.3 (-37.0 to -27.5) |
| ars_s0 | -30.6 (-34.2 to -27.6) | -47.2 (-52.5 to -40.8) | -36.8 (-47.5 to -18.9) | -37.5 (-54.8 to -13.0) | -22.9 (-28.0 to -18.3) |
| lstdq_v2_s0 | -21.1 (-28.6 to -14.8) | -32.7 (-44.0 to -21.5) | -18.8 (-29.0 to -5.0) | -16.9 (-45.3 to 11.6) | -17.1 (-24.8 to -11.2) |
| qlearn_s0 | -27.3 (-33.5 to -21.1) | -50.3 (-56.1 to -43.4) | -39.9 (-50.2 to -24.1) | -17.7 (-55.7 to 36.1) | -17.0 (-25.4 to -6.3) |

## Gain vs actuated (%, negative = less delay than actuated)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 9.8 (6.0 to 12.8) | 0.0 (0.0 to 0.0) | 6.0 (2.1 to 10.2) | 11.8 (-1.0 to 25.5) | 14.2 (8.3 to 19.1) |
| actuated | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) |
| webster | 191.6 (46.7 to 471.4) | 116.3 (93.5 to 138.3) | 71.3 (45.5 to 91.3) | 81.1 (53.7 to 108.4) | 220.1 (22.6 to 612.4) |
| maxpressure | -3.3 (-6.9 to 0.9) | 16.6 (10.2 to 24.3) | 7.3 (-6.3 to 28.9) | 15.5 (-11.9 to 55.0) | -13.8 (-15.5 to -12.2) |
| ars_s0 | 1.9 (-0.5 to 4.8) | 8.6 (4.9 to 11.9) | 3.0 (-4.5 to 11.3) | 9.6 (-13.9 to 47.6) | -1.7 (-6.1 to 2.9) |
| lstdq_v2_s0 | 17.3 (13.5 to 20.6) | 35.6 (27.3 to 43.4) | 34.5 (29.6 to 39.5) | 43.5 (10.7 to 91.4) | 5.9 (1.6 to 10.5) |
| qlearn_s0 | 18.4 (0.1 to 46.1) | 2.2 (1.2 to 3.1) | -1.8 (-7.5 to 5.2) | 41.9 (-7.8 to 133.0) | 23.8 (-4.9 to 64.8) |

## Regret: delay above the best controller in the same hour (s/veh)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 5.4 (4.6 to 6.0) | 0.7 (0.5 to 0.9) | 2.4 (1.8 to 3.0) | 4.1 (1.9 to 6.2) | 7.7 (6.5 to 8.4) |
| actuated | 2.8 (2.5 to 3.1) | 0.7 (0.5 to 0.9) | 1.4 (1.0 to 2.0) | 1.8 (0.7 to 2.9) | 3.8 (3.4 to 4.3) |
| webster | 44.8 (10.0 to 113.4) | 12.4 (10.8 to 13.8) | 11.4 (9.0 to 13.3) | 15.7 (11.1 to 20.3) | 58.0 (9.2 to 154.6) |
| maxpressure | 1.2 (0.8 to 1.7) | 2.8 (1.9 to 3.6) | 2.1 (0.5 to 4.4) | 4.5 (0.2 to 9.5) | 0.2 (0.1 to 0.4) |
| ars_s0 | 3.1 (2.1 to 4.4) | 1.6 (1.1 to 2.0) | 2.0 (0.7 to 4.0) | 3.4 (0.3 to 8.6) | 3.7 (2.0 to 5.6) |
| lstdq_v2_s0 | 5.7 (4.9 to 6.5) | 4.9 (3.7 to 6.1) | 6.5 (5.6 to 7.7) | 9.5 (4.5 to 15.8) | 5.5 (4.2 to 7.0) |
| qlearn_s0 | 8.7 (2.6 to 18.3) | 0.9 (0.8 to 1.1) | 1.3 (0.2 to 2.9) | 8.9 (0.8 to 22.9) | 11.9 (2.8 to 25.6) |

## Worst-off movement: highest 95th-percentile delay of any movement in the hour (s)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 126.4 (114.6 to 135.4) | 41.8 (40.7 to 43.3) | 82.7 (69.0 to 96.1) | 109.6 (76.2 to 142.9) | 167.5 (153.6 to 177.2) |
| actuated | 73.5 (69.8 to 79.3) | 41.8 (40.7 to 43.3) | 57.5 (54.9 to 61.3) | 61.7 (59.8 to 64.2) | 88.6 (84.4 to 95.4) |
| webster | 185.5 (84.6 to 376.2) | 59.4 (59.0 to 59.7) | 71.3 (64.4 to 77.9) | 140.7 (99.7 to 210.9) | 237.3 (96.7 to 506.4) |
| maxpressure | 112.0 (104.3 to 119.7) | 97.5 (94.0 to 101.3) | 125.3 (91.6 to 174.4) | 136.9 (96.2 to 191.6) | 113.9 (104.3 to 124.2) |
| ars_s0 | 92.3 (87.6 to 97.2) | 76.0 (67.3 to 83.6) | 87.7 (73.8 to 107.5) | 106.2 (60.4 to 186.5) | 98.0 (92.6 to 103.4) |
| lstdq_v2_s0 | 147.4 (135.1 to 159.8) | 103.5 (98.2 to 107.2) | 140.1 (115.3 to 173.8) | 162.6 (128.7 to 201.8) | 164.3 (147.7 to 180.9) |
| qlearn_s0 | 134.3 (101.0 to 169.0) | 45.4 (43.1 to 47.7) | 81.1 (59.4 to 102.8) | 206.8 (64.0 to 445.6) | 170.1 (116.4 to 223.9) |

## Hours with a queue reaching the leg end (share of hours with >= 10 vehicles unable to enter)

| Controller | all hours | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|---|
| gdot | 0.10 (0.06 to 0.16) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.16 (0.10 to 0.23) |
| actuated | 0.12 (0.07 to 0.21) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.19 (0.11 to 0.30) |
| webster | 0.25 (0.17 to 0.34) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.50 (0.00 to 1.00) | 0.37 (0.22 to 0.49) |
| maxpressure | 0.03 (0.00 to 0.07) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.04 (0.00 to 0.11) |
| ars_s0 | 0.19 (0.12 to 0.27) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.30 (0.19 to 0.41) |
| lstdq_v2_s0 | 0.05 (0.00 to 0.12) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.07 (0.00 to 0.17) |
| qlearn_s0 | 0.17 (0.11 to 0.25) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.25 (0.00 to 0.75) | 0.25 (0.14 to 0.37) |

## How often each controller is best in an hour

| Controller | light (Y < 0.15) | moderate (0.15-0.30) | busy (0.30-0.40) | heavy (Y >= 0.40) |
|---|---|---|---|---|
| gdot | 37 % | 9 % | 0 % | 0 % |
| actuated | 37 % | 9 % | 25 % | 0 % |
| webster | 0 % | 0 % | 0 % | 0 % |
| maxpressure | 10 % | 27 % | 25 % | 75 % |
| ars_s0 | 20 % | 9 % | 25 % | 13 % |
| lstdq_v2_s0 | 3 % | 0 % | 0 % | 0 % |
| qlearn_s0 | 30 % | 45 % | 25 % | 12 % |
