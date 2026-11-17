# 137 analysis: when and why each method wins (corrected-demand model, test weekdays)

7 days, 168 clean hours, learners pooled over training seeds. Model: attempt 7 (VALIDATION.md: + floating force-off P1/P5; V1 34/35, V2 29/35, V5 pass: accepted; V3 skips 19/35 reported).

## RQ1: how the ranking changes

### By saturation Y (sum of critical flow ratios, field counts)

| condition | hours | Actuated | MaxPressure | LSTDQ | Q-learning | ARS | GDOT plan | Webster | ranking (adaptive) |
|---|---|---|---|---|---|---|---|---|---|
| light, Y < 0.3 | 56 | 13.7 | 15.0 | 16.1 | 14.6 | 14.4 | 14.3 | 82.3 | Actuated > ARS > Q-learning > MaxPressure > LSTDQ |
| moderate, 0.3–0.45 | 11 | 20.0 | 20.1 | 24.7 | 21.3 | 21.3 | 25.8 | 201.7 | Actuated > MaxPressure > ARS > Q-learning > LSTDQ |
| busy, 0.45–0.6 | 61 | 24.7 | 24.7 | 26.6 | 28.6 | 25.6 | 29.4 | 48.0 | MaxPressure > Actuated > ARS > LSTDQ > Q-learning |
| heavy, Y ≥ 0.6 | 40 | 29.2 | 31.2 | 39.8 | 50.7 | 42.6 | 38.4 | 138.4 | Actuated > MaxPressure > LSTDQ > ARS > Q-learning |

### By time of day

| condition | hours | Actuated | MaxPressure | LSTDQ | Q-learning | ARS | GDOT plan | Webster | ranking (adaptive) |
|---|---|---|---|---|---|---|---|---|---|
| night 00–06 | 42 | 12.0 | 13.5 | 14.3 | 12.9 | 13.0 | 12.0 | 24.0 | Actuated > Q-learning > ARS > MaxPressure > LSTDQ |
| AM peak 06–10 | 28 | 23.1 | 21.3 | 22.4 | 22.5 | 22.4 | 26.2 | 28.3 | MaxPressure > ARS > LSTDQ > Q-learning > Actuated |
| midday 10–15 | 35 | 25.8 | 25.8 | 25.5 | 29.0 | 26.4 | 34.6 | 41.5 | LSTDQ > MaxPressure > Actuated > ARS > Q-learning |
| PM peak 15–19 | 28 | 28.0 | 31.2 | 38.0 | 43.3 | 35.1 | 33.6 | 38.4 | Actuated > MaxPressure > ARS > LSTDQ > Q-learning |
| evening 19–24 | 35 | 25.6 | 27.1 | 39.6 | 50.9 | 43.0 | 32.4 | 303.6 | Actuated > MaxPressure > LSTDQ > ARS > Q-learning |

### By within-hour variability (cv of the twelve 5-min totals)

| condition | hours | Actuated | MaxPressure | LSTDQ | Q-learning | ARS | GDOT plan | Webster | ranking (adaptive) |
|---|---|---|---|---|---|---|---|---|---|
| steady, cv < 0.15 | 73 | 25.9 | 25.6 | 28.8 | 33.3 | 29.3 | 29.7 | 58.6 | MaxPressure > Actuated > LSTDQ > ARS > Q-learning |
| variable, 0.15–0.25 | 38 | 26.8 | 29.5 | 36.0 | 41.7 | 35.6 | 39.3 | 100.3 | Actuated > MaxPressure > ARS > LSTDQ > Q-learning |
| very variable, cv ≥ 0.25 | 57 | 17.3 | 19.5 | 26.9 | 29.6 | 27.0 | 19.7 | 282.5 | Actuated > MaxPressure > LSTDQ > ARS > Q-learning |

- steady, cv < 0.15: mean volume 1863 veh/h
- variable, 0.15–0.25: mean volume 1641 veh/h
- very variable, cv ≥ 0.25: mean volume 411 veh/h

Variability and volume move together (quiet hours are the most variable), so this split is not independent of saturation.

## RQ2: what the controllers do (by saturation)

Per controller: cycle length; per phase group: average green per service, share of cycles served (100 % − skips), share of greens ended at max green. Learners: training seed 0.

### light, Y < 0.3 (56 hours)

