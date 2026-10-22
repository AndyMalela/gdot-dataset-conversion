"""Dual-ring (NEMA 8-phase) RL environment for SIG#7065 -- GDOT's own phase structure.

Replaces the simplified 4-stage single-ring model (stages.py) for EXP-008. Everything about the
signal hardware comes from GDOT's records, shared with the real-timing and Webster controllers:

  phases / movements    intersections/7065/timing/phase_map.json, decoded to the 19 signal links by
                        tools/build_sim.link_phases (identical link states to the real-timing runs)
  ring sequence         Ring 1: P2 -> P1 | P3 -> P4    Ring 2: P5 -> P6 | P7 -> P8
                        (clearance.json lead/lag; '|' = barrier, both rings cross together)
  clearance             measured yellow / red per phase (clearance.json)
  min green (vehicle)   measured per phase (Timing & Actuation 'min green complete')
  max green             largest green GDOT programs for that phase in any plan (split - Y - R)
  pedestrians           ped_min=True: each through phase's green >= Walk 7 s + its crosswalk's
                        Flashing Don't Walk (P2 22.0, P4 29.9, P6 25.2, P8 30.5 s), every cycle
                        (Oct 2 16:00 record: a walk ran every cycle on all four)

Controller behaviour (as a NEMA controller does it):
  - each ring decides independently, every 1 s: EXTEND or ADVANCE its current phase, once past min
    green; max green forces ADVANCE
  - a left-turn phase with no vehicle call (no vehicle within 30 m of its stop line) is skipped
  - the last phase of a ring in a barrier group that wants to end rests in green until the other ring
    is also ready; both then clear together, and the next group starts when both clearances end
  - no coordination with neighbouring signals (RL runs free)

Action = (ring 1, ring 2) in {EXTEND, ADVANCE}^2 -> 4 joint actions (0 EE, 1 EA, 2 AE, 3 AA); the
component for a ring that can't decide this second is ignored.
State (per decision): ring phase one-hots (2 x 4), lane occupancies gated by ring 1's phase and by
ring 2's phase (2 x 4 x lanes), barrier-rest flags (2), per-approach occupancy, insertion backlog and
occupancy change (as sumo_env 'pg_glob_rate').
Reward per second: -(halting vehicles on the approach lanes + vehicles waiting to enter).
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass

import stages as st
from sumo_env import ENTRY_EDGE, NET, QUEUE_SPEED, VEH_SPACING  # noqa: F401

try:
    import libsumo
    _HAS_LIBSUMO = True
except ImportError:
    _HAS_LIBSUMO = False
import traci

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "tools"))
import build_sim as B  # noqa: E402

TLS = "J"
RINGS = {1: ((2, 1), (3, 4)), 2: ((5, 6), (7, 8))}      # ring -> barrier groups -> phases in order
POS = {p: (r, g, i) for r, gs in RINGS.items() for g, ps in enumerate(gs) for i, p in enumerate(ps)}
LEFTS = {1, 3, 5, 7}
THRU = {2, 4, 6, 8}
WALK = 7.0
FDW = {2: 22.0, 4: 29.9, 6: 25.2, 8: 30.5}
MAX_GREEN = {1: 27.7, 2: 79.3, 3: 20.4, 4: 43.4, 5: 35.8, 6: 60.7, 7: 9.8, 8: 53.4}
CALL_DIST = 30.0
EXTEND, ADVANCE = 0, 1
N_ACTIONS = 4


@dataclass
class StepResult:
    state: list
    reward: float
    duration: float
    time: float
    done: bool


APPR_INDEX = {"NB": 0, "SB": 1, "EB": 2, "WB": 3}


def site_layout(site, d, net):
    """(net path, approach edges in state order, edge -> approach index) for a site.
    "7065" = the hand-built twin: exactly the original edge order (stages.APPROACH_EDGES), so trained
    weights and results stay reproducible. Other sites (e.g. "7065osm"): from the site's junction.json,
    each approach's stop-line edge followed by its straight upstream chain up to 500 m."""
    if site == "7065":
        appr = {"S_in": 0, "S_in_ext": 0, "N_near": 1, "N_far": 1, "N_far_ext": 1, "SW_in": 2}
        return NET, list(st.APPROACH_EDGES), lambda e: appr.get(e, 3)
    edges, idx = [], {}
    for a in sorted(d["junction"]["approaches"], key=lambda a: APPR_INDEX[a["label"]]):
        e, total = net.getEdge(a["edge"]), 0.0
        chain = []
        while e is not None and total < 500:
            chain.append(e.getID())
            total += e.getLength()
            preds = [p for p in e.getFromNode().getIncoming() if p.allows("passenger") and p.getID() not in chain]
            if not preds or e.getFromNode().getType().startswith("traffic_light"):
                break
            e = min(preds, key=lambda p: B.ob.angdiff(B.ob.approach_heading(p), B.ob.approach_heading(e)))
            if B.ob.angdiff(B.ob.approach_heading(e), B.ob.approach_heading(net.getEdge(chain[-1]))) > 45:
                break
        for x in chain:
            edges.append(x)
            idx[x] = APPR_INDEX[a["label"]]
    return str(d["net_path"]), edges, lambda e: idx[e]


