# Plan and state of things — second site, reframed research questions

> Live status and open decisions: [PROGRESS.md](PROGRESS.md). Site 137 details: [atsc/sites/137/README.md](atsc/sites/137/README.md).

Written 2026-11-16 01:50 JST (midterm talk is today). One page to read first; `OPEN_ISSUES.md` keeps the 7065
problem list, `atsc/README.md` the pipeline, `queries/research-questions-framing.md` the earlier framing draft.
Items marked **(decide)** need your decision; nothing marked that way is started.

---

## 1. Research framing (reframed 2026-11-15, supersedes the draft in `queries/`)

**Main question.** At a real, isolated NEMA intersection, under the constraints an agency actually operates
under, what traffic conditions determine whether adaptive control (rule-based or learned) reduces delay
compared with the actuated control already deployed, and by what timing mechanism?

| | Question | Measured by |
|---|---|---|
| RQ1 Where | Across the measured range of real demand (held-out days, hours, saturation), where do the controllers separate, and is there a region where all responsive controllers are equivalent? | delay per vehicle by condition bin, paired by day |
| RQ2 Why | For each separation, which timing mechanism accounts for it (cycle length, lost time, phase skips, green vs flow ratio)? Confirmed by giving the losing controller that one mechanism and checking whether the gap closes. | per-cycle diagnostics + counterfactual runs |
| RQ3 What it must know | How much of each gain depends on the information available: stop-bar presence vs lane-level queues vs advance counts, and count accuracy? | state-masking runs on the real detector layout |

Demand-calibration error is a methodology validity check, not an RQ.

Hypotheses, each with its mechanism, its counterfactual run, and the domain statement it would license:

| | Hypothesis | Because | Counterfactual | Literature side | Domain statement if confirmed |
|---|---|---|---|---|---|
| H1 | Below a saturation threshold every responsive controller performs the same once constraints are equal | min green + clearance fix the cycle floor; little is left to decide | actuated with the learner's min-green/skip rules | with Schreiber 2022, Alegre 2020; explains Sahachaiseree's low-demand gap as a baseline artefact | at low demand the timing constraints, not the control logic, set the delay |
| H2 | Near capacity the controllers separate; ordering follows how each allocates green against flow ratio | actuated maxes out into fixed-time; MaxPressure pays switching lost time it cannot anticipate | raise actuated max green; force the learner to MaxPressure's switching rule | with El-Tantawy 2014, Song 2026; against Alegre's "all equal" | near capacity the value of adaptivity is the value of anticipating queue clearance |
| H3 | Linear and neural learners perform the same when features encode the phase × lane interaction; linear fails without it | the decision is a conditional allocation, not a sum of lane pressures | linear with shared vs phase-gated lane weights (= 7065's EXP-001 vs EXP-002) | reconciles Schreiber (linear works) with Ault 2020 (linear fails) | any approximator, incl. hand rules, must represent the interaction |
| H4 (cut list) | The near-capacity gain needs lane-level queue information; with presence only the learner falls back to actuated | presence is what actuated already uses | mask the learner's state to presence only | partly with RESCO 2021 | the gain needs lane-level detection to exist |

Fixed before any run on the new site **(decide)**: H1's equivalence margin (proposal: 5 % of delay or 2 s/veh,
tested with TOST, paired by day); the saturation measure (proposal: ATSPM max-out / gap-out share per hour,
independent of counts, because counts are capped by throughput); the condition bins.

Known limits, stated up front: one site, so every claim is scoped to "an isolated four-leg NEMA intersection
with this detection layout"; real days may never reach capacity (then H2 is reported as untestable on real
days — a labelled demand-multiplier sweep is a separate **(decide)** deviation).

---

## 2. State of things (facts as of 2026-11-16)

### 7065 (first site): results exist, validity is limited

