# Simulation — signal 7100 (SR 9  @  Lindbergh Drive)

Quality-check simulation built by `tools/build_sim.py` from the real data for **2026-10-02**: network = OpenStreetMap (tools/osm_build.py), measured 5-min turning-movement counts, and the real time-of-day signal plans.

```bash
cd intersections/7100/sim
sumo-gui -c gui.sumocfg     # 07:45-09:00, press play
sumo -c sim.sumocfg         # full day, headless
```

## Demand (measured counts)

| Movement | Vehicles in the day |
|---|---|
| EB_TL | 188 |
| NB_T | 7034 |
| NB_TR | 7994 |
| SB_L | 1876 |
| SB_T | 11375 |
| SB_TR | 7269 |
| WB_L | 1299 |
| WB_R | 2088 |
| WB_TL | 1371 |

40494 vehicles in 2611 five-minute flows. Each flow starts upstream of the approach and passes the intersection.

## Signal (real plans)

Signal `69536974`. Schedule:

00:00 **A** (120 s) · 06:15 **B** (140 s) · 14:46 **C** (160 s) · 19:32 **D** (130 s) · 21:45 **A** (120 s)

Phase → movement: `../timing/phase_map.json` (from GDOT's Split Failure chart titles); splits: `../timing/timing_plan_7100.md`.

### Actuation parameters

| Phase | Min green (s, measured) | Max green in actuated periods (s) |
|---|---|---|
| P2 | 12.0 | – |
| P3 | 7.1 | – |
| P4 | 6.0 | – |
| P5 | 4.2 | – |
| P6 | 12.0 | – |

## Validation against the recorded signal (2026-10-02)

Vehicle extension chosen: **2.0 s through phases, 4.0 s left-turn phases** (grid 1.0, 2.0, 3.0, 4.0 × 2.0, 3.0, 4.0, 6.0, 8.0), mean absolute error of median green per phase: **4.8 s**.

| Window | Phase | Recorded median green (s) | n | Simulated median green (s) | n |
|---|---|---|---|---|---|
| 08:00 | P2 | 101.2 | 6 | 97.0 | 7 |
| 08:00 | P3 | 7.0 | 2 | – | 0 |
| 08:00 | P4 | 28.5 | 6 | 29.0 | 6 |
| 08:00 | P5 | 9.6 | 5 | 10.0 | 5 |
| 08:00 | P6 | 89.9 | 6 | 86.0 | 7 |
| 17:00 | P2 | 123.2 | 5 | 107.0 | 6 |
| 17:00 | P3 | 8.8 | 2 | 8.0 | 4 |
| 17:00 | P4 | 25.1 | 5 | 25.0 | 6 |
| 17:00 | P5 | 15.6 | 6 | 9.0 | 5 |
| 17:00 | P6 | 98.6 | 5 | 107.0 | 5 |

## Assumptions and gaps

- ASSUMPTION: shared-lane column EB_TL is split equally between its 2 movements (T, L); the real split is not measured.
- ASSUMPTION: shared-lane column WB_TL is split equally between its 2 movements (T, L); the real split is not measured.
- Arrivals: Poisson within each 5-min bin with the measured count (random times, seed 12345); counts per movement per bin are exact.
- Links with no phase (always red): NB_L — movements with no signal phase in GDOT's configuration (prohibited or not modelled).
- Offsets unknown (coordination with neighbouring signals not modelled).
- Controller: SUMO NEMA actuated dual ring. Coordinated plans use the real splits as force-offs within the real cycle, phases 2/6 coordinated; other phases gap out / skip on 20 m stop-bar detectors. Vehicle extension 2.0 s through phases, 4.0 s left-turn phases (not published by GDOT; fitted to the recorded greens).
- 2 neighbouring signal(s) in the network area switched off (their timing is unknown); only the target signal is controlled.

## Quality check (07:00-09:30, headless)

- vehicles loaded 5557, inserted 5498, still waiting to enter at 09:30 0, still running 18
- teleports 0 (jams 0), collisions 0, SUMO warnings 8
- mean per trip: waiting 26.1 s, time loss 34.1 s, departure delay 0.8 s
- **PASS** (pass = no teleports, no collisions, no entry backlog at 09:30)
