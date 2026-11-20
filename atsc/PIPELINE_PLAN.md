# Intersection model + validation, v3 plan — tighter, more faithful, reusable

Written 2026-11-20 after the midterm. Goal: (1) the simulated controller behaves as much like the real GDOT
controller as the ATSPM portal lets us measure; (2) validation is independent of tuning and tied to outcomes;
(3) a new intersection goes from signal ID to validated model by running the same stages, not by hand-written
site scripts. Nothing here is started. Items marked **(decide)** need the user.

---

## 0. What is wrong with the current (137) setup — the reasons for v3

| # | Weakness | Where it shows |
|---|---|---|
| W1 | Many controller settings are **assumed or defaulted**, not measured: P1 clearance (copied from P5), walk 4 s, detector call delay/extend, max greens, recall, dual entry, phase omits, transitions | `README.md` deviations list, VALIDATION attempts 1–7 |
| W2 | **Discharge (saturation flow) never calibrated**; passage time can absorb that error (P8 fitted at 8 s = grid edge); undercount estimate uses HCM 1.9 s while the sim discharges at ~2,100 veh/h/ln | VALIDATION attempt 8, sat_flow.py |
| W3 | **Tuning and validation use the same measure** (passage fitted to gap-out share; V2 checks gap-out share); V1 and V2 are not independent | VALIDATION criteria |
| W4 | The **20 validation days were reused for 8 attempts**; V2 passed at exactly 28/35; no uncertainty reported | VALIDATION, INTERPRETATION |
| W5 | **No outcome check** (delay, queues, split failures); P2/P6 (58 % of cars) not scored; skips fail (18/35); free/night mode not checked | VALIDATION |
| W6 | Demand correction checked only indirectly; no per-movement closed-loop check | VALIDATION finding 09:30, attempt 4 |
| W7 | **Site-specific scripts** (`left_turn_clearance_137.py`, `estimate_137_presence.py`, `offset_138.py`, `make_signal.py` constants) — a new site means re-writing them | tools/lanecheck, atsc/sites/137 |

## 1. Data layer — use every ATSPM product, read it once, keep provenance

