# Site 137 — model-building log (for the paper's "Proposed approach")

Plain record of every step taken to build and check the simulation of signal 137, in order: what was changed,
why, which data it used, the rule used to pick a value, and what came out. One entry per step, added as the work
goes. The formal pass/fail record (criteria written before each run) is `VALIDATION.md`; this log explains it.

Terms used below:
- **Phase**: one signal movement group. 137 has 8: P1 WB left (W Paces Ferry), P2 EB through, P3 NB left
  (Slaton), P4 SB through (E. Andrews), P5 EB left, P6 WB through, P7 SB left (E. Andrews), P8 NB through (Slaton).
  All lefts are protected-permissive and lead. P2/P6 are coordinated (main street).
- **Zone**: a radar (Wavetronix Matrix) detection area painted on a lane near the stop line. The controller sees
  "occupied / empty". GDOT's turning-movement "counts" for the side streets and the EB left are the number of
  times such a zone switches on (activations), not the number of vehicles.
- **Gap time (passage time)**: the controller ends a green when its zones have been empty for this long (gap-out).
  It also ends a green at its time limit (force-off).
- **Validation checks** (on 20 held-out days, never used to set anything): V1 average green (split) length within
  3 s, V2 share of greens that gap out within 15 points, each for ≥ 80 % of 35 phase × plan pairs; V5 health.
  V3 skip share is reported only.
- **Train days**: 29 weekdays used for all settings. Validation days: 20 other weekdays. Test days: locked.

---

## Starting point: attempt 8 (accepted 2026-11-17, before v3)

V1 34/35, V2 28/35, V5 pass → accepted. But two of its settings were fitted, not measured:
- **Gap time per phase** was chosen on train days so that the simulated gap-out share matched GDOT's (values
  4–8 s). Measured directly later: ~2 s. So the fitted gap time stood in for something else the model got wrong.
- **Side-street demand** used an estimate of how many vehicles one zone activation hides (factors 1.4–2.9,
  from zone occupancy time and the HCM 1,900 veh/h discharge).

Goal of v3 (`atsc/PIPELINE_PLAN.md`): replace fitted values with measured ones, so the model copies the real
controller and the method can be repeated at another intersection.

## Step A — measure controller settings directly (2026-11-20)

- **Data**: 72 GDOT Timing & Actuation (T&A) charts, 5 min each, 9 train days (8 windows a day), every phase.
- **Method** (`atsc/measure.py`): read the signal colour row and the zone on/off markers from the chart images.
  - Yellow and red-clear: length of the yellow and dark-red runs. P1 measured 3.2 / 2.3 s (before: copied from P5).
  - Gap time: for greens that end while the zone is empty, time from the last zone-off to the end of green; take the
    most common value. P1 1.9, P3 1.8, P4 3.4, P5 2.1, P7 2.2, P8 3.4 s (before: fitted 6, 6, 4, 6, 6, 8 s).
- **Result**: these replace the fitted values in `sim.json` / `signal.json`. The old fitted values are archived.

## Step B — queue discharge speed (2026-11-20)

- **Why**: how fast a queue leaves decides how long a green is needed. Field headways cannot be measured at 137
  (no per-vehicle stop-line count on the charts), so the target is the HCM base saturation flow, 1,900 veh/h/lane.
- **Method** (`calibrate_discharge.py`): SUMO's `tau` (driver's desired time gap) on a grid 1.0–1.5 s; measure
  the simulated discharge from the 5th queued vehicle on, 8 train days, 15:30–19:30. Rule: closest to 1,900.
- **Result**: tau 1.0 → 2,137; 1.1 → 2,044; **1.2 → 1,934 (chosen; left turns 1,789)**; 1.3 → 1,848.

## Step C — side-street demand by closed loop (2026-11-20)

- **Why**: GDOT's side-street counts are zone activations. Instead of estimating how many vehicles one
  activation hides, let the simulation copy the counting: choose the demand factor k so that the SIMULATED zone
  switches on as many times as GDOT reported.
