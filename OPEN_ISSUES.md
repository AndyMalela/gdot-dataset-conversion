# Open issues: SIG 7065 methods comparison

Working list of the current criticisms and problems, to tackle one at a time. Written 2026-11-10. Midterm talk
2026-11-16; results needed by about 2026-11-12.

For each issue: what is wrong, the evidence, why it matters, and the proposed next step. Tick the box and add a
dated line under **Resolution** when an item is closed. Items that need your decision are marked **(decide)**.

Order: blocking the midterm first (A), then research validity (B), fairness of the comparison (C), the story (D),
and housekeeping (E).

---

## A. Blocking the midterm

### A1. The evaluation is not finished
- [ ] **Problem.** 323 full-day runs are missing:
  - DQN: all 300 runs (5 training seeds × 3 simulation seeds × 20 days);
  - 23 runs of the other learners on simulation seeds 2–3, which failed or never ran.
- **Evidence.** `eval/hour_mv.csv` has 2,117 runs and has not changed since 2026-11-09 18:05.
- **Why it matters.** There is no DQN result, so there is no H2a-DQN verdict. The seed 2–3 statistics are also
  incomplete. `results/` dates from 2026-11-09 12:45: learners on simulation seed 1 only, and no DQN.
- **Next step.** About 1¾ h of compute with the machine left on. The run is resumable and skips finished work.
  Then `evaluate.py report`, `analyze.py`, and commit `results/`.
- **Resolution.**

### A2. The machine is unreliable
- [ ] **Problem.** There are two separate faults.
  1. **Probable faulty RAM.**
     - Files corrupted at random: invalid XML tokens, a route named `AB_T` instead of `EB_T` (one bit flipped).
     - Python segfaults at bit-flipped-looking addresses, and a kernel error on 2026-11-06.
     - The memory is not ECC, so the kernel logs nothing.
  2. **Stray power-key presses.** These caused the shutdowns on 2026-11-09 21:25 and 2026-11-10 16:49. The
     second came right after the Keychron keyboard disconnected and reconnected twice.
- **What was checked.** 12 finished runs (6 from Nov 7, 6 from Nov 9) were rerun and matched the stored rows
  exactly. So far, corruption breaks runs visibly rather than silently changing numbers. The DQN weights cannot
  be checked this way, because training is too long to repeat.
- **Safeguards in place.**
  - `evaluate.py` raises on a crashed worker instead of hanging.
  - An unreadable tripinfo file is kept in `debug/` for diagnosis.
  - DQN training logs such an episode as `nan` and continues.
- **Next step.**
  - Make the power key do nothing: `HandlePowerKey=ignore` in `/etc/systemd/logind.conf`, and
    `gsettings set org.gnome.settings-daemon.plugins.power power-button-action 'nothing'`.
  - Try another USB port or cable for the keyboard.
  - Run memtest86+ overnight after the midterm numbers are in.
  - Mention the rerun check in the report.
- **Resolution.**

### A3. The midterm summary is not written
- [ ] **Problem.** There is no one-page summary yet. It needs:
  - the comparison protocol (slide text);
  - the key messages with final numbers;
  - the limitations, including the failed validation (B1).
- **Next step.** Write it once A1 is done; it depends on the final numbers.
- **Resolution.**

---

## B. Research validity (does the simulation represent 7065?)

### B1. The simulation fails its own acceptance test
- [ ] **Problem.** `atsc/sites/7065/VALIDATION.md` says **not accepted yet**:

  | Check | Measure | Result |
  |---|---|---|
  | V1 | average split | 19/28 pairs within 3 s, worst 10.1 s: **fail** |
  | V2 | % gap-outs | 18/30 pairs within 15 points, worst 58: **fail** |
  | V3 | % skips | pass |
  | V4 | P8 discharge | pass |
  | V5 | health: overflow days, teleports | **fail** |

- **Evidence.** The failures are mostly on the left-turn phases. One candidate cause is the stop-bar radar
  undercounting lefts.
- **Why it matters.** This is the biggest hole. Every result is built on a simulation that has not passed its
  own test, and a comparison is only as credible as its simulation.
- **Next step.**
  - Midterm: state it openly as a limitation, with the likely cause.
  - After the midterm: test whether the ranking survives it (D3).
