# SIG 7065 simulation validation (Phase 1.6)

**Criteria written 2026-10-30, before any validation run.** They are fixed here and committed first; results are added below them without changing them.

## Setup

- **Days:** validation weekdays (Sep 1 – Oct 3, complete or usable, not Labor Day). Calibration (1.5) and any controller-parameter fit used train days only.
- **Simulation:** full day 00:00–24:00 on the calibrated site (`sim.json`). Controller: GDOT's own time-of-day plans on the NEMA engine, with gap-out on the field-style detectors (passage time fitted on train days, see "Passage time" below).
- **Field reference:** GDOT's per-plan Split Monitor statistics (`intersections/7065/timing/splitstats_7065.csv`, read by `tools/atspm_splitstats.py`): average split, % gap-outs, % force-offs (incl. max-outs), % skips per phase and plan band. Only bands that pass the reader's checksum (percentages sum to 100 ± 0.5) are used.
- **Simulated equivalents**, per phase and plan band (same band times as the field chart):
  - split = green + yellow + red clearance of each served phase;
  - gap % / force % / skip % = share of cycles in which the phase gapped out / was forced off or maxed out / was not served.

## Pass criteria

Phases 1, 3, 4, 5, 7, 8 (the non-coordinated phases, whose timing depends on traffic) × plans A, B, C, D and E (weekday plans). A pair is checked only when the field has a checked reading on at least 5 validation days.

| # | Quantity | A pair passes when | Criterion passes when |
|---|---|---|---|
| V1 | average split | \|median over days of (sim − field)\| ≤ 3 s | ≥ 80 % of pairs pass and no pair is off by more than 6 s |
| V2 | % gap-outs | \|median over days of (sim − field)\| ≤ 15 points | ≥ 80 % of pairs pass and no pair is off by more than 30 points |
| V3 | % skips | \|median over days of (sim − field)\| ≤ 15 points | ≥ 80 % of pairs pass |
| V4 | P8 discharge (critical movement, out of sample) | — | sim median P8 served per lane of nominal green over plan-C quarters within ± 5 % of the field median on the same days |
| V5 | health | — | 0 teleports; PM P8-through overflow (mean delay > 100 s) only on days with flagged count bins, plus at most 2 other days |

