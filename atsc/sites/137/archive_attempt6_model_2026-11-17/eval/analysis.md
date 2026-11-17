# 137 analysis: when and why each method wins (corrected-demand model, validation weekdays)

20 days, 480 clean hours, learners pooled over training seeds. Model: attempt 6 (VALIDATION.md: + signal 138 upstream; V1 splits 26/35, V2 gap-outs 23/35, not accepted). Preliminary until validated.

## RQ1: how the ranking changes

### By saturation Y (sum of critical flow ratios, field counts)

| condition | hours | Actuated | MaxPressure | LSTDQ | Q-learning | ARS | GDOT plan | Webster | ranking (adaptive) |
|---|---|---|---|---|---|---|---|---|---|
| light, Y < 0.3 | 164 | 14.8 | 16.1 | 17.6 | 15.7 | 15.6 | 15.5 | 26.6 | Actuated > ARS > Q-learning > MaxPressure > LSTDQ |
| moderate, 0.3–0.45 | 42 | 20.5 | 20.8 | 22.8 | 23.3 | 22.0 | 23.5 | 43.5 | Actuated > MaxPressure > ARS > LSTDQ > Q-learning |
| busy, 0.45–0.6 | 164 | 24.9 | 22.1 | 24.1 | 24.7 | 24.1 | 28.4 | 49.9 | MaxPressure > ARS > LSTDQ > Q-learning > Actuated |
| heavy, Y ≥ 0.6 | 110 | 31.3 | 36.5 | 35.5 | 61.8 | 58.0 | 49.8 | 87.2 | Actuated > LSTDQ > MaxPressure > ARS > Q-learning |

### By time of day

| condition | hours | Actuated | MaxPressure | LSTDQ | Q-learning | ARS | GDOT plan | Webster | ranking (adaptive) |
|---|---|---|---|---|---|---|---|---|---|
| night 00–06 | 120 | 13.1 | 16.8 | 16.9 | 15.1 | 14.7 | 13.1 | 24.0 | Actuated > ARS > Q-learning > MaxPressure > LSTDQ |
| AM peak 06–10 | 80 | 27.0 | 30.7 | 28.3 | 39.6 | 36.6 | 31.6 | 39.3 | Actuated > LSTDQ > MaxPressure > ARS > Q-learning |
| midday 10–15 | 100 | 28.3 | 31.6 | 29.7 | 42.2 | 42.0 | 49.8 | 58.1 | Actuated > LSTDQ > MaxPressure > ARS > Q-learning |
| PM peak 15–19 | 80 | 26.6 | 23.5 | 28.5 | 32.8 | 30.5 | 28.1 | 35.3 | MaxPressure > Actuated > LSTDQ > ARS > Q-learning |
| evening 19–24 | 100 | 23.0 | 20.7 | 24.5 | 37.6 | 34.8 | 26.7 | 127.6 | MaxPressure > Actuated > LSTDQ > ARS > Q-learning |

### By within-hour variability (cv of the twelve 5-min totals)

| condition | hours | Actuated | MaxPressure | LSTDQ | Q-learning | ARS | GDOT plan | Webster | ranking (adaptive) |
|---|---|---|---|---|---|---|---|---|---|
| steady, cv < 0.15 | 254 | 26.8 | 25.7 | 27.3 | 34.6 | 33.4 | 36.2 | 51.0 | MaxPressure > Actuated > LSTDQ > ARS > Q-learning |
| variable, 0.15–0.25 | 78 | 27.2 | 34.8 | 32.0 | 56.3 | 53.3 | 34.2 | 119.1 | Actuated > LSTDQ > MaxPressure > ARS > Q-learning |
| very variable, cv ≥ 0.25 | 148 | 16.6 | 20.0 | 21.1 | 24.1 | 19.4 | 21.8 | 34.3 | Actuated > ARS > MaxPressure > LSTDQ > Q-learning |

- steady, cv < 0.15: mean volume 1894 veh/h
- variable, 0.15–0.25: mean volume 1379 veh/h
- very variable, cv ≥ 0.25: mean volume 377 veh/h

Variability and volume move together (quiet hours are the most variable), so this split is not independent of saturation.

## RQ2: what the controllers do (by saturation)

Per controller: cycle length; per phase group: average green per service, share of cycles served (100 % − skips), share of greens ended at max green. Learners: training seed 0.

### light, Y < 0.3 (164 hours)

