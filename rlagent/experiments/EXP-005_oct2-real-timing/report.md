# EXP-005 — 7065 on the newer data (2026-10-02): RL vs real GDOT timing vs Webster vs tuned-actuated

**Date:** 2026-10-05. **Status:** ⚠️ Preliminary, single run. Current numbers: §2e (v6, extended twin). An independent review (below,
§7) lists what these numbers do and don't support — read it before citing them.

## 1. Setup

One run per controller (no seeds, no CI), **1.0× = the measured Oct 2 demand, unscaled**.

| Item | Value |
|---|---|
| Network | `sumotwin/7065.net.xml` (hand-built twin), same for all |
| Demand | `intersections/7065/sim/demand.rou.xml`: measured 5-min counts per movement, Oct 2 (47,149 veh/day, 8,366 in 15:00–18:00); rights and uncounted movements = 0 (as before) |
| Run | full day, drain to 30 h, SUMO seed 9999, time-to-teleport 300 s |
| Metric | as EXP-002+: **total delay = timeLoss + departDelay** per trip, trips by intended departure in **15:00–18:00**; plus unserved vehicles (demand − completed trips) |
| Script / raw | `data/run_exp005.py`, `data/results.json`, `data/ti_*.xml`, `data/run.log` |

Days: **every controller is tested on Oct 2.** Webster and tuned-actuated are designed from Oct 2
counts, real timing from GDOT's Oct 2 plans and recorded signal data; **RL is the May-trained
EXP-004 policy, unchanged** (trained on May 5–7), so Oct 2 is a new held-out day for it. EXP-002–004
tested on May 8 with May-designed baselines — not directly comparable (different day, lighter peak).

Controllers:
- **Real GDOT timing** — calibrated SUMO NEMA actuated-coordinated controller built from GDOT's
  time-of-day plans and measured parameters (`intersections/7065/sim/README.md`; frozen copy
  `data/real_timing_7065.add.xml`). Matches GDOT's recorded greens within 5.9 s mean per phase on
  this twin. Uses GDOT's own phase configuration (protected + permissive lefts as configured).
- **Webster fixed-time** — `fixed_time.py`, plan recomputed from Oct 2 peak-hour counts:
  cycle 73.4 s, ρ = 0.564, greens [5.0, 19.6, 15.5, 19.8] s.
- **Tuned-actuated** — `actuated_baseline.py`, max greens = Webster × 1.25 = [8.0, 24.5, 19.4, 24.7] s.
- **RL** — EXP-004 deployed policy (S8, seed 4, `ci/race/ratemg/s4/weights_random_s4.npy`), trained on
  May days; Oct 2 is a new held-out day.

Webster, tuned-actuated and RL use the `stages.py` 4-stage model (both lefts protected every cycle);
real timing uses GDOT's NEMA phases. That difference is part of what is compared.

## 2. v2 results (superseded by §2b) — peak 15:00–18:00, uncalibrated drivers

| Controller | Total delay (s/veh) | Time loss (s) | Depart delay (s) | Unserved (day) |
|---|---:|---:|---:|---:|
| **RL (EXP-004 deployed)** | **19.5** | 19.1 | 0.4 | 0 |
| Webster fixed-time | 24.6 | 24.2 | 0.5 | 0 |
| Real GDOT timing (calibrated NEMA) | 133.3 | 49.1 | 84.3 | 0 |
| Tuned-actuated | 464.1 | 33.8 | 430.4 | 0 |

Whole day (all trips): RL 18.2, Webster 23.7, real 147.9 (v2), tuned-actuated 264.7 s/veh.

Real timing was re-run (v2, 2026-10-05) after fixing the night-plan detector bug (§3.3): unserved 143 → 0, peak unchanged (133.3 s). v1 files kept as `data/*_v1_nightbug.*`.

## 2e. v6 — extended twin with real approach lengths (CURRENT)

