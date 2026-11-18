# Handoff: midterm presentation prep (site 137)

> **Update 2026-11-18 (later session): parts of this file are superseded.**
> - The test days were opened by the user's go-ahead under the registered plan, then rerun once after the registered
>   engine fix (TEST_PLAN.md amendment 1). Rule 1.1 and future-work item 7.1 are done.
> - The accepted model is now **attempt 8** (V1 34/35, V2 28/35, V3 18/35), not attempt 7. §4.4 and §5 numbers are
>   pre-amendment; current results are in `atsc/sites/137/TEST_PLAN.md` ("Amendment 1 results") and
>   `atsc/sites/137/INTERPRETATION.md`.
> - Deck with results filled: `presentation/eSocLab_Midterm-v3.pptx`, built by `build_v3.py` with `val8.json`
>   (attempt-8 validation pairs). v2 and its builder are unchanged.
> - Correction to slide 9 of v2: the GDOT plan is not a timer. It is actuated within a fixed coordinated cycle
>   (free mode at night); v3 groups it with the detector rules.

Written 2026-11-18 by the Claude session that prepared the midterm deck. It is for another Claude chat that picks up
this work. It records what that session read, decided and built, so nothing has to be re-derived.

- **Talk:** 2026-11-19. Approved title: "Reinforcement Learning Control for Field-Calibrated Traffic".
- **Deck:** `presentation/eSocLab_Midterm-v2.pptx`, built by `presentation/build_v2.py`.
  The user's original, `eSocLab_Midterm-MyVersion.pptx`, must never be modified.
- **Companion files:**
  - `presentation/validation_attempts_cheatsheet.md`: per-attempt Q&A.
  - `futureplan.md`: outcome-level validation candidates and open items.
- **Primary sources:** `atsc/sites/137/VALIDATION.md`, `TEST_PLAN.md`, `PROGRESS.md`, `PLAN.md`.

---

## 1. Standing rules (the user set or confirmed all of these)

1. **Test days stay locked.** May 18–29 is the final test set. Don't read test-day values unless the user explicitly
   unlocks them.
2. **Evidence comes only from GDOT ATSPM.** No outside traffic figures (news, AADT). Flag any constant that comes from
   outside (HCM, SUMO defaults).
3. **Don't say "twin".** It's built offline from historical data and nothing flows back, so strictly it is a digital
   *model* (Kritzinger et al. 2018 taxonomy, cited from memory and unchecked). Say "calibrated simulation".
4. **Don't claim interpretability or readability as a finding of this study.** The user rejected "engineers can
   audit it" as "too hope blinded": no traffic engineer has confirmed it. It may only appear as Sahachaiseree's
   argument, attributed to them.
5. **Rule for every justification on a slide:** it is (a) measured in this study, (b) cited and attributed, or
   (c) labelled as motivation. If it is none of the three, it doesn't go on the slide.
6. **Scope claims to what was read.** Say "in the studies we reviewed", never "no one has ever". The wiki covers
   about 31 papers, nearly all RL. It is not a full literature search.
7. **Validation slides show only attempt 7.** Attempts 1–6 go in backup.
8. **Results slides 12–14 stay blank** until the user asks for them to be filled.
9. **Audience level:** "almost dumbed down". The audience must understand the problem and how the solution was built.
   Keep the user's own slide structure.

---

## 2. Prior work and the novelty claim (the papers were read in full)

### 2.1 Where the papers are

The PDFs are in `/home/andy/Downloads/Things/gr-andy/raw/papers/`:

- **Kwesiga 2025:** `" [Submitted on 4 Mar 2025 (v1), Adaptive Traffic Signal Control based on Multi-Agent
  Reinforcement Learning. Case Study on a simulated real-world corridor.pdf"` (the filename starts with a space).
- **Meess 2024:** `"First steps towards real-world traffic signal control optimisation by reinforcement learning.pdf"`.
- **D2TSC (Li 2024):** `DataDrivenTSC.pdf`.

The wiki has summaries in `/home/andy/Downloads/Things/gr-andy/wiki/papers/`:

- `kwesiga2025-mappo-north-ave.md`
- `meess2024-first-steps.md`
- `li2024-d2tsc.md`
- `sahachaiseree2025-linear-fa-tsc.md`

