"""MaxPressure on the NEMA engine, from field detectors only (cyclic variant: the engine keeps the ring
order, so the rule decides only when to end the current green).

Queue per phase, input-output estimate from the same detectors the other controllers read (QueueEstimator,
also an input of LSTDQ v2):
    + vehicles counted on the phase's count zones (setback zones for throughs, stop-bar zones for lefts)
    - discharge at the calibrated saturation flow per lane while the phase shows green and its stop-bar
      zone is occupied
    = 0 once the stop-bar zone has been empty for RESET_S (the queue has cleared; covers vehicles still
      travelling from a setback zone to the stop line)
Lefts are counted only when they reach the 12 m stop-bar zone, so a long left queue is underestimated.

Pressure = queue x lanes (Varaiya: queue x service rate; the saturation flow per lane is common to all
phases). No downstream term: 7065 has no exit detectors (and the simulated exits are not metered).

Rule: once a green has served its minimum, end it when a phase waiting in the same ring has higher pressure,
or when its own queue is gone and another phase is called. Max greens, ped minimums, clearances and the
ring-barrier order are the engine's, as for every controller.
"""
from __future__ import annotations

import json
from pathlib import Path

SAT_FLOW = 1950 / 3600          # veh/s per lane of green (CALIBRATION.md)
RESET_S = 6.0                   # stop-bar zone empty this long -> queue cleared (~ setback-to-stop-line travel)


class QueueEstimator:
    """per-phase queue estimate (vehicles) from count zones and stop-bar zones; call update() every step."""
    def __init__(self, site_dir, sig):
        site_dir = Path(site_dir)
        mv = json.loads((site_dir / "movements.json").read_text())["movements"]
        self.lanes = {m["phases"][0]: m["lanes"] for m in mv.values()}
        det = [d for d in json.loads((site_dir / "detectors.json").read_text())["detectors"]
               if d.get("modelled", True)]
        self.phases = sorted(self.lanes)
        self.stopbar = {p: [f"ch{d['ch']}" for d in det if d["phase"] == p and d["kind"] == "stopbar"
                            and "right" not in d.get("note", "")] for p in self.phases}
        self.count = {p: ([f"ch{d['ch']}" for d in det if d["phase"] == p and d["kind"] == "setback"]
                          or self.stopbar[p]) for p in self.phases}
        self.e1 = set(sig.conn.inductionloop.getIDList())
        self.seen = {ch: set() for chs in self.count.values() for ch in chs}
        self.q = {p: 0.0 for p in self.phases}
        self.empty_since = {p: 0.0 for p in self.phases}

    def update(self, sig, display):
        conn, dt = sig.conn, sig.conn.simulation.getDeltaT()
        for p in self.phases:
            for ch in self.count[p]:
                ids = set(conn.inductionloop.getLastStepVehicleIDs(ch) if ch in self.e1
                          else conn.lanearea.getLastStepVehicleIDs(ch))
                self.q[p] += len(ids - self.seen[ch])
                self.seen[ch] = ids
            occupied = any(conn.lanearea.getLastStepVehicleNumber(ch) > 0 for ch in self.stopbar[p])
            if occupied:
                self.empty_since[p] = sig.now
                if display.get(p) == "G":
                    self.q[p] = max(0.0, self.q[p] - SAT_FLOW * self.lanes[p] * dt)
            elif sig.now - self.empty_since[p] >= RESET_S:
                self.q[p] = 0.0


class MaxPressurePolicy:
    def __init__(self, site_dir):
        self.site_dir = Path(site_dir)
        self.est = None

    def pressure(self, p):
        return self.est.q[p] * self.est.lanes[p]

    def end_requests(self, sig):
        if self.est is None:
            self.est = QueueEstimator(self.site_dir, sig)
            self.rings = {int(r): [p for g in gs for p in g] for r, gs in sig.sig["rings"].items()}
        self.est.update(sig, sig.engine.display())
        q = self.est.q
        out = set()
        for ring in (1, 2):
            p, mode, el, _ = sig.engine.ring_state(ring)
            if mode != "G" or el < sig.engine.ph[p].min_service() - 1e-9:
                continue
            waiting = [x for x in self.rings[ring] if x != p and (q[x] > 0 or sig.engine._called(x))]
            if not waiting:
                continue
            if q[p] <= 0 or self.pressure(p) < max(self.pressure(x) for x in waiting):
                out.add(ring)
        return out
