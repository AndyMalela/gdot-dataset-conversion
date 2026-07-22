"""Cyclic max-pressure baseline (Varaiya-style), on the same env/cycle.

Max-pressure control is the standard theory-grounded adaptive baseline: it is
provably throughput-optimal (network-stability sense) under acyclic free
phase selection. Our controller class -- like the real SIG#7065 cabinet --
runs a fixed NEMA ring cycle, so this implements the common CYCLIC
adaptation: at each 1 s decision (after min green),

    EXTEND while pressure(current phase) >= max over other phases' pressure,
    else ADVANCE (next phase in the fixed ring order);
    hard max-out at the same per-phase max-green envelope as the
    tuned-actuated baseline and the S8 RL agent ([15, 92, 30, 70]) so every
    controller competes with the SAME capacity envelope.

Pressure(phase) = sum of vehicle counts on the phase's served approach lanes
minus downstream queues; our exit edges are boundary sinks (no downstream
queue can form), so pressure reduces to served-lane queue mass. Weighting by
saturation rate is uniform across movements here (same vehicle class
everywhere), so it drops out of the argmax.

Deterministic; same sim seed as all other evals.

Usage:
  python3 maxpressure_baseline.py                # 5 scales, full day drained
  python3 maxpressure_baseline.py --scales 1.3
"""
from __future__ import annotations

import argparse
import os
import sys

import metrics
import stages as st
from actuated_baseline import phase_lanes
from sumo_env import Sig7065Env

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(
    HERE, "experiments", "EXP-003_spillback-features", "data"))
from peak_delay import peak_total_delay  # noqa: E402

DAY = "0508"
DRAIN_END = 108000
MIN_GREEN_MP = 8.0                    # same floor as the actuated baseline
MAX_GREENS = [15.0, 92.0, 30.0, 70.0]  # same envelope as tuned-actuated / S8


def pressures(conn, lanes_by_phase):
    return [sum(conn.lane.getLastStepVehicleNumber(l) for l in lanes)
            for lanes in lanes_by_phase]


def run_maxpressure(rou, scale, tripinfo, seed=9999, begin=0, end=DRAIN_END):
    env = Sig7065Env(rou, begin=begin, end=end, seed=seed, scale=scale,
                     label=f"mp{scale}", tripinfo=tripinfo)
    env.reset()
    lanes_by_phase = phase_lanes(env._conn)
    done = False
    while not done:
        p = pressures(env._conn, lanes_by_phase)
        cur = env.phase
        if env.phase_elapsed >= MAX_GREENS[cur]:
            action = st.ADVANCE                    # max-out (shared envelope)
        elif (env.phase_elapsed >= MIN_GREEN_MP
              and p[cur] < max(p[i] for i in range(st.N_PHASES) if i != cur)):
            action = st.ADVANCE                    # pressure lost the argmax
        else:
            action = st.EXTEND
        done = env.step(action, compute_reward=False).done
    env.close()
    return metrics.read_tripinfo(tripinfo)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scales", type=float, nargs="+",
                    default=[0.5, 0.8, 1.0, 1.3, 1.8])
    ap.add_argument("--out", default="results/maxpressure")
    args = ap.parse_args()
    outdir = os.path.join(HERE, args.out)
    os.makedirs(outdir, exist_ok=True)
    rou = os.path.join(HERE, "..", "sumodemand", f"{DAY}.rou.xml")

    print(f"Cyclic max-pressure (min {MIN_GREEN_MP}s, maxes {MAX_GREENS}) "
          f"-- day {DAY}, full day drained")
    for s in args.scales:
        ti = os.path.join(outdir, f"ti_maxpressure_x{s}.xml")
        if not os.path.exists(ti):
            m = run_maxpressure(rou, s, ti)
        else:
            m = metrics.read_tripinfo(ti)
        n_peak, pk = peak_total_delay(ti)
        print(f"  x{s}: {m.row()}")
        print(f"        PEAK(15-18h) total delay = {pk:.0f} s (n={n_peak})",
              flush=True)


if __name__ == "__main__":
    main()
