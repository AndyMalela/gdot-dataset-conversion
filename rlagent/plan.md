# Plan: replicate Sahachaiseree's linear-FA + LSTDQ controller, get initial metrics

## Goal (this plan only)

Faithfully reproduce Sahachaiseree & Oguchi's method — a **linear function
approximator trained with LSTDQ** for stage-selection traffic-signal control
— on the real SIG#7065 twin (`sumotwin/` + `sumodemand/`), and get a first
batch of metrics (average delay, halts, throughput) compared against a
fixed-time baseline, in the same format as the paper's own Table 6.

**Explicitly not in scope for this plan** (see "Deferred" at the bottom):
the high-saturation / spillback state-feature extension, and training on a
randomized multi-day demand distribution. Those come *after* this
replication is validated — trying to do both at once would make it
impossible to tell whether a bad result is a replication bug or a real
finding about the extension.

---

## Starting point (already built, don't redo)

- **`sumotwin/7065.net.xml`** — real SIG#7065 network, reviewed and fixed
  (two dead-ended approaches repaired, see review notes). Known caveats:
  approach lengths are ~25–55% off from the intended aerial measurements,
  and 3 of 4 real right-turn movements have no demand (never charted by
  GDOT); the 4th (WB) now bypasses the signal entirely via the traced slip
  lane (`E1`).
- **`sumodemand/0507.rou.xml`, `0508.rou.xml`** — calibrated single-day
  demand from real TMC data, validated against OCR daily totals (±2.5%).

## Problem found while scoping this plan

1. ~~**`sumodemand`'s WB routes are now broken.**~~ **FIXED.** They were
   built against the network *before* the slip lane split `NE_in` into
   `NE_in → NE_in.15 → NE_in.79`. `ROUTE_EDGES` in `build_demand.py` updated
   to the 3-edge WB path, `.rou.xml` files regenerated, and re-validated
   with a zero-warning, 100%-insertion full-day run against the current
   `sumotwin/7065.net.xml`. See `sumodemand/README.md`.

2. **The current TLS is not the paper's action space.** `7065.net.xml`'s
   signal at `J` is `netconvert`'s default actuated 2-ring logic (NS-pair
   green+protected-left, then EW-pair green+protected-left — 8 phase
   *entries* but only 2 real stage groups). Sahachaiseree's method needs a
   **stage-selection** action space: discrete stages the agent picks
   directly, including single-approach-exclusive stages (their Fig. 5 has
   8 stages: 2 NS combos, 2 EW combos, and 4 single-leg-only stages). This
   has to be designed fresh from our real connection map (dumped during the
   network review) — see Phase 0 below — and driven by the agent through
   TraCI rather than SUMO's built-in actuated logic.

---

## Phase 0 — Design the stage table

Governed by **[`rlagent/regulations.md`](regulations.md)** — this is not an
arbitrary design choice, it's constrained by GDOT policy and Georgia law.
Read that file before doing the tasks below.

- [x] ~~Fix `sumodemand/build_demand.py`'s `ROUTE_EDGES` for WB~~ — done.
- [x] GDOT 6785-2 warrants computed from all 4 calibrated days (rolling
  peak hour): **EB/NB/SB lefts warranted protected** (≥125 vph met on
  nearly all days, cross-products up to 127k); **WB-left never meets the
  125 vph leading warrant (70–92 vph)** → permissive-only, matching GDOT's
  asymmetric practice. Recorded in `stages.py` docstring.
- [x] Stage table designed: `stages.py` — 8 stages = the 8 NEMA dual-ring
  conflict-free combos (also a 1:1 translation of the paper's Fig. 5 set;
  their left-hand-drive "left/right" ↔ our right/left). WB-left runs 'g'
  (permissive/FYA-style) in EW_THRU, unopposed 'G' in EW_LEFT/WB_ONLY.
  Rights get no dedicated stage (zero demand + RTOR default), 'g' where
  conflict-free.
- [x] Interstage timing computed from real geometry + ITE formulas:
  **yellow 4.0 s** (35 mph, PRT 1.4 s, 10 ft/s² decel), **all-red 3.0 s**
  (longest crossing 40.3 m — the NB/SB through across Peachtree — measured
  from the net's internal lane lengths). δ = 1 s, min green 3 s (paper's
  low-constraint setting).
- [x] Signal driven purely via `traci.trafficlight.setRedYellowGreenState()`
  (`sumo_env.py`); `7065.net.xml` untouched.

**Done when:** a script can step through all 8 stages via TraCI in a fixed
order for one full cycle, with correct interstage timing, and no SUMO
errors/warnings. **✓ Done** — verified on live 0507 demand (08:00 window),
all 8 stage strings accepted, interstage sequencing correct.

---

## Phase 1 — Environment wrapper (`rlagent/env.py`)

Mirror the paper's Section 3.2 MDP definition on our network:

- **State `x(s)`:** one-hot of the active stage (8-dim) + raw vehicle count
  per approach lane (from `traci.lane.getLastStepVehicleNumber`), one count
  per real inbound lane up to the stop bar. Because our approach lengths
  are already short (see caveats above), a lane's full count is the
  equivalent of the paper's 79 m detector on their longer legs — no
  separate "detector window" needed.
- **Action:** stage index `∈ {0..7}` from Phase 0's table.
- **Reward:** `R = -Σ Qˡ` over all approach lanes, a vehicle counts as
  queued if speed < 5 km/h — copied directly from the paper's Eq. 13, not
  reinterpreted.
- **Timing:** decision interval `δ = 1 s`, minimum green `υ = 3 s`, amber
  4 s / all-red 3 s (computed in Phase 0 — supersedes the earlier 3 s/1 s
  placeholder borrowed from the paper).
