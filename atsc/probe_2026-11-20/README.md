# ATSPM portal probe — what exact numbers can we get? (2026-11-20)

Signal 137, 2026-03-10, 07:00–09:00 (and full days for the aggregate export). Scripts: `charts_probe.py`
(every DefaultCharts metric once), `agg_probe.py` (AggregateDataExport). Sample charts kept here.

## Findings

1. **Aggregate Data Export** (`/ATSPM/AggregateDataExport`, 14 aggregate metrics, 15-min…year bins) returns a
   **"Download Chart Data" XML with exact values** — but for GDOT every series is **0** (137 on 2026-03-10 and
   2026-11-18: detector activation count, split failures, phase termination). The aggregation tables are not
   populated. Not usable unless that changes; re-check occasionally.
2. **Default charts return images only** (no table, no XML; `.jpg`→`.xml` gives 404). TMC is the exception
   (`ShowDataTable`), already used.
3. **Most charts print exact summary numbers as text** in the header and in the per-plan stripe — readable with
   the same OCR approach as `tools/atspm_splitstats.py`, per requested window (so a 15-min or hourly window gives
   exact per-window numbers, like the Approach Volume window trick):

| Chart | Exact text printed (per phase, per plan stripe) | Use |
|---|---|---|
| Split Monitor | avg split, % gap-out, % max/force-off, % skip, 85th % split | already read (validation V1–V3) |
| Purdue Split Failure | total split failures; per plan: SF count and % SF | **outcome validation (queues)** |
| Approach Delay | avg delay per vehicle (AD, s); total delay (TD, h) — advance detector, "simplified" definition printed on chart | **outcome validation (delay)**, main-street throughs |
| Purdue Coordination Diagram | % arrivals on green (AoG), % green time (GT), platoon ratio (PR); advance detector distance | arrival / coordination validation; offsets |
| Wait Time | per plan: average wait, max wait (s) | **outcome validation**, every phase with stop-bar detection |
| Pedestrian Delay | ped presses (PP), cycles with ped requests, time-buffered presses, min/max/avg ped delay, avg cycle length | **exact ped demand per window** (replaces the 3-day chart sample) |
| Left Turn Gap Analysis | no summary numbers — stacked bars of gap counts by size bin | needs a bar reader (pixel heights), opposing-flow gaps for permissive lefts |
| Phase Termination | per-cycle dots (gap / max / force-off / skip) | per-cycle validation; pixel reader |
| Approach Speed, Yellow & Red Actuations | no chart for 137 (no speed detectors / not configured) | — |
| Preemption | chart (empty if none) | flag days with preemption |

4. **Key design consequence:** ATSPM's metrics have documented definitions computed from detector and phase
   events (e.g. Approach Delay = time from an advance-detector actuation during red to the start of green). The
   simulation can compute **the same metric from its own detector/phase events**, so validation compares like with
   like: simulated "ATSPM" numbers vs the portal's printed numbers, per window.
