"""EXP-005: 7065 on the newer data (2026-10-02) -- RL vs real GDOT timing vs Webster vs
tuned-actuated, one run each, 1.0x (the measured demand, no scaling).

Same for every controller: sumotwin/7065.net.xml, the Oct 2 demand
(intersections/7065/sim/demand.rou.xml: measured 5-min counts per movement), SUMO seed
9999, full day then drain to 30 h, the existing metric (peak 15:00-18:00 total delay =
timeLoss + departDelay by intended departure, EXP-003 peak_delay.py).

  python3 rlagent/experiments/EXP-005_oct2-real-timing/data/run_exp005.py
Writes tripinfos and results.json next to this file (skips controllers already run).
"""
import csv
import hashlib
import json
import os
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
RL = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
REPO = os.path.dirname(RL)
sys.path.insert(0, RL)
sys.path.insert(0, os.path.join(RL, "experiments", "EXP-003_spillback-features", "data"))
import numpy as np  # noqa: E402
import stages as st  # noqa: E402
import fixed_time  # noqa: E402
import actuated_baseline as act  # noqa: E402
from lstdq import LinearQ  # noqa: E402
from sumo_env import Sig7065Env, NET  # noqa: E402
from peak_delay import peak_total_delay, PEAK_BEGIN, PEAK_END  # noqa: E402

DATE = "2026-10-02"
ROU = os.path.join(REPO, "intersections", "7065", "sim", "demand.rou.xml")
TMC = os.path.join(REPO, "intersections", "7065", "counts", "tmc_7065_5min.csv")
REAL = os.path.join(HERE, "real_timing_7065.add.xml")
RL_WEIGHTS = os.path.join(RL, "ci", "race", "ratemg", "s4", "weights_random_s4.npy")
SEED, END = 9999, 108000


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


# --- Webster volumes from the Oct 2 counts (same rolling-hour rule as fixed_time.py) ---
COL = {("eb", "thru"): "EB_T", ("eb", "left"): "EB_L", ("wb", "thru"): "WB_T", ("wb", "left"): "WB_L",
       ("nb", "thru"): "NB_T", ("nb", "left"): "NB_L", ("sb", "thru"): "SB_T", ("sb", "left"): "SB_L"}


def oct2_peak_hour_volumes(date, begin, end):
    rows = [r for r in csv.DictReader(open(TMC)) if r["date"] == DATE]
    bins = {}
    for r in rows:
        t = int(r["time"][:2]) * 3600 + int(r["time"][3:]) * 60
        if begin <= t < end and r["status"] == "ok":
            bins[t] = r
    times = sorted(bins)
    out = {}
    for key, col in COL.items():
        best = 0
        for i in range(len(times) - 11):
            best = max(best, sum(int(bins[times[j]][col]) for j in range(i, i + 12)))
        out[key] = best
    return out


fixed_time.peak_hour_volumes = oct2_peak_hour_volumes      # Webster designed on Oct 2


def realised(tripinfo):
    """peak + whole-day numbers incl. insertion backlog and unserved vehicles."""
    root = ET.parse(tripinfo).getroot()
    pk = {"n": 0, "tl": 0.0, "dd": 0.0}
    day = {"n": 0, "tl": 0.0, "dd": 0.0}
    for ti in root.iter("tripinfo"):
        tl, dd = float(ti.get("timeLoss")), float(ti.get("departDelay"))
        intended = float(ti.get("depart")) - dd
        for acc, ok in ((day, True), (pk, PEAK_BEGIN <= intended < PEAK_END)):
            if ok:
                acc["n"] += 1
                acc["tl"] += tl
                acc["dd"] += dd
    f = lambda a: {"trips": a["n"], "total_delay_s": round((a["tl"] + a["dd"]) / a["n"], 1),
                   "time_loss_s": round(a["tl"] / a["n"], 1), "depart_delay_s": round(a["dd"] / a["n"], 1)}
    return {"peak": f(pk), "day": f(day)}