Coordinated phases 2 and 6 are reported but not scored (their split is set by the plan and the other phases' gap-outs).

The simulation is accepted as the base for Phase 2 if V1, V2, V4 and V5 pass. V3 is reported. A failed criterion is reported as failed, diagnosed, and fixed only with a change justified independently of the validation numbers (then rerun and reported as a second attempt, never replacing the first).

## Passage time (fitted on train days, before validation)

GDOT's passage (gap) time is not published. It is chosen on **train** weekdays from {1.0, 1.5, 2.0, 2.5, 3.0, 4.0} s as the value with the smallest mean \|sim − field\| % gap-outs over the scored phase-plan pairs, and is then fixed for validation.

### Amendment, 2026-10-30, before any validation run

The train-day fit above gave errors of 36–52 gap-out points at every passage value, decreasing towards the grid edge. On train days the field shows behaviour no single passage time can produce: P4, P7, P8 are forced off in 90–100 % of cycles in plans A–C and never skipped, P7 with only ~40 veh/h, while the same P4/P8 gap out 90–94 % of the time at night (plan E). That is **max recall** in the daytime plans, a controller setting GDOT does not publish. The controller fit is therefore extended, still on **train days only**:

1. **Max recall** in a plan for a scored phase whose train-day median force-off share is ≥ 90 % and median skip share ≤ 1 % (result: P4, P7, P8 in plans A, B, C).
2. **Passage time per phase** (the others), from {2, 3, 4, 6, 8} s, minimising the phase's mean \|sim − field\| % gap-outs over its actuated plans (tie: split).

Both are stored in `sim.json` (`controller`) and used unchanged for validation. The 1-s-grid fit is kept in the history as the first attempt.

## Results — attempt 1 (2026-10-30)

Controller settings fitted on train days (`sim.json` → `controller`): max recall P4, P7, P8 in plans A–C; passage P1 8, P3 8, P4 8, P5 8, P7 6, P8 4 s (`validation/passage_fit.csv`). The left-turn fits sit at the edge of the grid (8 s) and still miss by 26–42 gap-out points on train days.

Scoring fix applied after the run (`validate.py compare`): bands where the field never served the phase (skip 100 %, e.g. P3/P7 in night plan E) have no average split (the chart prints 0.0); the first scoring compared them as 0 s. Raw first scoring: `validation/score_attempt1_raw.md` (V1 19/30, worst 16.1 s: the same verdicts).

| Phase | Plan | days | avg split sim − field (s) | % gap-outs sim − field | % skips sim − field |
|---|---|---|---|---|---|
| P1 | A | 24 | +0.7 | +23 | +0 |
| P1 | B | 38 | +0.7 | +24 | +0 |
| P1 | C | 21 | +0.6 | +40 | +0 |
| P1 | D | 18 | +0.5 | +34 | +0 |
| P1 | E | 39 | +0.2 | -1 | +3 |
| P3 | A | 19 | -0.2 | +28 | +8 |
| P3 | B | 38 | -3.4 | +54 | +11 |
| P3 | C | 22 | -5.0 | +60 | +14 |
| P3 | D | 22 | -0.5 | -18 | +6 |
| P3 | E | 51 | — | +0 | +0 |
| P4 | A | 24 | -0.1 | +0 | +0 |
| P4 | B | 37 | +3.8 | +0 | +0 |
| P4 | C | 23 | +6.7 | +0 | +0 |
| P4 | D | 23 | +0.2 | +18 | +0 |
| P4 | E | 50 | +2.5 | -13 | +0 |
| P5 | A | 24 | -4.8 | +22 | +1 |
| P5 | B | 33 | -7.7 | +29 | -2 |
| P5 | C | 18 | -10.1 | +39 | -1 |
| P5 | D | 22 | -3.3 | +21 | +0 |
| P5 | E | 49 | +1.1 | -4 | +0 |
| P7 | A | 18 | -1.3 | +0 | +25 |
| P7 | B | 38 | -1.0 | -9 | +23 |
| P7 | C | 23 | -0.9 | -4 | +23 |
| P7 | D | 19 | -1.1 | +12 | +19 |
| P7 | E | 51 | — | +0 | +0 |
| P8 | A | 24 | +3.1 | +0 | +0 |
| P8 | B | 37 | +2.4 | +0 | +0 |
| P8 | C | 22 | +2.9 | +0 | +0 |
| P8 | D | 23 | +2.8 | -4 | +0 |
| P8 | E | 51 | +2.5 | -9 | +0 |

- **V1 average split:** 19/28 pairs within 3 s, worst 10.1 s → **FAIL**
- **V2 % gap-outs:** 17/30 pairs within 15 points, worst 60 → **FAIL**
- **V3 % skips:** 26/30 pairs within 15 points → **PASS** (reported)
- **V4 P8 discharge:** sim median 1952 vs field 1934 veh/h per lane of nominal green (+1.0 %) → **PASS**
- **V5 health:** 0 teleports; overflow days outside flagged days: 2026-09-14, 2026-09-23, 2026-09-28 → **FAIL**

**Verdict: not accepted yet.** V3 and V4 pass, V1, V2 and V5 fail.

### Diagnosis

- **What holds:** the critical movement's capacity, out of sample (V4, +1.0 %); the coordinated structure (P2/P6, cycle, force-offs); the Piedmont phases' behaviour (P4, P7, P8: termination within 0–18 points, split within ≈ 3 s, except P4 in B/C, which inherits time the simulated P3 leaves unused).
- **What fails: the left-turn phases.** In the simulation P3 and P5 end 3–10 s earlier than in the field, and gap out 20–60 points more often (V1, V2). The counted demand explains P3 but not P5:
  - P3 (Piedmont-N left, 1 lane): the field serves ≈ 6 vehicles per green at 2.2–2.8 s each, close to saturation, so it is forced off. The simulation serves more of them permissively during P4 (flashing yellow arrow), so fewer queue for P3. Suspect: simulated permissive gap acceptance too generous.
  - P5 (Peachtree-NE dual left): the field gives 20–30 s of green, with 54–72 % gap-outs, to 3–5 counted vehicles per lane per cycle. Under gap-out logic on the counted demand that is not reachable with any passage time. Candidates, none observable in the published data: unpublished detector extend/delay timers, unequal use of the two left lanes, or left-turn undercounting by the stop-bar radar (one zone both counts and holds the call, and a dense discharge can read as fewer vehicles).
  - P1's split matches (it lags P2 and rests to its force-off anyway); its termination label does not (field forced off 23–77 %, simulation mostly gaps out first).
- **V5:** three validation days outside the flagged set overflow on the Piedmont-N through (Sep 14, 23, 28). Sep 23 has an 18:05–18:10 burst just under the physical bound (`intersections/7065/timing/capacity_check/README.md`); the other two are to be examined.
- **Consequence for Phase 2 until fixed:** with left phases ending early, the coordinated phases inherit time in the simulation that they do not get in the field, so the simulated GDOT controller is somewhat optimistic. Any controller comparison run before attempt 2 is preliminary and says so.

### Next (attempt 2, justified independently of these numbers)

1. Permissive left-turn gap acceptance (SUMO junction model parameters for FYA turns), checked against P3's field termination on train days.
2. P5: test the dual-left lane-use and undercount hypotheses with the Timing & Actuation charts (per-lane presence vs. counts, Oct 2 08:00 window).
3. V5 days: inspect the Sep 14 and Sep 28 PM counts.

