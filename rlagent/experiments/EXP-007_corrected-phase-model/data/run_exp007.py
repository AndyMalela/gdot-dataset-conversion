"""EXP-007: RL and Webster on the corrected phase model + extended twin, vs real GDOT timing.

Changes from EXP-005 v6 / EXP-006 (see ../report.md):
  - stages.py: Peachtree lefts (dual lanes, NEMA 1+5) protected-only; every left->through
    transition pays yellow + all-red (as GDOT's controller does). Webster's lost time is
    therefore 28 s (was 18 s).
  - sumo_env: runs on sumotwin/7065_ext.net.xml; upstream edges observed and penalised.
  - RL max greens = the largest green GDOT programs for that movement in any plan
    (split - yellow - red): EW_LEFT 36, EW_THRU 80, NS_LEFT 21, NS_THRU 54 s.
  - Demand: data/demand/<day>.rou.xml (build_demand.py; Oct 2 identical to EXP-005 v6).

  train 2026-09-29 (RL; Webster designed from its busiest hour 15:00-18:00)
  select 2026-09-30 (RL seed with the lowest whole-day delay)
  test  2026-10-02 (unseen by both)

  python3 run_exp007.py webster | real | rl <seeds_dir> | table
"""
import glob
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
E5 = os.path.abspath(os.path.join(HERE, "..", "..", "EXP-005_oct2-real-timing", "data"))
sys.path.insert(0, E5)
import run_exp005 as R  # noqa: E402  (adds rlagent/ to the path; SEED 9999, END 30 h)
import run_exp005_v3 as V  # noqa: E402  (periods, by_period, cycle logging)
import run_exp005_v4 as V4  # noqa: E402  (vehicles, served_check, stats)
import run_exp005_v5 as V5  # noqa: E402  (peak_hour_volumes with corrected labels)
import numpy as np  # noqa: E402
import stages as st  # noqa: E402
import sumo_env  # noqa: E402
from lstdq import LinearQ  # noqa: E402

TRAIN, VAL, TEST = "2026-09-29", "2026-09-30", "2026-10-02"
DEM = os.path.join(HERE, "demand")
ROU = {d: os.path.join(DEM, f"{d}.rou.xml") for d in (TRAIN, VAL, TEST)}
NET = os.path.join(R.REPO, "sumotwin", "7065_ext.net.xml")
REAL_ADD = os.path.join(E5, "real_timing_7065_v6_ext.add.xml")
MAXG = [36, 80, 21, 54]
FEATURES = "pg_glob_rate"
assert sumo_env.NET == NET, "sumo_env must run on the extended twin"


def summarise(ti, rou, logs):
    dem = V4.vehicles(rou)
    res = V.by_period(ti)
    res["unserved_day"] = len(dem) - sum(1 for _ in ET.parse(ti).getroot().iter("tripinfo"))
    res["cycle_s"] = V.mean_cycles(V.CYCLE_STARTS) if logs else V.real_cycles()
    res["served_vs_counted"] = V4.served_check(ti, dem)
    res.update(V4.stats(ti))
    return res


def line(name, res):
    return f"{name[:34]:34s} " + "  ".join(f"{n.split()[0]} {res[n]['total_delay_s']}" for n, _, _ in V.PERIODS) \
        + f"  unserved {res['unserved_day']}"


def webster():
    R.fixed_time.peak_hour_volumes = V5.peak_hour_volumes
    cycle, rho, greens = R.fixed_time.webster_plan(TRAIN, R.PEAK_BEGIN, R.PEAK_END)
    plan = {"designed_on": TRAIN, "lost_time_s": R.fixed_time.cycle_lost_time(), "cycle_s": round(cycle, 1),
            "rho": round(rho, 3), "greens_s": [round(greens[i], 1) for i in range(st.N_PHASES)],
            "design_volumes": {f"{a}_{m}": v for (a, m), v in
                               V5.peak_hour_volumes(TRAIN, R.PEAK_BEGIN, R.PEAK_END).items()}}
    print("Webster", plan, flush=True)
    ti = os.path.join(HERE, "ti_webster.xml")
    V.CYCLE_STARTS.clear()
    R.fixed_time.run_fixed(ROU[TEST], greens, 0, R.END, ti, seed=R.SEED, scale=1.0)
    res = summarise(ti, ROU[TEST], True)
    print(line("Webster", res), flush=True)
    json.dump({"plan": plan, "test": res}, open(os.path.join(HERE, "results_webster.json"), "w"), indent=1)


