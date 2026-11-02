# Baselines on validation weekdays (full day)

Mean delay per vehicle (s/veh): signal delay + queueing + waiting to enter. Median over days; days with flagged count bins marked separately.

| Controller | all days median | IQR | days without flagged bins, median | P8 through (Piedmont-N) median | teleports |
|---|---|---|---|---|---|
| gdot | 47.3 | 46.2–52.3 | 47.0 | 52.6 | 0 |
| actuated | 39.3 | 39.1–42.7 | 39.3 | 33.3 | 0 |
| webster | 37.5 | 36.6–45.5 | 37.4 | 31.1 | 1 |
| lstdq | 33.6 | 33.5–36.1 | 33.6 | 27.9 | 0 |

Mean delay by time of day (s/veh, all validation weekdays pooled):

| Controller | night 00–06 | AM 06–10 | midday 10–15 | PM 15–19 | evening 19–24 |
|---|---|---|---|---|---|
| gdot | 29.8 | 45.5 | 48.9 | 69.3 | 41.6 |
| actuated | 27.9 | 39.3 | 42.0 | 44.9 | 38.7 |
| webster | 43.5 | 39.0 | 38.2 | 45.4 | 37.2 |
| lstdq | 26.8 | 33.6 | 35.7 | 37.7 | 33.6 |
