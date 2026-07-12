"""Proper held-out evaluation on 0508 (never trained on): RL vs fixed-time,
over the FULL DAY, at several demand scales, with an end-of-day drain so
metrics aren't truncation-biased.

Two problems with train_random.py's inline eval, both fixed here:
1. Truncation: it stopped stepping at 18:00 while congested, so 30-40% of
   vehicles never completed and were dropped from the tripinfo delay
   average (producing an implausible "more demand, less delay" inversion).
2. Windowing artifact: the .rou.xml flows span the full day, so a
   "15:00-18:00 window" that simply extends its end time to drain actually
   keeps inserting the real 18:00+ demand -- it was never a clean peak
   window. (Confirmed: a "drained" 1.0x run reported 14,243 trips, MORE
   than the 12,322 vehicles in 15:00-18:00, because 18:00-22:00 demand got
   pulled in.)

Full-day eval sidesteps both: begin=0, all of the day's real demand, then
drain past midnight until the network clears so every vehicle is counted.
Fixed-time runs under identical conditions so RL numbers are anchored.
Note the agent was TRAINED on the 15:00-18:00 peak only, so a full-day eval
is also a light-traffic generalization test (it should handle off-peak
trivially).
"""

from __future__ import annotations

import argparse
import os
import re

import numpy as np

import metrics
import stages as st
from fixed_time import run_fixed, webster_plan
from lstdq import LinearQ
from sumo_env import Sig7065Env

HERE = os.path.dirname(os.path.abspath(__file__))
DAY = "0508"
BEGIN = 0
PEAK_BEGIN, PEAK_END = 54000, 64800   # 15:00-18:00
DRAIN_END = 108000                    # run to 30:00 so even scaled peaks clear


def peak_window_rou() -> str:
    """Write a demand file with ONLY the 15:00-18:00 flows, so a peak-regime
    eval can drain cleanly without the full-day flows leaking in past 18:00
    (the artifact that broke the first drained eval). Returns its path."""
    src = os.path.join(HERE, "..", "sumodemand", f"{DAY}.rou.xml")
    dst = os.path.join(HERE, "results", f"_{DAY}_peakwindow.rou.xml")
    out = []
    for line in open(src):
        m = re.search(r'begin="(\d+)"', line)
        if m and "<flow" in line:
            if PEAK_BEGIN <= int(m.group(1)) < PEAK_END:
                out.append(line)
        else:
            out.append(line)   # header, <route>, </routes>
    open(dst, "w").writelines(out)
    return dst


def eval_rl(weights, scale, seed=9999, feature_mode="phase_gated", out="results"):
    ti = os.path.join(HERE, out, f"ti_heldout_rl_x{scale}.xml")
    env = Sig7065Env(rou_path(), begin=BEGIN, end=DRAIN_END, seed=seed,
                     scale=scale, label=f"hrl{scale}", tripinfo=ti,
                     feature_mode=feature_mode)
    obs = env.reset()
    agent = LinearQ(env.n_state_features, st.N_ACTIONS)
    agent.w = weights
    done = False
    while not done:
        res = env.step(agent.greedy(obs))
        obs, done = res.state, res.done
    env.close()
    return metrics.read_tripinfo(ti)


def eval_fixed(scale, seed=9999, out="results"):
    # Webster plan sized from the real PM peak hour (the design load a fixed
    # plan would be timed for), then held all day. (feature_mode irrelevant --
    # fixed-time ignores the agent state.)
    _, _, greens = webster_plan(DAY, PEAK_BEGIN, PEAK_END)
    ti = os.path.join(HERE, out, f"ti_heldout_fixed_x{scale}.xml")
    return run_fixed(rou_path(), greens, BEGIN, DRAIN_END, ti, seed=seed,
                     scale=scale)


def rou_path():
    return os.path.join(HERE, "..", "sumodemand", f"{DAY}.rou.xml")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--weights", default=os.path.join(
        HERE, "results", "weights_random_s0.npy"))
    p.add_argument("--scales", type=float, nargs="+",
                   default=[1.0, 1.3, 1.5])
    p.add_argument("--feature-mode", default="phase_gated",
                   help="must match the mode the weights were trained with")
    p.add_argument("--out", default="results",
                   help="dir (under rlagent/) for tripinfo outputs")
    args = p.parse_args()
    os.makedirs(os.path.join(HERE, args.out), exist_ok=True)
    w = np.load(args.weights)

    print(f"Held-out day {DAY}, FULL DAY drained to {DRAIN_END//3600}:00, "
          f"RL(domain-randomized) vs Webster fixed-time\n")
    print(f"{'scale':>5} | {'controller':<10} | {'thru':>6} | "
          f"{'delay[s]':>9} | {'halts':>6}")
    print("-" * 52)
    for s in args.scales:
        rl = eval_rl(w, s, feature_mode=args.feature_mode, out=args.out)
        fx = eval_fixed(s, out=args.out)
        tag = "in-range" if s <= 1.3 else "extrap"
        d = (rl.avg_delay - fx.avg_delay) / fx.avg_delay * 100
        print(f"{s:>5.1f} | {'RL '+tag:<10} | {rl.n_trips:>6} | "
              f"{rl.avg_delay:>9.2f} | {rl.avg_halts:>6.3f}")
        print(f"{'':>5} | {'fixed-time':<10} | {fx.n_trips:>6} | "
              f"{fx.avg_delay:>9.2f} | {fx.avg_halts:>6.3f}  (RL delay {d:+.1f}%)")
        print("-" * 52)


if __name__ == "__main__":
    main()
