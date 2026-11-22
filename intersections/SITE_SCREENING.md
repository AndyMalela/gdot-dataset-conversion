# Candidate sites — sensor screening (started 2026-11-22)

What each candidate's detectors can count, from the GDOT ATSPM configuration, 4-12 days of turning-movement counts
(Nov 10-13, 2026) and one Timing & Actuation window (Wed 2026-11-11 17:00-17:05). Lesson from 137: a movement
needs a count from MOVING vehicles (count-only zone, advance or exit zone, or a loop) — a stop-line presence zone
that also "counts" undercounts queues, and radar presence zones add dropouts (a stopped car counted 2+ times).
Right turns (right turn on red) will be inferred at every site. Details per site: `<id>/SCREENING.md` where written;
137 and 7130 sensor tables: `SENSORS_137_7130.md`.

| | 137 | 7130 | 7144 | 7696 |
|---|---|---|---|---|
| name | W Paces Ferry @ E Andrews / Slaton | SR 237 Piedmont Ave @ Monroe Dr | SR 3 Northside Dr @ W Wesley Rd | SR 8 Hollowell Pkwy @ J E Lowery Blvd |
| hardware | Wavetronix radar | Wavetronix radar | **inductive loops** | SmartMicro radar |
| vehicles/day (sum of counts) | ~10,000 | ~30,000-37,000 (exits) | ~20,000 | ~32,000 |
| main-street throughs | advance counts ✓ | advance (Piedmont) + exit counts ✓ | advance loops ✓ (one lane listed per direction) | advance + lane counts, 2 lanes each ✓ |
| main-street lefts | WB count zone ✓, EB presence ✗ | presence ✗ | SB presence loop; NB no bay (shared through-left) | WB in shared through-left lane; no EB left phase |
| cross-street movements | presence zones ✗ | lefts presence ✗; throughs from exits ✓ | presence loops (left, through-right) | presence zones (left, through-left, through-right) ✗ |
| stop-line detection on main street | none | presence zones | none | none |
| T&A check (left / cross-street zone) | dropout bursts, held through arrows | EB left held through arrow, burst in red | clean: one on/off per vehicle, no bursts in red | NB left: short on/off bursts in red |

Notes:
- 7144: loops do not drop stopped vehicles (no radar dropouts seen), but its stop-line loops are count + presence on
  one channel, so a queue can still merge into one count (loop length unknown). Only lane 1 is listed for Northside
  NB/SB: whether a second lane exists and is counted needs a lane check. NB left has no own phase (shared lane).
- 7696: the main street (Hollowell) is counted per lane; the cross street (Lowery) only by presence zones, and the
  SmartMicro NB-left zone shows the same kind of short bursts during red as the Wavetronix zones.
- None of the four has a moving-vehicle count on every non-right movement.

## Statewide sensor screen (`tools/atspm_signals/sensor_screen.py`, started 2026-11-22)

Signals with Turning Movement Counts, Timing and Actuation and Split Monitor (7,200 statewide; District 7 =
metro Atlanta first, 2,689). One configuration request per signal, cached in `tools/cache/config/`. Each
movement group (approach x lane movement, right-only lanes left out) gets its best count source:
A = moving-vehicle count (count-only zone/loop, or advance count on the through), B = loop that is count +
stop-bar presence, C = radar zone that is count + presence (137's problem), - = none. Exit-lane counts listed
apart. Check on known sites: 137 A3/C5, 7130 A4/C4/-3 (+4 exit legs), 7144 A2/B5 (all counted), 7696 A2/C5.
Output: `tools/atspm_signals/sensor_screening.csv`, ranked (all A/B first).

### District 7 result (2026-11-22)

2,689 signals screened, 0 failures. First-listed hardware: inductive loops ~1,680, video ~400, Wavetronix Matrix
~310, SmartMicro ~80, Gridsmart ~60. 1,491 have every movement group graded A or B (most are loop sites = B:
count + presence on one loop, queue merging possible). **130 have every group A**, 63 of them with ≥ 6 movement
groups (`signals_sensorA.csv`): mostly Wavetronix Matrix sites with separate count-only zones per lane (the zone
type that behaved well at 137, ch65), Gridsmart fisheye-camera sites and a few loop sites.
Caveat: "configured" is not "working" — next, 2 weekdays of turning-movement counts (Nov 11-12) for those 63 to
check data, completeness and volume (`screen.py`). Note: the jurisdiction column of signals_all.csv says "Cobb" for
most District 7 signals, including Atlanta ones; not used.