def real():
    ti = os.path.join(HERE, "ti_real.xml")
    subprocess.run(["sumo", "--net-file", NET, "--route-files", ROU[TEST], "--additional-files", REAL_ADD,
                    "--begin", "0", "--end", str(R.END), "--time-to-teleport", "300", "--seed", str(R.SEED),
                    "--no-step-log", "--duration-log.disable", "--tripinfo-output", ti,
                    "--statistic-output", ti.replace(".xml", "_stats.xml")], check=True, capture_output=True)
    res = summarise(ti, ROU[TEST], False)
    print(line("Real GDOT timing", res), flush=True)
    json.dump({"test": res}, open(os.path.join(HERE, "results_real.json"), "w"), indent=1)


def run_policy(w, rou, ti, label):
    env = sumo_env.Sig7065Env(rou, begin=0, end=R.END, seed=R.SEED, scale=1.0, label=label, tripinfo=ti,
                              feature_mode=FEATURES, enforce_max_green=True, max_greens=MAXG)
    obs = env.reset()
    agent = LinearQ(env.n_state_features, st.N_ACTIONS)
    agent.w = w
    done = False
    V.CYCLE_STARTS.clear()
    while not done:
        r = env.step(agent.greedy(obs), compute_reward=False)
        obs, done = r.state, r.done
    env.close()


def rl(sdir):
    out = {"seeds_dir": sdir, "train_day": TRAIN, "val_day": VAL, "test_day": TEST, "max_greens": MAXG, "seeds": {}}
    for wpath in sorted(glob.glob(os.path.join(HERE, sdir, "s*", "weights_random_s*.npy"))):
        s = os.path.basename(os.path.dirname(wpath))
        w = np.load(wpath)
        vti, tti = (os.path.join(os.path.dirname(wpath), f"ti_{k}.xml") for k in ("val", "test"))
        run_policy(w, ROU[VAL], vti, f"v{s}")
        val = V.by_period(vti)["Whole day"]["total_delay_s"]
        run_policy(w, ROU[TEST], tti, f"t{s}")
        out["seeds"][s] = {"val_whole_day_s": val, "test": summarise(tti, ROU[TEST], True)}
        print(f"{s}: val {val} | " + line("test", out["seeds"][s]["test"]), flush=True)
    out["selected_seed"] = min(out["seeds"], key=lambda k: out["seeds"][k]["val_whole_day_s"])
    print("selected on", VAL, ":", out["selected_seed"], flush=True)
    json.dump(out, open(os.path.join(HERE, f"results_rl_{sdir}.json"), "w"), indent=1)


def table(sdir="seeds"):
    w = json.load(open(os.path.join(HERE, "results_webster.json")))
    r = json.load(open(os.path.join(HERE, "results_real.json")))
    q = json.load(open(os.path.join(HERE, f"results_rl_{sdir}.json")))
    sel = q["seeds"][q["selected_seed"]]["test"]
    rows = [("Real GDOT timing", r["test"]), (f"Webster (designed {TRAIN})", w["test"]),
            (f"RL ({q['selected_seed']}, selected on {VAL})", sel)]
    print("| Controller | " + " | ".join(n for n, _, _ in V.PERIODS) + " | Unserved |")
    print("|---|" + "---|" * (len(V.PERIODS) + 1))
    for name, res in rows:
        print(f"| {name} | " + " | ".join(str(res[n]["total_delay_s"]) for n, _, _ in V.PERIODS)
              + f" | {res['unserved_day']} |")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "webster":
        webster()
    elif cmd == "real":
        real()
    elif cmd == "rl":
        rl(sys.argv[2] if len(sys.argv) > 2 else "seeds")
    elif cmd == "table":
        table(sys.argv[2] if len(sys.argv) > 2 else "seeds")
