# Phase cycles — SIG 7065 (Peachtree Rd @ Piedmont Rd)

How each controller in this project cycles through the signal phases. Sources: GDOT Split Monitor / Timing & Actuation records (`timing/timing_plan_7065.json`, `timing/clearance.json`, `timing/phase_map.json`), EXP-009 Webster plan, `rlagent/dualring_env.py`.

## Phases (GDOT numbering)

| Phase | Movement | Yellow + all-red (s) |
|---|---|---|
| P1 | Peachtree from SW, left (protected only) | 4.5 + 2.8 |
| P2 | Peachtree from NE, through (coordinated) | 3.1 + 2.6 |
| P3 | Piedmont from N, left (protected; then flashing yellow in P4) | 3.7 + 2.9 |
| P4 | Piedmont from S, through (+ P3's left on flashing yellow) | 3.6 + 3.0 |
| P5 | Peachtree from NE, left (protected only) | 4.2 + 3.0 |
| P6 | Peachtree from SW, through (coordinated) | 3.3 + 3.0 |
| P7 | Piedmont from S, left (protected; then flashing yellow in P8) | 3.0 + 3.2 |
| P8 | Piedmont from N, through (+ P7's left on flashing yellow) | 3.6 + 3.0 |

Right turns: Piedmont rights get a green arrow with their through phase; the Peachtree-SW right shares the through lane; the Peachtree-NE right is a free slip lane (no signal).

## Ring structure (all controllers)

```
Ring 1:  P2 → P1  ‖  P3 → P4  ‖
Ring 2:  P5 → P6  ‖  P7 → P8  ‖
          Peachtree   Piedmont      ‖ = barrier: both rings cross together
```

- Ring 1 runs the NE-through **before** the SW-left (P1 lags); ring 2 runs the NE-left **before** the SW-through (P5 leads).
- So within the Peachtree half: P2+P5 (all NE traffic) → P2+P6 (both throughs) → P1+P6 (all SW traffic).
- Piedmont lefts lead their throughs (P3, P7 first).

## 1. Real GDOT timing — 8 plans (split = green + yellow + red, seconds)

| Plan | Cycle | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 | Peachtree side | Piedmont side | Full split every cycle* |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **A** | 160 | 35 | 50 | 25 | 50 | 33 | 52 | 15 | 60 | 85 | 75 | P4, P7, P8 |
| **B** | 160 | 33 | 60 | 24 | 43 | 37 | 56 | 15 | 52 | 93 | 67 | P3, P4, P7, P8 |
| **C** | 180 | 25 | 85 | 27 | 43 | 43 | 67 | 15 | 55 | 110 | 70 | P3, P4, P7, P8 |
| **D** | 130 | 25 | 45 | 15 | 45 | 30 | 40 | 16 | 44 | 70 | 60 | P4 |
| **E** | 120 | 20 | 50 | – | 50 | 20 | 50 | – | 50 | 70 | 50 | – |
| **F** | 160 | 35 | 55 | 20 | 50 | 27 | 63 | 18 | 52 | 90 | 70 | P4, P5, P8 |
| **G** | 140 | 28 | 47 | 20 | 45 | 25 | 50 | 20 | 45 | 75 | 65 | P4, P8 |
| **H** | 130 | 20 | 50 | 16 | 44 | 30 | 40 | 15 | 45 | 70 | 60 | P1, P7 |

*Phases that (almost) never end early in GDOT's records (< 5% gap-outs) run their whole split every cycle in our simulation (max recall). P2/P6 are coordinated and also run full. Other phases end early when traffic clears and pass the time on.

### When each plan runs

| Day | Schedule |
|---|---|
| Weekday (39 of 64 days exactly; others differ only at changeovers) | 00:00 **E** · 06:15 **A** · 13:30 **B** · 15:30 **C** · 19:00 **B** · 19:30 **D** · 21:45 **E** |
| Saturday (11 of 12) | 00:00 **E** · 08:15 **G** · 11:30 **F** · 18:30 **G** · 20:45 **H** |
| Sunday (most common) | 00:00 **E** · 09:15 **G** · 11:30 **F** · 20:30 **H** |

### Cycle diagrams (1 character ≈ 2 s; `‖` = barrier; numbers = split in seconds)

**Plan A — 160 s**

```
Ring 1: [·········P2 50·········][·····P1 35·····]‖[···P3 25···][·········P4 50·········]‖
Ring 2: [····P5 33·····][·········P6 52··········]‖[P7 15·][···········P8 60············]‖
```

**Plan B — 160 s**

```
Ring 1: [···········P2 60············][····P1 33·····]‖[··P3 24···][·······P4 43········]‖
Ring 2: [·····P5 37······][··········P6 56···········]‖[P7 15·][·········P8 52··········]‖
```

**Plan C — 180 s**

```
Ring 1: [·················P2 85··················][···P1 25···]‖[···P3 27···][·······P4 43········]‖
Ring 2: [·······P5 43········][·············P6 67·············]‖[P7 15][··········P8 55···········]‖
```

**Plan D — 130 s**

```
Ring 1: [·······P2 45········][···P1 25···]‖[P3 15][········P4 45········]‖
Ring 2: [····P5 30····][······P6 40·······]‖[P7 16·][·······P8 44········]‖
```

**Plan E — 120 s**

```
Ring 1: [·········P2 50·········][·P1 20··]‖[·········P4 50·········]‖
Ring 2: [·P5 20··][·········P6 50·········]‖[·········P8 50·········]‖
```

**Plan F — 160 s**

```
Ring 1: [··········P2 55···········][·····P1 35·····]‖[·P3 20··][·········P4 50·········]‖
Ring 2: [···P5 27····][············P6 63············]‖[·P7 18·][·········P8 52··········]‖
```

**Plan G — 140 s**

```
Ring 1: [········P2 47·········][···P1 28····]‖[·P3 20··][·······P4 45········]‖
Ring 2: [··P5 25···][·········P6 50··········]‖[·P7 20··][·······P8 45········]‖
```

**Plan H — 130 s**

```
Ring 1: [·········P2 50·········][·P1 20··]‖[P3 16·][·······P4 44········]‖
Ring 2: [····P5 30····][······P6 40·······]‖[P7 15][········P8 45········]‖
```

## 2. Webster (EXP-009) — one fixed plan all day

Designed from the 31 training weekdays (median PM peak hour per movement), same phases, order and clearances as GDOT, with pedestrian minimum greens (walk 7 s + flashing don't-walk) on P2/P4/P6/P8. Cycle **125.1 s**, no actuation (every phase runs its full split every cycle).

| | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 |
|---|---|---|---|---|---|---|---|---|
| Green (s) | 7.5 | 36 | 18.5 | 36.9 | 10.8 | 32.2 | 5.3 | 50.5 |
| Split (s) | 14.8 | 41.7 | 25.1 | 43.5 | 18 | 38.5 | 11.5 | 57.1 |

```
Ring 1: [······P2 41.7······][P1 15]‖[··P3 25.1··][······P4 43.5·······]‖
Ring 2: [·P5 18·][·····P6 38.5·····]‖[P7][··········P8 57.1··········]‖
```

## 3. RL (dual-ring LSTDQ, EXP-008/009) — no fixed cycle

Same phases, order, barriers and clearances as GDOT. Every second each ring decides *hold* or *advance*, within these limits:

| | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 |
|---|---|---|---|---|---|---|---|---|
| Min green (s) | 4.2 | 29.0* | 4.2 | 36.9* | 6.8 | 32.2* | 4.2 | 37.5* |
| Max green (s) | 27.7 | 79.3 | 20.4 | 43.4 | 35.8 | 60.7 | 9.8 | 53.4 |

*pedestrian minimum (walk 7 s + measured flashing don't-walk), every cycle. Other mins are GDOT's measured minimum greens; max greens are the largest green GDOT programs for that phase in any plan. A left with no car waiting is skipped; a ring that finishes first holds its last green until the other ring is ready (barrier). In practice the trained policy ran ~118–125 s cycles in every period (EXP-008).

## Cycle length at a glance

| Controller | Night | AM | Midday | PM | Evening |
|---|---|---|---|---|---|
| Real GDOT (weekday) | 120 (E) | 160 (A) | 160 (A/B) | 180 (C) | 160/130/120 (B/D/E) |
| Webster | 125.1 | 125.1 | 125.1 | 125.1 | 125.1 |
| RL | ~118 | ~120 | ~120 | ~125 | ~120 |