The cross-paper comparison is `wiki/queries/experimental-setup-across-papers.md` (line ~64: no paper cleanly splits
days into train/validation/test).

### 2.2 What each paper actually did (checked against the PDF text)

| | Kwesiga 2025 (North Ave, Midtown Atlanta) | Meess 2024 (Ingolstadt, Germany) | D2TSC, Li 2024 (Zhuzhou, China) |
|---|---|---|---|
| **Data** | One afternoon, the PM peak of 2023-04-04: video counts plus 6 drones (part of a GDOT research project) | Loop-detector data turned into origin–destination demand ("different days and times during the week") | 7 days of camera data |
| **What was calibrated** | Speed distribution and car-following, fitted to drone-measured saturation headways, following GDOT's Vissim calibration guide. Fit judged "reasonably" from one plot; no numeric target | Nothing is calibrated in this paper. The demand quality figure (r = 0.88–0.99) is **cited from Pohlmann 2010**, not measured here | One sentence: the SUMO model "strictly follows the real-world traffic characteristics". No method, no numbers |
| **Controller / baseline** | Real controller software (MaxTime emulator, software-in-the-loop) loaded with GDOT's field timing | Real production actuated logic (TRENDS kernel), "one-to-one" | The field fixed plan, plus the deployed adaptive system |
| **Simulation checked against the field afterwards?** | **Not reported.** No travel-time, queue or signal-behaviour comparison with the field | **Not reported** | **Not reported.** Their R² = 0.926 checks their delay *estimator* against the *simulator*, not the simulator against reality |
| **Evaluated on held-out data?** | No: tested on the same afternoon's field volumes, scaled ×0.9 and ×1.05 | Not stated | No: evaluated on the same 7 days |
| **Reported gain** | MA-PPO up to **24% travel time** against the field-implemented plans | About **21%** against TRENDS actuated | — |

### 2.3 What is and isn't new

**Not new on its own:** a calibrated simulation with a realistic deployed or actuated baseline. Kwesiga 2025 does it
in Atlanta, against GDOT timing, with *higher* controller fidelity than ours: the real controller software, whereas we
use our own NEMA engine. Do **not** claim "first calibrated simulation with an actuated baseline".

**What is distinctive (in the studies reviewed):**

1. **Out-of-sample validation.** The simulation is checked on 20 days it wasn't tuned on, with pass criteria written
   before the first run. The papers above fit and evaluate on the same data, and don't report a field check.
2. **The reference is the real controller's own log.** We compare with the ATSPM Split Monitor (splits and gap-out
   shares per phase × plan). The others check vehicle behaviour (headways, speeds) at most, not whether the
   controller acts as it does in the field.
3. **It uses only data the agency already collects (ATSPM).** No drones, video or site visits, so it is cheap to
   transfer to other ATSPM signals. This is the strongest practical point.
4. **Days are split by date** into train, development and locked test sets.
5. **Validation found a real data defect:** the presence-zone undercount (§4.3), seen at both 137 and 7065.
6. **MaxPressure and actuated control appear in the same comparison table.** No paper in the wiki does this (wiki
   scope only).

**Turn the weakness into a reason.** Kwesiga and Meess get controller fidelity from the vendor software itself. We run
our own engine, which is exactly why we *had* to show that it behaves like GDOT's controller, and the Split Monitor
validation does that. Their fidelity is assumed from the software; ours is shown by evidence.

**Concede if asked:**

- Kwesiga's driver calibration (drone headways) is more direct than ours (SUMO defaults plus impatience 0.5).
- Kwesiga followed GDOT's Vissim calibration guide, which normally includes validation targets. They may have done
  checks without reporting them, so say "**do not report**", never "did not do".
- Only three calibrated-simulation papers were read in detail. There may be traffic-engineering (non-RL) work using
  ATSPM high-resolution data to calibrate simulations, possibly from Purdue/INDOT. This is unverified and no search
  was done.

**Safe sentence for the talk:**

> "Prior calibrated studies fit the simulation and evaluate on the same data, and don't report checking it against
> the field. Ours is validated on days it was not tuned on, against the real controller's logs, with criteria fixed in
> advance."

### 2.4 Related Work as three gaps (as on slide 4)

