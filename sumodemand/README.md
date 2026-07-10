# Calibrated demand for sumotwin

Wires per-movement turning-movement-count data into `<flow>` routes for the
[sumotwin](../sumotwin/) SUMO network. Built and validated by
[`build_demand.py`](build_demand.py) — do not hand-edit the generated
`.rou.xml` files, regenerate instead:

```bash
python3 sumodemand/build_demand.py
```

## Source data

Source of truth is the **GDOT portal's own Turning Movement Count report**
(`data/7065/{date}data.txt`) — a tabular export of exact 5-min per-movement
(L, T) vehicle counts, parsed by [`portal_report.py`](portal_report.py). This
replaced the earlier chart-digitizer pipeline (`atspm_digitizer` `tmc` mode,
still documented in the top-level `CLAUDE.md`) as the demand source: data.txt
is exact integers straight from the portal, not a pixel-traced approximation
of a chart image, so there's no digitization/pixel error. `build_demand.py`
only builds dates that have a **full-day (288-bin) `data.txt`**; partial
exports are skipped with a printed warning and any date without a `data.txt`
at all is simply not built.

**Cross-validated against the old pipeline**: for the two overlapping dates,
every one of the 8 per-movement daily totals from `data.txt` is an **exact**
match to the old digitizer's OCR-read chart totals (e.g. 0507 eb-thru: 15,776
both ways; 0508 nb-thru: 6,342 both ways) — strong confirmation the parser
and column mapping are correct, and a strict improvement in precision (the
old pixel-digitized values carried up to ±2.5% error against that same OCR
reading; this source has none).

**Status:** `0505`, `0506`, `0507`, and `0508` all have full-day `data.txt`
files and are built from the portal directly. Re-run `build_demand.py` once
more `data.txt` files are added; it picks up any `MMDDdata.txt` under
`data/7065/` automatically.

## OD → SUMO edge/lane mapping

Derived directly from the real `<connection>` lane channelization that
`netconvert` generated in `sumotwin/7065.net.xml` (not assumed/invented):

| Approach | Inbound edge(s) | Thru → | Left → | Right → |
|---|---|---|---|---|
| NB (from S, heading N) | `S_in` (lanes 1,2 thru / lane 3 left / lane 0 right) | `N_out` | `SW_out` | `NE_out` *(no data)* |
| SB (from N, heading S) | `N_far`→`N_near` (lanes 1,2 / lane 3 / lane 0) | `S_out` | `NE_out` | `SW_out` *(no data)* |
| EB (from SW, heading ENE) | `SW_in` (lanes 0-2 / lanes 3,4 / lane 0 shared) | `NE_out` | `N_out` | `S_out` *(no data)* |
| WB (from NE, heading WSW) | `NE_in`→`NE_in.15`→`NE_in.79` (lanes 1-5 thru+left / lane 0 diverges to the slip before `NE_in.79`) | `SW_out` | `S_out` | `E1`→`N_out.37`, a signal-bypassing free-right slip *(no data)* |

Piedmont Rd NE (`N`/`S` edges) carries the NB/SB pair; Peachtree Rd NE (`NE`/`SW`
edges) carries the EB/WB pair — matching the `nbsb`/`ebwb` chart-pair naming
convention from the ATSPM data and the twin's own street names. The N/S vs E/W
assignment (which physical leg is "eastbound" vs "westbound") was derived from
each leg's bearing off junction center `J` in the net's local coordinates
(NE leg is closer to due-east than true NE; SW leg mirrors it), consistent
with the artery being signed EB/WB rather than NE/SW-bound.

**WB is 3 edges, not 1.** `sumotwin`'s slip-lane rework split `NE_in` at the
point where the traced free-right diverges, so any WB thru/left route must
list all three segments (`NE_in NE_in.15 NE_in.79`) to actually reach the
signal — a single-edge `NE_in`→`SW_out`/`S_out` route (the pre-slip topology)
no longer resolves. This was caught during the RL-replication planning pass:
the original build script still had the 1-edge form and failed to load
against the current network; fixed here.

Each `<flow>` only specifies an **edge-level** `<route>`; no per-lane
assignment is set on the flow itself. This is sufficient: SUMO's junction
`<connection>` table already restricts each inbound→outbound edge pair to its
real lane(s) (e.g. EB-thru can only use `SW_in` lanes 0–2, EB-left only lanes
3–4), and the default lane-changing model funnels vehicles into a legal lane
before the stop line.

## Known gap: right turns