| controller | cycle s | main through P2/P6 | side through P4/P8 | main lefts P1/P5 | side lefts P3/P7 |
|---|---|---|---|---|---|
| Actuated | 50 | 26.1 s · 100 % · max 0 % | 11.6 s · 17 % · max 0 % | 10.6 s · 11 % · max 7 % | 7.7 s · 89 % · max 1 % |
| MaxPressure | 93 | 69.0 s · 100 % · max 32 % | 10.5 s · 28 % · max 0 % | 6.7 s · 13 % · max 0 % | 7.9 s · 81 % · max 0 % |
| LSTDQ | 109 | 78.0 s · 100 % · max 68 % | 21.0 s · 30 % · max 6 % | 8.2 s · 15 % · max 11 % | 10.1 s · 81 % · max 1 % |
| Q-learning | 48 | 25.9 s · 100 % · max 0 % | 9.6 s · 17 % · max 0 % | 6.5 s · 11 % · max 0 % | 7.2 s · 89 % · max 0 % |
| ARS | 74 | 43.3 s · 100 % · max 4 % | 14.8 s · 24 % · max 4 % | 6.5 s · 16 % · max 0 % | 14.1 s · 85 % · max 53 % |
| GDOT plan | 51 | 27.4 s · 100 % · max 0 % | 11.8 s · 16 % · max 0 % | 10.6 s · 11 % · max 6 % | 7.7 s · 90 % · max 1 % |

### moderate, 0.3–0.45 (42 hours)

| controller | cycle s | main through P2/P6 | side through P4/P8 | main lefts P1/P5 | side lefts P3/P7 |
|---|---|---|---|---|---|
| Actuated | 70 | 30.1 s · 100 % · max 0 % | 14.5 s · 57 % · max 1 % | 11.5 s · 46 % · max 19 % | 11.8 s · 77 % · max 14 % |
| MaxPressure | 70 | 36.2 s · 100 % · max 1 % | 11.4 s · 61 % · max 0 % | 6.6 s · 44 % · max 0 % | 9.3 s · 75 % · max 1 % |
| LSTDQ | 104 | 59.7 s · 100 % · max 31 % | 18.2 s · 71 % · max 3 % | 7.7 s · 51 % · max 5 % | 11.0 s · 75 % · max 4 % |
| Q-learning | 59 | 27.4 s · 100 % · max 0 % | 10.7 s · 55 % · max 0 % | 6.5 s · 40 % · max 0 % | 8.9 s · 77 % · max 0 % |
| ARS | 67 | 28.9 s · 100 % · max 0 % | 13.0 s · 58 % · max 0 % | 6.5 s · 46 % · max 0 % | 12.8 s · 76 % · max 58 % |
| GDOT plan | 103 | 61.2 s · 100 % · max 0 % | 15.7 s · 61 % · max 0 % | 11.9 s · 43 % · max 5 % | 11.8 s · 83 % · max 4 % |

### busy, 0.45–0.6 (164 hours)

| controller | cycle s | main through P2/P6 | side through P4/P8 | main lefts P1/P5 | side lefts P3/P7 |
|---|---|---|---|---|---|
| Actuated | 87 | 32.9 s · 100 % · max 0 % | 19.0 s · 86 % · max 2 % | 12.1 s · 63 % · max 28 % | 12.2 s · 81 % · max 26 % |
| MaxPressure | 71 | 31.4 s · 100 % · max 0 % | 11.9 s · 86 % · max 0 % | 6.6 s · 55 % · max 0 % | 8.5 s · 79 % · max 2 % |
| LSTDQ | 102 | 54.1 s · 100 % · max 17 % | 16.8 s · 92 % · max 1 % | 8.1 s · 61 % · max 5 % | 9.4 s · 83 % · max 4 % |
| Q-learning | 66 | 27.7 s · 100 % · max 0 % | 11.6 s · 85 % · max 0 % | 6.5 s · 54 % · max 0 % | 8.3 s · 78 % · max 0 % |
| ARS | 72 | 28.0 s · 100 % · max 0 % | 13.8 s · 83 % · max 0 % | 6.6 s · 59 % · max 0 % | 11.3 s · 79 % · max 55 % |
| GDOT plan | 129 | 74.4 s · 100 % · max 0 % | 19.7 s · 94 % · max 0 % | 11.9 s · 59 % · max 0 % | 10.4 s · 90 % · max 0 % |

### heavy, Y ≥ 0.6 (110 hours)

