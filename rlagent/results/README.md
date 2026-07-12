# `results/` layout

Run artifacts for the RL-agent experiments. The **narrative** (motivation,
diagnosis, conclusions) lives in `../experiments/EXP-*/report.md`; this folder
holds the raw run outputs those reports draw from.

## Top level

- **`weights_random_s0.npy`** — the canonical current-best weights
  (EXP-002, `feature_mode=phase_gated`, 264 params). This is the default
  `--weights` for `eval_heldout.py` and the file the `watch.py` examples use.
  Kept at the root on purpose so those paths stay stable.

## Per-experiment subdirs

| Dir | Experiment | Contents |
|-----|-----------|----------|
| `exp002_phasegated/` | EXP-002 (`phase_gated`) | held-out eval tripinfos (`ti_heldout_{rl,fixed}_x*.xml`), training tripinfos, `train_random_s0.csv` (per-episode log), train/eval `.log`s |
| `exp003_norm/` | EXP-003 ablation (`phase_gated_norm`) | **EXP-002's features, only *normalized* (count→occupancy); no new features.** Same 132-dim / 264 params. Isolates "does normalization alone help?" |
| `exp003_v3/` | EXP-003 (`phase_gated_v3`, single seed) | `phase_gated_norm` **plus** the one new feature (phase-gated normalized elapsed time). 136-dim / 272 params. weights + eval tripinfos + logs |
| `exp003b_v3/` | EXP-003b (`phase_gated_v3`, multi-seed s1–s4) | per-seed weights + `s0..s4/` eval subdirs (the parking-collapse variance study) |
| `archive_phase0_0507/` | **Retired** Phase-0, old 8-stage action space (Jul 10) | single-day 0507 runs incl. `*FAILED*`/`run1-3` iterations + the old `REPORT.md`. Superseded — does **not** match the current `stages.py`/`sumo_env.py`. History only. |

## Notes

- **`checkpoint_*.pkl` were deleted (2026-07-12).** They were resume-only caches
  (`--resume` state: final weights + accumulated experience buffer + RNG), ~6.9 GB
  total. Not needed for metrics or per-episode analysis — episode history is in the
  `train_random_s*.csv` files, metrics come from the tripinfo XMLs via `metrics.py`.
  To resume/extend a run you must retrain (the final weights are still here).
- `metrics.py` and `eval_heldout.py` take paths as arguments, so nothing in this
  folder is hard-referenced by code except the top-level `weights_random_s0.npy`
  default noted above.
