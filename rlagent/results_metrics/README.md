# results_metrics/ — committed metric data (rebuild figures anywhere)

Compact CSVs extracted from the ~50 GB of raw SUMO tripinfos + training logs
(which are **git-ignored** — see `/.gitignore`). These are everything needed to
rebuild the analysis and figures on any machine; regenerate them with
`python3 rlagent/extract_metrics.py` if the raw artifacts are present.

## `ci_delays.csv` — the CI-graph data
One row per `(variant, seed, scale)`; peak-window total delay (s), day 0508.

| column | meaning |
|---|---|
| `variant` | `pg_raw` / `pg_norm` / `pg_elapsed`, or `fixed` (Webster baseline) |
| `seed` | training seed 0–19 (`-1` for the deterministic fixed baseline) |
| `scale` | demand multiplier: 0.5 / 0.8 / 1.0 / 1.3 / 1.8 (v/c 0.62→1.66) |
| `peak_total_delay_s` | mean total delay (timeLoss+departDelay) over intended-15:00–18:00-depart trips |
| `n_peak_trips` | # trips in that window (sanity/weight) |

Coverage: 20 seeds × 3 variants × 5 scales = 300 RL rows (a couple of 1.3× cells
dropped as incomplete) + 5 fixed rows. Bootstrap over `seed` within each
`(variant, scale)` to get the median + 95% CI — see `plot_metrics.py` /
`finalize_ci.py`.

## `training_curves.csv` — the cumulative-reward data
One row per `(variant, seed, episode)`.

| column | meaning |
|---|---|
| `variant`, `seed`, `episode` | 20 episodes/seed |
| `day`, `scale` | the random day × demand scale drawn for that episode |
| `reward` | that episode's total (semi-MDP) reward (negative = queued veh-seconds) |
| `cumulative_reward` | running sum of `reward` over episodes (the over-time curve) |
| `decisions`, `switches`, `wall_s` | episode decision count, phase switches, wall-clock |

Coverage: pg_raw 20 seeds, pg_norm 20, pg_elapsed 16 (s1–4's original EXP-003b
logs weren't saved — their *delays* are still in `ci_delays.csv`).
**Caveat:** `reward` is **not comparable across episodes** — each episode uses a
different random day×scale, so absolute magnitude varies with load, not just
policy quality (see EXP-001). Read cumulative reward as training *progress*, not
a clean performance metric.

## Figures
`python3 rlagent/plot_metrics.py` (needs `matplotlib`) writes:
- `ci_delay_vs_scale.png` — median delay vs scale, 95% CI bands, fixed-time line.
- `cumulative_reward.png` — cumulative reward vs episode, per variant.

The PNGs are git-ignored (regenerate them); only the CSVs + scripts are tracked.
