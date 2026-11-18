# Midterm script (final deck: eSocLab_MidtermTHISONE.pptx)

Spoken length (bracketed parts not read aloud): about 2062 words: ~15:16 at 135 words a minute, ~14:44 at 140, counting slide 6 or 7, not both. These are the deck's speaker notes.

---

## Slide 1 — Reinforcement Learning Control for Field-Calibrated Traffic (~10 s)

Good afternoon. This study is titled Reinforcement Learning Control for Field Calibrated Controller. This mainly deals with traffic control, mainly at intersections

## Slide 2 — Agenda (~10 s)

This is the agenda for the presentation. I will go from the problem, to the approach, to the results and finish it with conclusion.

## Slide 3 — Problem Formulation (~30 s)

A traffic signal does one job: every second, keep the current green, or switch.

Signal control comes in three types. Fixed-time runs a preset schedule, whatever the traffic. Actuated uses detectors to stretch or end each green; that is what runs at our intersection. Adaptive changes the timing itself as traffic changes. Some adaptive controllers follow a designed rule. Others learn their rule from data: that is learned control, or reinforcement learning.

## Slide 4 — Problem Formulation (~30 s)

Learned control looks promising in papers: hundreds of studies report large gains, in simulation. But it rarely reaches the street. One main problem is agencies must be able to audit a controller against signal standards first, and that is still a barrier for learned control.

So an agency cannot tell whether a learned controller would beat what it already runs, by how much, and under what conditions.

## Slide 5 — Related Works (~75 s)

In the studies we reviewed, I see three gaps.

One: learned control is rarely tested against the controller that is actually installed. As Meess and colleagues put it, these tests "are rarely carried out". The two we found that do it test only their own method, and neither shows that their simulated copy of the real controller matches the real one's own records: how long each green lasted, and why it ended.

Two: studies disagree on when learned control pays off. One finds the gain shrinks as traffic grows, one finds it grows, one finds no change. But they used different methods against different baselines, and mostly varied only the amount of traffic.

Three: most studies use deep neural networks, which can be costly to compute on old field hardware. Linear learners are argued to be easier to inspect and quicker to train, but they are rarely evaluated on real traffic.

So we compare several methods side by side, against GDOT's real plan, in a simulation checked against GDOT's own records.

## Slide 6 — Study Objective (~65 s)

(by what the controller does and who waits; check it across training runs, worst-served movement, count errors delete this comment later, and by using more intersections)


(~40 s) Our goal: evaluate signal control methods against each other, and against the controller GDOT actually runs, on real traffic.

Three objectives, at one intersection. One: build a simulation that behaves like the real intersection, and check it against GDOT's own log on days we did not tune it on. Two: compare the methods on real days we held back, overall and by time of day, how busy the hour is, and sudden surges. Three: interpret how each method wins or loses, and who ends up waiting, and check that it holds.

Before any result, we wrote down what we expected: in normal traffic, the methods that react to traffic would all do about equally well; near capacity, they would pull apart.

## Slide 7 — Study Objective (~65 s)

(by what the controller does and who waits; check it across training runs, worst-served movement, count errors delete this comment later, and by using more intersections)


(~40 s) Our goal: evaluate signal control methods against each other, and against the controller GDOT actually runs, on real traffic.

Three objectives, at one intersection. One: build a simulation that behaves like the real intersection, and check it against GDOT's own log on days we did not tune it on. Two: compare the methods on real days we held back, overall and by time of day, how busy the hour is, and sudden surges. Three: interpret how each method wins or loses, and who ends up waiting, and check that it holds.

Before any result, we wrote down what we expected: in normal traffic, the methods that react to traffic would all do about equally well; near capacity, they would pull apart.

## Slide 8 — Proposed Approach (~45 s)

The system in four steps. One: data - everything comes from GDOT's own signal data. Two: a simulation of the intersection and the next signal. Before we use it, we check it: we run GDOT's real timing in it on 20 days we did not tune on, and compare with GDOT's own log. If it fails, we find the cause, fix it and check again. Three: we train the learners on training days only, and run all seven methods. Four: results - delay per vehicle on 7 held-back test days. Every method gets the same roads, cars and detectors; only the decision differs.

## Slide 9 — Methods Compared (~100 s)

Seven controllers, in the same types as before, and each one answers a question.

Fixed-time: Webster, the textbook timer. It is the kind of simple baseline most papers compare against.

Actuated: the GDOT plan, which is what runs on the street today, and the one we checked. Its greens follow the detectors, but inside a fixed cycle shared with the next signal. Our second actuated controller is the same one without the fixed cycle. It separates two things: how much of a gain comes from dropping the fixed cycle, and how much from learning. It is our reference.