- **Method** (`calibrate_demand.py`): one common k for the seven presence-zone movements, grid 1.0–3.2, 8 train
  days, 06:00–22:00; for each movement, the k whose ratio (simulated activations / GDOT count) is closest to 1 on
  the rising part of the curve; if no k reaches 1, flag it. Checked with one confirmation run.

## Attempt 9 — steps A + B + C (2026-11-20)

- Demand factors: NB_L 2.0, NB_T 2.4, NB_R 1.2, SB_L 1.4 (flagged), SB_T 2.4, SB_R 1.2, EB_L 1.2.
- **Result**: V1 28/35 but worst pair 6.4 s → FAIL; V2 10/35 → FAIL.
- **What we learned**: with the true ~2 s gap time every phase gapped out 15–55 points more often than the field
  and its green was 2–6 s shorter. How long a car keeps a zone on depends on the zone length, which GDOT does not
  publish (12 m had been assumed). The old 4–8 s gap time had been making up for that.

## Attempt 10 — zone length per zone (2026-11-20)

- **Data**: from the T&A charts, how long ONE moving vehicle keeps each zone on (activations that start and end
  inside one green): EB_L 1.91, NB_L 1.91, NB_R 1.61, NB_T 3.52, SB_L 2.64, SB_R 1.76, SB_T 2.05 s.
- **Method** (`calibrate_zones.py`): zone length grid 8–36 m; pick the length whose simulated single-vehicle
  time matches. Then step C again on the new zones.
- **Chosen**: NB_L 16, NB_T 36 (grid edge), NB_R 8, SB_L 24, SB_T 20, SB_R 8, EB_L 12 m.
- **Result**: **V1 31/35 PASS**; V2 10/35 FAIL. Side-street throughs now close; left arrows still gap out 15–50
  points more than the field. Counts for NB_T, SB_T, SB_L could not be matched by any factor (flagged).

## Diagnosis after attempt 10 (train days only)

Tools: `diag_train.py`, `diag_clear.py`. Also fixed: the chart reader put the time axis in the wrong place on the
P2/P6 charts (charts with no zone rows); P1–P8 other charts unchanged.
- In the field, a left zone stays occupied for a long time after its arrow turns green (median 6–9 s) and 35–41 %
  of arrows end with the zone still occupied. In the model: 2.5–7 s and 4–36 %.
- Left turners who arrive while the main street is green (they may turn in a gap: "permissive") keep the field zone
  on for long (75th percentile 6–14 s, 90th 21–35 s). In the model only ~2 s: SUMO moves a waiting left turner
  forward to a waiting point inside the junction, past the end of the zone, so its call to the controller drops.
  In the field the waiting car stays on the zone and keeps calling.
- Tried and rejected: SUMO `startupDelay` (drivers start late). 1 s already cuts queue discharge to ~1,700 veh/h
  and `tau` cannot bring it back to 1,900.

## Attempt 11 — left zones reach the waiting point (2026-11-20)

- **Change**: each left zone now continues past the stop line to SUMO's waiting point in the junction
  (5–12 m of junction lane). No length is fitted: it is where SUMO parks a waiting left turner.
- Check before running: permissive-period zone time P1 75th percentile 19.5 s (field 13.6, before 2.0).
- Step C again: NB_L 2.4, NB_T 3.2, SB_L 1.0, SB_T 2.8, EB_L 1.8 (four flagged).
- **Result**: **V1 33/35 PASS**; V2 14/35 FAIL (left excess 13–39 points, was 15–50). Best v3 result so far.
- **What we learned**: the left zones were now too long upstream (12–24 m + junction part): a moving turner kept
  them on ~3.5 s vs ~1.7 s in the field, and a long zone merges cars, which pushed the demand factors up.

## Attempt 12 — how far the left zones reach back (2026-11-20)

- **Method** (`calibrate_leftzones.py`): upstream extent u in {0, 3, 6, 9, 12} m; pick the u whose simulated
  median permissive-period zone time matches the field (P1 3.4, P5 2.5, P3 4.4, P7 2.2 s).
