# EXP-001 — Realistic ordered-actuated action space (binary extend/advance) with linear FA

**Date:** 2026-07-11 – 07-12
**Status:** ❌ Negative result (informative). Superseded by EXP-002.
**One-line:** Replacing the paper's 8-way stage-*selection* action space with a
realistic NEMA *ordered-actuated* action space (binary extend/advance) caused
the linear-FA agent to learn a degenerate "park on the busiest phase" policy
that gridlocks the intersection at **every** demand level tested — including
0.5× (half load). Root cause: the extend/advance formulation is
under-expressive for a linear function approximator.

---

## 1. Motivation

The base method (Sahachaiseree & Oguchi 2025, replicated in `rlagent/`) uses a
*stage-selection* action space: at each 1 s decision the agent picks any one of
8 conflict-free stages. That is more freedom than any real signal has — a real
NEMA controller runs a **fixed ring-barrier cycle** and only decides *when* to
move on. To make the digital twin faithful to the real SIG#7065 signal
(verified from field photos of the actual heads — see `rlagent/regulations.md`
§8), the action space was redesigned to the real intersection's operation.

## 2. Architecture under test

**Signal / action space** (`stages.py`):
- Fixed 4-phase ring-barrier cycle: `EW_LEFT → EW_THRU → NS_LEFT → NS_THRU →` (repeat).
- Per-phase movement states match the real heads: FYA protected-permissive
  lefts (EB/NB/SB protected + permissive; WB-left permissive-only), protected
  NB/SB right-turn "doghouse" overlaps, EB shared thru/right lane, WB free-flow
  slip lane outside the signal.
- **Action = binary**: `EXTEND` (hold current phase +1 s) or `ADVANCE` (step to
  next phase in the cycle). No arbitrary jumps.
- Interstage from ITE formulas for this geometry: yellow 4.0 s, all-red 3.0 s,
  applied *selectively* (only movements losing right-of-way clear; lead-left→
  through inserts no all-red). Min green 3 s, decision interval 1 s.

**Learner** (`lstdq.py`, unchanged from the base replication):
- Linear function approximator, `q(s,a) = w_a · x(s)`.
- **State** `x(s)` = `[phase one-hot (4), per-lane vehicle counts (32)]` = **36-dim**.
- **Weights** `w` = 2 actions × 36 = **72 parameters**.
- **Reward** = −Σ queue (vehicles < 5 km/h) on the 32 approach lanes, summed
  per-second over each decision's duration (semi-MDP), target discounted
  `γ^duration`, γ = 0.99 /s.
- Closed-form LSTDQ solve with ridge 1e-4; ε-greedy behaviour, ε = 0.05.
- LSTDQ solver independently verified against a 2-state toy MDP (analytic
  optimum recovered) — so the *solver* is not in question here.

**Training** (`train_random.py`):
- Domain-randomized: each episode samples a random day ∈ {0505, 0506, 0507} and
  a random demand scale ∈ [0.5, 1.3], over the **full 24 h day**.
- 0508 **held out entirely** for the generalization eval.
- Sensor-outage bins masked from the fit (0505 23:05–24:00, 0506 00:00–04:10 —
  a verified ~5 h detector blackout, not real zero traffic).
- 20 episodes, accumulated-experience (LSPI-style) refit each episode.
- Backend: `libsumo` (headless), ~5.5× faster than TraCI here.

## 3. Results

### 3.1 Training appeared to converge

Reward is not comparable across episodes (each has a different demand scale →
different absolute queue magnitude), but at **comparable scale** it improves
clearly over the run (see `data/train_curve.csv`):

| scale band | early episode | later episode | trend |
|---|---|---|---|
| ~0.59× | ep7 −798k | ep15 −393k | ↓ better |
| ~0.72–0.76× | ep1 −2.55M | ep16 −0.70M | ↓ better |
| ~1.00–1.04× | ep3 −2.13M | ep13 −1.40M | ↓ better |

Wall-time per episode also fell for comparable scales (ep1 44 s → ep16 18 s),
i.e. less gridlock as training progressed. **This looked like success.**

### 3.2 Held-out evaluation exposed total failure

On held-out day 0508, RL (greedy, trained) vs. Webster fixed-time, full day
drained to 30 h. Fixed-time and RL run on the *identical* network + 4-phase
cycle, differing only in *when* they advance. (Raw: `data/heldout_eval_RL_vs_fixed.txt`.)

| scale | controller | throughput | delay (s) | RL vs fixed |
|---|---|---|---|---|
| 0.5× | **fixed** | **26,297** (~100%) | **39.2** | — |
| 0.5× | RL | 16,961 (66%) | 205.9* | **+425%** delay |
| 0.8× | **fixed** | **41,255** (~100%) | **39.7** | — |
| 0.8× | RL | 25,755 (62%) | 138.5* | **+249%** delay |
| 1.0× | **fixed** | **51,530** (100%) | **39.9** | — |
| 1.0× | RL | 32,093 (62%) | 112.7* | **+182%** delay |
| 1.3× | **fixed** | **67,124** (~100%) | **41.8** | — |
| 1.3× | RL | 43,548 (65%) | 93.8* | **+125%** delay |

