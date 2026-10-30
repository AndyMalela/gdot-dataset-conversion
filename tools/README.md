# tools

All scripts. Data goes to `intersections/<id>/` (one folder per signal, layout in `paths.py`):

| Folder | Written by |
|---|---|
| `intersections/<id>/counts/` | `atspm_tmc.py` — turning-movement counts |
| `intersections/<id>/timing/` | `atspm_plans.py` (timing plans), `atspm_timing.py` (Timing & Actuation windows) |
| `intersections/<id>/config/` | `atspm_config.py` — detector configuration (hardware, type, lane, distance from stop bar) and approaches, from the public SignalDetail page |
| `intersections/<id>/network/` | `osm_build.py` — SUMO network from OpenStreetMap |
| `intersections/<id>/sim/` | `build_sim.py` — SUMO simulation (counts + timing) |
| `intersections/README.md` | `check_complete.py` — status table of every signal checked |
| `tools/cache/` | screening downloads, not curated |

Checking a new signal:
```bash
python3 tools/atspm_tmc.py <id> --start 2026-09-26 --end 2026-10-02   # counts
python3 tools/check_complete.py                                       # complete / incomplete
python3 tools/atspm_plans.py <id> --date 2026-10-02                   # timing plans
python3 tools/atspm_config.py <id>                                     # detector configuration
python3 tools/osm_build.py <id>                                       # SUMO network
```
Decisions (accepted / on hold / skipped) go in `intersections/signal_overrides.csv`.


## atspm_tmc.py — turning movement counts from GDOT ATSPM

```bash
python3 tools/atspm_tmc.py 7065                            # yesterday
python3 tools/atspm_tmc.py 7065 183 --days 30 --weekdays   # last 30 days, Mon–Fri
python3 tools/atspm_tmc.py 7065 --start 2026-09-01 --end 2026-09-30
python3 tools/atspm_tmc.py --help                          # all options
```

No dependencies beyond Python 3. Re-running is safe: cached days are skipped, failed days are retried.

Output in `intersections/<signal>/counts/`:

| File | Contents |
|---|---|
| `info.txt` | intersection name, movements, date range, complete/partial day counts |
| `tmc_<signal>_5min.csv` | one row per bin: `date, weekday, time, EB_L, EB_T, …, total, status` |
| `daily_summary.csv` | one row per day: volume, valid bins, outage % |
| `raw/` | gzipped server responses (~8 KB/day) |

`intersections/README.md` (from `check_complete.py`) is the status table of every signal checked: complete / accepted / on hold / incomplete, with reasons.

Some signals report extra sections besides vehicle turning movements: `EXIT_*` columns are exit-lane detector counts and `LRT_*` is light rail. They're kept, prefixed, and must not be used as turning movements. Signals whose every day is all zeros have detectors configured but log nothing (seen at 44, 228, 233, 362, 7820 on every date tried).

`status=outage` = a run of ≥3 all-zero bins (controller not logging). Those counts are left blank — don't treat them as zero traffic. Right-turn columns appear only where right-turn lanes are detected.

Be polite to the server: requests run one at a time with a 5 s pause (~25 s per intersection-day, so 90 days ≈ 40 min per intersection).

## atspm_signals/ — signal list and screening for sampling

```bash
python3 tools/atspm_signals/atspm_signals.py                         # all 8,983 signals -> signals_all.csv
python3 tools/atspm_signals/atspm_signals.py --area atlanta --names  # TMC-capable Atlanta signals + names -> signals_atlanta.csv
python3 tools/atspm_signals/screen.py signals_atlanta.csv --days 2   # pull 2 recent Tue–Thu per signal -> screening_atlanta.csv
python3 tools/atspm_signals/screen.py signals_atlanta.csv --limit 5  # quick test
```

- `signals_<label>.csv`: `signal_id, name, lat, lon, region, has_tmc, metrics` — parsed from the ATSPM map's `AddData.js`. `--area atlanta` is a rough bounding box, not city limits. `--bbox S W N E --label x` for any other area.
- `screening_<label>.csv`: one row per signal — completeness, hourly and peak-hour volume, left share, major-axis share, approaches/movements detected, shared lanes. Use it to filter (e.g. 4 approaches, ≥90% daytime coverage) and stratify.
- Screening downloads go into `intersections/<signal>/counts/raw/`, so `atspm_tmc.py` reuses them.
- `has_tmc=1` only means TMC is configured. Many signals detect only some movements (e.g. one left turn) — check `n_approaches` / `movements`.
- `TL` / `TR` = shared-lane detector: through and turn counted together.

### sample.py — reproducible stratified sample

```bash
python3 tools/atspm_signals/sample.py screening_atlanta.csv              # 4 per cell, seed 20261004
python3 tools/atspm_signals/sample.py screening_atlanta.csv --per-cell 5
```

