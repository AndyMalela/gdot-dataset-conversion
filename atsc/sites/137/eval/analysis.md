# 137 analysis: when and why each method wins (corrected-demand model, validation weekdays)

20 days, 480 clean hours, learners pooled over training seeds. Model: attempt 7 (VALIDATION.md: + floating force-off P1/P5; V1 34/35, V2 29/35, V5 pass: accepted; V3 skips 19/35 reported).

## RQ1: how the ranking changes

### By saturation Y (sum of critical flow ratios, field counts)

| condition | hours | Actuated | MaxPressure | LSTDQ | Q-learning | ARS | GDOT plan | Webster | ranking (adaptive) |
|---|---|---|---|---|---|---|---|---|---|
| light, Y < 0.3 | 164 | 11.8 | 13.9 | 14.2 | 11.8 | 12.3 | 12.6 | 46.0 | Q-learning > Actuated > ARS > MaxPressure > LSTDQ |
| moderate, 0.3–0.45 | 42 | 19.0 | 22.0 | 19.1 | 21.9 | 21.6 | 22.2 | 127.7 | Actuated > LSTDQ > ARS > Q-learning > MaxPressure |
| busy, 0.45–0.6 | 164 | 24.2 | 22.3 | 22.3 | 23.5 | 23.6 | 27.7 | 79.7 | MaxPressure > LSTDQ > Q-learning > ARS > Actuated |
| heavy, Y ≥ 0.6 | 110 | 31.5 | 39.0 | 31.3 | 48.5 | 62.0 | 50.6 | 193.2 | LSTDQ > Actuated > MaxPressure > Q-learning > ARS |

### By time of day

| condition | hours | Actuated | MaxPressure | LSTDQ | Q-learning | ARS | GDOT plan | Webster | ranking (adaptive) |
|---|---|---|---|---|---|---|---|---|---|
| night 00–06 | 120 | 9.2 | 13.8 | 12.4 | 9.8 | 10.1 | 9.2 | 23.2 | Actuated > Q-learning > ARS > LSTDQ > MaxPressure |
| AM peak 06–10 | 80 | 27.1 | 34.0 | 25.8 | 36.5 | 38.7 | 31.2 | 49.1 | LSTDQ > Actuated > MaxPressure > Q-learning > ARS |
| midday 10–15 | 100 | 28.0 | 33.1 | 27.8 | 38.5 | 49.5 | 51.2 | 98.6 | LSTDQ > Actuated > MaxPressure > Q-learning > ARS |
| PM peak 15–19 | 80 | 26.0 | 23.5 | 24.3 | 27.6 | 28.5 | 27.1 | 93.6 | MaxPressure > LSTDQ > Actuated > Q-learning > ARS |
| evening 19–24 | 100 | 21.7 | 20.2 | 21.3 | 24.4 | 29.1 | 25.2 | 290.7 | MaxPressure > LSTDQ > Actuated > Q-learning > ARS |

### By within-hour variability (cv of the twelve 5-min totals)

| condition | hours | Actuated | MaxPressure | LSTDQ | Q-learning | ARS | GDOT plan | Webster | ranking (adaptive) |
|---|---|---|---|---|---|---|---|---|---|
| steady, cv < 0.15 | 254 | 26.3 | 26.5 | 24.7 | 30.3 | 34.8 | 36.1 | 106.8 | LSTDQ > Actuated > MaxPressure > Q-learning > ARS |
| variable, 0.15–0.25 | 78 | 26.8 | 36.7 | 28.5 | 42.8 | 53.6 | 33.6 | 213.9 | Actuated > LSTDQ > MaxPressure > Q-learning > ARS |
| very variable, cv ≥ 0.25 | 148 | 14.1 | 19.3 | 16.4 | 19.3 | 17.9 | 19.5 | 76.6 | Actuated > LSTDQ > ARS > MaxPressure > Q-learning |

