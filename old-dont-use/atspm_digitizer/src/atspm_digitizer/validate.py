"""Extracted-vs-ground-truth comparison report.

Compares the daily total implied by the extracted 15-minute series with
the totals in the day's .md tables. Purely informational — extraction
output is never adjusted to match.
"""

from __future__ import annotations

import numpy as np

from .extract import ExtractedSeries
from .mdtables import GroundTruth
from .naming import ChartImage
from .yaxis import YAxis


def validation_report(
    img: ChartImage,
    yaxis: YAxis,
    series: list[ExtractedSeries],
    truth: GroundTruth | None,
) -> str:
    lines = [
        f"=== {img.path.name} ===",
        f"sensor: {img.sensor}   pair: {img.pair}   "
        f"y_max detected: {yaxis.y_max:.0f} ({yaxis.labels_used} labels)",
    ]
    if truth is None:
        lines.append("ground truth: NOT FOUND in companion .md — totals unchecked")
    combined_extracted = 0.0
    for s in series:
        n_nan = int(np.isnan(s.vph).sum())
        extracted = s.daily_total
        combined_extracted += extracted
        line = (
            f"{s.direction:<10} ({s.color} line)  "
            f"extracted total {extracted:9.0f}"
        )
        if truth and (t := truth.total_volume(s.direction)) is not None:
            err = (extracted - t) / t * 100.0
            line += f"   truth {t:7d}   error {err:+6.1f}%"
        line += (
            f"   [trace coverage {s.coverage * 100:.0f}%, {n_nan} empty bins"
            + (f", {s.interpolated_bins} interpolated" if s.interpolated_bins else "")
            + "]"
        )
        lines.append(line)
    if truth and (t := truth.total_volume(None)) is not None:
        err = (combined_extracted - t) / t * 100.0
        lines.append(
            f"{'Combined':<10}              "
            f"extracted total {combined_extracted:9.0f}   "
            f"truth {t:7d}   error {err:+6.1f}%"
        )
    if truth:
        for s in series:
            ph = truth.get(f"{s.direction} Peak Hour")
            phv = truth.get(f"{s.direction} Peak Hour Volume")
            if ph and phv:
                lines.append(
                    f"{s.direction:<10} peak hour: extracted "
                    f"{_peak_hour(s.vph)}   truth {ph} ({phv} vph)"
                )
    return "\n".join(lines) + "\n"


def _peak_hour(vph: np.ndarray) -> str:
    """Start time and volume of the best 4-bin (1 h) rolling window."""
    windows = np.array([
        np.nansum(vph[i : i + 4]) for i in range(len(vph) - 3)
    ]) * 0.25
    i = int(np.nanargmax(windows))
    h, m = divmod(i * 15, 60)
    return f"{h:02d}:{m:02d}-{(h + 1) % 24:02d}:{m:02d} ({windows[i]:.0f} veh)"
