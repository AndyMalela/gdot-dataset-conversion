# Adaptive Traffic Signal Control — SIG#7065 (Peachtree Rd & Piedmont Rd, Atlanta GA)

## Project

Graduate research project: build an adaptive traffic-signal-control RL agent.
`referencepaper/` holds the three papers this work builds on — Sahachaiseree
& Oguchi's linear-FA + LSTDQ method is the base method being replicated and
extended (see `rlagent/`); Chen's thesis and the APSIPA paper are a labmate's
prior work (Recurrent PPO on a Taipei roundabout) kept for context/comparison.
The extension goal is to make the base method perform well in **high
saturation / traffic-spillover** conditions, likely by adding 1–2 state
features.

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
     before trusting saturation results):** research notes (formerly
     `approachspeeddottedlinesinfo.txt`, intentionally deleted 2026-07-11
     to clean up the repo root once its key facts were extracted into this
     file and `rlagent/regulations.md`) documented an **active GDOT
     "Capacity Improvement" widening project (SR 237)** at this exact
     intersection — Piedmont Rd is being widened (roughly 5→7 lanes total
     across both directions) and lane configurations are actively
     changing. It's not confirmed which build state `sumotwin`'s digitized
     lane counts correspond to (current mid-construction vs. final
     post-widening), nor whether the calibrated demand (`data.txt`,
     presumably reflecting current/live traffic under construction)
     matches the geometry it's being run against. Worth resolving before
     leaning on any saturation/capacity finding. (Separately, the 35 mph
     posted-speed figure used throughout `sumotwin` and `rlagent` — see
     `rlagent/regulations.md` §6 — has been confirmed correct by the user
     directly, independent of the deleted notes file.)

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
   spillover performance. **This section was stale — code now exists well
   past Phase 0.** `stages.py` (8-stage action space + interstage timing),
   `sumo_env.py` (TraCI environment), `lstdq.py` (linear-FA/LSTDQ solver),
   `fixed_time.py` (Webster pretimed baseline), `train.py` /
   `train_random.py` (training loops), `eval_heldout.py`, `metrics.py`,
   and `watch.py` all exist, with results under `rlagent/results/`.
   `rlagent/regulations.md` is the supporting research backing the phase
   table's design (GDOT Policy 6785-2 left-turn warrants, NEMA
   phase-numbering convention, MUTCD/ITE clearance formulas, Georgia's
   RTOR default) plus a field-verification pass (§8) cross-checking it all
   against photos of the real signal heads. **Action space redesigned
   2026-07-11 to the realistic ordered-actuated model** (from the paper's
   free 8-stage selection): the agent runs the fixed ring-barrier cycle
   `EW_LEFT→EW_THRU→NS_LEFT→NS_THRU` with a binary EXTEND/ADVANCE action,
   FYA protected-permissive lefts (EB/NB/SB protected + permissive,
   WB-left permissive-only), protected NB/SB right-turn doghouse overlaps,
   and selective interstage clearance — all matching the photographed real
   heads (regulations.md §8). This changed the state (phase one-hot now 4
   wide) and action (2 not 8) dimensions, so **the old `results/` weights
   heads (regulations.md §8).

   **Current status (2026-07-12): base method replicated and validated — it
   now beats fixed-time.** The full experimentation trail (failures
   included, for the progress report) lives in `rlagent/experiments/`;
   `rlagent/experiments/README.md` is the live status index. The path
   there mattered:
   - **EXP-001 (negative):** the ordered-actuated action space (binary
     EXTEND/ADVANCE) + linear FA over `[phase-onehot, lane-counts]`
     produced a *degenerate* policy that parked on the busiest phase and
     gridlocked at **every** demand level incl. 0.5×. Root cause: the 32
     lane weights were shared across phases, so the phase×lane interaction
     that signal timing needs wasn't representable.
   - **EXP-002 (positive):** making the lane features **phase-gated**
     (each active phase gets its own lane-weight block; `feature_mode=
     "phase_gated"` in `sumo_env.py`, 132-dim state / 264 params) fixed
     it. The agent now runs a ~43 s adaptive cycle and **beats Webster
     fixed-time by 35–61% on delay at 100% throughput, scales 0.5–1.3×**,
     on held-out day 0508 — matching the paper's "~½ pretimed delay"
     claim. Training is full-day domain-randomized (day×scale), with the
     0505/0506 sensor-outage bins masked; runs on `libsumo` (~5.5×) with
     per-episode resumable checkpoints.
   Known open fidelity item: the twin models EB-through as 3 lanes but the
   real approach is likely ~2 (SR-237 widening) — correcting it makes 1.0×
   a genuinely near-saturated test (see EXP-001 §4.3). Treat
   `rlagent/plan.md`'s phase list as a rough historical map.