- **Resolution.**

### B2. Peachtree through counts are far too low (confirmed 2026-11-10)
- [ ] **Problem.** 7065's Peachtree through counts (P2 "SB_T" from the NE, P6 "NB_T" from the SW) come from
  stop-bar presence zones that cannot count a discharging queue. First seen as P2 reading about half of what the
  neighbouring signals imply.
- **Evidence.** Sep 14–25 weekdays, 06:00–20:00, heading SW:
  - 7058 sends 1,512 veh/h towards 7065, but 7065 counts 724 (ratio 0.48).
  - 7065 sends 595 veh/h towards 7066, but 7066 counts 1,196 (ratio 2.01).
  - ATSPM's arrivals-on-green chart also shows P2 at about one lane's worth.
  - Heading NE: possibly low too, but not clearly.
  - Piedmont: cannot be checked (7071 has no Piedmont through counts; 7079 is too far and counts only some
    movements).
- **Timing-chart check (2026-11-10): confirmed, and worse than half.** Detector actuations counted per lane on
  GDOT's Timing & Actuation charts, 5-min bins (`tools/lanecheck/`):

  | Bin | Phase | Report | Stop-bar presence zones | Upstream count zones |
  |---|---|---|---|---|
  | Sep 16 08:00 | P2 | 36 | 33 | 128 |
  | Sep 16 12:00 | P2 | 40 | 38 | 104 |
  | Sep 16 17:30 | P2 | 32 | 31 | 187 |
  | Sep 16 21:00 | P2 | 34 | 35 | 76 |
  | Oct 2 08:00 | P2 | 49 | 51 | 129 |
  | Sep 16 08:00 | P6 | 28 | 28 | 142 |
  | Sep 16 12:00 | P6 | 31 | 29 | 122 |
  | Sep 16 17:30 | P6 | 18 | 16 | 167 |
  | Sep 16 21:00 | P6 | 37 | 39 | 83 |
  | Oct 2 08:00 | P6 | 18 | 16 | 109 |

  - **The report's Peachtree through counts are the stop-bar presence zones** (P2: ch21–23, P6: ch5–7), not the
    upstream count zones (ch24–26, ch8–10). `DETECTORS.md` assumed the opposite and needs correcting.
  - A presence zone stays occupied while a queue discharges, so it cannot count it. The busier the approach, the
    less it counts: at 17:30 the report *falls* (P6: 18) while the upstream zones *rise* (167).
  - The upstream zones read 2.2–9× the report in the daytime. (Corrected 2026-11-12: at night the report is still about half; see below.)
  - The upstream zones are not exact either: the middle lane reads about twice the outer lanes, and sometimes
    more than one lane can discharge. Some double counting between lanes is likely.
  - Both Peachtree approaches are affected, not only P2.
- **Approach Volume report (2026-11-10).** Its lane-by-lane chart sums every channel tagged as a count detector.
  - At the neighbours and on Piedmont it equals the turning-movement totals.
  - On Peachtree it is about 3× the report, because it adds the upstream zones to the stop-bar zones and lefts.
  - So Approach Volume minus the report gives the upstream zones per day: about 24k veh/day from the NE (report
    through: 9.3k) and about 22k from the SW (report: 5.8k), Sep 16. The neighbours carry 17–26k on Peachtree.
  - Its upstream-radar (Advance) charts are unusable: from about 0.15× to 2.4× the counts.
  - Raw reports are cached in `tools/cache/av/`.
- **Consequences.**
  - Peachtree through demand in the simulation is too low by a factor of roughly 2–4, most in the peaks.
  - All four left-turn counts also come from stop-bar presence zones (ch1–2, ch17–18, ch33, ch48). They may be
    undercounted the same way, which would explain the failed left-turn validation (B1). Not yet checked.
  - Piedmont through counts: see the check below. They come from the right kind of zone and stand, with one
    open doubt on the S approach.
