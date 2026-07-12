# rlagent — Sahachaiseree linear-FA + LSTDQ replication on SIG#7065

Replication of Sahachaiseree & Oguchi (IET ITS 2025): an interpretable
traffic-signal controller — linear function approximator over raw stage/lane
features, learned with closed-form LSTDQ — instantiated on the real
Peachtree/Piedmont twin (`sumotwin/`) with real calibrated demand
(`sumodemand/`). Plan: [`plan.md`](plan.md). Regulatory grounding for the
action space: [`regulations.md`](regulations.md).

## Files

| File | What |
|---|---|
| `stages.py` | **Action space.** Realistic ordered-actuated NEMA control: the fixed ring-barrier cycle `EW_LEFT → EW_THRU → NS_LEFT → NS_THRU` with FYA protected-permissive lefts (EB/NB/SB protected in their left phase, permissive in their through phase; WB-left permissive-only per GDOT 6785-2 warrants), protected right-turn doghouse overlaps (NB/SB), shared-lane EB right, and the WB slip lane outside the signal. Selective interstage clearance (only movements that lose right-of-way clear; lead-left→through inserts no all-red). ITE interstage timing from real geometry (yellow 4.0 s, all-red 3.0 s). See [`regulations.md`](regulations.md) §8 for the field verification behind each choice. **This replaces the paper's free 8-stage selection** — see Deviations. |
| `sumo_env.py` | TraCI environment. State = phase one-hot (4) + 32 per-lane counts (paper's Eq. 12 form). **Action = binary {EXTEND, ADVANCE}** over the fixed cycle (not free stage selection). Reward Eq. 13 = −Σ queue at <5 km/h. |
| `lstdq.py` | Linear FA (Eq. 9–10) + LSTDQ optimality update (Eq. 11) with optional ridge. `python3 lstdq.py` runs a toy-MDP check against the analytic optimum. |
| `fixed_time.py` | Webster pretimed baseline (paper Appendix A.1) from the same portal volumes. |
| `train.py` | Episodic ε-greedy training (paper Fig. 2: 1 epoch = 1 episode) on one fixed day/window + greedy eval with tripinfo metrics. |
| `train_random.py` | Domain-randomized training: each episode samples a random day (0505/0506/0507) and demand scale (0.5–1.3×) over the **full day**; 0508 held out entirely for a full-day drained generalization eval (in-range + extrapolated scales). The 0505/0506 sensor-outage bins are masked from the fit (false exact-zero, not real demand). Full-day episodes are ~8× the old peak window, so the default episode count is lower — raise it if you have the budget. |
| `metrics.py` | avg delay (timeLoss), avg halts (waitingCount), throughput from tripinfo. |
| `trainutil.py` | Dependency-free live progress line (bar, per-episode reward/best, ETA) + interrupt-safe checkpointing (atomic write; saves weights, accumulated experience, and RNG state for exact resume). |

**Backend:** headless runs use `libsumo` (in-process, ~5.5× faster than the
TraCI socket here) automatically; `watch.py` (GUI) uses TraCI. No code change
needed — `sumo_env.py` picks the backend from the `gui` flag.

## Deviations from the paper (all deliberate, all documented in-file)

- **Real intersection, real demand** instead of their symmetric toy
  4×3-lane junction with Poisson arrivals — that's the whole point.
- **Ordered-actuated action space, not free stage selection** (the biggest
  change; supersedes the earlier 8-stage cut). The paper's agent picks any
  of 8 stages in any order — more freedom than any real signal has. Real
  NEMA control runs a fixed ring-barrier cycle and only chooses *when* to
  advance, so the action is now binary EXTEND/ADVANCE over
  `EW_LEFT→EW_THRU→NS_LEFT→NS_THRU`. This also makes each phase's signal
  states match the real photographed heads (FYA lefts, doghouse right
  overlaps) — see `regulations.md` §8. Old 8-stage weights/results are
  therefore stale (wrong action & state dimensions) and must be regenerated.
- **Semi-MDP reward + per-second discounting** (found necessary, evidence
  kept): the paper samples the queue penalty once per decision and
  discounts per decision, which at our scale (7 s interstage, near-capacity
  volumes) makes stage-switching artificially cheap — a thrash policy
  collects ~10× fewer penalty samples per simulated hour. Run 1 with the
  paper's literal semantics learned exactly that (its best-return episode
  was its most-switching one; greedy eval 338 s delay ≈ 10× worse than
  fixed-time — artifacts kept as `results/*_run1-perdecision-FAILED.*`).
  Fix: reward = Σ per-second queue snapshots over each decision's whole
  duration, target discounted `γ^duration` (`lstdq.py` handles both forms;
  4-tuple transitions recover the paper exactly).
- **Accumulated-experience refits (LSPI-style)**: the paper refits w from
  only the latest episode; at our scale (320 correlated params) that
  oscillates (run 2, kept as `*_run2-*`). `train.py` re-solves on all
  episodes so far — still closed-form, still hyperparameter-free.
- **Cycle-scale discount horizon**: γ = 0.99 per second (~100 s horizon ≈
  one cycle) instead of a naive γ = 0.9/s (~10 s horizon), which starved
  low-volume approaches invisibly (run 3, kept as `*_run3-*`). The paper's
  γ = 0.9 per *decision* only approximates per-second on their small toy.
- **Interstage 7 s** (computed for this 40 m box) vs their 4 s, applied
  *selectively* — only movements losing right-of-way clear; continuing
  movements (throughs, protected→permissive left downgrades) are held, so
  the two lead-left→through transitions insert no all-red at all.
- **Asymmetric protected-permissive (FYA) left-turn treatment** per GDOT
  warrants (their toy is symmetric protected-only; Georgia practice, this
  demand, and the real FYA heads aren't) — EB/NB/SB lefts turn permissively
  during their through phase, WB-left is permissive-only everywhere.
- **Ridge term** in the LSTDQ solve (their 20-feature A matrix doesn't need
  it; our 40 correlated lane counts do). `ridge=0` recovers Eq. 11 exactly.
- **Right turns**: zero measured demand (GDOT never reports them) — carried
  in the network, unserved by dedicated stages, WB right = physical slip
  lane outside the signal.
- Their left-hand-drive "left/right" naming maps to our right/left.

**Window correction (found, not carried over silently):** `train.py`'s
default window (07:00–09:00) was assumed to be "AM peak" without checking
the data — it isn't. All 4 calibrated days peak in the **PM, ~15:15–18:05**
(4,100–5,050 veh/hr); the AM window averages ~2,570 veh/hr, a moderate
load. `train_random.py` uses the real PM peak window (15:00–18:00);
`train.py`'s AM-window results in `results/REPORT.md` are relabeled there
as a moderate-load case, not "the hardest case" as first (wrongly) reported.

**Results: `results/REPORT.md`** (single-day AM-window run) and
`train_random.py`'s own stdout (domain-randomized run, held-out-day
generalization).

## Run

```bash
cd rlagent
python3 lstdq.py                             # solver self-check
python3 fixed_time.py --date 0507           # Webster baseline
python3 train.py --date 0507 --episodes 20    # single-day/window replication
python3 train_random.py --episodes 20         # full-day domain-randomized + held-out eval
python3 train_random.py --resume              # continue an interrupted run from checkpoint
python3 eval_heldout.py                        # rigorous RL-vs-fixed-time on held-out 0508
python3 watch.py --date 0507                   # watch a trained agent in sumo-gui
```

Results land in `results/`.