Setup audit (goal: every remaining gap must come from something deliberately not modelled — pedestrians, corridor coordination — never from a setup error). Found: the twin's approaches were far shorter than the real roads (Piedmont S 49 m vs 291 m, Piedmont N 45 m vs 230 m, Peachtree NE 80 m vs 194 m; OSM road length to the previous junction). Long-cycle queues spilled out of the network: vehicles couldn't enter (inflated depart delay) and entered only ~45 m from the stop line during green (lost capacity — why v4's real timing appeared unable to serve Piedmont EB's counted 1,006 veh/h). `sumotwin/7065_ext.net.xml` adds straight upstream segments (S +242 m, N +185 m, NE +114 m; lane count of the fed edge, so turn-lane storage is slightly overstated); junction J and its 19 signal links are identical, slip lane intact. The original twin file is untouched. The real-timing controller was recalibrated on it (median green error **3.5 s**, was 4.0). Script `data/run_exp005_v6.py`, raw `data/results_v6.json`.

| Controller | Night 00-06 | AM 06-10 | Midday 10-15 | PM peak 15-18 | Evening 18-24 | Whole day |
|---|---:|---:|---:|---:|---:|---:|
| *Demand (veh/h)* | 591 | 2087 | 2662 | 2789 | 2264 | 1965 |
| Webster (designed Sep 29) | 23.0 | 25.5 | 25.7 | 27.0 | 25.6 | 25.7 |
| Real GDOT timing | 32.3 | 45.7 | 48.9 | 69.7 | 50.6 | 51.2 |
| Old RL policy (reference; trained on rotated May demand, short twin) | 17.2 | 19.7 | 20.8 | 21.4 | 19.0 | 19.9 |

- Real timing: depart delay ≤ 7 s on every movement, every counted vehicle served in every period, 0 teleports / 0 collisions — the v4 'over capacity' finding was the short approaches. The remaining gap to Webster is in-network waiting (PM: lefts 52–81 s vs 17–29 s, Piedmont EB through 97 vs 21 s), the expected cost of 160–180 s coordinated cycles evaluated as an isolated intersection.
- The old RL policy's v4 collapse (PM 488 s) was also the short approaches (21.4 s here). It is still trained on rotated demand on the short twin; the retrained policies are EXP-006.
- Open audit items: out-of-sample validation of the real-timing controller; repeated random seeds; attribution of the remaining gap (pedestrian minimums for every controller; GDOT timing without coordination).

## 2d. v5 — Webster designed on a different day (superseded by §2e)

v4's Webster was designed from Oct 2's own counts and tested on Oct 2 (same-day foresight). v5 designs Webster on **Tue 2026-09-29** (busiest hour in 15:00–18:00, corrected mapping): cycle **81.0 s**, ρ = 0.605, greens [8.3, 13.3, 10.3, 35.1] s; tested on **Fri 2026-10-02** (unseen). Tuned-actuated is dropped from the comparison (not needed for now; its v5 run, tuned on Sep 29, is in `data/results_v5.json`). Real timing and the old RL policy are unchanged from v4. Script: `data/run_exp005_v5.py`; design-day demand: `data/design_0929/`.

| Controller | Night 00-06 | AM 06-10 | Midday 10-15 | PM peak 15-18 | Evening 18-24 | Whole day |
|---|---:|---:|---:|---:|---:|---:|
| *Demand (veh/h)* | 591 | 2087 | 2662 | 2789 | 2264 | 1965 |
| Webster (designed Sep 29) | 23.1 | 25.2 | 25.2 | 26.8 | 25.3 | 25.4 |
| Real GDOT timing | 31.6 | 45.2 | 49.7 | 185.7 | 143.6 | 98.7 |
| RL (EXP-004, trained on rotated May demand) | 19.1 | 20.2 | 20.6 | 488.0 | 315.5 | 188.3 |

Designing Webster on Sep 29 instead of Oct 2 costs it 1.7 s/veh whole-day (25.4 vs 23.7): the same-day foresight was worth ~7%. The retrained RL (corrected demand, trained/validated on other days) is EXP-006.

## 2c. v4 results — corrected directions, Poisson arrivals, default drivers (short twin; superseded)

