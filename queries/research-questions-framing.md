---
title: "Framing the research questions: compare methods on one intersection, then replicate"
tags: [query, research-design, research-questions, hypotheses, linear-rl, baselines, evaluation]
date: 2026-10-19
---

# Framing the research questions

This page saves one exchange: my working note (my questions plus my professor's comments) and the discussion that followed. It is the current best draft of the background, goal, hypotheses, RQs and approach.

Related: [[experimental-setup-across-papers]] (seeds, splits, statistics) · [[baseline-selection]] · [[demand-robustness]] · [[sahachaiseree2025-linear-fa-tsc]]

---

## Part A: my note (as written, 2026-10-19)

**Situation**
- I have 8 intersections built from OSM.
- I have about 60 days of data at 1 of them.
- I can scrape as many more days or intersections as I want.
- I have the real field timing, though it performs worse than Webster.

**Questions for me**
1. If we compare one method across intersection topologies and types, does that mean retraining the weight matrix for each intersection?
2. How many days should be used for training?

**Candidate learning algorithms (linear)**
- LSTDQ / LSPI
- SARSA
- LSPE(λ) (Least Squares Policy Evaluation) / linear TD(λ)
- Linear actor-critic

**Other algorithms**
- DQN
- MaxPressure

Some of these are off-policy and some are on-policy. Are they a good fit for the job?

**Professor's comments**
- "You are comparing methods, yes? Evaluating?"
- After I showed him 8 intersections from OSM: "get more methods, evaluate methods on 1 intersection." He said something about one method maybe excelling in one traffic situation (e.g. high saturation) and another at a different time of day. *I'm not sure about this; it seems a bit easy, and I might be misunderstanding him.*
- "Then test on another intersection." *I'm not sure why I'd use 1 as the main site; it feels like that would limit the findings.*
- If I find an anomaly (e.g. a scenario where some simulation factor affects performance): "investigate the reason, for example because of pedestrians, and find a way to patch it."
- On methods: I can stick to linear methods or not, but whatever I choose I must justify it.
- I asked whether it's fine to keep using the real timing data even though simple Webster timing beats it. He said "yes, that's fine."

**Template still to fill:** background · goal · hypothesis · research questions · proposed approach

---

## Part B: discussion

### 1. What the professor is describing

He is describing a **primary site plus replication sites** design. The study is a comparison of existing methods. That counts as a real contribution: [[nguyen2025-trex]] and [[song2026-capacity-region-corridor]] are both papers whose contribution is a comparison, not a new algorithm.

**Why one intersection as the main site.** At one site the geometry is fixed, so the only thing that changes between test hours is demand. Any change in which method wins can then be put down to traffic conditions. *(synthesis)*

Spreading the effort across 8 intersections with a few days each would confound two things. If a method wins at site 3, I couldn't tell whether that was because of the geometry or because of that day's traffic. *(synthesis)*

So the two parts answer different questions:
- The main site answers **when** each method wins.
- The other sites answer **whether that answer holds elsewhere**.

**Why "this method wins at high saturation, that one at a certain time of day" is not trivial.**
- Every paper in the wiki uses a single demand file or 2–3 made-up demand levels.
- None of them tests on days it didn't train on [[experimental-setup-across-papers]].
- With about 60 days × 18 h ≈ 1,000 real hours of demand at one site, I can map winners against *measured* conditions instead of hand-picked scenarios. Those conditions are degree of saturation, variation within the hour, and left-turn share. *(synthesis)*

The work is in doing this rigorously: building a credible simulation, running every controller on the same traffic, and doing the statistics. That is a thesis.

### 2. Answers to my two questions

**Q1. Retrain the weights for each intersection? Yes.**
- Per-site training is the norm. Kwesiga trains one agent per intersection [[kwesiga2025-mappo-north-ave]].
- A linear weight matrix is tied to that site's lanes and phases. Sahachaiseree's 160 weights are 20 features × 8 stages [[sahachaiseree2025-linear-fa-tsc]]. A site with a different layout needs a matrix of a different shape.
- What carries across sites is the **method**: the same features, reward, action space and hyperparameters, retrained on local data.
- The non-learning baselines are also set up per site:
  - Webster recomputed from local volumes
  - actuated settings
  - MaxPressure on local queues

Making the *trained policy itself* transfer is a different research question. It would need features defined per phase rather than per lane, as in [[schmidt2024-transferlight]] and [[gu2026-pi-elight]]. I'll keep that as optional future work.

**Q2. How many days for training?** Split by **day**, not by hour:

```
days  1–40 → train       (40 days × 18 h = 720 one-hour demand episodes)
days 41–50 → validation  (pick checkpoints / the seed I'd deploy)
days 51–60 → test        (touch once)
```

- **Order the split in time.** Training on history and running on the following weeks mimics real deployment, and it gives a free check for drift over time.
- **Check that weekdays and weekends are balanced** across train, validation and test.
- **720 episodes is plenty.** In Sahachaiseree's setup, linear LSTDQ converged in 10–50 episodes. Gradient methods needed 2,000–4,000 [[sahachaiseree2025-linear-fa-tsc]]. DQN will cycle through the training days many times, which is fine.
- **Optional extra:** train on 1, 3, 7, 14 and 40 days and plot test performance against that. "How much detector history does each method need?" is a practical question for an agency that already has ATSPM data.
- **Replication sites need only 2–3 weeks each**, e.g. 10 train / 4 test days.

### 3. The algorithms: does mixing on- and off-policy methods matter?

> Everything in this section except the Sahachaiseree and Kwesiga claims is general RL theory, not from the wiki.

**A category correction first.** LSPE(λ) and linear TD(λ) are **policy evaluation** methods. They score a fixed policy and do not choose actions on their own. They only become controllers inside policy iteration, or as the critic in an actor-critic.

So I'll drop LSPE as a separate controller and use TD(λ) as the critic inside the linear actor-critic.

**On vs off-policy is not a problem in simulation**, because every method can interact with the simulator freely. The difference shows up here:

| Issue | Off-policy (LSPI/LSTDQ, DQN) | On-policy (SARSA, actor-critic) |
|---|---|---|
| Reusing data | Reuses past samples, so needs less simulation | Throws data away after each update |
| Learning from logs of the field controller | Possible in principle. But fixed-time logs never show the alternative actions, so they can't replace simulation. | Not possible |
| Stability with function approximation | Off-policy learning plus bootstrapping plus function approximation can make learning diverge. LSTDQ solves for the weights in closed form, but the policy it produces can oscillate between versions. | Linear SARSA can wobble but doesn't blow up |
| Safety while learning online | Learns the greedy policy and ignores the cost of its own exploration | Accounts for its own exploration, so learns more cautiously |

**What makes the line-up defensible:** each pair of controllers isolates one design choice.

| Controller | Role / contrast |
|---|---|
| **LSPI (LSTDQ)** | Linear, batch, off-policy |
| **Linear SARSA(λ)** | vs LSPI: batch off-policy vs incremental on-policy |
| **Linear actor-critic (TD(λ) critic)** | vs SARSA: value-based vs policy-based. Drop this first if time is short. Sahachaiseree's literature review cites a failed linear actor-critic attempt (Cai 2025) [[sahachaiseree2025-linear-fa-tsc]]. |
| **DQN** | vs LSPI: same Q-learning family, linear vs neural network. This tests whether linear is enough. |
| Field plan | The status quo |
| Webster, re-timed by time of day | A re-tuned conventional plan |
| **Actuated (gap-out, NEMA)** | The real competitor. Georgia signals run this. In Sahachaiseree's tests, learned control beat gap-out control only at the highest demand [[sahachaiseree2025-linear-fa-tsc]]. |
| MaxPressure | An adaptive rule with no learning |

**Actuated control was missing from my list. Add it.**

**Justifying a mostly-linear line-up** (the professor asked for a justification):
- Engineers can read the weights directly [[sahachaiseree2025-linear-fa-tsc]].
- LSTDQ converged 40–100× faster than gradient methods [[sahachaiseree2025-linear-fa-tsc]]. That matters when the experiment multiplies sites × seeds × days.
- LSTDQ has almost no hyperparameters to tune [[sahachaiseree2025-linear-fa-tsc]].
- "Is linear enough on real demand?" is an open question. It has only been tested on one synthetic intersection [[interpretable-rl-tsc]].
- Including DQN turns "linear is enough" into a claim I test rather than assume.

**Fairness controls.** Every learner gets the same:
- state features (realistic detector inputs: stop-bar plus advance loops)
- reward
- decision interval
- action space

Keep the action space small, e.g. extend the current phase or move to the next one in the NEMA sequence, with field minimum greens, clearances and pedestrian times. There are two reasons:
- A linear Q-function has one weight vector per action, so more actions means more weights.
- More phases cost training time. Kwesiga's 8-phase agent needed 1,000+ episodes versus about 300 for 4-phase ones [[kwesiga2025-mappo-north-ave]], [[nema-dual-ring-action-space]].

### 4. Why the real timing does worse than Webster

The professor is right that this is fine, and it is expected. The parsed plan for signal 7065 (from `tools-timing/timing-data/7065/plans_7065.md`) is **coordinated, with a 159.8 s cycle and P2/P6 as the coordinated phases**.

- **The field cycle serves corridor progression, not this intersection's own delay.** A long cycle costs extra delay when the intersection is judged alone. *(inferred)*
- **The simulation counts the cost of coordination but none of its benefit.** Coordination pays off when vehicles arrive in platoons from the upstream signal. Random (Poisson) arrivals at an isolated intersection remove those platoons. *(inferred)*

This is the objective confound described in [[baseline-selection]]. Use it rather than hide it:
- **Field plan → Webster = the gain from re-tuning.**
- **Webster → actuated / MaxPressure / RL = the gain from adapting to traffic.**

[[baseline-selection]] notes that no wiki paper separates these two gains, so the split is a small contribution in itself.

**To check:** simulate the field plan with actuated logic, where the non-coordinated phases gap out. Simulating it as fixed splits would understate it further.

---

## Part C: draft for the template

### Background
- RL signal control is usually evaluated on one demand file, trained and tested on the same traffic, with no repeated runs or significance tests [[han2023-rl-traffic-survey]], [[experimental-setup-across-papers]].
- Reported gains depend heavily on how strong the baseline is. Against real production timing, MA-PPO tied the field plan in the coordinated direction (about 2%) and gained about 24% only in the direction the plan deprioritised [[kwesiga2025-mappo-north-ave]], [[baseline-selection]].
- Linear methods that engineers can interpret are promising, but have only been shown on synthetic demand at a single intersection [[sahachaiseree2025-linear-fa-tsc]].
- **The gap:** no study compares conventional, linear and deep controllers on many days of real demand, tested on held-out days, with results broken down by traffic condition. *(synthesis)*

### Goal
Find out which signal control methods perform best under which real traffic conditions at a real Atlanta intersection, and whether those findings carry over to intersections of a different type.

### Research questions
- **RQ1.** On held-out days at one real intersection, how do the controllers compare?
  - Conventional: field plan, Webster, actuated, MaxPressure.
  - Learned: the linear family and DQN.

  How does their ranking depend on degree of saturation, variation within the hour, and time of day?
- **RQ2.** Does a neural network beat linear methods at an isolated intersection? Judge this on four criteria: delay on held-out days, training cost, consistency across seeds, and interpretability.
- **RQ3.** After retraining at each site, do the RQ1 and RQ2 findings hold at intersections of a different type? Where they don't, what causes it (pedestrians, number of phases, shared lanes)? Can it be fixed, e.g. with constraints via action masking or constrained RL [[safe-rl-tsc]]?
- **RQ4 (optional).** How many days of training history does each method need?

### Hypotheses
Each one is falsifiable.
- **H1. The ranking depends on traffic conditions.**
  - Compared with fixed-time control, every adaptive method gains most at low or unbalanced demand.
  - Compared with actuated control, learned controllers gain only near saturation.

  This tests, on real demand, the pattern Sahachaiseree found on synthetic demand. There, learned control went from 17.6% to 48.7% better than pretimed control as demand dropped, and beat gap-out control only at the highest demand [[sahachaiseree2025-linear-fa-tsc]].
- **H2.** Linear methods come within a pre-set margin of DQN's delay on held-out days (e.g. 5%; fix the margin in advance), at a fraction of the training cost.
- **H3.** Measured in degree of saturation, the main site's map of which method wins where predicts the rankings at other sites. Where it doesn't, the difference traces to a specific site feature.

### Proposed approach
1. **Simulation fidelity at the main site.**
   - Build the SUMO model.
   - Turn the 5-min turning-movement counts (TMCs) into arrivals.
   - Check the simulated field plan against real ATSPM phase terminations.
2. **Protocol.** Details are in [[experimental-setup-across-papers]].
   - Time-ordered 40/10/10 day split, hours 04:00–22:00 only.
   - Every controller runs on identical traffic seeds.
   - 5 training seeds per learner, with checkpoints picked on validation days.
   - 10 simulation seeds per test hour.
   - Report the mean across seeds with a confidence interval.
   - Compare methods with paired tests on each test hour.
3. **Condition analysis.**
   - Describe each test hour by degree of saturation (from Webster's Y), variability of the 5-min counts, directional imbalance and left-turn share.
   - Model each method's difference from Webster as a function of those descriptors, with day as a random effect.
4. **Replication at 2–3 sites chosen to differ as much as possible:** 3-leg vs 4-leg, number of phases, protected vs permissive lefts, pedestrian volume. Two or three carefully built networks beat eight rough ones, because hand-building SUMO networks is the bottleneck.
5. **Diagnose and fix** whatever anomalies come up.

---

## Open decisions (mine to make)
- Weekends: include them, or analyse them separately?
- Does ATSPM give pedestrian calls for my sites? Not checked yet. The pedestrian angle in RQ3 depends on it.
- Which replication sites to build.
- Where the ~60-day dataset for the main site lives. Only 2 days of signal 7065 are cached in `tools/tmc-data/7065/`.

## My notes

[Leave blank — I'll fill this in]
