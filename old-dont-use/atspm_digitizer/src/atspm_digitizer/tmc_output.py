"""Outputs for the TMC pipeline: CSVs, QA overlays, validation, batch.

Output tree, rooted at the parent of the input dir (so input tmc/<code>/
gives outputs under tmc/result/<code>/ and tmc/testing/<code>/):

    tmc/result/<code>/<MMDD>-<appr>-<mvmt>.csv
    tmc/result/<code>/qa/<...>_overlay.png        (--plot)
    tmc/result/<code>/validation/<...>_validation.txt
    tmc/result/<code>/consolidated.csv            (--all)
    tmc/testing/<code>/<...>.png                   (visualization, separate script)
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pandas as pd

from .tmc_extract import BIN_MINUTES, N_BINS, TmcSeries
from .tmc_naming import TmcChart


def result_dir(code_dir: Path) -> Path:
    code_dir = code_dir.resolve()
    return code_dir.parent / "result" / code_dir.name


def bin_labels() -> list[str]:
    return [f"{(b * BIN_MINUTES) // 60:02d}:{(b * BIN_MINUTES) % 60:02d}"
            for b in range(N_BINS)]


def series_frame(chart: TmcChart, s: TmcSeries) -> pd.DataFrame:
    return pd.DataFrame({
        "time_5min": bin_labels(),
        "approach": s.approach,
        "movement": s.movement,
        "total_vph": np.round(s.vph, 1),
    })


def write_csv(out_dir: Path, chart: TmcChart, s: TmcSeries) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{chart.stem}.csv"
    series_frame(chart, s).to_csv(path, index=False)
    return path


def write_overlay(out_dir: Path, chart: TmcChart, s: TmcSeries) -> Path:
    qa = out_dir / "qa"
    qa.mkdir(parents=True, exist_ok=True)
    bgr = cv2.imread(str(chart.path), cv2.IMREAD_COLOR)
    box = s.box
    cv2.rectangle(bgr, (box.left, box.top), (box.right, box.bottom), (180, 180, 180), 1)
    for x, y in zip(s.trace_cols.astype(int), np.round(s.trace_rows).astype(int)):
        bgr[max(y - 1, 0):y + 1, x] = (0, 255, 0)
    path = qa / f"{chart.stem}_overlay.png"
    cv2.imwrite(str(path), bgr)
    return path


def validation_report(chart: TmcChart, s: TmcSeries) -> str:
    h = s.header
    n_nan = int(np.isnan(s.vph).sum())
    lines = [
        f"=== {chart.path.name} ===",
        f"{s.approach} {s.movement}  line: {s.sensor_line}",
        f"OCR header: subtitle={h.subtitle!r} PHF={h.phf} fLU={h.flu} "
        f"peak_hour={h.peak_hour} peak_hour_vph={h.peak_hour_volume}",
    ]
    extracted = s.daily_total
    if h.total_volume:
        err = (extracted - h.total_volume) / h.total_volume * 100
        lines.append(
            f"daily total: extracted {extracted:8.0f}   OCR {h.total_volume:8d}   "
            f"error {err:+6.1f}%   [coverage {s.coverage*100:.0f}%, {n_nan} empty 5-min bins]"
        )
    else:
        lines.append(
            f"daily total: extracted {extracted:8.0f}   OCR total: NOT READ   "
            f"[coverage {s.coverage*100:.0f}%, {n_nan} empty 5-min bins]"
        )
    return "\n".join(lines) + "\n"


def write_validation(out_dir: Path, chart: TmcChart, report: str) -> Path:
    vdir = out_dir / "validation"
    vdir.mkdir(parents=True, exist_ok=True)
    path = vdir / f"{chart.stem}_validation.txt"
    path.write_text(report)
    return path


def write_consolidated(out_dir: Path, frames: list[tuple[str, pd.DataFrame]]) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    parts = [df.assign(date=date)[["date", *df.columns]] for date, df in frames]
    path = out_dir / "consolidated.csv"
    pd.concat(parts, ignore_index=True).to_csv(path, index=False)
    return path
