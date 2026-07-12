"""SUMO/TraCI environment for the 7065 twin -- realistic ordered-actuated
control (see stages.py for the redesign rationale + regulations.md #8).

State:  one-hot of the active PHASE (4) + per-approach-lane occupancy (32
        lanes), placed in the active phase's block. Several feature_modes
        (see __init__): "flat" (EXP-001), "phase_gated" (EXP-002, raw
        counts), "phase_gated_norm" (EXP-003 ablation: counts normalized to
        occupancy by lane storage), "phase_gated_v3" (EXP-003: normalized
        occupancy + phase-gated elapsed-time). Normalization keeps all
        features ~[0,1] so LSTDQ's least-squares stays well-conditioned and
        the single ridge regularizes every feature evenly (see
        experiments/EXP-003).
Action: binary {EXTEND, ADVANCE} (stages.EXTEND / stages.ADVANCE).
        EXTEND holds the current phase for one decision interval; ADVANCE
        steps to the next phase in the fixed ring-barrier cycle. The agent
        can never reorder or skip -- exactly the freedom a real NEMA
        actuated controller has.
Reward (paper Eq. 13): R = -sum of lane queues over all approach lanes,
        where a vehicle queues if its speed < 5 km/h (1.389 m/s) -- the
        paper's explicit threshold, NOT SUMO's 0.1 m/s halting default.

Transition dynamics:
  - EXTEND: simulate delta (1 s); R and S at the next decision point.
  - ADVANCE: simulate the selective interstage clearance for the
    outgoing->incoming phase (yellow + all-red only on movements that lose
    right-of-way; None -> no interstage when nothing stops, e.g. the
    lead-left->through downgrade) followed by the minimum green upsilon
    (3 s); S at the next decision point. Min green is thus always satisfied
    at every decision point.

SEMI-MDP REWARD (deliberate deviation from the paper's Eq. 13 sampling --
see rlagent/README.md "Deviations"): the reward for a decision is the SUM
of per-second queue snapshots over the decision's whole duration (1 sample
for an extension, ~10 for a change), and the environment reports each
transition's duration so the learner can discount by gamma^duration.
The paper samples the queue ONCE per decision regardless of how much
simulated time the decision consumes. At their scale (4 s interstage, low
volumes) that's benign; here (7 s interstage, near-capacity volumes) it
made switching artificially cheap -- a thrash policy collects ~10x fewer
penalty samples per simulated hour, and the first 20-episode run duly
learned to thrash (best episode return = the episode with the MOST
switches; greedy eval 10x worse than fixed-time). Summing the penalty over
the transition and discounting per unit time restores return proportional
to (negative) vehicle-seconds of queuing, which is the delay objective the
paper's reward was meant to express. This subsumes their "higher penalty at
the start of green" device (all of the interstage queue growth is counted,
not just its endpoint).

Episode = one demand window of one calibrated day (sumodemand/MMDD.rou.xml),
started with empty roads at `begin`; transitions from the first `warmup` s
(default 300, paper's first evaluation period) are flagged so the learner
can drop them.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass

sys.path.append(os.path.join(os.environ.get("SUMO_HOME", "/usr/share/sumo"), "tools"))
import traci  # noqa: E402  (GUI backend, and headless fallback)

# libsumo is a drop-in, in-process replacement for traci (no socket IPC) --
# typically 5-10x faster for headless stepping. Same .simulation/.lane/
# .vehicle/.trafficlight API and .simulationStep()/.close(), but it's a
# process-global singleton (one sim at a time, no connection labels), so it
# is used only for headless runs; GUI (watch.py) still uses traci.
try:
    import libsumo  # noqa: E402
    _HAS_LIBSUMO = True
except Exception:
    _HAS_LIBSUMO = False

import stages as st  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NET = os.path.join(REPO, "sumotwin", "7065.net.xml")

QUEUE_SPEED = 5.0 / 3.6  # 5 km/h in m/s
VEH_SPACING = 7.5        # m per stored vehicle (~5 m veh + 2.5 m gap); used to
                         # normalize lane counts to occupancy in [0,1] (a lane's
                         # storage = length / VEH_SPACING). occupancy per lane is
                         # also the per-lane queue-to-storage ratio -> the
                         # spillback-risk signal, delivered via normalization
                         # rather than as a separate (redundant) feature.


@dataclass
class StepResult:
    state: "list[float]"
    reward: float      # sum of per-second queue penalties over the transition
    duration: float    # simulated seconds this decision consumed
    time: float
    done: bool


class Sig7065Env:
    def __init__(self, rou_xml: str, begin: int = 0, end: int = 86400,
                 warmup: int = 300, gui: bool = False, seed: int = 42,
                 label: str = "env", tripinfo: str | None = None,
                 scale: float = 1.0, feature_mode: str = "phase_gated"):
        # feature_mode:
        #   "flat"        -> [phase one-hot (4), lane counts (32)] = 36-dim
        #                    (EXP-001 baseline; lane weights shared across
        #                    phases -> cannot express phase x lane interaction)
        #   "phase_gated" -> [phase one-hot (4), lane counts placed in the
        #                    active phase's block, zeros elsewhere (4x32)] =
        #                    132-dim. Gives each (action, phase) its own lane
        #                    weights, restoring the action x lane expressiveness
        #                    the paper's stage-selection had (EXP-002 fix B).
        #   "phase_gated_norm" -> EXP-003 ablation: same 132-dim shape, but the
        #                    gated counts are normalized to occupancy in [0,1]
        #                    (count / lane storage). Isolates the effect of
        #                    normalization alone.
        #   "phase_gated_v3" -> EXP-003: phase_gated_norm PLUS a phase-gated
        #                    normalized elapsed-time feature (4) = 136-dim.
        #                    Occupancy adds the spillback-risk signal; elapsed
        #                    time adds commitment/max-green awareness.
        self.rou_xml = rou_xml
        self.feature_mode = feature_mode
        self.lane_storage: list[float] = []
        self.begin, self.end, self.warmup = begin, end, warmup
        self.gui, self.seed, self.label = gui, seed, label
        self.tripinfo = tripinfo
        self.scale = scale
        self.lanes: list[str] = []
        self.phase = 0
        self.phase_elapsed = 0.0
        self._conn = None

    # -- lifecycle ---------------------------------------------------------

    def reset(self, rou_xml: str | None = None, scale: float | None = None,
              seed: int | None = None) -> list[float]:
        """Per-episode overrides (rou_xml/scale/seed) let one env instance
        be reused across a randomized-demand training sampler without
        reconstructing the object each time."""
        if rou_xml is not None:
            self.rou_xml = rou_xml
        if scale is not None:
            self.scale = scale
        if seed is not None:
            self.seed = seed
        self.close()
        binary = "sumo-gui" if self.gui else "sumo"
        cmd = [binary, "--net-file", NET, "--route-files", self.rou_xml,
               "--begin", str(self.begin), "--end", str(self.end + 3600),
               "--time-to-teleport", "300", "--seed", str(self.seed),
               "--scale", str(self.scale),
               "--no-step-log", "--duration-log.disable", "--no-warnings"]
        if self.tripinfo:
            cmd += ["--tripinfo-output", self.tripinfo]
        # headless -> libsumo (in-process, fast); GUI -> traci (labelled).
        if not self.gui and _HAS_LIBSUMO:
            libsumo.start(cmd)
            self._conn = libsumo
        else:
            traci.start(cmd, label=self.label)
            self._conn = traci.getConnection(self.label)
        self.lanes = [
            f"{e}_{i}"
            for e in st.APPROACH_EDGES
            for i in range(self._conn.edge.getLaneNumber(e))
        ]
        # per-lane storage (max stored vehicles) for occupancy normalization
        self.lane_storage = [
            max(1.0, self._conn.lane.getLength(l) / VEH_SPACING) for l in self.lanes
        ]
        self.phase = 0
        self.phase_elapsed = st.MIN_GREEN
        self._set_state(st.GREEN_STATE[self.phase])
        # serve the initial phase for one minimum green before first decision
        self._advance(st.MIN_GREEN)
        return self._observe()

    def close(self):
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None

    # -- core step ---------------------------------------------------------

    def step(self, action: int, compute_reward: bool = True) -> StepResult:
        advance = self._advance_accumulating if compute_reward else self._advance_noreward
        t0 = self._conn.simulation.getTime()
        if action == st.EXTEND:                        # hold current phase
            reward = advance(st.DELTA)
            self.phase_elapsed += st.DELTA
        else:                                          # ADVANCE to next phase
            nxt = (self.phase + 1) % st.N_PHASES
            inter = st.transition(self.phase, nxt)     # selective clearance
            reward = 0.0
            if inter is not None:
                yellow, allred = inter
                self._set_state(yellow)
                reward += advance(st.YELLOW)
                self._set_state(allred)
                reward += advance(st.ALL_RED)
            self.phase = nxt
            self._set_state(st.GREEN_STATE[self.phase])
            reward += advance(st.MIN_GREEN)
            self.phase_elapsed = st.MIN_GREEN
        now = self._conn.simulation.getTime()
        return StepResult(self._observe(), reward, now - t0, now, now >= self.end)

    def in_warmup(self, t: float) -> bool:
        return t < self.begin + self.warmup

    # -- internals ---------------------------------------------------------

    def _set_state(self, ryg: str):
        self._conn.trafficlight.setRedYellowGreenState(st.TLS_ID, ryg)

    def _advance(self, seconds: float):
        target = self._conn.simulation.getTime() + seconds
        while self._conn.simulation.getTime() < target:
            self._conn.simulationStep()

    def _advance_noreward(self, seconds: float) -> float:
        """Like _advance, but keeps the (reward: float) return signature."""
        self._advance(seconds)
        return 0.0

    def _advance_accumulating(self, seconds: float) -> float:
        """Advance, summing the queue penalty after every simulated second."""
        total = 0.0
        target = self._conn.simulation.getTime() + seconds
        while self._conn.simulation.getTime() < target:
            self._conn.simulationStep()
            total += self._queue_reward()
        return total

    def _observe(self) -> list[float]:
        lane = self._conn.lane
        counts = [float(lane.getLastStepVehicleNumber(l)) for l in self.lanes]
        n = len(self.lanes)
        obs = [0.0] * st.N_PHASES          # phase one-hot (per-phase bias)
        obs[self.phase] = 1.0

        if self.feature_mode == "flat":
            obs.extend(counts)             # lane weights shared across phases
            return obs

        # value placed in the active phase's block (phase-gated). Normalized
        # modes use occupancy = count/storage in [0,1]; raw mode uses counts.
        if self.feature_mode == "phase_gated":
            vals = counts
        else:                              # phase_gated_norm / phase_gated_v3
            vals = [min(1.0, c / s) for c, s in zip(counts, self.lane_storage)]
        block = [0.0] * (st.N_PHASES * n)
        base = self.phase * n
        block[base:base + n] = vals
        obs.extend(block)

        if self.feature_mode == "phase_gated_v3":
            # phase-gated normalized elapsed time (commitment / max-green signal)
            el = [0.0] * st.N_PHASES
            el[self.phase] = min(1.0, self.phase_elapsed / st.MAX_GREEN)
            obs.extend(el)
        return obs

    def _queue_reward(self) -> float:
        veh, lane = self._conn.vehicle, self._conn.lane
        q = 0
        for l in self.lanes:
            for vid in lane.getLastStepVehicleIDs(l):
                if veh.getSpeed(vid) < QUEUE_SPEED:
                    q += 1
        return -float(q)

    @property
    def n_state_features(self) -> int:
        if self.feature_mode == "flat":
            return st.N_PHASES + len(self.lanes)
        dim = st.N_PHASES + st.N_PHASES * len(self.lanes)   # onehot + gated block
        if self.feature_mode == "phase_gated_v3":
            dim += st.N_PHASES                              # + phase-gated elapsed
        return dim