\* RL delay is **survivorship-biased** (only completed trips counted); with
~38% of trips never completing, true RL delay is worse than shown. The
delay-appears-to-*fall*-as-load-*rises* artifact is a direct symptom of this.

**Key reading:** fixed-time serves ~100% of demand at a steady ~40 s delay at
*every* scale. RL fails at *every* scale — **including 0.5×, where the
intersection has ample spare capacity.** So this is not "fails under
saturation"; it is "fails everywhere."

### 3.3 Root-cause diagnosis (the important part)

Instrumenting the trained greedy policy on 0508 at 0.5× (`data/policy_probe.txt`):

```
decisions: 7151
action counts: EXTEND=7142 ADVANCE=9   (advance fraction 0.0013)
phase green-time (s): EW_LEFT 20, EW_THRU 7151, NS_LEFT 20, NS_THRU 6
```

The policy **parks in `EW_THRU`** (the EB/WB through — which serves the single
busiest movement, EB through at ~1,860–2,105 veh/h) essentially forever, and
**starves the Piedmont (NS) approaches and both left phases** (~20 s each over
2 h). With the side street and lefts never served, their queues grow without
bound → gridlock, at any load.

**Why the linear model collapses to this** (weight analysis, `EXTEND−ADVANCE`):

```
phase-bias  EW_LEFT -172   EW_THRU +10   NS_LEFT -206   NS_THRU -41
lane-weights (shared across all phases): mean -9.3, spanning [-196, +140]
```

The Q-function is `w_a · [phase-onehot(4), lanes(32)]`. The **32 lane-count
weights are shared across all four phases**; the only per-phase term is the
one-hot, which adds a single *constant* per phase. Therefore the model **cannot
represent the one rule signal timing needs** — *"extend while the lanes served
by the CURRENT phase are busy; advance once they clear and another phase backs
up."* That rule is an **interaction between the active phase and the per-lane
queues**, and there are no interaction features. The busiest lanes (EB through)
almost never clear → always read "busy" → the shared weights always favour
EXTEND in `EW_THRU` → the agent parks there.

By contrast, the paper's original **stage-selection** action space gives each
stage its *own* weight vector over the lanes — an implicit action×lane
interaction — so "this stage is valuable when its lanes are full" *is*
representable. Swapping to binary extend/advance discarded that expressiveness.

## 4. Missteps / bugs encountered (recorded for the report)

1. **Fixed-time `scale` not forwarded** — when `eval_heldout.eval_fixed` was
   refactored to call `run_fixed(...)`, the demand `scale` argument was not
   passed, so the fixed-time baseline silently always ran at 1.0×. Caught
   because fixed-time throughput was *identical* (51,530) at 0.5/0.8/1.0×,
   which is physically impossible. Fixed by adding `scale` to `run_fixed`.
   (The 1.0× comparison was correct by coincidence; 0.5/0.8× were re-run.)
2. **Truncation-bias inversion** — the first held-out numbers showed delay
   *decreasing* with load, which looked like an impossible "more demand, less
   delay." It is the survivorship-bias symptom of §3.2: gridlocked trips never
   complete, so only the fast trips enter the average. Resolved by reading it
   correctly (via throughput) rather than "fixing" the number.
3. **Fidelity flag (open):** the twin models EB through as **3 lanes**
   (~700 veh/h/lane, unsaturated), but field observation suggests **2 lanes**
   (~1,050 veh/h/lane) due to the active SR-237 widening. The recorded sensor
   throughput of 2,105 veh/h *proves* EB ≥ 2 lanes (one lane maxes ~1,900). So
   the twin likely **overstates EB capacity** — the real high-saturation regime
   is under-represented. Tracked separately; does not affect this experiment's
   RL-vs-fixed conclusion (both ran on the same twin).

## 5. Conclusion & next step

The failure is **not** in the LSTDQ solver, the network topology, or the demand
(fixed-time proves the network + demand are servable, ~100% at ~40 s delay). It
is a **representation limitation**: the binary extend/advance action space +
linear FA over `[phase-onehot, lane-counts]` cannot express phase-conditional
timing, so the learned policy degenerates.

→ **EXP-002**: restore per-phase × lane expressiveness within the same ordered
action space by making the lane features *phase-gated* (place the 32 lane counts
in a per-phase block; zeros elsewhere), which reintroduces the action×lane
interaction the paper's stage-selection had. Decisive test: does the agent then
cycle sensibly and stop gridlocking at 0.5×?
