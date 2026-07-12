"""Tripinfo-based control-performance metrics.

Mirrors the paper's evaluation quantities on SUMO's own per-trip records:
  in-network delay     <- tripinfo timeLoss  (time lost to driving below
                          ideal speed, incl. stops, WHILE in the network)
  insertion delay      <- tripinfo departDelay (time a vehicle waited to be
                          inserted because its entry lane was full -- i.e.
                          spillback backed up to the source / unmet demand)
  total delay          <- timeLoss + departDelay  (what a traveller actually
                          experiences; the honest number under oversaturation)
  average number halts <- tripinfo waitingCount (# distinct stops < 0.1 m/s)
  throughput           <- # trips completed within the window

WHY total delay matters (learned the hard way, see experiments/EXP-002):
under oversaturation a controller can keep its *in-network* timeLoss low simply
by holding vehicles OUT of the network -- the queue then piles up at the
entrances as departDelay. Reporting timeLoss alone hid this and made a
peak-hour-worse policy look better. `avg_delay` below is now TOTAL delay;
`avg_timeloss` is kept separately so the two effects can be distinguished.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass


@dataclass
class TripMetrics:
    n_trips: int
    avg_delay: float        # total: timeLoss + departDelay
    avg_halts: float
    avg_timeloss: float = float("nan")   # in-network only
    avg_departdelay: float = float("nan")  # insertion backlog only

    def row(self) -> str:
        return (f"throughput={self.n_trips}  avg_delay={self.avg_delay:.2f}s "
                f"(timeLoss={self.avg_timeloss:.2f}+insert={self.avg_departdelay:.2f})  "
                f"avg_halts={self.avg_halts:.3f}")


def read_tripinfo(path: str) -> TripMetrics:
    root = ET.parse(path).getroot()
    tl, dd, halts = [], [], []
    for ti in root.iter("tripinfo"):
        tl.append(float(ti.get("timeLoss")))
        dd.append(float(ti.get("departDelay")))
        halts.append(int(ti.get("waitingCount")))
    n = len(tl)
    if n == 0:
        return TripMetrics(0, float("nan"), float("nan"))
    a_tl = sum(tl) / n
    a_dd = sum(dd) / n
    return TripMetrics(n, a_tl + a_dd, sum(halts) / n,
                       avg_timeloss=a_tl, avg_departdelay=a_dd)