- Stage 3 on corrected demand finished 2026-11-12 (`atsc/sites/7065/eval/report.md`, commit c17b0210):
  20 validation weekdays, simulation seed 1, 471 clean hours. Overall vehicle-weighted delay (s/veh):
  MaxPressure 34.6; actuated 42.7; GDOT plan 42.2; Webster 51.4; LSTDQ v2 seeds 38.4–43.1; LSTDQ v2f seeds
  36.7–48.6; LSTDQ v1 seeds 41.9–64.0; linear Q-learning seeds 44.6–91.8. By condition: every controller's
  gain over Webster is largest in light traffic (−30 to −40 %) and shrinks or reverses in heavy hours (Y ≥ 0.40).
- Not accepted: the simulation fails its own field-validation criteria (OPEN_ISSUES B1); 7065 runs
  coordinated in GDOT's Peachtree group but is modelled isolated (B4); the Peachtree through counts had to be
  rebuilt from upstream zones, and the NB side is still ~55 % high (B2); right turns carry no demand (B5).
- Stage 4 (ARS, NFQ, DQN, simulation seeds 2–3) is scripted (`debug/stage4.sh`) and **not run**.
- Decision taken 2026-11-13: 7065 is not the primary site. Its results stay as the first-site record.

### Machine

24 cores, 125 GB RAM, SUMO 1.27.1 via `uv run`, libsumo. Probable faulty RAM (OPEN_ISSUES A2): runs crash
visibly rather than silently so far; 12 reruns matched exactly. memtest still to run.

### Measured compute cost on 7065 (for planning)

| Step | Cost |
|---|---|
| LSTDQ training, one version × one seed (5 LSPI iterations × 22 episodes, 22 workers) | ≈ 7 min |
| Linear Q-learning, 5 seeds in parallel | ≈ 70 min |
| Evaluation, one controller × one full day | ≈ 8–9 min per worker; 500 runs ≈ 3 h 15 on 22 workers |
| NFQ / ARS (stage 4, planned) | 2 h timeout per seed; NFQ-to-convergence 12 h; DQN 24 h |

### Literature (read in full; numbers verified in the PDFs)

Sahachaiseree 2025, El-Tantawy 2014, Alegre 2020, Schreiber 2022, XLight 2025, Song 2026, Ault 2020, RESCO
2021, LibSignal 2024, Zhao 2024, Pálos. The gap is a disagreement, not a void: the three published answers to
"how does learned control's advantage change with demand" conflict, and the single-intersection
learned-vs-MaxPressure and linear-vs-neural results conflict too. Citable gap sentences: RESCO's "under what
circumstances"; Song's "single demand setting" (Zhao 2024 does **not** contain that claim — do not cite Zhao
for it).

### Uncommitted

`evaluate.py` teleport column, `debug/stage4.sh`, stage-3 LSTDQ weights/logs, `intersections/7067/config/`,
`tools/cache/*`, and today's `intersections/7088/`, `1036/`, `1090/`, `1457/` config pulls.

---

## 3. Site: 7088 screened today — not usable as the primary site

SR 9 (Peachtree Rd) @ Pharr Road, MaxTime controller. Pulled 2026-11-16: detector configuration, 4 weekdays of
counts (2026-09-29 to 10-02), timing plans (2026-10-02), Approach Volume (2026-09-14 to 09-25).

| Check | Finding | Source |
|---|---|---|
| Counted movements | EB_L, EB_TR, WB_L, WB_T, SB_L only — **no count on Peachtree through (P2 SB, P6 NB) and nothing on NB** | `intersections/7088/config/detectors.csv` (5 inductive loops, all stop-bar), `counts/info.txt` |
| Approach Volume | NB = 0 every day; SB 1,603–1,853/day (that is the SB left only); no advance detection (`adv 0`) | scratchpad `av_7088.csv` |
| Daily counted total | 4,713–5,013 veh/day — the side street and lefts; the main street is unmeasured | `counts/daily_summary.csv` |
| Isolation | coordinated plans A–F (cycles 120/130/160/180 s, P2+P6 get 70–120 s); neighbouring GDOT signals at 137 m (7087), 260 m (7093), 297 m (7078) | `timing/timing_plan_7088.md`, `signals_all.csv` |

