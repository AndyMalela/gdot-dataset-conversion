# EXP-008 — linear-FA + LSTDQ RL on GDOT's 8-phase dual ring

**Status (2026-10-05): first result, preliminary (one seed, one training day, one simulation seed).**
Verified by the independent monitor review (numbers recomputed from tripinfo; constraints checked on the
signal states SUMO displayed in two 1 h greedy replays).

## Setup

- Environment `rlagent/dualring_env.py`: GDOT's phases P1–P8 with the same link mapping as the real-timing
  controller; ring order P2→P1 | P3→P4 and P5→P6 | P7→P8; both rings cross the barrier together; measured
  yellow/red per phase (whole-second steps, rounding remainder carried so they average the measured values);
  measured vehicle min greens; pedestrian minimum on every through phase every cycle (walk 7 s + measured FDW);
  max greens = largest GDOT programs in any plan; uncalled lefts skipped; a ring that is done rests in green
  at the barrier. Each ring decides EXTEND/ADVANCE every second (4 joint actions). No coordination.
- Learner: `rlagent/train_dualring.py` — LinearQ + LSTDQ on all experience, ε = 0.05, γ = 0.99/s, ridge 1e-4.
  1 seed, 10 full-day episodes on 2026-09-29 at 1.0× (no demand scaling). Final weights used (no selection).
- Evaluation `data/eval_exp008.py`: same metric, demand files, SUMO seed (9999) and 30 h drain as EXP-007.

## Results (Oct 2, total delay s/veh; 47,149/47,149 served, 0 teleports, 0 collisions)

| Controller | Night 00–06 | AM 06–10 | Midday 10–15 | PM 15–18 | Evening 18–24 | Whole day |
|---|---|---|---|---|---|---|
| **RL, dual ring (this exp.)** | 30.6 | 36.9 | 36.9 | 39.3 | 36.0 | **36.6** |
| Webster, dual ring + ped minimums (EXP-007) | 34.5 | 38.1 | 39.2 | 40.6 | 39.5 | 39.0 |
| Real GDOT timing, actuated (EXP-007) | 32.3 | 45.7 | 48.9 | 69.7 | 50.6 | 51.2 |
| Real GDOT timing, fixed exact order (EXP-007) | 32.5 | 48.0 | 49.8 | 68.5 | 49.9 | 51.5 |

Sep 30 (not used for selection; detector outage 20:05–23:55): RL 37.1 whole day. Mean RL cycle ~118–125 s in
every period (plausible: minimum with ped minimums ≈ 83 s, ≈ 107 s with all lefts).

Whole day by movement, RL / real actuated / Webster+peds:

| Movement | RL | Real | Webster+peds |
|---|---|---|---|
| Piedmont from N, through | 33 | 66 | 31 |
| Piedmont from N, left | 33 | 46 | 24 |
| Piedmont from S, through | 31 | 48 | 38 |
| Piedmont from S, left | 29 | 45 | 28 |
| Peachtree from SW, through | 34 | 34 | 39 |
| Peachtree from SW, left | 50 | 66 | 67 |
| Peachtree from NE, through | 39 | 36 | 40 |
| Peachtree from NE, left | 56 | 67 | 65 |

## Monitor checks (passed)
Ped minimums held every time a through phase ran; vehicle minimums held; max greens obeyed while timing
(≤ 0.6 s whole-second overrun); longer greens only while resting at the barrier (NEMA behaviour); yellows
average the measured values; every concurrent phase pair legal under ring/barrier rules.

## Caveats (must accompany the numbers)
- One RL seed, one training day, one simulation seed, no selection: the 2.4 s/veh lead over Webster is small
  and unproven until repeated over seeds and days.
- RL advantages Webster's pretimed plan doesn't have: skips uncalled lefts (the real actuated controller can
  too); "perfect detection" — lane counts over the whole approach and route-based left-turn calls within 30 m
  (incl. vehicles not yet in the left lane).
- RL vs real timing carries EXP-007's caveats: counted (capped) demand, Poisson arrivals with no platoon credit
  for GDOT's coordination, RL runs free while GDOT coordinates Peachtree. Report as "in the twin".
- Minor: P4+P7 concurrency legal but never seen in GDOT's records; vehicle min greens from the Oct 2 record;
  max greens from different plans allow up to ~201 s cycles (observed ≤ 139 s); one 1 s all-red at a barrier.