Supersedes §2b. Changes: (1) GDOT's count labels mapped to the right approaches — the report's EB/WB are Piedmont and NB/SB are Peachtree, verified from detector actuation counts (`intersections/7065/timing/phase_map.json` count_labels; every earlier 7065 demand file, incl. sumodemand's May files used for RL training, had the four directions rotated); (2) Poisson arrivals with the measured count per movement per 5-min bin; (3) SUMO default driver behaviour — the impatience workaround is dropped; (4) real-timing controller rebuilt and recalibrated on the corrected demand (median green error 4.0 s per phase, was 5.9). One run each. Raw: `data/results_v4.json` (incl. served-vs-counted per movement per period), `data/run_v4.log`, `data/run_exp005_v4.py`.

**Total delay per vehicle (s), by intended departure time:**

| Controller | Night 00-06 | AM 06-10 | Midday 10-15 | PM peak 15-18 | Evening 18-24 | Whole day |
|---|---:|---:|---:|---:|---:|---:|
| *Demand (veh/h)* | 591 | 2087 | 2662 | 2789 | 2264 | 1965 |
| Tuned-actuated | 17.3 | 20.3 | 21.5 | 22.6 | 20.5 | 20.9 |
| Webster fixed-time | 21.2 | 23.7 | 23.9 | 25.0 | 23.2 | 23.7 |
| Real GDOT timing | 31.6 | 45.2 | 49.7 | 185.7 | 143.6 | 98.7 |
| RL (EXP-004, trained on swapped demand) | 19.1 | 20.2 | 20.6 | 488.0 | 315.5 | 188.3 |

All four serve every vehicle by the end of the drain (0 unserved); real timing: 0 teleports, 0 collisions.

**Cycle length (s):**

| Controller | Night 00-06 | AM 06-10 | Midday 10-15 | PM peak 15-18 | Evening 18-24 |
|---|---:|---:|---:|---:|---:|
| Tuned-actuated | 47.0 | 53.2 | 58.8 | 62.9 | 54.9 |
| Webster fixed-time | 76.0 | 76.0 | 76.0 | 76.0 | 76.0 |
| Real GDOT timing | 120 (plan) | 120/160 (plan) | 160 (plan) | 160/180 (plan) | 120/130/180 (plan) |
| RL (EXP-004, trained on swapped demand) | 49.8 | 36.4 | 37.9 | 57.1 | 49.0 |

Webster: computed cycle **73.4 s**, ρ = 0.564, greens [7.8, 13.2, 9.0, 29.4] s, designed from the correctly mapped Oct 2 15:00–18:00 counts (design volumes {'eb_thru': 315, 'eb_left': 146, 'wb_thru': 676, 'wb_left': 265, 'nb_thru': 399, 'nb_left': 56, 'sb_thru': 1006, 'sb_left': 154}). Tuned-actuated: max greens = Webster × 1.25 (grid {'1.25': 20.9, '1.5': 21.0, '2.0': 21.1, '2.5': 21.1, '3.0': 21.1}).

What the numbers say:
- **The May-trained RL policy breaks on the correct demand pattern:** PM peak 488 s, almost all on Peachtree southbound (GDOT SB, twin NE approach: through depart delay ~1,760 s, left ~108 s). In training that approach carried Piedmont's light WB flows (direction swap), so the policy never learned to serve it. It is not a fair test of the method — it shows the old policy is tied to the wrong demand and must be retrained (separate experiment).
- **Tuned-actuated is now the best controller** (whole day 20.9 vs Webster 23.7 s; it beats Webster in every period).
- **Real timing's PM peak (186 s) is one movement at capacity:** Piedmont EB through (from the north, 1,006 veh/h on 2 through lanes) has ~395 s depart delay. GDOT's plan C gives it ~48 s of green per 180 s cycle, ≈ 960 veh/h of SUMO capacity — just below the counted volume, which did get through in reality. So the twin's capacity on that approach is slightly low (candidate causes: GDOT's detector list shows a lane 'R 3' there that may carry through traffic in reality; SUMO saturation flow). To calibrate before judging GDOT's timing. Isolation (no coordination credit, no pedestrians) still applies.

## 2b. v3 results — superseded by §2c (directions were rotated in this version)

All four controllers on the **same calibrated demand** (driver gap acceptance impatience = 1.0, `data/calib_gap.py`: the setting at which the NB left under real timing is served at its counted rate, 102%, instead of 95% with a 1,675 s queue). One run each. Raw: `data/results_v3.json`, `data/run_v3.log`, `data/run_exp005_v3.py`.

**Total delay per vehicle (s) = time loss + depart delay, by intended departure time:**