Consequence: the dominant demand cannot be calibrated from ATSPM, and the site is more tightly coordinated
than 7065. Under the fidelity policy the main-street demand cannot be invented, so 7088 fails both selection
rules (complete counts; isolation). Kept as a screened-and-rejected record (`intersections/README.md` after
`check_complete.py`).

### Candidates already screened as isolated and complete (`tools/atspm_signals/candidates_isolated.csv`)

All three have all 8 left/through movements counted, 100 % daytime coverage, and the detector layout the atsc
engine already models (stop-bar presence + advance count loops), which 7065 did not.

| Signal | Intersection | Peak-hour veh | Nearest GDOT signal | Detection | Screening flags |
|---|---|---|---|---|---|
| 1457 | Barrett Parkway @ Burnt Hickory Rd (Cobb) | 6,535 | 934 m | video stop-bar + loop advance counts (330 ft) on both main approaches | WB_T < WB_L (check lane/detector assignment) |
| 1036 | SR 400 @ Settingdown Road | 4,353 | 2,227 m | loops: stop-bar + advance counts (480 ft) | none |
| 1090 | SR 10 @ SR 53 | 4,190 | 5,997 m | loops: stop-bar + advance counts (420–430 ft); one Wavetronix left | none |

**Decision 2026-11-16 02:00 (user): results today, on 137.** 137 (W Paces Ferry @ E Andrews/Slaton) already had
counts, timing, an OSM network and a passing sim check in `intersections/137/`; it was ported to the atsc v2 pipeline
overnight (`atsc/sites/137/`, run `debug/stage1.sh`). Its own data problems and the deviations taken to get it
running tonight are listed in `atsc/sites/137/README.md` (main ones: EB through rebuilt from the advance count zone,
WB left uncounted, lanes inferred from detector zones and from the counts, no calibration/validation). The three
candidates below stay the options for a properly screened primary site.

**(decide) Site, longer term.** Proposal: full screening of all three (7 days of counts, plans, OSM network, aerial lane
check — about 1 h of polite portal pulls per site plus the OSM build), then pick by (a) how close the real
days get to capacity (H2 needs it; 1457 is the busiest), (b) clean detection (1036/1090 have no flags), (c) a
network OSM builds without hand work. 7088 only if you have a reason outside these rules; then the main-street
demand problem has to be solved first, not assumed away.

---

## 4. What we will do, in order

| # | Step | Depends on | Estimate (working time) |
|---|---|---|---|
| 1 | Screen 1457, 1036, 1090 fully; choose the site | decision | ½ day |
| 2 | Site spec: geometry from OSM + aerial check (`GEOMETRY.md`), detector layout from config (`DETECTORS.md`), `signal.json` from the plans, movement map | 1 | 1–2 days |
| 3 | Demand: 60+ days of counts, outage audit, chronological split with a locked test window (**decide**: keep the same calendar lock 2026-10-04..10-22 for every site) | 1 | ½ day pulls + ½ day audit |
| 4 | Capacity calibration (discharge headway vs field) and field validation with criteria written first — the step 7065 never passed; budget it honestly | 2, 3 | 2–3 days |
| 5 | Mechanism diagnostics logged per cycle (cycle length, green split vs flow ratio, lost time, skips, queue at end of green, max-outs) — add to `episode.py`/`metrics.py` once, before any training | 2 | 1 day |
| 6 | Controllers on equal constraints: GDOT plan, actuated (real settings from config), Webster, MaxPressure, LSTDQ v2/v2f, v1 as the H3 ablation; linear Q-learning only if it stays in the hypotheses | 4, 5 | ½ day setup + ≈ 2 h training |
| 7 | Evaluation on the validation days (pre-registered subset first, see §5), paired by day, 1 simulation seed, all training seeds reported | 6 | ≈ 3 h compute per 500 runs |
| 8 | Counterfactual runs for H1 and H2 (one each), then H3 ablation | 7 | ≈ 1 day |
| 9 | Statistics: paired tests by day, equivalence test for H1 with the fixed margin, multiplicity noted | 7, 8 | ½ day |
| 10 | Locked test set, run once, at the end | 9 | ≈ 3 h compute |
| — | NFQ (neural comparator) if time allows; DQN, ARS, H4 on the cut list | | |

