"""OCR of the TMC chart header (validation reference only).

Each TMC chart prints its own summary above the plot, e.g.:

    Eastbound Thru Vehicle Lanes
    Total Volume = 13116; Peak Hour = 4:25 PM - 5:25 PM;
    Peak Hour Volume = 1173 VPH; PHF = 0.83; fLU = 0.89

There is no companion .md, so these values are read straight off the
image with OCR and used ONLY to sanity-check the extraction (compare the
printed Total Volume against the integrated series). They never alter the
extracted output.
"""

from __future__ import annotations

import functools
import re
from dataclasses import dataclass

import cv2
import numpy as np

from .plotbox import PlotBox


@dataclass
class TmcHeader:
    subtitle: str | None  # e.g. "Eastbound Thru Vehicle Lanes"
    total_volume: int | None
    peak_hour: str | None
    peak_hour_volume: int | None
    phf: float | None
    flu: float | None


@functools.cache
def _engine():
    from rapidocr_onnxruntime import RapidOCR

    return RapidOCR()


def _num(pattern: str, text: str, cast):
    m = re.search(pattern, text)
    return cast(m.group(1)) if m else None


def _header_variants(bgr: np.ndarray, box: PlotBox) -> list[np.ndarray]:
    """Several renderings to OCR and union.

    RapidOCR's tiny-text detection is inconsistent on this light-grey
    stats line: a given rendering may miss it while another reads it
    perfectly. The band alone fails on some charts and the full image on
    others (its detector is sensitive to crop aspect ratio), so we feed
    both — the full image plus band renderings (raw, 2x, binarized 2x) —
    and union the text, recovering the numbers on essentially any chart.
    """
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    band = gray[: max(box.top - 2, 1), :]
    bw = 255 - ((band < 150).astype(np.uint8) * 255)  # crisp black-on-white
    ups = cv2.INTER_CUBIC
    band_renders = [
        band,
        cv2.resize(band, None, fx=2, fy=2, interpolation=ups),
        cv2.resize(bw, None, fx=2, fy=2, interpolation=ups),
    ]
    return [bgr] + [cv2.cvtColor(r, cv2.COLOR_GRAY2BGR) for r in band_renders]


def read_header(bgr: np.ndarray, box: PlotBox) -> TmcHeader:
    """OCR the band between the image top and the plot box top."""
    lines: list[str] = []
    for render in _header_variants(bgr, box):
        result, _ = _engine()(render)
        lines += [txt for _b, txt, _c in (result or [])]
    flat = " ".join(lines).replace(" ", "")  # OCR drops most spaces; normalize

    subtitle = next(
        (t for t in lines if re.search(r"(Thru|Left|Right)Vehicle", t.replace(" ", ""))),
        None,
    )
    ph = re.search(r"PeakHour=([\d:APM\-]+?)(?::|;|PeakHourVolume)", flat)
    return TmcHeader(
        subtitle=subtitle,
        total_volume=_num(r"T[o0]t[a4]lV[o0]lume=(\d+)", flat, int),
        peak_hour=ph.group(1) if ph else None,
        peak_hour_volume=_num(r"PeakHourV[o0]lume=(\d+)", flat, int),
        phf=_num(r"PHF=(\d*\.?\d+)", flat, float),
        flu=_num(r"fLU=(\d*\.?\d+)", flat, float),
    )
