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

## Amendment 1 (2026-11-06 23:45, after the registered results; registered results stay primary in the record)

Registered `nfq`:

- Overall delay: median 69.9 s/veh over 5 training seeds, against LSTDQ v2's 34.9 s/veh.
- Its fitted values average about −14. The cost-to-go its data and discount imply is about −30, and LSTDQ v2's
  values average −27.
- It ends a green at only 7–15 % of decisions; LSTDQ v2 ends at 56 %.

Cause, a design error in the matching:

- LSTDQ's 5 iterations per fit each solve the fixed point exactly.
- One fitted-Q backup only looks one decision (~1 s) further ahead. The registered 5 backups per fit (25 in
  all) therefore give a controller that sees about the next 25 s, while γ = 0.99/s implies about 100 s.
- Ending a green costs lost time now and pays off later, so a short-sighted controller keeps greens.
- The registered `nfq` therefore tests a truncated horizon, not neural vs linear. H2a cannot be judged on it.

Amended variant `nfq_conv`, identical except for the fit:

- Backups repeat until the targets change by less than 0.5 % (mean absolute, relative), at most 400 per fit.
- One epoch per backup, to bound the cost.
- The stopping rule uses only the training data, not validation results.

Reporting and status:

- H2a is reported on `nfq_conv`, with the registered `nfq` shown next to it and this amendment cited.
- If `nfq_conv` also fails or diverges, that is reported as it is. No further amendment will be made.
- `qlearn` and `ars` results are unaffected and stay as registered.

## Results (2026-11-07; `eval/report.md`, overall vehicle-weighted delay, median over 5 training seeds, simulation seed 1)

| Learner | median (min–max) s/veh |
|---|---|
| LSTDQ v2 | 34.9 (34.5–37.4) |
| `ars` | 34.9 (34.7–35.1) |
| `qlearn` | 39.3 (36.9–64.1) |
| `nfq` (registered) | 69.9 (66.6–75.0) |
| `nfq_conv` (amendment 1) | 49.3 (47.3–66.4) |
| MaxPressure (reference) | 34.5 |

- **H2a supported, with a weak neural comparator.** LSTDQ v2 (34.9) is well within 5 % of `nfq_conv` (49.3).
  - `nfq_conv` never met its stopping rule: every fit ran the 400-backup cap. Its mean fitted value ended
    near −20, against LSTDQ's −27.
  - It is also worse than actuated control (40.8).
  - What this shows: with the same data budget and no tuning, the neural fitted-Q learner is far worse and
    less stable than the linear one. It does **not** show that no neural controller can do better here.
- **H2b, first part (mean delay) supported.** LSTDQ v2 ties `ars` (34.9 vs 34.9) and beats `qlearn`.
- **H2b, second part (spread over seeds vs `qlearn`) supported.** LSTDQ v2's seeds span 2.9 s/veh, `qlearn`'s
  27.2.
- **H2b, third part (training episodes vs `ars`) on the boundary.**
  - The evaluated weights were fitted on 110 episodes, against `ars`'s 1,100: exactly 1/10.
  - LSTDQ's training runs 132 episodes; the last round is not used for the evaluated weights. Counting all
    132, it is 0.12, so this part is rejected.
- **Run note.** `nfq_conv` seed 4 hung in its last training round, the data-collection round after fit 5,
  whose data the evaluated policy does not use. Its fit-5 network was saved before the hang; the run was
  stopped after ~17 h. That seed has no train_log.csv; its per-round delays are in the run log only.

## DQN (fixed 2026-11-09, before any DQN training)

Added at the student's request as the deep-RL comparator. It is the standard neural Q-learner in the
signal-control literature. NFQ stays in the record: it shares LSTDQ's data loop, but it is untuned and did not
converge.

**Algorithm** (`atsc/rl/methods.py` `DQNLearner`):

- Base method: DQN (Mnih et al. 2015).
- Double-DQN target (van Hasselt et al. 2016), semi-MDP form: r + γ^d · q_target(s′, argmax_a q(s′, a)).
- Experience replay and a target network.
- Huber loss, Adam, gradient-norm clipping.
- Online: it learns from every transition as it happens, through the controller's learner hook.

Same controller as every learner in this file: the v2 state (312 values), the binary extend / end decision every
1 s after the minimum green, the v2 reward (/100), γ = 0.99 per second, NEMA rules, training days and windows.

**Settings.** Stable-Baselines3's DQN defaults where they apply, adapted to this problem's scale:

| Setting | Value | SB3 default and reason for any change |
|---|---|---|
| Network | 312 → 256 → 256 → 2, ReLU | default 64 × 64; widened for a 312-value input |
| Learning rate | 1e-4 (Adam) | default |
| Replay buffer | 500,000 transitions | default 1M; this is about 150 episodes |
| Batch | 64 | default 32 |
| Learning starts | 10,000 transitions | |
| Train frequency | 1 gradient step per 4 transitions | default |
| Target update | hard copy every 10,000 gradient steps | default |
| Max gradient norm | 10 | default |
| Exploration | ε from 1.0 to 0.05, linear over the first 25 % of episodes, then 0.05 | |
| Episodes | 400 (≈ 1.2M transitions, ≈ 300k gradient steps) | |

The 400 episodes are 3.6 × LSTDQ's 110, used to give a deep learner a fair budget. Training cost is reported
next to the delay.

**Rules for the run:**

- Training seeds 0–4, all reported.
- Evaluated network: the final one (episode 400), with no selection on validation days, as for every other
  learner. Checkpoints every 50 episodes and per-episode training curves are kept and reported.
- Settings are not tuned on results. If DQN diverges or degenerates, that is reported as it is.
- Evaluation: `evaluate.py run`, 20 validation weekdays × simulation seeds 1–3, the same as the other learners.

**Hypothesis H2a-DQN** (fixed now): LSTDQ v2's overall vehicle-weighted delay is within **5 %** of DQN's. Both
are medians over 5 training seeds, pooled over simulation seeds.

- Rejected if LSTDQ v2 > 1.05 × DQN.
- Training cost (wall-clock time, episodes) and spread over seeds are reported next to it, which covers RQ2's
  other criteria.
- With DQN in the comparison, H2a is judged on DQN. The NFQ result is reported as a secondary comparator.
