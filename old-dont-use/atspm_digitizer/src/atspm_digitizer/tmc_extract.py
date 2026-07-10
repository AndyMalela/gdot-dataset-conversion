"""Extract the per-movement TOTAL volume series from a TMC chart.

We digitize only the movement total, at 5-minute resolution (288 bins).
Which line is the total depends on lane count:

- Multi-lane charts draw a black "Total Volume" line (the sum of the
  per-lane lines). Single-lane charts (fLU == 1) have no black line —
  the sole red lane line IS the total.

Design decisions, each forced by a real failure seen on this data:

- **Colour by channel dominance, not HSV thresholds.** The red line's
  saturation varies wildly along its length; a fixed HSV cut dropped its
  faint stretches. ``R - max(G, B)`` (and, for the black line, darkness
  gated to near-neutral pixels) captures the whole line regardless of
  boldness.
- **Gridlines are exactly as dark as the black line**, so they cannot be
  told apart by brightness. They are removed geometrically: full-width
  rows and full-height columns of the black mask are gridlines (the curve
  is neither). The red mask needs no such step — grey gridlines are not
  red.
- **Trace by per-column centre, not nearest-to-previous.** A continuity
  tracker "rides the tops" of this very spiky 5-min data and skips the
  valleys, over-integrating. Taking each column's line centre
  independently follows every peak and valley. The red line uses an
  intensity-weighted centroid (halo-robust); the black line uses the
  pixel median of its cleaned mask.
- **Calibrate the y-axis by RANSAC anchored at zero.** The digit OCR of
  the tick labels occasionally misreads one label (5<->8, 0<->5); a plain
  linear fit then tilts and biases every value by ~10%. The plot bottom
  is definitionally 0 vph, so the scale is the consensus (RANSAC) slope
  from bottom through the labels, immune to a single misread.

Per-lane counts are deliberately not extracted (they tangle at 5-min and
their lane utilisation fLU is printed on the chart).
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from .plotbox import DAY_MINUTES, PlotBox, find_plot_box
from .tmc_header import TmcHeader, read_header
from .tmc_naming import TmcChart
from .yaxis import _classify, label_glyphs, read_y_axis

N_BINS = 288
BIN_MINUTES = DAY_MINUTES // N_BINS  # 5

_EDGE_MARGIN = 10  # TMC exports wrap the whole image in a border
_RED_DOM = 18  # min (R - max(G,B)) for a red-line pixel
_BLACK_MAX = 115  # black line: brightest channel below this
_BLACK_SPREAD = 50  # ...and near-neutral (max-min channel below this)
_ROW_GRID = 0.40  # mask rows filled past this fraction of width are gridlines
_COL_GRID = 0.70  # ...columns past this fraction of height, likewise
_SINGLE_LANE_COV = 0.30  # black-line coverage below this ⇒ single-lane chart


@dataclass
class TmcSeries:
    date: str
    approach: str  # full name, e.g. Northbound
    movement: str  # Thru | Left | Right
    sensor_line: str  # "Total (black)" or "single lane (red)"
    vph: np.ndarray  # 288 five-minute bin means, NaN where no data
    coverage: float
    header: TmcHeader
    box: PlotBox
    trace_cols: np.ndarray  # traced pixel columns (for QA overlay)
    trace_rows: np.ndarray

    @property
    def daily_total(self) -> float:
        return float(np.nansum(self.vph) * (BIN_MINUTES / 60.0))


def _robust_slope(gray: np.ndarray, box: PlotBox) -> float:
    """vph per pixel (upward), anchored so box bottom = 0 vph.

    Each recognized non-zero label implies a slope to the (bottom, 0)
    anchor; the consensus (largest inlier set) slope is returned, so one
    misread label cannot tilt the scale. Falls back to the shared linear
    fit if no labels are recognized.
    """
    labels = []
    for ycenter, glyphs in label_glyphs(gray, box):
        digits, ok = [], True
        for _x, bitmap in glyphs:
            ch, score = _classify(bitmap)
            if score < 0.55:
                ok = False
                break
            digits.append(ch)
        if ok and digits:
            value = int("".join(digits))
            if value > 0 and box.bottom - ycenter > 8:
                labels.append((ycenter, value))
    if not labels:
        return -read_y_axis(gray, box).slope

    best_slope, best_inliers = None, -1
    for ycenter, value in labels:
        s = value / (box.bottom - ycenter)
        inliers = [
            v / (box.bottom - y)
            for y, v in labels
            if abs(v - s * (box.bottom - y)) <= 0.08 * v + 8
        ]
        if len(inliers) > best_inliers:
            best_inliers, best_slope = len(inliers), float(np.median(inliers))
    return best_slope


def _red_weight(bgr: np.ndarray, box: PlotBox) -> np.ndarray:
    """Per-pixel redness (R - max(G,B)), clipped ≥0, inside the plot box."""
    b, g, r = (bgr[..., i].astype(np.float32) for i in range(3))
    w = np.zeros(bgr.shape[:2], np.float32)
    iv = (slice(box.top + 2, box.bottom - 1), slice(box.left + 2, box.right - 1))
    w[iv] = np.clip(r - np.maximum(g, b), 0, None)[iv]
    return w


def _black_mask(bgr: np.ndarray, box: PlotBox) -> np.ndarray:
    """Dark, near-neutral pixels (the black Total line) minus gridlines."""
    b, g, r = (bgr[..., i].astype(int) for i in range(3))
    mx = np.maximum(np.maximum(r, g), b)
    spread = mx - np.minimum(np.minimum(r, g), b)
    m = np.zeros(bgr.shape[:2], np.uint8)
    iv = (slice(box.top + 2, box.bottom - 1), slice(box.left + 2, box.right - 1))
    m[iv] = ((mx[iv] < _BLACK_MAX) & (spread[iv] < _BLACK_SPREAD)).astype(np.uint8)
    sub = m[box.top + 2 : box.bottom - 1, box.left + 2 : box.right - 1]
    sub[sub.sum(1) > _ROW_GRID * (box.right - box.left), :] = 0  # horizontal gridlines
    sub[:, sub.sum(0) > _COL_GRID * (box.bottom - box.top)] = 0  # vertical gridlines
    return m.astype(bool)


def _trace_black(mask: np.ndarray, box: PlotBox) -> dict[int, float]:
    """Per-column pixel median of the cleaned black mask."""
    off = box.top + 2
    out = {}
    for x in range(box.left + 2, box.right - 1):
        ys = np.flatnonzero(mask[off : box.bottom - 1, x])
        if len(ys):
            out[x] = float(np.median(ys)) + off
    return out


def _trace_red(weight: np.ndarray, box: PlotBox, min_weight: float = 8.0) -> dict[int, float]:
    """Per-column intensity-weighted centroid of the redness signal."""
    off = box.top + 2
    ys = np.arange(off, box.bottom - 1)
    out = {}
    for x in range(box.left + 2, box.right - 1):
        col = weight[off : box.bottom - 1, x]
        if col.sum() > min_weight:
            out[x] = float((ys * col).sum() / col.sum())
    return out


def _bin_5min(box: PlotBox, slope: float, traced: dict[int, float]) -> np.ndarray:
    binned: list[list[float]] = [[] for _ in range(N_BINS)]
    for x, y in traced.items():
        minute = (x - box.left) / box.width * DAY_MINUTES
        b = min(int(minute // BIN_MINUTES), N_BINS - 1)
        binned[b].append(max(slope * (box.bottom - y), 0.0))
    out = np.full(N_BINS, np.nan)
    for b, vals in enumerate(binned):
        if vals:
            out[b] = float(np.mean(vals))
    return out


def extract_total(chart: TmcChart) -> TmcSeries:
    bgr = cv2.imread(str(chart.path), cv2.IMREAD_COLOR)
    if bgr is None:
        raise RuntimeError(f"cannot read image {chart.path}")
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    box = find_plot_box(gray, edge_margin=_EDGE_MARGIN)
    slope = _robust_slope(gray, box)
    header = read_header(bgr, box)

    # Single-lane charts have no black Total line: fLU == 1 (from the
    # header), or — if OCR missed it — the black mask barely covers the
    # plot. Either way, trace the sole red line instead.
    black = _black_mask(bgr, box)
    view = black[box.top + 2 : box.bottom - 1, box.left + 2 : box.right - 1]
    black_cov = float(np.mean(view.any(axis=0)))
    single = (header.flu is not None and header.flu >= 0.999) or black_cov < _SINGLE_LANE_COV

    if single:
        traced = _trace_red(_red_weight(bgr, box), box)
    else:
        traced = _trace_black(black, box)

    cols = np.array(sorted(traced), dtype=float)
    rows = np.array([traced[int(x)] for x in cols], dtype=float)
    return TmcSeries(
        date=chart.date,
        approach=chart.approach_name,
        movement=chart.movement_name,
        sensor_line="single lane (red)" if single else "Total (black)",
        vph=_bin_5min(box, slope, traced),
        coverage=len(traced) / max(box.width - 3, 1),
        header=header,
        box=box,
        trace_cols=cols,
        trace_rows=rows,
    )