| controller | cycle s | main through P2/P6 | side through P4/P8 | main lefts P1/P5 | side lefts P3/P7 |
|---|---|---|---|---|---|
| Actuated | 49 | 25.8 s · 100 % · max 0 % | 10.7 s · 15 % · max 0 % | 8.5 s · 11 % · max 2 % | 7.6 s · 90 % · max 1 % |
| MaxPressure | 94 | 70.4 s · 100 % · max 31 % | 10.0 s · 25 % · max 0 % | 6.7 s · 12 % · max 0 % | 7.8 s · 83 % · max 0 % |
| LSTDQ | 104 | 76.2 s · 100 % · max 45 % | 18.6 s · 27 % · max 10 % | 7.7 s · 14 % · max 12 % | 9.4 s · 83 % · max 1 % |
| Q-learning | 48 | 25.8 s · 100 % · max 0 % | 9.4 s · 15 % · max 0 % | 6.5 s · 11 % · max 0 % | 7.2 s · 91 % · max 0 % |
| ARS | 74 | 43.7 s · 100 % · max 3 % | 14.0 s · 22 % · max 3 % | 6.5 s · 15 % · max 0 % | 14.1 s · 87 % · max 53 % |
| GDOT plan | 50 | 27.2 s · 100 % · max 0 % | 10.8 s · 14 % · max 0 % | 8.4 s · 10 % · max 1 % | 7.6 s · 91 % · max 1 % |

### moderate, 0.3–0.45 (11 hours)

| controller | cycle s | main through P2/P6 | side through P4/P8 | main lefts P1/P5 | side lefts P3/P7 |
|---|---|---|---|---|---|
| Actuated | 68 | 29.0 s · 100 % · max 0 % | 15.2 s · 63 % · max 0 % | 9.4 s · 41 % · max 6 % | 12.0 s · 73 % · max 18 % |
| MaxPressure | 69 | 35.0 s · 100 % · max 2 % | 11.7 s · 66 % · max 0 % | 6.6 s · 40 % · max 0 % | 9.6 s · 71 % · max 4 % |
| LSTDQ | 87 | 47.4 s · 100 % · max 13 % | 16.1 s · 71 % · max 1 % | 7.3 s · 42 % · max 3 % | 10.9 s · 69 % · max 6 % |
| Q-learning | 59 | 27.1 s · 100 % · max 0 % | 11.0 s · 61 % · max 0 % | 6.5 s · 38 % · max 0 % | 9.0 s · 74 % · max 0 % |
| ARS | 67 | 28.5 s · 100 % · max 0 % | 13.3 s · 62 % · max 0 % | 6.6 s · 43 % · max 0 % | 12.7 s · 74 % · max 60 % |
| GDOT plan | 109 | 65.6 s · 100 % · max 0 % | 17.2 s · 70 % · max 0 % | 9.4 s · 43 % · max 2 % | 12.8 s · 78 % · max 8 % |

### busy, 0.45–0.6 (61 hours)

| controller | cycle s | main through P2/P6 | side through P4/P8 | main lefts P1/P5 | side lefts P3/P7 |
|---|---|---|---|---|---|
| Actuated | 85 | 32.3 s · 100 % · max 0 % | 19.7 s · 86 % · max 3 % | 10.4 s · 63 % · max 14 % | 12.1 s · 79 % · max 24 % |
| MaxPressure | 71 | 31.7 s · 100 % · max 0 % | 12.2 s · 87 % · max 0 % | 6.6 s · 54 % · max 0 % | 8.4 s · 78 % · max 3 % |
| LSTDQ | 98 | 51.5 s · 100 % · max 14 % | 15.9 s · 92 % · max 1 % | 7.6 s · 59 % · max 5 % | 9.2 s · 81 % · max 5 % |
| Q-learning | 66 | 27.6 s · 100 % · max 0 % | 11.9 s · 84 % · max 0 % | 6.5 s · 52 % · max 0 % | 8.2 s · 77 % · max 0 % |
| ARS | 72 | 28.0 s · 100 % · max 0 % | 13.9 s · 83 % · max 0 % | 6.6 s · 57 % · max 0 % | 11.5 s · 77 % · max 55 % |
| GDOT plan | 127 | 73.9 s · 100 % · max 0 % | 20.4 s · 94 % · max 0 % | 8.8 s · 60 % · max 0 % | 10.4 s · 87 % · max 1 % |

### heavy, Y ≥ 0.6 (40 hours)

| controller | cycle s | main through P2/P6 | side through P4/P8 | main lefts P1/P5 | side lefts P3/P7 |
|---|---|---|---|---|---|
| Actuated | 96 | 37.7 s · 100 % · max 1 % | 21.7 s · 90 % · max 6 % | 10.6 s · 70 % · max 17 % | 12.6 s · 83 % · max 41 % |
| MaxPressure | 75 | 33.8 s · 100 % · max 1 % | 12.2 s · 90 % · max 0 % | 6.6 s · 61 % · max 0 % | 8.4 s · 82 % · max 8 % |
| LSTDQ | 103 | 54.5 s · 100 % · max 16 % | 16.0 s · 93 % · max 3 % | 7.8 s · 63 % · max 7 % | 9.8 s · 85 % · max 14 % |
| Q-learning | 67 | 27.6 s · 100 % · max 0 % | 11.5 s · 89 % · max 0 % | 6.5 s · 56 % · max 0 % | 8.0 s · 80 % · max 0 % |
| ARS | 74 | 27.9 s · 100 % · max 0 % | 14.1 s · 86 % · max 0 % | 6.8 s · 63 % · max 1 % | 11.4 s · 81 % · max 57 % |
| GDOT plan | 134 | 76.0 s · 100 % · max 0 % | 22.4 s · 96 % · max 0 % | 9.0 s · 66 % · max 1 % | 10.7 s · 89 % · max 1 % |