- steady, cv < 0.15: mean volume 1894 veh/h
- variable, 0.15–0.25: mean volume 1379 veh/h
- very variable, cv ≥ 0.25: mean volume 377 veh/h

Variability and volume move together (quiet hours are the most variable), so this split is not independent of saturation.

## RQ2: what the controllers do (by saturation)

Per controller: cycle length; per phase group: average green per service, share of cycles served (100 % − skips), share of greens ended at max green. Learners: training seed 0.

### light, Y < 0.3 (164 hours)

| controller | cycle s | main through P2/P6 | side through P4/P8 | main lefts P1/P5 | side lefts P3/P7 |
|---|---|---|---|---|---|
| Actuated | 95 | 69.1 s · 100 % · max 0 % | 10.6 s · 74 % · max 0 % | 8.7 s · 15 % · max 3 % | 9.7 s · 32 % · max 6 % |
| MaxPressure | 118 | 93.2 s · 100 % · max 24 % | 10.0 s · 71 % · max 0 % | 6.7 s · 15 % · max 0 % | 8.6 s · 37 % · max 1 % |
| LSTDQ | 110 | 71.7 s · 100 % · max 0 % | 24.6 s · 74 % · max 45 % | 7.5 s · 20 % · max 8 % | 13.8 s · 33 % · max 0 % |
| Q-learning | 91 | 67.3 s · 100 % · max 0 % | 9.3 s · 75 % · max 0 % | 6.5 s · 14 % · max 0 % | 8.3 s · 31 % · max 0 % |
| ARS | 102 | 72.1 s · 100 % · max 0 % | 16.1 s · 73 % · max 9 % | 7.4 s · 17 % · max 8 % | 10.6 s · 33 % · max 28 % |
| GDOT plan | 99 | 73.6 s · 100 % · max 0 % | 10.6 s · 74 % · max 0 % | 8.6 s · 15 % · max 3 % | 9.8 s · 32 % · max 6 % |

### moderate, 0.3–0.45 (42 hours)

| controller | cycle s | main through P2/P6 | side through P4/P8 | main lefts P1/P5 | side lefts P3/P7 |
|---|---|---|---|---|---|
| Actuated | 69 | 31.4 s · 100 % · max 0 % | 14.6 s · 74 % · max 1 % | 9.6 s · 44 % · max 8 % | 11.8 s · 55 % · max 19 % |
| MaxPressure | 69 | 36.7 s · 100 % · max 1 % | 11.5 s · 73 % · max 0 % | 6.6 s · 41 % · max 0 % | 8.9 s · 59 % · max 1 % |
| LSTDQ | 73 | 36.9 s · 100 % · max 0 % | 14.7 s · 75 % · max 6 % | 7.1 s · 44 % · max 1 % | 9.7 s · 58 % · max 1 % |
| Q-learning | 60 | 29.2 s · 100 % · max 0 % | 10.8 s · 75 % · max 0 % | 6.5 s · 40 % · max 0 % | 8.6 s · 53 % · max 0 % |
| ARS | 66 | 30.8 s · 100 % · max 0 % | 12.9 s · 75 % · max 1 % | 8.1 s · 43 % · max 14 % | 10.8 s · 55 % · max 32 % |
| GDOT plan | 105 | 64.5 s · 100 % · max 0 % | 15.5 s · 77 % · max 0 % | 9.1 s · 43 % · max 2 % | 12.2 s · 64 % · max 5 % |

### busy, 0.45–0.6 (164 hours)