- **Piedmont timing-chart check (2026-11-11).** Same method, phases P8 (report "EB_T", from the N) and P4
  ("WB_T", from the S), same bins (`tools/lanecheck/tna_analyze_piedmont.py`):

  | Bin | P8 report | P8 count zones (T1+T2) | P4 report | P4 count zones (T1+T2) |
  |---|---|---|---|---|
  | Sep 16 02:00 | 2 | (chart rows dropped) | 7 | 9 (4+5) |
  | Sep 16 08:00 | 57 | 59 (24+35) | 51 | 51 (8+43) |
  | Sep 16 12:00 | 63 | 68 (26+42) | 33 | 36 (7+29) |
  | Sep 16 17:30 | 70 | 73 (40+33) | 40 | 43 (12+31) |
  | Sep 16 21:00 | 41 | 43 (20+23) | 31 | 33 (7+26) |
  | Oct 2 08:00 | 52 | 53 (18+35) | 33 | 36 (5+31) |

  - **The report's Piedmont through counts are the count zones** (P8: ch40–41, P4: ch55–56), within 0–9 %
    (my marker counter reads a few high). Piedmont's stop-bar zones are presence-only and not in the report.
  - The count zones fire through each green at 1.5–2.5 s spacing per lane, i.e. they count a discharging queue.
    So Piedmont does not have Peachtree's problem.
  - Known, small: on the worst PM days the P8 zones probably double-pulse in stop-and-go queues (spike bins up
    to 206 per 5 min; `intersections/7065/timing/capacity_check/README.md`). An overcount, not an undercount.
  - **Open doubt, P4 (from the S):** lane 1's count zone reads only ¼–⅕ of lane 2 (39 vs 160 over the six bins),
    while at the stop bar the two lanes look similar. Either lane 1's zone misses vehicles (then WB_T is too low,
    by up to about a third) or lane 2's zone also catches lane-1 vehicles (then the total is about right). Lane 2
    sometimes fires about 1 s apart, faster than one lane can discharge, which favours the second reading. Not
    settled; worth one look at the zone layout if GDOT can share it. P8's two lanes are balanced (128 vs 168).
  - P4's Advance channel (ch51) does not track the counts (24–76 vs 33–51); P8's (ch36) reads almost nothing.
    Consistent with the Approach Volume finding that the Advance data are unusable.
- **Numeric source for the upstream zones found (2026-11-12).** The Approach Volume report returns numeric
  totals for any window. A window [t, t + N − 1 min] reproduces the turning-movement report's bins **exactly**
  on Piedmont (12 of 12 comparisons, 5-min to 60-min windows; with end = t + N it includes one extra minute).
  So on Peachtree: Approach Volume − (left + through in the report) = the upstream count zones, as exact portal
  numbers, no chart reading. `tools/lanecheck/av_window.py`, `av_pull_15min.py` → 
  `intersections/7065/counts/av_7065_15min.csv` (train + validation days only; the locked test set is not requested).
  - **Checked on all 20 validation weekdays (2026-11-12, `tools/lanecheck/av_check.py`):** Piedmont Approach
    Volume = report in 3,794 of 3,794 15-min windows; no negative upstream value on Peachtree. Daily through
    traffic, median: from the NE 24,011 (report 9,252, ratio 2.6); from the SW 21,996 (report 5,654, ratio 3.9).
  - **All 63 usable train and validation days pulled (2026-11-12 12:40):** Piedmont exact in 11,882 of 11,882
    windows; no negative Peachtree value; 70 windows have no data (Monday-night outages already flagged in the
    counts). The largest Peachtree windows fall at 18:00–18:15 on the same days as the known P8 spike bins
    (Sep 21, 23, 24, Jul 21, Aug 12), so that spike is common to several approaches; cause not looked at.
  - **From the NE (P2): confirmed by the neighbour at every hour of the day.** 7058's through count towards 7065
    against the upstream zones, mean veh/h over 9 weekdays (Sep 14–25): 02:00 93 vs 89; 08:00 1,559 vs 1,423;
    12:00 1,510 vs 1,398; 17:00 2,025 vs 1,990; 21:00 877 vs 812. The report reads 45, 581, 534, 655, 361.
  - **The report is about half even at night**, when there is no queue (00:00–05:00: report 44–113 veh/h, upstream
    zones and 7058 both 80–245). So the stop-bar zones also miss free-flowing vehicles; "agree at night" in the
    first chart check was wrong (two sparse bins).
  - **From the SW (P6): not confirmed, probably somewhat high.** 7066 sends 60–80 % of what the upstream zones
    count (08:00 1,028 vs 1,604; 12:00 900 vs 1,372; 17:00 964 vs 1,571; 02:00 91 vs 109). The report reads 364,
    356, 292, 76. Possible reasons: the P6 zones also see left-turners before the left lanes begin (43–71 m,
    `DETECTORS.md`), or 7066 undercounts. Downstream, 7058 counts only 30–45 % of the zones (its count in that
    direction is clearly low). So the true P6 through flow lies between 7066's feed and the upstream zones.
  - The middle lane reads 1.5–1.8× the outer lanes on both approaches. P2's total is confirmed anyway, so the
    imbalance is not evidence of over-counting.
  - Evidence is limited to GDOT ATSPM data (student, 2026-11-12). A 2016 road-count figure quoted in a news
    article was looked at once and is not used.
