"""Train the linear-FA + LSTDQ agent on the dual-ring (GDOT phase structure) environment (EXP-008).

Same learner as train_random.py (LinearQ, LSTDQ on all experience so far, eps-greedy 0.05,
gamma 0.99 per second, ridge 1e-4, one episode = one full day), 4 joint actions.

  python3 train_dualring.py --demand <day1.rou.xml> [<day2.rou.xml> ...] --episodes 10 --scale 1.0 --seed 0 --out <dir>
"""
import argparse
import csv
import os
import pickle
import time

import numpy as np

from dualring_env import DualRingEnv, N_ACTIONS
from lstdq import LinearQ

p = argparse.ArgumentParser()
p.add_argument("--demand", required=True, nargs="+", help="one or more day files; one is drawn at random per episode")
p.add_argument("--episodes", type=int, default=10)
p.add_argument("--scale", type=float, default=1.0)
p.add_argument("--seed", type=int, default=0)
p.add_argument("--eps", type=float, default=0.05)
p.add_argument("--gamma", type=float, default=0.99)
p.add_argument("--ridge", type=float, default=1e-4)
p.add_argument("--end", type=int, default=86400)
p.add_argument("--no-ped-min", action="store_true")
p.add_argument("--out", required=True)
p.add_argument("--site", default="7065", help="network: 7065 (hand-built twin) or e.g. 7065osm")
a = p.parse_args()
os.makedirs(a.out, exist_ok=True)
rng = np.random.default_rng(a.seed)
env = DualRingEnv(a.demand[0], begin=0, end=a.end, seed=a.seed, scale=a.scale, ped_min=not a.no_ped_min,
                  site=a.site)
agent = LinearQ(env.n_state_features, N_ACTIONS, seed=a.seed)
print(f"features {env.n_state_features}, params {env.n_state_features * N_ACTIONS}, ped_min {env.ped_min}",
      flush=True)
log = open(os.path.join(a.out, f"train_s{a.seed}.csv"), "w", newline="")
w = csv.writer(log)
w.writerow(["episode", "day_file", "scale", "total_reward", "decisions", "wall_s"])
exp = []
for ep in range(1, a.episodes + 1):
    t0 = time.time()
    day = a.demand[int(rng.integers(len(a.demand)))]
    obs = np.asarray(env.reset(rou_xml=day, seed=a.seed * 1000 + ep), dtype=np.float32)
    done, tot, n = False, 0.0, 0
    while not done:
        act = agent.act_eps_greedy(obs, a.eps, rng)
        r = env.step(act)
        nxt = np.asarray(r.state, dtype=np.float32)
        if not env.in_warmup(r.time):
            exp.append((obs, act, r.reward, nxt, r.duration))
        tot += r.reward
        n += 1
        obs, done = nxt, r.done
    env.close()
    agent.lstdq_update(exp, gamma=a.gamma, ridge=a.ridge)
    np.save(os.path.join(a.out, f"weights_s{a.seed}.npy"), agent.w)
    np.save(os.path.join(a.out, f"weights_s{a.seed}_ep{ep}.npy"), agent.w)
    w.writerow([ep, os.path.basename(day), a.scale, f"{tot:.0f}", n, f"{time.time() - t0:.1f}"])
    log.flush()
    print(f"ep {ep}: reward {tot:.3e}  decisions {n}  {time.time() - t0:.0f} s", flush=True)
