# Site selection for the second study site (record for the thesis)

Written 2026-11-27. It records how the second site was chosen. The screening itself ran 2026-11-21..22; its
working notes are in `SITE_SCREENING.md` and `<id>/SCREENING.md`.

The rules below are the ones applied during the screening: they are in `tools/atspm_signals/sensor_screen.py`, and
the funnel steps are in the notes of those days. They are written here together **after** the choice, so they are a
record, not a pre-registration. No simulation, controller or RL result of any candidate existed when the choice was
made.

## Why a new rule was needed

At 137, 7 of 10 movements are "counted" only by stop-line presence zones. Those count activations, not vehicles:
- a queue merges into one activation;
- radar dropouts make one stopped car count 2+ times.

The v3 model attempts failed on this (`atsc/sites/137/MODEL_LOG.md`). The lesson: pick a site by its sensors first.
Every non-right movement must be counted from **moving** vehicles. Right turns are inferred at every site, because
right turn on red is allowed almost everywhere.

## Criteria

1. **Data available in ATSPM:** turning-movement counts, Timing & Actuation and Split Monitor.
2. **Every non-right movement group graded A** (`sensor_screen.py`):
   - A = count-only zone or loop, or an advance count on the through;
   - B = loop that is count + presence on one channel;
   - C = radar zone that is count + presence;
   - "–" = nothing counts it.
3. **At least 6 movement groups** (a real multi-phase intersection, not a mid-block signal).
4. **The configured detectors actually report:** complete turning-movement counts on two test weekdays (Nov 11-12).
5. **Deep check:**
   - the intersection's own in/out balance (exits against entries);
   - agreement with neighbouring signals on shared links;
   - stable configuration over the study period;
   - Timing & Actuation behaviour of the zones (one on/off per vehicle, no bursts during red).
6. **Contrast with 137:** busier and more lanes or phases (the midterm promise: a "busier" site). How busy is measured
   by the critical flow ratio Y (`atsc/sites/Y_COMPARISON.md`).

## Funnel (District 7, metro Atlanta)

| Step | Signals |
|---|---|
| Statewide signals with turning-movement counts, Timing & Actuation and Split Monitor | ~7,200 |
| District 7 screened (configuration of each) | 2,689 |
| Every group A or B | 1,491 |
| Every group A | 130 |
| … with ≥ 6 movement groups | 63 |
| … returning complete counts Nov 11-12 | 48 |
| Four-leg, left bay counted on every approach, deep-check shortlist | 6 (236, 7025, 7027, 7111, 7718, 8185) |

Earlier hand-picked candidates, checked before the statewide screen, and why they fell out:
- 7130, 7696: presence-zone counts on lefts / cross street, bursts in red.
- 7144: loops, but count + presence on one channel; lanes unclear.
- 7065: Peachtree throughs from presence zones, 2–9× too low in daytime.

## Decisions

| Signal | Decision | Reason |
|---|---|---|
| **7111** SR 9 Peachtree Rd @ Collier Rd | **chosen (user, 2026-11-22)** | See below |
| 8185 Perimeter Center Pkwy @ Hammond Dr | Reserve (possible third site) | Every movement incl. rights counted; protected dual lefts. But exits are 8–18 % below entries, and neighbour 8184 SB is not reporting |
| 7027 Moreland Ave @ Ponce de Leon | Rejected | Exits exceed entries by 18–35 %; disagrees with neighbour 7028; unexplained pseudo-phases (11/16/17); NB-left zone silent |
| 7718 Memorial Dr @ Maynard Terrace | Not now | Configuration changed during the period; east exit 0.33–0.41 of neighbour 7719 |
| 236 North Ave @ Techwood, 7025 N Highland @ North Ave | Not deep-checked | Gridsmart camera counts. A Gridsmart site in the screen showed implausible volume (183 Spring St ~95,000/day on three legs); would need a plausibility check first |

Why 7111:
- Every non-right movement has its own count-only zone in every lane, and every leg has exit counts.
- The in/out balance is −1 % to +12 % per day, and the gap is a plausible size for the uncounted Peachtree rights.
- ~39,000–46,000 vehicles/day (137: ~33,000–41,000); 2 Peachtree left bays + a protected double left + a driveway
  phase.

## Is 7111 "busier"? (measured 2026-11-27, train days only; `atsc/sites/Y_COMPARISON.md`)

- **Vehicles:** yes. The peak hours carry ~2,800–3,000 counted vehicles/h at 7111, against ~1,500–1,700 at 137 as
  reported (~2,100–2,200 with 137's undercount estimate).
- **Critical flow ratio Y:** no. 7111 has more lanes, so the load per lane is about the same: peak Y **0.47** at
  7111 against **0.47** at 137 as reported (**0.58** with 137's estimate). 7111's counts may be 11–16 % low (see
  neighbour check below), which would raise its Y to ~0.53.
- **The signal's own behaviour (GDOT Split Monitor):** yes. 7111's side and left phases end by force-off or max-out
  in 38–76 % of cycles and are rarely skipped. At 137 the same phases end that way in 15–52 % of cycles and are
  often skipped.
  - Reading: GDOT's 7111 timing is tight for its demand.
  - This depends on GDOT's split settings as well as on demand.

So 7111 is busier in volume, phases-at-limit and layout (corridor, double left, more lanes), but **not** in Y. The
thesis must say "busier" in these measured terms, not "near capacity".

## Known weaknesses of 7111 (reported, not hidden)

- **Neighbour disagreement.** 7111's radar exit count is 11–16 % below neighbour 7110's inductive loops on the north
  link, constant at every hour. Which is closer to the truth is unknown. Part may be mid-block driveway turns: there
  is a two-way left-turn lane, and Piedmont Hospital entrances are on that block.
- **Broken advance radar.** 7111's own Wavetronix Advance counts are broken. So the Purdue Coordination Diagram and
  Approach Delay reports at 7111 cannot be used for validation.
- **Peachtree rights** come from the shared outer through lanes. They are probably inside the "through" lane counts
  and are not separated.
- **Missing neighbour count.** Neighbour 7112's SB through count is 0 every day (not reporting).
- **Driveway leg.** The east leg is a Chick-fil-A drive-through and parking, with its own signal phase (P4).
- **Corridor.** Coordinated corridor with signals ~190 m and ~210 m away, so 7110 and 7112 must run with their real
  timing.

## Note on intersection shape

7111 has three public legs plus a signalized driveway; 137 has four public legs. Both independent critics (Fable,
Opus; 2026-11-22) judged the shape acceptable. The differences to report are corridor effects and the driveway
phase, not the leg count. The contrast between sites is stated by measured quantities (Y, volume, phases), not by
shape.
