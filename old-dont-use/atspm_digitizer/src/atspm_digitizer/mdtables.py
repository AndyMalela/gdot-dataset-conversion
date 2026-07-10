"""Parse the per-day MMDD.md ground-truth tables.

Each .md holds one section per chart image, headed by a '## ...' line
and a '*Plot: `<filename>`*' marker, followed by a markdown table of
summary metrics. These tables are typed text and are VALIDATION ONLY:
extracted volumes are never rescaled to match them.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

_PLOT_RE = re.compile(r"\*Plot:\s*`([^`]+)`\*")
_ROW_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$")


@dataclass
class GroundTruth:
    """Metrics for one chart image, keyed as they appear in the table."""

    plot_filename: str
    heading: str
    metrics: dict[str, str] = field(default_factory=dict)

    def total_volume(self, direction: str | None = None) -> int | None:
        """Daily total for a direction, or the combined total if None."""
        key = f"{direction} Total Volume" if direction else "Total Volume"
        val = self.metrics.get(key)
        return int(val.replace(",", "")) if val else None

    def get(self, key: str) -> str | None:
        return self.metrics.get(key)


def parse_md(md_path: Path) -> dict[str, GroundTruth]:
    """All ground-truth sections in a day file, keyed by plot filename stem."""
    sections: dict[str, GroundTruth] = {}
    current: GroundTruth | None = None
    heading = ""
    for line in md_path.read_text().splitlines():
        if line.startswith("##"):
            heading = line.lstrip("#").strip()
            current = None
            continue
        m = _PLOT_RE.search(line)
        if m:
            stem = Path(m.group(1)).stem
            current = GroundTruth(plot_filename=m.group(1), heading=heading)
            sections[stem] = current
            continue
        m = _ROW_RE.match(line)
        if m and current is not None:
            key, val = m.group(1), m.group(2)
            if key not in ("Metric", "-", "---") and not set(key) <= {"-"}:
                current.metrics[key] = val
    return sections
