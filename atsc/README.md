# atsc — v2 rebuild (simulation base + LSTDQ, from scratch)

Started 2026-10-23. Everything before this is frozen at git tag `pre-v2` (`rlagent/`, EXP-001–009). Data scrapers in `tools/` are reused; the simulation, controllers, learner and evaluation are rebuilt here.

## Principles

1. **The simulation is trusted only after it reproduces the field.** Run the real GDOT controller on real demand, on days not used for calibration, and compare against ATSPM records (green times, termination mix, split failures). Pass criteria are written down before running.
2. **One controller engine, many decision policies.** A single NEMA dual-ring engine enforces every rule (ring order, min greens, clearances, ped minimums, max greens, force-offs). Real plan, actuated, Webster, MaxPressure and LSTDQ only decide when to end a green, so differences in results come from the decision and nothing else.
3. **Field-available inputs.** Controllers read SUMO detectors placed like GDOT's (stop-bar presence + setback count loops), not perfect lane counts.
4. **Fidelity policy** (`/CLAUDE.md`): counts used as recorded; outages left blank; nothing rescaled to match an expectation; deviations from the real intersection disclosed.
5. **Locked test set.** 2026-10-04 to 2026-10-22 (scraped 2026-10-23) is held out. No result on those days is looked at until the final evaluation.

## Layout

```
atsc/
  sites/7065/      site spec (geometry, detectors, demand audit, validation)
    network/       build_net.py -> 7065v2.net.xml, detectors.add.xml
    signal.json    phases, rings, plans, schedule (make_signal.py)
  sim/             nema.py (engine), signal.py (SUMO glue + policies), detectors.py
  tests/           engine rule tests + cross-check against the old static program
```

## Phase 1 progress (simulation base, 7065)

| Step | Status |
|---|---|
| 1.1 Geometry spec | **done**: `sites/7065/GEOMETRY.md`; network `sites/7065/network/7065v2.net.xml` built by `build_net.py`, smoke test passes |
| 1.2 Field detector layout | **built**: `sites/7065/DETECTORS.md`, `atsc/sim/detectors.py`; Piedmont setback distance assumed (260 ft) until measured |
| 1.3 NEMA engine | **built + tested**: `atsc/sim/nema.py` (rules only), `atsc/sim/signal.py` (SUMO detectors in, signal out; `ActuatedPolicy`, `FixedPolicy`), `sites/7065/signal.json` (`make_signal.py`). 15 tests pass (`uv run python -m pytest atsc/tests`), incl. all 8 GDOT plans identical to the old static program per signal link. Known: 1 s steps end each interval up to 1 s late (~0.5 s per phase change); judge in 1.6. |
| 1.4 Demand audit | — |
| 1.5 Capacity calibration | — |
| 1.6 Field validation | — |
