# 137 analysis: when and why each method wins (corrected-demand model, validation weekdays)

20 days, 480 clean hours, learners pooled over training seeds. Model: attempt 7 (VALIDATION.md: + floating force-off P1/P5; V1 34/35, V2 29/35, V5 pass: accepted; V3 skips 19/35 reported).

## RQ1: how the ranking changes

### By saturation Y (sum of critical flow ratios, field counts)

| condition | hours | Actuated | MaxPressure | LSTDQ | Q-learning | ARS | GDOT plan | Webster | ranking (adaptive) |
|---|---|---|---|---|---|---|---|---|---|
| light, Y < 0.3 | 164 | 14.5 | 16.1 | 16.6 | 15.5 | 15.6 | 15.1 | 26.6 | Actuated > Q-learning > ARS > MaxPressure > LSTDQ |
| moderate, 0.3–0.45 | 42 | 20.1 | 20.8 | 22.0 | 23.1 | 22.0 | 22.9 | 43.5 | Actuated > MaxPressure > ARS > LSTDQ > Q-learning |
| busy, 0.45–0.6 | 164 | 24.5 | 22.1 | 23.4 | 24.6 | 24.1 | 27.5 | 49.9 | MaxPressure > LSTDQ > ARS > Actuated > Q-learning |
| heavy, Y ≥ 0.6 | 110 | 31.5 | 36.5 | 34.4 | 62.6 | 58.0 | 49.7 | 87.2 | Actuated > LSTDQ > MaxPressure > ARS > Q-learning |

### By time of day

| condition | hours | Actuated | MaxPressure | LSTDQ | Q-learning | ARS | GDOT plan | Webster | ranking (adaptive) |
|---|---|---|---|---|---|---|---|---|---|
| night 00–06 | 120 | 12.8 | 16.8 | 15.6 | 15.0 | 14.7 | 12.8 | 24.0 | Actuated > ARS > Q-learning > LSTDQ > MaxPressure |
| AM peak 06–10 | 80 | 27.4 | 30.7 | 27.0 | 39.3 | 36.6 | 30.6 | 39.3 | LSTDQ > Actuated > MaxPressure > ARS > Q-learning |
| midday 10–15 | 100 | 28.2 | 31.6 | 28.7 | 42.0 | 42.0 | 50.4 | 58.1 | Actuated > LSTDQ > MaxPressure > ARS > Q-learning |
| PM peak 15–19 | 80 | 26.2 | 23.5 | 28.4 | 33.8 | 30.5 | 27.0 | 35.3 | MaxPressure > Actuated > LSTDQ > ARS > Q-learning |
| evening 19–24 | 100 | 22.5 | 20.7 | 23.5 | 38.0 | 34.8 | 25.7 | 127.6 | MaxPressure > Actuated > LSTDQ > ARS > Q-learning |

### By within-hour variability (cv of the twelve 5-min totals)

| condition | hours | Actuated | MaxPressure | LSTDQ | Q-learning | ARS | GDOT plan | Webster | ranking (adaptive) |
|---|---|---|---|---|---|---|---|---|---|
| steady, cv < 0.15 | 254 | 26.5 | 25.7 | 26.4 | 35.0 | 33.4 | 35.8 | 51.0 | MaxPressure > LSTDQ > Actuated > ARS > Q-learning |
| variable, 0.15–0.25 | 78 | 27.4 | 34.8 | 32.0 | 56.5 | 53.3 | 33.5 | 119.1 | Actuated > LSTDQ > MaxPressure > ARS > Q-learning |
| very variable, cv ≥ 0.25 | 148 | 16.3 | 20.0 | 19.2 | 23.5 | 19.4 | 21.0 | 34.3 | Actuated > LSTDQ > ARS > MaxPressure > Q-learning |

- steady, cv < 0.15: mean volume 1894 veh/h
- variable, 0.15–0.25: mean volume 1379 veh/h
- very variable, cv ≥ 0.25: mean volume 377 veh/h