- **Left turns show the same signature (2026-11-12, two PM charts only, not quantified).** P5 green at Sep 16
  17:32:27–17:32:49: lane 2's zone stays on for 13.5 s of green (about 6–7 vehicles at saturation headway) and
  counts 1; lane 1 stays on for the first 11 s and counts 3 over the whole green. Lefts have no second detector
  set, so their true volume cannot be measured from the portal.
- **Open: how to correct the demand. (decide)** Proposed: Peachtree through = upstream zones (15-min totals,
  spread uniformly over the 15 min, as counts are now spread over 5 min). Lefts: as reported, undercount
  disclosed; an occupancy-based estimate only as a labelled sensitivity run.
- **Why it matters.** Peachtree is one of the two main roads. Its real demand changes which approach saturates,
  why GDOT gives Peachtree long greens, and possibly the controller ranking.
- **Next step.**
  - Correct `DETECTORS.md`.
  - Check the left-turn counts (B1). They have no second detector set to compare with, so the test is whether
    the vehicles counted per green fit the length of green the field gives.
  - Agree the correction method, then rebuild demand and validation after the midterm.
  - Midterm wording: "GDOT's report counts Peachtree through traffic with presence zones that miss queued
    vehicles; it reads 2–9× below the count zones in the daytime. Current results use the report as given; the
    corrected demand is the next step."
- **Resolution.**

### B8. Doubt: are the Peachtree and Piedmont counts assigned to the right roads?
- [ ] **Question (student, 2026-11-10).** The simulation puts GDOT's NB/SB columns on Peachtree and EB/WB on
  Piedmont. By compass it would be the other way round. Is the simulation's assignment right?
- **Evidence for the current assignment.**
  - GDOT's own phase titles name the roads: "SR 141 Peachtree Road SB" (P2), "SR 237 Piedmont Road EB" (P8).
  - Lane fingerprint: the NB/SB detector sets have 2 left + 3 through lanes, and the EB/WB sets have 1 left +
    2 through + 1 right. That matches Peachtree and Piedmont on the ground (student's Google Maps check,
    2026-10-23).
  - Report columns matched detector actuations per phase on 2026-10-02 (lefts 13/13, 16/16, 9/9; throughs 53/52,
    33/33).
  - New test, 2026-11-10: do a column's day-to-day ups and downs follow the neighbouring signal on the same road?
    15-min bins, Sep 14–25, 06:00–20:00, time-of-day mean removed.

    | Neighbour flow | Column expected (current assignment) | Correlation | Best other column |
    |---|---|---|---|
    | Piedmont S-bound arriving at 7079 | EB_T | +0.60 | +0.14 |
    | Peachtree SW-bound arriving at 7066 | SB_T | +0.48 | +0.15 |
    | Piedmont N-bound leaving 7079 | WB | +0.40 | +0.13 |
    | Peachtree NE-bound arriving at 7058 | NB_T | +0.21 | +0.13 |
    | Peachtree NE-bound through 7066 | NB | +0.14 | +0.10 |
    | Peachtree SW-bound arriving at 7058 | SB | +0.31 | **+0.38 (EB)** |

- **Reading.** Three links clearly support the current assignment and two weakly. One is ambiguous: the link into
  7065's Peachtree-NE approach.
- **Timing-chart check (2026-11-10).** The SB_T and NB_T columns equal, bin by bin, the three stop-bar through
  channels of the charts titled "SR 141 Peachtree Road SB / NB" (table in B2). Only Peachtree has three through
  lanes. The ambiguous link is explained by B2: that column falls as traffic rises.
