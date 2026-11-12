# Baselines on validation weekdays (full day)

Mean delay per vehicle (s/veh): signal delay + queueing + waiting to enter. Median over days; days with flagged count bins marked separately.

| Controller | all days median | IQR | days without flagged bins, median | P8 through (Piedmont-N) median | teleports |
|---|---|---|---|---|---|
| gdot | 46.1 | 45.5–49.7 | 45.8 | 51.9 | 0 |
| actuated | 46.7 | 46.0–51.1 | 46.6 | 44.6 | 0 |
| webster | 55.5 | 48.5–64.6 | 55.5 | 35.0 | 0 |
| maxpressure | 35.8 | 35.3–41.0 | 35.7 | 33.5 | 0 |

Mean delay by time of day (s/veh, all validation weekdays pooled):

| Controller | night 00–06 | AM 06–10 | midday 10–15 | PM 15–19 | evening 19–24 |
|---|---|---|---|---|---|
| gdot | 27.7 | 47.5 | 49.8 | 56.9 | 39.6 |
| actuated | 28.6 | 46.2 | 49.4 | 57.4 | 42.8 |
| webster | 43.8 | 36.5 | 41.2 | 97.4 | 50.2 |
| maxpressure | 26.3 | 35.8 | 38.1 | 45.2 | 34.7 |
