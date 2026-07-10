# atspm-digitizer

Digitizes GDOT ATSPM chart images (the portal offers no numerical export). Two
chart types are supported:

- **`process`** — **Approach Volume** charts → per-direction, **15-minute**
  volume CSVs (see below).
- **`tmc`** — **Turning Movement Count** charts → per-movement **5-minute**
  TOTAL volume CSVs (see "TMC mode" near the end).

## Approach Volume mode (`process`)

Everything is derived from the image itself: the plot box is detected from the
axis frame, the y-scale is read from the tick labels (bundled digit-template
matching — the y-axis maximum differs per chart), and the date / approach pair /
sensor come from the filename (`MMDD_<pair>_<sensor>.jpg`). The companion
`MMDD.md` tables are parsed for **validation only**: extracted totals are
compared against them, never rescaled to match.

## Usage

```sh
# one image
uv run atspm-digitizer process --image ../data/7065/0506_nbsb_matrix.jpg --plot

# all four charts of one day (the intended testing path)
uv run atspm-digitizer process --date 0506 --data-dir ../data/7065 --plot

# full batch over every day in the data dir (opt-in)
uv run atspm-digitizer process --all --data-dir ../data/7065

# parse/validate inputs without extracting
uv run atspm-digitizer process --date 0506 --data-dir ../data/7065 --dry-run
```

Flags: `--plot` writes QA overlay images of the extracted traces;
`--dry-run` reports what would be processed; `--interpolate` opt-in (see below).

New intersection: drop its images + `.md` files into `data/<code>/`, run one
date to check, then `--all`. No code changes or per-image config needed.

## Outputs

All outputs go to `result/<code>/` at the repo root (`<code>` = data dir name):

```
result/<code>/
├── MMDD_<pair>_<sensor>.csv                       # time_15min, direction, sensor, vph_raw
├── qa/MMDD_<pair>_<sensor>_overlay.png            # --plot only
├── validation/MMDD_<pair>_<sensor>_validation.txt # also printed to stdout
└── consolidated.csv                               # --all only (adds a date column)
```

`vph_raw` is the mean vehicles-per-hour within each 15-minute bin, **raw** from
the chart — no rescaling, smoothing, or gap-filling. Daily total = Σ(vph × 0.25).
Empty cells are bins where the line left no recoverable pixels: a true sensor
gap (e.g. the overnight 00:00–04:00 dropout) **or** a stretch where one approach
is drawn underneath the other and the black combined line. Both are kept as gaps
so the output stays 1-to-1 with the plotted line; consequently a chart whose
weaker line is occluded through its own peak (e.g. NB on a tall matrix chart)
will integrate well below the `.md` total, and that under-count is reported
honestly rather than papered over.

`--interpolate` (opt-in, never on by default) linearly bridges **interior** NaN
runs of at most 3 bins (45 min); longer gaps and leading/trailing gaps are left
as NaN. Filled bins are counted in the validation report. Use it only when you
want a continuous series for downstream modeling and accept the synthesized
points; the default output remains the faithful raw reading.

## How extraction works (pipeline modules)

| module | role |
|---|---|
| `naming.py` | filename convention, input discovery |
| `plotbox.py` | axis-frame detection; x: box width ↦ 0–1440 min |
| `yaxis.py` | tick-label digit recognition → robust linear fit row ↦ vph |
| `extract.py` | per-color line extraction (see below), 15-min binning |
| `mdtables.py` | ground-truth table parsing from `MMDD.md` |
| `validate.py` | extracted-vs-truth totals & peak-hour report |
| `output.py` | result tree, CSVs, QA overlays |

Line extraction handles the chart's hazards:

- **Dashed D-factor lines share the solid lines' hues.** Two guards: (1) drop
  only the tiny isolated components — a dash is a ~5 px speck, while a solid-line
  fragment (even one chopped short at a crossing) is a little longer/chunkier, so
  the size cutoff is set just above the dash size; setting it higher erases the
  fragmented line itself and opens whole-day gaps. (2) The tracker may cold-
  (re)acquire only on a wide "anchor" component and refuses a non-physical
  vertical jump (`_MAX_JUMP_PX`), so it follows the solid line through fragmented
  stretches without ever locking onto the dashes.
