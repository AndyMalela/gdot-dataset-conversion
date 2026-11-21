# SIG 137 simulation validation: GDOT timing against GDOT's own statistics

**Criteria written 2026-11-16 07:00, before any validation run.** Carried over from 7065's `VALIDATION.md`
(2026-10-30) unchanged, except V4 and V5 (site-specific, see below). Results are added below without changing them.
Note: the 137 methods evaluation (`eval/report.md`) was run *before* this validation; its actuated and GDOT-plan
rows use the controller settings validated here.

## Setup

- **Days:** validation weekdays 2026-04-20..05-15 (complete or usable, `split.json`). The locked test set is not used.
- **Simulation:** full day 00:00–24:00 on the site as evaluated (`sim.json`): GDOT's dated time-of-day plans on the
  NEMA engine, gap-out on the model's detectors, passage times and max recall as in `sim.json` → `controller`.
- **Field reference:** GDOT's per-plan Split Monitor statistics (`intersections/137/timing/splitstats_137.csv`, read
  by `tools/atspm_splitstats.py`, test days excluded): average split, % gap-outs, % force-offs (incl. max-outs),
  % skips per phase and plan band; only bands whose percentages sum to 100 ± 0.5.
- **Simulated equivalents** per phase and band, as at 7065 (`atsc/sim/metrics.py`).

## Pass criteria

Phases 1, 3, 4, 5, 7, 8 (non-coordinated) × weekday plans A–G. A pair is checked only when the field has a checked
reading on at least 5 validation days.

| # | Quantity | A pair passes when | Criterion passes when |
|---|---|---|---|
| V1 | average split | \|median over days of (sim − field)\| ≤ 3 s | ≥ 80 % of pairs pass and no pair is off by more than 6 s |
| V2 | % gap-outs | \|median over days of (sim − field)\| ≤ 15 points | ≥ 80 % of pairs pass and no pair is off by more than 30 points |
| V3 | % skips | \|median over days of (sim − field)\| ≤ 15 points | ≥ 80 % of pairs pass (reported) |
| V4 | (7065: P8 discharge) | — | **not defined for 137** (no calibrated critical movement); reported as not applicable |
| V5 | health | — | 0 teleports; PM (15:30–19:00) mean delay of W Paces Ferry through (EB_TR, WB_TR) > 100 s on at most 2 days |

Coordinated phases 2 and 6 are reported but not scored. The simulation is accepted if V1, V2 and V5 pass.

**Attempt 1** uses the settings as evaluated: passage 4 s through / 3 s left (old pipeline's fit to the recorded
greens of 2026-10-02 on an earlier network), max recall per plan where GDOT's own termination share shows < 5 %
gap-outs (`make_signal.py`). They were **not** fitted on train days as 7065's were. If attempt 1 fails, attempt 2 fits
them on train days with 7065's rule (max recall: train-day median force-off ≥ 90 % and skip ≤ 1 %; passage per phase
from {2, 3, 4, 6, 8} s minimising |sim − field| % gap-outs), then reruns validation and the methods evaluation.
Attempt 1 stays in the record.

## Results — attempt 1

Run 2026-11-16 07:27 (`validation/attempt1/`), settings `validation/attempt1/sim_attempt1.json`.

| Phase | Plan | days | avg split sim − field (s) | % gap-outs sim − field | % skips sim − field |
|---|---|---|---|---|---|
| P1 | A | 6 | -2.1 | +25 | -16 |
| P1 | B | 7 | -1.8 | +35 | -17 |
| P1 | C | 7 | -2.1 | +38 | +0 |
| P1 | D | 7 | -1.6 | +27 | -22 |
| P1 | E | 42 | -3.2 | +28 | -12 |
| P1 | G | 5 | +10.7 | -1 | +20 |
| P3 | A | 6 | -2.3 | +45 | -5 |
| P3 | B | 6 | +0.7 | -10 | -3 |
| P3 | C | 5 | -1.3 | +48 | -5 |
| P3 | D | 7 | +0.1 | +50 | -18 |
| P3 | E | 31 | -3.7 | +40 | -5 |
| P4 | A | 8 | -7.1 | +10 | +2 |
| P4 | B | 8 | -7.0 | +35 | -1 |
| P4 | C | 7 | -9.9 | +11 | +3 |
| P4 | D | 8 | -2.5 | -8 | +9 |
| P4 | E | 36 | -8.8 | +20 | +0 |
| P4 | G | 5 | -5.5 | +30 | +4 |
| P5 | A | 8 | -1.1 | +32 | -4 |
| P5 | B | 7 | -1.2 | +38 | +9 |
| P5 | C | 7 | -0.7 | +42 | -2 |
| P5 | D | 7 | +0.0 | +29 | -10 |
| P5 | E | 39 | -2.5 | +30 | +2 |
| P5 | G | 8 | +11.2 | -3 | +12 |
| P7 | A | 8 | +0.5 | +32 | -27 |
| P7 | B | 5 | +0.7 | +30 | -15 |
| P7 | C | 7 | -0.8 | +23 | -10 |
| P7 | D | 7 | -0.3 | +56 | -36 |
| P7 | E | 35 | -0.6 | +29 | -16 |
| P7 | G | 5 | +4.6 | -1 | -29 |
| P8 | A | 9 | -8.4 | -9 | +18 |
| P8 | B | 8 | -6.9 | +22 | +11 |
| P8 | C | 8 | -10.6 | +2 | +9 |
| P8 | D | 8 | -5.3 | -18 | +20 |
| P8 | E | 41 | -12.1 | +9 | +7 |
| P8 | G | 10 | -7.8 | +11 | +3 |

- **V1 average split:** 19/35 pairs within 3 s, worst 12.1 s → **FAIL**
- **V2 % gap-outs:** 11/35 pairs within 15 points, worst 56 → **FAIL**
- **V3 % skips:** 24/35 pairs within 15 points → **FAIL** (reported)
- **V4:** not defined for 137 (VALIDATION.md)
- **V5 health:** 0 teleports; days with W Paces Ferry through PM delay > 100 s: none → **PASS**

**Accepted (V1, V2, V5):** NO

**Diagnosis (before attempt 2).** One direction throughout: the simulated controller ends greens earlier than the
field's. Left phases (P1, P3, P5, P7) gap out 25–56 points more often than in the field; the side-street throughs
(P4, P8) get 5–12 s shorter splits. Consistent with passage times that are too short for this site (they were fitted
to one day on an earlier network), and possibly with the uncalibrated driver model discharging faster than the field.
Skips go the other way for the lefts (the simulation serves P1/P7 more often than the field), which a passage time
cannot fix: GDOT may use detector delay on the left-turn zones (common with flashing yellow arrows); not published.
Next: attempt 2 as registered above (train-day fit of max recall and passage per phase).

## Results — attempt 2

Run 2026-11-16 07:29–08:00 (`validation/attempt2/`, fit `validation/attempt2/passage_fit.csv`, settings
`validation/attempt2/sim_attempt2.json`). Train-day fit: **no phase meets the max-recall rule** (max recall dropped);
**passage 8 s for every scored phase, the edge of the grid** (P2/P6 fall back to the 2 s default when fully actuated).

