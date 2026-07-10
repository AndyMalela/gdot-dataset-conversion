"""Y-axis tick label reading.

The y-axis maximum differs per chart, so the scale must be read from the
tick labels in the image. The ATSPM portal renders every chart with the
same small font; bundled digit templates (see scripts/make_digit_templates.py)
are matched against glyphs segmented from the label strip left of the
plot box. All recognized (label value, pixel row) pairs are then fit to
a line, giving the full row -> vph calibration rather than trusting any
single label.
"""

from __future__ import annotations

import functools
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

import cv2
import numpy as np

from .plotbox import PlotBox

# Label strip: how far left of the plot box tick labels may extend.
# Wide enough for "10000" in two staggered columns, narrow enough to
# exclude the rotated axis title.
LABEL_STRIP_WIDTH = 90

_GLYPH_H = (5, 14)  # acceptable glyph bbox height range, px
_GLYPH_W = (2, 12)
_ROW_TOL = 3  # px: glyphs whose y-centers differ by <= this are one label
_MATCH_MIN = 0.55  # min normalized template score to accept a digit


def _binarize_labels(gray: np.ndarray, box: PlotBox) -> tuple[np.ndarray, int, int]:
    """Dark mask of the label strip with tick marks removed.

    Returns (mask, x_offset, y_offset) of the strip in image coords.
    """
    x0 = max(0, box.left - LABEL_STRIP_WIDTH)
    y0 = max(0, box.top - 8)
    strip = gray[y0 : box.bottom + 8, x0 : box.left - 1]
    mask = (strip < 128).astype(np.uint8)
    # JPEG compression can sever a digit's thin stroke horizontally,
    # splitting one glyph into two components. Close vertically only:
    # this heals such breaks without bridging the ~1px gap between
    # adjacent digits.
    vkernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, vkernel)
    # Tick marks are long thin horizontal strokes that can touch the
    # last digit of right-column labels; remove them so connected
    # components stay per-glyph. Digit strokes are < 9 px wide.
    hkernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 1))
    ticks = cv2.morphologyEx(mask, cv2.MORPH_OPEN, hkernel)
    return mask & ~ticks, x0, y0


def label_glyphs(
    gray: np.ndarray, box: PlotBox
) -> list[tuple[float, list[tuple[int, np.ndarray]]]]:
    """Segment tick-label glyphs, grouped into label rows.

    Returns [(row_y_center_in_image_coords, [(x, binary_bitmap), ...]), ...]
    sorted top to bottom; glyphs within a row sorted left to right.
    """
    mask, x0, y0 = _binarize_labels(gray, box)
    n, _, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)

    glyphs = []  # (ycenter, x, bitmap)
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        if not (_GLYPH_W[0] <= w <= _GLYPH_W[1] and _GLYPH_H[0] <= h <= _GLYPH_H[1]):
            continue
        if area < 8:
            continue
        glyphs.append((centroids[i][1], x, mask[y : y + h, x : x + w] * 255))

    glyphs.sort(key=lambda g: g[0])
    rows: list[list[tuple[float, int, np.ndarray]]] = []
    for g in glyphs:
        if rows and abs(g[0] - np.mean([r[0] for r in rows[-1]])) <= _ROW_TOL:
            rows[-1].append(g)
        else:
            rows.append([g])

    out = []
    for row in rows:
        row.sort(key=lambda g: g[1])
        # The rotated y-axis title can fall inside the strip on charts
        # where the labels sit close to the box. Title glyphs are far
        # left of the label digits, so keep only the rightmost cluster
        # of tightly spaced glyphs (inter-digit gaps are 1-3 px).
        cluster = [row[-1]]
        for g in reversed(row[:-1]):
            prev_left = cluster[0][1]
            if prev_left - (g[1] + g[2].shape[1]) <= 5:
                cluster.insert(0, g)
            else:
                break
        ycenter = float(np.mean([g[0] for g in cluster])) + y0
        out.append((ycenter, [(g[1], g[2]) for g in cluster]))
    return out


