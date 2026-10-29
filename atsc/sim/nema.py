"""NEMA dual-ring controller engine: every signal rule, no decisions.

The engine enforces ring order, lead/lag, barriers, minimum greens (incl. pedestrian minimums),
clearances, max greens (free mode) and force-offs (coordinated mode), and skips uncalled phases.
It never decides *when* a green should end on its own: each tick, the caller passes which rings'
policies want to end their current green, and the engine ends it only if the rules allow.

Every controller compared in this project (real GDOT plan, actuated, Webster, MaxPressure, RL) runs
on this engine, so differences in results come from the decision, not from the rules.

Pure Python, no SUMO, so it can be tested on its own (atsc/tests/test_nema.py).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

# mode of a ring
GREEN, REST, CLEAR, WAIT = "G", "B", "C", "W"     # REST = last phase of the group, resting in green


@dataclass
class Phase:
    min_green: float
    yellow: float
    red: float
    ped_min: float = 0.0            # walk + flashing don't walk, served every cycle (ped recall)
    max_green: float = math.inf     # free mode only
    recall: bool = False            # always called (e.g. through phases with ped recall)

    def min_service(self):
        return max(self.min_green, self.ped_min)


@dataclass
class Plan:
    """Coordinated plan: fixed cycle, splits (green + yellow + red), fixed force-offs.
    coordinated phases never gap out; they hold green until their force-off."""
    name: str
    cycle: float
    splits: dict[int, float]
    coordinated: tuple[int, ...] = (2, 6)
    offset: float = 0.0


@dataclass
class GreenRecord:
    phase: int
    start: float
    end: float = math.nan
    how: str = ""                   # gap | max | force | rest-end (ended at barrier after resting)

    @property
    def green(self):
        return self.end - self.start


@dataclass
class _Ring:
    phase: int
    mode: str = GREEN
    start: float = 0.0              # green start (abs time)
    clr_end: float = 0.0
    yellow_end: float = 0.0
    force_off: float = math.inf     # abs time, coordinated mode
    barrier: bool = False
    pending: str = ""               # termination type to log when the green ends


class NemaEngine:
    """rings: {1: ((a, b), (c, d)), 2: (...)} barrier groups in *service order* (lead first).

    tick(now, calls, end_requests) -> per-phase display {phase: 'G'|'y'|'r'} for active phases.
    `calls`: set of phases with a vehicle call (recall phases are added automatically).
    `end_requests`: set of rings whose policy wants to end the current green now.
    """

    def __init__(self, rings, phases: dict[int, Phase], plan: Plan | None = None, skip_uncalled=True):
        self.rings = rings
        self.ph = phases
        self.plan = plan
        self.skip_uncalled = skip_uncalled
        self.group = 0
        self.r: dict[int, _Ring] = {}
        self.greens: list[GreenRecord] = []
        self._open: dict[int, GreenRecord] = {}
        self.calls: set[int] = set()
        self.now = 0.0
        self.cycle_starts: list[float] = []
        self._started = False
        self.plan_provider = None       # callable(now) -> Plan | None, consulted at every cycle start

    # ------------------------------------------------------------------ helpers
    def _called(self, p):
        return p in self.calls or self.ph[p].recall

    def _omitted(self, p):
        """a phase with no time in the current plan (e.g. plan E's split 0 for P3/P7) is never served."""
        return self.plan is not None and self.plan.splits.get(p, 0) <= 0

    def _serve(self, p):
        return not self._omitted(p) and (not self.skip_uncalled or self._called(p))

    def _seq(self, ring):
        return self.rings[ring][self.group]

    def _fo_offset(self, ring, p, group_end=False):
        """cycle-time of p's force-off (fixed force-offs), or of the group end when p is the last
        phase served in its group (the following phase was skipped)."""
        pl = self.plan
        t = 0.0
        for g, seq in enumerate(self.rings[ring]):
            for q in seq:
                t += pl.splits[q]
                if q == p and g == self.group and not group_end:
                    return t - self.ph[p].yellow - self.ph[p].red
            if g == self.group and group_end:
                return t - self.ph[p].yellow - self.ph[p].red
        raise KeyError(p)

    def _next_abs(self, cyc_t, after):
        """first absolute time >= after whose cycle time is cyc_t."""
        pl = self.plan
        k = math.ceil((after - pl.offset - cyc_t) / pl.cycle - 1e-9)
        return pl.offset + cyc_t + k * pl.cycle

    def _set_force_off(self, ring, group_end=False):
        s = self.r[ring]
        if self.plan is None:
            s.force_off = math.inf
            return
        fo = self._fo_offset(ring, s.phase, group_end)
        s.force_off = self._next_abs(fo, s.start + self.ph[s.phase].min_service())

    def _start_green(self, ring, p):
        s = _Ring(phase=p, start=self.now)
        self.r[ring] = s
        self._open[ring] = GreenRecord(p, self.now)
        self._set_force_off(ring)
        self._maybe_last_in_group(ring)

    def _maybe_last_in_group(self, ring):
        """if p is the group's first phase and its partner won't be served, p runs to the group end."""
        s = self.r[ring]
        a, b = self._seq(ring)
        if s.phase == a and a != b and not self._serve(b) and self.plan is not None:
            self._set_force_off(ring, group_end=True)

    def _start_group(self):
        for ring in (1, 2):
            a, b = self._seq(ring)
            if self._omitted(a) or (self._serve(b) and not self._serve(a)):
                self._start_green(ring, b)
            else:
                self._start_green(ring, a)

    def _end_green(self, ring, how, barrier=False):
        s = self.r[ring]
        rec = self._open.pop(ring)
        rec.end, rec.how = self.now, how
        self.greens.append(rec)
        ph = self.ph[s.phase]
        s.mode, s.barrier = CLEAR, barrier
        s.yellow_end = self.now + ph.yellow
        s.clr_end = self.now + ph.yellow + ph.red

    def _min_done(self, s):
        return self.now - s.start >= self.ph[s.phase].min_service() - 1e-9

    def _try_end(self, ring, how):
        """end the current green of `ring`: move to the partner phase, or rest at the barrier."""
        s = self.r[ring]
        a, b = self._seq(ring)
        if s.phase == a and a != b and self._serve(b):
            self._end_green(ring, how)
        elif how in ("force", "max"):
            self._end_green(ring, how, barrier=True)        # terminated: clear now, wait at the barrier in red
        else:
            s.mode, s.pending = REST, how                   # gapped out: rest in green until the other ring is ready

    # ------------------------------------------------------------------ main
    def set_plan(self, plan: Plan | None):
        """takes effect for phases starting from now on (call it at a barrier / cycle boundary)."""
        self.plan = plan

    def tick(self, now, calls=(), end_requests=()):
        self.now = now
        self.calls = set(calls)
        if not self._started:
            self._started = True
            self.cycle_starts.append(now)
            if self.plan_provider:
                self.plan = self.plan_provider(now)
            self._start_group()
            return self.display()

        for ring in (1, 2):
            s = self.r[ring]
            if s.mode == GREEN:
                if self.plan is not None:                    # partner call can appear or drop any time
                    self._set_force_off(ring)
                    self._maybe_last_in_group(ring)
                el = now - s.start
                coord = self.plan is not None and s.phase in self.plan.coordinated
                if now >= s.force_off - 1e-9 and self._min_done(s):
                    self._try_end(ring, "force")
                elif self.plan is None and el >= self.ph[s.phase].max_green - 1e-9 and self._min_done(s):
                    self._try_end(ring, "max")
                elif ring in end_requests and not coord and self._min_done(s):
                    self._try_end(ring, "gap")
            elif s.mode == CLEAR and now >= s.clr_end - 1e-9:
                if s.barrier:
                    s.mode = WAIT
                else:
                    a, b = self._seq(ring)
                    self._start_green(ring, b)
            elif s.mode == REST:
                a, b = self._seq(ring)
                # a late call on the partner left while the other ring is still timing: serve it
                if s.phase == a and a != b and self._serve(b) and self._called(b) and self.r[3 - ring].mode == GREEN:
                    self._end_green(ring, s.pending or "gap")

        # barrier: both rings done with this group (resting in green, or cleared/clearing towards it)
        ready = lambda x: self.r[x].mode in (REST, WAIT) or (self.r[x].mode == CLEAR and self.r[x].barrier)
        if all(ready(x) for x in (1, 2)) and any(self.r[x].mode == REST for x in (1, 2)):
            for x in (1, 2):
                if self.r[x].mode == REST:
                    self._end_green(x, self.r[x].pending or "gap", barrier=True)
        if all(self.r[x].mode == WAIT for x in (1, 2)):
            self.group = 1 - self.group
            if self.group == 0:
                self.cycle_starts.append(now)
                if self.plan_provider:                      # time-of-day plan change at the cycle start
                    self.plan = self.plan_provider(now)
            self._start_group()
        return self.display()

    def display(self):
        out = {}
        for s in self.r.values():
            if s.mode in (GREEN, REST):
                out[s.phase] = "G"
            elif s.mode == CLEAR:
                out[s.phase] = "y" if self.now < s.yellow_end - 1e-9 else "r"
        return out

    def ring_state(self, ring):
        """(phase, mode, green elapsed, seconds to force-off) for policies."""
        s = self.r[ring]
        return s.phase, s.mode, self.now - s.start, s.force_off - self.now
