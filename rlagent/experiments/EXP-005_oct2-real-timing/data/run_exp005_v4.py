"""EXP-005 v4: corrected direction mapping + Poisson arrivals + default drivers.

Changes from v3 (see report §2c):
  - Demand: intersections/7065/sim/demand.rou.xml rebuilt by tools/build_sim.py with
      * GDOT's count labels translated to the right approaches (the report's EB/WB = Piedmont,
        NB/SB = Peachtree; verified from detector counts, phase_map.json count_labels),
      * Poisson arrivals: the measured count per movement per 5-min bin at random times (seed 12345),
      * SUMO default driver behaviour (no impatience workaround).
    Frozen copy: demand_oct2_v4.rou.xml.
  - Webster designed from the correctly mapped Oct 2 counts; tuned-actuated from that Webster.
  - Real timing: controller rebuilt on the corrected demand (frozen: real_timing_7065_v4.add.xml).
  - RL: the same EXP-004 policy, trained on May demand WITH THE DIRECTIONS SWAPPED (not retrained).
  - Served vs counted volume per movement per period.

  python3 rlagent/experiments/EXP-005_oct2-real-timing/data/run_exp005_v4.py
"""
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_exp005 as R  # noqa: E402
import run_exp005_v3 as V  # noqa: E402  (cycle logging, periods, real_cycles)
import stages as st  # noqa: E402

SIM = os.path.join(R.REPO, "intersections", "7065", "sim")
ROU4 = os.path.join(HERE, "demand_oct2_v4.rou.xml")
REAL4 = os.path.join(HERE, "real_timing_7065_v4.add.xml")
PM = json.load(open(os.path.join(R.REPO, "intersections", "7065", "timing", "phase_map.json")))
NET_TO_COUNT = {v: k for k, v in PM["count_labels"].items()}     # network approach -> GDOT label


def freeze():
    shutil.copy(os.path.join(SIM, "demand.rou.xml"), ROU4)
    s = open(os.path.join(SIM, "signal.add.xml")).read()
    s = re.sub(r'\s*<timedEvent type="SaveTLSStates"[^>]*/>', "", s)
    s = s.replace('<param key="show-detectors" value="true"/>', '<param key="show-detectors" value="false"/>')
    open(REAL4, "w").write(s)


# Webster: fixed_time.py's keys are the twin's approaches (eb = SW leg = Peachtree from SW, ...);
# take each from the GDOT column that belongs to that approach
def corrected_cols():
    out = {}
    for twin in ("eb", "wb", "nb", "sb"):
        g = NET_TO_COUNT[twin.upper()]
        out[(twin, "thru")], out[(twin, "left")] = f"{g}_T", f"{g}_L"
    return out


def vehicles(rou):
    """(id, depart) of every vehicle in the route file (trips or flows)."""
    root = ET.parse(rou).getroot()
    out = [(t.get("id"), float(t.get("depart"))) for t in root.iter("trip")]
    out += [(t.get("id"), float(t.get("depart"))) for t in root.iter("vehicle")]   # explicit-route files
    for f in root.iter("flow"):
        out += [(f"{f.get('id')}.{i}", float(f.get("begin"))) for i in range(int(f.get("number")))]
    return out


mv = lambda vid: "_".join(vid.split("_")[:2])          # GDOT column name, e.g. "EB_L"


def served_check(ti, dem):
    """per period: counted vehicles per movement vs completed trips (by intended departure)."""
    done = Counter()
    for t in ET.parse(ti).getroot().iter("tripinfo"):
        it = float(t.get("depart")) - float(t.get("departDelay"))
        for n, h0, h1 in V.PERIODS:
            if h0 * 3600 <= it < h1 * 3600:
                done[(n, mv(t.get("id")))] += 1
    want = Counter()
    for vid, dep in dem:
        for n, h0, h1 in V.PERIODS:
            if h0 * 3600 <= dep < h1 * 3600:
                want[(n, mv(vid))] += 1
    return {n: {m: f"{done[(n, m)]}/{want[(n, m)]}" for (n2, m) in sorted(want) if n2 == n}
            for n, _, _ in V.PERIODS}


