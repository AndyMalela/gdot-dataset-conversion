# GDOT ATSPM Approach Volume — Digitization

## Goal

Extract per-direction, 15-minute vehicle volume time series from GDOT ATSPM
"Approach Volume" chart images (the portal provides no numerical export) for
intersection SIG#7065 (SR 141 @ SR 237), used in reinforcement-learning
traffic-signal-control research.

The end product per day is a tidy CSV of 15-minute volumes for the four
approaches (NB, SB, EB, WB).

**Fidelity is the priority: the output must be as 1-to-1 to the original plot
as possible.** Extract the raw values the lines actually show. Do NOT rescale,
smooth, or otherwise warp the numbers to match any external figure. The
companion `.md` tables are used ONLY as a printed validation check after
extraction — never as a calibration input.

---

## Folder structure

```
GDOT/
├── CLAUDE.md (this file)
├── data/
│   └── 7065/ (intersection code)
│       ├── MMDD.md, MMDD_*.jpg (daily volume data)
│       └── ...
└── atspm_digitizer/ (pipeline: extracts 15-min volume time series from images)
```

---

## Folder contents & filename convention

Files are named `MMDD_<pair>_<sensor>.jpg` plus one `MMDD.md` per day.

- `MMDD` — month/day in 2026 (e.g. `0506` = May 6).
- `<pair>` — the approach pair shown in the chart:
  - `nbsb` = Northbound + Southbound approaches
  - `ebwb` = Eastbound + Westbound approaches
- `<sensor>` — the detector the chart is sourced from:
  - `advance-260ft` — Wavetronix Advance radar, 260 ft upstream of the stop bar
  - `advance-stopbar` — Wavetronix Advance radar at the stop bar
  - `matrix` — Wavetronix Matrix radar at the stop bar

So each day has **4 chart images** (nbsb × {advance, matrix}, ebwb × {advance,
matrix}) and **1 `.md`** file containing the four corresponding summary-metric
tables.

`ped_MMDD.jpg` is a Pedestrian Delay chart (different chart type — NOT a volume
chart, see "Out of scope" below).

Days currently present: 0502–0508 and 0513.

---

## What the volume chart looks like

Every Approach Volume chart is a 24-hour line plot with this fixed structure:

- **X-axis:** time of day, 00:00 → 00:00 (1440 minutes), hourly tick labels on
  BOTH the top and bottom axis.
- **Left Y-axis:** Volume (Vehicles Per Hour). Gridlines at regular intervals.
  **The Y-axis maximum DIFFERS PER IMAGE** — observed values include 1200,
  2400, 4000, 10000. Do NOT hardcode the Y scale; detect it from the axis tick
  labels in the image.
- **Right Y-axis:** Directional Split (0–1). Only relevant to the dashed
  D-factor lines, which we discard.

### Lines in the plot (which to keep, which to drop)