- Feature vector `x(s,a)` (state-action, size `m·n` per the paper's
  Eq. 9–10) lives in `lstdq.py` (`LinearQ.phi`), not a separate file.

**Done when:** `env.py` runs one full episode end-to-end with random
actions against `sumodemand/0507.rou.xml`, no TraCI errors, and prints a
sane reward trace (mostly negative, moving with visible queue buildup).
**✓ Done** — implemented as `sumo_env.py` (32 tracked lanes → 40-dim
state); random 30-min episode ran clean, reward trace sane.

---

## Phase 2 — Linear FA + LSTDQ learner (`rlagent/lstdq.py`, `rlagent/agent.py`)

- Implement the closed-form update (paper's Eq. 11): build `A` (outer
  product of `x(s,a)` with `x(s,a) - γ·x(s', argmax_a q̂(s',a;w))`) and `b`
  (`x(s,a)·r`) over a batch, solve `w = A⁻¹b`. Add ridge regularization
  (`A + λI`) before inverting — the paper doesn't need it at their toy
  scale, but our larger real lane count makes `A` more likely to be
  ill-conditioned, and this is cheap insurance.
- `ε`-greedy behavior policy for experience collection, one episode per
  learning epoch (matches the paper's Algorithm, Fig. 2), `γ = 0.9`.
- Match the paper's hyperparameter sweep as a starting point:
  `ε ∈ {0.01, 0.05, 0.10, 0.16}`, pick whichever converges best on our
  network rather than assuming their optimum (`ε = 0.05`, `ε = 0.16`
  depending on setting) transfers directly.

**Done when:** a unit/sanity check confirms the LSTDQ update produces a
sensible greedy policy on a tiny synthetic case (e.g. a 2-state toy MDP)
before trusting it on the full SUMO environment. **✓ Done** — `lstdq.py`'s
toy check recovers the analytic optimum exactly (Q = [9, 10], γ = 0.9).
ε-sweep remains open (initial run uses the paper's ε = 0.05).

---

## Phase 3 — Baseline controller

- Implement fixed-time / pretimed control using the paper's own Webster
  formula (Appendix A.1: `C_op = (1.5L+5)/(1-ρ)`), with cycle/split
  computed from the calibrated 0507 demand's peak volumes. This is the
  paper's primary comparison point (their Table 6) — reproduce it before
  reaching for anything fancier (actuated/passage-time can come later).

**Done when:** the fixed-time controller runs a full day of `0507.rou.xml`
and produces stable (non-deadlocked) average delay / halt numbers.
**✓ Done (AM-peak window)** — `fixed_time.py`: Webster over EW_THRU /
EW_LEFT / NS_THRU / NS_LEFT gives ρ = 0.438, C = 83.6 s for 0507
07:00–09:00; runs stable (5,119 trips, avg delay 33.45 s, avg halts 0.855
— strikingly close to the paper's pretimed principal-pattern numbers).
Full-day run still open.

---

## Phase 4 — Initial training run

- Train on **`sumodemand/0507.rou.xml` alone** (single calibrated real day)
  — intentionally not the randomized/multi-day/saturation-sweep
  distribution discussed for the later extension. This keeps the
  replication apples-to-apples with the paper's own single-arrival-pattern
  design and isolates "does the replication work" from "does it generalize."
- Train for enough episodes to see convergence (paper converged in ~10–50
  episodes with LSTDQ at their toy scale; budget more headroom here — our
  network and state space are larger and messier). Track average step
  reward, average delay, average queue per episode (mirrors paper's Fig. 7).
- Repeat across a handful of random seeds if compute allows (paper used 8);
  start with 1–3 for a fast first pass and say so explicitly in the
  results writeup rather than presenting a single seed as definitive.

**Done when:** the reward curve visibly rises and stabilizes rather than
diverging or staying flat.

---

## Phase 5 — Initial metrics report

- Evaluate the converged agent on held-out random-seed episodes with
  exploration off (paper used 30 test episodes; scale to what's feasible).
- Report average delay, average number of halts, and throughput for the
  RL agent vs. the Phase 3 fixed-time baseline, with % difference — same
  shape as the paper's Table 6.
- Deliverable: `rlagent/results/` with the metrics table, convergence
  plots, and a short writeup of whether the replication qualitatively
  matches the paper's story (LSTDQ converges fast; RL beats fixed-time).

---

## Deferred to a later plan (do not pull into this one)

- High-saturation / spillback state-feature extension (the 1–2 added
  features discussed separately).
- Domain-randomized training across multiple calibrated days + a
  demand-scaling sweep into oversaturation.
- Fixing approach-length/geometry fidelity in `sumotwin`, and digitizing
  the missing right-turn movements.

---

## Milestone checklist

- [x] Phase 0a: WB demand routes fixed + regenerated
- [x] Phase 0b: left-turn warrant criteria computed from calibrated demand
      (WB-left unwarranted → permissive-only; others protected)
- [x] Phase 0c: stage table + Georgia-consistent interstage timing designed
      (`stages.py`), drivable via TraCI for a full cycle
- [x] Phase 1: env runs a full random-action episode cleanly (`sumo_env.py`)
- [x] Phase 2: LSTDQ verified on toy case (`lstdq.py`), wired to the env
- [x] Phase 3: fixed-time baseline running and stable (`fixed_time.py`,
      AM-peak window; full-day pending)
- [ ] Phase 4: RL agent trains and converges on 0507 (in progress —
      first 20-episode AM-peak run)
- [ ] Phase 5: initial metrics table + writeup produced
