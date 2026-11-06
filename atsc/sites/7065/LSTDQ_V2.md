# LSTDQ v2: design fixed before training (2026-11-06)

Written after the first RQ1 evaluation (`eval/report.md`: MaxPressure lowest delay in most hours, LSTDQ v1 lowest
worst-movement delay) and **before** any v2 training. The changes fix two unfair or misaligned parts of v1. They
were not tuned on results. v1 stays in every result as it is.

## Why change v1

1. **Information.** MaxPressure keeps a running queue estimate per phase (vehicles counted in minus discharge). LSTDQ
   v1 sees only the last 30 s of counts, occupancy and time since the last vehicle, so a queue that has built for
   90 s of red looks almost like a short one. Both read the same detectors, so "MaxPressure beats LSTDQ" currently
   mixes the decision method with the information each one gets.
2. **Reward vs score.** v1 is rewarded for vehicles standing still (speed < 0.1 m/s); every controller is scored on
   delay (SUMO time loss + waiting to enter), which also counts slow crawling and braking/accelerating.
3. **Rings.** Each ring decides without seeing the other ring, although the effect of ending a green depends on it
   (ending can only park the ring at the barrier while the other ring still runs).

## Variants

| | v1 (unchanged) | v2 | v2f |
|---|---|---|---|
| Per-phase features | occ, gap, rate | + queue estimate (MaxPressure's estimator, same detectors) | same as v2 |
| Deciding-phase features | elapsed / max green, bias | + other ring: current phase (one-hot over its 4 phases), its elapsed / max green | same as v2 |
| Reward per second | − (vehicles stopped on the approaches + waiting to enter) | − (delay rate on the approaches + waiting to enter); delay rate = Σ edges vehicles × (1 − mean speed / speed limit) | v2 − Σ (accumulated waiting time of stopped vehicles) / 60 s |

v2f: each stopped vehicle costs 1 per second plus 1/60 per second for every second it has already waited, so a
vehicle at 60 s of waiting costs twice as much per second as one that just stopped (total cost grows with the
square of the wait). Purpose: make protection of the longest waits a designed property, after v1 showed it only
as a side effect. The 60 s scale is fixed here and not tuned.

Queue feature: estimated queue / (lanes x 20 veh), capped at 2. Everything else (action space, decision every 1 s
after the minimum, phase-gated blocks, discount 0.99/s, LSPI 5 iterations x 22 episodes, exploration, training
windows and days) is unchanged from v1.

## Training and evaluation (fixed now)

- Training seeds: v1 seeds 1-4 (seed 0 = the existing run), v2 seeds 0-4, v2f seeds 0-4. All reported; none dropped.
- Policy evaluated: iteration 5 of every seed (no selection on validation days).
- Evaluation: `evaluate.py run`, 20 validation weekdays, simulation seed 1 for every training seed; the existing
  3-seed runs stay for v1 seed 0 and the baselines.
- Primary metric: mean delay per vehicle. Reported per variant as the spread over training seeds (median, min,
  max), by traffic condition, plus the secondary measures (regret, worst-off movement, spillback hours).
- Comparisons that answer the question: v2 vs v1 = value of the information and reward fixes; v2 vs MaxPressure =
  decision method with equal information; v2f vs v2 = cost of designed fairness in mean delay.