| Line | Color | Style | Use it? |
|---|---|---|---|
| First approach (NB or EB) | blue | solid | **KEEP** |
| Second approach (SB or WB) | red | solid | **KEEP** |
| Combined volume | black | solid | drop (it's just NB+SB / EB+WB) |
| First approach D-factor | blue | dashed | **DROP** |
| Second approach D-factor | red | dashed | **DROP** |

Critical extraction hazard: the dashed D-factor lines share the SAME hue as the
solid data lines. They must be separated by **dash pattern, not color** — the
solid line is a continuous vertical run per column; the dashed line is short
broken segments. Require a minimum contiguous vertical run length (~≥4px) to
keep a pixel. The dashed lines often sit high on the plot (0.4–0.9 split maps
into the upper volume region), so failing to filter them injects large spurious
values, especially overnight where real volume is low.

---

## Companion `.md` tables (validation reference ONLY)

Each `MMDD.md` has four tables, one per chart image, each headed with the
sensor description and the plot filename. **These are NOT inputs to extraction
and must never be used to rescale or adjust extracted values.** Their only role
is a post-extraction sanity check that the script prints for the user to read.
Useful fields:

- `Total Volume` — full-day total (per direction and combined). Compare against
  the integrated extracted series and report the % difference.
- `Peak Hour` + `Peak Hour Volume` — cross-check peak timing/height.
- `Peak Hour Factor (PHF)` — within-peak-hour peakiness.
- `K Factor` — peak-hour volume / daily total (≈0.06–0.10 here).
- `D Factor` — directional split at the peak; used by the human to confirm
  which table maps to which image (match the table's NB/SB or EB/WB split to the
  visible dominance in the chart).

These tables are typed text — parse them directly (regex / markdown table
parse). Do NOT digitize them from images.

---

## CRITICAL: sensor reliability — which source to trust

Not all sensors are usable. Established from cross-checking three days
(May 6, 7, 13):

- **NS approach → USE `matrix` (stop bar). DISCARD `advance-260ft`.**
  The NS `advance-260ft` unit reports daily totals ~10–12× LOWER than the
  Matrix at the same intersection (e.g. May 6: 6,777 vs 83,460). This is not a
  real traffic difference — it is consistent with the advance unit covering only
  a partial set of lanes / a misconfigured detection zone. It is internally
  self-consistent (its own peak/K math checks out), so it LOOKS clean but is
  undercounting badly. The Matrix daily total (~75k–83k NS) is the physically
  correct figure for this arterial (peak ~7–8k vph, K≈0.09–0.10 → ~10× daily).

- **EW approach → USE `advance-stopbar`.** Here Advance and Matrix are both at
  the stop bar and agree within ~30% (e.g. May 6: 19,802 vs 30,402). Use
  Advance as the EW source.

- There is **NO universal Advance-vs-Matrix multiplier.** The discrepancy is
  specific to the NS advance-260ft unit. Decide per approach as above.

---

## Extraction algorithm (target behavior for the script)

Environment: Python, uv project, `opencv-python` + `numpy` + `pandas`.

1. **Locate plot box** by detecting the black axis frame (longest horizontal /
   vertical line segments).
2. **Calibrate pixel → data:** x maps 0→1440 min across box width; y maps
   0→`y_max` across box height (origin bottom-left). Detect `y_max` from the
   axis tick labels in the image.
3. **Per solid data line (blue, red):** build an HSV mask for that hue
   (blue ≈ hue 110–125, red ≈ hue 0–8 / 170–180). Remove dashed pixels by
   requiring contiguous vertical run length ≥ ~4px. Exclude the black combined
   line via low-saturation / low-value filtering.
4. **Per x-column:** take the vertical centroid of surviving masked pixels →
   one (time, vph) sample. Columns with no pixels (line occluded at crossings,
   or a true gap in the plot) → NaN.
5. **Bin to 15-min:** aggregate column samples into 96 bins. **Leave NaN bins
   as NaN by default** — a gap in the plot is preserved as a gap in the output,
   to stay 1-to-1 with the image. (Interpolation may be offered behind an
   explicit opt-in flag, but must never be on by default.)
6. **Validate (no rescaling):** integrate each direction's extracted series to
   a daily total and PRINT it next to the `.md` total with the % difference, for
   the user to inspect. Do NOT apply any scale factor. Output stays raw.

### Outputs

- One tidy CSV per processed image:
  `time_15min, direction, sensor, vph_raw`
  (raw extracted values only — no rescaled/calibrated column).
- `--plot` flag: overlay extracted points on the source image for visual QA.
- Validation report (extracted vs `.md` totals, with % difference) printed for
  the user. The `.md` is read only for this comparison, never to alter output.

---

## Data-quality notes already established

- **Sensor gaps:** brief blank periods (e.g. ~1 hr at 23:00, or 00:00–04:00)
  are normal ATSPM comm dropouts / overnight controller resets. They fall in the
  low-volume overnight trough. For 1-to-1 fidelity the extractor preserves these
  as NaN rather than inventing values; what to do with them is a later decision,
  not the digitizer's job. Not a reason to discard a day.
- **5-min vs 15-min charts:** only digitize 15-min-resolution charts. The
  5-min charts are too noisy/overlapping to digitize reliably.

---

## Out of scope for the volume script

- `ped_MMDD.jpg` (Pedestrian Delay charts) — a DIFFERENT chart type (cycle
  length, ped delay per request, % delay by cycle length). Not part of the
  volume extraction. Useful separately for thesis context (real signal cycle
  lengths per time-of-day plan, ped phase min-green as a hard CMDP constraint),
  but do not feed it to the volume digitizer.