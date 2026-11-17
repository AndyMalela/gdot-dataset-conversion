# 137 analysis: when and why each method wins (corrected-demand model, test weekdays)

7 days, 168 clean hours, learners pooled over training seeds. Model: attempt 7 (VALIDATION.md: + floating force-off P1/P5; V1 34/35, V2 29/35, V5 pass: accepted; V3 skips 19/35 reported).

## RQ1: how the ranking changes

### By saturation Y (sum of critical flow ratios, field counts)

| condition | hours | Actuated | MaxPressure | LSTDQ | Q-learning | ARS | GDOT plan | Webster | ranking (adaptive) |
|---|---|---|---|---|---|---|---|---|---|
| light, Y < 0.3 | 56 | 10.8 | 13.1 | 13.4 | 10.6 | 11.1 | 11.7 | 94.4 | Q-learning > Actuated > ARS > MaxPressure > LSTDQ |
| moderate, 0.3–0.45 | 11 | 19.3 | 19.2 | 19.5 | 19.2 | 19.3 | 25.3 | 227.1 | Q-learning > MaxPressure > Actuated > ARS > LSTDQ |
| busy, 0.45–0.6 | 61 | 24.5 | 25.0 | 23.4 | 27.2 | 25.7 | 29.5 | 57.9 | LSTDQ > Actuated > MaxPressure > ARS > Q-learning |
| heavy, Y ≥ 0.6 | 40 | 29.3 | 31.5 | 31.1 | 41.1 | 42.4 | 38.7 | 181.9 | Actuated > LSTDQ > MaxPressure > Q-learning > ARS |

### By time of day

| condition | hours | Actuated | MaxPressure | LSTDQ | Q-learning | ARS | GDOT plan | Webster | ranking (adaptive) |
|---|---|---|---|---|---|---|---|---|---|
| night 00–06 | 42 | 8.2 | 11.2 | 11.6 | 8.1 | 8.5 | 8.2 | 23.1 | Q-learning > Actuated > ARS > MaxPressure > LSTDQ |
| AM peak 06–10 | 28 | 22.8 | 21.2 | 21.1 | 21.8 | 21.9 | 26.1 | 30.6 | LSTDQ > MaxPressure > Q-learning > ARS > Actuated |
| midday 10–15 | 35 | 25.8 | 26.0 | 24.2 | 27.9 | 26.8 | 35.0 | 85.4 | LSTDQ > Actuated > MaxPressure > ARS > Q-learning |
| PM peak 15–19 | 28 | 27.8 | 32.0 | 30.6 | 42.2 | 38.2 | 34.0 | 42.7 | Actuated > LSTDQ > MaxPressure > ARS > Q-learning |
| evening 19–24 | 35 | 25.1 | 26.9 | 26.9 | 33.3 | 38.2 | 31.8 | 344.9 | Actuated > MaxPressure > LSTDQ > Q-learning > ARS |

### By within-hour variability (cv of the twelve 5-min totals)

| condition | hours | Actuated | MaxPressure | LSTDQ | Q-learning | ARS | GDOT plan | Webster | ranking (adaptive) |
|---|---|---|---|---|---|---|---|---|---|
| steady, cv < 0.15 | 73 | 25.8 | 25.7 | 25.2 | 29.6 | 29.4 | 29.7 | 81.7 | LSTDQ > MaxPressure > Actuated > ARS > Q-learning |
| variable, 0.15–0.25 | 38 | 26.6 | 30.1 | 27.9 | 37.4 | 36.5 | 39.7 | 123.8 | Actuated > LSTDQ > MaxPressure > ARS > Q-learning |
| very variable, cv ≥ 0.25 | 57 | 15.0 | 17.8 | 18.4 | 18.0 | 20.0 | 17.6 | 310.4 | Actuated > MaxPressure > Q-learning > LSTDQ > ARS |

- steady, cv < 0.15: mean volume 1863 veh/h
- variable, 0.15–0.25: mean volume 1641 veh/h
- very variable, cv ≥ 0.25: mean volume 411 veh/h

Variability and volume move together (quiet hours are the most variable), so this split is not independent of saturation.

## RQ2: what the controllers do (by saturation)

Per controller: cycle length; per phase group: average green per service, share of cycles served (100 % − skips), share of greens ended at max green. Learners: training seed 0.

### light, Y < 0.3 (56 hours)

