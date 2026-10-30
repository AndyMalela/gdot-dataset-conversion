"""SUMO side of the controller: field detectors in, signal state out, NEMA engine in between.

    sig = SumoSignal(conn, site_dir, net_file, policy=ActuatedPolicy(passage=2.0), mode="plan", day="2026-09-02")
    each simulation step:  conn.simulationStep(); sig.step()

Controllers see only the field-style detectors of atsc/sim/detectors.py (stop-bar presence zones and
setback count loops), never SUMO's vehicle lists.
"""
from __future__ import annotations

import dataclasses
import datetime as dt
import json
import sys
from pathlib import Path

import sumolib

from .nema import NemaEngine, Phase, Plan

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))
import build_sim as B  # noqa: E402  (link_table / link_phases: phase -> signal links, as in EXP-007..009)


# ---------------------------------------------------------------------------- site loading
def load_site(site_dir, net_file):
    site_dir = Path(site_dir)
    sig = json.loads((site_dir / "signal.json").read_text())
    det = json.loads((site_dir / "detectors.json").read_text())
    pm = json.loads((REPO / "intersections" / sig["signal"] / "timing/phase_map.json").read_text())
    junction = json.loads((REPO / "intersections" / f"{sig['signal']}osm" / "network/junction.json").read_text())
    net = sumolib.net.readNet(str(net_file))
    tlid, links = B.link_table(sig["signal"], {"junction": junction}, net)
    assert tlid == sig["tls"], (tlid, sig["tls"])
    lp = B.link_phases(links, pm)
    return sig, det, lp, max(links) + 1


def link_state(display, lp, n_links):
    """per-link SUMO state from the active phases' display (same rule as EXP-007..009)."""
    chars = []
    for i in range(n_links):
        prot, perm, rtor = lp.get(i, (set(), set(), False))
        if any(display.get(p) == "G" for p in prot):
            c = "G"
        elif any(display.get(p) == "G" for p in perm):
            c = "g"
        elif any(display.get(p) == "y" for p in prot | perm):
            c = "y"
        elif rtor and (prot or perm):
            c = "s"
        else:
            c = "r"
        chars.append(c)
    return "".join(chars)


def day_type(date):
    return "saturday" if date.weekday() == 5 else ("sunday" if date.weekday() == 6 else "weekday")


# ---------------------------------------------------------------------------- policies
class FixedPolicy:
    """never asks to end a green: phases run to their force-offs (pretimed, e.g. Webster)."""
    def end_requests(self, sig):
        return set()


class ActuatedPolicy:
    """gap-out: end the green once no detector of the phase has been actuated for its passage time.
    Detectors: the phase's stop-bar presence zones (actuated while occupied) and count zones.
    passage: seconds, one value or {phase: seconds}; max_recall: {plan name: phases that never gap out in
    that plan (they run to their force-off)}, e.g. as inferred from GDOT's Split Monitor (CONTROLLER.md)."""
    def __init__(self, passage=2.0, max_recall=None):
        self.passage = passage
        self.max_recall = {k: set(v) for k, v in (max_recall or {}).items()}

    def _passage(self, p):
        return self.passage.get(p, 2.0) if isinstance(self.passage, dict) else self.passage

    def end_requests(self, sig):
        out = set()
        recall = self.max_recall.get(sig._cur_plan_name, set())
        for ring in (1, 2):
            p, mode, el, _ = sig.engine.ring_state(ring)
            if p in recall:
                continue
            if mode == "G" and sig.now - sig.last_actuation.get(p, -1e9) >= self._passage(p) - 1e-9:
                out.add(ring)
        return out


def actuated_from_site(site_dir):
    """the site's fitted GDOT controller settings (sim.json 'controller'), or plain 2 s gap-out."""
    cal = json.loads((Path(site_dir) / "sim.json").read_text())
    c = cal.get("controller", {})
    return ActuatedPolicy({int(k): v for k, v in c.get("passage_s", {}).items()} or cal.get("passage_s", 2.0),
                          c.get("max_recall"))