@functools.cache
def _templates() -> list[tuple[str, np.ndarray]]:
    """Bundled (digit, bitmap) template variants."""
    tmpl = []
    digits_dir = resources.files("atspm_digitizer") / "digits"
    for entry in sorted(digits_dir.iterdir(), key=lambda e: e.name):
        if not entry.name.endswith(".png"):
            continue
        with resources.as_file(entry) as p:
            img = cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)
        if img is not None:
            tmpl.append((entry.name[0], img))
    if len({ch for ch, _ in tmpl}) < 10:
        raise RuntimeError(
            "Bundled digit templates missing; run scripts/make_digit_templates.py"
        )
    return tmpl


def _classify(bitmap: np.ndarray) -> tuple[str, float]:
    """Best digit for a glyph bitmap and its match score (0..1)."""
    best, best_score = "?", -1.0
    for ch, t in _templates():
        hh, ww = max(bitmap.shape[0], t.shape[0]), max(bitmap.shape[1], t.shape[1])
        if abs(bitmap.shape[1] - t.shape[1]) > 3:
            continue  # width mismatch ('1' vs others) — cheap reject

        def center(img: np.ndarray) -> np.ndarray:
            canvas = np.zeros((hh, ww), np.float32)
            dy, dx = (hh - img.shape[0]) // 2, (ww - img.shape[1]) // 2
            canvas[dy : dy + img.shape[0], dx : dx + img.shape[1]] = img
            return canvas

        a, b = center(bitmap), center(t)
        denom = np.maximum(a, b).sum()
        score = 1.0 - np.abs(a - b).sum() / denom if denom else 0.0
        if score > best_score:
            best, best_score = ch, float(score)
    return best, best_score


@dataclass(frozen=True)
class YAxis:
    """Linear pixel-row -> vph calibration from the tick labels."""

    slope: float  # vph per pixel row (negative: rows grow downward)
    intercept: float
    labels_used: int
    y_max: float  # vph at the plot box top edge

    def row_to_vph(self, row: np.ndarray | float) -> np.ndarray | float:
        return self.slope * np.asarray(row) + self.intercept


def read_y_axis(gray: np.ndarray, box: PlotBox) -> YAxis:
    points = []  # (row_ycenter, value)
    for ycenter, row_glyphs in label_glyphs(gray, box):
        digits = []
        ok = True
        for _x, bitmap in row_glyphs:
            ch, score = _classify(bitmap)
            if score < _MATCH_MIN:
                ok = False
                break
            digits.append(ch)
        if ok and digits:
            points.append((ycenter, int("".join(digits))))

    if len(points) < 3:
        raise RuntimeError(
            f"Only {len(points)} y-axis labels recognized — cannot calibrate"
        )

    rows = np.array([p[0] for p in points])
    vals = np.array([p[1] for p in points], dtype=float)
    # Theil-Sen initial fit: a misread label (e.g. '5'->'8' on the tiny
    # font) is a gross outlier that would skew a least-squares fit.
    ii, jj = np.triu_indices(len(rows), k=1)
    pair_slopes = (vals[jj] - vals[ii]) / (rows[jj] - rows[ii])
    slope = float(np.median(pair_slopes))
    intercept = float(np.median(vals - slope * rows))
    step = np.median(np.abs(np.diff(vals[np.argsort(rows)])))
    # Iterate: drop misreads (>40% of one label step off the fit), refit
    keep = np.ones(len(rows), bool)
    for _ in range(5):
        new_keep = np.abs(vals - (slope * rows + intercept)) < 0.4 * max(step, 1.0)
        if new_keep.sum() < 3:
            raise RuntimeError("Y-axis label fit too noisy to trust")
        slope, intercept = np.polyfit(rows[new_keep], vals[new_keep], 1)
        if (new_keep == keep).all():
            break
        keep = new_keep

    if slope >= 0:
        raise RuntimeError("Y-axis calibration has wrong sign (slope >= 0)")
    bottom_val = slope * box.bottom + intercept
    if abs(bottom_val) > 1.5 * step:
        raise RuntimeError(
            f"Y-axis value at box bottom is {bottom_val:.0f}, expected ~0"
        )
    return YAxis(
        slope=float(slope),
        intercept=float(intercept),
        labels_used=int(keep.sum()),
        y_max=float(slope * box.top + intercept),
    )
