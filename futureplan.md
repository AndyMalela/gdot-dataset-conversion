# Future plan

Items deliberately left for after the midterm (2026-11-19). Not scheduled yet.

## Outcome-level validation of the twin (137)

**Why:** the current validation (`atsc/sites/137/VALIDATION.md`, V1 split / V2 gap-outs / V5 health, attempt 7 accepted)
checks that the simulated controller *behaves* like the field one. It never compares a traffic *outcome* (delay, queue
failures) with the field — yet delay is the metric the methods are ranked on, and the research question is about
saturation. Also, V2 gap-outs is the same quantity the passage times were fitted to on train days (out-of-sample,
but not independent), so an outcome check would be the first fully independent one.

**Source:** GDOT ATSPM portal metric list (seen 2026-11-17). All are charts, not tables, so each needs its own OCR /
chart-reading code (as `tools/atspm_splitstats.py` does for the Split Monitor header). Check first whether a chart
prints exact summary numbers in its header or legend before tracing anything.

| ATSPM report | Possible use | Notes / to verify |
|---|---|---|
| **Purdue Split Failure** | Best candidate: share of cycles whose green did not clear the queue — a direct congestion / saturation check | Uses stop-bar presence occupancy; 137 has Matrix stop-bar zones on every phase except P2/P6 |
| **Approach Delay** | Compare simulated vs field delay per approach — closest to the evaluation metric | Estimated by ATSPM from advance detectors; 137 has advance zones only on EB/WB (260 ft) |
| **Arrivals on Red** (and Purdue Coordination Diagram, % arrivals on green) | Checks arrival platooning from signal 138 and progression | Advance detectors, EB/WB only; PCD already used for 137–138 offsets |
| **Wait Time** | Side-street / left-turn waiting from call to green | Check what detector it needs |
| **Left Turn Gap Analysis** | Permissive left-turn gaps in opposing traffic — targets the open V3 / permissive-share mismatch (sim 0.73–0.75 vs field 0.85–0.88) | |
| Purdue Phase Termination | Same information as Split Monitor gap-out / force-off / skip, per cycle | Possible cross-check of V2/V3 |
| Pedestrian Delay | Check of the measured pedestrian calls (attempt 3) | |
| Preemption Details | Check for emergency/rail preemption on study days (would explain odd days) | |

Rules when this is done: criteria written before the first run (as for V1–V5); validation days only, test days stay
locked; the existing attempt-7 acceptance is not revisited because of a new check — a failure is reported and
diagnosed as a new attempt.

## Other open items (from the midterm prep, 2026-11-17)

- Clearances, minimum greens and lead/lag were read from Timing & Actuation on 2026-10-02, outside the Mar–May study
  period: confirm on a Mar–May chart.
- `atsc/sites/137/README.md` is stale (still says no pedestrian timing, uncalibrated driver model, random arrivals,
  no validation): update to the attempt-7 state.
- Validation thresholds (3 s, 15 points, 80 % of pairs, caps 6 s / 30 points) have no written justification
  (carried over from 7065): write one, or cite simulation-calibration guidance (e.g. FHWA Traffic Analysis Toolbox
  Vol. III) after checking the reference.
- Demand-scale sweep has not been rerun on the attempt-7 model (latest is attempt 5, archived).
