# Other learners on the same controller: design fixed before training (2026-11-06)

Written after the LSTDQ v1/v2/v2f training-seed results (`eval/report.md`) and **before** any training of the
methods below. Settings are chosen from the methods' papers and common practice, not tuned on results.

## Question

LSTDQ v2 and MaxPressure now see the same detector information. What is left to compare is the **learning
method**. Every method below uses the same controller as LSTDQ v2:

- the same v2 state (phase-gated detector features and queue estimate, 312 values);
- the same binary action per ring (extend / end), decided every 1 s after the minimum;
- the same NEMA rules;
- the same training days and windows.

Only the learning method changes. This separates three things a methods comparison usually mixes:

| Method | Decision rule | How it is learnt | Isolates |
|---|---|---|---|
| LSTDQ v2 (existing) | linear Q | batch least squares on all data (LSPI) | reference |
| `qlearn` | linear Q, same features | online Q-learning, one transition at a time | batch vs online learning of the same linear model |
| `nfq` | neural network Q (312 → 64 → 64 → 2, ReLU) | neural fitted Q iteration, same LSPI loop and data | what the linear form costs (or protects) |
| `ars` | linear policy: end if θ·x > 0 | augmented random search on the delay itself, no value function | value-based vs direct policy search for a linear controller |

`qlearn` and `nfq` are trained on the v2 reward. `ars` has no reward signal per step. Its objective is the score
itself: the mean delay per vehicle of the training window.

## Settings (fixed now)

- **qlearn**
  - 110 episodes one after another. That is the same episode budget LSTDQ's evaluated weights were fitted on
    (5 × 22), and the same days, windows and seeds as LSTDQ v2 of the same training seed.
  - Episodes 1–22 use the actuated rule plus 20 % random actions; Q-learning is off-policy, so it learns from them.
  - After that: greedy on the live weights, plus 10 % random actions.
  - Update: w_a += α·δ·x / (x·x), with α = 0.05 (normalised LMS step, chosen for stability without tuning),
    γ = 0.99 per second, and rewards divided by 100 as in LSTDQ.
- **nfq**
  - The LSPI loop of `train_lstdq.py` unchanged: 6 rounds × 22 episodes, the same exploration, and refitting
    on all data so far.
  - Each fit: 5 fitted-Q iterations × 2 epochs, Adam (learning rate 1e-3, batch 512), squared error, warm start.
  - Output scale 50 (the order of the Q values).
- **ars** (Mania et al. 2018, basic version with top-b directions, no state normalisation; the features are
  already scaled)
  - 50 iterations, θ₀ = 0.
  - Each iteration tries N = 11 directions, each as θ ± νδ on the same day, window and simulation seed, with
    ν = 0.03.
  - The top b = 6 directions update θ, with step α = 0.02.
  - 1,100 episodes in total, **10 × LSTDQ's**. Direct search needs more samples, and that sample cost is
    part of the result.
- Training seeds 0–4 for each method; all reported, none dropped.
- Evaluated policy: the final iterate of each run (qlearn after 110 episodes, nfq fit 5, ars iteration 50).
  No selection on validation days.

## Evaluation (fixed now)

- `evaluate.py run --seeds 1`, on the same 20 validation weekdays as LSTDQ's extra training seeds.
- Reported like LSTDQ: per method, the spread over training seeds of overall delay, the same measures by
  traffic condition (Y bins), and the worst-off movement.
- Comparisons:
  - `qlearn` vs LSTDQ v2: batch vs online.
  - `nfq` vs LSTDQ v2: nonlinear vs linear with the same data.
  - `ars` vs LSTDQ v2: direct search vs value-based.
  - All of them against MaxPressure: learnt vs rule, on equal information.
- Divergence or a degenerate policy (for example, never ending a green) is a result and is reported, not
  re-run with other settings.
