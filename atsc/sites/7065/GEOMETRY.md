# SIG 7065 geometry audit (Phase 1.1)

Started 2026-10-23. Base network: `intersections/7065osm/network/7065osm.net.xml` (built by `tools/osm_build.py`, with 3 tag fixes in `osm_tag_fixes.json`). Each lane value below carries its source. Where sources disagree, the controller's own detector configuration wins, because it describes the intersection the counts and timing come from.

## Naming

GDOT names approaches by road direction, not compass (found in EXP-005; mapping in `intersections/7065/timing/phase_map.json`). This table uses compass legs plus GDOT phase numbers.

| Leg (compass, inbound) | Road | Through phase (GDOT label) | Left phase (GDOT label) | OSM approach edge |
|---|---|---|---|---|
| N leg, southbound | Piedmont Rd | P8 ("Piedmont EB") | P3 | `-525767115#1` |
| S leg, northbound | Piedmont Rd | P4 ("Piedmont WB") | P7 | `715642217#0` |
| SW leg, northeastbound | Peachtree Rd | P6 ("Peachtree NB") | P1 | `96433201#0` |
| NE leg, southwestbound | Peachtree Rd | P2 ("Peachtree SB") | P5 | `1153256544#1` |

## Stop-bar lanes: four sources

Student check (Google Maps, 2026-10-23), going round from the SW leg: SW 2 L + 3 T with the rightmost through lane also used for right turns (incl. right on red); N 1 L + 2 T + 1 exclusive R; NE 2 L + 3 T; S 1 L + 2 T + 1 exclusive R. **Agrees with the field detectors on every leg.**

Detector source: Timing & Actuation charts, 2026-10-02 08:00–08:05 (`intersections/7065/timing/dircheck/2026-10-02_0800_lanecount/01–10.jpg`), stop-bar presence channels per lane.

| Leg | Field detectors (2026-10-02) | OSM network (current) | Hand-built twin | Verdict |
|---|---|---|---|---|
| N (P8/P3) | L1 (ch33) · T1 ch37 · T2 ch38 · R3 ch39 → **1 L, 2 T, 1 R** | R, T, T, L | R, T, T, L | OSM correct (after tag fix) |
| S (P4/P7) | L1 (ch48) · T1 ch52 · T2 ch53 · R3 ch54 → **1 L, 2 T, 1 R** | TR, T, L, L+U | R, T, T, L | **OSM wrong**: 2 lefts and a shared through-right instead of 1 left, 2 through, exclusive right. Fix needed. |
| SW (P6/P1) | L1 ch1 · L2 ch2 · T1 ch5 · T2 ch6 · T3 ch7 → **2 L, 3 T**, no right detector | T, T, T, L, L (no right-turn connection) | TR, T, T, L, L | 2 L + 3 T agreed. Student check: rightmost through lane is shared with the right turn (RTOR). **OSM lacks the right connection; add it.** Right turns are undetected and carry no counted demand. |
| NE (P2/P5) | L1 ch17 · L2 ch18 · T1 ch21 · T2 ch22 · T3 ch23 → **2 L, 3 T** | T, T, T, L, L | T, T, T, L, L + free-right slip | Agreed. WB right is a signal-free slip in the twin; OSM has no right connection. Moot while right demand is zero. |

This resolves two open items from `CLAUDE.md`: Peachtree-SW has **3** through lanes, not 2, and the stop-bar lane counts reflect the construction state as of 2026-10-02, the same period the counts and timing come from. The caveat: a lane without a detector would not appear (for example, a shared right on SW).

### Side finding: right turns are not in the through counts

On both Piedmont approaches, the lane-by-lane **count** detectors cover T1 and T2 only (N: ch40, ch41; S: ch55, ch56). The right lane (R3) has presence detection only. So the P8 through count does not include right-turners, which rules out one explanation for the PM capacity mismatch (EXP-009, `intersections/7065/timing/capacity_check/README.md`). The remaining candidates are setback-loop double pulses and simulated saturation flow (Phase 1.5).

## Speed

| Leg | OSM network | Note |
|---|---|---|
| N | 35 mph (tag fix) | posted 35 mph confirmed by student |
| S | **40 mph** (OSM tag) | **wrong**: posted 35 mph (student check, 2026-10-23). Fix to 35. |
| SW, NE | 35 mph | |

## Queue storage and neighbouring signals

All four "other" signals in the OSM area are real GDOT signals (matched to the ATSPM signal list within 7 m):

| OSM signal | ATSPM | Distance from 7065 | Approach it bounds | Lane length to it |
|---|---|---|---|---|
| `69325270` | **7066** | 134 m | SW leg (Peachtree) | **~92 m** |
| `GS_cluster_69536535_69537116` | 7058 | 273 m | NE leg (Peachtree) | ~190 m |
| `GS_2239696512` | 7071 | 294 m | N leg (Piedmont) | ~219 m |
| `joinedS_...` | 7057 | 400 m | — | — |
| (none) | — | — | S leg (Piedmont) | ~291 m to network edge |

