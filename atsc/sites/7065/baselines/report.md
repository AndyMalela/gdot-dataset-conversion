# Baselines on validation weekdays (full day)

Mean delay per vehicle (s/veh): signal delay + queueing + waiting to enter. Median over days; days with flagged count bins marked separately.

| Controller | all days median | IQR | days without flagged bins, median | P8 through (Piedmont-N) median | teleports |
|---|---|---|---|---|---|
| gdot | 47.3 | 46.2–52.5 | 47.0 | 53.0 | 0 |
| actuated | 39.4 | 39.1–42.1 | 39.3 | 33.8 | 0 |
| webster | 37.3 | 36.7–45.4 | 37.1 | 31.1 | 0 |
| maxpressure | 32.8 | 32.6–37.3 | 32.8 | 28.0 | 0 |
| lstdq | 35.1 | 34.9–37.1 | 35.0 | 30.8 | 0 |

Mean delay by time of day (s/veh, all validation weekdays pooled):

| Controller | night 00–06 | AM 06–10 | midday 10–15 | PM 15–19 | evening 19–24 |
|---|---|---|---|---|---|
| gdot | 29.8 | 45.5 | 49.0 | 69.0 | 41.0 |
| actuated | 27.9 | 39.4 | 42.0 | 45.0 | 38.6 |
| webster | 43.5 | 38.6 | 38.3 | 45.1 | 37.3 |
| maxpressure | 26.7 | 32.6 | 34.8 | 37.3 | 34.3 |
| lstdq | 26.5 | 34.8 | 37.0 | 40.5 | 34.1 |
