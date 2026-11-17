# 137 analysis: when and why each method wins (corrected-demand model, validation weekdays)

20 days, 480 clean hours, learners pooled over training seeds. Model: attempt 5 (VALIDATION.md; splits pass, left-turn gap-outs do not). Preliminary until validated.

## RQ1: how the ranking changes

### By saturation Y (sum of critical flow ratios, field counts)

| condition | hours | Actuated | MaxPressure | LSTDQ | Q-learning | ARS | GDOT plan | Webster | ranking (adaptive) |
|---|---|---|---|---|---|---|---|---|---|
| light, Y < 0.3 | 164 | 13.4 | 14.4 | 15.9 | 14.0 | 13.7 | 14.0 | 25.4 | Actuated > ARS > Q-learning > MaxPressure > LSTDQ |
| moderate, 0.3–0.45 | 42 | 19.6 | 19.5 | 21.7 | 21.6 | 19.8 | 22.8 | 42.9 | MaxPressure > Actuated > ARS > Q-learning > LSTDQ |
| busy, 0.45–0.6 | 164 | 24.3 | 21.3 | 23.4 | 23.8 | 22.2 | 28.5 | 49.2 | MaxPressure > ARS > LSTDQ > Q-learning > Actuated |
| heavy, Y ≥ 0.6 | 110 | 30.7 | 38.1 | 36.9 | 60.3 | 52.0 | 49.3 | 85.7 | Actuated > LSTDQ > MaxPressure > ARS > Q-learning |

### By time of day

| condition | hours | Actuated | MaxPressure | LSTDQ | Q-learning | ARS | GDOT plan | Webster | ranking (adaptive) |
|---|---|---|---|---|---|---|---|---|---|
| night 00–06 | 120 | 11.7 | 15.3 | 15.4 | 13.6 | 13.0 | 11.7 | 22.8 | Actuated > ARS > Q-learning > MaxPressure > LSTDQ |
| AM peak 06–10 | 80 | 26.1 | 31.6 | 28.4 | 38.1 | 34.6 | 31.9 | 37.9 | Actuated > LSTDQ > MaxPressure > ARS > Q-learning |
| midday 10–15 | 100 | 27.8 | 32.7 | 30.8 | 42.2 | 40.6 | 48.7 | 56.5 | Actuated > LSTDQ > MaxPressure > ARS > Q-learning |
| PM peak 15–19 | 80 | 26.0 | 22.6 | 27.8 | 30.6 | 27.0 | 29.0 | 34.5 | MaxPressure > Actuated > ARS > LSTDQ > Q-learning |
| evening 19–24 | 100 | 22.2 | 19.4 | 23.6 | 35.6 | 26.6 | 25.6 | 127.5 | MaxPressure > Actuated > LSTDQ > ARS > Q-learning |

### By within-hour variability (cv of the twelve 5-min totals)

| condition | hours | Actuated | MaxPressure | LSTDQ | Q-learning | ARS | GDOT plan | Webster | ranking (adaptive) |
|---|---|---|---|---|---|---|---|---|---|
| steady, cv < 0.15 | 254 | 26.1 | 25.7 | 26.9 | 33.4 | 30.7 | 35.8 | 49.8 | MaxPressure > Actuated > LSTDQ > ARS > Q-learning |
| variable, 0.15–0.25 | 78 | 26.4 | 35.1 | 34.2 | 55.1 | 46.5 | 34.7 | 118.1 | Actuated > LSTDQ > MaxPressure > ARS > Q-learning |
| very variable, cv ≥ 0.25 | 148 | 15.6 | 18.7 | 19.6 | 22.1 | 17.3 | 20.7 | 33.8 | Actuated > ARS > MaxPressure > LSTDQ > Q-learning |

- steady, cv < 0.15: mean volume 1894 veh/h
- variable, 0.15–0.25: mean volume 1379 veh/h
- very variable, cv ≥ 0.25: mean volume 377 veh/h

Variability and volume move together (quiet hours are the most variable), so this split is not independent of saturation.

### Demand sweep (real profile × k, same 5 days, seed 0 learners): vehicle-weighted delay, s/veh

| scale | Actuated | MaxPressure | LSTDQ | Q-learning | ARS | GDOT plan | Webster | ranking (adaptive) |
|---|---|---|---|---|---|---|---|---|
| ×1 | 25.0 | 22.0 | 27.5 | 34.8 | 25.3 | 28.7 | 78.0 | MaxPressure > Actuated > ARS > LSTDQ > Q-learning |

## RQ2: what the controllers do (by saturation)

Per controller: cycle length; per phase group: average green per service, share of cycles served (100 % − skips), share of greens ended at max green. Learners: training seed 0.