def demand_total():
    return sum(int(f.get("number")) for f in ET.parse(ROU).getroot().iter("flow"))


def peak_demand_total():
    return sum(int(f.get("number")) for f in ET.parse(ROU).getroot().iter("flow")
               if PEAK_BEGIN <= float(f.get("begin")) < PEAK_END)


# --- controllers ---------------------------------------------------------------------
def run_rl(ti):
    w = np.load(RL_WEIGHTS)
    env = Sig7065Env(ROU, begin=0, end=END, seed=SEED, scale=1.0, label="exp005rl", tripinfo=ti,
                     feature_mode="pg_glob_rate", enforce_max_green=True, max_greens=[15, 92, 30, 70])
    obs = env.reset()
    agent = LinearQ(env.n_state_features, st.N_ACTIONS)
    agent.w = w
    done = False
    while not done:
        r = env.step(agent.greedy(obs), compute_reward=False)
        obs, done = r.state, r.done
    env.close()


def run_real(ti):
    # identical SUMO options to Sig7065Env, plus the real-timing controller (NEMA + time of day)
    cmd = ["sumo", "--net-file", NET, "--route-files", ROU, "--additional-files", REAL,
           "--begin", "0", "--end", str(END), "--time-to-teleport", "300", "--seed", str(SEED),
           "--scale", "1.0", "--no-step-log", "--duration-log.disable", "--no-warnings",
           "--tripinfo-output", ti]
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def main():
    cycle, rho, greens = fixed_time.webster_plan(DATE, PEAK_BEGIN, PEAK_END)
    tuned_max = [max(act.MIN_GREEN_ACT, greens[i] * 1.25) for i in range(st.N_PHASES)]
    info = {"date": DATE, "scale": 1.0, "seed": SEED, "end_s": END,
            "demand_file": os.path.relpath(ROU, REPO), "demand_md5": md5(ROU),
            "demand_vehicles_day": demand_total(), "demand_vehicles_peak": peak_demand_total(),
            "net": os.path.relpath(NET, REPO), "net_md5": md5(NET),
            "webster": {"cycle_s": round(cycle, 1), "rho": round(rho, 3),
                        "greens_s": [round(greens[i], 1) for i in range(st.N_PHASES)],
                        "design_volumes": {f"{a}_{m}": v for (a, m), v in
                                           oct2_peak_hour_volumes(DATE, PEAK_BEGIN, PEAK_END).items()}},
            "tuned_actuated_max_greens_s": [round(g, 1) for g in tuned_max],
            "rl_weights": os.path.relpath(RL_WEIGHTS, REPO), "rl_weights_md5": md5(RL_WEIGHTS),
            "real_timing": os.path.relpath(REAL, REPO), "results": {}}
    runs = [("real GDOT timing (calibrated NEMA)", "real", lambda ti: run_real(ti)),
            ("Webster fixed-time", "webster",
             lambda ti: fixed_time.run_fixed(ROU, greens, 0, END, ti, seed=SEED, scale=1.0)),
            ("tuned-actuated", "tuned_actuated",
             lambda ti: act.run_actuated(ROU, 1.0, ti, seed=SEED, end=END, max_greens=tuned_max)),
            ("RL (EXP-004 deployed, S8 seed 4)", "rl", run_rl)]
    for name, tag, fn in runs:
        ti = os.path.join(HERE, f"ti_{tag}.xml")
        t0 = time.time()
        if not os.path.exists(ti):
            fn(ti)
        r = realised(ti)
        r["wall_s"] = round(time.time() - t0)
        r["unserved_day"] = info["demand_vehicles_day"] - r["day"]["trips"]
        info["results"][name] = r
        print(f"{name:38s} peak total delay {r['peak']['total_delay_s']:7.1f} s  "
              f"(time loss {r['peak']['time_loss_s']}, depart delay {r['peak']['depart_delay_s']}, "
              f"trips {r['peak']['trips']})  unserved {r['unserved_day']}  [{r['wall_s']} s]", flush=True)
        json.dump(info, open(os.path.join(HERE, "results.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