| Controller | Night 00-06 | AM 06-10 | Midday 10-15 | PM peak 15-18 | Evening 18-24 | Whole day |
|---|---:|---:|---:|---:|---:|---:|
| *Demand (veh/h)* | 591 | 2087 | 2662 | 2789 | 2264 | 1965 |
| RL (EXP-004 deployed) | 16.1 | 18.1 | 18.3 | 19.2 | 17.7 | 18.1 |
| Tuned-actuated (fixed detector) | 16.1 | 19.8 | 20.6 | 21.3 | 19.7 | 20.0 |
| Webster fixed-time | 21.5 | 23.4 | 24.1 | 24.6 | 23.4 | 23.6 |
| Real GDOT timing | 29.0 | 45.4 | 49.7 | 53.5 | 40.7 | 45.5 |

Unserved vehicles (whole day): 0 for all four.

**Cycle length (s):**

| Controller | Night 00-06 | AM 06-10 | Midday 10-15 | PM peak 15-18 | Evening 18-24 | Whole day |
|---|---:|---:|---:|---:|---:|---:|
| RL (EXP-004 deployed) | 47.8 | 37.8 | 38.2 | 41.8 | 37.8 | 40.5 |
| Tuned-actuated (fixed detector) | 47.2 | 52.3 | 56.9 | 61.5 | 53.2 | 53.0 |
| Webster fixed-time | 75.0 | 75.0 | 75.0 | 75.0 | 75.0 | 75.0 |
| Real GDOT timing ⚠ | 120 (plan) | 120/160 (plan) | 160 (plan) | 160/180 (plan) | 120/130/180 (plan) | 120/130/160/180 (plan) |

- **Webster:** computed cycle **73.4 s** (ρ = 0.564, greens [5.0, 19.6, 15.5, 19.8] s, designed on Oct 2 15:00–18:00); as run 75.0 s (each stage is held in whole seconds plus the env's stage clearances). Fixed all day.
- **Real timing:** the programmed cycle of the plan(s) in force (coordinated plans hold their cycle).
- **Tuned-actuated / RL:** measured mean time between starts of the first stage, per period.

Read with care:
- **Real timing — evening/night fixed (2026-10-05).** Two causes, both corrected and re-run: (1) Oct 2's timing schedule was missing at build time, so the build used May 6's (night = unverified plan F); Oct 2's Split Monitor is now read (identical schedule, plan E at night). (2) Plan E (21:45–06:15) has no protected Piedmont lefts, and SUMO's NEMA controller puts no detector on a permissive-only lane, so P4/P8 only got their minimum green (~6 s per 120 s cycle) and the lefts queued for hours (22–24 h delays of 2,000–8,500 s). GDOT's recorded greens at 22:30 Oct 2 show P4/P8 run 42.9 of 43.4 s (and the Split Monitor shows pedestrian activity on them every cycle), so P4/P8 in plan E are now on **max recall**. A long minimum green instead made SUMO skip the phase (tried, rejected). Evening by hour now 32–51 s, unserved 0. Random arrivals were also tested: they did not change the collapse (`data/randomize_demand.py`), so arrival spacing was not the cause.
- **Tuned-actuated was broken in v1/v2 (and in EXP-004):** `actuated_baseline.py` looked for vehicles 26–30 m upstream *on the last edge only*, but the twin's SB edge `N_near` is 14.6 m and WB edge `NE_in.79` is 6.2 m, so SB and WB traffic was never detected (SB through waited 2,288 s to enter). Fixed: distance measured to the stop line along the vehicle's path. Its max greens barely matter at this load (Webster × 1.25…3.0 all give 20.0–20.3 s whole-day), so ×1.25 is kept. **EXP-004's tuned-actuated numbers predate this fix** (legacy behaviour: `legacy_detector=True`).
- Oct 2 is a light day (whole-day mean 1,965 veh/h, PM peak 2,789); RL vs tuned-actuated is 18.1 vs 20.0 s whole-day, a small margin at low v/c.

## 3. Read with care — what these numbers do and don't show

1. **Oct 2 is a light day at 7065's PM peak.** Peak-hour EB through = **1,006 veh/h** vs **2,105** on
   May 8 (same daily total, ~47–52k). The intersection is far from saturation (Webster ρ = 0.56),
   so this is a low-v/c test — exactly where RL beat Webster before (EXP-003/004 at 0.5×).
   RL −21% vs Webster here is consistent with that, not evidence for the high-saturation goal.
2. **Real timing's 133 s is almost entirely one movement:** Piedmont NB left (P7) has a mean
   **depart delay of 1,675 s** in the peak; every other movement is 0–16 s. GDOT gives that left a
   short protected phase (15 s split, ~9 s recorded green per 180 s cycle) plus a permissive arrow.
   In reality that serves the counted 146 veh/h; in SUMO permissive left-turners accept few gaps in
   the opposing 676 veh/h, so the queue spills back to the entry. **This is a SUMO
   permissive-left modelling limit, not a measured property of GDOT's timing** — a served-volume
   check (simulated vs counted veh/h per movement) should gate any real-timing comparison.
3. **The 143 unserved vehicles in v1** (Piedmont lefts, 23:00–24:00) were a controller-build bug,
   fixed and re-run (v2: 0 unserved): GDOT's night plan omits the protected Piedmont lefts, SUMO's
   NEMA controller generates no detector on a permissive-only lane, so those lefts couldn't call
   their phase. Fix = min recall on that phase in such plans (`tools/build_sim.py`).
4. **Tuned-actuated's 464 s is a baseline-construction artifact:** its max greens are Webster ×
   1.25, and Oct 2's light-day Webster cycle (73 s) caps phase 0 at 8 s, starving it at the peak.
   On May demand Webster's greens were larger. Retune (e.g. from the peak plan, or GDOT's splits)
   before comparing.