### light, Y < 0.3 (164 hours)

| controller | cycle s | main through P2/P6 | side through P4/P8 | main lefts P1/P5 | side lefts P3/P7 |
|---|---|---|---|---|---|
| Actuated | 50 | 26.1 s · 100 % · max 0 % | 11.9 s · 17 % · max 0 % | 10.6 s · 11 % · max 8 % | 7.7 s · 89 % · max 1 % |
| MaxPressure | 93 | 69.0 s · 100 % · max 32 % | 10.4 s · 28 % · max 0 % | 6.7 s · 14 % · max 0 % | 7.9 s · 81 % · max 0 % |
| LSTDQ | 114 | 82.0 s · 100 % · max 76 % | 24.7 s · 29 % · max 15 % | 9.6 s · 16 % · max 13 % | 10.0 s · 82 % · max 2 % |
| Q-learning | 48 | 25.9 s · 100 % · max 0 % | 9.6 s · 17 % · max 0 % | 6.5 s · 11 % · max 0 % | 7.2 s · 89 % · max 0 % |
| ARS | 83 | 53.1 s · 100 % · max 10 % | 12.0 s · 27 % · max 0 % | 6.5 s · 15 % · max 0 % | 13.7 s · 82 % · max 54 % |
| GDOT plan | 51 | 27.4 s · 100 % · max 0 % | 12.0 s · 16 % · max 0 % | 10.6 s · 11 % · max 6 % | 7.7 s · 90 % · max 1 % |

### moderate, 0.3–0.45 (42 hours)

| controller | cycle s | main through P2/P6 | side through P4/P8 | main lefts P1/P5 | side lefts P3/P7 |
|---|---|---|---|---|---|
| Actuated | 71 | 30.1 s · 100 % · max 0 % | 14.8 s · 57 % · max 1 % | 11.5 s · 47 % · max 19 % | 11.8 s · 79 % · max 13 % |
| MaxPressure | 69 | 36.2 s · 100 % · max 1 % | 11.3 s · 60 % · max 0 % | 6.6 s · 42 % · max 0 % | 9.2 s · 75 % · max 1 % |
| LSTDQ | 116 | 66.7 s · 100 % · max 41 % | 24.2 s · 72 % · max 13 % | 8.2 s · 55 % · max 4 % | 11.2 s · 77 % · max 4 % |
| Q-learning | 59 | 27.3 s · 100 % · max 0 % | 10.8 s · 55 % · max 0 % | 6.5 s · 40 % · max 0 % | 8.8 s · 78 % · max 0 % |
| ARS | 70 | 32.4 s · 100 % · max 1 % | 12.9 s · 60 % · max 0 % | 6.5 s · 47 % · max 0 % | 12.7 s · 76 % · max 59 % |
| GDOT plan | 103 | 59.4 s · 100 % · max 0 % | 16.2 s · 61 % · max 1 % | 11.9 s · 49 % · max 4 % | 11.9 s · 83 % · max 4 % |

### busy, 0.45–0.6 (164 hours)

| controller | cycle s | main through P2/P6 | side through P4/P8 | main lefts P1/P5 | side lefts P3/P7 |
|---|---|---|---|---|---|
| Actuated | 88 | 32.9 s · 100 % · max 0 % | 19.7 s · 87 % · max 2 % | 12.1 s · 65 % · max 29 % | 12.2 s · 81 % · max 26 % |
| MaxPressure | 71 | 31.4 s · 100 % · max 0 % | 12.0 s · 87 % · max 0 % | 6.6 s · 56 % · max 0 % | 8.5 s · 78 % · max 2 % |
| LSTDQ | 110 | 56.4 s · 100 % · max 22 % | 21.3 s · 93 % · max 5 % | 8.4 s · 65 % · max 5 % | 8.8 s · 85 % · max 2 % |
| Q-learning | 66 | 27.6 s · 100 % · max 0 % | 11.7 s · 85 % · max 0 % | 6.5 s · 54 % · max 0 % | 8.2 s · 78 % · max 0 % |
| ARS | 73 | 29.0 s · 100 % · max 0 % | 13.8 s · 84 % · max 0 % | 6.5 s · 59 % · max 0 % | 11.2 s · 78 % · max 55 % |
| GDOT plan | 130 | 72.2 s · 100 % · max 0 % | 20.3 s · 94 % · max 0 % | 12.3 s · 67 % · max 0 % | 10.5 s · 89 % · max 0 % |

### heavy, Y ≥ 0.6 (110 hours)