## RQ3: does the ranking hold?

### (b) Training seeds: overall vehicle-weighted delay per seed (s/veh)

| learner | per seed | median | spread |
|---|---|---|---|
| LSTDQ | 27.4, 41.4, 25.6, 29.9, 28.7 | 28.7 | 15.7 |
| Q-learning | 36.2, 32.6, 36.2, 36.2, 35.5 | 36.2 | 3.6 |
| ARS | 37.2, 27.5, 30.8, 31.3, 27.4 | 30.8 | 9.8 |

### (c) Worst-served movement: 95th-percentile delay of the worst movement in the hour (s), by saturation

| condition | Actuated | MaxPressure | LSTDQ | Q-learning | ARS | GDOT plan | Webster |
|---|---|---|---|---|---|---|---|
| light, Y < 0.3 | 51 | 116 | 118 | 78 | 69 | 60 | 203 |
| moderate, 0.3–0.45 | 72 | 182 | 193 | 146 | 118 | 178 | 628 |
| busy, 0.45–0.6 | 93 | 195 | 230 | 212 | 145 | 197 | 170 |
| heavy, Y ≥ 0.6 | 129 | 248 | 371 | 359 | 272 | 322 | 541 |

## Comparison with actuated, daily vehicle-weighted delay over the test days (7 days)

Pre-registered (TEST_PLAN.md). Primary: paired t-test on the daily log ratio ln(delay / actuated delay), Holm-adjusted over the six comparisons; ratio = geometric mean with its 95 % t interval. Equivalence (H1, margin per day max(2 s/veh, 5 % of actuated), fixed 2026-11-16): paired TOST at 5 %, t distribution. Secondary (reported, no verdict): mean and median difference, days won, Wilcoxon signed-rank (its smallest possible two-sided p is 0.0156 with 7 days). Learners: mean over training seeds and simulation seeds per hour; other controllers: mean over simulation seeds.

| method | ratio to actuated (95 % CI) | p primary | p Holm | p TOST | mean diff (s/veh) | median diff | days won | p Wilcoxon | verdict |
|---|---|---|---|---|---|---|---|---|---|
| MaxPressure | 1.025 (0.912–1.151) | 0.6262 | 0.6262 | 0.212 | +0.87 | -0.35 | 4/7 | 1.0000 | inconclusive |
| LSTDQ | 1.198 (1.052–1.363) | 0.0143 | 0.0574 | 0.949 | +5.36 | +3.44 | 1/7 | 0.0312 | inconclusive |
| Q-learning | 1.328 (0.997–1.768) | 0.0516 | 0.1033 | 0.939 | +10.02 | +3.01 | 1/7 | 0.0312 | inconclusive |
| ARS | 1.196 (1.019–1.403) | 0.0337 | 0.1012 | 0.926 | +5.49 | +3.25 | 1/7 | 0.0469 | inconclusive |
| GDOT plan | 1.227 (1.070–1.406) | 0.0107 | 0.0533 | 0.965 | +6.10 | +2.33 | 0/7 | 0.0156 | inconclusive |
| Webster | 3.167 (1.748–5.738) | 0.0032 | 0.0190 | 0.993 | +67.86 | +71.17 | 0/7 | 0.0156 | worse |

### Per training seed against actuated (descriptive)

| learner seed | delay (s/veh) | ratio to actuated (geometric mean) | days won |
|---|---|---|---|
| lstdq_v2_s0 | 27.4 | 1.078 | 2/7 |
| lstdq_v2_s1 | 41.4 | 1.494 | 0/7 |
| lstdq_v2_s2 | 25.6 | 1.018 | 3/7 |
| lstdq_v2_s3 | 29.9 | 1.176 | 2/7 |
| lstdq_v2_s4 | 28.7 | 1.132 | 1/7 |
| qlearn_s0 | 36.2 | 1.350 | 1/7 |
| qlearn_s1 | 32.6 | 1.241 | 2/7 |
| qlearn_s2 | 36.2 | 1.361 | 1/7 |
| qlearn_s3 | 36.2 | 1.350 | 1/7 |
| qlearn_s4 | 35.5 | 1.331 | 1/7 |
| ars_s0 | 37.2 | 1.404 | 1/7 |
| ars_s1 | 27.5 | 1.074 | 3/7 |
| ars_s2 | 30.8 | 1.186 | 1/7 |
| ars_s3 | 31.3 | 1.198 | 2/7 |
| ars_s4 | 27.4 | 1.066 | 4/7 |

