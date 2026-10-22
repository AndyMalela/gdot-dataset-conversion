# EXP-007 — corrected phase model + extended twin: RL and Webster vs real GDOT timing

**Status (2026-10-05): baselines done; RL moved to EXP-008 (GDOT dual ring).** Results §3 rewritten after an independent monitor review found the earlier version stale.
Single trial run, low statistical weight by design (the student asked for trial results first).

## 1. Why

An independent review of EXP-005/006 (2026-10-05) found that `rlagent/stages.py` — the phase model used
by both the RL env and the Webster baseline — was built under the rotated count labels and never
re-derived after the direction fix. Checked against the code and GDOT's configuration:

| | Old `stages.py` | GDOT's controller (evidence) |
|---|---|---|
| Peachtree lefts (dual lanes, NEMA 1+5) | permissive during the through phase; NE-leg left never protected | **protected-only** (Split Failure titles list permissive phases only for the Piedmont lefts; field photo: two left-arrow heads, no FYA sign) |
| Left → through transition | no yellow / all-red | yellow + red clearance every cycle on P1, P5, P3, P7 (Timing & Actuation) |
| Webster lost time L | 18 s | — |

Both gave RL and Webster capacity the real controller doesn't have. EXP-006 (training on that model,
and on the short twin) was stopped at episode 1–7 of 20 and is superseded.

## 2. Setup (changes from EXP-005 v6 / EXP-006)

- `stages.py`: Peachtree lefts protected-only (`G` in EW_LEFT, red otherwise); Piedmont lefts
  protected-permissive (FYA) unchanged. Every transition in which a movement loses green **or drops
  from protected to permissive** pays yellow (4 s) + all-red (3 s). Webster's L becomes 28 s.
- `sumo_env.py`: network = `sumotwin/7065_ext.net.xml` (real approach lengths); the upstream `*_ext`
  edges are in the state/reward lane set; spillback entry edges moved to the network edge.
