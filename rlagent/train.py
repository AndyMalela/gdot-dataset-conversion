"""Episodic LSTDQ training, replicating Sahachaiseree's Fig. 2 algorithm.

One epoch = one episode (paper Table 3): collect a full episode of
epsilon-greedy experience, then recompute w in closed form from that
episode's transitions. Warmup transitions (first 300 s) are discarded,
matching the paper's excluded first evaluation period.

Initial replication scope (plan.md Phase 4): single calibrated day,
AM-peak window by default -- generalization/randomization is a later,
separate plan.
"""

from __future__ import annotations

import argparse
import csv
import os
import time

import numpy as np

import metrics
import stages as st
from lstdq import LinearQ
from sumo_env import Sig7065Env

HERE = os.path.dirname(os.path.abspath(__file__))


def run_episode(env: Sig7065Env, agent: LinearQ, eps: float,
                rng: np.random.Generator, skip=None, on_step=None):
    """skip: optional callable(time)->bool marking transitions to exclude
    from the learning batch (on top of warmup) -- used to drop the known
    sensor-outage bins (0505 late night, 0506 early morning), which read a
    false exact-zero and are not genuine demand. They still simulate (empty
    roads, zero reward); they just don't corrupt the fit.
    on_step: optional callable(sim_time) called periodically for progress."""
    obs = env.reset()
    transitions, done = [], False
    tot_reward, n_steps, n_switch = 0.0, 0, 0
    while not done:
        a = agent.act_eps_greedy(obs, eps, rng)
        if a == st.ADVANCE:
            n_switch += 1
        res = env.step(a)
        drop = env.in_warmup(res.time) or (skip is not None and skip(res.time))
        if not drop:
            transitions.append((obs, a, res.reward, res.state, res.duration))
        tot_reward += res.reward
        n_steps += 1
        if on_step is not None and n_steps % 200 == 0:
            on_step(res.time)
        obs, done = res.state, res.done
    env.close()
    return transitions, tot_reward, n_steps, n_switch


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--date", default="0507")
    p.add_argument("--begin", type=int, default=25200)   # 07:00
    p.add_argument("--end", type=int, default=32400)     # 09:00
    p.add_argument("--episodes", type=int, default=20)
    p.add_argument("--eps", type=float, default=0.05)    # paper's LSTDQ pick
    p.add_argument("--gamma", type=float, default=0.9)
    p.add_argument("--ridge", type=float, default=1e-4)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", default="results")
    args = p.parse_args()

    outdir = os.path.join(HERE, args.out)
    os.makedirs(outdir, exist_ok=True)
    rou = os.path.join(HERE, "..", "sumodemand", f"{args.date}.rou.xml")
    rng = np.random.default_rng(args.seed)

    env = Sig7065Env(rou, begin=args.begin, end=args.end,
                     seed=args.seed, label="train")
    env.reset()
    agent = LinearQ(env.n_state_features, st.N_ACTIONS, seed=args.seed)
    env.close()

    log_path = os.path.join(outdir, f"train_{args.date}_s{args.seed}.csv")
    experience = []   # accumulated across episodes (LSPI-style batch reuse):
    # refitting on only the latest episode oscillates at this scale -- each
    # solve then sees 320 params worth of correlated features drawn from a
    # single policy's visitation, and the greedy policy swings episode to
    # episode (observed in runs 1-2; see README "Deviations").
    with open(log_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["episode", "total_reward", "decisions", "switches", "wall_s"])
        for ep in range(1, args.episodes + 1):
            # vary the traffic seed per episode like the paper varies
            # arrival realizations; demand file itself stays fixed
            env.seed = args.seed * 1000 + ep
            t0 = time.time()
            tr, tot_r, n_steps, n_sw = run_episode(env, agent, args.eps, rng)
            experience.extend(tr)
            agent.lstdq_update(experience, gamma=args.gamma, ridge=args.ridge)
            wall = time.time() - t0
            w.writerow([ep, f"{tot_r:.0f}", n_steps, n_sw, f"{wall:.1f}"])
            f.flush()
            print(f"ep {ep:3d}: reward {tot_r:9.0f}  decisions {n_steps:5d}  "
                  f"switches {n_sw:4d}  ({wall:.1f}s)")

    np.save(os.path.join(outdir, f"weights_{args.date}_s{args.seed}.npy"), agent.w)

    # greedy evaluation, exploration off, fresh seed
    ti = os.path.join(outdir, f"tripinfo_rl_{args.date}.xml")
    env = Sig7065Env(rou, begin=args.begin, end=args.end, seed=9999,
                     label="eval", tripinfo=ti)
    obs = env.reset()
    done = False
    while not done:
        res = env.step(agent.greedy(obs))
        obs, done = res.state, res.done
    env.close()
    m = metrics.read_tripinfo(ti)
    print(f"greedy eval: {m.row()}")
    print(f"log: {log_path}")


if __name__ == "__main__":
    main()
