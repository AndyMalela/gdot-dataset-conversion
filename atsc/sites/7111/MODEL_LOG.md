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

## Note 2026-11-22 — 7111 is a three-leg public intersection plus a signalized driveway

User pointed out that Peachtree @ Collier is a T. OpenStreetMap confirms: Collier Rd NW meets Peachtree from the
west only; the east approach in GDOT's configuration is a driveway (service roads only in OSM), carrying ~1,900
vehicles/day each way. It has its own phase (P4) and is modelled, but the intersection is simpler than 137
(which has a real four-leg cross street). Consequence for the thesis' "simple vs busier/more complex" contrast:
7111 is busier than 137 but not more complex in layout; 8185 (true four legs, dual lefts everywhere) is the
more complex candidate.

## Note 2026-11-22 — leg layout of the corridor (user check)

7111 (Collier Rd NW) and 7112 (Palisades Rd NE): public cross street on one side, signalized driveway to a
building/complex on the other (user, Google Maps; OpenStreetMap agrees). 7110 (Brighton Rd): three-leg (user);
GDOT's configuration still lists EB and WB Brighton approaches with counts (EB ~990/day, WB ~2,400/day) — open.
All driveway approaches that have a signal phase are modelled with that phase and their counted demand.

## Step 1b — geometry and signal heads from imagery (2026-11-27)

The user checked 7111 on Google Maps (Street View dated 2025, aerial). Full answers are in
`intersections/7111/MANUAL_CHECKS.md` (section "Answers so far").

Summary:
- The east leg is a Chick-fil-A drive-through and parking (a driveway with its own phase, P4).
- Collier: 2 left-only lanes (86 m long) + 1 through-right lane, and 1 lane out.
- Peachtree: 3 SB lanes, 2 NB lanes and a two-way left-turn lane, which becomes the left-turn bay at the signal.
- Left-turn signal heads match GDOT's phase table on all four approaches:
  - flashing yellow arrow (protected + permissive) on Peachtree NB and SB and on the driveway;
  - 2 red/green arrow heads with no flashing-yellow sign on Collier EB (protected only).
- Crosswalks with push buttons on all four legs.
- No speed sign seen. GDOT's configuration gives 35 mph on Peachtree.

Consequences for the model (to agree before results):
1. **Two-way left-turn lane between the signals.**
   - The lane lets drivers turn left into driveways mid-block. Those turns are not counted anywhere.
   - They are one possible part of the steady 13–16 % gap between 7111's north exit and 7110's NB count (Step 0
     neighbour check), together with the hospital entrances.
   - Planned treatment: no mid-block turns in the network. This is a disclosed deviation. The link mismatch is
     reported as measured.
2. **Collier speed.** No posted sign was seen and GDOT's field is blank. A Collier speed would need an outside
   constant (e.g. a statutory default), and it would have to be flagged.
3. **Bus stop on Peachtree NB, far side.** Not modelled unless a pull-out is ruled out and buses are frequent; any
   such data would be outside ATSPM. Flag as a known simplification.

### Step 1c — follow-up answers (2026-11-27)

- The two-way left-turn lane runs the whole length of each block. There is no fixed bay length.
- Peachtree rights use the outer through lane (shared through-right); there is no right-turn lane.
- Collier's double left: 86 m at full width + 12 m taper.
- The driveway exit has 2 lanes: left only, and through-right.
- No "No Turn on Red" signs, so right turn on red is allowed on all approaches. No U-turn signs.
- No bus signs seen.

Proposed network treatment (to agree before results):
- **Peachtree left-turn storage.** SUMO has no shared two-way left lane. Proposal: split each block's centre lane at
  the middle, so each direction gets about half the block (~95–105 m) as its left-turn lane at its own signal.
  - This is a disclosed simplification: both directions can really use the whole lane.
  - It is only a binding limit if a left-turn queue goes past half the block.
  - Check after building: the simulated maximum left queue against the half-block length.
- **Peachtree rights** come from the shared outer lane (no inferred turn bay).
- **Right turn on red** is allowed on every approach (no signs).
- **No U-turns** are modelled: ATSPM counts none.
- **No buses** are modelled.

### Step 1d — decision on the two-way left-turn lane (user, 2026-11-27)

The user decided: the centre lane is modelled as a **left-turn lane for traffic approaching 7111**, over the whole
modelled length of each Peachtree leg. Use in the outbound direction is ignored (it is a mid-block driveway turn
that nothing counts).
- Replaces the "split at mid-block" proposal of Step 1c.
- Disclosed simplification: in reality, mid-block lefts in both directions also use this lane.
- **Open point for the corridor model.** The north block (7111–7110, ~190 m) is also the approach of 7110's NB left
  (~950 vehicles/day). That left needs its own storage at 7110. To resolve with the user: the length of 7110's NB
  left bay (the solid-white part on the aerial), or another rule.
- 7112 has no conflict: its NB left is shared with through (lane 1), and there is no SB left on Peachtree there.

### Step 1e — can the driveway's through/right split be inferred? (2026-11-27)

Question (user): can the driveway's through vs right split (GDOT "WB_TR", ~1,040/day) be inferred from the exit
counts, or from the split monitor?

**(a) Daily flow balance at the four exits.**
- Data: 37 complete weekdays, Sep 1 – Nov 6. Days from Nov 9 on were not used (proposed test window).
- Unknowns: driveway through and right; Collier through and right; Peachtree NB right; Peachtree SB right.
- Assumption: Peachtree rights are made from the shared outer through lane (user check), so its lane count zone
  counts them inside NB_T and SB_T.
- Six equations (4 exits + the 2 combined through-right counts) but only five independent, because total in =
  total out. So **one unknown stays free**.
- Requiring every flow ≥ 0 leaves a range:
  - 32 of 37 days: driveway through ~0 to 50–1,100 per day, and right correspondingly ~0–1,100. **Too wide to use.**
  - 5 of 37 days: no non-negative solution (Sep 1, Sep 16, Oct 7, Nov 3, Nov 5). The counts there do not balance
    (exits − entries +2,400 to +6,300).
- Script: inline check, not kept. Result recorded here.

**(b) Split Monitor.** Reports only how long each phase was green and why it ended. It cannot say where vehicles
went.

**(c) Proposed: exit-zone hits timed against the phase that is green.**
- Uses the event log behind Timing & Actuation. Exit zones: north ch107/108, east (Chick-fil-A) ch123, south
  ch75-77, west (Collier) ch91.
- During P4 (driveway green), Peachtree is red and Collier's left (P3) is not running. So:
  - north-exit hits = driveway rights;
  - west-exit hits = driveway throughs.
- During P8 (Collier through-right green), east-exit hits = Collier throughs.
- Then the other splits follow from the counts.
- Error sources to quantify:
  - right turn on red from other approaches into the same exit (allowed everywhere);
  - the travel time from stop line to exit zone (offset to fit);
  - radar misses at the exit zones.
- Only on training days, after the test days are locked. The cached 2026-11-11 window is inside the proposed test
  window and is not used.
