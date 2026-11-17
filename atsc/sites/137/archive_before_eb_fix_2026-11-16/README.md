# Archived 2026-11-16 04:25 — runs on a defective 137 setup (not to be cited)

Preliminary methods comparison (seed 0, 5 validation days), LSTDQ/Q-learning/ARS seed-0 weights, the demand-sweep
levels x1.25 and x1.5, and seeds 1-4 partial training, all produced before two fixes:

1. EB approach was one lane upstream of the last 40 m (OSM); the user checked: two lanes, left-only from ~65 m.
2. The P2 (EB through) stop-bar zone was dropped from the queue estimator because its note contained "right"
   ("through/right lane"), so MaxPressure's and the v2 learners' EB queue estimate reset to 0 every 6 s.
   Found by instrumenting MaxPressure (Mar 4 PM: 707-846 s/veh; 22.4 s/veh after the fix).

The preliminary report here was never read. Kept as the record of the attempt.