| Gap | Literature | What it justifies in this study |
|---|---|---|
| **1. When does learned control pay off?** | Sahachaiseree 2025 (gain shrinks as demand rises), El-Tantawy 2014 (gain grows), Alegre 2020 (no change): three answers to one question | Comparing across traffic conditions, from light to heavy |
| **2. Against what baseline?** | Many studies compare only against fixed-time, so their gains can't be compared with gains against deployed practice. (Kwesiga's 24% and Meess's 21% are **not** small. An earlier claim that "gains are smaller against actuated" was wrong and was retracted.) | The method set: deployed practice (GDOT plan, actuated), the strongest rule (MaxPressure) and a textbook floor (Webster), not only RL against fixed-time |
| **3. In what simulation?** | Kwesiga, Meess and D2TSC build or calibrate the simulation, but don't report a field check, and they test on the data they calibrated with | A simulation calibrated to GDOT data and validated on unseen days |

### 2.5 Why these methods (agreed framing)

- **Why linear RL.** It isn't chosen because it wins: on 137 it doesn't beat actuated. The framing is: **"We test the
  most deployable form of RL (linear) against what agencies already run, to see when it's worth it."** An
  inconclusive answer is still an answer.
  - **"Fast to train":** use only measured numbers. LSTDQ takes about 7 min per seed and linear Q-learning about
    70 min for 5 seeds, both measured on 7065 and not on 137.
  - **DQN 24 h / NFQ 12 h:** these are *planned budgets* in PLAN.md, not measurements. Don't put them on a slide.
  - **"Converges":** too strong. LSTDQ runs a fixed 5 rounds, so say that.
  - **"Runs on existing controller hardware":** unverified. Say only "the decision step is computationally trivial".
  - **"Data efficient":** true for LSTDQ specifically. Sahachaiseree reports about 10–50 episodes against 2,000–4,000
    for gradient-trained models. It barely matters in a simulator with unlimited data, so don't lead with it.
- **Why three linear learners.** They share the features, the action (extend or end green) and the training days;
  only the way they learn differs:
  - **LSTDQ:** batch least squares; the reference method (Sahachaiseree 2025).
  - **Linear Q-learning:** semi-gradient TD with a normalised step, online. Comparing it with LSTDQ asks *batch vs
    online* (Lagoudakis & Parr 2003 predict that least squares is more stable).
  - **ARS:** random search directly on delay, with no value function (Mania et al. 2018). It asks *value-based vs
    direct policy search*. Ault 2020 is a related interpretable-policy search.
- **Baselines:**
  - Webster: textbook fixed-time floor.
  - GDOT plan: what is actually deployed, time-of-day.
  - Actuated: deployed-style detector logic.
  - MaxPressure: the strongest rule-based method in the literature.
- **Dropped or later:**
  - NFQ: dropped (no time).
  - DQN: after the midterm, as the neural reference. Until it runs, don't claim "linear is enough".
  - PPO: excluded (unstable in RESCO / Ault 2020).

---

## 3. Terminology answers

- **"Field-calibrated":** calibrated *to* field data, not *in* the field. That is standard traffic-engineering usage
  (Kwesiga writes "field-measured headways" and "field-implemented plans"). Define it once: "the simulation is tuned
  to GDOT's real-world measurements (ATSPM) and checked against them on days it wasn't tuned on." Nothing was deployed
  on the real road.
- **"Validation" has two meanings.** The slides keep "validation" for checking the simulation, and call the 20
  Apr 20 – May 15 days "**development days**", even though the code calls that split "validation".

---

## 4. Site 137 and the simulation (facts for Q&A)

### 4.1 Site and data split

- **Site:** W. Paces Ferry Rd @ E. Andrews Dr / Slaton Dr, Buckhead, Atlanta.
  - W. Paces Ferry is the main street (EB/WB, 2 lanes each way).
  - The side streets are E. Andrews (SB) and Slaton (NB), with 3 lanes.
  - Upstream signal 138 is about 260 m east and is simulated with its own field timing.
- **Days** (weekdays, Mar–May 2026):
  - **Train:** Mar 2 – Apr 17 (29 days).
  - **Development:** Apr 20 – May 15 (20 days).
  - **Test, locked:** May 18–29 (7 days). Memorial Day, May 25, is excluded; May 21 and May 27 are absent.

### 4.2 Taken from GDOT, and what isn't

**From GDOT ATSPM:**

