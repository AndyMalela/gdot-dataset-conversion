"""EXP-005 v6: same as v5 but on the EXTENDED twin (real approach lengths).

The original twin's approaches are far shorter than the real roads (Piedmont S 49 m vs 291 m, Piedmont N
45 m vs 230 m, Peachtree NE 80 m vs 194 m), so long-cycle queues spill out of the network: vehicles
can't enter (inflated depart delay) and enter only 45 m from the stop line during green (lost
capacity). sumotwin/7065_ext.net.xml adds straight upstream segments (S +242 m, N +185 m, NE +114 m;
same lane count as the edge they feed; junction J and its 19 signal links unchanged).

All controllers on the extended twin, same Oct 2 demand (rebuilt on it by tools/build_sim.py: corrected
direction labels, Poisson arrivals seed 12345, default drivers), seed 9999, full day + drain:
  - real GDOT timing: controller recalibrated on the extended twin (median green error 3.5 s)
  - Webster: designed on 2026-09-29 (as v5)
  - RL: the old EXP-004 policy (trained on rotated May demand, short twin) -- reference only
"""
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_exp005 as R  # noqa: E402
import run_exp005_v3 as V  # noqa: E402
import run_exp005_v4 as V4  # noqa: E402
import sumo_env  # noqa: E402
import stages as st  # noqa: E402

NET_EXT = os.path.join(R.REPO, "sumotwin", "7065_ext.net.xml")
SIM = os.path.join(R.REPO, "intersections", "7065", "sim")
ROU6 = os.path.join(HERE, "demand_oct2_v6_ext.rou.xml")
REAL6 = os.path.join(HERE, "real_timing_7065_v6_ext.add.xml")


def freeze():
    shutil.copy(os.path.join(SIM, "demand.rou.xml"), ROU6)
    s = open(os.path.join(SIM, "signal.add.xml")).read()
    s = re.sub(r'\s*<timedEvent type="SaveTLSStates"[^>]*/>', "", s)
    s = s.replace('<param key="show-detectors" value="true"/>', '<param key="show-detectors" value="false"/>')
    open(REAL6, "w").write(s)


def run_real(ti):
    cmd = ["sumo", "--net-file", NET_EXT, "--route-files", ROU6, "--additional-files", REAL6,
           "--begin", "0", "--end", str(R.END), "--time-to-teleport", "300", "--seed", str(R.SEED),
           "--no-step-log", "--duration-log.disable", "--tripinfo-output", ti,
           "--statistic-output", ti.replace(".xml", "_stats.xml")]
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def main():
    freeze()
    sumo_env.NET = NET_EXT            # env-driven controllers (Webster, RL) on the extended twin too
    R.NET = NET_EXT
    v5 = json.load(open(os.path.join(HERE, "results_v5.json")))
    greens = {i: g for i, g in enumerate(v5["webster"]["greens_s"])}
    dem = V4.vehicles(ROU6)
    per = {n: sum(1 for _, d in dem if h0 * 3600 <= d < h1 * 3600) / (h1 - h0) for n, h0, h1 in V.PERIODS}
    info = {"version": "v6", "net": os.path.relpath(NET_EXT, R.REPO), "net_md5": R.md5(NET_EXT),
            "test_day": R.DATE, "demand_file": os.path.relpath(ROU6, R.REPO), "demand_md5": R.md5(ROU6),
            "demand_vehicles_day": len(dem), "demand_veh_per_h": {k: round(v) for k, v in per.items()},
            "webster": v5["webster"], "results": {}}
    runs = [("Real GDOT timing (calibrated NEMA)", "real", run_real, False),
            ("Webster fixed-time (designed Sep 29)", "webster",
             lambda ti: R.fixed_time.run_fixed(ROU6, greens, 0, R.END, ti, seed=R.SEED, scale=1.0), True),
            ("RL (old EXP-004 policy, reference)", "rl", lambda ti: (setattr(R, "ROU", ROU6), R.run_rl(ti)), True)]
    for name, tag, fn, logs in runs:
        ti = os.path.join(HERE, f"ti_{tag}_v6.xml")
        V.CYCLE_STARTS.clear()
        fn(ti)
        res = V.by_period(ti)
        res["unserved_day"] = len(dem) - sum(1 for _ in ET.parse(ti).getroot().iter("tripinfo"))
        res["cycle_s"] = V.mean_cycles(V.CYCLE_STARTS) if logs else V.real_cycles()
        res["served_vs_counted"] = V4.served_check(ti, dem)
        res.update(V4.stats(ti))
        info["results"][name] = res
        print(f"{name[:38]:38s} " + "  ".join(f"{n.split()[0]} {res[n]['total_delay_s']}" for n, _, _ in V.PERIODS)
              + f"  unserved {res['unserved_day']}", flush=True)
        json.dump(info, open(os.path.join(HERE, "results_v6.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
