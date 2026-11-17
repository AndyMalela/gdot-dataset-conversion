# Site 137 — W. Paces Ferry Rd @ E. Andrews Dr / Slaton Dr (Buckhead, Atlanta)

Built 2026-11-16 (night before the midterm) on the atsc v2 pipeline, reusing 7065's engine, controllers, learners
and evaluation. **Provisional**: no capacity calibration and no field validation on this site yet.

## Data (GDOT ATSPM only)

| Item | Source |
|---|---|
| Study period | 2026-03-02..05-29 weekdays: the only period where GDOT's report counts all ten movements (from ~August EB_TR and WB_L read 0) |
| Split | train 03-02..04-17 (29 usable days), validation 04-20..05-15 (20), **test 05-18..05-29 locked** (proposed, not yet confirmed by the user) |
| Counts | turning-movement report, 5-min, as exported — except WB_TR (below) |
| WB through | from the upstream signal **138** (~260 m east): WB_T(138) + NB_TL(138) − WB_L(137) per 5-min bin. 137's own WB advance zone read 8.8–22.6k/day vs 4.3–7.5k from 138, while every other movement is steady (agreed 2026-11-16 03:40) |
| Plans | Split Monitor read for each of the 56 train/validation days: A–D (130/120/140/110 s) until 04-28, E/F/G (160/180/90 s) from 04-29 |
| Clearances, min greens, lead/lag | Timing & Actuation, 2026-10-02 |
| Detector layout | SignalDetail configuration table |

## Deviations from the field (state with every result)

1. **Lanes**: W Paces Ferry left + through/right each way, E Andrews right/through/left — **checked by the user**.
   Slaton Dr NB right/through/left from its three detector zones — **not yet confirmed**. OSM bay lengths and the
   single EB lane upstream of the last 40 m are unverified.
2. **WB through from 138** (above): ~260 m of frontage between the signals is uncounted; NB_TL(138) includes a few
   driveway-through vehicles (upper bound); 203 bins (1 %) where 138's inflow < 137's WB left set to 0.
3. **EB/WB right turns run as through** (no right-turn zone on W Paces Ferry).
4. **Stop-bar presence on P2/P6 added in the model** (field: advance count zones only on the coordinated throughs),
   so every controller reads the same detectors.
5. **No pedestrian timing** (not read): ped_min 0, no recall. **P1 clearance** = P5's (not read).
6. **Uncalibrated driver model** (SUMO defaults, 0.5 s step); saturation flow 1,900 veh/h/lane (HCM base) for Webster and Y.
7. **Not isolated**: 138 is ~260 m away on the same corridor; the model is isolated with random (not platooned)
   arrivals, so GDOT's coordinated plan pays coordination's cost without its benefit (same limitation as 7065 B4).
8. Night bands (Split Monitor "Actuated") run in engine free mode; six days with a failed plan read use the nearest
   day's schedule; three night plans that omitted P2/P6 were misreads and are excluded.

## Files

`signal.json` (make_signal.py), `detectors.json`, `movements.json`, `split.json`, `sim.json`, `network/`,
`baselines.py`, `train_lstdq.py`, `train_methods.py`, `evaluate.py`, `audit_demand.py`, `scale_summary.py`
(copies of 7065's with site constants changed); runs: `debug/stage1.sh` (methods), `debug/stage2_scale.sh` (demand sweep).
