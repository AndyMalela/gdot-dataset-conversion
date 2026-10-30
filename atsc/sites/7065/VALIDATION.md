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

## Results

(not run yet)
