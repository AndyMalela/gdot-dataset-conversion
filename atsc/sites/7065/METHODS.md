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

## Place in the research questions (fixed 2026-11-06, before any validation result of these methods)

In `queries/research-questions-framing.md` (draft), RQ2 asks whether a neural network beats linear methods. It
judges this on four criteria: delay on held-out days, training cost, consistency across seeds and
interpretability. H2 says linear comes within a pre-set margin of the neural network's delay.

The methods here make RQ2 and H2 testable, and extend RQ2 to the learning method within the linear family:

- **RQ2a (neural vs linear).** `nfq` is the neural learner. It is trained on the same data loop as LSTDQ. That
  is a cleaner contrast than DQN (online, with replay and a target network), which would change the data and
  the learner at once.
- **RQ2b (which linear learner).** With the same features, does the learning method matter? The three options
  are batch least squares (LSTDQ v2), online TD (`qlearn`) and direct policy search (`ars`).

Hypotheses (margin and comparators fixed now):

- **H2a.** LSTDQ v2's overall vehicle-weighted delay is within **5 %** of `nfq`'s. Both are the median over 5
  training seeds on simulation seed 1. LSTDQ v2 should also use less training wall-clock time.
  - Same test per traffic-condition bin, reported as a secondary result.
  - Rejected if LSTDQ v2 > 1.05 × `nfq`.
- **H2b.** Among linear learners with the same features:
  - LSTDQ v2 is within 5 % of the better of `qlearn` and `ars`.
  - LSTDQ v2 has a smaller spread over training seeds (max − min) than `qlearn`.
  - LSTDQ v2 uses at most 1/10 of `ars`'s training episodes.
  - Each part is rejected on its own. Expected from LSPI's sample efficiency and stability over online TD
    (Lagoudakis & Parr 2003) and ARS's sample cost (Mania et al. 2018).
- **RQ1 / H1.** All learners also enter the condition map: which method wins at which degree of saturation.
  The linear family in RQ1 is LSTDQ v1/v2/v2f, `qlearn` and `ars`, with `nfq` as the neural learner.

Deviations from the draft protocol, stated with the results:

- The final iterate is evaluated, not a checkpoint picked on validation days.
- 1 simulation seed per extra training seed, not 10.
- The neural learner is NFQ, not DQN.
- 7065 is not isolated: it is in GDOT's coordinated Peachtree group.

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
