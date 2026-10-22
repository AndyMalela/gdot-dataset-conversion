# Capacity check — why real timing gridlocks the twin on most weekdays (2026-10-15)

**Question:** On 9 of 10 EXP-009 test weekdays, real GDOT timing can't carry the counted Piedmont-from-north
through flow (GDOT column EB_T, phase P8) in the twin, although GDOT's detectors counted those vehicles.
Three candidate causes were checked with GDOT's Timing & Actuation charts (lane-by-lane count + stop-bar presence
detectors), Sep 24 (worst day) 17:00–17:15 and 17:55–18:20, Oct 2 (within capacity) 17:00–17:15. Charts in this folder.

| Candidate cause | Evidence | Verdict |
|---|---|---|
| Real P8 green longer than plan C's split | P8 green ≈ 45–48 s per 180 s cycle in every Sep 24 cycle checked — plan C exactly | **Ruled out** |
| More lanes than the twin (SR-237 widening) | Sep 24 detectors show 2 through lanes (T1 ch37/40, T2 ch38/41) + 1 right lane (R3 ch39) at the stop bar — same as the twin | **Ruled out** |
| Twin discharges too slowly | Twin saturation flow on this approach = **1,640 veh/h/lane of green** (permanent-green test, demand 7,000 veh/h, vType sigma 0.5, tau 1.0 as used by all demand files). HCM base ≈ 1,900; GDOT's own PM totals imply ~1,800–2,200 | **Main cause** |
| Counts inflated | The "lane-by-lane count" detectors are setback loops (they fire during red; stop-bar presence doesn't). A few 5-min bins exceed any physical discharge (Sep 24 18:05 = 184, 18:10 = 206; Sep 21 210; Sep 23 182 vs ≈ 90 possible), with sub-second hit spacing in stop-and-go queues — likely repeated pulses per vehicle | **Contributing, on the worst days only** |

## Numbers

PM plan C 15:30–19:00 (3.5 h), P8 green share 48.4/180, 2 through lanes:

| Day | counted | max @1,800 | max @2,000 |
|---|---|---|---|
| 09-17 | 3,742 | 3,388 | 3,764 |
| 09-18 | 3,591 | 3,388 | 3,764 |
| 09-21 | 3,898 | 3,388 | 3,764 |
| 09-22 | 3,560 | 3,388 | 3,764 |
| 09-23 | 3,894 | 3,388 | 3,764 |
| 09-24 | 4,147 | 3,388 | 3,764 |
| 09-25 | 3,433 | 3,388 | 3,764 |
| 09-28 | 3,691 | 3,388 | 3,764 |
| 09-29 | 3,725 | 3,388 | 3,764 |
| 10-02 | 3,291 | 3,388 | 3,764 |

The twin's ~1,640 veh/h/lane gives a PM max of ≈ 3,090 — below every test day's count, so queues grow for the whole
3.5-hour plan. At ~1,900–2,000 most days fit; Sep 21, 23, 24 still exceed it, partly from the spike bins.

Twin saturation flow by driver parameters (same test):

| sigma | tau | veh/h/lane of green |
|---|---|---|
| 0.5 | 1.0 | 1,642 (current) |
| 0.3 | 1.0 | 1,846 |
| 0.2 | 1.0 | 1,920 |
| 0.0 | 1.0 | 2,066 |
| 0.5 | 0.9 | 1,744 |
| 0.5 | 0.8 | 1,868 |

## Change made (2026-10-15, student-approved)

Demand vType sigma 0.5 -> 0.2 (`tools/build_sim.py`); EXP-009 rerun as v4.

**Measurement caveat (independent audit):** the permanent-green test above is limited by how fast SUMO inserts
vehicles on some approaches (no standing queue forms), so it is unreliable as a method. A cyclic test (90 s red /
45 s green, standing queue, 1 s step) gives, per lane of green incl. start-up loss:

| Approach | sigma 0.5 | sigma 0.2 |
|---|---|---|
| Piedmont-N through | 1,715–1,800 | 1,920–2,010 |
| other throughs | 1,744–1,856 | 1,932–2,072 |
| protected left | 1,691 | 1,856 |

So sigma 0.2 raised capacity ~11–12 % evenly on every approach (permissive-left gap acceptance barely changed).
The twin now sits at or slightly above the HCM base (1,900) and above typical adjusted field values
(~1,700–1,800): slightly optimistic.

**Result:** real timing improved a lot (weekday mean 146.8 -> 70.5 s/veh) but Piedmont-from-N through is still
over the twin's capacity (~1,033 veh/h under plan C) on every test weekday (v/c 1.00–1.32); Sep 21 and Sep 24 are
still effectively gridlocked. Weekday real-timing numbers therefore remain a twin/count artefact. The spike bins
are kept as recorded (fidelity policy).