- RL max greens = the largest green GDOT programs for that movement in any plan (split − yellow − red,
  `intersections/7065/timing/timing_plan_7065.json`): EW_LEFT 36, EW_THRU 80, NS_LEFT 21, NS_THRU 54 s
  (were 30/70/15/92, inherited from EXP-004's tuned-actuated envelope under rotated demand).
- `train_random.py`: `--no-eval` now actually skips the built-in May 8 held-out eval (it was ignored).
- Demand: `data/demand/<day>.rou.xml` built on the extended twin by `data/build_demand.py` (same rules
  as `tools/build_sim.py`; Oct 2 file is byte-identical to EXP-005 v6's).
- Days: RL trained on **2026-09-29** (20 full-day episodes, demand ×U(0.5, 1.6) per episode, 3 seeds),
  seed selected on **2026-09-30** (lowest whole-day delay), tested on **2026-10-02**. Webster designed
  from 2026-09-29's busiest hour in 15:00–18:00, tested on 2026-10-02.
- Real GDOT timing: unchanged from EXP-005 v6 (calibrated NEMA, same frozen signal file), re-run here.
- Metric: total delay (timeLoss + departDelay) per vehicle by intended departure; SUMO seed 9999; drain to 30 h.

## 3. Results (Oct 2, total delay s/veh; all 47,149 counted vehicles served, 0 teleports, 0 collisions)

Numbers recomputed independently from the tripinfo files by the monitor review (2026-10-05).

| Controller | Phase structure | Night 00–06 | AM 06–10 | Midday 10–15 | PM 15–18 | Evening 18–24 | Whole day |
|---|---|---|---|---|---|---|---|
| Real GDOT timing, actuated (SUMO NEMA) | GDOT dual ring, **P1 forced to lead** (SUMO's TS2 NEMA as configured won't serve a lagging P1; Type 170 serves it but mis-applies the force-offs; other controller types untested) | 32.3 | 45.7 | 48.9 | 69.7 | 50.6 | **51.2** |
| Real GDOT timing, fixed-time | GDOT dual ring, exact order (P2→P1, P5→P6, P3→P4, P7→P8), programmed splits, no actuation | 32.5 | 48.0 | 49.8 | 68.5 | 49.9 | **51.5** |
| **Webster, GDOT dual ring + pedestrian minimums** (cycle 127 s) | exact order; through greens ≥ walk 7 s + measured FDW | 34.5 | 38.1 | 39.2 | 40.6 | 39.5 | **39.0** |
| Webster, GDOT dual ring, no ped minimums (cycle 91 s) | exact order | 28.8 | 32.4 | 34.3 | 33.1 | 33.5 | 33.1 |
| Webster, simplified 4-stage (cycle 119 s) | `stages.py`: both rings switch together, uniform 4+3 s clearance | 35.0 | 38.8 | 39.9 | 41.6 | 38.9 | 39.3 |
| RL | — | no valid result (see below) | | | | | |

**Like-for-like comparison: real timing (51.2–51.5) vs Webster on GDOT's dual ring with pedestrian
minimums (39.0).** Real timing is worse in every period except night (32.3 vs 34.5), with the largest gap
in the PM (69.7 vs 40.6).

Not valid as comparators:
- **Webster dual ring without ped minimums (33.1):** its greens (P2 15.0 s, P6 9.3 s) are shorter than the
  crosswalk's flashing-don't-walk alone (22.0 / 25.2 s). GDOT's real splits already contain the
  pedestrian-timed greens (P4/P8 green = walk + FDW), so comparing against a ped-free Webster is unfair to GDOT.
- **Webster 4-stage (39.3):** simplified phase structure (not GDOT's); costs ~6 s/veh vs the same Webster on
  the dual ring (39.3 vs 33.1). Kept for the record only. An earlier version of this section compared real
  timing only against this row and claimed "the gap falls to 11.9 s/veh" and "at night real timing beats
  Webster" — both withdrawn.
- Real timing actuated vs fixed exact order differ by 0.3 s/veh: the P1 order workaround doesn't matter.

**RL:** no valid result. Trial 1 (3 seeds, 4-stage model, demand ×U(0.5,1.6)) failed: selected seed
145.6 s/veh, degenerate (holds Peachtree at max, skips Piedmont at 3 s; night Piedmont-from-N waits
490 s/veh). Trial 2 (6 seeds, ×U(0.5,1.3)) and a quick 1.0× run were stopped by the student's decision to
move the RL to GDOT's dual ring — **EXP-008**. All EXP-007 RL work used the simplified 4-stage model.

### Caveats on all rows (single trial: one Poisson draw, SUMO seed 9999)
- **Demand = GDOT's counted volumes**, treated as arrivals. They are detector counts (most likely stop-bar
  departures); in the PM, when Piedmont fails ≥ half its cycles (§5), counts are capped near what real timing
  served. Direction of this bias across controllers is unclear. Right turns uncounted (zero demand).
- **Poisson arrivals**: no platoons, which under-credits GDOT's coordination (P2 platoon ratio 1.52, §5).
- **Real-timing vehicle extension (1.0 / 8.0 s) was fitted on Oct 2's recorded greens — the test day.**
- Clearances from one 5-min window (Sep 29 09:50); medians over all 690 recorded rows differ by ≤ 0.6 s per
  interval (P1 4.0/3.4 vs 4.5/2.8 used), per-phase totals within ~0.5 s.
- Right-on-red: links 5/9/15 are `r` in the actuated real run and `s` in the fixed and dual-ring Webster runs;
  no numeric effect (zero right-turn demand) but inconsistent.
- Validation day Sep 30 has a detector outage 20:05–23:55 (47 bins of zero demand), so its "whole day"
  omits most of the evening.
- Differences under ~1 s/veh (51.2 vs 51.5, 39.0 vs 39.3) are within single-run noise.

## 4. Separate finding: real-timing controller vs GDOT's Timing & Actuation record (16:00–16:10)

User-downloaded charts in `data-timing/7065/` (Oct 2 16:00–16:10, plan C, not a calibration window)
compared with the v6 simulation in the same window:

- Cycle 180 s, greens of P1, P2, P7, P8 and clearances match (±0.6 s chart resolution).
- **Phase order wrong in the simulation:** GDOT runs P1 *after* P2 (P2 and P5 start together),
  confirmed in all 12 informative recorded windows (May 8, Sep 29, Oct 2; plans A–E). `timing/clearance.json` says "P1 leads"
  because its source window began mid-P1. Not yet fixed.
- P5 shorter in the simulation (19–35 s vs 34–35 s real); P6 longer (65–78 vs 60–62 s).
- P3 is on max recall in the simulation but gapped out once in reality (time passed to P4).
- P4/P8 greens equal pedestrian Walk + Flashing Don't Walk exactly (e.g. P8 17.6 + 30.5 = 48.1 s vs
  48.0 s green): those phases are pedestrian-timed. Peds walk every cycle on all four through phases.
  Neither Webster plan meets those pedestrian minimums (Peachtree through 18.0 s green vs ~29–32 s needed).

These affect only the real-timing controller and the pedestrian attribution; they are queued for after
this trial.

## 5. Purdue charts, Oct 2 16:00 (plan 39 = C) — `intersections/7065/timing/purdue_2026-10-02_1600/`

**Split failures (16:00–16:11, 4 cycles):** Peachtree phases P1, P2, P6: 0 failures (P6 green occupancy only
~32%: unused green); P5 (Peachtree left): 1/3. **Piedmont phases fail half or more of the cycles:**
P3 2/4, P4 through 3/4, P7 2/4, P8 through 2/4, permissive lefts in P4/P8 1/4 and 2/4. The real intersection
under plan C is oversaturated on Piedmont while Peachtree has spare green — the same pattern as the twin
(Piedmont through ≈ v/c 1, ~100 s/veh in the PM). So the twin's PM congestion is not a twin artifact; GDOT's
plan C favours Peachtree (the coordinated street) at Piedmont's expense — a coordination priority.

**Coordination diagrams (16:00–18:11):** P2 Peachtree SB (advance detector 260 ft): arrivals on green 67%
vs green time 44%, **platoon ratio 1.52** — real progression from the upstream signal. The twin's Poisson
arrivals give ≈1.0, so it under-credits GDOT's coordinated green on this movement (HCM progression factor
≈ (1−0.67)/(1−0.44) ≈ 0.6 on uniform delay). P4 Piedmont WB: platoon ratio 1.05 (random, as modelled).
P6/P8 (and P4) detector volumes don't match the turning-movement counts (P8 ~50–90 veh/h vs 980 counted;
P6 ~50 vs 254; P4 ~650–780 vs 385; detector distance blank on P4/P8), so their ratios are not used.

**Phase termination:** pedestrian activity every cycle on P2, P4, P6, P8.

Queued: the same green/red occupancy ratios measured in the simulation for 16:00–16:11 (outcome
validation); a platooned-arrival variant for Peachtree SB to size the coordination effect.