`S_in→NE_out` (NB-right), `N_near→SW_out` (SB-right), `SW_in→S_out` (EB-right,
sharing `SW_in` lane 0 with EB-thru), and `NE_in→NE_in.15→E1→N_out.37`
(WB-right — the traced free-right slip that bypasses the signal entirely) are
all real lanes in the network, but **GDOT never reports right-turn counts for
this intersection** — neither the portal's `data.txt` export nor the
`*-thru.jpg`/`*-left.jpg` TMC charts have an R column/movement. Per the
project's fidelity policy (no fabricated values), these are left at **zero
flow** rather than guessed — this under-represents real right-turning traffic
and should be kept in mind when interpreting saturation/spillback results on
the `NE_out`, `SW_out`, `S_out`, and `N_out.37` receiving links.

If right-turn counts become available later, add `("nb","right")` etc. to
`ROUTE_EDGES` in `build_demand.py` and to `portal_report.py`'s parsing, then
re-run.

## Vehicle counts per bin

Each `<flow>` uses `number="N"`, the **exact integer vehicle count straight
from `data.txt`** for that 5-min window — not SUMO's own `vehsPerHour`
periodic insertion (which was found to systematically over-insert by ~2% over
many short 300 s windows), and not a rounded rate derived from a digitized
`vph` value (the old pipeline's `N = round(vph × 300s / 3600)` step, which no
longer applies since data.txt already gives a count, not a rate). A
`count == 0` bin simply emits no `<flow>` for that interval — there's nothing
to simulate either way, same behavior as the old pipeline's NaN-bin skip.

**Caveat found while validating this pipeline:** not every `count == 0` bin
is a genuine measured zero. `0505` and `0506` each have a block where **all 8
movements read exactly 0 simultaneously** — `0505`: 23:05–23:55 (50 min);
`0506`: 00:00–04:10 (4h15m). A real intersection carrying 50k+ veh/day does
not have every single movement (including the highest-volume ones) drop to
literal zero at once; this is a sensor/communication outage, matching the
overnight comm-dropout pattern the top-level `CLAUDE.md` already documents
for this intersection's *other* data source — the portal is just reporting
it as `0` here instead of leaving it blank. `0507`/`0508` have no such
system-wide simultaneous run (only scattered, non-simultaneous individual
zero bins on low-volume movements, e.g. `wb-left`/`nb-left` overnight —
plausibly genuine). Numerically this changes nothing (a skipped zero-bin and
a skipped NaN-bin both emit no `<flow>`, so the simulated output is
unaffected), but **don't describe these two outage windows as "confirmed
recorded zero traffic"** — they're unmeasured, not zero. Per `CLAUDE.md`'s
own guidance this isn't a reason to discard either day, just to flag it here
and treat those specific windows as unknown rather than validated-empty
if it matters for the analysis at hand.

## Validation

All four full-day runs (`sumo -c sumodemand/050{5,6,7,8}.sumocfg`) complete
with **zero warnings or errors** and insert vehicle counts that **exactly
match** each day's data.txt "Vehicle Total" daily sum: 0505 → 46,283, 0506 →
54,606, 0507 → 50,906, 0508 → 51,530. (0507's old digitizer-based build
inserted ~50,682, a −0.44% shortfall — the exact-count switch closed that gap
entirely.) `time-to-teleport=300` is set precautionary should the signal
timing itself cause a queue-related teleport, not because of anything
demand-side.

## Run it

```bash
sumo-gui -c sumodemand/0507.sumocfg   # or 0505 / 0506 / 0508.sumocfg
sumo      -c sumodemand/0507.sumocfg  # headless
```

These are standalone configs (they don't touch `sumotwin/7065.sumocfg`, which
stays demand-free per its own header comment). To wire a profile into the twin
directly instead, uncomment `<route-files>` in `sumotwin/7065.sumocfg`,
point it at `../sumodemand/0507.rou.xml`, and change `<time><end>` from
`3600` to `86400`.

## What this is / isn't

This is a **calibrated real-day demand profile**, useful for validation and as
a distribution anchor. Per the earlier discussion on training methodology: do
**not** train an RL agent on a single day's profile scaled up/down — that
freezes this day's directional split, turning ratios, and burst shape at every
demand level. Use 0505/0506/0507/0508 (and more days as their data.txt is added) to
characterize the *range* of these factors, and randomize over that range each
training episode, with a demand-scaling sweep pushed into oversaturation for
the spillover extension. (`rlagent/plan.md`'s initial replication pass
deliberately uses a single day as-is instead — see that plan for why.)
