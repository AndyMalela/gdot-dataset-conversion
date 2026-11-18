# Midterm script (deck v10)

Spoken length: about 1582 words: ~11:43 at 135 words a minute, ~11:18 at 140, counting only one of the two objective slides (6 or 7). These are the speaker notes in eSocLab_Midterm-v10.pptx.

---

## Slide 1 — Title (~10 s)

Good afternoon. This study is titled Reinforcement Learning Control for Field Calibrated Controller. This mainly deals with traffic control, mainly at intersections

## Slide 2 — Agenda (~10 s)

This is the agenda for the presentation. I will go from the problem, to the approach, to the results and finish it with conclusion.

## Slide 3 — Problem Formulation (~30 s)

A traffic signal does one job: every second, keep the current green, or switch.

Signal control comes in three types. Fixed-time runs a preset schedule, whatever the traffic. Actuated uses detectors to stretch or end each green; that is what runs at our intersection. Adaptive changes the timing itself as traffic changes. Some adaptive controllers follow a designed rule. Others learn their rule from data: that is learned control, or reinforcement learning.

## Slide 4 — Problem Formulation (~30 s)

Learned control looks promising in papers: hundreds of studies report large gains, in simulation. But it rarely reaches the street. One main problem is agencies must be able to audit a controller against signal standards first, and that is still a barrier for learned control.

So an agency cannot tell whether a learned controller would beat what it already runs, by how much, and under what conditions.

## Slide 5 — Related Works (~165 s)

Slide 5: Related Works
1 Rarely compared against the real controller, and that controller's copy never checked*
Tests against engineer-tuned actuated control "are rarely carried out" (Meess 2024)
The two that do (Kwesiga 2025, Meess 2024) test only their own method, and don't check their simulated controller against what the real one did (how long each green lasted, why it ended)
2 Studies disagree on when learned control pays off, and mostly vary only traffic volume
Linear RL vs actuated: gain shrinks as traffic grows (Sahachaiseree & Oguchi 2025)
Table-based RL vs fixed / actuated: gain grows (El-Tantawy 2014)
Linear RL vs rule-based adaptive: no change (Alegre 2022)
3 Most studies use deep RL; linear RL is rarely evaluated
Deep RL can be costly to compute, and field controllers may run old hardware (Chen 2022)
Linear RL is argued to be easier to inspect and quick to train (Sahachaiseree & Oguchi 2025)
Footer: * in the studies we reviewed
Optional tags: 1 → O1 + O2, 2 → O2, 3 → O2.
Script (~55 s):
In the studies we reviewed, I see three gaps.
One: learned control is rarely tested against the controller that is actually installed. As Meess and colleagues put it, these tests "are rarely carried out". The two we found that do it test only their own method. And neither shows that their simulated copy of the real controller behaves like the real one. A real controller keeps its own records: how long each green lasted, and why it ended. Neither study compares against those records.
Two: studies disagree on when learned control pays off. One finds the gain shrinks as traffic grows, one finds it grows, one finds no change. But they used different methods against different baselines, and mostly varied only the amount of traffic.
Three: most studies use deep neural networks. A review notes that this can be costly to compute, and that field controllers often run old hardware. Linear learners are argued to be easier to inspect and quicker to train, but they are rarely evaluated on real traffic.
So we compare several methods, linear learners included, side by side, against GDOT's real plan, in a simulation where we checked that plan's copy against GDOT's own records.

## Slide 6 — Study Objective (~55 s)

Our goal: evaluate signal control methods against each other, and against the controller GDOT actually runs, on real traffic.

Three objectives, at one intersection. One: build a simulation that behaves like the real intersection, and check it against GDOT's own log on days we did not tune it on. Two: compare the methods on real days we held back, overall and by time of day, how busy the hour is, and sudden surges. Three: interpret how each method wins or loses, and who ends up waiting, and check that it holds.

Before any result, we wrote down what we expected: in normal traffic, the methods that react to traffic would all do about equally well; near capacity, they would pull apart.

## Slide 7 — Study Objective v2 (~50 s)

[Alternative to the previous slide: use one of the two.] Our goal is the field problem: give agencies evidence on when, and why, adaptive and learned control pays off over the control already deployed, on real traffic.

Three objectives, at one intersection. One: simulate and calibrate the intersection from GDOT's logged data, and check it on days we did not tune it on. Two: compare each method's performance, by time of day, how busy the hour is, and sudden surges. Three: interpret how each method wins or loses, and who ends up waiting, and check that it holds.

