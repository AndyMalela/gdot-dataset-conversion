"""EXP-006 evaluation: RL retrained on corrected-direction demand.

  train  : 2026-05-07, 05-08, 09-28, 09-29 (random day x scale 0.5-1.6 per episode, 20 episodes/seed)
  select : 2026-09-30 (validation, 1.0x measured demand) -> lowest whole-day total delay
  test   : 2026-10-02 (unseen by RL and by Webster; Webster designed on 09-29)

Reports the validation-selected seed AND the distribution over all seeds, plus real GDOT timing and
Webster (from EXP-005 results_v4/v5, same Oct 2 demand file, md5-checked).

  python3 rlagent/experiments/EXP-006_retrain-corrected-demand/data/eval_exp006.py
"""
import glob
import json
import os
import statistics as stt
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RL = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
E5 = os.path.join(RL, "experiments", "EXP-005_oct2-real-timing", "data")
sys.path.insert(0, RL)
sys.path.insert(0, E5)
import numpy as np  # noqa: E402
import stages as st  # noqa: E402
from lstdq import LinearQ  # noqa: E402
from sumo_env import Sig7065Env  # noqa: E402
import run_exp005 as R  # noqa: E402
import run_exp005_v3 as V  # noqa: E402

DEM = os.path.join(HERE, "demand")
VAL, TEST = "2026-09-30", "2026-10-02"
MAXG = [30, 70, 15, 92]


def run_policy(w, rou, ti, label):
    env = Sig7065Env(rou, begin=0, end=R.END, seed=R.SEED, scale=1.0, label=label, tripinfo=ti,
                     feature_mode="pg_glob_rate", enforce_max_green=True, max_greens=MAXG)
    obs = env.reset()
    agent = LinearQ(env.n_state_features, st.N_ACTIONS)
    agent.w = w
    done = False
    V.CYCLE_STARTS.clear()
    while not done:
        r = env.step(agent.greedy(obs), compute_reward=False)
        obs, done = r.state, r.done
    env.close()
    return V.by_period(ti), V.mean_cycles(V.CYCLE_STARTS)


def main():
    # usage: eval_exp006.py [seeds_dir] [train days, comma-separated]
    sdir = sys.argv[1] if len(sys.argv) > 1 else "seeds"
    days = (sys.argv[2] if len(sys.argv) > 2 else "2026-05-07,2026-05-08,2026-09-28,2026-09-29").split(",")
    out = {"train_days": days, "seeds_dir": sdir, "val_day": VAL,
           "test_day": TEST, "max_greens": MAXG, "seeds": {}}
    for wpath in sorted(glob.glob(os.path.join(HERE, sdir, "s*", "weights_random_s*.npy"))):
        s = os.path.basename(os.path.dirname(wpath))
        w = np.load(wpath)
        vti = os.path.join(os.path.dirname(wpath), "ti_val.xml")
        tti = os.path.join(os.path.dirname(wpath), "ti_test.xml")
        val, _ = run_policy(w, os.path.join(DEM, f"{VAL}.rou.xml"), vti, f"v{s}")
        test, cyc = run_policy(w, os.path.join(DEM, f"{TEST}.rou.xml"), tti, f"t{s}")
        out["seeds"][s] = {"val_whole_day_s": val["Whole day"]["total_delay_s"], "test": test, "test_cycle_s": cyc}
        print(f"{s}: val {val['Whole day']['total_delay_s']:7.1f} s | test " +
              "  ".join(f"{n.split()[0]} {test[n]['total_delay_s']}" for n, _, _ in V.PERIODS), flush=True)
    sel = min(out["seeds"], key=lambda k: out["seeds"][k]["val_whole_day_s"])
    out["selected_seed"] = sel
    out["seed_distribution"] = {
        n: {"median": round(stt.median(v["test"][n]["total_delay_s"] for v in out["seeds"].values()), 1),
            "min": min(v["test"][n]["total_delay_s"] for v in out["seeds"].values()),
            "max": max(v["test"][n]["total_delay_s"] for v in out["seeds"].values())}
        for n, _, _ in V.PERIODS}
    v4 = json.load(open(os.path.join(E5, "results_v4.json")))
    v5 = json.load(open(os.path.join(E5, "results_v5.json")))
    assert R.md5(os.path.join(DEM, f"{TEST}.rou.xml")) == v4["demand_md5"], "test demand differs from EXP-005 v4"
    out["baselines"] = {"Real GDOT timing": v4["results"]["Real GDOT timing (calibrated NEMA)"],
                        "Webster (designed 2026-09-29)": v5["results"]["Webster fixed-time (designed Sep 29)"],
                        "webster_plan": v5["webster"]}
    json.dump(out, open(os.path.join(HERE, f"results_{sdir}.json"), "w"), indent=1)
    print(f"selected (validation {VAL}): {sel}", flush=True)


if __name__ == "__main__":
    main()
