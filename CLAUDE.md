# Adaptive Traffic Signal Control — SIG#7065 (Peachtree Rd & Piedmont Rd, Atlanta GA)

## Project

Graduate research project: build an adaptive traffic-signal-control RL agent.
`referencepaper/` holds the three papers this work builds on — Sahachaiseree
& Oguchi's linear-FA + LSTDQ method is the base method being replicated and
extended (see `rlagent/`); Chen's thesis and the APSIPA paper are a labmate's
prior work (Recurrent PPO on a Taipei roundabout) kept for context/comparison.
The extension goal is to make the base method perform well in **high
saturation / traffic-spillover** conditions, likely by adding 1–2 state
features — that extension work has not started yet (see "Next steps" below);
everything built so far is groundwork and replication.

## Fidelity policy (governs every data step in this project)

**Never rescale, smooth, or invent values to match an external figure.**
Extract/use the raw numbers a source actually gives. Where a measurement is
genuinely missing or unreliable, say so explicitly rather than filling it
in — this applies as much to the current live pipeline (e.g. `sumodemand`
flags two sensor-outage windows as *unmeasured*, not as confirmed zero
traffic, even though the portal reports them as `0`) as it did to the
retired chart-digitizing pipeline this principle was first written for.

---

## Current status (read this first)

The project has moved through three stages. The first is fully retired; the
second and third are live.

1. **Retired: chart-image digitizing.** Two pixel-tracing pipelines
   (`atspm_digitizer`'s `process` mode for 15-min "Approach Volume" charts,
   and `tmc` mode for 5-min per-movement TMC charts) were built to extract
   volume data from GDOT ATSPM chart *images*, since the portal appeared to
   offer no numerical export. Both are retired now that a direct tabular
   export was found (see #2) — pixel-tracing a chart image is strictly worse
   than the exact numbers the portal already provides underneath it. All
   code, raw chart images, and digitized results from this era have been
   moved to **`old-dont-use/`** — historical reference only, do not build on
   it or resurrect it without a specific reason (e.g. if a date is needed
   that only exists as a chart, not a portal export).

2. **Live data source: the GDOT portal's own Turning Movement Count report.**
   `data/7065/{date}data.txt` — a tabular export with exact integer 5-min
   per-movement (Left, Thru) vehicle counts, parsed by
   `sumodemand/portal_report.py`. Cross-validated against the old pipeline's
   OCR-read chart totals for the two overlapping dates: **exact match on all
   16** movement/day totals (e.g. 0507 eb-thru: 15,776 both ways) — strong
   confirmation the parser is correct, and a strict precision improvement
   (the old pixel-digitized values carried up to ±2.5% error against that
   same OCR reading). **4 days on hand: 0505, 0506, 0507, 0508.** Right-turn
   movements are not in this export at all — GDOT doesn't report/chart them
   for this intersection, at any stage of either pipeline.

3. **`sumotwin/`** — SUMO digital twin of the real intersection, digitized
   directly from a georeferenced aerial rather than OSM (OSM under-maps the
   Piedmont north leg — no lane/oneway tags, wrong geometry). Includes a
   hand-traced free-right slip lane for the WB approach's right turn
   (Peachtree NE leg → Piedmont N leg, `NE_in`→`E1`→`N_out.37`), which
   bypasses the signal entirely, matching the real channelized geometry.
   **Reviewed and fixed**: the netedit session that added the slip lane had
   silently disconnected two other junctions (`NE_in`'s and `N_far`'s
   continuation into the rest of the network dead-ended) — found via
   systematic per-movement routing tests, fixed by restoring the missing
   `<connection>`s and re-running `netconvert`, verified with a 30-minute
   all-movement stress test (zero warnings, zero teleports, 100% insertion).
   See `sumotwin/README.md` for the full lane-config table.

   **Known caveats, not yet resolved:**
   - Approach lengths are 25–55% off from what `digitize.py` intended
     (quantified per-leg in the review notes) — geometry precision was
     explicitly deprioritized to get training running sooner; revisit with
     `aerial_overlay.png` when it matters.
   - `sumotwin/README.md`, `build.sh`, and `digitize.py` still describe the
     folder as a "`7065twinv2` duplicate" from before it was renamed to
     `sumotwin`, and hardcode paths (`7065twinv2/...`) that no longer exist.
     **Do not run `build.sh`** until this is reconciled — as currently
     written it would regenerate the network from the plain XML *without*
     the slip lane or the connectivity fix, silently destroying both.
   - **Possible construction-state mismatch (unverified, worth checking
     before trusting saturation results):** `approachspeeddottedlinesinfo.txt`
     (repo root) has research notes on an **active GDOT "Capacity
     Improvement" widening project (SR 237)** at this exact intersection —
     Piedmont Rd is being widened (notes say roughly 5→7 lanes total across
     both directions) and lane configurations are actively changing. It's
     not confirmed which build state `sumotwin`'s digitized lane counts
     correspond to (current mid-construction vs. final post-widening), nor
     whether the calibrated demand (`data.txt`, presumably reflecting
     current/live traffic under construction) matches the geometry it's
     being run against. Worth resolving before leaning on any
     saturation/capacity finding.

4. **`sumodemand/`** — calibrated demand builder, wiring the portal data
   into SUMO `<flow>` routes for all 4 days. Fully validated: all four
   full-day runs complete with zero warnings/errors and insert vehicle
   counts exactly matching each day's portal total (0505: 46,283 / 0506:
   54,606 / 0507: 50,906 / 0508: 51,530). Known gap: right-turn movements
   (NB/SB/EB rights + the WB slip) carry zero flow, since GDOT never
   measures them — not fabricated. Known caveat: **0505 (23:05–23:55) and
   0506 (00:00–04:10) each have a block where all 8 movements read exactly
   0 simultaneously** — a sensor/comm outage the portal reports as `0`
   rather than leaving blank, not genuine zero traffic (a real intersection
   doesn't have every movement, including its busiest, drop to literal zero
   together). Doesn't change simulated output (a skipped zero-bin behaves
   identically to the old pipeline's skipped NaN-bin), just don't cite those
   two windows as confirmed-empty. See `sumodemand/README.md`.

