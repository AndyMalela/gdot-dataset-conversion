"""LSTDQ signal controller: decides, for each ring once its green has served its minimum, every DECISION_S
seconds, whether to extend the green (0) or end it (1). The NEMA engine still enforces every rule (max green,
pedestrian minimums, ring order, barriers), exactly as for the other controllers.

State (field-deployable, detectors only), per phase p:
    occ   share of p's stop-bar presence zones occupied now
    gap   seconds since p's detectors last saw a vehicle, capped at GAP_CAP, / GAP_CAP
    rate  vehicles counted on p's count zones in the last RATE_WIN s, per lane, / (RATE_WIN * 0.5 veh/s)
plus the deciding phase's elapsed green / its max green, and a bias. Phase-gated: the block is placed in the
slot of the deciding phase (8 phases), so every phase has its own weights (v1 EXP-002).

Reward (training only, not a controller input): minus vehicles stopped on the approaches and waiting to
enter, per second, i.e. minus the delay accumulating in the network.
"""
from __future__ import annotations

import json
from collections import deque
from pathlib import Path

import numpy as np

DECISION_S = 1.0
GAP_CAP = 10.0
RATE_WIN = 30.0
PHASES = tuple(range(1, 9))
PER_PHASE = 3
BLOCK = PER_PHASE * len(PHASES) + 2          # + elapsed, bias
M = BLOCK * len(PHASES)                      # phase-gated state size


class LSTDQPolicy:
    def __init__(self, site_dir, w=None, eps=0.0, behaviour=None, seed=0, record=False):
        """w: LinearQ weights (None: no model yet, use `behaviour`); behaviour: fallback policy for
        iteration 0 (e.g. ActuatedPolicy); eps: share of random actions; record: keep transitions."""
        self.site_dir = Path(site_dir)
        self.w = None if w is None else np.asarray(w).reshape(2, M)
        self.eps, self.behaviour, self.record = eps, behaviour, record
        self.rng = np.random.default_rng(seed)
        mv = json.loads((self.site_dir / "movements.json").read_text())["movements"]
        self.lanes = {}
        for m in mv.values():
            self.lanes[m["phases"][0]] = m["lanes"]
        self._init = False
        self.open = {}                       # ring -> [x, a, reward so far, t0]
        self.X, self.A, self.R, self.X2, self.D = [], [], [], [], []
        self.last_dec = {1: -1e9, 2: -1e9}

    # ---- detector bookkeeping
    def _setup(self, sig):
        det = json.loads((self.site_dir / "detectors.json").read_text())
        det = [d for d in det["detectors"] if d.get("modelled", True)]
        self.stopbar = {p: [f"ch{d['ch']}" for d in det if d["phase"] == p and d["kind"] == "stopbar"
                            and "right" not in d.get("note", "")] for p in PHASES}
        # count channels: upstream zones for throughs, the stop-bar zones for lefts (they also count)
        self.count = {p: ([f"ch{d['ch']}" for d in det if d["phase"] == p and d["kind"] == "setback"]
                          or self.stopbar[p]) for p in PHASES}
        self.seen = {ch: set() for chs in self.count.values() for ch in chs}
        self.hits = {p: deque() for p in PHASES}
        self.approach_edges = self._approach_edges(sig)
        self._init = True

    def _approach_edges(self, sig):
        import sumolib
        from ..sim import run
        mv = json.loads((self.site_dir / "movements.json").read_text())
        net = sumolib.net.readNet(str(run.net_file(self.site_dir).resolve()))
        edges = set()
        for m in mv["movements"].values():
            p, _ = net.getShortestPath(net.getEdge(mv["entry_edges"][m["leg"]]), net.getEdge(m["from"]),
                                       vClass="passenger")
            edges |= {e.getID() for e in p}
        return sorted(edges)

    def _observe_counts(self, sig):
        conn, t = sig.conn, sig.now
        for p, chs in self.count.items():
            for ch in chs:
                ids = (conn.inductionloop.getLastStepVehicleIDs(ch) if ch in self._e1
                       else conn.lanearea.getLastStepVehicleIDs(ch))
                new = [v for v in ids if v not in self.seen[ch]]
                if new:
                    self.hits[p].append((t, len(new)))
                self.seen[ch] = set(ids)
            while self.hits[p] and self.hits[p][0][0] < t - RATE_WIN:
                self.hits[p].popleft()

    def features(self, sig, phase, elapsed):
        conn = sig.conn
        blk = np.zeros(BLOCK)
        for i, p in enumerate(PHASES):
            sb = self.stopbar[p]
            occ = np.mean([conn.lanearea.getLastStepVehicleNumber(ch) > 0 for ch in sb]) if sb else 0.0
            gap = min(GAP_CAP, sig.now - sig.last_actuation.get(p, -1e9)) / GAP_CAP
            n = sum(k for _, k in self.hits[p])
            rate = min(1.5, n / max(1, self.lanes.get(p, 1)) / (RATE_WIN * 0.5))
            blk[i * PER_PHASE:(i + 1) * PER_PHASE] = (occ, gap, rate)
        blk[-2] = elapsed / max(1.0, sig.engine.ph[phase].max_green)
        blk[-1] = 1.0
        x = np.zeros(M)
        k = PHASES.index(phase)
        x[k * BLOCK:(k + 1) * BLOCK] = blk
        return x

    def _reward_rate(self, sig):
        conn = sig.conn
        halted = sum(conn.edge.getLastStepHaltingNumber(e) for e in self.approach_edges)
        return -(halted + len(conn.simulation.getPendingVehicles()))

    # ---- called by SumoSignal every step
    def end_requests(self, sig):
        if not self._init:
            self._e1 = set(sig.conn.inductionloop.getIDList())
            self._setup(sig)
        self._observe_counts(sig)
        dt = sig.conn.simulation.getDeltaT()
        if self.record and self.open:
            r = self._reward_rate(sig) * dt
            for o in self.open.values():
                o[2] += r
        out = set()
        for ring in (1, 2):
            p, mode, el, _ = sig.engine.ring_state(ring)
            if mode != "G" or el < sig.engine.ph[p].min_service() - 1e-9:
                continue
            if sig.now - self.last_dec[ring] < DECISION_S - 1e-9:
                continue
            self.last_dec[ring] = sig.now
            x = self.features(sig, p, el)
            if self.record and ring in self.open:
                x0, a0, r0, t0 = self.open.pop(ring)
                self.X.append(x0); self.A.append(a0); self.R.append(r0); self.X2.append(x); self.D.append(sig.now - t0)
            if self.rng.random() < self.eps:
                a = int(self.rng.integers(2))
            elif self.w is not None:
                a = int(np.argmax(self.w @ x))
            else:
                a = int(ring in self.behaviour.end_requests(sig))
            if self.record:
                self.open[ring] = [x, a, 0.0, sig.now]
            if a == 1:
                out.add(ring)
        return out

    def samples(self):
        """recorded transitions as arrays (open ones at the end are dropped)."""
        if not self.X:
            return None
        return (np.array(self.X), np.array(self.A), np.array(self.R), np.array(self.X2), np.array(self.D))