Variability and volume move together (quiet hours are the most variable), so this split is not independent of saturation.

## RQ2: what the controllers do (by saturation)

Per controller: cycle length; per phase group: average green per service, share of cycles served (100 % − skips), share of greens ended at max green. Learners: training seed 0.

### light, Y < 0.3 (164 hours)

| controller | cycle s | main through P2/P6 | side through P4/P8 | main lefts P1/P5 | side lefts P3/P7 |
|---|---|---|---|---|---|
| Actuated | 49 | 25.9 s · 100 % · max 0 % | 11.7 s · 17 % · max 0 % | 8.6 s · 11 % · max 3 % | 7.7 s · 89 % · max 1 % |
| MaxPressure | 93 | 69.0 s · 100 % · max 32 % | 10.5 s · 28 % · max 0 % | 6.7 s · 13 % · max 0 % | 7.9 s · 81 % · max 0 % |
| LSTDQ | 102 | 73.8 s · 100 % · max 42 % | 19.1 s · 29 % · max 10 % | 7.8 s · 14 % · max 12 % | 9.3 s · 81 % · max 1 % |
| Q-learning | 48 | 25.9 s · 100 % · max 0 % | 9.6 s · 17 % · max 0 % | 6.5 s · 11 % · max 0 % | 7.2 s · 89 % · max 0 % |
| ARS | 74 | 43.3 s · 100 % · max 4 % | 14.8 s · 24 % · max 4 % | 6.5 s · 16 % · max 0 % | 14.1 s · 85 % · max 53 % |
| GDOT plan | 50 | 27.3 s · 100 % · max 0 % | 11.8 s · 16 % · max 0 % | 8.6 s · 11 % · max 2 % | 7.7 s · 90 % · max 1 % |

### moderate, 0.3–0.45 (42 hours)

| controller | cycle s | main through P2/P6 | side through P4/P8 | main lefts P1/P5 | side lefts P3/P7 |
|---|---|---|---|---|---|
| Actuated | 68 | 29.5 s · 100 % · max 0 % | 14.8 s · 57 % · max 1 % | 9.5 s · 45 % · max 7 % | 11.8 s · 78 % · max 13 % |
| MaxPressure | 70 | 36.2 s · 100 % · max 1 % | 11.4 s · 61 % · max 0 % | 6.6 s · 44 % · max 0 % | 9.3 s · 75 % · max 1 % |
| LSTDQ | 95 | 54.5 s · 100 % · max 21 % | 15.9 s · 70 % · max 2 % | 7.3 s · 47 % · max 3 % | 10.3 s · 75 % · max 3 % |
| Q-learning | 59 | 27.4 s · 100 % · max 0 % | 10.7 s · 55 % · max 0 % | 6.5 s · 40 % · max 0 % | 8.9 s · 77 % · max 0 % |
| ARS | 67 | 28.9 s · 100 % · max 0 % | 13.0 s · 58 % · max 0 % | 6.5 s · 46 % · max 0 % | 12.8 s · 76 % · max 58 % |
| GDOT plan | 102 | 61.3 s · 100 % · max 0 % | 16.0 s · 61 % · max 1 % | 9.2 s · 43 % · max 3 % | 11.9 s · 83 % · max 4 % |

### busy, 0.45–0.6 (164 hours)