Realistic first learned-controller result on the new site: about 1.5–2 weeks from the site decision, dominated
by steps 2–4. Thesis due mid-January 2027: that leaves time for one clean pass plus the counterfactuals, not
for the cut list.

---

## 5. Running faster without losing validity

What the compute actually goes to on 7065: evaluation (≈ 3 h per 500 full-day runs) ≫ LSTDQ training
(15 runs ≈ 1 h 50) ≈ Q-learning (≈ 70 min). Neural learners and DQN would add 10–24 h each.

| Cut | Valid? | Why |
|---|---|---|
| Simulation seeds 3 → 1 | yes, state it | the unit of analysis is the day, paired across controllers; day-to-day variance dominates; 7065 already uses 1 |
| Training seeds 5 → 3 for expensive learners only | acceptable, state it | spread over seeds is a result (7065 v1 ranged 42–64 s/veh), so never fewer than 3; LSTDQ seeds cost 7 min — keep 5 |
| Fewer methods: drop DQN, ARS; NFQ only if time | yes | they are not in H1–H3; a weak comparator is worse than none |
| Evaluation days: pre-registered subset (e.g. every other validation weekday) first, fill in later | yes, if chosen before any result is seen | halves the first pass; the rest completes the same analysis |
| Evaluate only controllers in the hypotheses | yes | 7065 evaluated 25 controller-seeds; the hypotheses need ≈ 12 |
| Keep evaluation windows at full days | keep | RQ1's "where" needs the whole demand range |
| Shorter training (fewer episodes/iterations) | **no** | changes the method; LSTDQ at 5 × 22 is already small |
| Larger time step, lighter calibration | **no** | the discharge calibration is fitted at 0.5 s |
| Pick the best seed or checkpoint on validation days | **no** | final iterate of every seed, all reported |
| Reuse training days for evaluation | **no** | held-out days are the whole point |
| Counterfactual runs later than the main pass | yes | they are the RQ2 answer; schedule after step 7 |

Minimum viable thesis under the clock: H1 + H2 with one counterfactual each, H3 from the v1/v2 ablation, rule
controllers + LSTDQ only, 1 simulation seed, pre-registered day subset first.

---

## 6. Today (2026-11-16, midterm)

Overnight (02:00–~06:00): 137 built on the atsc pipeline; Approach Volume (advance detection) pulled for
2026-08-03..10-03 weekdays; Webster, actuated, GDOT plan, MaxPressure, LSTDQ v1/v2/v2f x 5 seeds trained and
evaluated on the September validation weekdays (simulation seed 1). Status: `atsc/sites/137/debug/stage1.log`;
results: `atsc/sites/137/eval/report.md`. These are **preliminary**: no calibration, no field validation, lanes
unverified (README deviations 1–11). A validated result on a screened primary site remains 1–2 weeks away.
What can be shown truthfully today:

- Problem, related work and the reframed questions/hypotheses (§1), with the literature disagreement as the gap.
- First-site results from 7065 (§2) as preliminary, with their limits stated: validation not accepted,
  coordinated site modelled isolated, main-street counts rebuilt.
- Second-site results from 137 (overnight run) as preliminary, with the README deviation list.
- The site-selection method working: 7088 screened and rejected on evidence in one hour (§3); the three
  candidates that pass.
- Plan and schedule (§4), cut list (§5).

Decisions pending: site (§3); H1 margin, saturation measure, bins, demand-multiplier sweep (§1); calendar
lock for the new site (§4 step 3).