| controller | cycle s | main through P2/P6 | side through P4/P8 | main lefts P1/P5 | side lefts P3/P7 |
|---|---|---|---|---|---|
| Actuated | 102 | 39.4 s · 100 % · max 1 % | 22.8 s · 94 % · max 6 % | 12.4 s · 73 % · max 32 % | 12.3 s · 85 % · max 40 % |
| MaxPressure | 76 | 33.8 s · 100 % · max 1 % | 12.2 s · 94 % · max 0 % | 6.5 s · 61 % · max 0 % | 8.1 s · 82 % · max 6 % |
| LSTDQ | 112 | 58.4 s · 100 % · max 24 % | 19.9 s · 96 % · max 5 % | 8.5 s · 68 % · max 7 % | 8.3 s · 89 % · max 3 % |
| Q-learning | 68 | 27.6 s · 100 % · max 0 % | 11.7 s · 92 % · max 0 % | 6.5 s · 60 % · max 0 % | 7.7 s · 81 % · max 0 % |
| ARS | 75 | 29.1 s · 100 % · max 0 % | 14.3 s · 91 % · max 0 % | 6.5 s · 65 % · max 0 % | 10.9 s · 80 % · max 55 % |
| GDOT plan | 133 | 72.6 s · 100 % · max 0 % | 22.0 s · 98 % · max 0 % | 11.6 s · 71 % · max 0 % | 9.9 s · 92 % · max 0 % |

## RQ3: does the ranking hold?

### (a) Detector-count error: GDOT counts as reported vs corrected side-street demand (same days)

| model | Actuated | MaxPressure | LSTDQ | Q-learning | ARS | GDOT plan | Webster | ranking (adaptive) |
|---|---|---|---|---|---|---|---|---|
| first pass (reported counts) | 17.1 | 19.0 | 18.0 | 46.9 | 19.6 | 20.9 | 48.5 | Actuated > LSTDQ > MaxPressure > ARS > Q-learning |
| corrected counts (attempt 5) | 25.2 | 26.7 | 27.5 | 36.1 | 32.2 | 34.3 | 59.8 | Actuated > MaxPressure > LSTDQ > ARS > Q-learning |

The two models differ in the counted side-street and EB-left demand (and in pedestrians, passage times and left-turn calibration); the ranking change is the effect of the whole correction.

### (b) Training seeds: overall vehicle-weighted delay per seed (s/veh)

| learner | per seed | median | spread |
|---|---|---|---|
| LSTDQ | 31.0, 26.3, 29.7, 25.1, 25.5 | 26.3 | 6.0 |
| Q-learning | 38.7, 33.5, 36.0, 36.2, 35.9 | 36.0 | 5.2 |
| ARS | 32.4, 33.5, 31.9, 30.9, 32.1 | 32.1 | 2.6 |

### (c) Worst-served movement: 95th-percentile delay of the worst movement in the hour (s), by saturation

| condition | Actuated | MaxPressure | LSTDQ | Q-learning | ARS | GDOT plan | Webster |
|---|---|---|---|---|---|---|---|
| light, Y < 0.3 | 46 | 103 | 105 | 73 | 55 | 53 | 66 |
| moderate, 0.3–0.45 | 70 | 105 | 136 | 113 | 85 | 117 | 157 |
| busy, 0.45–0.6 | 79 | 104 | 128 | 120 | 85 | 161 | 155 |
| heavy, Y ≥ 0.6 | 115 | 203 | 219 | 261 | 200 | 300 | 312 |

## Comparison with actuated, daily vehicle-weighted delay over the validation days

Equivalence (H1): margin per day max(2 s/veh, 5 % of actuated), fixed before any result was read; paired TOST at 5 % (normal approximation). Difference: paired t-test and Wilcoxon signed-rank (two-sided), days won = days with less delay than actuated.

| method | mean diff (s/veh) | median diff | days won | p TOST | p t-test | p Wilcoxon | verdict |
|---|---|---|---|---|---|---|---|
| MaxPressure | +1.21 | -2.65 | 17/20 | 0.406 | 0.722 | 0.0400 | better on typical days (Wilcoxon), mean not significant |
| LSTDQ | +2.16 | -0.64 | 14/20 | 0.534 | 0.260 | 0.5958 | inconclusive |
| Q-learning | +10.06 | -0.98 | 11/20 | 0.887 | 0.146 | 0.2943 | inconclusive |
| ARS | +6.38 | -1.27 | 14/20 | 0.762 | 0.312 | 0.7841 | inconclusive |
| GDOT plan | +8.73 | +4.05 | 0/20 | 0.913 | 0.093 | 0.0000 | worse on typical days (Wilcoxon), mean not significant |
| Webster | +32.36 | +7.07 | 0/20 | 0.989 | 0.025 | 0.0000 | worse |

