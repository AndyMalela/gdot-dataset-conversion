"""Output tree: result/<intersection_code>/ at the repo root.

The repo root is taken as the parent of the data/ directory containing
the intersection folder (data/<code>/...); if the layout differs, the
current working directory is used.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pandas as pd

from .extract import BIN_MINUTES, N_BINS, ExtractedSeries
from .naming import ChartImage
from .plotbox import PlotBox

# Overlay trace colors (BGR), chosen to contrast with the source lines
_TRACE_BGR = {"blue": (0, 255, 0), "red": (0, 255, 255)}


def result_dir(code_dir: Path) -> Path:
    code_dir = code_dir.resolve()
    root = code_dir.parent.parent if code_dir.parent.name == "data" else Path.cwd()
    return root / "result" / code_dir.name


def bin_labels() -> list[str]:
    return [f"{(b * BIN_MINUTES) // 60:02d}:{(b * BIN_MINUTES) % 60:02d}"
            for b in range(N_BINS)]


def series_frame(img: ChartImage, series: list[ExtractedSeries]) -> pd.DataFrame:
    """Long-format extraction result for one image."""
    labels = bin_labels()
    frames = []
    for s in series:
        frames.append(pd.DataFrame({
            "time_15min": labels,
            "direction": s.direction,
            "sensor": img.sensor,
            "vph_raw": np.round(s.vph, 1),
        }))
    return pd.concat(frames, ignore_index=True)


def write_csv(out_dir: Path, img: ChartImage, series: list[ExtractedSeries]) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{img.stem}.csv"
    series_frame(img, series).to_csv(path, index=False)
    return path


def write_overlay(
    out_dir: Path,
    img: ChartImage,
    bgr: np.ndarray,
    box: PlotBox,
    series: list[ExtractedSeries],
) -> Path:
    qa_dir = out_dir / "qa"
    qa_dir.mkdir(parents=True, exist_ok=True)
    canvas = bgr.copy()
    cv2.rectangle(canvas, (box.left, box.top), (box.right, box.bottom),
                  (180, 180, 180), 1)
    for s in series:
        color = _TRACE_BGR[s.color]
        for x, y in zip(s.trace_cols.astype(int), np.round(s.trace_rows).astype(int)):
            canvas[max(y - 1, 0) : y + 1, x] = color
        cv2.putText(
            canvas,
            f"{s.direction}: traced ({'green' if s.color == 'blue' else 'yellow'})",
            (box.left + 10, box.top - 8 - 14 * (s.color == "red")),
            cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1, cv2.LINE_AA,
        )
    path = qa_dir / f"{img.stem}_overlay.png"
    cv2.imwrite(str(path), canvas)
    return path


def write_validation(out_dir: Path, img: ChartImage, report: str) -> Path:
    vdir = out_dir / "validation"
    vdir.mkdir(parents=True, exist_ok=True)
    path = vdir / f"{img.stem}_validation.txt"
    path.write_text(report)
    return path


def write_consolidated(out_dir: Path, frames: list[tuple[str, pd.DataFrame]]) -> Path:
    """Stack per-image frames (with a date column) into consolidated.csv."""
    out_dir.mkdir(parents=True, exist_ok=True)
    parts = [df.assign(date=date)[["date", *df.columns]] for date, df in frames]
    path = out_dir / "consolidated.csv"
    pd.concat(parts, ignore_index=True).to_csv(path, index=False)
    return path
