"""EXP-008 evaluation: dual-ring RL policy on 2026-09-30 (validation) and 2026-10-02 (test), same metric,
seed and drain as EXP-007's baselines.   python3 eval_exp008.py <weights.npy> <tag>"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
E7 = os.path.abspath(os.path.join(HERE, "..", "..", "EXP-007_corrected-phase-model", "data"))
sys.path.insert(0, os.path.abspath(os.path.join(E7, "..", "..", "EXP-005_oct2-real-timing", "data")))
sys.path.insert(0, E7)
import run_exp007 as X  # noqa: E402
from dualring_env import DualRingEnv, N_ACTIONS  # noqa: E402
from lstdq import LinearQ  # noqa: E402

w = np.load(sys.argv[1])
tag = sys.argv[2]
out = {"weights": sys.argv[1]}
for day in (X.VAL, X.TEST):
    ti = os.path.join(HERE, f"ti_rl_{tag}_{day}.xml")
    env = DualRingEnv(X.ROU[day], begin=0, end=X.R.END, seed=X.R.SEED, scale=1.0, tripinfo=ti,
                      stats=ti.replace(".xml", "_stats.xml"))
    obs = env.reset()
    ag = LinearQ(env.n_state_features, N_ACTIONS)
    ag.w = w
    done = False
    while not done:
        r = env.step(ag.greedy(obs), compute_reward=False)
        obs, done = r.state, r.done
    X.V.CYCLE_STARTS[:] = env.cycle_starts          # logged at each barrier crossing into group 1
    env.close()
    res = X.summarise(ti, X.ROU[day], True)
    out[day] = res
    print(X.line(f"RL dual ring {day}", res), "| cycle", res["cycle_s"], flush=True)
json.dump(out, open(os.path.join(HERE, f"results_rl_{tag}.json"), "w"), indent=1)