- **Next step.** Student to confirm or keep the doubt open.
- **Resolution.**

### B3. "Heavy" demand is not really saturated
- [ ] **Problem.** The heavy bin (Y ≥ 0.40) peaks at about Y = 0.54. Queues reach the start of the modelled road
  in only about 15 % of heavy hours.
- **Why it matters.** Any "high saturation" claim is barely tested. The heavy-demand win of LSTDQ v2f should be
  described as busy-peak, not oversaturated.
- **Next step.**
  - Wording now: describe the bins by Y, not as "saturated".
  - After the midterm: B2's corrected P2 demand or a demand-scaling scenario would reach real saturation. Each
    scenario needs your agreement first. **(decide)**
- **Resolution.**

### B4. 7065 is modelled as isolated, but it runs coordinated
- [ ] **Problem.**
  - In the field, 7065 runs in GDOT's coordinated Peachtree group with 7066, 7071 and 7058 (shared cycle
    120/160/180/130 s).
  - The model is isolated: random arrivals, no platoons, offset 0 (the true offsets are unknown).
- **Why it matters.** The field plan pays coordination's cost without its benefit, so its 50.3 s/veh is
  pessimistic. Adaptive controllers are not tested against platoon arrivals.
- **Next step.** State it with every figure (already in `results/README.md`). After the midterm: a
  platoon-arrival robustness scenario (D3).
- **Resolution.**

### B5. Right turns carry no demand
- [ ] **Problem.** GDOT does not count right turns at 7065, so none are simulated. That includes the NE
  free-right slip, which bypasses the signal.
- **Why it matters.** Shared through-right lanes are less loaded than in reality, and some of B2's gap may be
  rights.
- **Next step.** State it as a limitation. After the midterm: a rights scenario with assumed shares, labelled as
  an assumption.
- **Resolution.**

### B6. The detector count-zone distance is assumed
- [ ] **Problem.** The simulation places all Matrix count zones at 79.2 m. GDOT's configuration gives no distance,
  and one T&A chart suggests at least about 50 m (`DETECTORS.md`).
- **Why it matters.** It affects which vehicles the simulated detectors count, and the state that every learner
  sees.
- **Next step.** Estimate the distance from red-phase counts over many T&A cycles (the open item in
  `DEMAND.md`).
- **Resolution.**

### B7. Geometry sign-off is pending
- [ ] **Problem.** The NE bay geometry has not been signed off by you. **(decide)**
- **Next step.** Review `atsc/sites/7065/GEOMETRY.md` and confirm, or list the corrections.
- **Resolution.**

---

## C. Fairness of the comparison

### C1. The neural comparator is weak
- [ ] **Problem.** NFQ never converged.
  - The registered version (5 backups) gives 69.9 s/veh.
  - Amendment 1 (to convergence) hit the 400-backup cap and gives 49.3, worse than actuated control.
  - So "linear beats neural" (H2a) currently rests on a strawman.
- **Status.** A proper Double DQN (SB3-default settings, target update corrected) is trained on 5 seeds but not
  yet evaluated (A1). H2a is judged on DQN once it is evaluated: LSTDQ v2 within 5 % of DQN.
- **Next step.**
  - Evaluate DQN (A1).
  - After the midterm: an **equal tuning budget** for every method, rule controllers included (MaxPressure,
    actuated), fixed before running.
- **Resolution.**

### C2. H2b's episode-budget part is borderline
- [ ] **Problem.** H2b's episode-budget criterion comes out at 110/1100 = 0.10, or 0.12 counting all 132
  episodes. That is on the boundary.
- **Next step.** Report it as borderline, not as supported. Recheck once DQN is in (A1).
- **Resolution.**

### C3. No correction for multiple tests
- [ ] **Problem.** About 50 paired tests against MaxPressure are made with no correction, so expect about 2 false
  positives (already noted in `results/README.md`).
- **Next step.** Add a Holm correction column to `paired_vs_maxpressure.csv`, or limit the claims to the
  pre-registered comparisons.
- **Resolution.**

### C4. Teleports are not recorded in the evaluation
- [ ] **Problem.** One teleport (an NB_L vehicle) was seen in an evaluation log, and the controller that caused it
  is not known. `evaluate.py` does not record teleports.
