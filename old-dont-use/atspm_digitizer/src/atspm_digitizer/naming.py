"""Filename conventions and input discovery.

Volume chart images are named ``MMDD_<pair>_<sensor>.jpg`` where
pair is ``nbsb`` or ``ebwb`` and sensor is one of ``advance-260ft``,
``advance-stopbar``, ``matrix``. Each day also has a ``MMDD.md`` file
with the ground-truth summary tables.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

PAIR_DIRECTIONS = {
    "nbsb": ("Northbound", "Southbound"),
    "ebwb": ("Eastbound", "Westbound"),
}
SENSORS = ("advance-260ft", "advance-stopbar", "matrix")

_IMAGE_RE = re.compile(
    r"^(?P<date>\d{4})_(?P<pair>nbsb|ebwb)_(?P<sensor>" + "|".join(SENSORS) + r")$"
)


@dataclass(frozen=True)
class ChartImage:
    """A volume chart image plus everything derivable from its name."""

    path: Path
    date: str  # MMDD
    pair: str  # nbsb | ebwb
    sensor: str

    @property
    def directions(self) -> tuple[str, str]:
        """(blue line direction, red line direction)."""
        return PAIR_DIRECTIONS[self.pair]

    @property
    def stem(self) -> str:
        return f"{self.date}_{self.pair}_{self.sensor}"

    @property
    def md_path(self) -> Path:
        return self.path.with_name(f"{self.date}.md")


def parse_image_path(path: Path) -> ChartImage:
    m = _IMAGE_RE.match(path.stem)
    if not m:
        raise ValueError(
            f"{path.name!r} does not match MMDD_<pair>_<sensor>.jpg "
            f"(pair: nbsb|ebwb, sensor: {'|'.join(SENSORS)})"
        )
    return ChartImage(path=path, date=m["date"], pair=m["pair"], sensor=m["sensor"])


def discover_images(data_dir: Path, date: str | None = None) -> list[ChartImage]:
    """All volume chart images in data_dir, optionally for one MMDD date.

    Non-matching files (e.g. ped_*.jpg, *.md) are silently skipped.
    """
    images = []
    for path in sorted(data_dir.iterdir()):
        if path.suffix.lower() not in (".jpg", ".jpeg", ".png"):
            continue
        if not _IMAGE_RE.match(path.stem):
            continue
        img = parse_image_path(path)
        if date is None or img.date == date:
            images.append(img)
    return images


def intersection_code(data_dir: Path) -> str:
    """The intersection code is the data directory's own name."""
    return data_dir.resolve().name
