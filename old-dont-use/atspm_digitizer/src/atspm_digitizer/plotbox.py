"""Plot-box detection and pixel <-> data calibration.

The plot area is bounded by dark axis/grid lines. Gridlines inside the
box are also dark and span its full width/height, so the frame is taken
as the outermost rows/columns whose dark-pixel count spans most of the
opposite dimension.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

DAY_MINUTES = 1440


@dataclass(frozen=True)
class PlotBox:
    left: int
    right: int
    top: int
    bottom: int

    @property
    def width(self) -> int:
        return self.right - self.left

    @property
    def height(self) -> int:
        return self.bottom - self.top

    def col_to_minute(self, col: np.ndarray | float) -> np.ndarray | float:
        return (np.asarray(col) - self.left) / self.width * DAY_MINUTES


def find_plot_box(
    gray: np.ndarray,
    dark_thresh: int = 100,
    span_frac: float = 0.45,
    edge_margin: int = 0,
) -> PlotBox:
    """Locate the axis frame in a grayscale chart image.

    span_frac is deliberately below the full span: the frame lines are
    interrupted where data lines cross them, and JPEG noise erodes a
    few pixels. edge_margin ignores long lines within that many pixels of
    the image border — some exports (e.g. the TMC charts) wrap the whole
    image in a frame that would otherwise be mistaken for the plot box.
    """
    dark = gray < dark_thresh
    h, w = gray.shape

    col_runs = dark.sum(axis=0)
    row_runs = dark.sum(axis=1)

    # Candidate frame lines must span a large fraction of the image,
    # and lie inside the image-border margin.
    cols = np.array([x for x in np.where(col_runs > h * span_frac)[0]
                     if edge_margin <= x < w - edge_margin])
    rows = np.array([y for y in np.where(row_runs > w * span_frac)[0]
                     if edge_margin <= y < h - edge_margin])
    if len(cols) < 2 or len(rows) < 2:
        raise RuntimeError(
            f"Could not locate plot frame (found {len(cols)} vertical, "
            f"{len(rows)} horizontal long lines)"
        )
    box = PlotBox(left=int(cols[0]), right=int(cols[-1]), top=int(rows[0]), bottom=int(rows[-1]))
    if box.width < w * 0.4 or box.height < h * 0.25:
        raise RuntimeError(f"Implausible plot box {box}")
    return box