| Phase | Plan | days | avg split sim − field (s) | % gap-outs sim − field | % skips sim − field |
|---|---|---|---|---|---|
| P1 | A | 6 | +2.7 | +22 | -19 |
| P1 | B | 7 | +2.3 | +17 | -17 |
| P1 | C | 7 | +3.3 | +39 | -5 |
| P1 | D | 7 | +3.1 | +26 | -29 |
| P1 | E | 42 | +2.1 | +31 | -16 |
| P1 | G | 5 | +4.8 | +39 | +21 |
| P3 | A | 6 | +0.9 | +2 | -6 |
| P3 | B | 6 | +0.2 | -2 | -1 |
| P3 | C | 5 | +1.2 | +1 | -4 |
| P3 | D | 7 | +3.6 | +18 | -12 |
| P3 | E | 31 | +0.9 | +9 | -5 |
| P4 | A | 8 | -3.1 | +7 | +4 |
| P4 | B | 8 | -2.3 | +22 | -0 |
| P4 | C | 7 | -5.5 | +10 | +3 |
| P4 | D | 8 | +1.2 | -6 | +5 |
| P4 | E | 36 | -4.1 | +17 | +0 |
| P4 | G | 5 | -4.6 | +22 | +11 |
| P5 | A | 8 | +4.0 | +27 | -9 |
| P5 | B | 7 | +3.2 | +21 | -1 |
| P5 | C | 7 | +4.1 | +40 | -9 |
| P5 | D | 7 | +4.3 | +28 | -13 |
| P5 | E | 39 | +3.1 | +27 | +2 |
| P5 | G | 8 | +5.5 | +44 | +16 |
| P7 | A | 8 | +2.7 | +0 | -26 |
| P7 | B | 5 | +2.2 | -5 | -15 |
| P7 | C | 7 | +0.8 | -1 | -6 |
| P7 | D | 7 | +3.5 | +36 | -36 |
| P7 | E | 35 | +2.5 | -11 | -15 |
| P7 | G | 5 | +1.4 | +26 | -29 |
| P8 | A | 9 | -3.6 | -7 | +17 |
| P8 | B | 8 | -4.1 | +11 | +9 |
| P8 | C | 8 | -5.3 | +1 | +7 |
| P8 | D | 8 | -1.9 | -19 | +20 |
| P8 | E | 41 | -7.0 | +8 | +6 |
| P8 | G | 10 | -6.0 | +5 | +12 |

- **V1 average split:** 15/35 pairs within 3 s, worst 7.0 s → **FAIL**
- **V2 % gap-outs:** 16/35 pairs within 15 points, worst 44 → **FAIL**
- **V3 % skips:** 23/35 pairs within 15 points → **FAIL** (reported)
- **V4:** not defined for 137 (VALIDATION.md)
- **V5 health:** 0 teleports; days with W Paces Ferry through PM delay > 100 s: none → **PASS**

**Accepted (V1, V2, V5):** NO

**Diagnosis.** The longer passage fixed the side-street lefts (P3, P7: gap-out error 6–9 points on train days) and
halved the worst split error (12.1 → 7.0 s), but two patterns remain that no passage time removes:
- **Main-street lefts P1, P5**: the simulation still gaps them out 17–44 points more often *and* now gives them 2–5 s
  longer splits, while serving them more often (skips 5–29 points lower). In the field these lefts are skipped more and,
  when served, run to their force-off. That is the signature of a call delay on the left-turn zones (a vehicle must wait
  some seconds before the phase is called), common with flashing yellow arrows. GDOT's configuration table publishes
  no movement delay for any 137 detector (`Move. Delay` empty, latency 0), so it cannot be set from the data.
- **Side-street throughs P4, P8**: splits still 2–7 s short with the passage at the grid edge, i.e. the simulated side
  street clears faster than the field's. Consistent with the driver model being uncalibrated (no Phase 1.5 discharge
  calibration was done for 137, unlike 7065).

