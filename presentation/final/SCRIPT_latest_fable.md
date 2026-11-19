# Spoken script — midterm talk, 2026-11-19 (deck: LATEST_fable.pptx)

**Slides 1–13 spoken: 1361 words, about 9.7 min at ~140 wpm** (per-slide timings below sum to ~585 s). Slide 14 is a backup picture, not timed.

| Slide | Title | Words | ~Seconds |
|---|---|---|---|
| 1 | Title | 39 | 15 |
| 2 | Agenda | 31 | 15 |
| 3 | Background | 82 | 35 |
| 4 | Background: how a signal decides | 94 | 40 |
| 5 | Related Works | 115 | 50 |
| 6 | Study Objective | 58 | 25 |
| 7 | Proposed Approach | 98 | 40 |
| 8 | Dataset | 83 | 35 |
| 9 | Methods Compared | 111 | 50 |
| 10 | Experimental Setup | 117 | 50 |
| 11 | Results | 251 | 110 |
| 12 | Results by Condition | 114 | 50 |
| 13 | Conclusion & Future Work | 168 | 70 |

## Slide 1 — Title (~15 s)
Good afternoon. I'm Andifallih Noor Malela. My project uses reinforcement learning to control traffic signals, and tests it against the real signal timing at an intersection in Atlanta, Georgia. This is a midterm report, so the results are preliminary.

## Slide 2 — Agenda (~15 s)
Here is the plan. I'll start with the problem and related work, then our objective and approach, then the experiment design, the preliminary results, and finally the conclusion and future work.

## Slide 3 — Background (~35 s)
Traffic is growing faster than roads. In the United States, from 1980 to 2023, vehicle-miles travelled rose 114 percent, but lane-miles rose only 13 percent. In the UK, from 2010 to 2024, traffic rose 11 percent while road length grew 0.6 percent. So existing roads, especially in cities, must carry more vehicles. Intersections are where roads and traffic cross, so delay builds up there. Haydari and Yilmaz, in a 2022 survey, describe adaptive signal control as an effective solution for reducing congestion.

## Slide 4 — Background: how a signal decides (~40 s)
At every moment, a traffic signal makes one decision: keep the current green, or move to the next phase. There are three ways to make that decision. Fixed-time runs a preset schedule. Actuated uses sensors to extend or end a green. Adaptive changes its timing as traffic changes, by a designed rule or by learning from data. Learning from data is reinforcement learning, or RL. In simulations, Chen and colleagues, in 2022, found that RL beats fixed and actuated control. But it is unclear whether simple, low-cost RL does as well as deep RL.

## Slide 5 — Related Works (~50 s)
Deep RL uses neural networks. It performs strongly on complex problems: city networks, corridors, and a six-arm roundabout in Taipei (Chen, 2025). In calibrated simulations it has even beaten real field timing, as in Gong 2019 and Kwesiga 2025. But it is costly to train. Linear RL is the simpler alternative. Sahachaiseree and Oguchi (2025) train a linear controller in about ten iterations, and argue that it is easier to read. The gap is that linear and deep RL are rarely compared directly. In the studies we reviewed, Schreiber 2022 is the one comparison, and linear Q-learning came close to DQN. So it is unknown when linear is enough, and when deep RL pulls ahead.

## Slide 6 — Study Objective (~25 s)
Our goal: insight into how adaptive and learned control methods perform at an intersection calibrated to real field data. Three objectives. One: build a simulated intersection that mimics a real one. Two: train and test linear and deep RL under different traffic conditions. Three: find out how and when each method wins, and what it costs to train.

## Slide 7 — Proposed Approach (~40 s)
The approach has two parts. On the left, we build the simulation from GDOT's signal data and training-day traffic. We run GDOT's real timing in it on held-out days and compare with GDOT's own logs. If it does not pass, we find the cause, tune on training days, and check again. On the right, once it passes, the learners train on the training days. Then every method, with GDOT's plan as the baseline, is tested on locked test days. The output is delay per car. All methods get the same roads, cars and detectors; only the decision differs.

## Slide 8 — Dataset (~35 s)
Our intersection is West Paces Ferry Road at East Andrews Drive in Atlanta, signal 137, with four legs. The data come from Georgia DOT's signal system: vehicle counts per movement every five minutes, and logs of what the signal did. The road layout comes from OpenStreetMap. The main street has two lanes each way and carries roughly 60 percent of the vehicles. The side streets have three lanes each way. We use weekdays from March to May 2026, about 33,000 vehicles per weekday.

