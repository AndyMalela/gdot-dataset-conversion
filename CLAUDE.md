# Adaptive Traffic Signal Control — linear vs deep RL at real, field-calibrated intersections (Atlanta, GDOT)

## Project

Graduate thesis (Ritsumeikan, eSocLab), due **2026-01-20**. Compare learned signal controllers against the
controller GDOT actually runs, in SUMO simulations built and validated from GDOT ATSPM data.

**Research direction (set at the midterm, 2026-11-19):** when is cheap **linear RL** (LSTDQ, SARSA(λ)) enough,
and when does **deep RL** (DQN) pull ahead — compared with GDOT's real timing plan, by time of day, traffic level,
surges, and at a simple vs a busier intersection. Gap (in the studies reviewed): linear and deep RL are rarely
compared directly, and never at the same field-calibrated intersection against its deployed controller on
held-out days (closest: Schreiber 2022, Alegre 2022, RESCO/Ault & Sharon 2021, Gong 2019, Kwesiga 2025).

**Timeline promised at the midterm:** by 2026-11-30 train & test SARSA and DQN at site 137 · by 2026-12-19 add a
contrasting (busier, near-capacity, more lanes/phases) intersection — likely 7065 · by 2026-01-20 finish the thesis.

## Rules (apply to every step)

- **Fidelity.** Never rescale, smooth or invent values to match an expectation. Use raw numbers; leave outages
  blank and say so. Any correction (e.g. the 137 presence-zone undercount estimate) is disclosed as an estimate.
- **Data only from GDOT ATSPM** for evidence and inputs (plus standards such as HCM / MUTCD / FHWA guides; road
  layout from OpenStreetMap). No outside traffic figures (news, AADT). Flag any outside constant.
- **Disclose every deviation** from the real intersection and agree it before results; never keep one silently.
- **Locked test sets — never look before the final run:** 137 = 2026-05-18..05-29; 7065 = 2026-10-04..10-22.
  Write pass criteria / statistics before running (`TEST_PLAN.md`, `VALIDATION.md` per site).
- **Tooling.** SUMO 1.27.1 is pinned in uv: always `uv run …`, never the system `sumo` (1.28 crashed).
- **Git.** Commit locally; push to origin main only what won't break. Commit messages end with
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. The user reads `.md` files in Obsidian on mobile — push when done.
- **Writing for the user:** plain, literal wording; slide text = short simple bullets; cite only what was checked.

## Current state

- **Site 137** (W. Paces Ferry Rd @ E. Andrews Dr / Slaton Dr), primary site. Study period Mar 2–May 29, 2026
  weekdays: 29 training / 20 held-out (validation) / 7 locked test days.
  - Simulation **validated** (attempt 8, `atsc/sites/137/VALIDATION.md`): green length within 3 s in 34/35 cases,
    gap-out share within 15 pts in 28/35 (needed 28), health pass; left-arrow skips 18/35 still off (reported).
  - Tuned on training days: passage times, driver impatience 0.5, presence-zone undercount factors; floating
    force-off P1/P5; signal 138 runs upstream with its real timing.
  - Final test done (`TEST_PLAN.md` amendment 1, `INTERPRETATION.md`): delay s/veh — GDOT plan 31.2, LSTDQ 25.3,
    Q-learning 30.6 (also actuated-no-cycle 24.9, MaxPressure 26.1, ARS 30.4, Webster 117.7).
  - Not yet validated: delay/queues (Split Failure, Approach Delay — see `futureplan.md`), P2/P6, skips.
- **Site 7065** (Peachtree Rd @ Piedmont Rd): earlier v2 site; Peachtree through counts come from presence zones
  (2–9× too low in daytime) — must be handled before it can be the busier second site.
- **Next:** SARSA(λ) and DQN at 137 (same inputs, actions and rules; fixed tuning budget written into TEST_PLAN
  first); then the second site; strengthen validation (delay check, bootstrap over days).

## Where things are

```
GDOT/
├── atsc/                 v2 pipeline (start here: atsc/README.md)
│   ├── sim/              NEMA engine, SUMO glue, demand, metrics, Webster, MaxPressure
│   ├── rl/               LSTDQ + learning methods
│   └── sites/137, 7065/  per-site spec, VALIDATION.md, TEST_PLAN.md, INTERPRETATION.md, eval_*/
├── intersections/        ATSPM data per signal (counts, timing, config); OVERVIEW.md, signal_list.csv
├── tools/                ATSPM scrapers/readers (atspm_*.py, lanecheck/, build_sim.py)
├── presentation/         midterm decks: final/ (talk decks + SCRIPT_latest_fable.md), archive/ (old versions)
├── referencepaper/       Sahachaiseree (base method), Chen thesis / APSIPA (labmate)
├── queries/              literature notes (experimental setup, state representation, RQ framing)
├── PLAN.md               research framing (2026-11-16; partly superseded by the direction above)
├── PROGRESS.md           live status log, newest first
├── OPEN_ISSUES.md        7065 problem list
├── futureplan.md         post-midterm validation ideas (outcome-level checks from ATSPM)
└── rlagent/, sumotwin/, sumodemand/, data-old/, data-timing/   v1 project (frozen at git tag `pre-v2`) — reference only
```

The literature wiki lives outside the repo at `/home/andy/Downloads/Things/gr-andy/wiki/` (papers in `raw/papers/`).
