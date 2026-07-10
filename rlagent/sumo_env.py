"""SUMO/TraCI environment replicating Sahachaiseree's MDP on the 7065 twin.

State  (paper Eq. 12): one-hot of the active stage (8) + raw vehicle count
        per approach lane (32 lanes across the inbound edge chains) -> 40-dim.
        A vehicle is counted on presence, irrespective of speed.
Action: target stage index in {0..7} (stages.STAGES). Same index as the
        active stage = stage-extension; different = stage-change.
Reward (paper Eq. 13): R = -sum of lane queues over all approach lanes,
        where a vehicle queues if its speed < 5 km/h (1.389 m/s) -- the
        paper's explicit threshold, NOT SUMO's 0.1 m/s halting default.

Transition dynamics (paper Fig. 6, delta < tau + upsilon case):
  - extension: simulate delta (1 s); R_{t+1} and S_{t+1} at the next
    decision point.
  - change: simulate the interstage tau (yellow 4 s + all-red 3 s) and the
    minimum green upsilon (3 s); S_{t+1} at the next decision point.

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
import traci  # noqa: E402

import stages as st  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NET = os.path.join(REPO, "sumotwin", "7065.net.xml")

QUEUE_SPEED = 5.0 / 3.6  # 5 km/h in m/s


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
                 label: str = "env", tripinfo: str | None = None):
        self.rou_xml = rou_xml
        self.begin, self.end, self.warmup = begin, end, warmup
        self.gui, self.seed, self.label = gui, seed, label
        self.tripinfo = tripinfo
        self.lanes: list[str] = []
        self.stage = 0
        self._conn = None

    # -- lifecycle ---------------------------------------------------------

    def reset(self) -> list[float]:
        self.close()
        binary = "sumo-gui" if self.gui else "sumo"
        cmd = [binary, "--net-file", NET, "--route-files", self.rou_xml,
               "--begin", str(self.begin), "--end", str(self.end + 3600),
               "--time-to-teleport", "300", "--seed", str(self.seed),
               "--no-step-log", "--duration-log.disable", "--no-warnings"]
        if self.tripinfo:
            cmd += ["--tripinfo-output", self.tripinfo]
        traci.start(cmd, label=self.label)
        self._conn = traci.getConnection(self.label)
        self.lanes = [
            f"{e}_{i}"
            for e in st.APPROACH_EDGES
            for i in range(self._conn.edge.getLaneNumber(e))
        ]
        self.stage = 0
        self._set_state(st.GREEN_STATE[self.stage])
        # serve the initial stage for one minimum green before first decision
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

    def step(self, action: int) -> StepResult:
        t0 = self._conn.simulation.getTime()
        if action == self.stage:                       # stage extension
            reward = self._advance_accumulating(st.DELTA)
        else:                                          # stage change
            self._set_state(st.YELLOW_STATE[self.stage])
            reward = self._advance_accumulating(st.YELLOW)
            self._set_state(st.ALL_RED_STATE)
            reward += self._advance_accumulating(st.ALL_RED)
            self.stage = action
            self._set_state(st.GREEN_STATE[self.stage])
            reward += self._advance_accumulating(st.MIN_GREEN)
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

    def _advance_accumulating(self, seconds: float) -> float:
        """Advance, summing the queue penalty after every simulated second."""
        total = 0.0
        target = self._conn.simulation.getTime() + seconds
        while self._conn.simulation.getTime() < target:
            self._conn.simulationStep()
            total += self._queue_reward()
        return total

    def _observe(self) -> list[float]:
        obs = [0.0] * st.N_STAGES
        obs[self.stage] = 1.0
        lane = self._conn.lane
        obs.extend(float(lane.getLastStepVehicleNumber(l)) for l in self.lanes)
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
        return st.N_STAGES + len(self.lanes)
