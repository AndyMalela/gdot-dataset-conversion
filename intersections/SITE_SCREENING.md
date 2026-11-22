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
| vehicles/day (sum of counts) | ~33,000-41,000 (corrected 2026-11-22; was wrongly "~10,000") | ~30,000-37,000 (exits) | ~20,000 | ~32,000 |
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

### Turning-movement check of the 63 all-A signals (Nov 11-12, 2026)

48 of 63 return counts, all 100 % complete on both days; 15 return nothing (configured, not working). Entering
volume recomputed from approach movements only (screen.py's `hourly_volume` adds exit and bike counts). Full list:
`tools/atspm_signals/candidates_sensorA.csv`. Four-leg sites with a left-turn bay counted on all four approaches
(8-phase layout like 137), ranked by vehicles/day:

| signal | name | vehicles/day | hardware | movement groups |
|---|---|---|---|---|
| 236 | North Ave @ Techwood Dr | ~56,000 | Gridsmart (camera) | 8 |
| 7025 | N Highland Ave @ North Ave | ~46,300 | Gridsmart | 12 |
| 7027 | SR 42 (Moreland Ave) @ SR 8 | ~43,100 | Wavetronix Matrix count zones | 11 |
| 7111 | SR 9 @ Collier Rd | ~41,800 | Wavetronix Matrix | 8 |
| 7718 | SR 154 @ Maynard Terrace | ~37,800 | Wavetronix Matrix | 9 |
| 8185 | Perimeter Center Pkwy @ Hammond Dr | ~33,300 | Wavetronix Matrix | 9 |

Three-bay sites of note: 255 North Ave @ Luckie St (~47,900), 7160 SR 3 @ Magnolia St (~46,500), 7013 Moreland @
Hosea L Williams (~46,000), 7066 SR 141 @ Maple Dr (~40,100), 7084 SR 9 @ Habersham Rd (~35,000). For comparison
137 carries ~33,000-41,000 vehicles/day (raw counts).
Not yet checked for these: T&A behaviour of the count zones, timing-plan reads, neighbours, lanes on the aerial.
Gridsmart volumes need a plausibility check (183 Spring St shows ~95,000/day on three legs).

### Deep checks so far (2026-11-22) — details in `<id>/SCREENING.md`

| signal | verdict | main reason |
|---|---|---|
| 7111 Peachtree Rd @ Collier Rd | **first site (user, 2026-11-22)** | every non-right movement counted per lane; own in/out balance fits; ~11-16 % below 7110's loops |
| 8185 Perimeter Center Pkwy @ Hammond Dr | strong second candidate | every movement incl. rights counted; protected dual lefts; exits ~10 % below entries |
| 7027 Ponce de Leon @ Moreland | rejected | exits exceed entries by 18-35 %; disagrees with 7028; unexplained pseudo-phases |
| 7718 Memorial Dr @ Maynard Ter | not now | configuration changed mid-period; east exit undercounts (0.33-0.41 of neighbour) |