| controller | cycle s | main through P2/P6 | side through P4/P8 | main lefts P1/P5 | side lefts P3/P7 |
|---|---|---|---|---|---|
| Actuated | 85 | 32.6 s · 100 % · max 0 % | 19.6 s · 89 % · max 2 % | 10.4 s · 63 % · max 14 % | 12.1 s · 74 % · max 27 % |
| MaxPressure | 69 | 30.4 s · 100 % · max 0 % | 12.0 s · 89 % · max 0 % | 6.6 s · 55 % · max 0 % | 8.2 s · 73 % · max 2 % |
| LSTDQ | 83 | 39.7 s · 100 % · max 0 % | 14.6 s · 91 % · max 2 % | 7.4 s · 57 % · max 2 % | 8.8 s · 76 % · max 3 % |
| Q-learning | 66 | 27.9 s · 100 % · max 0 % | 11.8 s · 89 % · max 0 % | 6.5 s · 54 % · max 0 % | 7.9 s · 71 % · max 0 % |
| ARS | 72 | 29.8 s · 100 % · max 0 % | 13.6 s · 88 % · max 0 % | 9.0 s · 56 % · max 24 % | 9.0 s · 73 % · max 19 % |
| GDOT plan | 129 | 75.7 s · 100 % · max 0 % | 20.2 s · 95 % · max 0 % | 8.8 s · 60 % · max 0 % | 10.3 s · 87 % · max 0 % |

### heavy, Y ≥ 0.6 (110 hours)

| controller | cycle s | main through P2/P6 | side through P4/P8 | main lefts P1/P5 | side lefts P3/P7 |
|---|---|---|---|---|---|
| Actuated | 99 | 38.6 s · 100 % · max 1 % | 22.8 s · 94 % · max 6 % | 10.6 s · 72 % · max 17 % | 12.2 s · 82 % · max 39 % |
| MaxPressure | 73 | 31.7 s · 100 % · max 0 % | 12.2 s · 94 % · max 0 % | 6.6 s · 60 % · max 0 % | 7.9 s · 79 % · max 5 % |
| LSTDQ | 92 | 45.2 s · 100 % · max 2 % | 15.3 s · 95 % · max 2 % | 7.7 s · 63 % · max 6 % | 8.5 s · 83 % · max 6 % |
| Q-learning | 69 | 28.5 s · 100 % · max 0 % | 11.9 s · 94 % · max 0 % | 6.5 s · 59 % · max 0 % | 7.5 s · 77 % · max 0 % |
| ARS | 76 | 30.0 s · 100 % · max 0 % | 14.5 s · 93 % · max 1 % | 9.5 s · 63 % · max 31 % | 8.6 s · 79 % · max 18 % |
| GDOT plan | 133 | 75.3 s · 100 % · max 0 % | 22.1 s · 98 % · max 0 % | 8.8 s · 66 % · max 0 % | 9.8 s · 92 % · max 0 % |

## RQ3: does the ranking hold?

### (a) Detector-count error: GDOT counts as reported vs corrected side-street demand (same days)

| model | Actuated | MaxPressure | LSTDQ | Q-learning | ARS | GDOT plan | Webster | ranking (adaptive) |
|---|---|---|---|---|---|---|---|---|
| first pass (reported counts) | 17.1 | 19.0 | 18.0 | 46.9 | 19.6 | 20.9 | 48.5 | Actuated > LSTDQ > MaxPressure > ARS > Q-learning |
| corrected counts (attempt 7 model) | 25.3 | 27.6 | 24.6 | 31.5 | 36.5 | 34.3 | 122.0 | LSTDQ > Actuated > MaxPressure > Q-learning > ARS |

The two models differ in the counted side-street and EB-left demand (and in pedestrians, passage times and left-turn calibration); the ranking change is the effect of the whole correction.

### (b) Training seeds: overall vehicle-weighted delay per seed (s/veh)

| learner | per seed | median | spread |
|---|---|---|---|
| LSTDQ | 23.8, 24.2, 24.7, 24.5, 25.7 | 24.5 | 1.9 |
| Q-learning | 34.0, 31.1, 32.4, 27.0, 32.8 | 32.4 | 7.0 |
| ARS | 37.2, 31.3, 40.0, 32.2, 41.6 | 37.2 | 10.3 |

### (c) Worst-served movement: 95th-percentile delay of the worst movement in the hour (s), by saturation

