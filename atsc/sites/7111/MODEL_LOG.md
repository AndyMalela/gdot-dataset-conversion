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

## Step 2 — day split locked; site selection written; how busy (2026-11-27)

- **Day split** (`split.json`, `VALIDATION.md`):
  - train Aug 31 – Oct 9 (29 weekdays);
  - validation Oct 13 – Nov 6 (19 weekdays);
  - **test locked Nov 9 – 20 (9 weekdays)**;
  - federal holidays (Sep 7, Oct 12, Nov 11) excluded.
  - Exposure before the split is disclosed: screening saw daily count totals of Nov 9–13.
- **Site selection record:** `intersections/SITE_SELECTION.md` (criteria, funnel 2,689 → 130 → 63 → 48 → 6,
  decisions, weaknesses).
- **How busy** (`atsc/sites/y_compare.py` → `atsc/sites/Y_COMPARISON.md`, train days):
  - peak Y = 0.47 at both 7111 and 137 (137 as reported; 0.58 with its undercount estimate);
  - 7111 carries ~1.8× the vehicles/h of 137 but over more lanes;
  - 7111's non-coordinated phases hit force-off/max-out in 38–76 % of cycles (137: 15–52 %).
  - So 7111 = more volume, tighter timing, more complex layout; **not** a higher flow ratio. Reported as such.

## Step 3 — through/right split of the driveway and Collier approaches from exit zones (rule written 2026-11-28, before reading any window)

**Problem.** The driveway (P4) and Collier (P8) each have one shared through-right lane, with a single count
(WB_TR, EB_TR). The split decides where the traffic goes. The daily flow balance leaves one unknown free
(Step 1e).

**Data.** Timing & Actuation charts, 5-min windows, phases 1, 2, 3, 4, 5, 6, 8, with lane-by-lane count rows
(`tools/lanecheck/tna_fetch.py`).
- **Days:** every other usable train day, 13 days — 08-31, 09-02, 09-04, 09-09, 09-11, 09-15, 09-17, 09-21,
  09-23, 09-25, 09-29, 10-06, 10-08.
- **Windows:** 07:00, 08:30, 10:00, 12:00, 13:30, 15:00, 17:00, 18:30. Plus the format test window 09-16 12:00.
- No validation or test day is used.

**What the test window showed** (09-16 12:00, looked at only to check the chart format):
- The exit zones are drawn as count rows: west exit ch91 on the P4 chart, north exit ch107/108 on P6, east exit
  ch123 on P8, south exit ch75-77 on P2.
- The approach lane-count zones (ch86, ch117) also fire during red. So they count **arrivals**, not departures, and
  only the exit zones give departure times.

**Rule.**
1. **Driveway through** = west-exit (ch91) hits inside the P4 service window, minus the SB right-on-red estimate for
   that window.
   - **P4 service window** = P4 green start + 1 s to the end of P4 red clearance + 3 s (travel to the exit zone).
   - Nothing else can reach the west exit then: Peachtree is red, NB left (P1/P6) is not running, Collier (P8)
     goes east or south.
2. **SB right-on-red rate** = west-exit hits per second during P3-only time (Collier left on, P4 not on), with the
   same 3 s lag. In that time the only source for the west exit is the SB right on red. The rate is applied to the
   P4 service window.
3. **Collier through** = east-exit (ch123) hits inside the P8 service window, minus the NB right-on-red rate (east-exit
   hits per second during P4-only time without P8 — if none exists, during P3 time without P8).
4. **Exit-zone detection ratio:** west-exit hits during P1-protected-only time (NB left alone, Peachtree through red)
   ÷ NB-left lane-count hits (ch65) in the same cycles. Reported. Used to judge whether the exit zone misses vehicles.
   Shares (step 5) use the same zone for numerator and the approach count for the denominator, so a constant exit miss
   rate biases the share downward by that ratio → **the share is divided by the detection ratio if it differs from
   1 by more than 5 %**.
5. **Through share** = Σ driveway throughs ÷ Σ WB_TR count (ch86) over the same windows. Same for Collier. Pooled
   over all windows, and also reported by time-of-day window.
   - Uncertainty: bootstrap over days.
   - Right share = 1 − through share. Applied per 5-min bin to WB_TR and EB_TR in the demand.
6. **Reading markers:** markers per row counted with `tools/lanecheck/tna_count.py`-style column blobs; times from
   the plot frame (`tna_events.frame`). Any window whose phase displays cannot be read is dropped and listed.

No outcome of this step is compared with validation statistics before the rule is applied in full.
