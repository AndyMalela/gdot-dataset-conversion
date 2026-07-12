# Experiment log — RL signal control on SIG#7065

Running lab notebook for the RL-agent work (`rlagent/`). Each experiment is
a dated, self-contained record: motivation, exact architecture/action-space/
training config, results (including failures), diagnosis, and what it led to
next. **Failures and missteps are recorded deliberately** — they are the
"experimentation" narrative for the graduation progress report, not noise to
be cleaned away.

This folder is expected to grow. Add a new `EXP-NNN_<slug>/` per experiment;
keep raw result snapshots under each experiment's `data/` so the numbers
quoted in a `report.md` can always be traced back.

## Conventions

- **Fidelity policy** (project-wide, see `/CLAUDE.md`): never rescale/smooth/
  invent numbers to match an expectation; report what the system actually did,
  including when it fails. Every metric here is copied from a real run.
- **Metrics** (from SUMO `tripinfo`, via `metrics.py`):
  - *throughput* = number of trips **completed** within the drained sim.
  - *delay* = mean **total delay = `timeLoss` + `departDelay`** (s) over trips.
    `timeLoss` is in-network delay; `departDelay` is time spent unable to enter
    (insertion backlog = spillback to source). **Both matter** — under
    oversaturation a controller can keep `timeLoss` low by holding vehicles out
    of the network, dumping the delay into `departDelay`. Reporting `timeLoss`
    only (the original bug, fixed 2026-07-12) hides this; see EXP-002 §3.4.
    Also: when trips don't complete (gridlock), completed-trip averages are
    survivorship-biased, so low delay next to low throughput is *worse*.
  - *halts* = mean `waitingCount` (distinct stops) over completed trips.
- **"drain"**: the eval runs demand for the 24 h day, then keeps simulating
  with no new arrivals until the network clears (to 30 h), so trips still en
  route at midnight are counted honestly rather than truncated.
- **Held-out day**: 0508 is never used in training; it is the generalization
  test. Training days: 0505, 0506, 0507.

## Index

| ID | Title | Outcome |
|----|-------|---------|
| [EXP-001](EXP-001_ordered-actuated-extend-advance/report.md) | Realistic ordered-actuated action space (binary extend/advance) + linear FA | **Negative** — degenerate policy, gridlocks at all demand levels incl. 0.5×. Root cause: representation under-expressiveness (lane weights shared across phases). |
| [EXP-002](EXP-002_phase-gated-features/report.md) | Phase-gated lane features (restore per-phase×lane expressiveness) | **Mixed / corrected.** Fixes the gridlock/degeneracy (real representation bug); throughput 100% at all scales. But on **total delay (incl. insertion backlog)**, RL beats fixed-time **only at 0.5× (v/c 0.62)**; from ~v/c 0.7 up it is worse (+98% to +440%, worst near capacity). Matches the paper. Also fixed a metrics bug (timeLoss-only undercounted oversaturated delay). **High-saturation performance is the open problem.** |
| [EXP-003](EXP-003_spillback-features/report.md) | Spillback-aware features (normalized occupancy + phase-gated elapsed) + norm-only ablation + **multi-seed (003b)** | **Best RL variant on the median** — v3 beats norm & EXP-002 at every scale (1.3×: 1855 vs 2747 vs 3709 s). Normalization = clean monotonic gain. **But ~40% of seeds hit a parking collapse** (high variance); the 1.3× "spike" was a bad-seed artifact. Still short of fixed-time in saturation. Root cause: phase-gating hides other approaches from the advance decision. |

## Planned / backlog (not yet started)

- **EXP-003c — robustness fix.** The parking variance has two compounding
  causes (see EXP-003 §4b/§4c): (i) partial observability — phase-gating hides
  the starved approaches from the advance decision; (ii) an **ill-conditioned
  LSTDQ solve** (`A` singular; `cond(A+ridge·I)`≈1e8–1e10; ridge-sensitive ~1.5;
  non-PD) that leaves the elapsed-time weight under-determined and
  counter-intuitively signed. Candidate fixes: (a) non-gated global per-approach
  queue summary; (b) raise/cross-validate ridge; (c) drop the redundant phase
  one-hot / use one global elapsed feature; (d) SVD/pseudo-inverse solver;
  (e) enforce max-green in the env instead of learning it via elapsed (removes
  the destabilizing feature, hard-bounds parking).
- **EXP-004 — reward redesign.** The `−queue` reward is gameable under
  oversaturation (RL sheds delay into insertion backlog; see EXP-002 §3.4).
  Try a throughput- / total-delay-aware reward that penalizes insertion
  backlog. EXP-003 lets the agent *see* spillback; the reward may be needed to
  make it *act* on it.
- **Stronger baselines (deferred until real signal data is available).** Our
  current baseline is *pretimed Webster* — the weaker of the paper's two
  baselines. The real SIG#7065 signal is **actuated** (gap-out records in
  ATSPM) + time-of-day. Planned: (a) a passage-time / gap-out **actuated
  baseline** (paper Appendix A), and (b) comparison vs the **real timing plan**
  if the ATSPM phase-switching data can be extracted. Report RL vs both.
- **DRL / other adaptive baselines (EXP-005/006+).** Compare the linear-FA
  method against deep RL (DQN, etc.) and other adaptive controllers — the
  interpretability-vs-performance trade-off is the point.

## Cross-cutting: infrastructure notes

- **Simulation backend**: headless training/eval uses `libsumo` (in-process),
  ~5.5× faster than the TraCI socket here (12 s → 2.2 s for a 1 h window);
  GUI (`watch.py`) uses TraCI. Selected automatically by `sumo_env.py`.
- **Reproducibility / failsafe**: `train_random.py` checkpoints weights +
  accumulated experience + RNG state every episode (atomic write); `--resume`
  continues bit-exactly (verified: a resumed episode was byte-identical to the
  uninterrupted run).
- **Baseline**: Webster fixed-time (`fixed_time.py`) runs on the *same* env
  and the *same* 4-phase cycle, so RL-vs-fixed differ only in *when* they
  advance — a fair, apples-to-apples comparison.