| condition | Actuated | MaxPressure | LSTDQ | Q-learning | ARS | GDOT plan | Webster |
|---|---|---|---|---|---|---|---|
| light, Y < 0.3 | 40 | 89 | 62 | 43 | 45 | 48 | 100 |
| moderate, 0.3–0.45 | 67 | 118 | 92 | 104 | 95 | 117 | 409 |
| busy, 0.45–0.6 | 77 | 106 | 100 | 112 | 98 | 162 | 253 |
| heavy, Y ≥ 0.6 | 104 | 205 | 155 | 229 | 243 | 304 | 668 |

## Comparison with actuated, daily vehicle-weighted delay over the validation days (20 days)

Pre-registered (TEST_PLAN.md). Primary: paired t-test on the daily log ratio ln(delay / actuated delay), Holm-adjusted over the six comparisons; ratio = geometric mean with its 95 % t interval. Equivalence (H1, margin per day max(2 s/veh, 5 % of actuated), fixed 2026-11-16): paired TOST at 5 %, t distribution. Secondary (reported, no verdict): mean and median difference, days won, Wilcoxon signed-rank (its smallest possible two-sided p is 1.91e-06 with 20 days). Learners: mean over training seeds and simulation seeds per hour; other controllers: mean over simulation seeds.

| method | ratio to actuated (95 % CI) | p primary | p Holm | p TOST | mean diff (s/veh) | median diff | days won | p Wilcoxon | verdict |
|---|---|---|---|---|---|---|---|---|---|
| MaxPressure | 1.003 (0.903–1.115) | 0.9460 | 0.9460 | 0.511 | +2.10 | -1.89 | 17/20 | 0.0759 | inconclusive |
| LSTDQ | 0.958 (0.932–0.985) | 0.0042 | 0.0209 | 0.016 | -0.74 | -1.34 | 19/20 | 0.0007 | equivalent |
| Q-learning | 1.098 (0.968–1.246) | 0.1372 | 0.3582 | 0.799 | +5.76 | -0.59 | 11/20 | 0.2455 | inconclusive |
| ARS | 1.144 (0.963–1.359) | 0.1194 | 0.3582 | 0.836 | +10.44 | -0.25 | 11/20 | 0.4091 | inconclusive |
| GDOT plan | 1.186 (1.050–1.340) | 0.0086 | 0.0342 | 0.871 | +8.57 | +2.78 | 0/20 | 0.0000 | worse |
| Webster | 2.484 (1.626–3.795) | 0.0002 | 0.0015 | 0.989 | +90.41 | +15.49 | 0/20 | 0.0000 | worse |

### Per training seed against actuated (descriptive)

| learner seed | delay (s/veh) | ratio to actuated (geometric mean) | days won |
|---|---|---|---|
| lstdq_v2_s0 | 23.8 | 0.926 | 18/20 |
| lstdq_v2_s1 | 24.2 | 0.945 | 19/20 |
| lstdq_v2_s2 | 24.7 | 0.944 | 19/20 |
| lstdq_v2_s3 | 24.5 | 0.951 | 19/20 |
| lstdq_v2_s4 | 25.7 | 1.020 | 7/20 |
| qlearn_s0 | 34.0 | 1.109 | 11/20 |
| qlearn_s1 | 31.1 | 1.087 | 11/20 |
| qlearn_s2 | 32.4 | 1.113 | 11/20 |
| qlearn_s3 | 27.0 | 1.046 | 11/20 |
| qlearn_s4 | 32.8 | 1.107 | 11/20 |
| ars_s0 | 37.2 | 1.134 | 11/20 |
| ars_s1 | 31.3 | 1.088 | 12/20 |
| ars_s2 | 40.0 | 1.185 | 9/20 |
| ars_s3 | 32.2 | 1.097 | 12/20 |
| ars_s4 | 41.6 | 1.200 | 9/20 |