Both registered attempts failed. **The 137 simulation is not accepted as validated.** Per the protocol, a further
attempt needs a change justified independently of these numbers; the candidate is the skipped step itself: discharge
calibration against field data (7065's Phase 1.5) before validation, not a new parameter tuned to the score.
`sim.json` is restored to the attempt-1 settings, which are the ones the methods evaluation in `eval/` used.

## Attempt 3 — registered 2026-11-16 08:20, before running

Changes, each from a GDOT measurement other than the validation statistics (train days only):

1. **Pedestrians** (48 Timing & Actuation windows, every hour 06–21 on 03-10, 03-24, 04-08; `make_signal.py` PED):
   main-street crossings (ped overlaps 2, 6) show a walk in every cycle of every window → P2, P6 on pedestrian
   recall, minimum = walk 4.0 s (assumed: not observable while resting in walk) + flashing don't walk 17.1 / 20.5 s;
   side-street crossings (overlaps 4, 8) are pushed 0–8 times an hour → P4, P8 pedestrian-actuated, minimum walk
   4.0 s + FDW 20.5 / 18.1 s when called, Poisson calls at the measured hourly rates (hours not measured → 0).
   Engine: `atsc/sim/nema.py` ped_actuated (backwards compatible; 7065's 16 tests pass).
2. **Discharge: checked, not changed.** No 137 movement is forced off in most cycles on train days (side-street
   throughs gap out 60–86 %), so the field never shows a capacity to calibrate against. Against the HCM base
   (1,900 veh/h/lane) the simulated E Andrews SB through lane discharges 1,650 veh/h/lane under a standing queue:
   slower, not faster, so calibrating toward HCM would shorten side-street greens further. No justified change.
3. Controller settings refitted on train days with the same rule as attempt 2 (pedestrians change the greens).

Expected (stated before running): pedestrians lengthen P4/P8 only in the ~5 % of cycles with a push, so they
cannot close most of the 2–7 s side-street split gap; the main-street left (P1/P5) pattern is untouched. A pass is
not expected; the attempt is run because the change is measured and belongs in the model either way.

## Results — attempt 3

Run 2026-11-16 08:22–08:55 (`validation/attempt3/`: score, fit, `sim_attempt3.json`, `signal_attempt3.json`).
Train-day refit: again no max recall, passage 8 s for every scored phase (grid edge).

| Phase | Plan | days | avg split sim − field (s) | % gap-outs sim − field | % skips sim − field |
|---|---|---|---|---|---|
| P1 | A | 6 | +2.7 | +20 | -17 |
| P1 | B | 7 | +1.9 | +12 | -21 |
| P1 | C | 7 | +3.2 | +38 | -9 |
| P1 | D | 7 | +3.3 | +31 | -34 |
| P1 | E | 42 | +2.2 | +30 | -18 |
| P1 | G | 5 | +4.5 | +32 | +27 |
| P3 | A | 6 | +0.6 | -2 | -5 |
| P3 | B | 6 | +0.1 | -1 | -1 |
| P3 | C | 5 | +1.3 | +1 | -4 |
| P3 | D | 7 | +3.5 | +22 | -15 |
| P3 | E | 31 | +0.8 | +7 | -4 |
| P4 | A | 8 | -2.2 | +7 | -1 |
| P4 | B | 8 | -1.6 | +17 | +0 |
| P4 | C | 7 | -4.5 | +12 | +1 |
| P4 | D | 8 | +1.1 | -3 | +5 |
| P4 | E | 36 | -2.9 | +18 | -0 |
| P4 | G | 5 | -3.5 | +22 | +11 |
| P5 | A | 8 | +3.4 | +23 | -6 |
| P5 | B | 7 | +2.2 | +11 | +4 |
| P5 | C | 7 | +3.5 | +43 | -6 |
| P5 | D | 7 | +3.7 | +24 | -9 |
| P5 | E | 39 | +2.3 | +25 | +2 |
| P5 | G | 8 | +4.6 | +33 | +23 |
| P7 | A | 8 | +2.5 | -0 | -25 |
| P7 | B | 5 | +2.0 | -1 | -16 |
| P7 | C | 7 | +0.9 | -4 | -9 |
| P7 | D | 7 | +3.3 | +34 | -35 |
| P7 | E | 35 | +2.6 | -10 | -15 |
| P7 | G | 5 | +1.7 | +24 | -26 |
| P8 | A | 9 | -2.7 | -7 | +18 |
| P8 | B | 8 | -3.2 | +11 | +10 |
| P8 | C | 8 | -4.3 | +3 | +6 |
| P8 | D | 8 | -2.1 | -18 | +17 |
| P8 | E | 41 | -5.9 | +9 | +7 |
| P8 | G | 10 | -5.1 | +5 | +10 |

- **V1 average split:** 20/35 pairs within 3 s, worst 5.9 s → **FAIL**
- **V2 % gap-outs:** 18/35 pairs within 15 points, worst 43 → **FAIL**
- **V3 % skips:** 21/35 pairs within 15 points → **FAIL** (reported)
- **V4:** not defined for 137 (VALIDATION.md)
- **V5 health:** 0 teleports; days with W Paces Ferry through PM delay > 100 s: none → **PASS**

**Accepted (V1, V2, V5):** NO

**Compared with attempt 2:** V1 15 → 20/35 pairs within 3 s and the worst split now 5.9 s (inside the 6 s cap);
V2 16 → 18/35. Passing needs 28/35 on both. The improvement is mostly P4/P8 splits (pedestrian calls) and is
smaller than the remaining misfit, as expected.

**What still fails, and the measurement that would explain it (not yet made):**
- Left-turn phases served too often (P1, P7 skipped 9–35 points less than in the field; P1, P5 gap out 11–43 points
  more). Consistent with a call delay on the left-turn zones, so left-turners that clear on the flashing yellow
  arrow never call the protected arrow. Measurable from Timing & Actuation detector events (detector on vs phase
  call), not from the configuration table (no delay published).
- Side-street through splits still 1.6–5.9 s short. Consistent with longer presence zones than the assumed 12 m
  (a longer zone keeps the phase extended). Measurable from detector occupancy times on the same charts.

**Current site configuration = attempt 3** (measured pedestrians, train-fitted 8 s passage). The methods evaluation
in `eval/`, the preliminary report and the demand sweep were produced with the **attempt-1** model (no pedestrians,
4/3 s passage); its files are kept in `validation/attempt1/` and must be cited as such.

## Finding 2026-11-16 09:30 — side-street and EB-left counts come from presence zones

While measuring the call handling (Timing & Actuation charts with detector occupancy and phase-call events 43/44,
`tools/lanecheck/tna_events.py`, train days):

- **Call handling matches the model**: a call registers when the stop-bar zone turns on and drops when it turns off
  (no delay, non-locking). The call-delay hypothesis for P1/P5 is refuted.
- **GDOT's report counts are detector-on events of the stop-bar presence zones.** On 03-10 07:30, 08:30 and 17:00 the
  report's 5-min SB_T, NB_T, NB_L, SB_L, EB_L, WB_L equal (±1–2) the number of zone activations in the chart, while
  single occupancies last 30–210 s and span whole greens (a discharging queue keeps the zone occupied, so several
  vehicles register as one). This is the defect found at 7065 on Peachtree (memory: 7065-peachtree-through-counts-
  presence-zones), on the same zone type ("Lane-by-lane Count; Stop Bar Presence", Wavetronix Matrix).
- At 137 that zone type counts **NB L/T/R, SB L/T/R and EB L**. Count-only zones: EB through (13769, 13775), WB left
  (13765); WB through is taken from 138. So the side-street demand in the model is a **lower bound in busy periods**,
  by an unknown factor; no other ATSPM zone measures the side streets.
- This explains the side-street splits being short in every attempt (less simulated side-street traffic than the
  field serves), and it is not fixable by a controller setting. It also affects the methods evaluation (side-street
  demand understated), not only validation.

## Attempt 4 — registered 2026-11-16 10:20, before running (user chose option 2, "estimate")

**Change: estimated side-street and EB-left demand** (`tools/lanecheck/estimate_137_presence.py`, applied by
`build_upstream_counts_137.py` → `intersections/137/counts/tmc_137_5min_estimated.csv`):
- Sample: Timing & Actuation charts with stop-bar zone occupancy, 5-min windows at 07:30, 08:30, 10:30, 12:30, 15:30,
  17:00, 18:30, 20:30 on 9 train days (03-03, 03-05, 03-10, 03-12, 03-18, 03-24, 03-31, 04-08, 04-14).
- Per activation: vehicles = 1 + floor((time occupied during the phase's own protected green − PASS) / H);
  H = 3600 / 1,900 s (HCM base); PASS = measured median time one free-moving vehicle occupies the zone. Permissive
  left turns and right turns on red count 1 per activation (they do not discharge at saturation): conservative.
- Per movement factor k = estimated / reported over the sample; applied to every daytime (06:00–22:00) bin of
  NB_L, NB_T, NB_R, SB_L, SB_T, SB_R, EB_L on all days (train and validation; the test set is not read); nights as
  reported. Stochastic rounding, seeded per bin. Sensitivity reported with H = 3600 / 1,650 s.
- Disclosed deviation: these columns are now model-based estimates, not GDOT's numbers.

Then, as in attempts 2–3: demand audit, Webster unchanged (methods only), controller settings refitted on train days
with the same rule, validation with the same criteria. A pass is possible but not expected with certainty: the
left-turn misfit (P1/P5) may also come from SUMO's permissive gap acceptance, which this change does not touch.
If it passes, the methods evaluation is rerun on this model.

## Results — attempt 4

Run 2026-11-16 10:12–10:38 (`validation/attempt4/`, `debug/validate_attempt4.log`). Factors from 72 windows on 9 train
days (H = 3600/1,900 s): EB_L 1.41, NB_T 1.46, SB_L 1.73, SB_T 2.29, NB_L 2.52, SB_R 2.72, NB_R 2.95 (1,650: 1.37–2.60).
Demand audit after the correction: 7 bins (≤ 0.25 % of any movement) above the physical bound. Train-day refit: no max
recall, passage 8 s (grid edge) again.

| Phase | Plan | days | avg split sim − field (s) | % gap-outs sim − field | % skips sim − field |
|---|---|---|---|---|---|
| P1 | A | 6 | +2.0 | +20 | -25 |
| P1 | B | 7 | +0.9 | -3 | -21 |
| P1 | C | 7 | +2.9 | +27 | -14 |
| P1 | D | 7 | +3.0 | +27 | -30 |
| P1 | E | 42 | +2.0 | +27 | -21 |
| P1 | G | 5 | +3.1 | +22 | +26 |
| P3 | A | 6 | -1.4 | +5 | -23 |
| P3 | B | 6 | -1.0 | +6 | -25 |
| P3 | C | 5 | -1.0 | +7 | -27 |
| P3 | D | 7 | +0.4 | +19 | -25 |
| P3 | E | 31 | -0.4 | -4 | -20 |
| P4 | A | 8 | -1.1 | +14 | -7 |
| P4 | B | 8 | -1.9 | +12 | -3 |
| P4 | C | 7 | -2.8 | +8 | -2 |
| P4 | D | 8 | +1.3 | +7 | -9 |
| P4 | E | 36 | -1.3 | +18 | -4 |
| P4 | G | 5 | -1.2 | +26 | -1 |
| P5 | A | 8 | +3.7 | +20 | -26 |
| P5 | B | 7 | +1.4 | -6 | -11 |
| P5 | C | 7 | +3.8 | +32 | -25 |
| P5 | D | 7 | +4.5 | +23 | -26 |
| P5 | E | 39 | +3.2 | +22 | -15 |
| P5 | G | 8 | +4.0 | +30 | +4 |
| P7 | A | 8 | +0.4 | -5 | -32 |
| P7 | B | 5 | -0.6 | -18 | -20 |
| P7 | C | 7 | -0.2 | -14 | -13 |
| P7 | D | 7 | +2.8 | +21 | -39 |
| P7 | E | 35 | +0.9 | -20 | -18 |
| P7 | G | 5 | -0.1 | +6 | -33 |
| P8 | A | 9 | -1.0 | -6 | +3 |
| P8 | B | 8 | -1.6 | -3 | -2 |
| P8 | C | 8 | -0.9 | +5 | -4 |
| P8 | D | 8 | -0.1 | -5 | +4 |
| P8 | E | 41 | -2.6 | +9 | -3 |
| P8 | G | 10 | -2.2 | +5 | -6 |

- **V1 average split:** 29/35 pairs within 3 s, worst 4.5 s → **PASS**
- **V2 % gap-outs:** 19/35 pairs within 15 points, worst 32 → **FAIL**
- **V3 % skips:** 16/35 pairs within 15 points → **FAIL** (reported)
- **V4:** not defined for 137 (VALIDATION.md)
- **V5 health:** 0 teleports; days with W Paces Ferry through PM delay > 100 s: none → **PASS**

**Accepted (V1, V2, V5):** NO

**V1 now passes** (29/35 within 3 s, worst 4.5 s, from 20/35 and 5.9 s): the side-street splits (P4, P8) match the
field once the presence-zone undercount is estimated, which supports that diagnosis. **V2 still fails** (19/35, worst
32 points). Every failing pair but three is a left-turn phase (P1, P5 gap out 20–32 points more than the field; P1,
P3, P5, P7 are skipped 13–39 points less). Pattern: the field serves its lefts less often but, when it does, runs them
to the force-off; the simulation serves short left queues almost every cycle and gaps them out. Consistent with more
left-turners clearing on the flashing yellow arrow in the field than in SUMO (permissive gap acceptance). Measurable
from the same detector-event charts: the share of left-zone activations that end during the opposing through green.

## Attempt 5 — registered 2026-11-16 11:24, before the calibration grid is run

**Target (field, independent of the validation statistics):** how left-turners leave the stop-bar zone, from the
72 detector-event windows on 9 train days (`tools/lanecheck/left_turn_clearance_137.py`). Activations ending during
the left's own arrow ("protected") vs during its permissive phase or the 6 s after it ("permissive"); activations
ending at other times ("other", 20–49 % in the field, ~2 % in the simulation: most likely the radar dropping a
stationary vehicle for a moment) are left out of the share. Permissive share = permissive / (protected + permissive):

| left turn | field | simulation, attempt-4 model |
|---|---|---|
| WB_L (P1) | 0.89 | 0.67 |
| EB_L (P5) | 0.85 | 0.72 |
| NB_L (P3) | 0.49 | 0.35 |
| SB_L (P7) | 0.61 | 0.44 |

Every left clears permissively more often in the field than in SUMO: the attempt-4 diagnosis, now measured.

**Calibration (train days, same windows):** SUMO's junction-model parameters for vehicles yielding on a permissive
movement, one vehicle type for all: `jmTimegapMinor` (accepted time gap, default 1 s) and `impatience` (default 0),
grid {default; jmTimegapMinor 0.5; impatience 0.5; impatience 1.0; jmTimegapMinor 0.5 + impatience 0.5}.
**Rule (fixed now):** the setting with the smallest mean |sim − field| permissive share over the four lefts; a tie
(within 0.02) goes to the smaller change from default. Then, as before: controller refit on train days, validation
with the same criteria; methods evaluation rerun on the result whether or not it passes, labelled accordingly.

### Attempt 5 calibration result (2026-11-16 11:29)

| setting | WB_L | EB_L | NB_L | SB_L | mean abs diff |
|---|---|---|---|---|---|
| **impatience 0.5 (chosen by the rule)** | 0.66 | 0.71 | 0.39 | 0.54 | **0.135** |
| impatience 1.0 | 0.67 | 0.71 | 0.38 | 0.53 | 0.139 |
| jmTimegapMinor 0.5 + impatience 0.5 | 0.67 | 0.71 | 0.36 | 0.49 | 0.152 |
| jmTimegapMinor 0.5 | 0.67 | 0.72 | 0.35 | 0.45 | 0.164 |
| default | 0.67 | 0.72 | 0.35 | 0.44 | 0.167 |
| field | 0.89 | 0.85 | 0.49 | 0.61 | |

The driver parameters move the side-street lefts a little and the main-street lefts (WB, EB) not at all: the gap is
not how SUMO drivers accept gaps but how many gaps there are. Probable cause: opposing W Paces Ferry traffic arrives
at random in the model, but in platoons released by signal 138 (~260 m) in the field, leaving gaps between platoons
for permissive turns (limitation 7 of README.md, now with a measured effect). Both 137 and 138 publish the Purdue
Coordination Diagram, so arrival platoons and the 137–138 offset are measurable: the candidate for attempt 6 is to
run 138 under its own timing upstream instead of random arrivals. Attempt 5 continues as registered (impatience 0.5).

## Results — attempt 5

Run 2026-11-16 11:30–11:41 (`validation/attempt5/`), vtype impatience 0.5, controller refit on train days.

| Phase | Plan | days | avg split sim − field (s) | % gap-outs sim − field | % skips sim − field |
|---|---|---|---|---|---|
| P1 | A | 6 | +2.2 | +19 | -24 |
| P1 | B | 7 | +0.9 | -6 | -19 |
| P1 | C | 7 | +3.0 | +29 | -9 |
| P1 | D | 7 | +3.1 | +27 | -32 |
| P1 | E | 42 | +1.8 | +26 | -22 |
| P1 | G | 5 | +3.0 | +22 | +23 |
| P3 | A | 6 | -1.4 | +7 | -22 |
| P3 | B | 6 | -0.8 | +8 | -23 |
| P3 | C | 5 | -1.0 | +7 | -23 |
| P3 | D | 7 | +0.4 | +22 | -25 |
| P3 | E | 31 | -0.6 | -2 | -20 |
| P4 | A | 8 | -1.0 | +13 | -8 |
| P4 | B | 8 | -1.6 | +5 | -4 |
| P4 | C | 7 | -2.7 | +13 | -2 |
| P4 | D | 8 | +1.8 | +7 | -8 |
| P4 | E | 36 | -2.3 | +17 | -4 |
| P4 | G | 5 | -1.3 | +28 | +0 |
| P5 | A | 8 | +3.3 | +23 | -23 |
| P5 | B | 7 | +1.5 | -6 | -7 |
| P5 | C | 7 | +3.8 | +34 | -23 |
| P5 | D | 7 | +3.9 | +28 | -23 |
| P5 | E | 39 | +3.2 | +22 | -13 |
| P5 | G | 8 | +3.5 | +29 | +4 |
| P7 | A | 8 | +1.2 | -0 | -30 |
| P7 | B | 5 | -0.2 | -12 | -18 |
| P7 | C | 7 | +0.0 | -9 | -12 |
| P7 | D | 7 | +3.1 | +20 | -39 |
| P7 | E | 35 | +1.5 | -16 | -19 |
| P7 | G | 5 | -0.3 | +11 | -32 |
| P8 | A | 9 | -1.2 | -2 | +4 |
| P8 | B | 8 | -1.3 | -1 | -2 |
| P8 | C | 8 | -1.3 | +3 | -4 |
| P8 | D | 8 | -0.4 | -4 | +4 |
| P8 | E | 41 | -3.0 | +11 | -2 |
| P8 | G | 10 | -2.2 | +1 | -4 |

- **V1 average split:** 27/35 pairs within 3 s, worst 3.9 s → **FAIL**
- **V2 % gap-outs:** 20/35 pairs within 15 points, worst 34 → **FAIL**
- **V3 % skips:** 17/35 pairs within 15 points → **FAIL** (reported)
- **V4:** not defined for 137 (VALIDATION.md)
- **V5 health:** 0 teleports; days with W Paces Ferry through PM delay > 100 s: none → **PASS**

**Accepted (V1, V2, V5):** NO

Against attempt 4: V1 29 → 27/35 (one pair short of the 28 needed; worst 4.5 → 3.9 s), V2 19 → 20/35. The calibration
shifted the left-turn phases slightly but cannot create the gaps that platooned arrivals give in the field (see the
calibration result above). **Not accepted.** Next registered candidate: attempt 6, signal 138 upstream under its own
timing, offset from the Purdue Coordination Diagram. The methods evaluation is being rerun on this attempt-5 model as
registered (`debug/attempt5_and_rerun.sh`); the attempt-1-model results are in `archive_attempt1_model_2026-11-16/`.

## Attempt 6 — registered 2026-11-16 14:50, before running (user: "do that")

**Change: signal 138 (W Paces Ferry @ Paces Ferry Pl, ~260 m east) simulated under its own field timing**, so
westbound traffic reaches 137 in the platoons and gaps 138 releases instead of at random (diagnosis of attempts 4–5).
- 138 (OSM node 69548021, already in the network, previously switched off) runs GDOT's own time-of-day plans for
  each day (Split Monitor, `intersections/138/timing/`) on the same NEMA engine, coordinated-actuated, whatever
  controls 137 (`neighbour138/`, `atsc/sim/run.py` neighbours, `atsc/sim/episode.py`).
- Offsets: per plan, the field time between 137's and 138's coordinated green ends, measured on Timing & Actuation
  charts of both signals for the same windows (`neighbour138/offset_138.py`); 137's plans get an absolute offset 0.
- 138's own movements that do not reach 137 are added from its turning-movement report (EB left, EB through,
  Paces Pl SB): they call 138's side and left phases, which is what interrupts the westbound flow. Not scored.
- ASSUMPTIONS, disclosed: 138's minimum greens as 137's for the same phase type, no pedestrian timing at 138, the
  field driveway leg (P4, NB) is not in OSM so its calls are missing, advance zones at 260 ft, 138's presence-zone
  counts used as reported (lower bounds).
Then: left-turn clearance check against the field target (as in attempt 5), controller refit on train days, validation
with the same criteria; methods evaluation rerun on the result.

### Attempt 6 inputs measured (2026-11-16 15:30)

Offsets (`neighbour138/offset_138.py`, paired Timing & Actuation windows): 138's westbound green ends within 2 s of
137's in every plan (A −1.7, B +0.9, C +0.2, D −0.5, E/G −1.1, G/J 0.0 s; spread 3.5–8.7 s over 12–36 pairs).
138 follows 137's schedule with its own plan of the same cycle (the two read schedules share the cycle at 91 % of
daytime 15-min points; the rest are band edges and misread bands). 138's P2/P6 on recall (only advance zones there).

Left-turn clearance with 138 simulated (train-day windows, impatience 0.5), permissive share:

| left turn | field | attempt 5 (138 off) | attempt 6 (138 on) |
|---|---|---|---|
| WB_L | 0.89 | 0.66 | 0.75 |
| EB_L | 0.85 | 0.71 | 0.73 |
| NB_L | 0.49 | 0.39 | 0.40 |
| SB_L | 0.61 | 0.54 | 0.61 |
| mean abs diff | | 0.135 | 0.088 |

Platooned arrivals move the left turns towards the field, as diagnosed; they do not close the gap fully (the driveway
leg and its calls at 138 are not modelled).

## Results — attempt 6

Run 2026-11-16 15:32–16:06 (`validation/attempt6/`), 138 simulated under its field timing, impatience 0.5, train-day
refit (no max recall; passage P1 8, P3 6, P4 3, P5 8, P7 6, P8 8 s).

| Phase | Plan | days | avg split sim − field (s) | % gap-outs sim − field | % skips sim − field |
|---|---|---|---|---|---|
| P1 | A | 6 | +2.1 | +4 | -9 |
| P1 | B | 7 | +0.9 | -6 | -0 |
| P1 | C | 7 | +3.1 | +15 | +5 |
| P1 | D | 7 | +3.4 | +20 | -22 |
| P1 | E | 42 | +2.0 | +15 | -7 |
| P1 | G | 5 | +3.0 | +17 | +36 |
| P3 | A | 6 | -1.3 | +6 | -23 |
| P3 | B | 6 | -1.1 | +8 | -25 |
| P3 | C | 5 | -0.9 | +12 | -25 |
| P3 | D | 7 | +0.0 | +16 | -25 |
| P3 | E | 31 | -0.3 | -1 | -18 |
| P4 | A | 8 | -1.7 | +14 | -8 |
| P4 | B | 8 | -1.9 | +13 | -4 |
| P4 | C | 7 | -3.2 | +15 | -2 |
| P4 | D | 8 | +1.6 | +9 | -11 |
| P4 | E | 36 | -2.4 | +19 | -4 |
| P4 | G | 5 | -2.4 | +30 | +1 |
| P5 | A | 8 | +3.5 | +19 | -23 |
| P5 | B | 7 | +1.7 | -3 | -11 |
| P5 | C | 7 | +4.4 | +38 | -20 |
| P5 | D | 7 | +4.3 | +27 | -25 |
| P5 | E | 39 | +3.4 | +25 | -16 |
| P5 | G | 8 | +3.7 | +30 | +4 |
| P7 | A | 8 | +1.4 | +5 | -32 |
| P7 | B | 5 | -0.6 | -14 | -18 |
| P7 | C | 7 | -0.3 | -10 | -13 |
| P7 | D | 7 | +2.9 | +23 | -39 |
| P7 | E | 35 | +1.4 | -19 | -17 |
| P7 | G | 5 | -0.7 | +7 | -32 |
| P8 | A | 9 | -1.7 | -8 | +5 |
| P8 | B | 8 | -1.8 | -3 | -3 |
| P8 | C | 8 | -1.4 | +2 | -4 |
| P8 | D | 8 | -0.5 | -10 | +8 |
| P8 | E | 41 | -3.5 | +9 | -2 |
| P8 | G | 10 | -2.4 | +2 | -5 |

- **V1 average split:** 26/35 pairs within 3 s, worst 4.4 s → **FAIL**
- **V2 % gap-outs:** 23/35 pairs within 15 points, worst 38 → **FAIL**
- **V3 % skips:** 19/35 pairs within 15 points → **FAIL** (reported)
- **V4:** not defined for 137 (VALIDATION.md)
- **V5 health:** 0 teleports; days with W Paces Ferry through PM delay > 100 s: none → **PASS**

**Accepted (V1, V2, V5):** NO

| attempt | V1 split ≤ 3 s | V2 gap-outs ≤ 15 pt | worst gap-out pair |
|---|---|---|---|
| 1 | 19/35 | 11/35 | 56 |
| 2 | 15/35 | 16/35 | 44 |
| 3 | 20/35 | 18/35 | 43 |
| 4 | **29/35 ✓** | 19/35 | 32 |
| 5 | 27/35 | 20/35 | 34 |
| 6 | 26/35 | **23/35** | 38 |

Not accepted. V2 keeps improving with each measured change (11 → 23 of 35); V1 sits at the threshold (26–29 of the 28
needed). The remaining gap-out misfits are the EB left P5 (19–38 points, plans A, C, D, E, G) and P1 in the evening
plan D and PM plan G: the main-street lefts still clear on the flashing yellow less often than in the field. Next
measured candidate: the driveway leg at 138 (absent in OSM), whose calls interrupt the westbound flow in the field.

**Consistency fix found while checking attempt 6 (16:10):** `debug/stage1.sh` re-ran `make_signal.py`, which overwrote
the train-fitted controller in `sim.json` with max recall from the Split Monitor termination shares. Validation used
the fitted controller, the methods evaluation did not. Effect: only the GDOT-plan controller (plan mode); actuated
(free mode), MaxPressure and the learners do not use max recall. Affected: the attempt-5 methods evaluation's
GDOT-plan rows (archived). Fixed: `make_signal.py` leaves a train-fitted controller untouched; the attempt-6
evaluation runs with the fitted controller restored before any GDOT-plan run.

## Attempt 7 — registered 2026-11-17, before running (user: "ok do validation first")

**Finding (train weekdays, GDOT's Split Monitor only; `force_off_mode.py`):** the main-street lead lefts P1 and P5 never
run past their programmed split in the field: their 85th-percentile split equals the split (15, 15, 15, 15 s in plans
A–D) in **0 of 98 (P1) and 0 of 96 (P5)** served train-day bands. The side-street phases do exceed theirs (P3 15/94,
P4 46/114, P7 46/99, P8 38/108 bands; pedestrian minimums and partner-skipped greens). The engine uses fixed
force-offs for every phase (`nema.py`), so a lead left that starts early, after a side street ended early, runs to
its fixed point in the cycle; on the validation days the simulated P1/P5 p85 split reaches 18–27 s against 12–18 s
programmed. This is the controller's force-off mode, not driver behaviour: GDOT's controller caps P1/P5 at their
split (floating force-off) and gives unused time to the coordinated phases.

**Check made before registering, left-turn clearance split (field, train days):** only 2 % of the main-street
left activations end in the 6 s after the permissive green (sneakers), so the remaining permissive-share gap is not
a missing end-of-green clearance in SUMO. The attempt-6 model, same windows: 2 % (EB_L) and 5 % (WB_L) after the green, so SUMO matches the field there
(permissive share 0.73 / 0.75 vs field 0.85 / 0.88; `debug/clearance_split_a6.txt`). (`left_turn_clearance_137.py` now reports this column and reads train-day
windows only; the tool cache also holds two validation days fetched for `offset_138.py` on 2026-11-16, which the
field target above excludes.)

**Change:** floating force-off for the non-coordinated phases the rule selects — rule fixed now: a phase floats when
its p85 split is within 0.5 s of its split in every served train-day band; result **P1 and P5**; P3, P4, P7, P8 keep
fixed force-offs. `nema.Plan.floating`, signal.json plan key `floating_force_off` (written by `make_signal.py` from
`force_off.json`). Free mode (nights) is unaffected. Then, as before: controller refit on train days (passage),
validation with the same criteria; the methods evaluation is rerun for the controllers this affects (GDOT plan and
actuated, through the refit passage times), whether or not it passes.

## Results — attempt 7

Run 2026-11-17 01:35–02:08 (`validation/attempt7/`): floating force-off P1/P5, train-day refit (no max recall; passage P1 6, P3 6, P4 4, P5 6, P7 6, P8 8 s), otherwise as attempt 6 (138 upstream, impatience 0.5).

| Phase | Plan | days | avg split sim − field (s) | % gap-outs sim − field | % skips sim − field |
|---|---|---|---|---|---|
| P1 | A | 6 | +0.0 | +6 | -9 |
| P1 | B | 7 | -0.2 | +3 | -0 |
| P1 | C | 7 | -0.1 | +6 | +4 |
| P1 | D | 7 | +0.4 | +12 | -22 |
| P1 | E | 42 | -0.2 | +15 | -9 |
| P1 | G | 5 | +0.1 | -1 | +34 |
| P3 | A | 6 | -1.3 | +7 | -23 |
| P3 | B | 6 | -0.9 | +9 | -24 |
| P3 | C | 5 | -0.9 | +12 | -25 |
| P3 | D | 7 | +0.0 | +18 | -25 |
| P3 | E | 31 | -0.3 | -2 | -18 |
| P4 | A | 8 | -1.1 | +11 | -8 |
| P4 | B | 8 | -1.6 | +5 | -4 |
| P4 | C | 7 | -2.3 | +12 | -1 |
| P4 | D | 8 | +2.1 | +8 | -11 |
| P4 | E | 36 | -1.8 | +18 | -4 |
| P4 | G | 5 | -1.6 | +27 | +1 |
| P5 | A | 8 | +0.6 | +1 | -23 |
| P5 | B | 7 | -0.2 | -3 | -11 |
| P5 | C | 7 | +0.5 | +5 | -20 |
| P5 | D | 7 | +0.6 | +6 | -27 |
| P5 | E | 39 | +0.3 | +14 | -16 |
| P5 | G | 8 | +0.2 | -3 | +3 |
| P7 | A | 8 | +1.7 | +5 | -32 |
| P7 | B | 5 | -0.7 | -15 | -18 |
| P7 | C | 7 | -0.3 | -10 | -13 |
| P7 | D | 7 | +3.1 | +26 | -41 |
| P7 | E | 35 | +1.4 | -18 | -19 |
| P7 | G | 5 | -0.6 | +7 | -32 |
| P8 | A | 9 | -1.5 | -7 | +3 |
| P8 | B | 8 | -1.5 | -4 | -3 |
| P8 | C | 8 | -1.2 | +2 | -5 |
| P8 | D | 8 | -0.5 | -9 | +6 |
| P8 | E | 41 | -2.5 | +9 | -2 |
| P8 | G | 10 | -1.8 | +2 | -5 |

- **V1 average split:** 34/35 pairs within 3 s, worst 3.1 s → **PASS**
- **V2 % gap-outs:** 29/35 pairs within 15 points, worst 27 → **PASS**
- **V3 % skips:** 19/35 pairs within 15 points → **FAIL** (reported)
- **V4:** not defined for 137 (VALIDATION.md)
- **V5 health:** 0 teleports; days with W Paces Ferry through PM delay > 100 s: none → **PASS**

**Accepted (V1, V2, V5):** YES

| attempt | V1 split ≤ 3 s | V2 gap-outs ≤ 15 pt | worst gap-out pair | accepted |
|---|---|---|---|---|
| 1 | 19/35 | 11/35 | 56 | no |
| 2 | 15/35 | 16/35 | 44 | no |
| 3 | 20/35 | 18/35 | 43 | no |
| 4 | 29/35 | 19/35 | 32 | no |
| 5 | 27/35 | 20/35 | 34 | no |
| 6 | 26/35 | 23/35 | 38 | no |
| **7** | **34/35** | **29/35** | 27 | **yes** |

**Accepted** under the criteria fixed before attempt 1 (V1, V2, V5). V3 (skips, reported, not a criterion) still fails,
19/35: the model serves the lefts' and side streets' arrows more often than the field (P1/P5 skipped 9–27 points less
in most plans; P3, P7 likewise), consistent with the left-turners' permissive share still below the field
(0.73–0.75 vs 0.85–0.88). State this with every result. The methods evaluation is rerun for the two controllers the
change reaches (GDOT plan: floating force-off; actuated: refit passage times); the learners, MaxPressure and Webster
do not use either (free mode without passage, or their own fixed plans), so their attempt-6 runs stand.

Correction (2026-11-17 12:10): LSTDQ v2 and Q-learning do reach the change indirectly — they train with the actuated
controller (refit passage times) as their behaviour policy. Both were therefore retrained on the attempt-7 model
(5 seeds each, `debug/attempt7_retrain.sh`) and re-evaluated on the 20 validation days; old weights are in
`archive_attempt6_model_2026-11-17/`. LSTDQ 27.5 -> 26.7 s/veh, Q-learning 37.3 -> 37.6 s/veh (seeds pooled). ARS
(no behaviour policy), MaxPressure and Webster are unaffected. Every method in `eval/` is now on the attempt-7 model.

## Attempt 8 — TEST_PLAN.md amendment 1 (registered there before running)

Attempt 7 + engine fix F1 (no barrier crossing without a conflicting call, coordinated dwell, dual entry on the
throughs), F2 (undeparted vehicles scored; no effect on the plan-mode validation runs), F3 (measured saturation flow
in `sim.json`; used only by the queue estimate and Webster, not by the GDOT replica). Same train-day refit and
criteria. Run 2026-11-17 17:13–17:46 (`validation/attempt8/`). Refit unchanged: passage P1 6, P3 6, P4 4, P5 6,
P7 6, P8 8 s, no max recall.

Saturation flow (`sat_flow.py`, 29 train weekdays 15:30–19:30 [corrected 2026-11-18 from "33": `sim.json` sat_flow_source, written by the script, says 29], headways from the 5th queued vehicle): through
P2 2,176, P4 2,057, P6 2,175, P8 2,078 veh/h/lane; left P7 1,964 (333 headways); P1, P3, P5 too few protected
queued headways → pooled left 1,963. Faster than both values it replaces (1,950 / 1,900) and than the 1,650
noted in attempt 3 (a different, start-up-inclusive measure on one lane).

Result: V1 34/35 (worst 3.1 s) PASS, V2 28/35 (worst 28) PASS, V5 PASS → **accepted**; V3 skips 18/35 (reported).
Per-pair differences move by ≤ 2 points from attempt 7: **F1 does not explain the V3 skip mismatch** (the
review's guess). In plan mode the coordinated phases already hold until their force-off, and the side-street
lefts are skipped less in the model than in the field because they are called more often, not because the
engine served them uncalled. The F1 effect is in free mode (actuated, MaxPressure, learners) at light demand.

## Attempt 9 (v3) — registered 2026-11-20, before running

Model changes, each from GDOT data or a standard, none fitted to a validation statistic (`atsc/PIPELINE_PLAN.md`,
previous files in `archive_before_v3_2026-11-20/`):
- **A. Passage times measured directly** (`atsc/measure.py`: last stop-bar zone-off → end of green, median over the
  cached train-day Timing & Actuation windows): P1 1.9, P3 1.8, P4 3.4, P5 2.1, P7 2.2, P8 3.4 s (were fitted
  6/6/4/6/6/8 s to the train-day gap-out share). **P1 clearance measured** 3.2 / 2.3 s (was P5's, assumed). This
  removes the circularity between tuning and V2: gap-out share is no longer used to set anything.
- **B. Discharge** calibrated to the HCM base saturation flow (field headways are not measurable at 137):
  SUMO `tau` 1.2 → through 1,934, left 1,789 veh/h/ln (`calibrate_discharge.py`).
- **C. Presence-zone undercount factors** re-chosen in closed loop (`calibrate_demand.py`, train days): the
  factor per movement for which the simulated zone gives as many activations as GDOT reported.

Criteria V1–V5 unchanged. **Added, written now, scored when the ATSPM outcome numbers for the validation days are
read** (`tools/atspm_charts.py`, plan-band windows; simulated with the same definitions, `atsc/sim/atspm_sim.py`):
- **O1 split failures** (count per plan band, per phase × plan; same band length on both sides), **O2 wait time** (average, per phase × plan),
  **O3 arrivals on green** and **O4 approach delay** (P2, P6, advance detectors), **O5 closed-loop count ratio**
  (simulated presence-zone activations / GDOT count, per movement).
- A case passes when |median over validation days of (sim − field)| ≤ half the field's own day-to-day
  interquartile range for that case (min. 5 days of field readings); only each phase's own approach chart is used. Reported with a bootstrap over days (share
  of 1,000 resamples in which ≥ 80 % of cases pass). O1–O4 are reported (not acceptance criteria) for this first
  outcome attempt; O5 passes per movement at 0.8–1.25.

## Results — attempt 9

Run 2026-11-20 (`validation/attempt9/`). V1 28/35 (worst 6.4 s) **FAIL**, V2 10/35 (worst 55) **FAIL**, V3 21/35
(reported), V5 PASS → **not accepted**. Every scored phase gaps out 15–55 points MORE often than the field and its
green is 2–6 s shorter. With the passage time now measured (~2 s), the remaining free quantity in gap-out is how long
a vehicle keeps the zone occupied, i.e. the zone length — assumed 12 m, not published by GDOT. The old 4–8 s fitted
passage was compensating for it. Outcome checks O1–O5 wait for the field numbers.

## Attempt 10 (v3) — registered 2026-11-20, before running

- **A2. Stop-bar zone length per zone** (`calibrate_zones.py`, train days): the length whose simulated single-vehicle
  occupancy (median of activations inside one own green) matches the field's measured one (`pass_s`, 72 train-day
  T&A windows): NB_L 16, NB_T 36 (grid edge, field 3.5 s vs sim 3.0 s at 36 m), NB_R 8, SB_L 24, SB_T 20, SB_R 8,
  EB_L 12 m; zones without a field measurement keep 12 m. Uses no validation statistic.
- **C redone** on the new zones (activations depend on zone length): closed-loop factors re-chosen with the same rule.
- Everything else as attempt 9; criteria unchanged (V1–V5; O1–O5 as registered for attempt 9).

## Results — attempt 10

Run 2026-11-20 (`validation/attempt10/`). **V1 31/35 (worst 4.2 s) PASS**, V2 10/35 (worst 50) **FAIL**, V3 24/35
(reported), V5 PASS → **not accepted**.
- The zone lengths fixed the side-street throughs: P4/P8 gap-out error now 0–18 points (was 9–35), green length
  within 0–2 s on most plans.
- **The left arrows still gap out 15–50 points more than the field** (P1 +15–27, P3 +37–50, P5 +27–43, P7 +4–42).
  Re-measuring the passage on the field charts with only greens that end before their maximum and with the zone
  empty gives the same ~2.0–2.2 s for P1, P5, P7, so the passage is not the cause. On the field charts many left
  arrows end early **while their zone is still occupied** (P1 42, P5 46, P7 31 of ~100–200 greens): an end that is
  neither a gap-out nor a split-length force-off (likely fixed force-offs reached after a late start, or arrows
  whose waiting vehicle is not extending). The model does not reproduce that mechanism yet.
- **Closed-loop counts conflict with the zone lengths for the side throughs**: with the longer zones, no factor
  reproduces GDOT's NB_T (best 0.76) or SB_T (0.45) counts, nor SB_L (0.42 at k = 1). The single-vehicle occupancy
  (`pass_s`) of a through zone is long because vehicles slow or stop on it, which a longer simulated zone imitates
  but then merges more vehicles into one activation than the field does. Zone length alone cannot match both
  measurements: the detection model (radar zone behaviour) needs a different representation, not another length.

Not accepted. Diagnosis needs per-cycle data on the left arrows (Phase Termination charts, cycle position of each
end) before another attempt is registered; no further change is made to the model now.

## Diagnosis after attempt 10 (2026-11-20, train days only; no model change yet)

Tools: `diag_train.py` (Split Monitor shares on train days), `diag_clear.py` (zone occupancy around arrow
starts, field T&A vs simulation). Reader fix: `tools/lanecheck/tna_events.py` misplaced the plot edges on charts
with no detector rows (P2, P6); fallback added, other charts unchanged.
- Train days show the same pattern as validation: served left arrows gap out 64-96 % in the model vs 17-60 % in
  the field; the model also skips the lefts less.
- Field left zones stay occupied long after the arrow starts (median 6-9 s; 35-41 % of arrows end with the zone
  occupied) vs the model (median 2.5-7 s; 4-36 %). Field through zones clear fast (median ~3 s) while the model's
  long through zones (20-36 m from attempt 10) stay occupied 9-17 s: the pass_s-based zone lengths are wrong
  for the throughs.
- Left vehicles that arrive during the permissive period: field zone occupancy p75 6-14 s, p90 21-35 s (they wait
  on the zone for a gap); model p75 2 s (SUMO moves them to its waiting point inside the junction, off the zone,
  or they find a gap at once). So in the field the waiting permissive turners keep calling and are still on the
  zone when the arrow starts; in the model they are not.
- SUMO `startupDelay` (driver start-up) was probed and rejected: 1 s already cuts saturation flow to ~1,700 and
  `tau` cannot restore 1,900.
Next candidate (to be registered before running): represent left zones as covering the driver's waiting
position past the stop line (detection-model change), shorter through zones from the queue-clear measurement.

## Attempt 11 (v3) — registered 2026-11-20, before running

- **A3. Left-turn zones reach the waiting point inside the junction** (`detectors.json` `into_junction:
  waiting_point` on ch1, ch19, ch9, ch29; `atsc/sim/detectors.py`). A permissive left turner in SUMO waits for its
  gap at an internal stop point past the stop line, i.e. off a zone that ends at the stop line, so its call drops;
  on GDOT's charts the waiting turner keeps the zone occupied (diagnosis above). The zone now covers the stop line
  to that waiting point (5-12 m of junction lane; no length is fitted). Train-day check before registering:
  permissive-period occupancy P1 p75 19.5 s (field 13.6, before 2.0), P5 9.5 (6.0, before 2.0).
- **C redone** on the new zones with the same rule (activations depend on the zone).
- Everything else as attempt 10 (through zones stay as attempt 10; their count conflict stays flagged).
  Criteria unchanged (V1-V5; O1-O5 as registered for attempt 9).

## Results — attempt 11

Run 2026-11-20 (`validation/attempt11/`). C factors: NB_L 2.4, NB_T 3.2, NB_R 1.2, SB_L 1.0, SB_T 2.8, SB_R 1.2,
EB_L 1.8 (NB_L, NB_T, SB_L, SB_T flagged: no factor reaches the count). **V1 33/35 (worst 4.2 s) PASS**, V2 14/35
(worst 39) **FAIL**, V3 19/35 (reported), V5 PASS → **not accepted**. Left gap-out excess down from 15-50 to
13-39 points; the model now skips the lefts less (P5 -17 to -29, P3 -19 to -24). Train-day check: a moving
left turner occupies the new (12-24 m + junction) zone ~3.5 s at the 25th percentile vs ~1.7 s in the field, so
the zone reaches too far back; a long zone merges vehicles into fewer activations, which pushes the closed-loop
demand factors up (EB_L 1.2 → 1.8) and with them the calls.

## Attempt 12 (v3) — registered 2026-11-20, before running

- **A4. Upstream extent of the left zones** (`calibrate_leftzones.py`, train days): the zone keeps its
  junction part (stop line to SUMO's waiting point) and reaches u m back from the stop line, u in {0, 3, 6, 9, 12}
  per zone, chosen so that the simulated median occupancy of activations that start in the permissive period
  (permissive phase green, arrow not) is closest to the field's (train-day T&A: P1 3.4, P3 4.4, P5 2.5, P7 2.2 s).
  A detector-level measurement; no termination or skip share is used.
- **C redone** on the new zones, same rule. Everything else as attempt 11; criteria unchanged.

## Results — attempt 12

A4 chose u: P1 0, P5 3, P3 3, P7 3 m (field permissive-period medians P1 3.4, P5 2.5, P3 4.4, P7 2.2 s; P1's
simulated median is 7.5-8.5 s for every u, so the rule fell to the smallest). C: NB_L 1.4, NB_T 2.8, NB_R 1.2,
SB_L 2.4, SB_T 2.8, SB_R 1.2, EB_L 1.4. Run 2026-11-20 (`validation/attempt12/`): V1 24/29 (worst 8.1 s) FAIL,
V2 16/35 (worst 45) FAIL, V3 20/35, V5 PASS → **not accepted**. **Design error in the grid:** u = 0 leaves only the
junction part, which a WB-left vehicle stopped at the stop line during red never occupies, so P1 was almost
never called (skips +17 to +76). The grid should have started where a stopped vehicle is covered.

## Finding 2026-11-20 — presence-zone counts include radar dropouts

Train-day T&A (9 days): share of zone activations that start and end while the movement has no green (own or
permissive phase green, or the 3 s after it), so no vehicle can have left: EB_L (ch19) 0.07, NB_L (ch9) 0.19,
SB_L (ch29) 0.43, SB_T (ch12) 0.65, NB_T (ch32) 0.61 (WB_L ch1 0.05, not a count source). The model's zones:
0.00-0.08. A stopped vehicle that the radar loses and finds again is counted twice by GDOT's report. The
closed-loop step (C) matched the model's activations to these inflated counts, which is why it raised the side
street demand and why NB_T, SB_T and SB_L could never be matched. (`measure_dropouts.py`)

## Attempt 13 (v3) — registered 2026-11-20, before running

- **A4 corrected:** left zones = junction part + u = 3 m upstream for all four (3 m is the smallest grid value that
  covers a vehicle stopped at the stop line; it was A4's choice for P3, P5, P7, and P1's measurement is flat
  for u ≥ 3, so the tie rule gives 3).
- **C corrected for dropouts:** for EB_L, NB_L, NB_T, SB_L, SB_T the closed-loop target is GDOT's count x (1 -
  field dropout share), and the model's activations are counted the same way (dropouts excluded). NB_R, SB_R
  (right turns leave on red) as before. Same grid and rule otherwise.
- Everything else as attempt 11 (through zones as attempt 10). Criteria unchanged.
- Amendment before running: C's grid gains 0.6 and 0.8 (a dropout-corrected count can be below GDOT's raw count).

## Results — attempt 13

C (dropouts removed both sides): NB_L 1.4, NB_T 0.6, NB_R 1.2, SB_L 1.4, SB_T 1.0, SB_R 1.2, EB_L 1.4; confirmation
ratios 0.99-1.03 for all but SB_L (0.75, flagged) — the first time the counts are reproduced. Run 2026-11-20
(`validation/attempt13/`): V1 22/35 (worst 10.9 s) FAIL, V2 11/35 (worst 52) FAIL, V3 22/35, V5 PASS → **not
accepted**. P1 now close (gap-out +4 to +16 on plans A-E). The side-street through greens are 5-11 s too short:
with the dropouts removed the through demand fell (NB_T 3.2 → 0.6, SB_T 2.8 → 1.0), and the through zones are the
long attempt-10 zones (36 / 20 m), whose behaviour does not match the field: train-day T&A shows the field through
zone occupied at green start in 29 % of greens and clearing ~3 s after the green starts, the model's in ~100 % and
after 9-17 s. A long zone merges a moving queue into one activation, so the closed loop now under-supplies.

## Exploration after attempt 13 — side-street through zone geometry (train days, not an attempt)

`explore_thruzones.py`: zone = u m before + d m past the stop line, attempt-13 demand. Field: occupied at green
start 0.29 / 0.28 (ch12 / ch32), clear 3.1 / 3.2 s, single-activation occupancy 2.05 / 3.52 s, dropouts 0.65 / 0.61.
Model: any u ≥ 2 m gives 0.94 / 0.76 occupied at start (every SUMO driver stops at the same point, on the zone);
u = 0 gives 0.00; activation occupancy 1.0-2.0 s for every geometry; dropouts 0.00 always. No geometry reproduces
the field zone's behaviour: on GDOT's radar the first stopped vehicle is sometimes on the zone, sometimes not, and is
often lost and found again. This is detector behaviour, not zone length, and SUMO's detectors cannot show it.
Stopped here: the next step needs a decision on method (see PROGRESS.md 2026-11-20 evening).

## Attempt 14 (v3) — registered 2026-11-21, before running (user: "for 137 do whatever you want to do")

- Model = attempt 13 (measured clearances, HCM discharge, left zones to the waiting point, counts without radar
  dropouts), plus an **effective gap time per phase** fitted on train days with attempt 2's rule, unchanged: max
  recall by the train-day rule, then per phase the passage in {2, 3, 4, 6, 8} s with the smallest mean |sim − field|
  gap-out share over the plans (ties: mean |split difference|). **Disclosed deviation**: the field's measured gap
  times are ~2-3.4 s (kept in `sim.json` `passage_measured`); the fitted value stands in for radar-zone behaviour
  SUMO's detectors do not reproduce (stopping position on/off the zone, dropouts, waiting turners), found in the
  diagnosis and exploration above. Because the fit uses the gap-out share on train days, V2 on validation days
  tests whether that effective value carries over to other days, not whether the gap time itself is right.
- Criteria unchanged (V1, V2, V5; V3 reported; O1-O5 reported when the field outcome numbers are read).
