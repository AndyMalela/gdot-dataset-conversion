# SIG 7065 field detector layout (Phase 1.2)

Source: Timing & Actuation charts 2026-10-02 08:00–08:05 (`intersections/7065/timing/dircheck/2026-10-02_0800_lanecount/`), and Purdue Coordination Diagram headers 2026-10-02 16:00 (`intersections/7065/timing/purdue_2026-10-02_1600/`). Machine-readable copy: `detectors.json`.

Leg and phase names as in `GEOMETRY.md` (GDOT labels by road, not compass).

**Hardware (student, 2026-10-30): no inductive loops.** Detection at 7065 is video cameras, Wavetronix SmartSensor Matrix (stop-bar radar, presence per lane zone) and Wavetronix SmartSensor Advance (upstream radar). Zones are drawn in software, so "setback loop" below means an upstream count zone, and its distance is a configuration value, not something visible on the pavement. The PCD's 260 ft for Peachtree is most likely the Advance distance setting. Which device feeds which channel is not published.

| Phase | Leg / movement | Lanes | Stop-bar presence (channel) | Upstream count zones (channel) | Upstream distance |
|---|---|---|---|---|---|
| P1 | SW left | 2 | L1 ch1, L2 ch2 | none (the presence channels also count) | — |
| P2 | NE through | 3 | T1 ch21, T2 ch22, T3 ch23 | T1 ch24, T2 ch25, T3 ch26 | **260 ft / 79 m** (PCD header) |
| P3 | N left | 1 | L1 ch33 | none | — |
| P4 | S through (+ R lane) | 2 + R | T1 ch52, T2 ch53, R3 ch54 | T1 ch55, T2 ch56 | **unknown** (PCD header blank) |
| P5 | NE left | 2 | L1 ch17, L2 ch18 | none | — |
| P6 | SW through | 3 | T1 ch5, T2 ch6, T3 ch7 | T1 ch8, T2 ch9, T3 ch10 | **260 ft / 79 m** (PCD header) |
| P7 | S left | 1 | L1 ch48 | none | — |
| P8 | N through (+ R lane) | 2 + R | T1 ch37, T2 ch38, R3 ch39 | T1 ch40, T2 ch41 | **unknown** (PCD header blank) |

Notes:
- Upstream count zones fire during red (vehicles pass them before joining the queue); stop-bar presence does not count passing traffic during red (`intersections/7065/timing/capacity_check/README.md`).
- Right-turn lanes (R3) have presence only, no count zone, consistent with right turns missing from the count report.
- On P2/P6 the chart also lists the stop-bar channels under "Lane-by-lane Count". Which set feeds the turning-movement report is not stated by ATSPM; a rough tally of the 08:00 chart (one on/off pair per vehicle) is consistent with the setback set only (P2: report 49 per 5 min). Treated as: **through counts = upstream zones; left counts = stop-bar zones.**
- **The PCD (arrivals-on-green) for P4/P8 is not usable:** its header has no detector distance and its volume line reads ~50–100 veh/h against ~1,100 veh/h counted. P2/P6 PCD volumes also read low (≈ one lane). ATSPM arrivals-on-green is therefore not used for validation.

## Open

- **Piedmont upstream-zone distance (P4, P8).** Not published, and not visible on the pavement (radar/video, no loops). Only source: GDOT's ATSPM detector configuration ("distance from stop bar"), if the student can reach it. Otherwise 260 ft as on Peachtree, **disclosed as an assumption**.
  **Raised in priority (2026-10-30, `DEMAND.md` §5):** 79 m lies upstream of the N-leg bays (40 m), so in the simulation the P8 zones also count left- and right-turners. If GDOT's real N zones are placed like that, the EB_T count includes turners too, which would inflate the P8 count. The same question applies to P6 (SW: Peachtree's published 79 m lies above the left-lane tapers, which start at 71 m and 43 m; student check 2026-10-30).
- **Stop-bar presence zone length.** Not published. Assumed 12 m (40 ft, a common stop-bar presence zone length), disclosed as an assumption; it only affects how long a call stays on, i.e. the actuated controller's gap-out behaviour, which Phase 1.6 checks against recorded green times.

## How the simulation uses it

- Stop-bar presence → SUMO lane-area detector (e2) of the zone length, ending at the stop line, one per lane.
- Upstream count zone → SUMO induction loop (e1) at the assumed distance, one per through lane (a point detector standing in for a short radar/video zone).
- Every controller reads only these detectors (vehicle counts, occupancy, presence), never SUMO's lane vehicle lists.

## Built and checked (2026-10-29)

`uv run python -m atsc.sim.detectors atsc/sites/7065` → `network/detectors.add.xml` (28 detectors). Upstream count detectors are placed by walking each lane upstream through its straight predecessors, so P8's sit on the 2-lane section above the 40 m bay and P6's on the 3-lane edge 46–92 m upstream.

Check with the smoke-test flows (every movement, 10 min): each stop-bar zone counts exactly the vehicles routed through its lane group (lefts 50/50 per movement, rights 10/10, SW stop bar 60 = 50 through + 10 right on the shared lane). Upstream detectors, with vehicles entering upstream of them: 50/50 on SW and N.

**Note for the demand build (1.4):** in that check every vehicle stayed in the lane it was inserted in (light traffic, no reason to change lanes), so per-lane detector readings depend on how vehicles are spread across lanes at insertion. Demand must insert far enough upstream and spread across lanes (e.g. `departLane="best"` with enough distance, or `"random"`), otherwise per-lane occupancy and gap-out are distorted.
