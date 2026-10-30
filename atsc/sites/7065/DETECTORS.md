# SIG 7065 field detector layout (Phase 1.2)

Source: **GDOT ATSPM configuration table** (`intersections/7065/config/detectors.csv`, scraped 2026-10-30 by `tools/atspm_config.py` from the public SignalDetail page: hardware, detection type, lane, distance from stop bar per channel), plus Timing & Actuation charts 2026-10-02 08:00–08:05 (`intersections/7065/timing/dircheck/2026-10-02_0800_lanecount/`) for which lane each channel watches. Machine-readable copy: `detectors.json`.

Leg and phase names as in `GEOMETRY.md` (GDOT labels by road, not compass).

**Hardware: no inductive loops** (student, 2026-10-30; confirmed by the configuration table). Every lane channel is **Wavetronix SmartSensor Matrix** (side-fire radar near the stop bar, zones drawn in software). Each through approach also has one **Wavetronix SmartSensor Advance** channel (approach-wide upstream radar, "Advanced Count"). Zone positions are configuration values, not visible on the pavement. "Upstream count zone" below = a Matrix "Lane-by-lane Count" channel.

| Phase | Leg / movement | Lanes | Stop-bar presence, Matrix (channel) | Upstream count zones, Matrix (channel) | Advance radar (channel, distance) |
|---|---|---|---|---|---|
| P1 | SW left | 2 | L1 ch1, L2 ch2 (also count) | none | — |
| P2 | NE through | 3 | T1 ch21, T2 ch22, T3 ch23 (also tagged count) | T1 ch24, T2 ch25, T3 ch26 | ch20, **260 ft / 79 m** |
| P3 | N left | 1 | L1 ch33 (also count) | none | — |
| P4 | S through (+ R lane) | 2 + R | T1 ch52, T2 ch53, R3 ch54 | T1 ch55, T2 ch56 | ch51, distance blank |
| P5 | NE left | 2 | L1 ch17, L2 ch18 (also count) | none | — |
| P6 | SW through | 3 | T1 ch5, T2 ch6, T3 ch7 (also tagged count) | T1 ch8, T2 ch9, T3 ch10 | ch4, **260 ft / 79 m** |
| P7 | S left | 1 | L1 ch48 (also count) | none | — |
| P8 | N through (+ R lane) | 2 + R | T1 ch37, T2 ch38, R3 ch39 | T1 ch40, T2 ch41 | ch36, distance blank |

**Distance of the Matrix count zones: not in GDOT's configuration** (blank for every Matrix channel). The 260 ft that the PCD shows belongs to the Advance channels, not to the count zones, so the earlier reading "count zones at 79 m on Peachtree" was wrong. Evidence on where they are: on the P8 chart (Oct 2 08:00), after the green ends at 08:02:15 the count channels keep firing for 15–35 s (≈ 7 vehicles in T1, ≈ 10 in T2) and then stop until the next green, i.e. the zone sits behind 7–10 queued cars, **roughly ≥ 50 m** (7 m per car; more if the queue had not cleared). The simulation keeps 79.2 m for all four legs as a **disclosed assumption** until a multi-cycle estimate is made from the T&A charts (open item below).

Notes:
- Upstream count zones fire during red (vehicles pass them before joining the queue); stop-bar presence does not count passing traffic during red (`intersections/7065/timing/capacity_check/README.md`).
- Right-turn lanes (R3) have presence only, no count zone, consistent with right turns missing from the count report.
- On P2/P6 the configuration also tags the stop-bar channels as "Lane-by-lane Count". Which set feeds the turning-movement report is not stated by ATSPM; a rough tally of the 08:00 chart (one on/off pair per vehicle) is consistent with the setback set only (P2: report 49 per 5 min). Treated as: **through counts = upstream zones; left counts = stop-bar zones.**
- **The PCD (arrivals-on-green) for P4/P8 is not usable:** it uses the Advance channel (ch36/ch51), whose distance GDOT left blank, and its volume line reads ~50–100 veh/h against ~1,100 veh/h counted. P2/P6 PCD volumes also read low (≈ one lane). ATSPM arrivals-on-green is therefore not used for validation.

## Open

- **Matrix count-zone distance (all four through approaches).** Not in GDOT's configuration. Estimate from red-phase counts in Timing & Actuation charts over many cycles (vehicles counted between end of green and the zone going silent ≈ cars queued in front of it). One P8 chart says ≥ ~50 m. Until then 79.2 m, disclosed.
  Why it matters (`DEMAND.md` §5): if the N (P8) zones sit upstream of the 40 m bays, they also see left- and right-turners, both in the simulation and possibly in GDOT's EB_T count; the same on SW (left tapers start at 71 m and 43 m, student check 2026-10-30).
- **Advance radar channels (ch4, 20, 36, 51)** are listed in `detectors.json` (`"modelled": false`) but not in the simulation yet. GDOT's controller may use them (e.g. dilemma-zone extension); they are a candidate input for the controllers in Phase 2.
- **Stop-bar presence zone length.** Not published. Assumed 12 m (40 ft, a common stop-bar presence zone length), disclosed as an assumption; it only affects how long a call stays on, i.e. the actuated controller's gap-out behaviour, which Phase 1.6 checks against recorded green times.

## How the simulation uses it

- Stop-bar presence → SUMO lane-area detector (e2) of the zone length, ending at the stop line, one per lane.
- Upstream count zone → SUMO induction loop (e1) at the assumed distance, one per through lane (a point detector standing in for a short radar/video zone).
- Every controller reads only these detectors (vehicle counts, occupancy, presence), never SUMO's lane vehicle lists.

## Built and checked (2026-10-29)

`uv run python -m atsc.sim.detectors atsc/sites/7065` → `network/detectors.add.xml` (28 Matrix channels; the 4 Advance channels are not modelled). Upstream count detectors are placed by walking each lane upstream through its straight predecessors, so P8's sit on the 2-lane section above the 40 m bay and P6's on the 3-lane edge 46–92 m upstream.

Check with the smoke-test flows (every movement, 10 min): each stop-bar zone counts exactly the vehicles routed through its lane group (lefts 50/50 per movement, rights 10/10, SW stop bar 60 = 50 through + 10 right on the shared lane). Upstream detectors, with vehicles entering upstream of them: 50/50 on SW and N.

**Note for the demand build (1.4):** in that check every vehicle stayed in the lane it was inserted in (light traffic, no reason to change lanes), so per-lane detector readings depend on how vehicles are spread across lanes at insertion. Demand must insert far enough upstream and spread across lanes (e.g. `departLane="best"` with enough distance, or `"random"`), otherwise per-lane occupancy and gap-out are distorted.