Adaptive, with a designed rule: MaxPressure, which gives green to the longest queue. It is the most common rule-based baseline in the studies we reviewed, so it tells us whether a learned rule beats a designed one.

Adaptive, learned from data: three linear learners. They see the same detector inputs and use the same kind of model; they differ only in how they learn. LSTDQ is our base method, from Sahachaiseree and Oguchi, who argue linear learners are easier to inspect. In the same paper they compare it with Q-learning, which learns step by step; we include it to see whether the learning method matters. ARS is our addition: a third way to learn the same kind of rule, by trial and error.

[Point at: the four group headings, then the three learners.]

[Not read aloud - if asked:
Why linear, not deep RL? Deployment: agencies must be able to check a controller against standards (Chen et al. 2022), and deep RL can be costly to compute on old field hardware. Sahachaiseree and Oguchi argue linear is easier to inspect and LSTDQ converged in about 10 learning iterations. A deep learner as a reference is planned, so we do not claim linear is enough.
Why these three learners? One per way of learning the same linear rule: solve from all data at once (LSTDQ), step by step (Q-learning), or search the rule directly (ARS). Same inputs, same model, so any difference comes from the learning method.
Why not SARSA? It is in the same family as Q-learning: both learn step by step; the difference is only which next action they learn from. Q-learning already covers that way of learning, so we expect similar behaviour. Linear SARSA(lambda), as in Alegre et al. 2022, would be a small extension, not a new kind of method.
Is ARS from a traffic paper? No: Mania et al. 2018, general reinforcement learning. We added it to cover direct policy search.
Sources: Webster 1958; MaxPressure, Varaiya 2013; LSTDQ, Lagoudakis & Parr 2003, applied to signals by Sahachaiseree & Oguchi 2025; Q-learning, Watkins 1989; ARS, Mania et al. 2018.]

## Slide 10 — Sim Calibration & Validation (~75 s)

First question: does our simulation behave like the real intersection?

To build it, we used only 29 past weekdays. We fed it how many cars came every five minutes, in each direction; GDOT's real timing schedules; and where the detectors sit. One surprise: on the side streets, a whole queue of cars leaving on green was counted as one car, so we corrected those counts.

Then we checked it on 20 other days it had never seen. We gave it the same real timing and each day's real car counts, and compared it with the signal's own records of what it actually did. How long did each green light last? In 34 of 35 cases, within 3 seconds, about one and a half cars. Why did each green end: because cars stopped coming, or because its time ran out? 28 of 35 match. To pass, we needed 28 of 35, a rule we set before the first try.

One limit: this checks what the signal does, not how long the cars wait.

[If asked: the 3-second and 28-of-35 thresholds are a judgement call fixed before the first run. 3 seconds is about one and a half cars. The same idea, a share of cases within a tolerance, is in the FHWA guide, which uses 85% for traffic counts.]

## Slide 11 — Dataset (~25 s)

The intersection is West Paces Ferry Road at East Andrews Drive, in Atlanta: signal 137. The next signal, 138, is 260 metres east, and runs its real timing.

We use weekdays from March to May 2026: 29 days to train, 20 to develop, and the last 7 held back as the test.

## Slide 12 — Experimental Setup (~65 s)

We measure delay: the seconds each car loses compared with driving freely, including waiting to enter. Lower is better. For cars heading west, it includes their wait at signal 138.

The days are split by date into three groups. 29 training days: used to tune the simulation and to train the learners. 20 development days: used to check the simulation and to compare the methods while we could still find and fix problems. And 7 test days, held back until the end, for the final comparison, so that no decision was based on them.

A tie means within 2 seconds, fixed before any result. Each method is compared with the no-cycle controller day by day: a tie needs an equivalence test, and a difference a t-test corrected for testing six methods at once, both at p below 0.05. With only 7 test days, many comparisons stay not settled.

[Not read aloud - if asked: the test days were opened once under a plan written beforehand; after that run we found four errors, wrote the fixes down, reran once, and report both results (backup: Test Run and Rerun). Each learner is trained 5 times, on training days only, and results are the average of the 5. A tie is within 2 s/veh or 5 %, whichever is larger - a judgement call. Conditions: time of day, how busy the hour is, how uneven the traffic is, sudden surges. The what-if raises every count by 25 % on 5 development days; the learners trained on real counts only.]

## Slide 13 — Results (~100 s)

On the 7 test days, the deployed GDOT plan has 31.2 seconds of delay per car. The same controller without its fixed cycle: 24.9. LSTDQ: 25.3. MaxPressure: 26.1. All three beat the deployed plan on all 7 days. So three methods cut delay by 5 to 6 seconds, and one of them does no learning at all.

