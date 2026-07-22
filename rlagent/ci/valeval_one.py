import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, stages as st
from lstdq import LinearQ
from sumo_env import Sig7065Env
seed = int(sys.argv[1])
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sdir = os.path.join(HERE, "ci", "race", "ratemg", f"s{seed}")
ti = os.path.join(sdir, "ti_val_0507_x1.3.xml")
if os.path.exists(ti): sys.exit(0)
rou = os.path.join(HERE, "..", "sumodemand", "0507.rou.xml")
env = Sig7065Env(rou, begin=0, end=108000, seed=9999, scale=1.3,
                 label=f"v{seed}", tripinfo=ti, feature_mode="pg_glob_rate",
                 enforce_max_green=True, max_greens=[15,92,30,70])
obs = env.reset()
agent = LinearQ(env.n_state_features, st.N_ACTIONS)
agent.w = np.load(os.path.join(sdir, f"weights_random_s{seed}.npy"))
done = False
while not done:
    r = env.step(agent.greedy(obs), compute_reward=False)
    obs, done = r.state, r.done
env.close()
print(f"s{seed} val done")