5. **Isolated intersection.** GDOT's 160/180 s cycles serve SR 237 corridor coordination (7065,
   7130 and 7431 switch plans at the same times). An isolated model gives coordination no credit,
   so long-cycle real timing is structurally penalised here.

## 4. Note — RL demand scaling to be tested

The past results scale demand with SUMO `--scale` (random duplication/thinning of vehicles,
uniform across movements and bins). We will test whether it does what it should:
realised vs nominal vehicles per scale; volume/capacity per approach with corrected lanes
(the twin's EB through is likely 3 lanes vs ~2 real); and whether the delay metric hides
insertion backlog at high scales. Also: the May "1.0×" and Oct 2 "1.0×" are very different loads
(§3.1), so a scale factor alone does not define the test condition — report v/c alongside it.

## 5. Next

- Served-volume check per movement for every controller (simulated vs counted veh/h).
- Calibrate SUMO's permissive-left gap acceptance (junction model) against the counted left
  volumes, then re-run real timing.
- Retune the tuned-actuated baseline for the test day.
- Then the decisive test at higher load (the scaling check first).

## 7. Independent review (2026-10-05) — what is and isn't supported

A separate sceptical review of this experiment (read-only, all files) concluded:

**Supported:** RL ≈ tuned-actuated < Webster at low v/c on this twin (one run, one day; RL's whole
margin over tuned-actuated comes from Piedmont, on Peachtree through it is worse); the May-trained
policy transfers to Oct 2 without retuning; the actuated-baseline detector bug was real, and
EXP-004's actuated numbers are invalid until re-run.

**Not supported:** "RL beats the real GDOT timing" (the isolated model gives coordination no credit,
has no pedestrians, and permissive lefts needed workarounds); "RL beats a properly tuned actuated
controller" (only max greens were varied, and they don't matter at this load; min green and gap were
not tuned); any high-saturation claim; "the real-timing model is validated" (fitted and checked on
the same 16 phase medians, fitted values at grid edges, done before the impatience change; no
throughput/queue/delay validation); impatience = 1.0 as a calibration (post-hoc, grid edge);
EXP-004's "beats every baseline" (only the Webster comparison survives).

**Highest-priority open check — possible direction mislabel.** GDOT's phase titles call Peachtree
"NB/SB" and Piedmont "EB/WB"; the demand assumes the count report's EB/WB are compass directions
(EB = Peachtree). Recorded left-turn greens fit the counts far better under GDOT's labels (P5 runs
20–29 s: 46–64 veh/h under the current mapping vs 156–256 under GDOT's; P7 runs its 8.8 s minimum:
122–161 vs 46–64). CLAUDE.md's own note blames the EB-through lane mismatch on the SR 237
(Piedmont) widening, which only makes sense if "EB" is on Piedmont. If confirmed, every 7065 demand
file in the project (May and Oct) has movements on the wrong approaches. To be settled from GDOT's
detector labels before further experiments.

**Pedestrians** (added after the review, from the Oct 2 Split Monitor with ped activity shown):
pedestrian calls hold P2/P4/P6/P8 open for ~34–48 s in most cycles. No controller in this
experiment models pedestrians; RL's 38–42 s cycles may be infeasible with real pedestrian demand.
