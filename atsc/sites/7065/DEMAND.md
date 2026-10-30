# SIG 7065 demand audit (Phase 1.4)

2026-10-30. Train (Jul 10 – Aug 31) and validation (Sep 1 – Oct 3) days only. The locked test set (Oct 4–22) is not read: `atsc/sim/demand.load_counts` skips those rows unless `allow_locked=True`, which is reserved for the final evaluation.

Source: `intersections/7065/counts/tmc_7065_5min.csv` (GDOT ATSPM Turning Movement Counts, 5-min bins, exact integers). Outage rule from the scraper: ≥ 3 consecutive all-zero bins → `outage`, counts blank.

Reproduce: `uv run python atsc/sites/7065/audit_demand.py` (tables below, `demand_audit/days.csv`, `demand_audit/flagged_bins.csv`), then `uv run python atsc/sites/7065/check_demand.py 2026-07-16` (simulation check).

## 1. Counts → network

GDOT labels approaches by road direction, not compass (`phase_map.json` `count_labels`). Mapping in `movements.json`:

| GDOT column | Leg (compass) | Phases | Lanes | Counted by |
|---|---|---|---|---|
| NB_L / NB_T | SW, Peachtree | P1 / P6 | 2 / 3 | stop-bar / upstream zones |
| SB_L / SB_T | NE, Peachtree | P5 / P2 | 2 / 3 | stop-bar / upstream zones |
| EB_L / EB_T | N, Piedmont | P3 (+ P4 permissive) / P8 | 1 / 2 | stop-bar / upstream zones |
| WB_L / WB_T | S, Piedmont | P7 (+ P8 permissive) / P4 | 1 / 2 | stop-bar / upstream zones |

Detection is radar (Wavetronix Matrix / Advance) and video, not loops (`DETECTORS.md`); "setback" below means an upstream count zone.

Right turns are not counted by GDOT (no count detector on the right lanes) and carry **no demand**.

## 2. Day quality

Rules as `tools/dataset_7065.py`: complete = no outage bin; usable = ≤ 30 min of outage 06:00–22:00; suspect = one movement at 0 for ≥ 2 h of daytime while the others count; bad = more outage.

| Set | Weekday | Saturday | Sunday | Holiday |
|---|---|---|---|---|
| Train | 22 complete, 9 usable, 6 bad | 7 complete | 3 usable, 5 bad | — |
| Validation | 17 complete, 3 usable, 3 bad | 5 complete | 1 usable, 3 bad | 1 usable (Labor Day) |

**Usable for the study: 51 weekdays (31 train, 20 validation) and 12 Saturdays.** No suspect days in either set (the two suspect days, Jul 6–7, are outside the split). Outage bins inside usable days generate no traffic and are listed per route file (`*.rou.xml.meta.json`, `outage_windows_s`) so evaluation can mask them.

## 3. Physically impossible bins