| controller | cycle s | main through P2/P6 | side through P4/P8 | main lefts P1/P5 | side lefts P3/P7 |
|---|---|---|---|---|---|
| Actuated | 100 | 39.2 s · 100 % · max 1 % | 22.2 s · 94 % · max 6 % | 12.3 s · 72 % · max 32 % | 12.3 s · 85 % · max 40 % |
| MaxPressure | 76 | 34.0 s · 100 % · max 1 % | 12.3 s · 93 % · max 0 % | 6.6 s · 60 % · max 0 % | 8.1 s · 82 % · max 6 % |
| LSTDQ | 112 | 60.5 s · 100 % · max 23 % | 16.8 s · 97 % · max 2 % | 8.3 s · 66 % · max 7 % | 9.7 s · 87 % · max 14 % |
| Q-learning | 68 | 27.6 s · 100 % · max 0 % | 11.7 s · 92 % · max 0 % | 6.5 s · 60 % · max 0 % | 7.7 s · 80 % · max 0 % |
| ARS | 74 | 27.8 s · 100 % · max 0 % | 14.3 s · 90 % · max 0 % | 6.8 s · 64 % · max 1 % | 11.1 s · 80 % · max 56 % |
| GDOT plan | 133 | 74.3 s · 100 % · max 0 % | 21.6 s · 98 % · max 0 % | 11.4 s · 65 % · max 0 % | 9.8 s · 92 % · max 0 % |

## RQ3: does the ranking hold?

### (a) Detector-count error: GDOT counts as reported vs corrected side-street demand (same days)

| model | Actuated | MaxPressure | LSTDQ | Q-learning | ARS | GDOT plan | Webster | ranking (adaptive) |
|---|---|---|---|---|---|---|---|---|
| first pass (reported counts) | 17.1 | 19.0 | 18.0 | 46.9 | 19.6 | 20.9 | 48.5 | Actuated > LSTDQ > MaxPressure > ARS > Q-learning |
| corrected counts (attempt 6 model) | 25.9 | 26.7 | 27.5 | 37.3 | 35.5 | 34.6 | 60.9 | Actuated > MaxPressure > LSTDQ > ARS > Q-learning |

The two models differ in the counted side-street and EB-left demand (and in pedestrians, passage times and left-turn calibration); the ranking change is the effect of the whole correction.

### (b) Training seeds: overall vehicle-weighted delay per seed (s/veh)

| learner | per seed | median | spread |
|---|---|---|---|
| LSTDQ | 29.5, 25.7, 25.0, 26.8, 30.7 | 26.8 | 5.7 |
| Q-learning | 38.3, 34.5, 38.1, 38.3, 37.5 | 38.1 | 3.8 |
| ARS | 45.0, 29.3, 36.3, 36.5, 30.6 | 36.3 | 15.7 |

### (c) Worst-served movement: 95th-percentile delay of the worst movement in the hour (s), by saturation

| condition | Actuated | MaxPressure | LSTDQ | Q-learning | ARS | GDOT plan | Webster |
|---|---|---|---|---|---|---|---|
| light, Y < 0.3 | 46 | 106 | 105 | 77 | 62 | 54 | 68 |
| moderate, 0.3–0.45 | 71 | 103 | 131 | 122 | 96 | 119 | 158 |
| busy, 0.45–0.6 | 79 | 105 | 129 | 124 | 94 | 167 | 156 |
| heavy, Y ≥ 0.6 | 106 | 190 | 211 | 277 | 224 | 302 | 317 |

## Comparison with actuated, daily vehicle-weighted delay over the validation days

Equivalence (H1): margin per day max(2 s/veh, 5 % of actuated), fixed before any result was read; paired TOST at 5 % (normal approximation). Difference: paired t-test and Wilcoxon signed-rank (two-sided), days won = days with less delay than actuated.

| method | mean diff (s/veh) | median diff | days won | p TOST | p t-test | p Wilcoxon | verdict |
|---|---|---|---|---|---|---|---|
| MaxPressure | +0.58 | -2.43 | 17/20 | 0.281 | 0.814 | 0.0637 | inconclusive |
| LSTDQ | +1.54 | -0.33 | 12/20 | 0.328 | 0.155 | 0.8983 | inconclusive |
| Q-learning | +10.62 | -0.74 | 11/20 | 0.918 | 0.102 | 0.2611 | inconclusive |
| ARS | +8.86 | -1.07 | 12/20 | 0.859 | 0.181 | 0.9854 | inconclusive |
| GDOT plan | +8.32 | +3.12 | 0/20 | 0.887 | 0.127 | 0.0000 | worse on typical days (Wilcoxon), mean not significant |
| Webster | +32.71 | +7.15 | 0/20 | 0.989 | 0.025 | 0.0000 | worse |

