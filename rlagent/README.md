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
| `stages.py` | **Phase 0 deliverable.** 8-stage action space (paper Fig. 5 structure = the 8 NEMA dual-ring combos), instantiated from this intersection's real link map, with GDOT 6785-2 warrant-based left-turn treatment (WB-left permissive-only — computed, not assumed) and ITE interstage timing from real geometry (yellow 4.0 s, all-red 3.0 s). |
| `sumo_env.py` | TraCI environment: paper's MDP (state Eq. 12 = stage one-hot + 32 per-lane counts; reward Eq. 13 = −Σ queue at <5 km/h; transition semantics Fig. 6). |
| `lstdq.py` | Linear FA (Eq. 9–10) + LSTDQ optimality update (Eq. 11) with optional ridge. `python3 lstdq.py` runs a toy-MDP check against the analytic optimum. |
| `fixed_time.py` | Webster pretimed baseline (paper Appendix A.1) from the same portal volumes. |
| `train.py` | Episodic ε-greedy training (paper Fig. 2: 1 epoch = 1 episode) + greedy eval with tripinfo metrics. |
| `metrics.py` | avg delay (timeLoss), avg halts (waitingCount), throughput from tripinfo. |

## Deviations from the paper (all deliberate, all documented in-file)

- **Real intersection, real demand** instead of their symmetric toy
  4×3-lane junction with Poisson arrivals — that's the whole point.
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
- **Interstage 7 s** (computed for this 40 m box) vs their 4 s.
- **Asymmetric left-turn treatment** per GDOT warrants (their toy is
  symmetric; Georgia practice and this demand aren't).
- **Ridge term** in the LSTDQ solve (their 20-feature A matrix doesn't need
  it; our 40 correlated lane counts do). `ridge=0` recovers Eq. 11 exactly.
- **Right turns**: zero measured demand (GDOT never reports them) — carried
  in the network, unserved by dedicated stages, WB right = physical slip
  lane outside the signal.
- Their left-hand-drive "left/right" naming maps to our right/left.

## Run

```bash
cd rlagent
python3 lstdq.py                       # solver self-check
python3 fixed_time.py --date 0507     # Webster baseline, AM peak
python3 train.py --date 0507 --episodes 20   # LSTDQ training + greedy eval
```

Default window: 07:00–09:00 AM peak. Results land in `results/`.