5. **`rlagent/`** — the active project: replicate Sahachaiseree's linear-FA
   + LSTDQ controller on the real twin, get initial metrics, *then* (a
   deliberately separate, later plan) extend it for high-saturation/
   spillover performance. **No agent code exists yet** — `rlagent/plan.md`
   is the phased implementation plan, currently at **Phase 0** (designing
   the stage table / action space — not yet done). `rlagent/regulations.md`
   is the supporting research backing that design: real GDOT left-turn
   phasing warrant thresholds (Policy 6785-2's exact cross-product/volume/
   crash criteria), the GDOT/NEMA phase-numbering convention, MUTCD/ITE
   clearance-interval formulas, and Georgia's right-turn-on-red default —
   all meant to make the stage table a computed, sourced design rather than
   an arbitrary one borrowed wholesale from the paper's toy intersection.

---

## Folder structure

```
GDOT/
├── CLAUDE.md (this file)
├── referencepaper/ (Sahachaiseree base method + Chen thesis/APSIPA labmate papers)
├── data/7065/{date}data.txt (live demand source: GDOT portal TMC report exports)
├── sumotwin/ (SUMO digital twin network — see its README.md)
├── sumodemand/ (calibrated demand built from data/7065/ — see its README.md)
├── rlagent/ (active project: plan.md + regulations.md; no code yet)
├── old-dont-use/ (retired chart-digitizer pipeline + raw chart images — historical only)
└── approachspeeddottedlinesinfo.txt (scratch research notes on the real intersection's
    active widening project + SUMO lane/geometry specifics — see caveat in #3 above)
```

---

## Next steps

- Resolve the construction-state question (§3) before trusting any
  saturation/capacity result from `sumotwin`.
- Reconcile `sumotwin/README.md` / `build.sh` / `digitize.py` with the
  current folder name and the hand-added slip lane (or at minimum, guard
  `build.sh` so it can't silently clobber the current network).
- `rlagent/plan.md` Phase 0: compute the left-turn warrant criteria from
  the calibrated demand, design the stage table, compute Georgia-consistent
  interstage timing — then Phases 1–5 (environment wrapper, LSTDQ learner,
  fixed-time baseline, initial training run, initial metrics report).
- Only 4 real calibrated days exist. Per `sumodemand/README.md`'s own
  closing note: don't train on one day scaled up/down — use these 4 to
  characterize the demand *range* (directional split, turning ratios, burst
  shape) and randomize over that range per training episode once training
  begins for real; `rlagent/plan.md`'s initial replication pass deliberately
  uses a single day as-is first, to validate the replication before adding
  that complexity.