## Slide 9 — Methods Compared (~50 s)
We compare four learning methods and one baseline. Three are linear. LSTDQ is our base method: it solves a least-squares problem, in about ten training rounds. Q-learning uses the same linear model but learns step by step, so it tests whether least squares matters. SARSA is the best-backed linear method in traffic: Alegre and colleagues tested it on a real city network. For deep RL we use DQN, the most common deep method, with the same inputs, so the only difference is linear versus deep. The baseline is GDOT's real timing plan, run in the validated simulation. Today I show LSTDQ and Q-learning. SARSA and DQN were not trained in time.

## Slide 10 — Experimental Setup (~50 s)
We measure delay per car: the seconds each car loses compared with driving freely. Lower is better. Weekdays are split in three: 29 training days, to build the simulation and train the learners; 20 held-out days, to check the simulation; and 7 locked test days, for the final comparison only. Each learner is trained five times from different random starts; we report the average. We compare overall, by time of day, in sudden surges, and in a what-if with 25 percent more traffic. The statistics were planned before the final test and pair methods by day: a tie test, equal if within 2 seconds or 5 percent, and a difference test, a paired t-test with Holm correction.

## Slide 11 — Results (~110 s)
First, these results are preliminary. The simulation, LSTDQ and Q-learning are done. SARSA and DQN were not trained in time. The simulation passed its pre-set checks on 20 held-out days: green length within 3 seconds in 34 of 35 cases, and why greens end within 15 points in 28 of 35, the number we needed. That checks signal behaviour, not delay. On the 7 test days, GDOT's plan has 31.2 seconds of delay per car. LSTDQ has 25.3, and beat the plan on all 7 days. Q-learning has 30.6, and beat it on 5 of 7. Both learners cut side-street delay: under LSTDQ, side streets drop from 49.6 to 33.8 seconds, while the main street, with 58 percent of cars, goes from 18.2 to 19.2.

Why did LSTDQ beat Q-learning? Same linear model, same inputs; only how the weights are learned differs. LSTDQ collects a batch of experience and solves for all the weights at once, each round. Q-learning nudges the weights a little after every step. In our runs, LSTDQ was stable after the first round, while Q-learning's weights kept growing and its training delay rose. This matches Sahachaiseree and Oguchi, who found their LSTDQ controller stable while the same model trained by gradient descent diverged. In general RL, step-by-step Q-learning with function approximation can diverge. In plain words: solving from a batch is steadier than nudging after every step, which can overshoot and drift. One intersection, linear only; SARSA will show whether a better step-by-step learner closes the gap.

## Slide 12 — Results by Condition (~50 s)
No method wins everywhere. At night, GDOT's plan and Q-learning are about equal, 8.2 and 8.1, and LSTDQ is behind at 11.6. In the morning peak, midday and evening peak, LSTDQ is best: 21.1, 24.2 and 30.6, against the plan's 26.1, 35.0 and 34.0. Q-learning is worse than the plan in the evening: 42.2. Surges are six hours with sudden side-street surges, picked after seeing the results, so treat that row as an illustration: plan 85.4, LSTDQ 58.0, Q-learning 114.5. The last row is a what-if with 25 percent more traffic, on five held-out days: 63.1, 51.7 and 76.9. LSTDQ is lowest again, and Q-learning is worst. When traffic is heavy, Q-learning breaks down.

## Slide 13 — Conclusion & Future Work (~70 s)
Done so far: the simulation is built and passed its check, and LSTDQ and Q-learning are trained and tested against GDOT's plan. Not yet: SARSA and DQN. These findings are preliminary: one intersection, linear learners only. LSTDQ beat today's plan on all 7 test days, 25.3 against 31.2 seconds. Least-squares learning was stable; step-by-step Q-learning was not. LSTDQ cut side-street delay from 49.6 to 33.8 seconds and kept the main street about the same. Limitations: one intersection, linear learners only so far, and the simulation was checked on controller behaviour, not delay.

Future work. By November 30, we train and test SARSA and DQN. By December 19, we add a contrasting intersection: a busier, more complex one, with heavier traffic closer to capacity, and more lanes and phases. Likely Peachtree Road and Piedmont Road, signal 7065, also in Atlanta. There we can see where deep RL might pull ahead. We also plan a traffic-growth what-if at the first site. By January 20, we finish the thesis. Thank you.

## Slide 14 — Backup: model picture
(Backup, not part of the timed talk.) This is the intersection model in SUMO. The road layout comes from OpenStreetMap, and the signals run GDOT's timing. Show it if someone asks what the simulation looks like.

## Appendix slides 15–19 (only if asked)