- **Why it matters.** A controller that causes gridlock can look better than it is, because teleported vehicles
  stop accumulating delay.
- **Next step.** Log teleports per run in `hour_mv.csv` (needs a rerun), or at least count them in a rerun of the
  heavy hours.
- **Resolution.**

---

## D. The story

### D1. State a single claim
- [ ] **Problem.** The direction has shifted several times: the spillover extension, a methods comparison, a
  deployable linear controller, a ladder of learners. That left no single claim. The comparison is now the
  thesis (your professor's requirement).
- **Proposed claim.** "A controlled, field-calibrated comparison of linear RL and rule-based signal control:
  where each wins, why, and whether the ranking survives the known field-data errors." The novelty is *how* the
  methods are compared:
  - a controlled ladder (same state, action and reward);
  - a map of strengths and weaknesses by condition;
  - a mechanism explanation;
  - robustness to data errors;
  - statistics.
- **Next step.** Write RQ2a/b, H2a/b, H2a-DQN and the claim into Part C of
  `queries/research-questions-framing.md`. **(decide)**
- **Resolution.**

### D2. Own the interpretation
- [ ] **Problem.** Most of the code was written by Claude. At the midterm and the defense, you need to explain the
  findings yourself.
- **Questions to be ready for** (answers in `results/analysis.md`):
  - Why does LSTDQ v2f lose at light demand (+3.3 s against MaxPressure) and win at heavy demand (−2.7 s)?
  - Why does MaxPressure starve the P5 left (~7.5 s greens)? It counts lefts only in the 12 m stop-bar zone.
  - What did v2f learn? A gap-out-like rule; it extends while a queue remains and ends to serve queues at the
    next phases; most effects agree in sign on 5/5 seeds.
  - Why do the left-turn phases fail validation (B1)?
  - Why is the field plan worst? Cycles reach 173 s at heavy demand, and coordination is not modelled (B4).
- **Next step.** Go through `results/analysis.md` and rehearse these answers.
- **Resolution.**

### D3. The robustness scenarios have not started
- [ ] **Problem.** "Does the ranking survive the data errors?" is the most original part of the plan, and nothing
  has been run yet.
- **Planned scenarios.** Each is labelled as a sensitivity scenario, not replacement data, and each needs your
  agreement before it runs. **(decide)**
  - P2 undercount (B2);
  - left-turn undercount (B1);
  - right turns (B5);
  - platoon arrivals from the green wave (B4).
- **Next step.** After the midterm. Fix the scenario definitions in a design document before running, as with
  `METHODS.md`.
- **Resolution.**

### D4. There is no evaluation reward, by design
- [x] **Decision (2026-11-09).** Report delay, not RL reward, on the slides.
  - The reward differs between learners (v1 penalises halted vehicles, v2 the delay rate, v2f adds waiting time),
    so it is not comparable.
  - Rule controllers have no reward at all.
  - The training curves (`results/training_curves.csv`) cover the "did it learn" question.
- **Option.** A "minus total delay" reward-style figure can be made from the existing data.
- **Resolution.** Closed unless a reward figure is wanted.

---

## E. Housekeeping

### E1. Project notes are out of date
- [ ] **Problem.** `CLAUDE.md` and `lastchat.md` still describe the old goal (the Sahachaiseree spillover
  extension) and the old `rlagent/` work. They do not describe the methods comparison in `atsc/`.
- **Next step.** Update `CLAUDE.md`'s status section and retire `lastchat.md`.
- **Resolution.**

### E2. Work is uncommitted or unpushed
- [ ] **Problem.**
  - The seed 2–3 evaluation rows (`eval/hour_mv.csv`, `eval/mech.csv`) and the DQN training logs and weights
    (`learners/dqn/`) are not committed.
  - 26 local commits have not been pushed. **(decide)**
  - Other uncommitted changes are yours: `VIEWING_SIM.md`, the neighbour folders under `intersections/`,
    `intersections/counts_index.csv`, a timestamp-only change in `sumotwin/7065_ext.net.xml`, and
    `PresentationSlidesTemplate.pdf`.
- **Next step.** Commit the evaluation data and DQN outputs after A1. Push when you say so.
- **Resolution.**
