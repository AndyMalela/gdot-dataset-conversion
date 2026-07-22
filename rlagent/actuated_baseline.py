"""NEMA-style fully-actuated (passage-time / gap-out) baseline.

The real SIG#7065 cabinet is actuated (gap-out records exist in ATSPM), so
pretimed Webster understates the real-world baseline. Until the real ATSPM
phase log is obtained, this implements the paper's own stronger conventional
baseline (Sahachaiseree Appendix A.2, passage-time control) on our twin:

  - local detector per approach lane: 4 m long, 30 m upstream of the stop
    line (paper's exact geometry);
  - after a minimum green of 8 s, green ends ("gaps out") when the time gap
    since the last detector actuation on ANY served lane exceeds 3 s;
  - max-out at MAX_GREEN (30 s, stages.py) -- the bound a real controller
    enforces in hardware;
  - same fixed 4-phase ring-barrier sequence + interstage clearance as every
    other controller here (identical env), so the comparison isolates the
    green-termination logic only.

Deterministic (no training, no seeds beyond the sim seed shared with all
other evals).

Usage:
  python3 actuated_baseline.py                 # all 5 scales, full day drained
  python3 actuated_baseline.py --scales 1.3
"""
from __future__ import annotations

import argparse
import os
import sys

import metrics
import stages as st
from sumo_env import Sig7065Env

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(
    HERE, "experiments", "EXP-003_spillback-features", "data"))
from peak_delay import peak_total_delay  # noqa: E402

DAY = "0508"
DRAIN_END = 108000
# paper Appendix A.2 parameters
DET_FAR, DET_NEAR = 30.0, 26.0   # detector spans 26-30 m upstream of stop line
VEH_LEN = 5.0                    # our fleet's vehicle length (overlap check)
GAP_OUT = 3.0                    # s since last actuation -> terminate green
MIN_GREEN_ACT = 8.0              # s (paper's actuated minimum, not env's 3 s)


def phase_lanes(conn):
    """served in-lanes per phase, from the TLS controlled-link table."""
    links = conn.trafficlight.getControlledLinks(st.TLS_ID)
    move_lanes = {m: {links[i][0][0] for i in idxs if links[i]}
                  for m, idxs in st.LINKS.items()}
    return [sorted(set().union(*(move_lanes[m] for m in moves)))
            for _, moves in st.PHASES]


def detector_hit(conn, lanes) -> bool:
    """any vehicle body overlapping the 26-30 m upstream detector zone?"""
    for ln in lanes:
        L = conn.lane.getLength(ln)
        for vid in conn.lane.getLastStepVehicleIDs(ln):
            pos = conn.vehicle.getLanePosition(vid)   # front bumper
            if (L - DET_FAR) <= pos <= (L - DET_NEAR + VEH_LEN):
                return True
    return False


def run_actuated(rou, scale, tripinfo, seed=9999, begin=0, end=DRAIN_END,
                 max_greens=None):
    """max_greens: per-phase max green (s). None -> uniform stages.MAX_GREEN.
    A real cabinet's TOD max settings are proportioned to demand; the tuned
    variant derives them from the Webster splits (x1.25 headroom) so the
    actuated baseline is not handicapped by a uniform 30 s cap that starves
    the critical movement at high v/c."""
    if max_greens is None:
        max_greens = [st.MAX_GREEN] * st.N_PHASES
    env = Sig7065Env(rou, begin=begin, end=end, seed=seed, scale=scale,
                     label=f"act{scale}", tripinfo=tripinfo)
    env.reset()
    lanes_by_phase = phase_lanes(env._conn)
    last_hit = env._conn.simulation.getTime()   # actuation clock
    done = False
    while not done:
        now = env._conn.simulation.getTime()
        if detector_hit(env._conn, lanes_by_phase[env.phase]):
            last_hit = now
        gap = now - last_hit
        if env.phase_elapsed >= max_greens[env.phase]:
            action = st.ADVANCE                      # max-out
        elif env.phase_elapsed >= MIN_GREEN_ACT and gap > GAP_OUT:
            action = st.ADVANCE                      # gap-out
        else:
            action = st.EXTEND
        res = env.step(action, compute_reward=False)
        if action == st.ADVANCE:
            last_hit = env._conn.simulation.getTime()  # new phase, fresh clock
        done = res.done
    env.close()
    return metrics.read_tripinfo(tripinfo)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--scales", type=float, nargs="+",
                   default=[0.5, 0.8, 1.0, 1.3, 1.8])
    p.add_argument("--out", default="results/actuated")
    p.add_argument("--tuned", action="store_true",
                   help="per-phase max greens from Webster splits x1.25 "
                        "(demand-proportioned TOD maxes) instead of a "
                        "uniform 30 s cap")
    args = p.parse_args()
    outdir = os.path.join(HERE, args.out)
    os.makedirs(outdir, exist_ok=True)
    rou = os.path.join(HERE, "..", "sumodemand", f"{DAY}.rou.xml")

    max_greens = None
    tag = "actuated"
    if args.tuned:
        from fixed_time import webster_plan
        _, _, greens = webster_plan(DAY, 54000, 64800)   # PM-peak design load
        # greens is a {phase_idx: green} dict -- take values in phase order
        # (iterating the dict directly yields the KEYS 0..3, which silently
        # produced max_greens of [8,8,8,8] on the first run -- caught because
        # the result was catastrophically bad).
        max_greens = [max(MIN_GREEN_ACT, greens[i] * 1.25)
                      for i in range(st.N_PHASES)]
        tag = "actuated_tuned"
        print(f"tuned max greens (Webster x1.25): "
              f"{[round(g,1) for g in max_greens]}")

    print(f"Fully-actuated (gap-out {GAP_OUT}s, min {MIN_GREEN_ACT}s, "
          f"max {'per-phase' if args.tuned else st.MAX_GREEN}) "
          f"-- day {DAY}, full day drained")
    for s in args.scales:
        ti = os.path.join(outdir, f"ti_{tag}_x{s}.xml")
        if not os.path.exists(ti):
            m = run_actuated(rou, s, ti, max_greens=max_greens)
        else:
            m = metrics.read_tripinfo(ti)
        n_peak, pk = peak_total_delay(ti)
        print(f"  x{s}: {m.row()}")
        print(f"        PEAK(15-18h) total delay = {pk:.0f} s  (n={n_peak})",
              flush=True)


if __name__ == "__main__":
    main()
