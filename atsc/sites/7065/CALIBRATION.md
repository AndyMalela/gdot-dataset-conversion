# SIG 7065 discharge calibration (Phase 1.5)

2026-10-30. Train weekdays only (22 complete days, Jul 10 – Aug 31), PM plan C (15:30–19:00). Reproduce: `uv run python atsc/sites/7065/calibrate.py` then `calibration_summary.py`.

## What is calibrated, and against what

- **Parameters:** SUMO's Krauss driver model, one vehicle type for every approach: `sigma` (driver imperfection) and `tau` (reaction time); also tried `minGap` and the simulation step length.
- **Field quantity:** Piedmont-N through (EB_T, P8), the one movement where the field measures discharge. Under plan C, P8 is forced off in every cycle, P7 runs in 99 % of cycles, so P8's green is a fixed 48.4 s, and a 15-min quarter holds exactly 5 cycles = 242 s of P8 green. GDOT's count zones are Matrix radar near the stop line (`DETECTORS.md`), so a count is a vehicle the real intersection **served**. Field P8 served per lane of green, train days: median **1,986 veh/h**, IQR 1,830–2,150 (308 quarters).
- **Criterion (set before choosing):** the *least generous* setting under which the simulation, running GDOT's own plans, serves the counted P8 flow: no **overflow day** (P8-through mean delay > 100 s, i.e. ≈ 1.5 × the cycle delay of a movement at capacity) among train days without flagged count bins (`DEMAND.md` §3).

## Result

| sigma | tau | minGap | step | overflow days | P8 delay median (s) | sim P8 served per lane of green: p25 / median / p75 / p90 |
|---|---|---|---|---|---|---|
| 0.5 (SUMO default) | 1.0 | 2.5 | 1.0 | 19 | 603 | 1,755 / 1,830 / 1,904 / 1,986 |
| 0.2 | 1.0 | 2.5 | 1.0 | 14 | 166 | 1,837 / 1,979 / 2,068 / 2,150 |
| 0.0 | 1.0 | 2.5 | 1.0 | 6 | 95 | 1,830 / 2,001 / 2,120 / 2,202 |
| 0.2 | 1.0 | 1.5 | 1.0 | 7 | 97 | 1,837 / 2,001 / 2,112 / 2,217 |
| 0.2 | 1.0 | 2.5 | 0.5 | 2 | 81 | 1,830 / 2,008 / 2,150 / 2,239 |
| 0.5 | 0.8 | 2.5 | 0.5 | 1 | 76 | 1,822 / 1,993 / 2,164 / 2,261 |
| **0.2** | **0.9** | **2.5** | **0.5** | **0** | **72** | **1,822 / 1,993 / 2,157 / 2,276** |
| 0.3 | 0.8 | 2.5 | 0.5 | 0 | 70 | 1,822 / 1,993 / 2,157 / 2,283 |
| 0.2 | 0.8 | 2.5 | 0.5 | 0 | 68 | 1,822 / 1,993 / 2,142 / 2,283 |
| field | | | | | | 1,830 / 1,986 / 2,150 / 2,276 |

Full grid (15 settings): `calibration/grid.csv`. tau < 1 s with 1 s steps is not collision-free in SUMO and produced mass teleports; those rows are invalid.

**Chosen: sigma 0.2, tau 0.9 s, 0.5 s steps** (`sim.json`): the least generous of the four settings with no overflow day. Discharge 1,950 veh/h per lane of *actual* green (HCM base 1,900). The simulated distribution of P8 served per quarter matches the field's at every quantile within 1 %.

## Findings

- **The step length mattered as much as the driver.** At 1 s steps the simulation loses time at every start-up and every signal change (intervals end up to 1 s late); 0.5 s halves P8 delay at the same driver parameters. All v2 runs use 0.5 s.
- **The remaining overflow days are the flagged-count days.** With the chosen setting, P8-through delay is 65–75 s on 19 of 22 days, i.e. the cycle delay of a movement right at capacity, with no overflow queue. The three days that overflow (Jul 16, Jul 21, Aug 12) are exactly the days with physically impossible 18:10 count bins (`DEMAND.md` §3).
- **Caveat:** fitted on one movement. Other approaches share the vehicle type but are not saturated in the field, so their capacity is not observed directly. Phase 1.6 checks their signal behaviour (splits, gap-outs) instead.