- Eligible = data returned, ≥90% daytime coverage, ≥3 detected approaches.
- Cells = peak-hour volume tertile (low/med/high) × complexity (simple/standard/complex). Complexity is a proxy from detector layout (exclusive left-turn detectors per approach); a `complexity` column in the screening CSV overrides it.
- Within a cell: seeded shuffle, first N selected. To replace a failed site, add `signal_id,reason` to `rejections_<label>.csv` and re-run — the next site in that cell's order is taken.
- Outputs `sample_<label>.csv` (every eligible signal with cell, rank, selected, weight) and `sample_<label>_report.md` (eligibility, cell table, frame-vs-sample balance, selected list).

## Timing

## atspm_timing.py — signal timing from GDOT ATSPM Timing & Actuation charts

The portal only returns chart images, so the script requests short windows, downloads the charts and reads the coloured bars pixel by pixel. There is no OCR: each chart's phase is identified by template-matching its header, and the time axis comes from the requested window.

```bash
python3 tools/atspm_timing.py 7065 --date 2026-05-08                  # 24 windows: HH:00–HH:15 every hour
python3 tools/atspm_timing.py 7065 --date 2026-05-05 2026-05-06 --hours 6-21
python3 tools/atspm_timing.py 7065 --date 2026-05-08 --times 07:30 17:15
python3 tools/atspm_timing.py 7065 --date 2026-05-08 --times 14:00 --window 5   # clearance calibration
python3 tools/atspm_timing.py 7065 --rebuild                          # re-parse saved images only
```

Requires Pillow and numpy. Re-running is safe: windows that have already been downloaded are skipped.

**Cost:** about 50 s per window (30 s of server time plus 15 images), so 24 windows take about 20 min per intersection-day. Sample for time-of-day plans; don't pull whole days.

### Output in `intersections/<signal>/timing/`

| File | Contents |
|---|---|
| `info.txt` | intersection name, windows parsed, charts found |
| `tod_<signal>.csv` | **one row per window**: `cycle_s_est`, `ped_walks`, then for each phase/overlap `n`, `green_med`, `green_max`, `yellow`, `red_clear` (and `walks` where there is a ped row) |
| `greens_<signal>.csv` | one row per green: start, `green_s`, `min_green_s`, `yellow_s`, `red_clear_s`, `to_next_green_s` |
| `intervals_<signal>.csv` | every coloured interval: vehicle green/yellow/red_clear/red/no_data, ped walk/ped_clear/dont_walk |
| `raw/<date>_<HHMM>_<W>min/` | downloaded charts renamed `Phase_2.jpg`, `Overlap_4.jpg`, …; identical copies → `*_dup.jpg` |

Column keys: `P2` = Phase 2, `OL4` = Overlap 4. Pedestrian rows appear on overlap charts (ped overlaps).

### Accuracy

| Window | s per pixel | Use for |
|---|---|---|
| 15 min (default) | 0.86 | cycle length, splits, greens (±0.5 s), ped walks |
| 5 min | 0.29 | yellow / red clearance (fixed values, so calibrate once per signal) |

Boundaries are estimated to a fraction of a pixel from blended JPEG pixels. Still, 15-min windows read yellow about 0.2–0.4 s shorter than 5-min windows. Take clearances from one 5-min window.

- `truncated=1` means the interval touches the window edge. Those intervals are excluded from medians.
- `cycle_s_est` is the median green-to-green spacing across phases. In free or actuated operation (often at night) the cycle isn't fixed, so check the spread in `greens_<signal>.csv`.
- `min_green_s` is the dark-green "begin green" block (event 1 until event 3, min complete).

## atspm_plans.py — time-of-day timing plans (use this for a SUMO baseline)

```bash
python3 tools/atspm_plans.py 7065 --date 2026-09-29              # one day, + clearance window
python3 tools/atspm_plans.py 7065 44 337 --date 2026-09-29 2026-09-30
python3 tools/atspm_plans.py 7065 --rebuild                       # re-parse saved charts
```

One **Split Monitor** request per signal-day (~15–40 s) gives the whole day's plan bands and the controller's **programmed split** per phase; one 5-min Timing & Actuation window (~10–40 s) in the longest daytime plan gives yellow, red clearance and which phase of each pair leads. Much cheaper than sampling Timing & Actuation every hour.

Output in `intersections/<signal>/timing/`:

| File | Contents |
|---|---|
| `timing_plan_<signal>.md` | **read this**: schedule, plans (cycle + split per phase), checks, clearances, lead/lag |
| `timing_plan_<signal>.json` | same, machine-readable |
| `plans_<signal>.csv` | one row per plan band per date: raw read, rounded split, where each value came from |
| `split_monitor/<date>/Phase_<n>.jpg` | the charts (plan numbers are printed on them) |
| `clearance.json`, `raw/<date>_<HHMM>_5min/` | clearance window and its charts |