- Turning Movement Counts: demand.
- Split Monitor: plans, passage-time fit, force-off mode, and the validation reference.
- Timing & Actuation:
  - pedestrian calls;
  - presence-zone undercount factors;
  - left-turn clearance target;
  - the 137–138 offset;
  - call handling.
- Detector configuration.

**Not from GDOT** (disclose these):

- Geometry: OSM plus the user's lane check.
- Saturation flow: HCM, 1,900 veh/h/lane.
- Drivers: SUMO defaults except impatience 0.5.
- Detection: a 40 ft stop-bar zone is assumed, and stop-bar detectors were added on P2/P6.
- Pedestrians: a 4.0 s walk is assumed, with no pedestrian calls 21:00–06:00.
- EB/WB right turns run as through movements.
- Clearances and minimum greens were read on 2026-10-02, outside the study period.

### 4.3 Demand and the undercount

- **Demand.** Each 5-min bin gets exactly the GDOT count, after correction. Each car's time inside the bin is uniformly
  random, which makes this **Poisson arrivals conditioned on the measured count**. Cars enter early by their
  free-flow time so they reach the stop line in the right bin. The seed changes times and lanes, never counts.
  Westbound through traffic arrives in platoons released by signal 138.
- **Presence-zone undercount.**
  - **Which counts:** the side-street (NB/SB) and EB-left counts come from stop-bar presence zones.
  - **Why they're low:** a queue discharging on green keeps the zone occupied, so about 5 cars register as 1.
  - **Correction:** cars are estimated from how long the zone stays occupied during green, at about 1.9 s per car.
    This gives a factor per movement from 9 train days, applied to daytime bins.
  - The same defect was found at 7065, there via neighbour flows, not via validation.

### 4.4 Validation (attempt 7, accepted)

**Method:** run GDOT's own timing in the simulation on the 20 development days. Compare with the Split Monitor per
phase × plan: 35 pairs, phases 1/3/4/5/7/8, plans A–G, and a pair needs at least 5 days.

**Criteria:**

| Check | What is compared | A pair passes if | The check passes if | Attempt 7 |
|---|---|---|---|---|
| **V1** | Average split (green + yellow + red clearance) | \|median over days of (sim − field)\| ≤ 3 s | ≥ 28/35 pairs pass, and no pair is worse than 6 s | **34/35**, worst 3.1 s |
| **V2** | % of cycles ending in a gap-out | median gap ≤ 15 points | ≥ 28/35 pairs pass, and no pair is worse than 30 points | **29/35**, worst 27 |
| **V5** | Health | — | 0 teleports, and W. Paces Ferry through PM delay > 100 s on at most 2 days | **Passed** |
| V3 | Skips | — | Reported, not scored | 19/35 (does not match) |

V4 is not defined for 137.

**Why the median over days:** one odd day can't decide pass or fail. A total would just grow with the number of days.

**Thresholds:** a judgement call, carried over unchanged from 7065, with no written justification. Defend them as
fixed before the first run and never changed: 3 s is about 1–2 cars' worth of green. FHWA Traffic Analysis Toolbox
Vol. III uses a similar "about 85% of cases within tolerance" rule. That is cited from memory and must be checked
before citing.

**Is it enough?** It's enough for a first validation, but it is indirect:

- It checks controller *behaviour*, never an *outcome* such as delay.
- V2 is the same quantity the passage times were fitted to (out-of-sample, but not independent).
- V3 fails: the simulation serves left arrows more than the field does (flashing-yellow share 0.73–0.75 vs 0.85–0.88).
- It is validated only under GDOT's timing.

Its strength is that it **caught real errors**: the undercount, the missing platoons and the force-off mode.
Outcome-level checks (Purdue Split Failure and others) are in `futureplan.md`.

**Attempts:**

| # | Change | V1 | V2 |
|---|---|---|---|
| 1 | As built | 19 | 11 |
| 2 | Passage times fitted on train days | 15 | 16 |
| 3 | Pedestrians | 20 | 18 |
| 4 | Undercount corrected | 29 | 19 |
| 5 | Impatience 0.5 | 27 | 20 |
| 6 | Signal 138 | 26 | 23 |
| 7 | Floating force-off for P1/P5 | **34** | **29** |

- Controller fixes: attempts 2 and 7. Traffic fixes: 3–6. So validation tests the traffic too, through the controller.
- Details per attempt are in `validation_attempts_cheatsheet.md`.