`tools/build_sim.py` switches the neighbours off (unsignalised). Consequences for v2:

- Arrivals at 7065 are random within each 5-min bin, not platoons released by 7066/7058/7071. This is a **scope boundary** (isolated intersection), to be stated, and quantified later with arrivals-on-green (Phase 1.4).
- A queue on the SW leg longer than ~92 m would block 7066 in reality; in the simulation it passes through. **v2 must record "queue beyond available storage" events per approach** instead of letting them pass silently.
- Vehicles must never be refused entry because a queue reached the network edge. Entry points must sit far enough upstream (to be checked with the worst PM queue).

## Turn-bay lengths

Read from 7065osm's edge splits (lane count per edge, traced upstream from the stop line, 2026-10-23).

| Item | 7065osm | Hand-built twin | Status |
|---|---|---|---|
| NE dual-left bay | 5 lanes for 0–92 m, then 3 → ≈ 92 m | | OSM-derived, plausible, not measured |
| SW dual-left bay | 5 lanes 0–33 m, 4 lanes 33–46 m, 3 after → staggered ≈ 33 m / 46 m | | **Measured (student, 2026-10-30):** at 60 m, 3 lanes (2 T + 1 T/R) with the first left lane already diverging; 1st left lane taper 71 → 53 m (full width from 53 m), 2nd left lane taper 43 → 28 m. Modelled from mid-taper: 4 lanes from **62 m** (fix 5), 5 lanes from 33 m (mid-taper 35.5 m; 2 m difference kept). |
| S leg bay (left or right) | 4 lanes for 0–86 m, then 3 → one ≈ 86 m bay | | OSM-derived, plausible, not measured |
| **N leg left bay + right lane** | 4 lanes for 0–128 m, then 2 → both ≈ 128 m | left pocket 40 m | **Wrong in 7065osm.** Student check (2026-10-23): left and right lanes both split off fully **40 m** before the stop line (matches the hand-built twin). 7065osm's 128 m came from a hand tag fix setting 4 lanes on the whole segment. **Fix: 4 lanes for the last 40 m only, 2 lanes upstream.** |
| NE free-right slip | absent | present | Exists in reality (student check), but right turns carry no counted demand, so it is omitted. |

## Fixes applied: `network/7065v2.net.xml` (2026-10-23)

Built by `network/build_net.py` from 7065osm (reproducible; no hand edits in netedit).

| # | Fix | Check after build |
|---|---|---|
| 1 | S leg lane use → right, through, through, left (no U-turn) | lanes `r s s L` ✓ |
| 1b | SW leg rightmost through lane also takes the right turn | lanes `rs s s l l` ✓ |
| 2 | N leg: 4 lanes for the last 40 m only, 2 through lanes upstream | 4 lanes 0–40 m, 2 lanes 40 m+ ✓ |
| 3 | S leg speed 35 mph | 35 mph on all three S-leg edges ✓ |
| 5 | SW leg (2026-10-30): first left lane from 62 m (mid-taper of the measured 71 → 53 m) instead of OSM's 46 m; `build_net.py` measures the built network and corrects the split position until it lands within 0.5 m | 4 lanes from 61.7 m ✓ |
| 4 | NE leg (2026-10-30): OSM widens 4 → 6 lanes on a 1.9 m micro-edge just before the bay, one upstream lane fanning out to stop-bar through lanes 0 and 1; SUMO sent every vehicle to the first, starving through lane 1. Rewired so each upstream lane feeds one through lane (`build_net.py` fix 4). | lane use balanced, see `DEMAND.md` ✓ |

Smoke test (`network/smoke.rou.xml`, every counted movement + 3 rights, 10 min, netconvert's guessed program): 430 inserted, 430 completed, 0 teleports, 0 warnings.

**Not done, on purpose: extending entry points.** The plan said to move entry points upstream so queues never reach the network edge. That would invent road beyond real signals 7066/7071/7058. (One exception the other way, 2026-10-30: the SW entry moved *downstream*, to the 3-lane edge 144 m from the stop line, because OSM's 2-lane stretch further up left the leftmost through lane unused; still beyond 7066 at 92 m. `DEMAND.md`.) Instead: vehicles that cannot enter are counted through `departDelay` (already part of total delay), and v2 records **storage-exceedance events** (queue longer than the lane length to the next upstream signal: SW 92 m, NE 190 m, N 219 m, S 291 m to the network edge). In reality those queues would block the neighbouring signal, which this isolated model cannot represent; they are reported, not hidden.