| controller | cycle s | main through P2/P6 | side through P4/P8 | main lefts P1/P5 | side lefts P3/P7 |
|---|---|---|---|---|---|
| Actuated | 86 | 32.5 s · 100 % · max 0 % | 19.5 s · 86 % · max 2 % | 10.3 s · 64 % · max 14 % | 12.2 s · 81 % · max 25 % |
| MaxPressure | 71 | 31.4 s · 100 % · max 0 % | 11.9 s · 86 % · max 0 % | 6.6 s · 55 % · max 0 % | 8.5 s · 79 % · max 2 % |
| LSTDQ | 96 | 50.3 s · 100 % · max 12 % | 15.3 s · 91 % · max 1 % | 7.6 s · 59 % · max 4 % | 9.2 s · 82 % · max 5 % |
| Q-learning | 66 | 27.7 s · 100 % · max 0 % | 11.6 s · 85 % · max 0 % | 6.5 s · 54 % · max 0 % | 8.3 s · 78 % · max 0 % |
| ARS | 72 | 28.0 s · 100 % · max 0 % | 13.8 s · 83 % · max 0 % | 6.6 s · 59 % · max 0 % | 11.3 s · 79 % · max 55 % |
| GDOT plan | 129 | 75.5 s · 100 % · max 0 % | 20.2 s · 94 % · max 0 % | 8.8 s · 59 % · max 0 % | 10.4 s · 89 % · max 0 % |

### heavy, Y ≥ 0.6 (110 hours)

| controller | cycle s | main through P2/P6 | side through P4/P8 | main lefts P1/P5 | side lefts P3/P7 |
|---|---|---|---|---|---|
| Actuated | 99 | 38.5 s · 100 % · max 1 % | 22.6 s · 94 % · max 6 % | 10.6 s · 72 % · max 17 % | 12.3 s · 84 % · max 39 % |
| MaxPressure | 76 | 34.0 s · 100 % · max 1 % | 12.3 s · 93 % · max 0 % | 6.6 s · 60 % · max 0 % | 8.1 s · 82 % · max 6 % |
| LSTDQ | 105 | 55.9 s · 100 % · max 16 % | 15.7 s · 96 % · max 1 % | 7.8 s · 65 % · max 6 % | 9.3 s · 87 % · max 11 % |
| Q-learning | 68 | 27.6 s · 100 % · max 0 % | 11.7 s · 92 % · max 0 % | 6.5 s · 60 % · max 0 % | 7.7 s · 80 % · max 0 % |
| ARS | 74 | 27.8 s · 100 % · max 0 % | 14.3 s · 90 % · max 0 % | 6.8 s · 64 % · max 1 % | 11.1 s · 80 % · max 56 % |
| GDOT plan | 133 | 75.4 s · 100 % · max 0 % | 22.0 s · 98 % · max 0 % | 8.8 s · 65 % · max 0 % | 9.8 s · 92 % · max 0 % |

## RQ3: does the ranking hold?

### (a) Detector-count error: GDOT counts as reported vs corrected side-street demand (same days)

| model | Actuated | MaxPressure | LSTDQ | Q-learning | ARS | GDOT plan | Webster | ranking (adaptive) |
|---|---|---|---|---|---|---|---|---|
| first pass (reported counts) | 17.1 | 19.0 | 18.0 | 46.9 | 19.6 | 20.9 | 48.5 | Actuated > LSTDQ > MaxPressure > ARS > Q-learning |
| corrected counts (attempt 7 model) | 25.8 | 26.7 | 26.7 | 37.6 | 35.5 | 34.1 | 60.9 | Actuated > MaxPressure > LSTDQ > ARS > Q-learning |

The two models differ in the counted side-street and EB-left demand (and in pedestrians, passage times and left-turn calibration); the ranking change is the effect of the whole correction.

### (b) Training seeds: overall vehicle-weighted delay per seed (s/veh)

| learner | per seed | median | spread |
|---|---|---|---|
| LSTDQ | 25.0, 30.2, 25.8, 26.3, 26.2 | 26.2 | 5.2 |
| Q-learning | 38.3, 36.3, 37.8, 38.1, 37.3 | 37.8 | 2.0 |
| ARS | 45.0, 29.3, 36.3, 36.5, 30.6 | 36.3 | 15.7 |

### (c) Worst-served movement: 95th-percentile delay of the worst movement in the hour (s), by saturation

