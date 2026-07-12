# Initial replication metrics — LSTDQ linear-FA agent on SIG#7065

**Scope:** first pass of `plan.md` Phases 4–5. Single calibrated day (0507),
07:00–09:00 window, single seed, 25 episodes. Not yet: multi-seed, full-day,
ε/γ sweeps.

**Correction (window mislabeled):** this run was described below as "AM
peak" and "the hardest case" — that was an unverified assumption, not
checked against the data. A direct check of all 4 calibrated days shows
**every one peaks in the PM, roughly 15:15–18:05** (4,100–5,050 veh/hr),
never in the AM. The 07:00–09:00 window used here averages ~2,570 veh/hr —
a real but *moderate* load, not the peak. So "our test window is the
hardest case" below is wrong; it's actually a moderate-demand comparison.
See `train_random.py` (domain-randomized PM-peak training) + `eval_heldout.py`
(the anchored held-out evaluation) for the follow-up.

**Eval-methodology note (two bugs found + fixed in the held-out eval).**
`train_random.py`'s *inline* held-out numbers on 0508 are NOT trustworthy
and are superseded by `eval_heldout.py`:
1. *Truncation bias* — the inline eval stopped stepping at the window end
   while still congested, so 30–40% of vehicles never completed and were
   dropped from the tripinfo delay average. Result: an implausible
   "more demand → less delay" inversion (1.0× showed 103 s delay,
   1.5× only 58 s). Delay-over-completed-trips is meaningless when
   completion varies 62–71% across scales.
2. *Windowing artifact* — the `.rou.xml` flows span the full day, so
   extending the sim end to "drain" the 15:00–18:00 window actually kept
   inserting the real 18:00+ demand (a "drained" 1.0× run reported 14,243
   trips vs the 12,322 vehicles genuinely in 15:00–18:00).
`eval_heldout.py` fixes both by evaluating over the **full day** (all real
demand, no artificial window) with an end-of-day drain so every vehicle
completes and is counted, and by running a fixed-time baseline under
identical conditions so the RL numbers are anchored. Its output is the
figure to cite, not the inline block.

## Headline result (greedy agent, exploration off, held-out traffic seed)

| Controller | Throughput (trips done in window) | Avg delay [s] | Avg halts |
|---|---|---|---|
| Webster fixed-time (ρ=0.438, C=83.6 s) | **5,119** | **33.45** | 0.855 |
| LSTDQ linear FA (run 4, converged) | 3,951 | 46.08 | **0.633** |

The replication **converges and controls credibly but does not yet beat
fixed-time on delay/throughput at the AM peak**. It already beats it on
halts (smoother flow for the traffic it serves). Note the paper's own
result shows the RL advantage shrinking as demand intensity rises — at
their heaviest ("principal") pattern RL ≈ pretimed (−5.8% delay), with the
big wins at moderate/low intensity. Our test window is the hardest case;
off-peak windows are the natural next comparison and were not run yet.

## Convergence (run 4: γ=0.99/s, accumulated experience)

Total episode reward: −780k…−340k (chaotic, eps 1–10) → −256k → −165k…−185k
**stable plateau from ep ~14 through 25**. First run with the paper's
rise-and-stabilize signature. `train_0507_s0.csv` has the full log.

## The three adaptations that were required (each evidence-backed;
artifacts of every failed run archived alongside)

1. **Semi-MDP reward accumulation + γ^Δt discounting** (`*_run1-*`):
   paper's one-queue-sample-per-decision reward makes a 10 s stage change
   cost one penalty sample vs ten for ten extensions → thrash policy
   (338 s delay; its best-return episode was its most-switching one).
2. **Accumulated-experience refits, LSPI-style** (`*_run2-*`): refitting
   320 correlated weights on a single episode's data oscillates
   (185 s delay, no reward trend). Re-solving on all episodes so far
   converges; still closed-form, still hyperparameter-free.
3. **Cycle-scale discount horizon** (`*_run3-*`): γ=0.9 per *second* is a
   ~10 s horizon — starving a side street is invisible (117 s delay with
   suspiciously *good* halts = heavy movements served smoothly, light ones
   parked; throughput 2,760 exposed it). γ=0.99/s (~100 s ≈ one cycle)
   fixed it. The paper's γ=0.9 *per decision* only ≈ per-second on their
   small, extension-dominated toy.

**Interpretation for the thesis:** these aren't bugs in the paper — they're
scale effects. Its formulation is internally consistent on a 4 s-interstage,
undersaturated toy intersection and breaks in three specific, explainable
ways on a 7 s-interstage, near-capacity real one. That's a finding, and it
motivates the planned high-saturation extension rather than undermining it.

## Known caveats on these numbers

- Single seed, single day, single window; throughput counts only trips
  completed by 09:00 (identical truncation for both controllers — fair).
- Right-turn demand is structurally missing (never measured by GDOT).
- `sumotwin` geometry caveats (approach lengths, construction state) per
  CLAUDE.md apply to both controllers equally.

## Next steps (in order)

1. ~~Off-peak + moderate windows~~ — superseded: see `train_random.py`,
   which trains on the real PM peak window with domain-randomized
   scale (0.5–1.3×) and day (0505/0506/0507), holding 0508 out entirely
   for a genuine generalization test (in-range 1.0× and extrapolated
   1.5×/1.8× scales).
2. More episodes + ε/γ sensitivity, then 2–3 seeds for spread.
3. Full-day evaluation vs the full-day Webster baseline (52.5 s delay).
4. Only after replication is satisfactory: the saturation/spillover
   state-feature extension (separate plan).