Bound per movement and 5-min bin: lanes × 2,400 veh/h/lane (1.5 s headway, a physical ceiling well above HCM's 1,900 base) × the most green + yellow the movement's phases can get in any 300 s window under the plan(s) in effect, computed by running the NEMA engine with every other phase at its minimum (`demand.max_service`). Setback-counted movements add the queue that fits between the upstream zone and the stop line (counted, not yet discharged; 7 m per car).

| Movement | Bins above the bound (usable days) | Share of its vehicles | Bins above the same bound at 1,900 |
|---|---|---|---|
| EB_T (Piedmont N through, P8) | **5 bins on 5 days** | 0.12 % | 19 |
| every other movement | 0 | 0 | 0–1 |

All flagged bins are EB_T (`demand_audit/flagged_bins.csv`). The five on usable days are all the **18:10** bin (Jul 16, Jul 21, Aug 12, Sep 21, Sep 24); two more are on bad days (Aug 4 17:25, Aug 18 16:40). EB_T has a 18:05–18:20 burst on a few days only (max 184–212 vehicles per bin against a median of ~90), consistent with over-counting in stop-and-go queues (the sub-second hit spacing noted in `intersections/7065/timing/capacity_check/README.md`; with radar/video detection, a long vehicle read twice or a split track, rather than the loop double pulses assumed there). **Kept as recorded** (fidelity policy); they are 0.12 % of EB_T and are reported, not removed.

### Finding: Piedmont-N through is saturated in the field, and its count is a discharge count

Over 51 weekdays, the EB_T median per 5-min bin during plan C (180 s cycle) repeats with a 15-min period (e.g. 17:00–17:10: 80 / 92 / 100; 17:15–17:25: 82 / 93 / 98). 15 min is the least common multiple of the 180 s cycle and the 300 s bin, so the count follows the number of P8 greens in each bin. A detector counting free arrivals would not show the signal's rhythm. **The queue therefore stands over the N upstream count zones for much of the PM, and those zones count vehicles discharging.**

The implied discharge rate is ~1,080 veh/h over P8's ~48 s of green per 180 s cycle, about **2,000 veh/h per lane of green**. That is high, above HCM's 1,900 base. One reason it could be inflated: see the open item on zone position (§5).

Median EB_T flow during plan C runs at **1,169 veh/h per lane of the *maximum possible* P8 green + yellow** (p99 1,746). The other through movements are at 100–390. P8 is the one critical movement in the PM.

## 4. Demand generation (`atsc/sim/demand.write_routes`)

- One vehicle per counted vehicle at a uniformly random time in its 5-min bin (Poisson arrivals with the measured count; counts per bin exact).
- Each vehicle departs early by its free-flow time from the network entry to the detector that counted it, so it reaches that detector within its bin.
- Explicit routes entry → approach → exit, each crossing 7065 exactly once.
- Entries: N 258 m, S 291 m, NE 320 m (network edge, beyond 7071/7058), SW 144 m (just upstream of 7066). Neighbouring signals run unsignalised (`atsc/sim/run.start`).
- vType: SUMO passenger defaults. Driver parameters (sigma, tau) are fitted in 1.5, not here.
- **`departLane="random"`** (see below).

### Lane use: the problem and the fix

GDOT's export has movement totals only (no per-lane volumes), so the target is HCM's lane-utilization factors. The busiest lane carries ≈ 37 % of a 3-lane movement and ≈ 52 % of a 2-lane one.

The first check (`departLane="best"`) put SW through at 81 / 19 / 0 % across its three lanes at the upstream detectors and NE through at 75 / 1 / 24 %, which wastes about a third of their capacity. There were two causes:

1. Where one upstream lane fans out into two stop-bar lanes, SUMO sends every vehicle to the first of them, and SUMO's lane-changing barely rebalances queues. Raising lcSpeedGain to 5–10 or setting lcKeepRight to 0 changed nothing.
2. OSM wiring artifacts:
   - **NE:** a 4→6-lane widening on a 1.9 m micro-edge. Rewired, `GEOMETRY.md` fix 4.
   - **SW:** a 2-lane stretch 119 m long upstream of a 2→3 fan-out. The entry was moved to the 3-lane edge after it.

The SW left bay was later corrected to the measured tapers (`GEOMETRY.md` fix 5); rerunning the check gave the same lane shares and counts within ±1 %.

Results after the fixes, Jul 16 14:30–19:30, real GDOT plans, gap-out 2 s. Each cell is the share per lane at the upstream detectors / at the stop bar.

| departLane | SW through (3) | NE through (3) | N through (2) | S through (2) |
|---|---|---|---|---|
| best | 79 / 19 / 2 · 55 / 29 / 16 | 73 / 25 / 2 · 49 / 31 / 21 | 57 / 43 · 54 / 46 | 62 / 38 · 52 / 48 |
| free | 78 / 18 / 4 · 55 / 28 / 17 | 78 / 19 / 3 · 50 / 29 / 21 | 56 / 44 · 54 / 46 | 84 / 16 · 59 / 41 |
| **random** | **33 / 33 / 34 · 31 / 35 / 34** | **45 / 30 / 24 · 39 / 33 / 29** | **53 / 47 · 54 / 46** | **59 / 41 · 52 / 48** |

`random` is adopted. Left-turners inserted in a through lane make their strategic lane change over the 144–320 m of approach.

### Simulation check, Jul 16 14:30–19:30 (`demand_audit/check/2026-07-16.md`)

| Movement | GDOT count | Sim counting detectors |
|---|---|---|
| NB_T / SB_T / WB_T | 1,500 / 3,160 / 1,889 | 1,501 / 3,164 / 1,894 |
| SB_L / WB_L | 1,099 / 205 | 1,104 / 204 |
| NB_L | 747 | 846: lane changes inside the 12 m stop-bar zones are counted twice; dual-left use 66 / 34 % |
| EB_T / EB_L | 5,553 / 742 | 5,039 / 660, with **up to 633 vehicles waiting to enter** the N leg |

0 teleports. Throughs and lefts on three legs reach their detectors as counted. The N leg does not: P8 cannot discharge the counted flow under real plans in the simulation, so the queue reaches the network edge. This is the known capacity question, and it belongs to **1.5**.

## 5. Open items

- **Upstream-zone position vs. turn bays.**
  - The assumed 79 m (Peachtree's published 260 ft) lies *upstream* of the N-leg bays (40 m, student check) and of the SW left-lane tapers (71 m and 43 m, student check 2026-10-30). The S-leg bay (≈ 90 m real, 86 m sim) and the NE bay (92 m) contain it.
  - In the simulation, the N and SW upstream zones therefore also see left-turners (EB_L, NB_L above), which affects gap-out.
  - In the field, the same would hold if GDOT's zones sit at 79 m: the EB_T (and NB_T) counts would include turners, inflating the P8 count (§3) and the capacity puzzle.
  - Detection is radar/video (no loops), so the distance cannot be read from the pavement. Only source: GDOT's ATSPM detector configuration ("distance from stop bar"). Until then, 79 m stays a disclosed assumption.
- **SW dual-left lane use 66 / 34 %** (fan-out at the bay entry). Left demand there is low (≈ 150 veh/h PM); revisit if P1 turns out critical.
- **Storage-exceedance recording** (`GEOMETRY.md`) is not implemented yet; it goes with the evaluation metrics.
