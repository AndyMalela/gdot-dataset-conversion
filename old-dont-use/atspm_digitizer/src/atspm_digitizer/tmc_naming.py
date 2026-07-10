"""Filename conventions and discovery for Turning Movement Count charts.

TMC chart images are named ``MMDD-<approach>-<movement>.jpg`` where
approach is nb|sb|eb|wb and movement is thru|left|right. Each chart plots
one movement's per-lane counts plus a black Total line (single-lane
charts have only the one lane, which is itself the total). We extract the
movement TOTAL only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

APPROACHES = {"nb": "Northbound", "sb": "Southbound", "eb": "Eastbound", "wb": "Westbound"}
MOVEMENTS = {"thru": "Thru", "left": "Left", "right": "Right"}

_RE = re.compile(
    r"^(?P<date>\d{4})-(?P<approach>nb|sb|eb|wb)-(?P<movement>thru|left|right)$"
)


@dataclass(frozen=True)
class TmcChart:
    path: Path
    date: str  # MMDD
    approach: str  # nb|sb|eb|wb
    movement: str  # thru|left|right

    @property
    def approach_name(self) -> str:
        return APPROACHES[self.approach]

    @property
    def movement_name(self) -> str:
        return MOVEMENTS[self.movement]

    @property
    def stem(self) -> str:
        return f"{self.date}-{self.approach}-{self.movement}"


def parse_chart_path(path: Path) -> TmcChart:
    m = _RE.match(path.stem)
    if not m:
        raise ValueError(
            f"{path.name!r} does not match MMDD-<approach>-<movement>.jpg "
            f"(approach: nb|sb|eb|wb, movement: thru|left|right)"
        )
    return TmcChart(path=path, date=m["date"], approach=m["approach"],
                    movement=m["movement"])


def discover_charts(data_dir: Path, date: str | None = None) -> list[TmcChart]:
    charts = []
    for path in sorted(data_dir.iterdir()):
        if path.suffix.lower() not in (".jpg", ".jpeg", ".png"):
            continue
        if not _RE.match(path.stem):
            continue
        c = parse_chart_path(path)
        if date is None or c.date == date:
            charts.append(c)
    return charts


def intersection_code(data_dir: Path) -> str:
    return data_dir.resolve().name