| condition | Actuated | MaxPressure | LSTDQ | Q-learning | ARS | GDOT plan | Webster |
|---|---|---|---|---|---|---|---|
| light, Y < 0.3 | 45 | 106 | 99 | 71 | 62 | 54 | 68 |
| moderate, 0.3–0.45 | 68 | 103 | 134 | 116 | 96 | 117 | 158 |
| busy, 0.45–0.6 | 78 | 105 | 125 | 123 | 94 | 160 | 156 |
| heavy, Y ≥ 0.6 | 104 | 190 | 205 | 276 | 224 | 300 | 317 |

## Comparison with actuated, daily vehicle-weighted delay over the validation days (20 days)

Pre-registered (TEST_PLAN.md). Primary: paired t-test on the daily log ratio ln(delay / actuated delay), Holm-adjusted over the six comparisons; ratio = geometric mean with its 95 % t interval. Equivalence (H1, margin per day max(2 s/veh, 5 % of actuated), fixed 2026-11-16): paired TOST at 5 %, t distribution. Secondary (reported, no verdict): mean and median difference, days won, Wilcoxon signed-rank (with 7 days its smallest possible two-sided p is 0.016). Learners: mean over training seeds and simulation seeds per hour; other controllers: mean over simulation seeds.

| method | ratio to actuated (95 % CI) | p primary | p Holm | p TOST | mean diff (s/veh) | median diff | days won | p Wilcoxon | verdict |
|---|---|---|---|---|---|---|---|---|---|
| MaxPressure | 0.973 (0.892–1.060) | 0.5058 | 0.8584 | 0.291 | +0.76 | -2.06 | 17/20 | 0.0759 | inconclusive |
| LSTDQ | 1.022 (0.966–1.081) | 0.4292 | 0.8584 | 0.112 | +0.92 | -0.26 | 12/20 | 0.7285 | inconclusive |
| Q-learning | 1.215 (1.017–1.451) | 0.0336 | 0.1345 | 0.925 | +10.99 | -0.23 | 11/20 | 0.1536 | inconclusive |
| ARS | 1.148 (0.972–1.355) | 0.0985 | 0.2956 | 0.866 | +9.04 | -0.53 | 12/20 | 0.6742 | inconclusive |
| GDOT plan | 1.174 (1.044–1.321) | 0.0099 | 0.0496 | 0.867 | +7.97 | +2.81 | 0/20 | 0.0000 | worse |
| Webster | 1.700 (1.300–2.223) | 0.0006 | 0.0033 | 0.984 | +32.89 | +7.62 | 0/20 | 0.0000 | worse |

### Per training seed against actuated (descriptive)

| learner seed | delay (s/veh) | ratio to actuated (geometric mean) | days won |
|---|---|---|---|
| lstdq_v2_s0 | 25.0 | 0.969 | 17/20 |
| lstdq_v2_s1 | 30.2 | 1.102 | 8/20 |
| lstdq_v2_s2 | 25.8 | 0.984 | 17/20 |
| lstdq_v2_s3 | 26.3 | 1.015 | 13/20 |
| lstdq_v2_s4 | 26.2 | 1.010 | 12/20 |
| qlearn_s0 | 38.3 | 1.224 | 10/20 |
| qlearn_s1 | 36.3 | 1.186 | 11/20 |
| qlearn_s2 | 37.8 | 1.226 | 10/20 |
| qlearn_s3 | 38.1 | 1.217 | 10/20 |
| qlearn_s4 | 37.3 | 1.208 | 11/20 |
| ars_s0 | 45.0 | 1.313 | 8/20 |
| ars_s1 | 29.3 | 1.021 | 13/20 |
| ars_s2 | 36.3 | 1.166 | 10/20 |
| ars_s3 | 36.5 | 1.125 | 11/20 |
| ars_s4 | 30.6 | 1.041 | 13/20 |

