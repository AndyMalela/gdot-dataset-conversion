# Baselines on validation weekdays (full day)

Mean delay per vehicle (s/veh): signal delay + queueing + waiting to enter. Median over days; days with flagged count bins marked separately.

| Controller | all days median | IQR | days without flagged bins, median | P8 through (Piedmont-N) median | teleports |
|---|---|---|---|---|---|
| gdot | 48.4 | 48.0–56.6 | 48.3 | 52.4 | 15 |
| actuated | 49.5 | 48.5–57.6 | 49.3 | 47.9 | 17 |
| webster | 103.8 | 86.5–141.5 | 103.8 | 35.2 | 1 |
| maxpressure | 352.9 | 292.2–426.5 | 343.9 | 31.4 | 37 |
| lstdq | 35.1 | 34.9–37.1 | 35.0 | 30.8 | 0 |

Mean delay by time of day (s/veh, all validation weekdays pooled):

| Controller | night 00–06 | AM 06–10 | midday 10–15 | PM 15–19 | evening 19–24 |
|---|---|---|---|---|---|
| gdot | 27.7 | 50.2 | 55.4 | 64.5 | 41.9 |
| actuated | 28.6 | 48.2 | 52.9 | 67.8 | 46.1 |
| webster | 43.8 | 43.1 | 51.7 | 249.8 | 111.3 |
| maxpressure | 26.3 | 46.8 | 65.5 | 676.1 | 732.8 |
| lstdq | 26.5 | 34.8 | 37.0 | 40.5 | 34.1 |