- **Chosen**: P1 0, P5 3, P3 3, P7 3 m. P1's value did not change with u (7.5–8.5 s), so the rule fell to 0.
- **Result**: V1 24/29 FAIL, V2 16/35 FAIL. **Mistake in my grid**: u = 0 leaves only the junction part, and a WB
  left car stopped at the stop line on red is never on it, so P1 was almost never called. Recorded as a failure.

## Finding — GDOT's zone counts include radar dropouts (2026-11-20)

- **Data**: T&A charts, train days (`measure_dropouts.py`). An activation that starts and ends while its
  movement has no green (and spans no green start) cannot be a car leaving: the radar lost a stopped car and found
  it again. Share of activations: EB_L 0.07, NB_L 0.19, SB_L 0.43, SB_T 0.65, NB_T 0.61. Model: 0.00–0.08.
- **Meaning**: GDOT counts such a car two or more times. Step C had matched the model to these inflated counts.

## Attempt 13 — counts without dropouts (2026-11-20)

- **Change**: left zones u = 3 m for all four (smallest value that covers a car stopped at the stop line). Step C
  target = GDOT count × (1 − dropout share), model dropouts removed the same way; grid extended down to 0.6.
- Demand factors: NB_L 1.4, NB_T 0.6, NB_R 1.2, SB_L 1.4, SB_T 1.0, SB_R 1.2, EB_L 1.4. Confirmation ratios
  0.99–1.03 for every movement except SB_L (0.75) — the first time the counts are reproduced.
- **Result**: V1 22/35 FAIL (P4/P8 greens 5–11 s too short), V2 11/35 FAIL. P1 now close (gap-out +4 to +16).

## Exploration — side-street through zone shape (2026-11-20, not an attempt)

- `explore_thruzones.py`: zone = u m before + d m after the stop line, 9 shapes, train days.
- Field through zone: occupied when the green starts in only 29 % of greens, clears ~3 s after green start, 61–65 %
  dropouts. Model: any u ≥ 2 m → occupied at green start in 76–94 % (every SUMO driver stops on the same spot);
  u = 0 → 0 %; dropouts always 0. **No shape reproduces the field zone's behaviour.**

---

## Why the newer attempts pass the green-length check (V1) less often

| attempt | V1 pairs within 3 s | what set the side-street through green length |
|---|---|---|
| 8 | 34/35 ✓ | fitted 4–8 s gap time + estimated demand factors (NB_T 1.5, SB_T 2.3) |
| 9 | 28/35 ✗ | measured ~3.4 s gap time, 12 m zones → greens end 2–6 s early |
| 10 | 31/35 ✓ | long through zones (36 / 20 m) + inflated demand (NB_T 3.2, SB_T 2.8) |
| 11 | 33/35 ✓ | same as 10 |
| 12 | 24/29 ✗ | P1 almost never called (grid mistake) |
| 13 | 22/35 ✗ | dropouts removed → demand NB_T 0.6, SB_T 1.0 → P4/P8 greens 5–11 s short |

An actuated green lasts as long as cars keep arriving within the gap time. Two things set it: **how many cars
come** and **how long each car keeps the zone on**. Neither is measured directly at 137:
- The number of side-street through cars is hidden inside GDOT's "count", which is zone activations. It is
  pushed UP by radar dropouts (one stopped car counted 2+ times) and pushed DOWN by queues (several cars in a row
  counted once). The closed loop can untangle the two only if the model's zone behaves like GDOT's zone — and the
  exploration shows it does not.
- Attempts 10–11 passed V1 because two errors cancelled: zones too long (each car holds the green too long) and
  demand ~3× too high (counting dropouts as cars). Attempt 13 removed the dropout error (counts now honest) but
  kept the long zones, and the model's long zone turns a queue into one activation, so the closed loop now gives
  too FEW cars → short greens.
- So V1 got worse because the remaining error is no longer hidden by a second error. The weak link is the
  side-street through demand, which depends on how the radar zone behaves, which SUMO's detectors cannot copy.

Open decision (2026-11-20): (a) keep measured gap times and report V2 failing; (b) gap time per phase as an
"effective" value fitted on train days, disclosed; (c) use attempt 8 for the Nov 30 runs and continue v3 later.
