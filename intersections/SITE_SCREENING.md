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
