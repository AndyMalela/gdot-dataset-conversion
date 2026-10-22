# Simulation — signal 137 (W. Paces Ferry Rd  @  E. Andrews Dr/Slaton Dr)

Quality-check simulation built by `tools/build_sim.py` from the real data for **2026-10-02**: network = OpenStreetMap (tools/osm_build.py), measured 5-min turning-movement counts, and the real time-of-day signal plans.

```bash
cd intersections/137/sim
sumo-gui -c gui.sumocfg     # 07:45-09:00, press play
sumo -c sim.sumocfg         # full day, headless
```

## Demand (measured counts)

| Movement | Vehicles in the day |
|---|---|
| EB_L | 1859 |
| NB_L | 509 |
| NB_R | 839 |
| NB_T | 612 |
| SB_L | 2164 |
| SB_R | 1409 |
| SB_T | 908 |
| WB_TR | 7747 |

16047 vehicles in 2227 five-minute flows. Each flow starts upstream of the approach and passes the intersection.

## Signal (real plans)

Signal `69545429`. Schedule:

00:00 **Actuated** (104 s) · 06:31 **A** (130 s) · 10:02 **B** (120 s) · 14:01 **C** (140 s) · 20:01 **D** (110 s) · 22:01 **Actuated** (104 s)

Phase → movement: `../timing/phase_map.json` (from GDOT's Split Failure chart titles); splits: `../timing/timing_plan_137.md`.

### Actuation parameters

| Phase | Min green (s, measured) | Max green in actuated periods (s) |
|---|---|---|
| P1 | 5.1 | 10 (95th percentile of phase times (lower bound)) |
| P2 | 12.1 | 72 (max-out dots) |
| P3 | 5.2 | 11 (95th percentile of phase times (lower bound)) |
| P4 | 7.7 | 18 (95th percentile of phase times (lower bound)) |
| P5 | 5.1 | 10 (max-out dots) |
| P6 | 12.0 | 152 (95th percentile of phase times (lower bound)) |
| P7 | 5.2 | 15 (max-out dots) |
| P8 | 7.8 | 12 (95th percentile of phase times (lower bound)) |

## Validation against the recorded signal (2026-10-02)

Vehicle extension chosen: **4.0 s through phases, 3.0 s left-turn phases** (grid 1.0, 2.0, 3.0, 4.0 × 2.0, 3.0, 4.0, 6.0, 8.0), mean absolute error of median green per phase: **6.3 s**.

| Window | Phase | Recorded median green (s) | n | Simulated median green (s) | n |
|---|---|---|---|---|---|
| 08:00 | P1 | 9.7 | 2 | 9.0 | 7 |
| 08:00 | P2 | 82.3 | 6 | 62.0 | 7 |
| 08:00 | P3 | 9.7 | 4 | 9.0 | 7 |
| 08:00 | P4 | 22.4 | 7 | 26.0 | 7 |
| 08:00 | P5 | 9.7 | 3 | 6.0 | 5 |
| 08:00 | P6 | 88.2 | 6 | 68.0 | 7 |
| 08:00 | P7 | 8.9 | 5 | 8.0 | 7 |
| 08:00 | P8 | 20.8 | 5 | 27.0 | 7 |
| 17:00 | P1 | 9.6 | 4 | 10.0 | 5 |
| 17:00 | P2 | 83.2 | 5 | 70.0 | 6 |
| 17:00 | P3 | 8.7 | 3 | 9.0 | 6 |
| 17:00 | P4 | 26.7 | 6 | 30.0 | 6 |
| 17:00 | P5 | 9.6 | 4 | 9.0 | 6 |
| 17:00 | P6 | 89.1 | 5 | 71.0 | 6 |
| 17:00 | P7 | 8.8 | 5 | 8.0 | 7 |
| 17:00 | P8 | 22.5 | 6 | 30.0 | 5 |

## Assumptions and gaps

- ASSUMPTION: shared-lane column WB_TR is split equally between its 2 movements (T, R); the real split is not measured.
- Arrivals: Poisson within each 5-min bin with the measured count (random times, seed 12345); counts per movement per bin are exact.
- Yellow/red clearance not measured for phase(s) [1]: defaults 3.5 s / 2.0 s used.
- Offsets unknown (coordination with neighbouring signals not modelled).
- Max recall (full split every cycle, < 5% gap-outs on the Split Monitor): plan B: P3, P7.
- 'Actuated' periods (Free or uncoordinated) run actuated, uncoordinated, with max greens from Split Monitor max-outs where seen, otherwise the 95th percentile of observed phase times (a lower bound on the real max).
- Controller: SUMO NEMA actuated dual ring. Coordinated plans use the real splits as force-offs within the real cycle, phases 2/6 coordinated; other phases gap out / skip on 20 m stop-bar detectors. Vehicle extension 4.0 s through phases, 3.0 s left-turn phases (not published by GDOT; fitted to the recorded greens).
- 1 neighbouring signal(s) in the network area switched off (their timing is unknown); only the target signal is controlled.

## Quality check (07:00-09:30, headless)

- vehicles loaded 1988, inserted 1975, still waiting to enter at 09:30 0, still running 11
- teleports 0 (jams 0), collisions 0, SUMO warnings 37
- mean per trip: waiting 30.8 s, time loss 41.5 s, departure delay 0.7 s
- **PASS** (pass = no teleports, no collisions, no entry backlog at 09:30)
