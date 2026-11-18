# Midterm script (deck v4)

Spoken length: 1192 words, about 9:10 at a calm 130 words a minute, about 8:50 at 135.
Backup slides (16–21) are only for questions.

---

## Slide 1 — Title (~10 s, 0:10)

Good afternoon. I compare traffic signal controllers at one real intersection in Atlanta, in a simulation built only from the state transport agency's own data.

## Slide 2 — Agenda (~5 s, 0:15)

Problem, approach, results.

## Slide 3 — Problem: Promising in Papers, Rare on the Street (~45 s, 1:00)

On the street today, engineers set timing plans, and detectors stretch or end a green when cars are there.

Research promises more. A 2025 review counted 470 papers on learned signal control, called reinforcement learning, since 2015. Reviews report clear gains over fixed and detector-based control, in simulation.

But it rarely reaches the street. A 2022 review found no learned controller had been deployed. A 2025 paper still calls field use rare.

So the problem is this: an agency cannot tell from published results whether a learned controller would beat what it already runs, at its own intersection, with its own traffic.

*Point at:* the box at the bottom.

## Slide 4 — Why the Evidence Falls Short (~65 s, 2:05)

In the studies we reviewed, I see four reasons.

One: is the test realistic? Most studies use made-up road networks. The three real-road studies we read build their simulation from real data, but none reports checking it against the real road. And they test on the same data.

Two: better than what is installed? Mostly the comparison is a weak baseline. Meess and colleagues write that tests against engineer-tuned controllers are rarely carried out.

Three: when does it pay off? Three papers give three different answers. And in a real field test of an adaptive system, the gain depended on the time of day.

Four: better for whom? Results are one average over all cars. A 2025 review lists fairness, who waits, as an open problem.

Our base method is the linear learner of Sahachaiseree and Oguchi.

## Slide 5 — Research Objective (~45 s, 2:50)

Our goal is the field problem: give agencies evidence on when, and why, learned control pays off over the control already on the street.

This study is one step: one intersection, one simulation.

Three objectives. One: build the simulation and check it against the real controller's log, on days we did not tune it on. Two: rank the controllers on real days we held back. Three: explain each win or loss, and who ends up waiting.

Before any result, we wrote down what we expected: in normal traffic, the methods that react to traffic would all do about equally well.

## Slide 6 — Proposed Approach (~30 s, 3:15)

Left: every input comes from the agency's signal data portal. Five-minute counts, the real timing plans, and where the detectors are.

Middle: the simulation runs a loop every second. Cars drive, detectors see them, and the controller decides one thing: extend this green, or end it. A rule engine then enforces the safety rules: minimum green, yellow, red, and pedestrian time.

*Point at:* the "Controller" box.

## Slide 7 — Dataset (~25 s, 3:40)

The intersection is West Paces Ferry Road at East Andrews Drive, in Atlanta: signal 137. The next signal, 138, is 260 metres east, and runs its real timing.

We use weekdays from March to May 2026: 29 days to train, 20 to develop, and the last 7 held back as the test.

## Slide 8 — Calibration & Validation (~60 s, 4:40)

Everything we tuned came from the agency's reports, on training days only.

One thing we found: the side-street counts come from detectors at the stop line. A queue leaving on green keeps the detector covered, so several cars count as one. We corrected for that.

Then the check. We run the real timing plans in the simulation on 20 days not used for tuning, and compare with the real controller's own log. The pass rules were fixed before the first run.

The green time each movement gets matches within 3 seconds in 34 of 35 cases. Why each green ended matches in 28 of 35. One thing does not match yet: how often a turn arrow is skipped, 18 of 35. We report that. It took 8 attempts.

*Point at:* the dots on the diagonal.

## Slide 9 — Methods Compared (~55 s, 5:35)

Seven controllers. Webster is the textbook fixed timer.

The GDOT plan is what runs on the street today, and the one we checked. It runs a fixed cycle, a fixed-length round of greens, shared with the next signal.

Actuated is the same controller without the fixed cycle: it keeps a green as long as cars keep arriving, and ends it at a gap. On the street, that only happens at night, and then the two give the same delay. In daytime it is our what-if, and our reference.