| controller | cycle s | main through P2/P6 | side through P4/P8 | main lefts P1/P5 | side lefts P3/P7 |
|---|---|---|---|---|---|
| Actuated | 91 | 66.9 s · 100 % · max 0 % | 10.0 s · 75 % · max 0 % | 8.6 s · 14 % · max 1 % | 9.3 s · 31 % · max 6 % |
| MaxPressure | 117 | 92.8 s · 100 % · max 25 % | 9.8 s · 70 % · max 0 % | 6.6 s · 14 % · max 0 % | 8.4 s · 38 % · max 1 % |
| LSTDQ | 108 | 69.6 s · 100 % · max 0 % | 24.8 s · 74 % · max 47 % | 7.6 s · 19 % · max 9 % | 14.2 s · 32 % · max 0 % |
| Q-learning | 89 | 65.7 s · 100 % · max 0 % | 9.2 s · 75 % · max 0 % | 6.5 s · 13 % · max 0 % | 8.3 s · 30 % · max 0 % |
| ARS | 100 | 70.1 s · 100 % · max 0 % | 15.8 s · 73 % · max 8 % | 7.2 s · 16 % · max 7 % | 10.5 s · 33 % · max 26 % |
| GDOT plan | 96 | 71.2 s · 100 % · max 0 % | 9.9 s · 74 % · max 0 % | 8.5 s · 13 % · max 1 % | 9.4 s · 31 % · max 5 % |

### moderate, 0.3–0.45 (11 hours)

| controller | cycle s | main through P2/P6 | side through P4/P8 | main lefts P1/P5 | side lefts P3/P7 |
|---|---|---|---|---|---|
| Actuated | 69 | 30.0 s · 100 % · max 0 % | 15.7 s · 77 % · max 0 % | 9.3 s · 42 % · max 5 % | 12.1 s · 54 % · max 24 % |
| MaxPressure | 67 | 34.8 s · 100 % · max 2 % | 11.8 s · 76 % · max 0 % | 6.6 s · 37 % · max 1 % | 9.1 s · 57 % · max 4 % |
| LSTDQ | 71 | 34.1 s · 100 % · max 0 % | 15.5 s · 77 % · max 6 % | 7.1 s · 41 % · max 1 % | 10.2 s · 54 % · max 4 % |
| Q-learning | 59 | 28.3 s · 100 % · max 0 % | 11.1 s · 75 % · max 0 % | 6.5 s · 37 % · max 0 % | 8.3 s · 54 % · max 0 % |
| ARS | 65 | 29.7 s · 100 % · max 0 % | 13.3 s · 77 % · max 0 % | 8.1 s · 40 % · max 14 % | 10.5 s · 53 % · max 30 % |
| GDOT plan | 110 | 66.4 s · 101 % · max 0 % | 17.1 s · 81 % · max 0 % | 9.3 s · 44 % · max 1 % | 13.2 s · 62 % · max 10 % |

### busy, 0.45–0.6 (61 hours)

| controller | cycle s | main through P2/P6 | side through P4/P8 | main lefts P1/P5 | side lefts P3/P7 |
|---|---|---|---|---|---|
| Actuated | 84 | 32.3 s · 100 % · max 0 % | 19.8 s · 89 % · max 3 % | 10.3 s · 63 % · max 15 % | 11.9 s · 72 % · max 26 % |
| MaxPressure | 69 | 30.5 s · 100 % · max 0 % | 12.3 s · 89 % · max 0 % | 6.6 s · 54 % · max 1 % | 8.1 s · 72 % · max 3 % |
| LSTDQ | 83 | 40.0 s · 100 % · max 1 % | 15.1 s · 91 % · max 3 % | 7.3 s · 56 % · max 2 % | 8.7 s · 74 % · max 2 % |
| Q-learning | 66 | 27.9 s · 100 % · max 0 % | 12.0 s · 89 % · max 0 % | 6.5 s · 52 % · max 0 % | 7.9 s · 68 % · max 0 % |
| ARS | 72 | 29.5 s · 100 % · max 0 % | 13.9 s · 89 % · max 0 % | 8.8 s · 55 % · max 22 % | 8.9 s · 70 % · max 17 % |
| GDOT plan | 127 | 73.8 s · 100 % · max 0 % | 20.4 s · 95 % · max 0 % | 8.8 s · 60 % · max 0 % | 10.3 s · 85 % · max 1 % |

### heavy, Y ≥ 0.6 (40 hours)

| controller | cycle s | main through P2/P6 | side through P4/P8 | main lefts P1/P5 | side lefts P3/P7 |
|---|---|---|---|---|---|
| Actuated | 96 | 37.6 s · 100 % · max 1 % | 22.0 s · 91 % · max 6 % | 10.6 s · 69 % · max 17 % | 12.5 s · 80 % · max 42 % |
| MaxPressure | 72 | 31.4 s · 100 % · max 1 % | 12.1 s · 91 % · max 0 % | 6.6 s · 58 % · max 0 % | 8.3 s · 77 % · max 7 % |
| LSTDQ | 92 | 45.2 s · 100 % · max 1 % | 15.7 s · 92 % · max 4 % | 7.7 s · 62 % · max 6 % | 9.0 s · 81 % · max 7 % |
| Q-learning | 68 | 28.8 s · 100 % · max 0 % | 11.7 s · 91 % · max 0 % | 6.5 s · 58 % · max 0 % | 7.7 s · 76 % · max 0 % |
| ARS | 76 | 30.4 s · 100 % · max 0 % | 14.5 s · 90 % · max 1 % | 9.5 s · 61 % · max 31 % | 8.9 s · 78 % · max 21 % |
| GDOT plan | 133 | 76.0 s · 100 % · max 0 % | 22.3 s · 97 % · max 0 % | 9.0 s · 66 % · max 1 % | 10.7 s · 88 % · max 1 % |

