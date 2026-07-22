import os, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import numpy as np, stages as st
from lstdq import LinearQ
from sumo_env import Sig7065Env
sys.path.insert(0, os.path.join(HERE,"experiments","EXP-003_spillback-features","data"))
from peak_delay import peak_total_delay
rou = os.path.join(HERE,"..","sumodemand","0508.rou.xml")
w = np.load(os.path.join(HERE,"ci/race/ratemg/s4/weights_random_s4.npy"))
for scale in (1.3, 0.5, 0.8):
    ti = os.path.join(HERE, f"ci/race/ratemg/s4/ti_repro_x{scale}.xml")
    env = Sig7065Env(rou, begin=0, end=108000, seed=9999, scale=scale,
                     label=f"rp{scale}", tripinfo=ti, feature_mode="pg_glob_rate",
                     enforce_max_green=True, max_greens=[15,92,30,70])
    obs = env.reset(); agent = LinearQ(env.n_state_features, st.N_ACTIONS); agent.w = w
    done = False
    while not done:
        r = env.step(agent.greedy(obs), compute_reward=False); obs, done = r.state, r.done
    env.close()
    n, d = peak_total_delay(ti)
    print(f"REPRO x{scale}: peak={d:.1f} s (n={n})", flush=True)
