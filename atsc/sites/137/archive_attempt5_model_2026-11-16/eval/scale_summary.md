# Demand-scale sweep (137, preliminary subset of validation days, simulation seed 1)

Every 5-min count of the real day multiplied by k (labelled sensitivity experiment, not real traffic). Cell: vehicle-weighted mean delay s/veh (days run) · teleports · hours with a queue reaching the leg end / hours. Controllers trained at x1 only.

| Controller | x1 | x1.25 | x1.5 | x1.75 | x2 | x2.5 |
|---|---|---|---|---|---|---|
| actuated | 25.2 (20d) · 0 tp · 36/480 h | 46.4 (5d) · 0 tp · 40/120 h | 215.9 (5d) · 0 tp · 68/120 h | 885.9 (5d) · 0 tp · 82/120 h | 2233.8 (5d) · 0 tp · 83/120 h | 4999.0 (5d) · 0 tp · 89/120 h |
| gdot | 34.3 (20d) · 0 tp · 46/480 h | 71.0 (5d) · 0 tp · 44/120 h | 313.1 (5d) · 0 tp · 74/120 h | 1125.1 (5d) · 0 tp · 84/120 h | 2498.3 (5d) · 0 tp · 86/120 h | 5256.2 (5d) · 0 tp · 88/120 h |
| maxpressure | 26.7 (20d) · 0 tp · 20/480 h | 52.2 (5d) · 0 tp · 29/120 h | 323.7 (5d) · 0 tp · 70/120 h | 1486.4 (5d) · 0 tp · 82/120 h | 2610.2 (5d) · 1 tp · 84/120 h | 5270.6 (5d) · 0 tp · 87/120 h |
| webster | 59.8 (20d) · 0 tp · 100/480 h | 240.2 (5d) · 0 tp · 65/120 h | 940.5 (5d) · 0 tp · 81/120 h | 1783.6 (5d) · 0 tp · 76/120 h | 2771.2 (5d) · 0 tp · 86/120 h | 5663.9 (5d) · 0 tp · 93/120 h |
| ars_s0 | 32.4 (20d) · 0 tp · 65/480 h | 77.9 (5d) · 0 tp · 54/120 h | 364.1 (5d) · 0 tp · 79/120 h | 1033.2 (5d) · 0 tp · 84/120 h | 2550.9 (5d) · 0 tp · 90/120 h | 5357.4 (5d) · 0 tp · 93/120 h |
| ars_s1 | 33.5 (20d) · 0 tp · 66/480 h | - | - | - | - | - |
| ars_s2 | 31.9 (20d) · 0 tp · 58/480 h | - | - | - | - | - |
| ars_s3 | 30.9 (20d) · 0 tp · 54/480 h | - | - | - | - | - |
| ars_s4 | 32.1 (20d) · 0 tp · 50/480 h | - | - | - | - | - |
| lstdq_v2_s0 | 31.0 (20d) · 0 tp · 23/480 h | 65.4 (5d) · 0 tp · 37/120 h | 308.8 (5d) · 0 tp · 73/120 h | 1101.5 (5d) · 0 tp · 83/120 h | 2434.3 (5d) · 1 tp · 85/120 h | 5357.7 (5d) · 1 tp · 92/120 h |
| lstdq_v2_s1 | 26.3 (20d) · 0 tp · 26/480 h | - | - | - | - | - |
| lstdq_v2_s2 | 29.7 (20d) · 0 tp · 21/480 h | - | - | - | - | - |
| lstdq_v2_s3 | 25.1 (20d) · 0 tp · 23/480 h | - | - | - | - | - |
| lstdq_v2_s4 | 25.5 (20d) · 0 tp · 17/480 h | - | - | - | - | - |
| qlearn_s0 | 38.7 (20d) · 0 tp · 59/480 h | 179.0 (5d) · 0 tp · 54/120 h | 954.1 (5d) · 0 tp · 79/120 h | 2749.6 (5d) · 0 tp · 83/120 h | 4414.5 (5d) · 0 tp · 84/120 h | 7442.0 (5d) · 1 tp · 91/120 h |
| qlearn_s1 | 33.4 (20d) · 0 tp · 52/480 h | - | - | - | - | - |
| qlearn_s2 | 36.0 (20d) · 0 tp · 49/480 h | - | - | - | - | - |
| qlearn_s3 | 36.2 (20d) · 0 tp · 54/480 h | - | - | - | - | - |
| qlearn_s4 | 35.9 (20d) · 0 tp · 54/480 h | - | - | - | - | - |