## RQ3: does the ranking hold?

### (b) Training seeds: overall vehicle-weighted delay per seed (s/veh)

| learner | per seed | median | spread |
|---|---|---|---|
| LSTDQ | 24.8, 24.7, 23.9, 25.3, 27.5 | 24.8 | 3.6 |
| Q-learning | 31.8, 29.6, 30.8, 29.5, 31.2 | 30.8 | 2.3 |
| ARS | 29.7, 28.5, 31.8, 29.4, 32.7 | 29.7 | 4.2 |

### (c) Worst-served movement: 95th-percentile delay of the worst movement in the hour (s), by saturation

| condition | Actuated | MaxPressure | LSTDQ | Q-learning | ARS | GDOT plan | Webster |
|---|---|---|---|---|---|---|---|
| light, Y < 0.3 | 46 | 112 | 74 | 50 | 53 | 56 | 222 |
| moderate, 0.3–0.45 | 71 | 147 | 105 | 127 | 111 | 180 | 661 |
| busy, 0.45–0.6 | 93 | 184 | 152 | 196 | 158 | 204 | 220 |
| heavy, Y ≥ 0.6 | 134 | 251 | 232 | 321 | 284 | 332 | 716 |

## Comparison with actuated, daily vehicle-weighted delay over the test days (7 days)

Pre-registered (TEST_PLAN.md). Primary: paired t-test on the daily log ratio ln(delay / actuated delay), Holm-adjusted over the six comparisons; ratio = geometric mean with its 95 % t interval. Equivalence (H1, margin per day max(2 s/veh, 5 % of actuated), fixed 2026-11-16): paired TOST at 5 %, t distribution. Secondary (reported, no verdict): mean and median difference, days won, Wilcoxon signed-rank (its smallest possible two-sided p is 0.0156 with 7 days). Learners: mean over training seeds and simulation seeds per hour; other controllers: mean over simulation seeds.

| method | ratio to actuated (95 % CI) | p primary | p Holm | p TOST | mean diff (s/veh) | median diff | days won | p Wilcoxon | verdict |
|---|---|---|---|---|---|---|---|---|---|
| MaxPressure | 1.037 (0.894–1.204) | 0.5691 | 1.0000 | 0.355 | +1.31 | -1.05 | 4/7 | 0.9375 | inconclusive |
| LSTDQ | 1.014 (0.953–1.078) | 0.6111 | 1.0000 | 0.026 | +0.41 | -0.04 | 4/7 | 0.9375 | equivalent |
| Q-learning | 1.190 (0.952–1.486) | 0.1045 | 0.3135 | 0.864 | +5.74 | +0.75 | 2/7 | 0.1094 | inconclusive |
| ARS | 1.192 (1.002–1.418) | 0.0479 | 0.1916 | 0.913 | +5.46 | +2.82 | 1/7 | 0.0469 | inconclusive |
| GDOT plan | 1.239 (1.079–1.423) | 0.0091 | 0.0456 | 0.969 | +6.36 | +2.56 | 0/7 | 0.0156 | worse |
| Webster | 4.348 (2.851–6.631) | 0.0001 | 0.0009 | 0.998 | +91.83 | +75.88 | 0/7 | 0.0156 | worse |

### Per training seed against actuated (descriptive)

| learner seed | delay (s/veh) | ratio to actuated (geometric mean) | days won |
|---|---|---|---|
| lstdq_v2_s0 | 24.8 | 0.995 | 4/7 |
| lstdq_v2_s1 | 24.7 | 0.991 | 5/7 |
| lstdq_v2_s2 | 23.9 | 0.961 | 6/7 |
| lstdq_v2_s3 | 25.3 | 1.013 | 5/7 |
| lstdq_v2_s4 | 27.5 | 1.104 | 1/7 |
| qlearn_s0 | 31.8 | 1.224 | 2/7 |
| qlearn_s1 | 29.6 | 1.156 | 2/7 |
| qlearn_s2 | 30.8 | 1.193 | 2/7 |
| qlearn_s3 | 29.5 | 1.159 | 1/7 |
| qlearn_s4 | 31.2 | 1.208 | 2/7 |
| ars_s0 | 29.7 | 1.170 | 1/7 |
| ars_s1 | 28.5 | 1.125 | 2/7 |
| ars_s2 | 31.8 | 1.240 | 1/7 |
| ars_s3 | 29.4 | 1.156 | 2/7 |
| ars_s4 | 32.7 | 1.262 | 1/7 |

