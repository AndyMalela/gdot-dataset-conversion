"""Solid-line extraction from the chart plot area.

Each chart has five lines: solid blue and solid red (the two approach
volumes — what we want), a solid black combined line, and dashed blue
and red D-factor lines. The black line drops out via the saturation
threshold of the HSV masks. Separating a solid data line from the
dashed D-factor line of the same hue is the central hazard.

Two defences separate the solid line from the same-hue dashed one:

1. Connected-component size. A D-factor dash is a short isolated speck
   (~5 px); the solid line, even where it fragments at crossings with
   the other line and the black gridlines, leaves pieces a little
   longer (>=6 px) or chunkier. Dropping only the truly tiny components
   (``_CC_MIN_WIDTH`` / ``_CC_MIN_AREA``) removes dashes while keeping
   those fragments — the earlier, far higher thresholds erased the real
   line and produced whole-day gaps on heavily-weaving charts.
2. Continuity tracking. A per-column tracker walks the kept mask,
   choosing the pixel run nearest its current position and refusing a
   non-physical vertical jump (``_MAX_JUMP_PX``), so it follows the
   solid line through the fragmented stretches without stepping onto a
   far-off feature. Cold (re)acquisition — where there is no recent
   position — is gated to wide "anchor" components so a cold start can
   never land on the dashed line.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from .plotbox import DAY_MINUTES, PlotBox
from .yaxis import YAxis

N_BINS = 96
BIN_MINUTES = DAY_MINUTES // N_BINS

# HSV hue ranges (OpenCV: H 0-179)
_HUE = {
    "blue": [(100, 130)],
    "red": [(0, 8), (170, 179)],
}
_SAT_MIN = 60
_VAL_MIN = 60

# Dash rejection by component size. A D-factor dash is a short isolated
# speck (~5 px, small area); a fragment of the solid line is at least a
# little longer or chunkier. These thresholds sit just above the dash
# size so dashes are dropped while real line fragments survive — keep
# them low: higher values delete the fragmented line itself.
_CC_MIN_WIDTH = 6
_CC_MIN_AREA = 30
# Anchor width: a component at least this wide is a trusted piece of the
# solid line — the tracker may COLD-(re)acquire only on these. Dashes
# never reach this width, so a cold start can never land on the dashed
# D-factor line. Once tracking, the kept mask is followed by continuity.
_CC_ANCHOR_WIDTH = 50

# Continuity tracking: forget the last traced y after this many empty
# columns (the line may resume anywhere after a sensor gap).
_TRACK_RESET_COLS = 30
# Max vertical move (px) the tracked line may make between adjacent
# columns. A drawn volume polyline spans ~10 px horizontally per 15-min
# point, so even a near-vertical real segment stays well under this; a
# larger jump means the only surviving pixels are a far-off feature
# (e.g. a leftover dashed D-factor segment), so the column is left empty
# rather than snapped onto it.
_MAX_JUMP_PX = 40
# Optional interpolation (opt-in only): largest interior NaN run, in
# 15-min bins, that --interpolate will bridge linearly.
_MAX_GAP_BINS = 3


@dataclass
class ExtractedSeries:
    direction: str
    color: str
    vph: np.ndarray  # 96 bin means, NaN where no data
    trace_cols: np.ndarray  # per-column pixel trace (for QA overlay)
    trace_rows: np.ndarray
    coverage: float  # fraction of columns with a traced sample
    interpolated_bins: int = 0  # bins synthesized by --interpolate (0 if raw)

    @property
    def daily_total(self) -> float:
        """Vehicles/day implied by the binned series (NaN bins excluded)."""
        return float(np.nansum(self.vph) * (BIN_MINUTES / 60.0))


def _color_mask(hsv: np.ndarray, color: str) -> np.ndarray:
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    mask = np.zeros(h.shape, bool)
    for lo, hi in _HUE[color]:
        mask |= (h >= lo) & (h <= hi)
    return (mask & (s >= _SAT_MIN) & (v >= _VAL_MIN)).astype(np.uint8)


def _drop_dashes(mask: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Drop tiny dash specks; return (kept mask, anchor mask).

    A component is kept if it is wide or chunky enough to be a solid-line
    fragment rather than a dash; anchor pixels belong to wide components
    on which the tracker may cold-(re)acquire the line.
    """
    n, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    keep = np.zeros(n, bool)
    anchor = np.zeros(n, bool)
    for i in range(1, n):
        w, area = stats[i, cv2.CC_STAT_WIDTH], stats[i, cv2.CC_STAT_AREA]
        keep[i] = w >= _CC_MIN_WIDTH or area >= _CC_MIN_AREA
        anchor[i] = w >= _CC_ANCHOR_WIDTH
    return keep[labels].astype(np.uint8), anchor[labels]


def _runs(col: np.ndarray) -> list[tuple[int, int]]:
    """(start, end) of each run of True values; end exclusive."""
    idx = np.flatnonzero(col)
    if len(idx) == 0:
        return []
    breaks = np.flatnonzero(np.diff(idx) > 1)
    starts = np.concatenate([[0], breaks + 1])
    ends = np.concatenate([breaks + 1, [len(idx)]])
    return [(int(idx[s]), int(idx[e - 1]) + 1) for s, e in zip(starts, ends)]