The portal returns chart images (T&A, Split Monitor, PCD …) plus a few exact numbers (TMC JSON, Approach Volume
totals, Split Monitor header). One package `atspm/` (moving today's `tools/atspm_*.py`) with, per product:
`fetch(sig, window) → cache`, `parse(cache) → tidy table`, and a provenance record (URL payload, date, parser
version, read errors).

| ATSPM product | Gives | Use in v3 |
|---|---|---|
| Turning Movement Counts (MT 5) | 5-min counts per movement | demand (with zone-type check) |
| Approach Volume (MT 7) | exact window totals, advance + stop-bar | cross-check counts; upstream zones (window trick) |
| SignalDetail config | detectors: type, lane, distance, approach | network detectors; **auto-classify count vs presence zones** |
| Timing & Actuation (MT 17) | per-cycle phase intervals, detector on/off, calls (43/44), ped intervals, overlaps | the main measurement source: clearances, min/max greens, passage, call delay, recall, ped timing, discharge headways, occupancy |
| Split Monitor (MT 12) | per-plan splits; % gap/force/max/skip (exact header numbers) | plan schedule; validation (behaviour) |
| Plans chart (MT 2) | plan number by time of day | schedule |
| Purdue Coordination Diagram | arrivals vs green, cycle, offsets | offsets to neighbours; arrivals-on-green validation |
| Purdue Phase Termination | per-cycle termination type | per-cycle validation (distributions, not just %) |
| Purdue Split Failure | cycles where the queue did not clear | **outcome validation (queues)** |
| Approach Delay | delay per approach (advance detectors) | **outcome validation (delay)**, main street |
| Arrivals on Red | arrival platooning | neighbour/coordination check |
| Left Turn Gap Analysis | gaps in opposing flow for permissive lefts | permissive left-turn calibration (open V3/skip issue) |
| Wait Time | call-to-green wait | outcome validation, side streets |
| Pedestrian Delay | ped calls and waits | pedestrian rates per hour, per day |
| Yellow & Red Actuations | vehicles entering on yellow/red | clearance/driver behaviour sanity check |
| Preemption Details | preemption events | flag/exclude affected days |

First task (**probe**, ~1 day): for each product, record whether the portal returns exact numbers anywhere
(headers, legends, tooltips, CSV/data-export buttons, raw-event option) before writing any image parser. Exact
numbers replace pixel reading wherever they exist.

## 2. Controller replica — every parameter measured or explicitly assumed

A **parameter registry** per site (`params.json`): each controller/driver/demand parameter with value, source
(product + windows), method, sample size, and status `measured | fitted | assumed | default`. The model builder
reads only the registry; the report card prints every non-`measured` row.

| Parameter (per phase / plan) | Measurement from the event charts (T&A unless noted) |
|---|---|
| Phase → movement map, rings, barriers, lead/lag, sequence per plan | phase titles + T&A order per cycle (detect sequence changes by plan) |
| Yellow, red clearance (every phase, incl. P1) | median interval length per phase |
| Min green | shortest green ending in gap-out with no ped call |
| Max green / splits, cycle, offset, coordinated phases | Split Monitor + T&A force-off points; PCD for offsets |
| Force-off mode (fixed / floating) per phase | where force-offs fall in the cycle vs split (generalises `force_off_mode.py`) |
| Passage time | time from last detector-off to gap-out (direct, not fitted to gap-out share → removes W3) |
| Detector call delay / extend, locking | detector-on → call (43) → green; detector-off → call drop (44) (generalises 137 finding) |
| Vehicle / max / ped recall | phase served with no call; green always to max |
| Dual entry, conditional service, skips | partner-phase service when no call; skip patterns per plan |
| Ped walk, FDW, recall, push rates per hour | ped intervals + Pedestrian Delay |
| FYA / permissive behaviour, overlaps (right-turn overlaps) | overlap rows in T&A |
| Plan transitions, free (night) operation | T&A across plan boundaries; night bands |
| Neighbour signals within ~400 m | same pipeline, run upstream with their own plans; offsets from PCD/T&A |

Engine work (`atsc/sim/nema.py`): add only what the measurements show is used (call delay, dual entry,
conditional service, transitions), each with a unit test.

## 3. Traffic and drivers — calibrate in a fixed order so errors cannot hide in each other

1. **Discharge first.** Saturation headways and start-up lost time from stop-bar occupancy during queued greens
   (T&A, train days) → calibrate SUMO car-following (`tau`, `sigma`, `accel`) per site. Fixes W2.
2. **Demand second.** Counts per movement; zone type from SignalDetail; presence-zone undercount estimated with
   the **measured** headway (not HCM); right turns, driveways, neighbour inflow handled by explicit rules.
   **Closed-loop check:** simulated zone activations per movement vs GDOT's raw reported counts (±10 %). Fixes W6.
3. **Permissive lefts third.** Gap acceptance from Left Turn Gap Analysis + T&A clearance timing.
4. **Controller settings last**, all direct measurements (section 2); nothing fitted to a validation measure.

Every step has its own pass bar, written before it runs (e.g. headway CDF within X; activations within ±10 %).

## 4. Validation — independent, outcome-level, with uncertainty

- **Days.** Calibration days and validation days never mix; validation days are opened once per attempt and every
  attempt is logged. Prefer validating on a **fresh block** (e.g. later weeks) **(decide)**; report pass rates
  under a **bootstrap over days**, not one count. Fixes W4.
- **Thresholds from the field's own variability:** a case passes when the sim's median error is within the
  field's day-to-day spread (e.g. interquartile range) for that case, with a hard cap. Written before running.
- **Three levels, all from ATSPM, none used in calibration:**
  1. *Controller behaviour (per cycle):* distributions of green length, termination type, skips, cycle length —
     every phase including coordinated P2/P6, and night free mode.
  2. *Detectors:* actuation counts and occupancy per detector.
  3. *Outcomes:* split-failure share, arrivals on green, approach delay (where advance detectors exist), wait time.
- Acceptance needs levels 1 and 3. A failed check is diagnosed on calibration-day data only (as now).

## 5. Making it reusable — one pipeline, one site file

```
atsc/sites/<id>/site.json   signal id, name, neighbours, study period, day split, exclusions — the only hand-written file
atsc/pipeline/              stages, each idempotent, cached, with provenance:
  1 fetch      all ATSPM products for the period            → intersections/<id>/
  2 screen     day quality, outages, plan changes, preemption → quality report
  3 network    OSM + lane/detector check vs SignalDetail       → network/ (flags mismatches for the user)
  4 controller measure section-2 parameters                    → params.json (registry)
  5 discharge  calibrate driver model                          → params.json
  6 demand     counts + corrections + closed-loop check        → demand/
  7 validate   section-4 checks                                → VALIDATION report card
  8 evaluate   methods on locked test days                     → eval/
uv run python -m atsc.pipeline <id> <stage>      # or: all
```

- Site-specific code moves into the pipeline as general functions (137's `estimate_137_presence.py`,
  `left_turn_clearance_137.py`, `offset_138.py`, `force_off_mode.py`).
- **Report card** per site (markdown, auto-generated): data coverage, registry with every assumed value,
  each pass bar and result, deviations list. This is what the thesis appendix cites.
- **Regression test:** running the pipeline on 137 must reproduce the accepted attempt-8 model within tolerance
  before it is trusted on a new site.
- Onboarding a new signal = write `site.json`, run `all`, resolve the flagged items. Screening for candidates
  already exists (`tools/atspm_signals/`).

## 6. Order and timeline (against the dates promised at the midterm)

| When | What |
|---|---|
| by 11-30 | **Promise first:** SARSA(λ) and DQN on the current, accepted 137 model (unchanged), same test protocol. In parallel: section-1 probe and the parameter registry for 137 (measure only, no model change). |
| 12-01 → 12-12 | Pipeline stages 1–7 (sections 2–5), regression-tested on 137. |
| 12-12 → 12-19 | Second (busier) site through the pipeline: validated model + all methods on its locked test days. |
| 12-20 → 01-20 | Thesis writing; any 137 rebuild only as a disclosed check (see D1). |

## Decisions needed

- **D1 (decide). What happens to 137's results if the v3 model differs?** 137's test days have already been opened,
  so new 137 numbers on the same days are a second look. Proposal: keep the accepted 137 model as the thesis model
  for 137; run v3 on 137 only as a **validation comparison** (does the tighter model change the ranking?), reported
  as such; use v3 fully on the second site.
- **D2 (decide). Second site:** 7065 (busy, but its Peachtree through counts are presence-zone undercounts and its
  test set is 10-04..10-22) or a new screened signal chosen for contrast (near capacity, more lanes/phases, count
  zones on the main street).
- **D3 (decide). Validation day scheme** for the new site: one fresh block, or k-fold by week with a final fresh block.
- **D4 (decide). Scope cap:** if the portal probe shows a product can only be read from images, is it worth a parser
  before 12-19, or deferred? Proposal: Split Failure and Phase Termination now (outcome + per-cycle); the rest later.
