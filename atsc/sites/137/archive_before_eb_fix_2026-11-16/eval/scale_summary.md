# Demand-scale sweep (137, preliminary subset of validation days, simulation seed 1)

Every 5-min count of the real day multiplied by k (labelled sensitivity experiment, not real traffic). Cell: vehicle-weighted mean delay s/veh (days run) · teleports · hours with a queue reaching the leg end / hours. Controllers trained at x1 only.

| Controller | x1 | x1.25 |
|---|---|---|
| actuated | 17.7 (5d) · 0 tp · 1/120 h | 22.2 (5d) · 0 tp · 7/120 h |
| gdot | 21.5 (5d) · 0 tp · 3/120 h | 34.1 (5d) · 0 tp · 12/120 h |
| maxpressure | 77.3 (5d) · 0 tp · 22/120 h | 808.4 (5d) · 0 tp · 62/120 h |
| webster | 86.5 (5d) · 0 tp · 8/120 h | 258.6 (5d) · 0 tp · 53/120 h |
| ars_s0 | 17.9 (5d) · 0 tp · 1/120 h | 27.6 (5d) · 0 tp · 16/120 h |
| lstdq_v2_s0 | 21.9 (5d) · 0 tp · 3/120 h | 34.2 (5d) · 0 tp · 15/120 h |
| qlearn_s0 | 265.9 (5d) · 0 tp · 40/120 h | 1806.8 (5d) · 0 tp · 77/120 h |