MaxPressure gives green to the longest queue.

Three linear learners score "extend" and "end" from the detectors, and pick the higher. They differ only in how they learn.

## Slide 10 — Experiments (~30 s, 6:05)

We measure delay: the seconds each car loses compared with driving freely. Lower is better. For cars heading west, it includes their wait at signal 138.

A tie means within 2 seconds, fixed before any result.

One honest note: we opened the test days once, then found four errors in our setup. We wrote the fixes down, reran once, and keep both results.

## Slide 11 — Results: Real Days (~45 s, 6:45)

Here is the answer on the 7 test days.

The deployed GDOT plan: 31.2 seconds of delay. The linear learner LSTDQ: 25.3. MaxPressure: 26.1. And the same controller without its fixed cycle: 24.9. All three beat the deployed plan on all 7 days.

So three methods cut delay by 5 to 6 seconds per car, and one of them does no learning at all.

Against that no-cycle controller, LSTDQ is a tie: within 2 seconds, shown statistically. Q-learning, at 30.6, and ARS, at 30.4, are not settled. The days vary too much to say.

*Point at:* the first three rows.

## Slide 12 — Results: When (~50 s, 7:35)

When does each method win?

At night, the no-cycle controller has 8.2 seconds; LSTDQ 11.6 and MaxPressure 11.2. In the morning peak, every adaptive method beats the no-cycle controller; LSTDQ is lowest, at 21.1. At midday, LSTDQ again: 24.2. In the evening peak the no-cycle controller wins: 27.8. In six hours with sudden side-street surges, which we picked out after seeing the results, it wins clearly: 39.1, against 58.0 for LSTDQ.

Bottom: a what-if on 5 development days, every count up by a quarter. The learners trained on real counts only. No-cycle controller 45.0, MaxPressure 51.3, LSTDQ 51.7.

No method wins everywhere. The simple rule is the safest default.

## Slide 13 — Main Findings: Who Waits (~45 s, 8:20)

The deployed GDOT plan favours the main street: 18 seconds there, 50 on the side streets.

LSTDQ keeps the main street at 19, and cuts the side streets to 34.

The no-cycle controller shares the wait evenly: 25 on both.

So LSTDQ and the no-cycle controller have about the same average, but different people wait.

Why? Our likely explanation, not yet tested: the learners are rewarded per car, and most cars are on the main street. And the side streets only have detectors at the stop line, so a long side queue is mostly invisible.

*Point at:* the red side-street bars.

## Slide 14 — Conclusion (~35 s, 8:55)

For this one intersection:

One. The simulation, built only from the agency's data, passed its check on unseen days. It checks how the controller behaves, not delay itself.

Two. The gain over today's timing needs no learning. We expected the learning methods to at least match the best simple rule. Only LSTDQ clearly did.

Three. Learning changes who waits.

Whether methods split apart near capacity, we cannot test on real days here. This intersection is rarely that busy.

## Slide 15 — Future Work (~15 s, 9:10)

Next: test whether the ranking survives errors in the counts. Check the simulation on the test days. Test why the side streets wait. And train on heavier traffic.

Thank you.

---

## Backup slides (only if asked)

**16 — Validation attempts.** Eight attempts. Each fix came from training-day data, never from the check itself, and the pass rules never changed.

**17 — Detector undercount.** A queue leaving on green keeps the stop-line detector covered, so several cars count as one. We estimate the cars from how long the detector stays covered, about 1.9 seconds per car.

**18 — Prior simulations.** In the studies we reviewed, none reports a check against the real road, and none tests on held-back days. The Georgia Tech study uses the real controller software, which is stronger than our own engine.

**19 — Inputs not from GDOT.** Road layout from OpenStreetMap, standard driver behaviour, and a few assumed detector and pedestrian settings. All are listed here.

**20 — Test run and rerun.** First run: LSTDQ 30.6, no-cycle controller 25.2. After the four registered fixes: 25.3 and 24.9. Both are reported.

**21 — How the learner decides.** It scores "extend" and "end" from detector features every second, and learns its scores offline from recorded training days.

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