How to read it:
- Plan letters (A, B, …) group bands with the same splits. The controller's plan numbers are on the charts but not parsed (6-px font, no OCR).
- **Checks**: in each barrier group the two rings must sum to the same time; cycle = sum of the groups. `closes within 1 s` = pixel rounding (0.52 s/px). `barrier mismatch` / `unverified` = the split line was hidden under dots in that band; values are reported as read, never adjusted. Check the chart.
- **Actuated** = bands where no programmed-split line can be read: either Free mode or an uncoordinated actuated plan (the band label on the chart says which; e.g. 337 is "Free", 7130's nights are "Plan 1"/"Plan 7"). The table shows observed median phase times (`~`), not programmed values.
- Assumes NEMA dual ring (1–4 | 5–8). Phases above 8 (e.g. 10–16, often pedestrian/overlap phases) are listed but not checked.
- The portal's firewall rejects requests carrying empty `YAxisMin`/`Y2AxisMin` (which the website sends — why it hangs on "loading"); the script leaves them out.

Validated on 7065 against a hand-read of 05-06…05-08: all five plans identical to the second.

## SUMO network

## osm_build.py — SUMO network for an ATSPM signal, from OpenStreetMap

```bash
python3 tools/osm_build.py 7065
python3 tools/osm_build.py 7065 44 337 --radius 250
python3 tools/osm_build.py 7065 --rebuild      # reuse downloaded osm.xml
```

Needs SUMO (`netconvert`, `sumo`, `$SUMO_HOME/tools` for sumolib) and Pillow. Coordinates come from `tools/atspm_signals/signals_all.csv`; ATSPM count columns from `intersections/<signal>/counts/info.txt` (run `tools/atspm_tmc.py` first to get the movement map). OSM is downloaded from the public Overpass API (with a mirror and retries; it is often busy).

Output in `intersections/<signal>/network/`:

| File | Contents |
|---|---|
| `report.md` | **read this**: target junction, approaches (lanes, OSM tags, lane use), flags, movement map, smoke test |
| `preview.png` | drawing of the area; target approaches in blue, signals in red |
| `<signal>.net.xml` | the SUMO network |
| `<signal>.sumocfg`, `smoke.rou.xml` | smoke-test scenario (`sumo-gui -c <signal>.sumocfg` to look at it) |
| `movement_map.csv` | ATSPM column (`EB_L`, `NB_TR`, …) → SUMO `from_edge`, `to_edge` |
| `junction.json` | same summary, machine-readable |
| `osm.xml`, `netconvert.log` | raw download and netconvert warnings |

What it does:
1. netconvert with junction joining, signal guessing from OSM `traffic_signals` tags, passenger roads only (service roads dropped), cropped to the radius.
2. Target = signalised junction nearest the ATSPM location. If OSM has no signal tag there, the nearest real junction (≥3 approaches, ≤60 m) is signalised and this is flagged.
3. Approaches are labelled EB/WB/NB/SB by direction of travel (best one-to-one fit to the compass). Turns are classified by heading change, so a U-turn on a divided road isn't mistaken for a left.
4. Smoke test: 120 veh/h on every turning movement for 10 min under netconvert's guessed signal program; PASS = all inserted, none stuck, 0 teleports, 0 collisions.

**Flags to take seriously** (OSM is often wrong; it was for 7065's north leg):
- `no lanes tag … netconvert default` — the lane count is invented by netconvert. Check aerial imagery.
- `two-way way with lanes=N total` — the per-direction split is guessed.
- `ATSPM counts X but OSM has no …` / `OSM approach(es) … have no ATSPM counts` — the OSM layout and GDOT's detectors disagree (missing leg, wrong label, or no detector).
- `little queue space` — the network edge or next signal is close; queues can spill out of the model.

The signal program in the net is netconvert's guess, not the real timing. Real plans: `tools/atspm_plans.py`.

## Simulation

```bash
python3 tools/atspm_phasemap.py <id> --date 2026-10-02     # phase titles -> transcribe timing/phase_map.json
python3 tools/atspm_timing.py <id> --date 2026-10-02 --times 08:00 17:00   # recorded greens for validation
python3 tools/build_sim.py <id>                            # build, calibrate, validate, snapshot
python3 tools/make_overview.py                             # intersections/OVERVIEW.md + overview.png
```

`build_sim.py` writes `intersections/<id>/sim/`: measured 5-min demand (`demand.rou.xml`), the signal (`signal.add.xml`), `sim.sumocfg` (full day), `peak.sumocfg` (07:00–09:30 check), `gui.sumocfg` + `view.xml` (watch 07:45–09:00), `snapshot.png`, and `README.md` with every assumption and the validation table.

Signal (`--controller nema`, default) = SUMO NEMA actuated-coordinated dual ring, built from:
- GDOT's time-of-day plans (cycle, splits as force-offs, schedule) — Split Monitor
- measured yellow / red clearance, lead/lag, min greens — Timing & Actuation
- max greens in Free/actuated periods — Split Monitor max-out dots (else a 95th-percentile lower bound)
- max recall where a phase never gaps out (< 5% gap-outs, from the Split Monitor dot colours)
- which approach each phase controls — `timing/phase_map.json` (GDOT Split Failure chart titles)
- vehicle extension (not published) — chosen from 1–4 s to match the recorded greens

Validation: simulated vs recorded median green per phase in the 08:00 and 17:00 Timing & Actuation windows. `--controller fixed` gives the plain fixed-time version of the same plans.
