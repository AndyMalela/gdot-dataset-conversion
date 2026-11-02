# Baselines on validation weekdays (full day)

Mean delay per vehicle (s/veh): signal delay + queueing + waiting to enter. Median over days; days with flagged count bins marked separately.

| Controller | all days median | IQR | days without flagged bins, median | P8 through (Piedmont-N) median | teleports |
|---|---|---|---|---|---|
| gdot | 47.4 | 46.4–52.0 | 47.1 | 52.7 | 0 |
| actuated | 39.7 | 39.3–41.6 | 39.6 | 34.0 | 0 |
| webster | 167.4 | 119.4–247.2 | 160.4 | 54.5 | 3083 |

Mean delay by time of day (s/veh, all validation weekdays pooled):

| Controller | night 00–06 | AM 06–10 | midday 10–15 | PM 15–19 | evening 19–24 |
|---|---|---|---|---|---|
| gdot | 30.2 | 45.9 | 48.9 | 67.0 | 41.1 |
| actuated | 28.5 | 39.5 | 41.9 | 44.1 | 38.5 |
| webster | 43.6 | 144.7 | 245.0 | 202.0 | 140.5 |
