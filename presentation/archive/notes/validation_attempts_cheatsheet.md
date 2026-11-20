# 137 twin validation — attempt by attempt (Q&A cheat sheet)

Source: `atsc/sites/137/VALIDATION.md`. V1 = splits within 3 s, V2 = gap-out share within 15 points; scores are
phase×plan pairs passing out of 35; a pass needs ≥ 28/35 on both (plus V5 health, which passed every time).

Rule behind every attempt: each change is justified by GDOT data from the practice (train) days — never by tuning
to the validation score — and written down before the run.

| Attempt | Splits | Gap-outs | Change |
|---|---|---|---|
| 1 | 19 | 11 | settings as first built |
| 2 | 15 | 16 | passage times fitted on practice days |
| 3 | 20 | 18 | + measured pedestrians |
| 4 | **29 ✓** | 19 | + side-street undercount corrected |
| 5 | 27 | 20 | + left-turn driver calibration |
| 6 | 26 | 23 | + upstream signal 138 simulated |
| **7** | **34 ✓** | **29 ✓** | + lead-left floating force-off → **accepted** |

---

## Attempt 1 — settings as first built (19 / 11)

- **Symptom:** the simulated light ends greens too early everywhere: lefts gap out 25–56 points more than the field,
  side-street through splits 5–12 s short.
- **Cause:** passage times (how long the light waits for the next car before ending green) were copied from an old fit
  to one day on an earlier network — not fitted to this site.
- **What we did:** nothing yet — this is the baseline.

## Attempt 2 — passage times fitted on practice days (15 / 16)

- **Symptom carried in:** greens end too early (attempt 1).
- **Cause:** passage times wrong for this site.
- **What we did:** for each phase, chose the passage time from {2, 3, 4, 6, 8} s that best matches GDOT's practice-day
  gap-out share (Split Monitor).
- **What it fixed:** side-street lefts (gap-out error down to 6–9 points); worst split error halved (12.1 → 7.0 s).
- **What remained:**
  - side-street throughs still 2–7 s short even at the longest passage time;
  - main-street lefts (P1/P5) odd: gap out too often *and* served too often.
  - Splits score fell slightly (15/35).

## Attempt 3 — added pedestrians (20 / 18)

- **Symptom:** side-street through splits too short.
- **Cause (partly):** pedestrian calls were missing — a push lengthens the side-street green for the walk.
- **What we did:** measured pedestrians on Timing & Actuation charts (48 windows, 3 practice days):
  - main-street crossing walks every cycle → served every cycle;
  - side-street buttons pushed 0–8 times an hour → random calls at that rate;
  - walk + flashing don't walk times from the charts.
- **Also checked, not changed:** discharge speed vs HCM — our cars were already slower, so no justified change.
- **What it fixed:** side-street splits a little (worst split now 5.9 s, inside the 6 s cap).
- **What remained:** side-street splits still short — pedestrians only affect ~5 % of cycles.

## Attempt 4 — side-street undercount corrected (29 ✓ / 19)

- **Symptom:** side-street splits still too short — too few simulated cars on the side streets.
- **Cause (found on Timing & Actuation charts):** GDOT's side-street and EB-left counts come from stop-bar
  **presence** zones. A queue leaving on green keeps the zone occupied, so 5 cars count as 1.
  Same defect as at 7065.
  - The same check refuted the "call delay" idea for the main-street lefts.
- **What we did:** estimated the real number of cars from how long the zone stayed occupied during green
  (~1.9 s per car, HCM rate) → a correction factor per movement from 9 practice days, applied to daytime bins.
- **What it fixed:** **splits pass for the first time** (worst 4.5 s) — the biggest single fix.
- **What remained:** gap-outs fail, almost entirely on the left-turn phases.

## Attempt 5 — left-turn driver calibration (27 / 20)

- **Symptom:** left-turn phases gap out / get served differently from the field.
- **Cause (measured):** in the field 85–89 % of main-street left-turners clear on the flashing yellow; in the sim only
  67–72 % — so the sim needs the arrow more.
- **What we did:** tested SUMO's gap-acceptance settings against practice-day detector events; impatience 0.5 won by a
  rule fixed in advance.
- **What it fixed:** side-street lefts a little.
- **What remained:** main-street lefts unchanged. Key finding: driver settings aren't the cause — the problem is
  **how many gaps exist in oncoming traffic**, not how drivers accept them. Splits one pair short (27).

## Attempt 6 — upstream signal 138 simulated (26 / 23)

- **Symptom:** main-street left-turners can't find enough gaps.
- **Cause:** westbound traffic arrived at random in the sim; in the field it arrives in **platoons** released by
  signal 138 (~260 m away), leaving gaps between them.
- **What we did:**
  - ran 138 under its own GDOT plans every day;
  - measured the offset between the signals from both signals' charts (138's green ends within 2 s of 137's);
  - added 138's other traffic from its count report.
- **What it fixed:** flashing-yellow share closer to field (mean error 0.135 → 0.088); gap-outs improved (23).
- **What remained:** EB left (P5) and P1 in evening/PM plans still off; splits just short (26).

## Attempt 7 — lead-left floating force-off (34 ✓ / 29 ✓) — ACCEPTED

- **Symptom:** main-street lead lefts ran too long in the sim — p85 split 18–27 s vs 12–18 s programmed.
- **Cause:** GDOT's Split Monitor (practice days) shows P1/P5 **never** ran past their programmed split (0 of 98 and
  0 of 96 periods). Our controller used fixed force-off points, so a left that started early (after a side street
  ended early) ran on to its fixed point.
  - This is the controller's force-off mode, not driver behaviour.
- **What we did:** P1/P5 capped at their split ("floating force-off"), chosen by a rule fixed in advance (phases whose
  p85 split never exceeds the split); spare time goes to the main street. Passage times refitted on practice days.
- **What it fixed:** both criteria pass — splits 34/35 (worst 3.1 s), gap-outs 29/35 (worst 27).
- **Still open (state it):** skips 19/35 — the sim serves left arrows more often than the field (flashing-yellow
  share 0.73–0.75 vs 0.85–0.88).

---

## Fix types (one-liner)

- **Controller fixes:** 2 (passage times), 7 (force-off mode).
- **Traffic fixes:** 3 (pedestrians), 4 (demand), 5 (driver behaviour), 6 (arrival pattern).
- So validation tested the traffic too, through the controller.