Against that no-cycle controller, LSTDQ is a tie: within 2 seconds, with p 0.026. The deployed plan is significantly worse, p 0.046. The other two learners, Q-learning at 30.6 and ARS at 30.4, beat the deployed plan on 5 of 7 days, but against the no-cycle controller they, and MaxPressure, are not settled: the days vary too much to call a tie or a difference. Webster's textbook timer is far behind, at 117.7.

Why does nobody beat the no-cycle controller? It is GDOT's own controller, with GDOT's own detector settings, just without the fixed cycle. Once the cycle is gone, this simple rule already serves this intersection well, likely because it is rarely near capacity. Learning adds no clear gain on average: on the development days LSTDQ was slightly better, 24.6 against 25.3 seconds, so any gain is under a second. This is why the comparison matters: against the deployed plan, learning looks like a 5 to 6 second gain; against the same controller without its cycle, that gain disappears.

[Point at: the first three rows, then the p columns.]

[Not read aloud: Webster is designed for a typical day and overflows on busy evenings. p diff. = paired t-test on the daily delay ratio, Holm-corrected over six methods; p tie = equivalence test, margin 2 s/veh or 5 %, whichever is larger. Development days (20), s/veh: GDOT plan 34.3, no-cycle 25.3, LSTDQ 24.6, MaxPressure 27.6, Q-learning 31.5, ARS 36.5, Webster 122.0.] [If asked: dropping the cycle gives up timing with the next signal; we count delay around this intersection only, so that benefit is not fully counted. Development days: LSTDQ better than no-cycle, 19 of 20 days, p 0.021 (Holm).]

## Slide 14 — Results: Time of Day Difference (~55 s)

When does each method win? At night, Q-learning is lowest, 8.1, with the no-cycle controller and the deployed plan at 8.2; LSTDQ and MaxPressure lose about 3 seconds. In the morning peak, LSTDQ is lowest: 21.1. At midday, LSTDQ again: 24.2. In the evening peak, the no-cycle controller wins: 27.8. In six hours with sudden side-street surges, picked after seeing the results, it wins clearly: 39.1, against 58.0 for LSTDQ and over 74 for the others. With every count up by a quarter, on 5 development days the learners never trained on, the no-cycle controller has 45.0; MaxPressure and LSTDQ about 51; Q-learning and ARS fall far behind.

No method wins everywhere. The simple rule is the safest default.