Before any result, we wrote down what we expected: in normal traffic, the methods that react to traffic would all do about equally well; near capacity, they would pull apart.

## Slide 8 — Proposed Approach (~45 s)

The system in four steps. One: data - everything comes from GDOT's own signal data. Two: a simulation of the intersection and the next signal. Before we use it, we check it: we run GDOT's real timing in it on 20 days we did not tune on, and compare with GDOT's own log. If it fails, we find the cause, fix it and check again. Three: we train the learners on training days only, and run all seven methods. Four: results - delay per vehicle on 7 held-back test days. Every method gets the same roads, cars and detectors; only the decision differs.

## Slide 9 — Calibration & Validation (~75 s)

First question: does our simulation behave like the real intersection?

To build it, we used only 29 past weekdays. We fed it how many cars came every five minutes, in each direction; GDOT's real timing schedules; and where the detectors sit. One surprise: on the side streets, a whole queue of cars leaving on green was counted as one car, so we corrected those counts.

Then we checked it on 20 other days it had never seen. We gave it the same real timing and each day's real car counts, and compared it with the signal's own records of what it actually did. How long did each green light last? In 34 of 35 cases, within 3 seconds, about one and a half cars. Why did each green end: because cars stopped coming, or because its time ran out? 28 of 35 match. To pass, we needed 28 of 35, a rule we set before the first try.

One limit: this checks what the signal does, not how long the cars wait.

[If asked: the 3-second and 28-of-35 thresholds are a judgement call fixed before the first run. 3 seconds is about one and a half cars. The same idea, a share of cases within a tolerance, is in the FHWA guide, which uses 85% for traffic counts.]

## Slide 10 — Methods Compared (~60 s)

Seven controllers, in the same types as before.

Fixed-time: Webster, the textbook timer.

Actuated: the GDOT plan, what runs on the street today, and the one we checked. Its greens follow the detectors, but inside a fixed cycle: a fixed-length round of greens, shared with the next signal. Our second actuated controller is the same one without the fixed cycle. On the street that only happens at night, and then the two give the same delay. In daytime it is our what-if, and our reference.

Adaptive, with a designed rule: MaxPressure gives green to the longest queue. Adaptive, learned from data: three linear learners score "extend" and "end" from the detectors, and pick the higher. They differ only in how they learn. LSTDQ is our base method. Sahachaiseree and Oguchi argue linear learners are easier to inspect.

[Point at: the four column headings: the same types as slide 3.]

## Slide 11 — Dataset (~25 s)

The intersection is West Paces Ferry Road at East Andrews Drive, in Atlanta: signal 137. The next signal, 138, is 260 metres east, and runs its real timing.

We use weekdays from March to May 2026: 29 days to train, 20 to develop, and the last 7 held back as the test.

## Slide 12 — Experiments (~30 s)

We measure delay: the seconds each car loses compared with driving freely. Lower is better. For cars heading west, it includes their wait at signal 138.

A tie means within 2 seconds, fixed before any result.

One honest note: we opened the test days once, then found four errors in our setup. We wrote the fixes down, reran once, and keep both results.

## Slide 13 — Results: Real Days (~35 s)

On the 7 test days, the deployed GDOT plan has 31.2 seconds of delay. LSTDQ: 25.3. MaxPressure: 26.1. And the same controller without its fixed cycle: 24.9. All three beat the deployed plan on all 7 days.

So three methods cut delay by 5 to 6 seconds per car, and one of them does no learning at all.

Against that no-cycle controller, LSTDQ is a tie: within 2 seconds, shown statistically. Q-learning, at 30.6, and ARS, at 30.4, are not settled.

[Point at: the first three rows.]

## Slide 14 — Results: When (~40 s)

In the morning peak, every adaptive method beats the no-cycle controller; LSTDQ is lowest, at 21.1. At midday, LSTDQ again: 24.2. In the evening peak the no-cycle controller wins: 27.8. In six hours with sudden side-street surges, which we picked out after seeing the results, it wins clearly: 39.1, against 58.0 for LSTDQ.

Bottom: a what-if on 5 development days, every count up by a quarter. The learners trained on real counts only. No-cycle controller 45.0, MaxPressure 51.3, LSTDQ 51.7.

No method wins everywhere. The simple rule is the safest default.

## Slide 15 — Main Findings: Who Waits (~40 s)

The deployed GDOT plan favours the main street: 18 seconds there, 50 on the side streets.