- **Lines occlude each other.** Tracing runs bidirectionally with per-column
  continuity so a line obscured from one side is still picked up from the other.
  Where a line is *completely* hidden (no pixels at all — drawn under the other
  approach and/or the black combined line), those columns have no sample and the
  bin stays NaN. The hidden values are **not** invented from the other line.
- **The black combined line** never enters the masks (saturation threshold).

Observed accuracy on SIG#7065 recommended sources (NS→matrix, EW→advance-stopbar):
daily totals within ±8% of the `.md` ground truth, most within ±3%, peak hours
within one 15-min bin. Every residual error is a slight *under*-count from gaps
left at line crossings / occlusion — there is no positive overshoot, i.e. no
dashed-line contamination. Where a sensor is genuinely off (e.g. 0502's
~04:00–10:00 outage) the gap is preserved, lowering that day's total honestly.

## Digit templates

`src/atspm_digitizer/digits/` holds tiny glyph templates for the two font
sizes the portal renders tick labels in. If a future chart style fails y-axis
calibration, regenerate with:

```sh
uv run python scripts/make_digit_templates.py <chart.jpg> <top_label_value> <label_step> [...]
```

passing one chart per font size whose label values you can read yourself.

## TMC mode (`tmc`) — Turning Movement Counts, 5-minute totals

TMC charts plot one movement's per-lane counts plus a black **Total** line, at
5-minute resolution, with the day's summary printed in the header. We extract
**only the movement total** (per-lane lines tangle at 5-min and their
lane-utilisation `fLU` is printed anyway), into 288-bin 5-minute CSVs.

```sh
uv run atspm-digitizer tmc --image ../tmc/7065/0511-eb-thru.jpg --plot
uv run atspm-digitizer tmc --date 0511 --data-dir ../tmc/7065 --plot
uv run atspm-digitizer tmc --all       --data-dir ../tmc/7065          # opt-in batch
uv run atspm-digitizer tmc --date 0511 --data-dir ../tmc/7065 --dry-run
```

- **Inputs:** `tmc/<code>/MMDD-<approach>-<movement>.jpg`
  (approach ∈ nb|sb|eb|wb, movement ∈ thru|left|right). Intersection- and
  date-agnostic; drop new days in and rerun.
- **Outputs** (rooted at the input dir's parent):
  `tmc/result/<code>/MMDD-<appr>-<mvmt>.csv` — columns `time_5min, approach,
  movement, total_vph` (raw, NaN kept for gaps); `qa/…_overlay.png` with
  `--plot`; `validation/…_validation.txt`; `consolidated.csv` with `--all`.
- **Which line is the total:** multi-lane charts → the black Total line;
  single-lane charts (no Total line, `fLU = 1`) → the sole coloured line.
- **Validation via OCR:** there is no companion `.md`. The header (`Total
  Volume`, `Peak Hour`, `PHF`, `fLU`) is read with OCR (`rapidocr-onnxruntime`,
  pip-only, offline) purely to cross-check — the extracted daily total is
  compared to the printed one; the OCR never alters output.

How the total line is traced (gridlines are as dark as the line, so they can't
be separated by brightness):

- Horizontal gridlines are removed as long horizontal pixel runs (the curve is
  never horizontal for long).
- Vertical gridlines are handled by the tracer, which walks the line by
  continuity — in each column it takes the dark pixel nearest the previous
  height, so a vertical gridline (which passes through that height) is harmless
  and steep 5-min spikes are preserved.

Observed accuracy on 0511 (extracted daily total vs OCR-printed total): the
through movements and most lefts land within ~±6%; low-volume left movements can
run a bit higher (one at +12.5%). The validation report flags any chart whose
extracted total diverges from the printed one, so outliers are easy to spot.
