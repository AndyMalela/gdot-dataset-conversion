# SIG 7065 controller comparison — preliminary (Phase 2, 2026-11-02)

**Preliminary:** run on the aerial-twin base, whose validation is not accepted yet (`VALIDATION.md` attempt 2: the left-turn phases P1/P3/P5 do not match the field). Locked test days (Oct 4–22) not used.

Setup: 20 validation weekdays (Sep 1 – Oct 3, complete or usable, not Labor Day), full day 00:00–24:00, same network, demand, driver model (`sim.json`) and field-style detectors for every controller. Delay = signal delay + queueing + waiting to enter. Raw tables: `baselines/report.md`, `baselines/runs.csv`, `baselines/hourly.csv`.

| Controller | What it is | Median daily delay (s/veh) | vs GDOT |
|---|---|---|---|
| gdot | GDOT's time-of-day coordinated-actuated plans (fixed force-offs, fitted recall/passage) | 47.3 | — |
| actuated | fully actuated, no cycle; same passage times, max green = largest in any GDOT plan | 39.3 | −17 % |
| webster | pretimed Webster plans per GDOT period, design hour from train days, X ≤ 0.9 per phase | 37.5 | −21 % |
| lstdq | LSTDQ (LSPI, 5 iterations, 22 episodes each, train days), binary extend/end every second, phase-gated linear features | 33.6 | −29 % |

By time of day (s/veh, pooled): LSTDQ is lowest in every period (night 26.8, AM 33.6, midday 35.7, PM 37.7, evening 33.6). GDOT's plans are worst in the PM (69.3, the P8 overflow); Webster is worst at night (43.5: pedestrian minimums force a ~107 s cycle on empty streets).

Per movement (median s/veh): LSTDQ is lowest or within ~1 s of the lowest on all eight movements, so the gain is not bought by starving a minor movement. Largest gains: Piedmont-N through EB_T (P8) 52.6 → 27.9, Piedmont lefts.

## Caveats, before anything is concluded

1. **Base not accepted.** In the simulation P3/P5 end early, which gives the coordinated phases time the field does not; that biases *gdot* (and the shared passage times) in an unknown direction.
2. **Isolated intersection.** The neighbouring signals (7066, 7071, 7058) are off, arrivals are random within 5-min bins. Coordination's purpose (progression between signals) earns GDOT nothing here, while the cycle-free controllers (actuated, LSTDQ) lose nothing by breaking it. The comparison is fair only for an isolated intersection.
3. **LSTDQ evaluated at its final iteration**, not the best on validation, so no selection on these days; one training seed only.
4. **Webster** keeps pedestrian walk + flashing don't walk in every cycle (as GDOT's ped recall does), which costs it at night.
5. **Waiting to enter** counts as delay; S and SW legs store less queue than the real road (`GEOMETRY.md`).
6. 1 teleport (Webster), 0 for the others.

The 7065v2 (OSM network) runs of 2026-10-31 are in `baselines/v2osm/` and `lstdq/v2osm/` (Webster there predates the X ≤ 0.9 fix and is invalid).