# ---------------------------------------------------------------------------- the controller
class SumoSignal:
    def __init__(self, conn, site_dir, net_file, policy, mode="plan", day=None, plan=None,
                 skip_uncalled=True, free_max=None, schedule=None):
        """mode 'plan': GDOT's time-of-day plans for `day` (YYYY-MM-DD); mode 'fixed': one given Plan;
        mode 'schedule': own time-of-day plans, `schedule` = [(start s, Plan)] (e.g. Webster);
        mode 'free': no cycle, max greens `free_max` (default: signal.json max_green_free)."""
        self.conn, self.policy = conn, policy
        self.sig, det, self.lp, self.n_links = load_site(site_dir, net_file)
        self.tls = self.sig["tls"]
        ph = {}
        for k, v in self.sig["phases"].items():
            q = int(k)
            mx = (free_max or {}).get(q, v["max_green_free"])
            ph[q] = Phase(min_green=v["min_green"], yellow=v["yellow"], red=v["red"], ped_min=v["ped_min"],
                          max_green=mx, recall=v["recall"])
        rings = {int(r): tuple(tuple(g) for g in gs) for r, gs in self.sig["rings"].items()}
        self.engine = NemaEngine(rings, ph, None, skip_uncalled=skip_uncalled)
        if mode == "plan":
            self._sched = self._schedule(dt.date.fromisoformat(day))
            self.engine.plan_provider = self._plan_at
        elif mode == "fixed":
            self.engine.plan = plan
        elif mode == "schedule":
            self._own = sorted(schedule, key=lambda x: x[0])
            self.engine.plan_provider = self._own_plan_at
        self._cur_plan_name = None
        # detectors per phase
        self.stopbar, self.setback = {}, {}
        for d in [d for d in det["detectors"] if d.get("modelled", True)]:
            (self.stopbar if d["kind"] == "stopbar" else self.setback).setdefault(d["phase"], []).append(f"ch{d['ch']}")
        self.last_actuation = {}
        self.now = 0.0
        self._last_state = None
        self.plan_log = []              # (time, plan name) at every change

    # ---- time-of-day plans
    def _schedule(self, date):
        from .demand import schedule
        return schedule(self.sig, date)

    def _plan_at(self, now):
        name = None
        for t0, n in self._sched:
            if now >= t0:
                name = n
        name = name or self._sched[0][1]
        if name == self._cur_plan_name:
            return self.engine.plan
        self._cur_plan_name = name
        self.plan_log.append((now, name))
        p = self.sig["plans"][name]
        # the new plan's cycle starts now (real controllers transition over a few cycles; not modelled)
        return Plan(name, p["cycle"], {int(k): v for k, v in p["splits"].items()}, tuple(p["coordinated"]), offset=now)

    def _own_plan_at(self, now):
        cur = [p for t0, p in self._own if t0 <= now][-1:] or [self._own[0][1]]
        p = cur[0]
        if p.name == self._cur_plan_name:
            return self.engine.plan
        self._cur_plan_name = p.name
        self.plan_log.append((now, p.name))
        return Plan(p.name, p.cycle, dict(p.splits), tuple(p.coordinated), offset=now)

    # ---- per step
    def read_detectors(self):
        la, il = self.conn.lanearea, self.conn.inductionloop
        calls = set()
        for p, ids in self.stopbar.items():
            occupied = any(la.getLastStepVehicleNumber(d) > 0 for d in ids)
            if occupied:
                calls.add(p)
                self.last_actuation[p] = self.now
        for p, ids in self.setback.items():
            if any(il.getLastStepVehicleNumber(d) > 0 or il.getLastStepOccupancy(d) > 0 for d in ids):
                self.last_actuation[p] = self.now
        return calls

    def step(self):
        self.now = self.conn.simulation.getTime()
        calls = self.read_detectors()
        ends = self.policy.end_requests(self) if self.engine._started else set()
        disp = self.engine.tick(self.now, calls, ends)
        state = link_state(disp, self.lp, self.n_links)
        if state != self._last_state:
            self.conn.trafficlight.setRedYellowGreenState(self.tls, state)
            self._last_state = state
        return disp

    def greens_table(self):
        return [dataclasses.asdict(g) for g in self.engine.greens]
