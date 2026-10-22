"""EXP-005 v5: baselines designed on a different day than they are tested on.

v4's Webster plan (and the tuned-actuated settings derived from it) were designed from Oct 2's
own counts and tested on Oct 2 -- same-day foresight. Here:
  - DESIGN day = Tue 2026-09-29 (complete weekday, no outage bins): Webster from its busiest hour
    in 15:00-18:00 (correct direction mapping); tuned-actuated multiplier chosen by simulating
    Sep 29 demand (built with the same tools/build_sim.py rules: corrected labels, Poisson
    arrivals, seed 12345).
  - TEST day = Fri 2026-10-02 (unseen by both): the frozen v4 demand.
Real timing (GDOT's own plans) and RL (trained on May) are unchanged; their v4 results are copied.

  python3 rlagent/experiments/EXP-005_oct2-real-timing/data/run_exp005_v5.py
"""
import csv
import json
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_exp005 as R  # noqa: E402
import run_exp005_v3 as V  # noqa: E402
import run_exp005_v4 as V4  # noqa: E402
import stages as st  # noqa: E402

sys.path.insert(0, os.path.join(R.REPO, "tools"))
import build_sim as B  # noqa: E402

DESIGN, TEST = "2026-09-29", R.DATE
DDIR = os.path.join(HERE, "design_0929")
ROU_DESIGN = os.path.join(DDIR, "demand.rou.xml")


def peak_hour_volumes(date, begin, end):
    rows = [r for r in csv.DictReader(open(R.TMC)) if r["date"] == date]
    bins = {}
    for r in rows:
        t = int(r["time"][:2]) * 3600 + int(r["time"][3:]) * 60
        if begin <= t < end and r["status"] == "ok":
            bins[t] = r
    times = sorted(bins)
    out = {}
    for key, col in V4.corrected_cols().items():
        out[key] = max((sum(int(bins[times[j]][col]) for j in range(i, i + 12))
                        for i in range(len(times) - 11)), default=0)
    return out


def main():
    # design-day demand (same rules as the test-day demand)
    os.makedirs(DDIR, exist_ok=True)
    d = B.load("7065")
    net = B.sumolib.net.readNet(str(d["net_path"]))
    from pathlib import Path
    B.build_demand("7065", d, DESIGN, net, Path(DDIR), "poisson")

    R.fixed_time.peak_hour_volumes = peak_hour_volumes
    cycle, rho, greens = R.fixed_time.webster_plan(DESIGN, R.PEAK_BEGIN, R.PEAK_END)
    print(f"Webster designed on {DESIGN}: cycle {cycle:.1f} s, rho {rho:.3f}, "
          f"greens {[round(greens[i], 1) for i in range(st.N_PHASES)]}", flush=True)

    tune = {}
    for m in V.TUNE_GRID:
        mx = [max(R.act.MIN_GREEN_ACT, greens[i] * m) for i in range(st.N_PHASES)]
        ti = os.path.join(DDIR, f"_ti_tune_m{m}.xml")
        R.act.run_actuated(ROU_DESIGN, 1.0, ti, seed=R.SEED, end=R.END, max_greens=mx)
        tune[m] = (V.by_period(ti)["Whole day"]["total_delay_s"], mx)
        os.remove(ti)
        print(f"tuned-actuated x{m} on {DESIGN}: whole-day {tune[m][0]} s", flush=True)
    m_best = min(tune, key=lambda k: tune[k][0])

    v4 = json.load(open(os.path.join(HERE, "results_v4.json")))
    info = {"version": "v5", "design_day": DESIGN, "test_day": TEST,
            "test_demand_file": v4["demand_file"], "demand_veh_per_h": v4["demand_veh_per_h"],
            "webster": {"designed_on": DESIGN, "cycle_s": round(cycle, 1), "rho": round(rho, 3),
                        "greens_s": [round(greens[i], 1) for i in range(st.N_PHASES)],
                        "design_volumes": {f"{a}_{mv}": v for (a, mv), v in
                                           peak_hour_volumes(DESIGN, R.PEAK_BEGIN, R.PEAK_END).items()}},
            "tuned_actuated": {"tuned_on": DESIGN, "grid": {str(k): v[0] for k, v in tune.items()},
                               "chosen_multiplier": m_best,
                               "max_greens_s": [round(g, 1) for g in tune[m_best][1]]},
            "results": {}}
    dem = V4.vehicles(V4.ROU4)
    runs = [("Webster fixed-time (designed Sep 29)", "webster",
             lambda ti: R.fixed_time.run_fixed(V4.ROU4, greens, 0, R.END, ti, seed=R.SEED, scale=1.0)),
            ("Tuned-actuated (tuned Sep 29)", "tuned_actuated",
             lambda ti: R.act.run_actuated(V4.ROU4, 1.0, ti, seed=R.SEED, end=R.END, max_greens=tune[m_best][1]))]
    for name, tag, fn in runs:
        ti = os.path.join(HERE, f"ti_{tag}_v5.xml")
        V.CYCLE_STARTS.clear()
        fn(ti)
        res = V.by_period(ti)
        res["unserved_day"] = len(dem) - sum(1 for _ in ET.parse(ti).getroot().iter("tripinfo"))
        res["cycle_s"] = V.mean_cycles(V.CYCLE_STARTS)
        res["served_vs_counted"] = V4.served_check(ti, dem)
        info["results"][name] = res
        print(f"{name:38s} " + "  ".join(f"{n.split()[0]} {res[n]['total_delay_s']}"
                                         for n, _, _ in V.PERIODS) + f"  unserved {res['unserved_day']}", flush=True)
    for k in ("Real GDOT timing (calibrated NEMA)", "RL (EXP-004 policy, trained on direction-swapped May demand)"):
        info["results"][k] = v4["results"][k]
    json.dump(info, open(os.path.join(HERE, "results_v5.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
