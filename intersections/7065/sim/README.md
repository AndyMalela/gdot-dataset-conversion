# Simulation — signal 7065 (SR 141  @  SR 237)

Quality-check simulation built by `tools/build_sim.py` from the real data for **2026-10-02**: network = hand-built network sumotwin/7065_ext.net.xml, measured 5-min turning-movement counts, and the real time-of-day signal plans.

```bash
cd intersections/7065/sim
sumo-gui -c gui.sumocfg     # 07:45-09:00, press play
sumo -c sim.sumocfg         # full day, headless
```

## Demand (measured counts)

| Movement | Vehicles in the day |
|---|---|
| EB_L | 2817 |
| EB_T | 14038 |
| NB_L | 2908 |
| NB_T | 6081 |
| SB_L | 3122 |
| SB_T | 10110 |
| WB_L | 1064 |
| WB_T | 7009 |

47149 vehicles in 2279 five-minute flows. Each flow starts upstream of the approach and passes the intersection.

## Signal (real plans)

Signal `J`. Schedule:

00:00 **E** (120 s) · 06:15 **A** (160 s) · 13:30 **B** (160 s) · 15:30 **C** (180 s) · 19:02 **B** (160 s) · 19:29 **D** (130 s) · 21:45 **E** (120 s)

Phase → movement: `../timing/phase_map.json` (from GDOT's Split Failure chart titles); splits: `../timing/timing_plan_7065.md`.

### Actuation parameters

| Phase | Min green (s, measured) | Max green in actuated periods (s) |
|---|---|---|
| P1 | 4.2 | 13 (95th percentile of phase times (lower bound)) |
| P2 | 7.8 | 53 (95th percentile of phase times (lower bound)) |
| P3 | 4.2 | 21 (95th percentile of phase times (lower bound)) |
| P4 | 6.0 | 43 (95th percentile of phase times (lower bound)) |
| P5 | 6.8 | 36 (95th percentile of phase times (lower bound)) |
| P6 | 7.8 | 71 (95th percentile of phase times (lower bound)) |
| P7 | 4.2 | 10 (95th percentile of phase times (lower bound)) |
| P8 | 6.0 | 43 (95th percentile of phase times (lower bound)) |

## Validation against the recorded signal (2026-10-02)

Vehicle extension chosen: **1.0 s through phases, 8.0 s left-turn phases** (grid 1.0, 2.0, 3.0, 4.0 × 2.0, 3.0, 4.0, 6.0, 8.0), mean absolute error of median green per phase: **4.2 s**.

| Window | Phase | Recorded median green (s) | n | Simulated median green (s) | n |
|---|---|---|---|---|---|
| 08:00 | P1 | 27.7 | 6 | 17.0 | 5 |
| 08:00 | P2 | 43.8 | 5 | 54.0 | 5 |
| 08:00 | P3 | 10.5 | 6 | 17.0 | 6 |
| 08:00 | P4 | 51.6 | 5 | 43.0 | 6 |
| 08:00 | P5 | 19.8 | 5 | 15.0 | 5 |
| 08:00 | P6 | 49.9 | 6 | 56.0 | 5 |
| 08:00 | P7 | 8.8 | 6 | 7.0 | 6 |
| 08:00 | P8 | 53.3 | 5 | 53.0 | 6 |
| 17:00 | P1 | 17.5 | 5 | 17.0 | 5 |
| 17:00 | P2 | 79.0 | 4 | 79.0 | 5 |
| 17:00 | P3 | 20.8 | 5 | 19.0 | 5 |
| 17:00 | P4 | 36.9 | 5 | 36.0 | 5 |
| 17:00 | P5 | 29.2 | 4 | 23.0 | 5 |
| 17:00 | P6 | 68.7 | 4 | 76.0 | 5 |
| 17:00 | P7 | 8.8 | 5 | 7.0 | 5 |
| 17:00 | P8 | 48.2 | 5 | 48.0 | 5 |

## Assumptions and gaps

- Count-report direction labels translated to network approaches (GDOT labels approaches by road-based direction): NB -> EB, EB -> SB, SB -> WB, WB -> NB. Vehicle ids keep GDOT's column names.
- Arrivals: Poisson within each 5-min bin with the measured count (random times, seed 12345); counts per movement per bin are exact.
- Offsets unknown (coordination with neighbouring signals not modelled).
- Plan I: rings don't add up to one cycle (unverified read or an unmodelled phase); slack given to P6 +10 s so SUMO's controller accepts it.
- Plan J: rings don't add up to one cycle (unverified read or an unmodelled phase); slack given to P2 +19 s so SUMO's controller accepts it.
- Plan K: rings don't add up to one cycle (unverified read or an unmodelled phase); slack given to P2 +5 s so SUMO's controller accepts it.
- Plan L: rings don't add up to one cycle (unverified read or an unmodelled phase); slack given to P8 +10 s so SUMO's controller accepts it.
- Plan M: rings don't add up to one cycle (unverified read or an unmodelled phase); slack given to P6 +8 s so SUMO's controller accepts it.
- Plan N: rings don't add up to one cycle (unverified read or an unmodelled phase); slack given to P6 +9 s so SUMO's controller accepts it.
- Plan O: rings don't add up to one cycle (unverified read or an unmodelled phase); slack given to P2 +6 s so SUMO's controller accepts it.
- Plan P: rings don't add up to one cycle (unverified read or an unmodelled phase); slack given to P2 +46 s, P8 +3 s so SUMO's controller accepts it.
- Plan Q: rings don't add up to one cycle (unverified read or an unmodelled phase); slack given to P6 +19 s so SUMO's controller accepts it.
- Plan R: rings don't add up to one cycle (unverified read or an unmodelled phase); slack given to P2 +40 s, P8 +3 s so SUMO's controller accepts it.
- Plan S: rings don't add up to one cycle (unverified read or an unmodelled phase); slack given to P2 +5 s so SUMO's controller accepts it.
- Plan T: rings don't add up to one cycle (unverified read or an unmodelled phase); slack given to P2 +31 s so SUMO's controller accepts it.
- Plan U: rings don't add up to one cycle (unverified read or an unmodelled phase); slack given to P2 +48 s so SUMO's controller accepts it.
- Min recall on phases serving a left only permissively when the plan omits that left's protected phase (SUMO generates no detector for permissive-only lanes): plan I: P4, P8; plan M: P4, P8; plan T: P4, P8.
- Max recall on phases that are the only service of a permissive-only left and ran at >= 90% of their max in GDOT's recorded greens (Timing & Actuation, same plan): plan E: P4 (recorded 42.9 of 43.4 s); plan E: P8 (recorded 42.9 of 43.4 s).
- Max recall (full split every cycle, < 5% gap-outs on the Split Monitor): plan A: P4, P7, P8; plan B: P3, P4, P7, P8; plan C: P3, P4, P7, P8; plan D: P4; plan F: P4, P5, P8; plan G: P4, P8; plan H: P1, P7; plan J: P4, P8; plan K: P4, P7, P8; plan L: P3, P4, P7; plan N: P1, P3, P4, P7, P8; plan O: P4, P7; plan P: P3, P4, P7, P8; plan Q: P3, P4, P7, P8; plan R: P4, P7, P8; plan S: P4, P7, P8; plan U: P4, P8.
- SUMO LIMITATION: GDOT runs P1 after the coordinated phase (lagging); SUMO's NEMA controller (TS2, coordinated, as configured here) does not serve a phase that lags a coordinated phase, so it runs leading here (same splits). Type 170 serves it but mis-applies these force-offs; other controller types untested. A fixed-time run with GDOT's exact order is in rlagent/experiments/EXP-007_corrected-phase-model.
- 'Actuated' periods (Free or uncoordinated) run actuated, uncoordinated, with max greens from Split Monitor max-outs where seen, otherwise the 95th percentile of observed phase times (a lower bound on the real max).
- Controller: SUMO NEMA actuated dual ring. Coordinated plans use the real splits as force-offs within the real cycle, phases 2/6 coordinated; other phases gap out / skip on 20 m stop-bar detectors. Vehicle extension 1.0 s through phases, 8.0 s left-turn phases (not published by GDOT; fitted to the recorded greens).

## Quality check (07:00-09:30, headless)

- vehicles loaded 6127, inserted 6088, still waiting to enter at 09:30 0, still running 46
- teleports 0 (jams 0), collisions 0, SUMO warnings 8
- mean per trip: waiting 39.4 s, time loss 44.3 s, departure delay 0.5 s
- **PASS** (pass = no teleports, no collisions, no entry backlog at 09:30)
