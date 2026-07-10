"""Parser for GDOT ATSPM portal "Turning Movement Counts" report exports.

These are the portal's own tabular 5-min per-movement vehicle counts
(<MMDD>data.txt, under data/<code>/) -- the numeric ground truth the
pixel-chart digitizer pipeline (atspm_digitizer `tmc` mode) was
approximating from chart images. Where a data.txt exists for a date, it
replaces the digitizer outright: exact integer per-bin counts, no
dashed-line/y-axis pixel error, and (unlike the digitized CSVs) no
rendering gaps -- every 5-min bin is populated, even at zero volume.

Right-turn movements are absent here for the same reason they're absent
from the digitizer: GDOT never charts/reports them for this intersection.

Format (tab-separated), as downloaded from the portal:
    an approach header row (Eastbound / Westbound / Northbound / Southbound)
        -- sometimes preceded by one or two stray lines (seen so far:
           " Vehicle", "- \tVehicle"); located by content, not position
    the next row: movement header (L / T / Total per approach + Vehicle Total)
    one row per 5-min bin -- "<h>:<mm> AM/PM" then 4 x (L, T, Total) + grand total
    a final "Total" row + column sums (not a bin -- excluded)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

APPROACH_ORDER = ["eb", "wb", "nb", "sb"]
BIN_SECONDS = 300
N_BINS = 288  # a full day at 5-min resolution

_FILENAME_RE = re.compile(r"^(?P<date>\d{4})data\.txt$")
_TIME_RE = re.compile(r"^(?P<h>\d{1,2}):(?P<m>\d{2}) (?P<ampm>AM|PM)$")


def _time_label_to_seconds(label: str) -> int:
    m = _TIME_RE.match(label)
    if not m:
        raise ValueError(f"unparseable time label: {label!r}")
    h, mm, ampm = int(m["h"]), int(m["m"]), m["ampm"]
    if ampm == "AM":
        h = 0 if h == 12 else h
    else:
        h = 12 if h == 12 else h + 12
    return h * 3600 + mm * 60


@dataclass(frozen=True)
class PortalReport:
    date: str  # MMDD
    path: Path
    # (approach, movement) -> {begin_seconds: count}; movement in {"left", "thru"}
    counts: dict[tuple[str, str], dict[int, int]]
    n_bins: int  # data rows actually present in the file (288 == full day)

    @property
    def is_full_day(self) -> bool:
        return self.n_bins == N_BINS


def parse_report(path: Path) -> PortalReport:
    m = _FILENAME_RE.match(path.name)
    if not m:
        raise ValueError(f"{path.name!r} does not match MMDDdata.txt")
    date = m["date"]

    lines = [l for l in path.read_text().splitlines() if l.strip()]
    header_idx = next(
        (i for i, l in enumerate(lines) if l.strip().startswith("Eastbound")), None
    )
    if header_idx is None:
        raise ValueError(f"{path.name!r}: no 'Eastbound...' header row found")
    data_lines = [
        l for l in lines[header_idx + 2:] if not l.strip().startswith("Total")
    ]

    counts: dict[tuple[str, str], dict[int, int]] = {
        (a, mv): {} for a in APPROACH_ORDER for mv in ("left", "thru")
    }
    for line in data_lines:
        parts = [p.strip() for p in line.split("\t")]
        begin = _time_label_to_seconds(parts[0])
        idx = 1
        for a in APPROACH_ORDER:
            left, thru = int(parts[idx]), int(parts[idx + 1])
            idx += 3  # skip that approach's own Total column
            counts[(a, "left")][begin] = left
            counts[(a, "thru")][begin] = thru

    return PortalReport(date=date, path=path, counts=counts, n_bins=len(data_lines))


def discover_reports(report_dir: Path) -> list[PortalReport]:
    """All MMDDdata.txt files directly under report_dir, parsed and date-sorted."""
    reports = []
    for path in sorted(report_dir.glob("*data.txt")):
        if _FILENAME_RE.match(path.name):
            reports.append(parse_report(path))
    return reports