[Not read aloud - full numbers moved off the slide, s/veh, in the order GDOT plan / no-cycle / MaxPressure / LSTDQ / Q-learning / ARS. Test days: night 00-06 8.2/8.2/11.2/11.6/8.1/8.5; morning peak 06-10 26.1/22.8/21.2/21.1/21.8/21.9; midday 10-15 35.0/25.8/26.0/24.2/27.9/26.8; evening peak 15-19 34.0/27.8/32.0/30.6/42.2/38.2; 6 surge hours 85.4/39.1/74.8/58.0/114.5/95.7. What-if on 5 development days: real counts 27.4/24.5/22.8/23.3/26.7/27.3; every count +25 % 63.1/45.0/51.3/51.7/76.9/100.4. From +50 % every controller's queues keep growing for much of the day, so methods are not ranked above +25 %. Green on the slide = lowest in the row. These by-condition numbers are descriptive: no statistical test.]

## Slide 15 — Learners Compared (~70 s)

The three learners get the same detector inputs and the same kind of linear model. The only difference is how they learn. LSTDQ solves for its weights from all recorded decisions at once. Q-learning nudges the weights a little after every decision. ARS tries random changes and keeps the ones that lower delay.

LSTDQ is clearly the best of the three: 25.3 seconds all day, against about 30.5 for the other two, and it holds up in busy hours, 31.1 against about 41 to 42. Q-learning and ARS are better at night, 8.1 and 8.5 against 11.6, but they fall apart when traffic is heavy.

Training tells the same story. LSTDQ settles after one round. Q-learning is best early and drifts if it keeps training. ARS stays noisy, even with about ten times more simulation runs.

So with the same model, the learning method decides whether the controller is usable. That is why LSTDQ is our base method.

[Not read aloud: busy hours = heavy-hour band on test days (validation: LSTDQ 31.3, Q 48.5, ARS 62.0; no-cycle 31.5). Days won against no-cycle on test: LSTDQ 4, Q-learning 2, ARS 1 of 7. Training budget of the kept iterate, 4-hour window-episodes: LSTDQ 44-110, Q-learning 22-44, ARS 220-1,100. Q-learning weights keep growing in later rounds in 4 of 5 seeds. ARS: random search, 11 directions per step on 312 weights. Verdicts vs no-cycle: LSTDQ tie (p 0.026); Q-learning and ARS not settled. The 'same model, different solver' argument is Lagoudakis & Parr 2003's case for least-squares methods.]

## Slide 16 — Results: Who Waits (~60 s)

Who waits? Test days, delay per car. The deployed GDOT plan favours the main street: 18 seconds there, 50 on the side streets. LSTDQ keeps the main street at 19 and cuts the side streets to 34, about 16 seconds less. The no-cycle controller shares the wait evenly: 25 on both.

MaxPressure and the other learners also make the side streets wait longer: 34 to 42 seconds there, against 19 to 28 on the main street. So LSTDQ and the no-cycle controller have about the same average, but different people wait.

Why? Our likely explanation, not yet tested: the learners are rewarded per car, and 58 percent of cars are on the main street. And the side streets only have detectors at the stop line, so a long side queue is mostly invisible.

[Point at: the red side-street column.]

## Slide 17 — Conclusion (~90 s)

For this one intersection. One: the simulation, built only from the agency's data, passed its check on unseen days; it checks how the signal behaves, not delay itself. Two: beating today's timing needs no learning - the deployed plan has 31.2 seconds, the same controller without its fixed cycle 24.9. We expected the learning methods to at least tie the best simple rule; only LSTDQ did, at 25.3. Three: learning changes who waits. And among the learners, how they learn matters most: LSTDQ holds up in busy hours, Q-learning and ARS do not.

Whether methods split apart near capacity, we cannot test on real days here: this intersection is rarely that busy. These results hold for this intersection; whether they hold elsewhere is the next question.

Next steps. One: train and compare on heavier traffic, with the counts scaled up, to test whether the methods pull apart near capacity. Two: repeat the comparison at more intersections, each validated the same way, to see whether our results come from the methods or from this place. Three: retrain the learners with side-street cars weighted more, to test one of our two likely reasons the side streets wait.

Thank you.

[Not read aloud - moved off the slide: the simple rule is more robust at night, in surges and with +25 % traffic; why the learners shift the wait is not yet tested. Limitations: the check covers controller behaviour, not delay itself; the test days were run twice, the rerun after fixes registered before it; side-street demand is a corrected estimate of GDOT's counts; delay is scored around this intersection, so the benefit of timing it with the next signal is not fully counted; one site; our own controller engine; left arrows are served more often than in the field.]
[If asked 'why only one intersection so far?': building and validating the simulation took eight attempts here; we wanted one fully validated site first. 'What would a new intersection give?': it may not change the results, and that would be a finding too; but 137 cannot test heavy traffic (rarely near capacity), what the detectors see (side streets only have stop-line detectors), or a different setting (here one signal tied to one neighbour). A second site needs its own validation first.]

## Slide 18 — SUMO Intersection Sim (~10 s)

(60 s) Preliminary findings, honest limits, and what comes next. The data finding is worth saying: GDOT's presence-zone counts undercount queued traffic - found at two intersections.

---

## Likely questions

**Why only one intersection?**
Building and validating the simulation took eight attempts here. We wanted one fully validated site before adding a second; a second site is one of our next steps.

**Why would a new intersection change anything? What does it give that 137 doesn't?**
It may not change the results, and that would be a finding too. But 137 can't answer three things: heavy traffic (it is rarely near capacity, so we couldn't test whether methods pull apart there); what the detectors see (side streets here only have stop-line detectors, one of our two likely reasons the learners make side streets wait); and the setting (one signal tied to one neighbour). One site tells us what happens here; a second tells us whether it's the method or the place. (A second site needs its own validation first.)

**Why did you choose these methods?**
Each answers one question. GDOT's plan is the real, validated benchmark. The same controller without its fixed cycle separates the gain from dropping the cycle from the gain from learning. Webster is the textbook baseline most papers use. MaxPressure is the most common rule-based adaptive baseline, so it tests learned vs designed rules. The three linear learners use the same inputs and model and differ only in how they learn: LSTDQ (base method, Sahachaiseree & Oguchi), Q-learning (step by step, compared in the same paper), ARS (direct search, our addition).

**Why not SARSA, or other linear methods?**
SARSA is in the same family as Q-learning: both learn step by step, the difference is only which next action they learn from. Q-learning already covers it. Linear SARSA(lambda), as in Alegre et al. 2022, would be a small extension.

**Is ARS from a traffic paper?**
No: Mania et al. 2018, general reinforcement learning. We added it to cover direct policy search.

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
