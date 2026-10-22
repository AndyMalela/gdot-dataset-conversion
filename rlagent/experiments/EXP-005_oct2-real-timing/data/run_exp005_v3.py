"""EXP-005 v3: same four controllers as v2, now with
  - calibrated driver gap acceptance (impatience = 1.0, from calib_gap.py) for EVERY controller,
  - results per time period (night / AM / midday / PM peak / evening) and the whole day,
  - measured mean cycle length per period for every controller,
  - tuned-actuated retuned for the test day: max greens = Webster greens x m, m chosen from a
    grid by lowest whole-day total delay on Oct 2 (tuned on the test day = strongest version).

  python3 rlagent/experiments/EXP-005_oct2-real-timing/data/run_exp005_v3.py
Writes results_v3.json, ti_*_v3.xml.
"""
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_exp005 as R  # noqa: E402  (paths, Webster-from-Oct-2 patch, controllers)
import stages as st  # noqa: E402
import sumo_env  # noqa: E402

IMPATIENCE = 1.0
PERIODS = [("Night 00-06", 0, 6), ("AM 06-10", 6, 10), ("Midday 10-15", 10, 15),
           ("PM peak 15-18", 15, 18), ("Evening 18-24", 18, 24), ("Whole day", 0, 24)]
TUNE_GRID = (1.25, 1.5, 2.0, 2.5, 3.0)
ROU_CAL = os.path.join(HERE, "demand_oct2_impatience1.rou.xml")


def make_rou():
    s = open(R.ROU).read()
    s = re.sub(r'<vType id="car"[^>]*/>',
               f'<vType id="car" vClass="passenger" sigma="0.5" impatience="{IMPATIENCE}"/>', s, 1)
    open(ROU_CAL, "w").write(s)


# --- cycle logging for the env-driven controllers (Webster, tuned-actuated, RL) -------
CYCLE_STARTS = []
_orig_step = sumo_env.Sig7065Env.step


def _logged_step(self, *a, **k):
    before = self.phase
    r = _orig_step(self, *a, **k)
    if self.phase == 0 and before != 0:                 # back to the first stage = new cycle
        CYCLE_STARTS.append(self._conn.simulation.getTime())
    return r


sumo_env.Sig7065Env.step = _logged_step


def mean_cycles(starts):
    out = {}
    for name, h0, h1 in PERIODS:
        iv = [b - a for a, b in zip(starts, starts[1:]) if h0 * 3600 <= a < h1 * 3600]
        out[name] = round(sum(iv) / len(iv), 1) if iv else None
    return out


def real_cycles():
    """Real timing: cycle of the plan(s) in force (coordinated plans hold their cycle)."""
    plan = json.load(open(os.path.join(R.REPO, "intersections", "7065", "timing", "timing_plan_7065.json")))
    sched = plan["schedule"][R.DATE]
    out = {}
    for name, h0, h1 in PERIODS:
        cyc = set()
        for b in sched:
            s_ = int(b["start"][:2]) * 60 + int(b["start"][3:])
            e_ = int(b["end"][:2]) * 60 + int(b["end"][3:])
            if b["kind"] == "plan" and s_ < h1 * 60 and e_ > h0 * 60 and b["minutes"] >= 30:
                cyc.add(plan["plans"][b["plan"]]["cycle_s"])
        out[name] = "/".join(str(c) for c in sorted(cyc)) + " (plan)" if cyc else None
    return out


def by_period(ti):
    acc = {n: [0, 0.0, 0.0] for n, _, _ in PERIODS}
    for t in ET.parse(ti).getroot().iter("tripinfo"):
        tl, dd = float(t.get("timeLoss")), float(t.get("departDelay"))
        it = float(t.get("depart")) - dd
        for n, h0, h1 in PERIODS:
            if h0 * 3600 <= it < h1 * 3600:
                a = acc[n]
                a[0] += 1
                a[1] += tl
                a[2] += dd
    return {n: {"trips": a[0], "total_delay_s": round((a[1] + a[2]) / a[0], 1),
                "time_loss_s": round(a[1] / a[0], 1), "depart_delay_s": round(a[2] / a[0], 1)}
            for n, a in acc.items() if a[0]}


