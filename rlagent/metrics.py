"""Tripinfo-based control-performance metrics.

Mirrors the paper's evaluation quantities on SUMO's own per-trip records:
  average delay        <- tripinfo timeLoss  (time lost to driving below
                          ideal speed, incl. stops -- the paper defines delay
                          as additional travel time vs the free-flow speed)
  average number halts <- tripinfo waitingCount (# distinct stops < 0.1 m/s)
  throughput           <- # trips completed within the window
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass


@dataclass
class TripMetrics:
    n_trips: int
    avg_delay: float
    avg_halts: float

    def row(self) -> str:
        return (f"throughput={self.n_trips}  avg_delay={self.avg_delay:.2f}s  "
                f"avg_halts={self.avg_halts:.3f}")


def read_tripinfo(path: str) -> TripMetrics:
    root = ET.parse(path).getroot()
    delays, halts = [], []
    for ti in root.iter("tripinfo"):
        delays.append(float(ti.get("timeLoss")))
        halts.append(int(ti.get("waitingCount")))
    n = len(delays)
    if n == 0:
        return TripMetrics(0, float("nan"), float("nan"))
    return TripMetrics(n, sum(delays) / n, sum(halts) / n)