LSTDQ keeps the main street at 19, and cuts the side streets to 34.

The no-cycle controller shares the wait evenly: 25 on both.

So LSTDQ and the no-cycle controller have about the same average, but different people wait.

Why? Our likely explanation, not yet tested: the learners are rewarded per car, and most cars are on the main street. And the side streets only have detectors at the stop line, so a long side queue is mostly invisible.

[Point at: the red side-street bars.]

## Slide 16 — Conclusion (~35 s)

For this one intersection:

One. The simulation, built only from the agency's data, passed its check on unseen days. It checks how the controller behaves, not delay itself.

Two. The gain over today's timing needs no learning. We expected the learning methods to at least match the best simple rule. Only LSTDQ clearly did.

Three. Learning changes who waits.

Whether methods split apart near capacity, we cannot test on real days here. This intersection is rarely that busy.

## Slide 17 — Future Work (~15 s)

Next: test whether the ranking survives errors in the counts. Check the simulation on the test days. Test why the side streets wait. And train on heavier traffic.

Thank you.

---

## Backup slides (only if asked)

**18 — Backup: Validation Attempts.** (backup, 0 s) Only if asked. Each change was justified by train-day GDOT data and registered before the run; the pass rules never changed. The rules, why these numbers, the limits and which report gives what are on the next backup slide.

**19 — Backup: Validation Rules and Limits.** (backup, 0 s) Only if asked. The pass rules were written before the first attempt and never changed. The thresholds are a judgement call: 3 seconds is about one and a half cars; the FHWA guide uses the same idea, a share of cases within a tolerance. Two limits: turn-arrow skips do not match yet, and the gap times were tuned to the same measure on training days.

**20 — Backup: Detector Undercount.** (backup, 0 s) Only if asked. Found while diagnosing short side-street greens in validation (137); first seen at 7065 by comparing flows with neighbouring signals.

**21 — Backup: Prior Simulations.** (backup, 0 s) Only if asked. Fair contrast: they calibrate or build the simulation and evaluate on the same data; none reports checking it against field observations. Kwesiga's controller fidelity (real MaxTime software) and drone-based driver calibration are stronger than ours.

**22 — Backup: Inputs Not From GDOT.** (backup, 0 s) Only if asked. Disclosed assumptions.

**23 — Backup: Test Run and Rerun.** (backup, 0 s) Only if asked. The test days were opened once under the registered plan. After that run an independent review found four errors; the fixes were written down before the rerun and justified by signal-controller rules, a scoring error and train-day measurements, not by the test results. Both results are reported. The rerun is a second look at the same days, so it is not a clean held-out test; fresh days are needed to confirm the tie.

---

## Likely questions

**You reran the test after seeing it. Isn't the tie tuned to the test?**
Partly a fair worry. In the first run LSTDQ had 30.6 seconds against 25.2. The four fixes were written down before the rerun, and came from controller rules and training-day data, not from test results. Both results are reported. Fresh days are needed to confirm the tie.

**Isn't dropping the fixed cycle unfair to GDOT? It is shared with the next signal for a reason.**
Yes, the shared cycle helps traffic flow along the road. We count only cars at this intersection, plus the westbound wait at signal 138. So we only claim the local cost here, about 6 seconds per car: 31.2 against 24.9. We do not claim the plan is bad for the whole road.

**Your check covers signal timing, not delay. Is the 50-second side-street delay real?**
Not shown directly. All methods run in the same simulation, so the comparison is fair. Checking delay itself against the agency's reports is a next step.

**Why does LSTDQ lose at night?**
At night it has 11.6 seconds against 8.2. In quiet hours it runs long cycles, 108 to 146 seconds against 91, and often holds side-street greens to their maximum. Q-learning uses the same inputs and gets 8.1. So the inputs are not the problem. The likely cause is its learned weights. Not tested yet.

**Why linear and not deep learning?**
Sahachaiseree and Oguchi argue linear learners are fast to train and easy to read. We test that family first. A deep learner is planned as a reference, so we do not claim linear is enough.

**Isn't this what the Georgia Tech paper did, also in Atlanta?**
Kwesiga and colleagues also beat the deployed timing. They report travel time 2 percent better in the main direction, 24 percent in the other, and lower side-street delay. Their setup is stronger in two ways: real controller software, and a stretch of road with 7 signals. But they used one afternoon, tested on that same afternoon, and had no no-cycle controller. That controller is what shows the gain here needs no learning.