def demand_by_period():
    c = defaultdict(int)
    for f in ET.parse(ROU_CAL).getroot().iter("flow"):
        h = float(f.get("begin")) / 3600
        for n, h0, h1 in PERIODS:
            if h0 <= h < h1:
                c[n] += int(f.get("number"))
    return {n: round(c[n] / (h1 - h0)) for n, h0, h1 in PERIODS}


def run_real(ti):
    cmd = ["sumo", "--net-file", R.NET, "--route-files", ROU_CAL, "--additional-files", R.REAL,
           "--begin", "0", "--end", str(R.END), "--time-to-teleport", "300", "--seed", str(R.SEED),
           "--scale", "1.0", "--no-step-log", "--duration-log.disable", "--no-warnings",
           "--tripinfo-output", ti, "--collision.action", "warn"]
    p = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return p


def main():
    make_rou()
    R.ROU = ROU_CAL                                      # every controller uses the calibrated demand
    cycle, rho, greens = R.fixed_time.webster_plan(R.DATE, R.PEAK_BEGIN, R.PEAK_END)
    info = {"date": R.DATE, "impatience": IMPATIENCE, "demand_file": os.path.relpath(ROU_CAL, R.REPO),
            "demand_md5": R.md5(ROU_CAL), "demand_veh_per_h": demand_by_period(),
            "webster": {"cycle_s": round(cycle, 1), "rho": round(rho, 3),
                        "greens_s": [round(greens[i], 1) for i in range(st.N_PHASES)]},
            "results": {}}

    # tuned-actuated: pick the multiplier on Webster greens with the lowest whole-day delay
    tune = {}
    for m in TUNE_GRID:
        mx = [max(R.act.MIN_GREEN_ACT, greens[i] * m) for i in range(st.N_PHASES)]
        ti = os.path.join(HERE, f"_ti_tune_m{m}.xml")
        R.act.run_actuated(ROU_CAL, 1.0, ti, seed=R.SEED, end=R.END, max_greens=mx)
        tune[m] = (by_period(ti)["Whole day"]["total_delay_s"], mx)
        os.remove(ti)
        print(f"tuned-actuated x{m}: max greens {[round(g, 1) for g in mx]} -> whole-day delay {tune[m][0]} s",
              flush=True)
    m_best = min(tune, key=lambda k: tune[k][0])
    info["tuned_actuated"] = {"grid": {str(k): v[0] for k, v in tune.items()}, "chosen_multiplier": m_best,
                              "max_greens_s": [round(g, 1) for g in tune[m_best][1]]}

    runs = [("Real GDOT timing (calibrated NEMA)", "real", run_real, None),
            ("Webster fixed-time", "webster",
             lambda ti: R.fixed_time.run_fixed(ROU_CAL, greens, 0, R.END, ti, seed=R.SEED, scale=1.0), True),
            ("Tuned-actuated", "tuned_actuated",
             lambda ti: R.act.run_actuated(ROU_CAL, 1.0, ti, seed=R.SEED, end=R.END,
                                           max_greens=tune[m_best][1]), True),
            ("RL (EXP-004 deployed, S8 seed 4)", "rl", R.run_rl, True)]
    for name, tag, fn, logs_cycles in runs:
        ti = os.path.join(HERE, f"ti_{tag}_v3.xml")
        CYCLE_STARTS.clear()
        fn(ti)
        res = by_period(ti)
        res["unserved_day"] = R.demand_total() - sum(1 for _ in ET.parse(ti).getroot().iter("tripinfo"))
        res["cycle_s"] = mean_cycles(CYCLE_STARTS) if logs_cycles else real_cycles()
        info["results"][name] = res
        print(f"{name:36s} " + "  ".join(f"{n.split()[0]} {res[n]['total_delay_s']}" for n, _, _ in PERIODS if n in res)
              + f"  unserved {res['unserved_day']}", flush=True)
        json.dump(info, open(os.path.join(HERE, "results_v3.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
