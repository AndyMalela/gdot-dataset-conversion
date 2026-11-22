# Site 7111 — model-building log (for the paper's "Proposed approach")

SR 9 Peachtree Rd @ Collier Rd, simulated with its neighbours 7110 (Brighton Rd, ~190 m north) and 7112
(Palisades Rd, ~210 m south). Chosen 2026-11-22 from the GDOT sensor screen (`intersections/SITE_SCREENING.md`,
`intersections/7111/SCREENING.md`). Same format as `atsc/sites/137/MODEL_LOG.md`: one entry per step — what,
why, data, rule, result.

## Step 0 — site choice (2026-11-22)

- Why 7111: every movement except the Peachtree right turns has its own count-only radar zone in each lane (the
  lesson from 137: presence-zone "counts" are not vehicle counts); its own counts balance (exits − entries
  −1 % to +12 %, the gap being the uncounted right turns); clean detector behaviour on the T&A chart.
- Known issues, disclosed from the start: 7111's radar counts are ~11-16 % below 7110's loops on the link
  between them (constant at every hour; cause not known — radar miss or driveway inflow); 7111's advance radar
  counts are broken (so GDOT's arrival-based reports there are not usable); 7112's southbound count is 0 every
  day; the Peachtree right turns at 7111 are not counted and must be inferred.
- Manual checks requested from the user: `intersections/7111/MANUAL_CHECKS.md`.

## Step 1 — base data pull (started 2026-11-22)

- Period: weekdays 2026-08-31 .. 2026-11-20 (~58 days), for 7111, 7110 and 7112.
- Pulled: turning-movement counts (5-min), Split Monitor charts per day (timing plans per band) and GDOT's per-plan
  statistics read from them (`debug/pull_7111.sh`). Later, after the day split is written: Timing & Actuation
  windows on train days (controller measurements) and the outcome reports.
- Rule: no train / validation / test split is chosen yet; until it is written down (VALIDATION.md for 7111),
  the data are only checked for completeness, not analysed.