class _Hw:
    """Signal hardware from GDOT's records (loaded once per site)."""
    def __init__(self, site="7065"):
        d = B.load(site)
        net = B.sumolib.net.readNet(str(d["net_path"]))
        self.tlid, links = B.link_table(site, d, net)
        if site == "7065":
            assert self.tlid == TLS
        self.net_path, self.approach_edges, self.appr_of = site_layout(site, d, net)
        self.n_links = max(links) + 1
        self.lp = B.link_phases(links, d["phase_map"])
        c = d["clearance"]
        self.yellow = {int(k): float(v) for k, v in c["yellow"].items()}
        self.red = {int(k): float(v) for k, v in c["red_clear"].items()}
        assert c["lead"] == {"1/2": 2, "5/6": 5, "3/4": 3, "7/8": 7}, c["lead"]
        self.min_green = {p: v for p, v in B.actuation_params(d, "2026-10-02")["min_green"].items() if p <= 8}
        # signal links whose approaching vehicles call each phase (its protected links)
        self.call_links = {p: {i for i, (prot, _, _) in self.lp.items() if p in prot} for p in range(1, 9)}


class DualRingEnv:
    def __init__(self, rou_xml, begin=0, end=86400, seed=42, scale=1.0, label="dr", tripinfo=None,
                 ped_min=True, warmup=300, drain=0, stats=None, gui=False, gui_settings=None, site="7065"):
        self.rou_xml, self.begin, self.end, self.seed, self.scale = rou_xml, begin, end, seed, scale
        self.label, self.tripinfo, self.ped_min, self.warmup, self.drain = label, tripinfo, ped_min, warmup, drain
        self.stats = stats
        self.gui, self.gui_settings = gui, gui_settings      # watch in sumo-gui (traci; slower)
        self.site = site
        self.hw = _Hw(site)
        self._conn = None
        self._state_cache = {}
        net = B.sumolib.net.readNet(self.hw.net_path)
        self.lanes = [f"{e}_{i}" for e in self.hw.approach_edges for i in range(len(net.getEdge(e).getLanes()))]

    # ---------------------------------------------------------------- setup
    def min_g(self, p):
        m = self.hw.min_green.get(p, 5.0)
        if self.ped_min and p in FDW:
            m = max(m, WALK + FDW[p])
        return m

    @property
    def n_state_features(self):
        return 8 + 2 * 4 * len(self.lanes) + 2 + 2 + 4 + 1 + 4

    def reset(self, rou_xml=None, scale=None, seed=None):
        if rou_xml is not None:
            self.rou_xml = rou_xml
        if scale is not None:
            self.scale = scale
        if seed is not None:
            self.seed = seed
        self.close()
        cmd = ["sumo-gui" if self.gui else "sumo", "--net-file", self.hw.net_path, "--route-files", self.rou_xml, "--begin", str(self.begin),
               "--end", str(self.end + self.drain), "--time-to-teleport", "300", "--seed", str(self.seed),
               "--scale", str(self.scale), "--no-step-log", "--duration-log.disable", "--no-warnings"]
        if self.tripinfo:
            cmd += ["--tripinfo-output", self.tripinfo]
        if self.stats:
            cmd += ["--statistic-output", self.stats]
        if self.gui:
            cmd += ["--start"] + (["--gui-settings-file", self.gui_settings] if self.gui_settings else [])
        if _HAS_LIBSUMO and not self.gui:
            libsumo.start(cmd)
            self._conn = libsumo
        else:
            traci.start(cmd, label=self.label)
            self._conn = traci.getConnection(self.label)
        lane = self._conn.lane
        self.lane_storage = [max(1.0, lane.getLength(l) / VEH_SPACING) for l in self.lanes]
        self.lane_approach = [self.hw.appr_of(l.rsplit("_", 1)[0]) for l in self.lanes]
        self.approach_storage = [sum(s for s, a in zip(self.lane_storage, self.lane_approach) if a == i)
                                 for i in range(4)]
        self._prev_appr = None
        # ring state: phase, mode 'G' green / 'B' resting at barrier (green) / 'C' clearing / 'W' waiting
        self.group = 0
        self.ring = {}
        self.cycle_starts = []
        self._last_state = None
        for r in (1, 2):
            self._start_group_phase(r, first=True)
        self._apply()
        self._run_until_decision(0.0)
        return self._observe()

    def close(self):
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None

    # ---------------------------------------------------------------- ring logic
    def _called(self, p):
        """a vehicle within CALL_DIST of the stop line whose next signal link is one of p's protected
        links (looked up along the route, so short stop-line edges don't shorten the zone)"""
        veh, links = self._conn.vehicle, self.hw.call_links[p]
        for l in self.lanes:
            for v in self._conn.lane.getLastStepVehicleIDs(l):
                for tls, idx, dist, _ in veh.getNextTLS(v)[:1]:
                    if tls == self.hw.tlid and idx in links and dist <= CALL_DIST:
                        return True
        return False

    def _start_group_phase(self, r, first):
        a, b = RINGS[r][self.group]
        if first:
            p = a if (a in THRU or self._conn is None or self._called(a)) else b
        else:
            p = b
        carry = self.ring.get(r, {}).get("carry", {"y": 0.0, "r": 0.0})
        self.ring[r] = {"p": p, "mode": "G", "el": 0.0, "clr": 0.0, "ny": 0, "carry": carry}

    def _begin_clear(self, r, barrier=False):
        s = self.ring[r]
        p, c = s["p"], s["carry"]
        y, rd = self.hw.yellow[p] + c["y"], self.hw.red[p] + c["r"]
        ny, nr = int(round(y)), int(round(rd))
        c["y"], c["r"] = y - ny, rd - nr
        s["mode"], s["ny"], s["clr"], s["ctot"] = "C", ny, float(ny + nr), float(ny + nr)
        if barrier:
            s["barrier"] = True

    def _eligible(self, r):
        s = self.ring[r]
        return s["mode"] == "G" and s["el"] >= self.min_g(s["p"])

    def _advance_ring(self, r):
        s = self.ring[r]
        a, b = RINGS[r][self.group]
        if s["p"] == a and a != b and (b in THRU or self._called(b)):
            self._begin_clear(r)                                                # clear, then b
        else:
            s["mode"] = "B"                                                     # last phase: rest in green

    def _tick(self):
        """1 s of controller time after the action is applied."""
        for r in (1, 2):
            s = self.ring[r]
            if s["mode"] in ("G", "B"):
                s["el"] += 1.0
                if s["mode"] == "G" and s["el"] >= MAX_GREEN[s["p"]] and s["el"] >= self.min_g(s["p"]):
                    self._advance_ring(r)
            elif s["mode"] == "C":
                s["clr"] -= 1.0
                if s["clr"] <= 0:
                    if s.get("barrier"):
                        s["mode"] = "W"
                    else:
                        self._start_group_phase(r, first=False)
        for r in (1, 2):
            s = self.ring[r]
            a, b = RINGS[r][self.group]
            if s["mode"] == "B" and s["p"] == a and b in LEFTS and \
                    self.ring[3 - r]["mode"] != "B" and self._called(b):
                self._begin_clear(r)
        # barrier: both rings resting -> clear together
        if all(self.ring[r]["mode"] == "B" for r in (1, 2)):
            for r in (1, 2):
                self._begin_clear(r, barrier=True)
        if all(self.ring[r]["mode"] == "W" for r in (1, 2)):
            self.group = 1 - self.group
            if self.group == 0 and self._conn is not None:
                self.cycle_starts.append(self._conn.simulation.getTime())      # E8: logged at the barrier
            for r in (1, 2):
                self._start_group_phase(r, first=True)
        self._apply()

    def _apply(self):
        active = []
        for r in (1, 2):
            s = self.ring[r]
            if s["mode"] in ("G", "B"):
                active.append((s["p"], "G"))
            elif s["mode"] == "C":
                active.append((s["p"], "y" if s["ctot"] - s["clr"] < s["ny"] else "r"))
        key = tuple(active)
        state = self._state_cache.get(key)
        if state is None:                       # same rule as before, computed once per combination
            act = dict(active)
            chars = []
            for i in range(self.hw.n_links):
                prot, perm, rtor = self.hw.lp.get(i, (set(), set(), False))
                if any(act.get(p) == "G" for p in prot):
                    c = "G"
                elif any(act.get(p) == "G" for p in perm):
                    c = "g"
                elif any(act.get(p) == "y" for p in prot | perm):
                    c = "y"
                elif rtor and (prot or perm):
                    c = "s"
                else:
                    c = "r"
                chars.append(c)
            state = self._state_cache[key] = "".join(chars)
        if self._conn is not None and state != self._last_state:
            self._conn.trafficlight.setRedYellowGreenState(self.hw.tlid, state)
            self._last_state = state

    def _run_until_decision(self, reward, accumulate=False):
        t0 = self._conn.simulation.getTime()
        while True:
            self._conn.simulationStep()
            if accumulate:
                reward += self._queue_reward()
            self._tick()
            now = self._conn.simulation.getTime()
            if now >= self.end or any(self._eligible(r) for r in (1, 2)):
                return reward, now - t0

    # ---------------------------------------------------------------- RL interface
    def step(self, action, compute_reward=True):
        a1, a2 = (action >> 1) & 1, action & 1
        for r, a in ((1, a1), (2, a2)):
            if a == ADVANCE and self._eligible(r):
                self._advance_ring(r)
        self._apply()
        reward, dur = self._run_until_decision(0.0, accumulate=compute_reward)
        now = self._conn.simulation.getTime()
        done = now >= self.end
        if done and self.drain:
            # let the network drain under a simple fixed policy: advance at max green (no learning)
            while self._conn.simulation.getMinExpectedNumber() > 0 and \
                    self._conn.simulation.getTime() < self.end + self.drain:
                self._conn.simulationStep()
                for r in (1, 2):
                    if self._eligible(r) and self.ring[r]["el"] >= MAX_GREEN[self.ring[r]["p"]]:
                        self._advance_ring(r)
                self._tick()
        return StepResult(self._observe(), reward, dur, now, done)

    def in_warmup(self, t):
        return t < self.begin + self.warmup

    def _queue_reward(self):
        veh, lane = self._conn.vehicle, self._conn.lane
        q = 0
        for l in self.lanes:
            for vid in lane.getLastStepVehicleIDs(l):
                if veh.getSpeed(vid) < QUEUE_SPEED:
                    q += 1
        q += len(self._conn.simulation.getPendingVehicles())
        return -float(q)

    def _observe(self):
        counts = [float(self._conn.lane.getLastStepVehicleNumber(l)) for l in self.lanes]
        occ_l = [min(1.0, c / s) for c, s in zip(counts, self.lane_storage)]
        n = len(self.lanes)
        obs = [0.0] * 8
        for r in (1, 2):
            obs[(r - 1) * 4 + [p for gs in RINGS[r] for p in gs].index(self.ring[r]["p"])] = 1.0
        for r in (1, 2):
            block = [0.0] * (4 * n)
            k = [p for gs in RINGS[r] for p in gs].index(self.ring[r]["p"])
            block[k * n:(k + 1) * n] = occ_l
            obs.extend(block)
        obs.extend(1.0 if self.ring[r]["mode"] == "B" else 0.0 for r in (1, 2))
        obs.extend(1.0 if self.ring[r]["mode"] in ("C", "W") else 0.0 for r in (1, 2))
        appr = [0.0] * 4
        for c, a in zip(counts, self.lane_approach):
            appr[a] += c
        occ = [min(1.0, appr[i] / self.approach_storage[i]) for i in range(4)]
        obs.extend(occ)
        obs.append(min(1.0, len(self._conn.simulation.getPendingVehicles()) / 100.0))
        prev = self._prev_appr if self._prev_appr is not None else occ
        obs.extend(max(-1.0, min(1.0, (occ[i] - prev[i]) * 5.0)) for i in range(4))
        self._prev_appr = occ
        return obs