---

## Folder structure

```
GDOT/
├── CLAUDE.md (this file)
├── referencepaper/ (Sahachaiseree base method + Chen thesis/APSIPA labmate papers)
├── data/7065/{date}data.txt (live demand source: GDOT portal TMC report exports)
├── sumotwin/ (SUMO digital twin network — see its README.md)
├── sumodemand/ (calibrated demand built from data/7065/ — see its README.md)
├── rlagent/ (active project: stages.py/train.py/lstdq.py/etc. + plan.md + regulations.md)
├── old-dont-use/ (retired chart-digitizer pipeline + raw chart images — historical only)
├── lastchat.md (most recent session's working notes — training status, bugs found/fixed)
└── how-lsdtq-works.txt, command-notes.txt (scratch notes)
```

---

## Next steps

- Resolve the construction-state question (§3) before trusting any
  saturation/capacity result from `sumotwin`.
- Reconcile `sumotwin/README.md` / `build.sh` / `digitize.py` with the
  current folder name and the hand-added slip lane (or at minimum, guard
  `build.sh` so it can't silently clobber the current network).
- `rlagent/plan.md`'s Phase 0–5 list is largely done (stage table, env
  wrapper, LSTDQ learner, fixed-time baseline, and training runs all exist
  — see `stages.py`/`sumo_env.py`/`lstdq.py`/`fixed_time.py`/`train.py`).
  What's actually outstanding, per `lastchat.md`: wire
  `eval_heldout.py`'s unused `peak_window_rou()` helper into the eval
  functions and re-run, to get a fair peak-vs-peak comparison against
  fixed-time — the only clean result so far (full-day eval of a
  peak-trained agent) is a known-unfair test, not evidence the method
  doesn't work.
- Retrain on the redesigned action space — the old `results/` (weights,
  tripinfos, REPORT.md) were produced under the free 8-stage selector and
  no longer match `stages.py`/`sumo_env.py`. Both `train.py`,
  `train_random.py`, `fixed_time.py`, `eval_heldout.py`, and `watch.py`
  have been updated to the new binary EXTEND/ADVANCE action and run clean
  (smoke-tested: 0 teleports/collisions/warnings), but no fresh training
  run has been done yet.
- `sumotwin/README.md` references `digitize.py`, `build.sh`, and several
  PNGs (`preview.png`, `redigitized_overlay.png`, etc.) that no longer
  exist in `sumotwin/` at all (not just stale paths, as previously noted
  here — they're gone). Only `7065.net.xml`, `7065_slip.net.xml`,
  `7065.sumocfg`, `7065.view.xml`, `osm_raw.osm.xml`, and `plain/*.xml`
  remain. Reconcile the README or restore those scripts before relying on
  its "Rebuild" instructions.
- Only 4 real calibrated days exist. Per `sumodemand/README.md`'s own
  closing note: don't train on one day scaled up/down — use these 4 to
  characterize the demand *range* (directional split, turning ratios, burst
  shape) and randomize over that range per training episode once training
  begins for real; `rlagent/plan.md`'s initial replication pass deliberately
  uses a single day as-is first, to validate the replication before adding
  that complexity.
