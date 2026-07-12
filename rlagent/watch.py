"""Watch a trained (or fixed-time) controller run in sumo-gui.

Examples:
    python3 watch.py --date 0507                      # trained RL agent
    python3 watch.py --date 0507 --controller fixed    # Webster baseline
    python3 watch.py --date 0507 --begin 0 --end 86400 --delay 50
"""

from __future__ import annotations

import argparse
import os

import numpy as np

import stages as st
from fixed_time import webster_plan
from lstdq import LinearQ
from sumo_env import Sig7065Env

HERE = os.path.dirname(os.path.abspath(__file__))


def watch_rl(rou_xml: str, weights_path: str, begin: int, end: int, seed: int,
             scale: float = 1.0, feature_mode: str = "phase_gated"):
    env = Sig7065Env(rou_xml, begin=begin, end=end, seed=seed, scale=scale,
                     gui=True, label="watch_rl", feature_mode=feature_mode)
    obs = env.reset()
    agent = LinearQ(env.n_state_features, st.N_ACTIONS)
    w = np.load(weights_path)
    expected = env.n_state_features * st.N_ACTIONS
    if w.size != expected:
        raise SystemExit(
            f"weights size {w.size} != {expected} expected for "
            f"feature_mode='{feature_mode}' ({env.n_state_features} feats x "
            f"{st.N_ACTIONS} actions). Pass the matching --feature-mode.")
    agent.w = w
    done = False
    while not done:
        res = env.step(agent.greedy(obs), compute_reward=False)
        obs, done = res.state, res.done
    env.close()


def watch_fixed(rou_xml: str, date: str, begin: int, end: int, seed: int,
                scale: float = 1.0):
    _, _, greens = webster_plan(date, begin, end)
    env = Sig7065Env(rou_xml, begin=begin, end=end, seed=seed, scale=scale,
                     gui=True, label="watch_fixed")
    env.reset()
    done = False
    while not done:
        target = greens[env.phase]
        while not done and env.phase_elapsed < target:
            res = env.step(st.EXTEND, compute_reward=False)
            done = res.done
        if not done:
            res = env.step(st.ADVANCE, compute_reward=False)
            done = res.done
    env.close()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--date", default="0507")
    p.add_argument("--controller", choices=["rl", "fixed"], default="rl")
    p.add_argument("--weights", default=None,
                   help="defaults to results/weights_<date>_s0.npy")
    p.add_argument("--begin", type=int, default=25200)   # 07:00
    p.add_argument("--end", type=int, default=32400)      # 09:00
    p.add_argument("--seed", type=int, default=9999)
    p.add_argument("--scale", type=float, default=1.0,
                   help="demand multiplier (e.g. 1.3, 1.5)")
    p.add_argument("--feature-mode", default="phase_gated",
                   help="must match how the weights were trained: "
                        "flat (exp1), phase_gated (exp2), phase_gated_v3 (exp3)")
    args = p.parse_args()

    rou = os.path.join(HERE, "..", "sumodemand", f"{args.date}.rou.xml")

    if args.controller == "rl":
        weights = args.weights or os.path.join(
            HERE, "results", f"weights_{args.date}_s0.npy")
        print(f"loading {weights}")
        watch_rl(rou, weights, args.begin, args.end, args.seed, args.scale,
                 args.feature_mode)
    else:
        watch_fixed(rou, args.date, args.begin, args.end, args.seed, args.scale)