---

## 5. Results on hand (attempt-7 model, development days; NOT on the slides yet)

**Delay** is SUMO timeLoss + departDelay, weighted by vehicle, in s/veh:

| Method | Delay |
|---|---|
| Actuated | 25.8 |
| MaxPressure | 26.7 |
| LSTDQ | 26.7 |
| GDOT plan | 34.1 |
| ARS | 35.5 |
| Q-learning | 37.6 |
| Webster | 60.9 |

- **Spread across training seeds:** LSTDQ 5.2, Q-learning 2.0, ARS 15.7 s/veh. The pre-registered expectation that
  LSTDQ varies less than Q-learning did **not** hold.
- **Against actuated:** no adaptive method differs significantly, but equivalence is not shown either (TOST
  inconclusive). GDOT plan and Webster are significantly worse (0/20 days won).
- **Earlier session notes (verify in `atsc/sites/137/eval/analysis.md` before using):**
  - Ranking by load: actuated wins light and heavy hours; MaxPressure wins busy hours (Y 0.45–0.6), the PM peak and
    the evening.
  - MaxPressure runs shorter cycles near capacity.
  - LSTDQ runs long cycles of 95–105 s.
  - On the Apr 28 surge, MaxPressure averages 87 s/veh against 45 for actuated.
  - Worst-served movement p95: about 190–205 s under MaxPressure and the learners, against 104 s under actuated.
- The demand-scale sweep has not been rerun on attempt 7. The last one was on attempt 5, a model that did not pass
  validation.

---

## 6. Deck state (`eSocLab_Midterm-v2.pptx`, 20 slides, 4:3)

| # | Slide |
|---|---|
| 1 | Title |
| 2 | Agenda |
| 3 | Problem |
| 4 | Related Work (3 gaps) |
| 5 | Study Goal (goal, O1–O3 tied to gaps, H1/H2) |
| 6 | System Overview (build → calibrate & validate → train → compare, with a fail → fix loop) |
| 7 | Dataset |
| 8 | Calibration & Validation (native scatter of the 35 pairs, attempt-7 criteria) |
| 9 | Methods Compared |
| 10 | How the Learner Decides |
| 11 | Evaluation Design |
| 12–14 | Results ×2 and Main Findings: **blank** |
| 15 | Conclusion (done so far, limitations; findings box blank) |
| 16 | Future Work |
| 17–20 | Backup: validation attempts; detector undercount; prior simulations comparison; inputs not from GDOT |

- Every slide has speaker notes.
- The title slide's "Ritsumeikan University" line is cut off in the LibreOffice render. The user's original renders
  the same way, so it is probably font substitution. It hasn't been checked in PowerPoint.

**Rebuild:**

```
uv run --no-project --with python-pptx --with lxml python presentation/build_v2.py \
  presentation/eSocLab_Midterm-MyVersion.pptx out.pptx val7.json \
  /home/andy/Downloads/GDOT/intersections/137/network/preview.png
```

`val7.json` holds the per-pair medians. It was computed from `atsc/sites/137/validation/attempt7/sim_splitstats.csv`
and `intersections/137/timing/splitstats_137.csv`; it lives in the old session's scratchpad and may need regenerating.

---

## 7. Future work (as on slide 16; each item has a purpose)

1. **Final locked test** on May 18–29, under the registered plan.
2. **Outcome-level validation from ATSPM.** Purdue Split Failure is the best candidate; the others are in
   `futureplan.md`. It is the first fully independent check and targets saturation.
3. **Replicate at 7065** (Peachtree @ Piedmont), one site and not 2–3, given the thesis deadline (about late January):
   - Purpose 1: does the same calibrate-then-validate procedure, with unchanged criteria, pass at a second site?
   - Purpose 2: a consistency check at a coordinated site closer to capacity.
   - **Caveat to say yourself:** 7065 differs in both coordination and saturation, so a different ranking can't be
     pinned on either. Two or three sites can't separate "conditions" from "site". Saturated sites are also where
     presence-zone counts undercount most.
4. **Train the learners at saturation** (H2), and **add DQN** as the neural reference.

**Other open items:**

- Confirm the clearances and minimum greens on a Mar–May chart.
- `atsc/sites/137/README.md` is stale: it still says there is no pedestrian timing, among other things.
- Write a justification for the validation thresholds.