**Slide 15.** (appendix, only if asked) What goes into the simulation. From GDOT's signal data: road layout, sensor positions, five-minute counts per movement, cycle length, minimum and maximum greens, yellow and red times, plan structure, and pedestrian button rates. We tune driver behaviour, gap time and saturation flow. The simulation passes if the average green length is within 3 seconds of the logs, and the reasons greens end (no more cars, or maximum limit hit) match the logs. It passed on the 20 held-out days: green length within 3 seconds in 34 of 35 cases, and why greens end within 15 points in 28 of 35, the number needed.

**Slide 16.** (appendix, only if asked) Three learners, the same detector inputs. LSTDQ and Q-learning learn the same linear model, but LSTDQ solves for its weights from all recorded decisions at once, while Q-learning nudges them after every decision. ARS tries random changes and keeps those that lower delay. LSTDQ: 25.3 s all day, against about 30.5 for the other two, and 31.1 in busy hours against about 41 to 42. Q-learning and ARS are better at night. LSTDQ settles after one round, Q-learning drifts if it keeps training, and ARS stays noisy even with about ten times more simulation runs. ARS is not part of the main story.

**Slide 17.** (appendix, only if asked) Full test-day comparison with the statistical values: paired by day, tie test with margin 2 s or 5 percent, and paired t-test on the daily log ratio with Holm correction. This table also includes the extra controllers (the no-cycle actuated controller, MaxPressure and Webster) that are not part of the main story. MaxPressure gives green to the longest queue (Varaiya 2013). Webster is a textbook fixed timer (Webster 1958), built for a typical day.

**Slide 18.** (appendix, only if asked) Full by-condition table with all adaptive methods and the real plan, including the extra controllers that are not in the main story. Surges are six hours picked after seeing the results, and the +25 percent row is a what-if on five held-out days, so these rows are descriptive.

**Slide 19.** (appendix, only if asked) Main-street and side-street delay for every method on the test days. Likely reasons the learners favour the main street, not yet tested: they are rewarded per car and most cars are on the main street, and side streets only have stop-line detectors.

## Likely questions

**Q1. Why linear RL?**  
It trains fast, about ten rounds for LSTDQ, it is simple, and Sahachaiseree and Oguchi argue it is easier to read than deep RL. The open question, in the studies we reviewed, is when linear is enough and when deep RL pulls ahead. DQN, which has the same inputs, is planned to test exactly that.

**Q2. Why these methods, and why not PPO?**  
Each one answers a question. LSTDQ is the base method, Q-learning tests whether least squares matters, SARSA is the linear method with the best track record in traffic, and DQN is the deep counterpart with the same inputs. PPO-type methods need far more training: in the RESCO benchmark, IPPO and FMA2C needed about 1,400 episodes against about 100 for IDQN. DQN is the closer counterpart to our linear Q-learning.

**Q3. How do you know the simulation is right?**  
We set the checks before we looked, and ran GDOT's real timing on 20 held-out days. Average green length was within 3 seconds in 34 of 35 cases, and why greens end was within 15 points in 28 of 35, which was the number needed. That checks controller behaviour. It does not prove delay is right, so a delay check is the next step. I would not say the simulation matches reality, only that it passed these checks.

**Q4. Why only one intersection?**  
Building and checking the simulation took several attempts, and we wanted one fully checked site first. This is a midterm: the results are preliminary and hold for this intersection. The plan is to add a contrasting, busier intersection by December 19, to see whether they hold there and where deep RL might pull ahead.

**Q5. Did you check delay in the simulation?**  
Not yet. The check so far is on controller behaviour: how long greens are, and why they end. Comparing simulated delay with a measured delay is a limitation and a next step.

**Q6. What is a seed? Why five runs?**  
A seed is the random starting point of a training run. A learner can come out differently each time, so we train each one five times and report the average, rather than trust one lucky or unlucky run.

**Q7. Why did LSTDQ beat Q-learning?**  
They use the same linear model and the same inputs. Only how the weights are learned differs. LSTDQ solves for the weights from a batch of experience in one least-squares step each round, which is a steady approximate policy iteration (Lagoudakis and Parr 2003). Q-learning nudges the weights after every step. In our runs LSTDQ was stable after the first round, while Q-learning's weights kept growing, roughly 27 to 182, and its training delay rose. Sahachaiseree and Oguchi saw the same thing: LSTDQ was stable, and the same linear model trained by gradient descent diverged. In general RL, step-by-step Q-learning with function approximation can diverge; that is general knowledge, not from our papers. Caveats: one intersection, linear only. SARSA, which is also step by step, will show whether a better step-by-step learner closes the gap.

**Q8. Why does Q-learning do badly in heavy traffic?**  
We have not tested the cause. The pattern fits the drift we saw in its weights: the best Q-learning version was an early training round, picked on training days, and it does worse when traffic is far from what it learned on. This is a hypothesis, not a result.
