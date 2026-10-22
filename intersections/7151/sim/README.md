# Simulation — signal 7151 (17th Street  @  Bishop Street)

Quality-check simulation built by `tools/build_sim.py` from the real data for **2026-10-02**: network = OpenStreetMap (tools/osm_build.py), measured 5-min turning-movement counts, and the real time-of-day signal plans.

```bash
cd intersections/7151/sim
sumo-gui -c gui.sumocfg     # 07:45-09:00, press play
sumo -c sim.sumocfg         # full day, headless
```

## Demand (measured counts)

| Movement | Vehicles in the day |
|---|---|
| EB_L | 1657 |
| EB_T | 6527 |
| NB_TL | 810 |
| SB_L | 823 |
| SB_TR | 1267 |
| WB_T | 6907 |
| WB_TR | 1097 |

19088 vehicles in 2397 five-minute flows. Each flow starts upstream of the approach and passes the intersection.

## Signal (real plans)

Signal `cluster_1278558749_283201123`. Schedule:

00:00 **Actuated** (75 s)

Phase → movement: `../timing/phase_map.json` (from GDOT's Split Failure chart titles); splits: `../timing/timing_plan_7151.md`.

### Actuation parameters

| Phase | Min green (s, measured) | Max green in actuated periods (s) |
|---|---|---|
| P1 | 6.0 | 25 (max-out dots) |
| P2 | 10.2 | 45 (max-out dots) |
| P6 | 10.2 | 45 (max-out dots) |
| P7 | 7.9 | 40 (max-out dots) |
| P8 | 7.8 | 40 (max-out dots) |

## Validation against the recorded signal (2026-10-02)

Vehicle extension chosen: **4.0 s through phases, 8.0 s left-turn phases** (grid 1.0, 2.0, 3.0, 4.0 × 2.0, 3.0, 4.0, 6.0, 8.0), mean absolute error of median green per phase: **6.6 s**.

| Window | Phase | Recorded median green (s) | n | Simulated median green (s) | n |
|---|---|---|---|---|---|
| 08:00 | P1 | 6.9 | 4 | 10.0 | 13 |
| 08:00 | P2 | 23.3 | 15 | 11.0 | 15 |
| 08:00 | P6 | 31.0 | 11 | 29.0 | 16 |
| 08:00 | P7 | 8.6 | 4 | 10.0 | 6 |
| 08:00 | P8 | 8.6 | 9 | 8.0 | 14 |
| 17:00 | P1 | 10.5 | 8 | 12.0 | 6 |
| 17:00 | P2 | 27.5 | 9 | 13.0 | 15 |
| 17:00 | P6 | 44.7 | 8 | 22.0 | 15 |
| 17:00 | P7 | 13.8 | 9 | 10.0 | 10 |
| 17:00 | P8 | 13.9 | 9 | 10.0 | 15 |

## Assumptions and gaps

- ASSUMPTION: shared-lane column WB_TR is split equally between its 2 movements (T, R); the real split is not measured.
- ASSUMPTION: shared-lane column NB_TL is split equally between its 2 movements (T, L); the real split is not measured.
- ASSUMPTION: shared-lane column SB_TR is split equally between its 2 movements (T, R); the real split is not measured.
- Arrivals: Poisson within each 5-min bin with the measured count (random times, seed 12345); counts per movement per bin are exact.
- Offsets unknown (coordination with neighbouring signals not modelled).
- 'Actuated' periods (Free or uncoordinated) run actuated, uncoordinated, with max greens from Split Monitor max-outs where seen, otherwise the 95th percentile of observed phase times (a lower bound on the real max).
- Controller: SUMO NEMA actuated dual ring. Coordinated plans use the real splits as force-offs within the real cycle, phases 2/6 coordinated; other phases gap out / skip on 20 m stop-bar detectors. Vehicle extension 4.0 s through phases, 8.0 s left-turn phases (not published by GDOT; fitted to the recorded greens).
- 2 neighbouring signal(s) in the network area switched off (their timing is unknown); only the target signal is controlled.

## Quality check (07:00-09:30, headless)

- vehicles loaded 2173, inserted 2172, still waiting to enter at 09:30 0, still running 19
- teleports 0 (jams 0), collisions 0, SUMO warnings 3
- mean per trip: waiting 10.8 s, time loss 16.9 s, departure delay 0.5 s
- **PASS** (pass = no teleports, no collisions, no entry backlog at 09:30)