def run_real(ti):
    cmd = ["sumo", "--net-file", R.NET, "--route-files", ROU4, "--additional-files", REAL4,
           "--begin", "0", "--end", str(R.END), "--time-to-teleport", "300", "--seed", str(R.SEED),
           "--no-step-log", "--duration-log.disable", "--tripinfo-output", ti,
           "--statistic-output", ti.replace(".xml", "_stats.xml")]
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def stats(ti):
    p = ti.replace(".xml", "_stats.xml")
    if not os.path.exists(p):
        return {}
    r = ET.parse(p).getroot()
    return {"teleports": int(r.find("teleports").get("total")), "collisions": int(r.find("safety").get("collisions"))}


def main():
    freeze()
    R.ROU = ROU4
    V.ROU_CAL = ROU4
    R.COL.clear()
    R.COL.update(corrected_cols())
    dem = vehicles(ROU4)
    cycle, rho, greens = R.fixed_time.webster_plan(R.DATE, R.PEAK_BEGIN, R.PEAK_END)
    hours = {n: h1 - h0 for n, h0, h1 in V.PERIODS}
    per = Counter()
    for _, dep in dem:
        for n, h0, h1 in V.PERIODS:
            if h0 * 3600 <= dep < h1 * 3600:
                per[n] += 1
    info = {"date": R.DATE, "version": "v4", "demand_file": os.path.relpath(ROU4, R.REPO),
            "demand_md5": R.md5(ROU4), "demand_vehicles_day": len(dem),
            "demand_veh_per_h": {n: round(per[n] / hours[n]) for n in hours},
            "count_labels": PM["count_labels"],
            "webster": {"cycle_s": round(cycle, 1), "rho": round(rho, 3),
                        "greens_s": [round(greens[i], 1) for i in range(st.N_PHASES)],
                        "design_volumes": {f"{a}_{m}": v for (a, m), v in
                                           R.oct2_peak_hour_volumes(R.DATE, R.PEAK_BEGIN, R.PEAK_END).items()}},
            "results": {}}
    tune = {}
    for m in V.TUNE_GRID:
        mx = [max(R.act.MIN_GREEN_ACT, greens[i] * m) for i in range(st.N_PHASES)]
        ti = os.path.join(HERE, f"_ti_tune4_m{m}.xml")
        R.act.run_actuated(ROU4, 1.0, ti, seed=R.SEED, end=R.END, max_greens=mx)
        tune[m] = (V.by_period(ti)["Whole day"]["total_delay_s"], mx)
        os.remove(ti)
        print(f"tuned-actuated x{m}: whole-day {tune[m][0]} s", flush=True)
    m_best = min(tune, key=lambda k: tune[k][0])
    info["tuned_actuated"] = {"grid": {str(k): v[0] for k, v in tune.items()}, "chosen_multiplier": m_best,
                              "max_greens_s": [round(g, 1) for g in tune[m_best][1]]}
    runs = [("Real GDOT timing (calibrated NEMA)", "real", run_real, False),
            ("Webster fixed-time", "webster",
             lambda ti: R.fixed_time.run_fixed(ROU4, greens, 0, R.END, ti, seed=R.SEED, scale=1.0), True),
            ("Tuned-actuated", "tuned_actuated",
             lambda ti: R.act.run_actuated(ROU4, 1.0, ti, seed=R.SEED, end=R.END, max_greens=tune[m_best][1]), True),
            ("RL (EXP-004 policy, trained on direction-swapped May demand)", "rl", R.run_rl, True)]
    for name, tag, fn, logs in runs:
        ti = os.path.join(HERE, f"ti_{tag}_v4.xml")
        V.CYCLE_STARTS.clear()
        fn(ti)
        res = V.by_period(ti)
        res["unserved_day"] = len(dem) - sum(1 for _ in ET.parse(ti).getroot().iter("tripinfo"))
        res["cycle_s"] = V.mean_cycles(V.CYCLE_STARTS) if logs else V.real_cycles()
        res["served_vs_counted"] = served_check(ti, dem)
        res.update(stats(ti))
        info["results"][name] = res
        print(f"{name[:40]:40s} " + "  ".join(f"{n.split()[0]} {res[n]['total_delay_s']}"
                                             for n, _, _ in V.PERIODS if n in res)
              + f"  unserved {res['unserved_day']}", flush=True)
        json.dump(info, open(os.path.join(HERE, "results_v4.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