def _trace_pass(
    mask: np.ndarray, anchor: np.ndarray, box: PlotBox, xs: range
) -> dict[int, float]:
    """One directional tracking pass: column -> traced y.

    Where a column has several pixel runs (a dash fragment merged into
    the solid component at a crossing), the run nearest the previously
    traced y wins. Without recent context — at the start or after a
    long gap — the line is only (re)acquired on an anchor run (a pixel
    of a wide component), so the tracker can never lock onto leftover
    D-factor dashes.
    """
    traced: dict[int, float] = {}
    last_y: float | None = None
    cols_since_hit = 0
    view = slice(box.top + 2, box.bottom - 1)
    for x in xs:
        runs = _runs(mask[view, x])
        if last_y is None:
            runs = [(s, e) for s, e in runs if anchor[view, x][s:e].any()]
        centroids = [box.top + 2 + (s + e - 1) / 2.0 for s, e in runs]
        if last_y is None:
            y = centroids[int(np.argmax([e - s for s, e in runs]))] if runs else None
        elif centroids:
            nearest = centroids[int(np.argmin([abs(c - last_y) for c in centroids]))]
            # Reject a non-physical jump: the solid line is absent here
            # and only a far-off feature survives — leave the column empty.
            y = nearest if abs(nearest - last_y) <= _MAX_JUMP_PX else None
        else:
            y = None
        if y is None:
            cols_since_hit += 1
            if cols_since_hit > _TRACK_RESET_COLS:
                last_y = None
            continue
        traced[x] = y
        last_y = y
        cols_since_hit = 0
    return traced


def _trace_line(
    mask: np.ndarray, anchor: np.ndarray, box: PlotBox
) -> tuple[np.ndarray, np.ndarray]:
    """Bidirectional trace of the line, merged per column.

    A single forward pass cannot acquire the line in regions where
    crossings chop it below the anchor width (e.g. the two approaches
    weaving around each other overnight); the pass coming from the
    other side arrives with tracking context and follows it through.
    Columns where the passes disagree are dropped as ambiguous.
    """
    fwd = _trace_pass(mask, anchor, box, range(box.left + 2, box.right - 1))
    bwd = _trace_pass(mask, anchor, box, range(box.right - 2, box.left + 1, -1))
    cols, rows = [], []
    for x in sorted(fwd.keys() | bwd.keys()):
        ys = [d[x] for d in (fwd, bwd) if x in d]
        if len(ys) == 2 and abs(ys[0] - ys[1]) > 3.0:
            continue
        cols.append(x)
        rows.append(float(np.mean(ys)))
    return np.array(cols, dtype=float), np.array(rows, dtype=float)


def _bin_15min(minutes: np.ndarray, vph: np.ndarray) -> np.ndarray:
    """Aggregate (minute, vph) samples into 96 bin means."""
    out = np.full(N_BINS, np.nan)
    if len(minutes) == 0:
        return out
    bins = np.clip((minutes // BIN_MINUTES).astype(int), 0, N_BINS - 1)
    for b in range(N_BINS):
        sel = bins == b
        if sel.any():
            out[b] = float(vph[sel].mean())
    return out


def _interpolate_gaps(vph: np.ndarray, max_gap: int = _MAX_GAP_BINS) -> int:
    """Linearly interpolate interior NaN runs of at most max_gap bins.

    Opt-in only (--interpolate). Mutates vph in place; returns the number
    of bins filled. Leading/trailing NaN runs are left as gaps — there is
    no second endpoint to interpolate against, and inventing edge values
    would not be 1-to-1 with the plot.
    """
    isnan = np.isnan(vph)
    if isnan.all() or not isnan.any():
        return 0
    valid = np.flatnonzero(~isnan)
    filled = 0
    for left, right in zip(valid[:-1], valid[1:]):
        gap = right - left - 1
        if 0 < gap <= max_gap:
            vph[left + 1 : right] = np.interp(
                np.arange(left + 1, right), [left, right], [vph[left], vph[right]]
            )
            filled += gap
    return filled


def extract_series(
    bgr: np.ndarray,
    box: PlotBox,
    yaxis: YAxis,
    directions: tuple[str, str],
    interpolate: bool = False,
) -> list[ExtractedSeries]:
    """Extract both approach-volume lines (blue, red) from a chart.

    By default the output is raw: each 15-min bin is the mean of the
    pixel samples actually traced on that line, and bins with no traced
    pixels stay NaN — a gap in the plot is preserved as a gap, 1-to-1
    with the image. Pass interpolate=True to linearly bridge short
    interior gaps (see _interpolate_gaps); this is never on by default.
    """
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    out = []
    for color, direction in zip(("blue", "red"), directions):
        mask, anchor = _drop_dashes(_color_mask(hsv, color))
        cols, rows = _trace_line(mask, anchor, box)
        minutes = box.col_to_minute(cols) if len(cols) else cols
        vph = np.maximum(yaxis.row_to_vph(rows), 0.0) if len(rows) else rows
        binned = _bin_15min(minutes, vph)
        series = ExtractedSeries(
            direction=direction,
            color=color,
            vph=binned,
            trace_cols=cols,
            trace_rows=rows,
            coverage=len(cols) / max(box.width - 3, 1),
        )
        if interpolate:
            series.interpolated_bins = _interpolate_gaps(series.vph)
        out.append(series)
    return out
