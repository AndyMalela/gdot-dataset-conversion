"""EXP-009: significance test of real GDOT timing vs Webster vs dual-ring LSTDQ on held-out days.

One entry point, resumable: finished jobs are skipped, so a re-run after a fix only redoes what changed.

  uv run python matrix.py prepare            # demand replications, real-timing signals per day, Webster plan
  uv run python matrix.py train [--seeds 0-4 --episodes 20]
  uv run python matrix.py run [--only real_nema,webster --force]
  uv run python matrix.py report

Days come from intersections/7065/dataset (README "Proposed split"): weekdays that are complete or usable,
chronological: train Jul 10 - Aug 31 (31), validation Sep 1 - 16 (10), test Sep 17 - Oct 2 (10); Saturdays
(complete) are a separate weekend test. Everything runs on sumotwin/7065_ext.net.xml with the same metric as
EXP-007/008 (total delay = timeLoss + departDelay by intended departure; drain to 30 h).
"""
import argparse
import csv
import json
import multiprocessing as mp
import os
import re
import shutil
import statistics as stt
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RL = HERE.parent.parent
REPO = RL.parent
E5 = RL / "experiments" / "EXP-005_oct2-real-timing" / "data"
E7 = RL / "experiments" / "EXP-007_corrected-phase-model" / "data"
for p in (RL, E5, E7, REPO / "tools"):
    sys.path.insert(0, str(p))

DATA = HERE / "data"
DEM, SIG, RUNS, TRAIN = DATA / "demand", DATA / "signals", DATA / "runs", DATA / "train"
NET = REPO / "sumotwin" / "7065_ext.net.xml"
DAYS_CSV = REPO / "intersections" / "7065" / "dataset" / "days.csv"
SPLIT = {"train": ("2026-07-10", "2026-08-31"), "val": ("2026-09-01", "2026-09-16"),
         "test": ("2026-09-17", "2026-10-02")}
TEST_REPS, SAT_REPS = 10, 3
BASE_SEED, SUMO_SEED, END = 12345, 9999, 108000
ACT_DATE = "2026-10-02"          # day of GDOT's Timing & Actuation records used to calibrate real timing
EXT = (1.0, 8.0)                 # vehicle extension fitted to those records (intersections/7065/sim/README.md)
WALK = 7.0
FDW = {2: 22.0, 4: 29.9, 6: 25.2, 8: 30.5}
PH = {1: ("eb", "left", 2), 2: ("wb", "thru", 3), 3: ("sb", "left", 1), 4: ("nb", "thru", 2),
      5: ("wb", "left", 2), 6: ("eb", "thru", 3), 7: ("nb", "left", 1), 8: ("sb", "thru", 2)}
GROUPS = ({1: (2, 1), 2: (5, 6)}, {1: (3, 4), 2: (7, 8)})
SIGNAL_CTRL = ("real_nema", "real_fixed", "webster")
SITE = "7065"                    # network: "7065" = hand-built twin (sumotwin/7065_ext.net.xml); "7065osm" = OSM


def set_site(site):
    """Point every path / network-dependent constant at a site. "7065" keeps the original layout (data/,
    report.md) so earlier results stay where they are; other sites get data_<site>/, report_<site>.md."""
    global SITE, DATA, DEM, SIG, RUNS, TRAIN, NET, EXT, PH
    import re as _re
    import build_sim as B
    SITE = site
    DATA = HERE / ("data" if site == "7065" else f"data_{site}")
    DEM, SIG, RUNS, TRAIN = DATA / "demand", DATA / "signals", DATA / "runs", DATA / "train"
    d = B.load(site)
    NET = Path(d["net_path"])
    # vehicle extension fitted for this site's real-timing controller (tools/build_sim.py <site>)
    m = _re.search(r"Vehicle extension chosen: \*\*([\d.]+) s through phases, ([\d.]+) s left-turn",
                   (REPO / "intersections" / site / "sim" / "README.md").read_text())
    EXT = (float(m.group(1)), float(m.group(2)))
    # Webster's lanes per phase from the site's own lane use (through = lanes with T, left = lanes with L)
    lanes = {}
    for a in d["junction"]["approaches"]:
        mv = a["lane_moves"]
        lanes[(a["label"].lower(), "thru")] = sum("T" in x for x in mv)
        lanes[(a["label"].lower(), "left")] = sum("L" in x for x in mv)
    ph = {p: (k[0], k[1], lanes[(k[0], k[1])]) for p, k in PH.items()}
    if site == "7065":
        assert ph == PH, (ph, PH)          # derived lanes reproduce the original hard-coded table
    PH = ph


# ----------------------------------------------------------------------------- days
def days():
    rows = list(csv.DictReader(open(DAYS_CSV)))
    good = lambda r: r["quality"] in ("complete", "usable")
    out = {k: [r["date"] for r in rows if r["day_type"] == "weekday" and good(r) and a <= r["date"] <= b]
           for k, (a, b) in SPLIT.items()}
    out["sat"] = [r["date"] for r in rows if r["day_type"] == "saturday" and r["quality"] == "complete"]
    return out


def demand_file(day, rep):
    return DEM / f"{day}_r{rep}.rou.xml"


# ----------------------------------------------------------------------------- prepare
def _demand_job(args):
    day, rep = args
    import build_sim as B
    f = demand_file(day, rep)
    if f.exists():
        return
    d = B.load(SITE)
    net = B.sumolib.net.readNet(str(d["net_path"]))
    with tempfile.TemporaryDirectory() as tmp:
        B.build_demand(SITE, d, day, net, Path(tmp), "poisson", seed=BASE_SEED + rep)
        shutil.move(os.path.join(tmp, "demand.rou.xml"), f)


def _signal_job(day):
    import build_sim as B
    d = B.load(SITE)
    d["actuation"] = B.actuation_params(d, ACT_DATE)
    d["actuation_date"] = ACT_DATE
    net = B.sumolib.net.readNet(str(d["net_path"]))
    for ctrl, kind, ext in (("real_nema", "nema", EXT), ("real_fixed", "fixed", 2.0)):
        f = SIG / f"{ctrl}_{day}.add.xml"
        if f.exists():
            continue
        with tempfile.TemporaryDirectory() as tmp:
            notes = B.build_signal(SITE, d, net, day, Path(tmp), kind, ext)[0]
            s = open(os.path.join(tmp, "signal.add.xml")).read()
        s = re.sub(r'\s*<timedEvent type="SaveTLSStates"[^>]*/>', "", s)
        s = s.replace('<param key="show-detectors" value="true"/>', '<param key="show-detectors" value="false"/>')
        f.write_text(s)
        (SIG / f"{ctrl}_{day}.notes.txt").write_text("\n".join(notes) + "\n")


def webster_plan(train_days):
    """Webster on GDOT's dual ring + pedestrian minimums, designed from the training days: per movement,
    the median over training days of that day's busiest rolling hour in 15:00-18:00."""
    import run_exp005 as R
    import run_exp005_v5 as V5
    import webster_dualring as W
    per = defaultdict(list)
    for day in train_days:
        for k, v in V5.peak_hour_volumes(day, R.PEAK_BEGIN, R.PEAK_END).items():
            per[k].append(v)
    vol = {k: stt.median(v) for k, v in per.items()}
    d = W.B.load(SITE)
    c = d["clearance"]
    yel = {int(k): float(v) for k, v in c["yellow"].items()}
    red = {int(k): float(v) for k, v in c["red_clear"].items()}
    mins = W.B.actuation_params(d, ACT_DATE)["min_green"]
    y = {p: vol[(a, m)] / (1800.0 * n) for p, (a, m, n) in PH.items()}
    lost = {p: yel[p] + red[p] for p in PH}
    crit = []
    for g in GROUPS:
        r = max(g, key=lambda k: sum(y[p] for p in g[k]))
        crit.append((r, sum(y[p] for p in g[r]), sum(lost[p] for p in g[r])))
    Y, L = sum(c_[1] for c_ in crit), sum(c_[2] for c_ in crit)
    C = min(max((1.5 * L + 5) / (1 - Y), 40.0), 180.0)
    green = {}
    for g, (r, yc, _) in zip(GROUPS, crit):
        T = (C - L) * yc / Y + sum(lost[p] for p in g[r])
        for ring, ps in g.items():
            free, ys = T - sum(lost[p] for p in ps), sum(y[p] for p in ps)
            for p in ps:
                green[p] = max(mins.get(p, 5.0), free * y[p] / ys)
    for p, f in FDW.items():                                   # pedestrian minimums every cycle
        green[p] = max(green[p], WALK + f)
    for g in GROUPS:                                          # rings re-balanced to the longer one
        T = max(sum(green[p] + lost[p] for p in ps) for ps in g.values())
        for ps in g.values():
            slack, ys = T - sum(green[p] + lost[p] for p in ps), sum(y[p] for p in ps)
            for p in ps:
                green[p] += slack * y[p] / ys
    splits = {p: green[p] + lost[p] for p in PH}
    cycle, prog = W.write_add(d, splits, yel, red, SIG / "webster.add.xml")
    info = {"design_days": train_days, "design_rule": "median over design days of each day's busiest "
            "rolling hour 15:00-18:00 per movement", "volumes_veh_h": {p: vol[(PH[p][0], PH[p][1])] for p in PH},
            "Y": round(Y, 3), "L_s": round(L, 1), "cycle_formula_s": round(C, 1), "cycle_s": round(cycle, 1),
            "greens_s": {p: round(g_, 1) for p, g_ in sorted(green.items())}}
    (SIG / "webster.json").write_text(json.dumps(info, indent=1))
    return info


def prepare(a):
    D = days()
    for p in (DEM, SIG, RUNS, TRAIN):
        p.mkdir(parents=True, exist_ok=True)
    jobs = [(d, 0) for d in D["train"] + D["val"]] + [(d, r) for d in D["test"] for r in range(TEST_REPS)] \
        + [(d, r) for d in D["sat"] for r in range(SAT_REPS)]
    print(f"days: train {len(D['train'])}, val {len(D['val'])}, test {len(D['test'])}, sat {len(D['sat'])}; "
          f"{len(jobs)} demand files", flush=True)
    with mp.Pool(a.workers) as pool:
        pool.map(_demand_job, jobs)
        pool.map(_signal_job, D["val"] + D["test"] + D["sat"])
    if not (SIG / "webster.add.xml").exists():
        print("Webster:", json.dumps(webster_plan(D["train"])), flush=True)
    print("prepared", flush=True)


# ----------------------------------------------------------------------------- train
def train(a):
    D = days()
    lo, hi = map(int, a.seeds.split("-"))
    files = [str(demand_file(d, 0)) for d in D["train"]]
    procs = []
    for s in range(lo, hi + 1):
        out = TRAIN / f"s{s}"
        if (out / f"weights_s{s}_ep{a.episodes}.npy").exists() and not a.force:
            continue
        out.mkdir(parents=True, exist_ok=True)
        cmd = [sys.executable, str(RL / "train_dualring.py"), "--demand", *files, "--episodes", str(a.episodes),
               "--scale", "1.0", "--seed", str(s), "--out", str(out), "--site", SITE]
        procs.append(subprocess.Popen(cmd, stdout=open(out / "train.log", "w"), stderr=subprocess.STDOUT))
    for p in procs:
        p.wait()
    print(f"trained {len(procs)} seed(s)", flush=True)


# ----------------------------------------------------------------------------- run
def rl_seeds():
    return sorted(int(p.name[1:]) for p in TRAIN.glob("s*") if (p / f"weights_{p.name}.npy").exists())


def _summarise(ti, rou, stats_path):
    import run_exp005_v3 as V
    import run_exp005_v4 as V4
    res = V.by_period(ti)
    dem = V4.vehicles(rou)
    res["unserved_day"] = len(dem) - sum(1 for _ in ET.parse(ti).getroot().iter("tripinfo"))
    st = ET.parse(stats_path).getroot()
    res["teleports"] = int(st.find("teleports").get("total"))
    res["collisions"] = int(st.find("safety").get("collisions"))
    # per movement (GDOT column) per period: vehicles and mean total delay
    mv = defaultdict(lambda: [0, 0.0])
    for t in ET.parse(ti).getroot().iter("tripinfo"):
        dd = float(t.get("departDelay"))
        it = float(t.get("depart")) - dd
        m = "_".join(t.get("id").split("_")[:2])
        for n, h0, h1 in V.PERIODS:
            if h0 * 3600 <= it < h1 * 3600:
                x = mv[f"{n}|{m}"]
                x[0] += 1
                x[1] += float(t.get("timeLoss")) + dd
    res["by_movement"] = {k: {"n": v[0], "total_delay_s": round(v[1] / v[0], 2)} for k, v in mv.items()}
    return res


def _run_job(job):
    ctrl, day, rep = job
    out = RUNS / ctrl / day / f"r{rep}"
    if (out / "summary.json").exists():
        return job, "skip"
    out.mkdir(parents=True, exist_ok=True)
    rou = demand_file(day, rep)
    ti, stats = out / "tripinfo.xml", out / "stats.xml"
    t0 = time.time()
    if ctrl in SIGNAL_CTRL:
        add = SIG / ("webster.add.xml" if ctrl == "webster" else f"{ctrl}_{day}.add.xml")
        cmd = ["sumo", "--net-file", str(NET), "--route-files", str(rou), "--additional-files", str(add),
               "--begin", "0", "--end", str(END), "--time-to-teleport", "300",
               "--seed", str(SUMO_SEED + rep), "--no-step-log", "--duration-log.disable", "--no-warnings",
               "--tripinfo-output", str(ti), "--statistic-output", str(stats)]
        for attempt in range(3):                 # SUMO 1.28 segfaults intermittently; a rerun is deterministic
            r = subprocess.run(cmd, capture_output=True)
            if r.returncode == 0:
                break
            (out / f"crash_{attempt}.txt").write_text(f"exit {r.returncode}\n{r.stderr.decode()[-2000:]}")
        else:
            raise RuntimeError(f"sumo failed 3 times on {job}")
    else:
        import numpy as np
        from dualring_env import DualRingEnv, N_ACTIONS
        from lstdq import LinearQ
        s = ctrl.split("_s")[1]
        w = np.load(TRAIN / f"s{s}" / f"weights_s{s}.npy")
        env = DualRingEnv(str(rou), begin=0, end=END, seed=SUMO_SEED + rep, tripinfo=str(ti), stats=str(stats),
                          site=SITE)
        obs = env.reset()
        ag = LinearQ(env.n_state_features, N_ACTIONS)
        ag.w = w
        done = False
        while not done:
            r = env.step(ag.greedy(obs), compute_reward=False)
            obs, done = r.state, r.done
        env.close()
    res = _summarise(str(ti), str(rou), str(stats))
    res.update({"controller": ctrl, "day": day, "rep": rep, "sumo_seed": SUMO_SEED + rep,
                "demand_seed": BASE_SEED + rep, "wall_s": round(time.time() - t0, 1)})
    (out / "summary.json").write_text(json.dumps(res, indent=1))
    ti.unlink()                                  # tripinfo is large; summary keeps what the report needs
    return job, "ok"


def run(a):
    D = days()
    seeds = rl_seeds()
    ctrls = list(SIGNAL_CTRL) + [f"rl_s{s}" for s in seeds]
    if a.only:
        ctrls = [c for c in ctrls if c in a.only.split(",")]
    jobs = []
    for c in ctrls:
        if c.startswith("rl_"):
            jobs += [(c, d, 0) for d in D["val"]]               # seed selection
        jobs += [(c, d, r) for d in D["test"] for r in range(TEST_REPS)]
        jobs += [(c, d, r) for d in D["sat"] for r in range(SAT_REPS)]
    if a.force:
        for c, d, r in jobs:
            f = RUNS / c / d / f"r{r}" / "summary.json"
            if f.exists():
                f.unlink()
    print(f"{len(jobs)} jobs, {a.workers} workers, controllers {ctrls}", flush=True)
    t0, n = time.time(), 0
    with mp.Pool(a.workers) as pool:
        for job, st in pool.imap_unordered(_run_job, jobs):
            n += 1
            if st == "ok" or n % 50 == 0:
                print(f"[{n}/{len(jobs)}] {job} {st}  {time.time() - t0:.0f}s", flush=True)


# ----------------------------------------------------------------------------- report
def load_runs():
    out = {}
    for f in RUNS.glob("*/*/r*/summary.json"):
        r = json.loads(f.read_text())
        out[(r["controller"], r["day"], r["rep"])] = r
    return out


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, m, prev = [0.0] * len(ps), len(ps), 0.0
    for k, i in enumerate(order):
        prev = max(prev, min(1.0, (m - k) * ps[i]))
        adj[i] = prev
    return adj


def report(a):
    from scipy.stats import wilcoxon
    import run_exp005_v3 as V
    D, R = days(), load_runs()
    seeds = rl_seeds()
    PER = [n for n, _, _ in V.PERIODS]
    val = {s: stt.mean(R[(f"rl_s{s}", d, 0)]["Whole day"]["total_delay_s"] for d in D["val"])
           for s in seeds if all((f"rl_s{s}", d, 0) in R for d in D["val"])}
    best = min(val, key=val.get)
    names = {"real_nema": "Real GDOT timing (actuated)", "real_fixed": "Real GDOT timing (fixed, exact order)",
             "webster": "Webster (dual ring + ped minimums)", f"rl_s{best}": f"LSTDQ dual ring (seed {best}, best on validation)"}
    main = ["real_nema", "webster", f"rl_s{best}"]
    pairs = [(f"rl_s{best}", "webster"), (f"rl_s{best}", "real_nema"), ("webster", "real_nema")]
    L = ["# EXP-009 — significance test: real timing vs Webster vs LSTDQ (SIG 7065)", "",
         f"Generated by `matrix.py report`. Test = {len(D['test'])} weekdays ({D['test'][0]} – {D['test'][-1]}) × "
         f"{TEST_REPS} replications (new arrival draw + SUMO seed each; identical across controllers). "
         "Total delay s/veh (timeLoss + departDelay, by intended departure). "
         "Wilcoxon signed-rank, paired, two-sided, Holm-adjusted over the 3 comparisons, α = 0.05.", "",
         "## RL seed selection (validation weekdays, 1 replication)", "",
         "| Seed | mean whole-day delay |", "|---|---|"]
    L += [f"| {s} | {v:.1f}{' **← selected**' if s == best else ''} |" for s, v in sorted(val.items())]

    def block(day_list, reps, title):
        keys = [(d, r) for d in day_list for r in range(reps)]
        have = [k for k in keys if all((c, *k) in R for c in main + ["real_fixed"])]
        out = [f"## {title} ({len(have)} paired runs)", "",
               "| Controller | " + " | ".join(PER) + " | wins (whole day) |", "|---|" + "---|" * (len(PER) + 1)]
        whole = {c: [R[(c, *k)]["Whole day"]["total_delay_s"] for k in have] for c in main + ["real_fixed"]}
        wins = {c: 0 for c in main}
        for i in range(len(have)):
            wins[min(main, key=lambda c: whole[c][i])] += 1
        for c in main + ["real_fixed"]:
            cells = []
            for p in PER:
                v = [R[(c, *k)][p]["total_delay_s"] for k in have]
                cells.append(f"{stt.mean(v):.1f} ({min(v):.1f}–{max(v):.1f})")
            out.append(f"| {names[c]} | " + " | ".join(cells) + f" | {wins.get(c, '–')} |")
        out += ["", "Mean (min–max) over runs. Wins = runs where that controller had the lowest whole-day delay "
                "among the three main controllers.", "",
                "**Significance — primary test uses one value per day** (the mean of that day's replications), "
                "because replications of the same day are not independent. The run-level p (every replication "
                "as a pair) is shown for reference only.", "",
                "| Comparison | period | mean difference (s/veh) | A better on days | p day-level (Holm) | "
                "significant | p run-level (Holm) |", "|---|---|---|---|---|---|---|"]
        sig = {}
        dlist = sorted({k[0] for k in have})
        for p in PER:
            raw_d, raw_r, rows = [], [], []
            for x, y in pairs:
                dm = [stt.mean(R[(x, d, r)][p]["total_delay_s"] - R[(y, d, r)][p]["total_delay_s"]
                               for (d2, r) in have if d2 == d) for d in dlist]
                dr = [R[(x, *k)][p]["total_delay_s"] - R[(y, *k)][p]["total_delay_s"] for k in have]
                raw_d.append(wilcoxon(dm).pvalue if any(dm) else 1.0)
                raw_r.append(wilcoxon(dr).pvalue if any(dr) else 1.0)
                rows.append((x, y, stt.mean(dr), sum(v < 0 for v in dm)))
            for (x, y, md, nb), pd_, pr_ in zip(rows, holm(raw_d), holm(raw_r)):
                sig[(x, y, p)] = (md, pd_)
                out.append(f"| {names[x]} − {names[y]} | {p} | {md:+.1f} | {nb}/{len(dlist)} | {pd_:.2g} | "
                           f"{'yes' if pd_ < 0.05 else 'no'} | {pr_:.2g} |")
        return out + [""], sig

    b1, sig = block(D["test"], TEST_REPS, "Weekday test")
    b2, _ = block(D["sat"], SAT_REPS, "Saturday test (weekend; separate)")
    L += [""] + b1 + b2
    # per test day + twin capacity check for Piedmont-from-N through (GDOT EB_T, phase P8) under PM plan C
    import run_exp005_v5 as V5
    t = json.loads((REPO / "intersections" / "7065" / "timing" / "timing_plan_7065.json").read_text())
    c8 = t["plans"]["C"]["splits_s"]["8"] - t["clearance"]["yellow"]["8"] - t["clearance"]["red_clear"]["8"]
    gC = c8 / t["plans"]["C"]["cycle_s"]
    WEB_G8 = json.loads((SIG / "webster.json").read_text())["greens_s"]["8"] / json.loads((SIG / "webster.json").read_text())["cycle_s"]
    TWIN_SAT = 1920      # veh/h per lane of green the twin discharges (cyclic queue test, sigma 0.2: 1,920-2,010)
    cap = 2 * TWIN_SAT * gC
    L += ["## Whole-day delay per test day (mean over replications) and twin capacity check", "",
          f"Capacity check: GDOT's PM plan C gives Piedmont-from-N through (P8, 2 lanes) {c8:.1f} s of green per "
          f"{t['plans']['C']['cycle_s']} s. At the twin's discharge rate (about {TWIN_SAT} veh/h per lane of green; "
          f"intersections/7065/timing/capacity_check/README.md) that is about {cap:.0f} veh/h. 'v/c' = that day's "
          "counted PM peak hour / this capacity; above 1 the queue under real timing grows through the PM. The last "
          "column is the resulting PM delay of that movement under real timing (actuated). GDOT's detectors counted "
          "these vehicles passing, so where the twin can't carry them the real-timing number reflects the twin and "
          "the counts (some PM bins look inflated by set-back count detectors), not GDOT's controller.", "",
          "| Day | counted PM peak, Piedmont-N through (veh/h) | v/c at twin capacity | "
          + " | ".join(names[c] for c in main + ["real_fixed"]) + " | real timing PM delay, Piedmont-N through |",
          "|---|---|---|" + "---|" * 5]
    over = []
    for d in D["test"]:
        v = V5.peak_hour_volumes(d, 15 * 3600 + 1800, 19 * 3600)[("sb", "thru")]
        vc = v / cap
        if vc > 1.005:
            over.append(d)
        eb = [R[("real_nema", d, r)]["by_movement"].get("PM peak 15-18|EB_T", {}).get("total_delay_s")
              for r in range(TEST_REPS) if ("real_nema", d, r) in R]
        eb = [x for x in eb if x is not None]
        L.append(f"| {d} | {v} | {vc:.3f}{(' (at capacity)' if vc <= 1.005 else ' **>1**') if vc > 1 else ''} | " + " | ".join(
            f"{stt.mean(R[(c, d, r)]['Whole day']['total_delay_s'] for r in range(TEST_REPS) if (c, d, r) in R):.1f}"
            for c in main + ["real_fixed"]) + (f" | {stt.mean(eb):.0f} |" if eb else " | – |"))
    ok_days = [d for d in D["test"] if d not in over]
    if len(ok_days) >= 5 and len(ok_days) < len(D["test"]):
        bv, _ = block(ok_days, TEST_REPS, f"Weekday test restricted to days within twin capacity ({len(ok_days)} days)")
        L += [""] + bv
    elif len(ok_days) < len(D["test"]):
        L += ["", f"{len(D['test']) - len(ok_days)} of {len(D['test'])} test weekdays exceed the twin's capacity for "
              f"this movement under plan C (within: {', '.join(ok_days) or 'none'}; too few for a separate test). "
              "Real-timing weekday results are therefore NOT evidence about GDOT's controller; use the Saturday block "
              f"for real timing. Webster gives P8 a larger share of a shorter cycle (about v/c "
              f"{max(V5.peak_hour_volumes(d, 15 * 3600 + 1800, 19 * 3600)[('sb', 'thru')] for d in D['test']) / (2 * TWIN_SAT * WEB_G8):.2f} "
              "on the busiest day) and RL adapts, so both are mostly below capacity for this movement (on the "
              "highest-demand day some Webster/RL runs still have isolated teleports); they are compared on the same "
              "counts, so that comparison stays paired and fair."]
    # RL seed spread and robustness, generated from the data
    web = {d: stt.mean(R[("webster", d, r)]["Whole day"]["total_delay_s"] for r in range(TEST_REPS)
                       if ("webster", d, r) in R) for d in D["test"]}
    vrank = {s_: i + 1 for i, s_ in enumerate(sorted(val, key=val.get))}
    L += ["", "## All RL seeds on the weekday test (whole day)", "",
          "| Seed | validation rank | test mean | worst test day | days better than Webster | p vs Webster (day-level, raw) |",
          "|---|---|---|---|---|---|"]
    rows_s = []
    for s_ in seeds:
        dm = {d: stt.mean(R[(f"rl_s{s_}", d, r)]["Whole day"]["total_delay_s"] for r in range(TEST_REPS)
                          if (f"rl_s{s_}", d, r) in R) for d in D["test"]}
        if not dm:
            continue
        wd = max(dm, key=dm.get)
        nb = sum(dm[d] < web[d] for d in D["test"])
        diffs = [dm[d] - web[d] for d in D["test"]]
        pv = wilcoxon(diffs).pvalue if any(diffs) else 1.0
        rows_s.append((s_, stt.mean(dm.values()), nb, pv, [d for d in D["test"] if dm[d] >= web[d]]))
        L.append(f"| {s_}{' (selected)' if s_ == best else ''} | {vrank.get(s_, '–')} | {stt.mean(dm.values()):.1f} | "
                 f"{dm[wd]:.1f} ({wd}) | {nb}/{len(D['test'])} | {pv:.3g} |")
    allwin = [s_ for s_, _, nb, _, _ in rows_s if nb == len(D["test"])]
    sig_s = [s_ for s_, _, _, pv, _ in rows_s if pv < 0.05]
    lose = sorted({d for *_, ld in rows_s for d in ld})
    allmean = [s_ for s_, mn, *_ in rows_s if mn < stt.mean(web.values())]
    worst_s = max(rows_s, key=lambda x: x[1])[0]
    L += ["", f"**Seed robustness:** {len(allmean)} of {len(rows_s)} seeds have a lower weekday mean than Webster; "
          f"the day-level difference is significant (raw p < 0.05) for {'only ' if len(sig_s) < len(rows_s) else ''}"
          f"{len(sig_s)} of {len(rows_s)} seeds ({', '.join(map(str, sig_s)) or 'none'}). Days on which at least one seed is not better than Webster: "
          f"{', '.join(lose) or 'none'}. "
          f"{len(allwin)} of {len(rows_s)} seeds beat Webster on every test weekday. "
          f"The worst seed on test is seed {worst_s} (validation rank {vrank.get(worst_s)} of {len(vrank)}); "
          + ("validation picked it out as worst." if vrank.get(worst_s) == len(vrank) else
             "validation did not single it out (validation uses one replication per day and the seeds differ "
             f"there by only {max(val.values()) - min(val.values()):.2f} s/veh), so seed selection is not a reliable "
             "guard against an unstable seed.")]
    bad = [k for k, r in R.items() if r["unserved_day"] or r["teleports"] or r["collisions"]]
    bad_txt = "; ".join(f"{c} {d} r{r} ({R[(c, d, r)]['teleports']} teleports, {R[(c, d, r)]['collisions']} collisions, "
                        f"{R[(c, d, r)]['unserved_day']} unserved)" for c, d, r in sorted(bad))
    L += ["", f"Runs with unserved vehicles, teleports or collisions: {len(bad)}" + (f" — {bad_txt}" if bad else ""), "",
          "## Caveats (apply to every number above)", "",
          "- Single-intersection twin: no corridor coordination or platoon arrivals (Poisson within each 5-min "
          "count), which under-credits GDOT's coordinated Peachtree timing.",
          "- Demand = GDOT's counted 5-min volumes (stop-bar detector counts); right turns are not counted.",
          "- Twin capacity: driver imperfection sigma = 0.2 (SUMO default 0.5), so a through lane discharges about "
          "1,920-2,010 veh/h of green in a cyclic queue-discharge test, at or slightly above the HCM base saturation "
          "flow (1,900) and above typical adjusted field values (~1,700-1,800) -- slightly optimistic. It is a standard-value calibration, "
          "not a fit to measured discharge at this intersection (intersections/7065/timing/capacity_check/README.md). "
          "Some PM count bins on Sep 21/23/24 exceed any physical discharge and are likely repeated pulses from "
          "set-back count detectors in stop-and-go queues; they are kept as recorded (fidelity policy).",
          "- Webster is one all-day plan designed for the PM peak (no time-of-day plans); it can be beaten off-peak "
          "by any adaptive controller.",
          "- RL: idealised detection (whole-approach lane occupancy, route-based left-turn calls); skips uncalled "
          "lefts (GDOT's actuated controller can too; Webster cannot).",
          "- Real timing (actuated): SUMO's NEMA controller runs P1 before P2 (GDOT runs it after); the fixed "
          "exact-order row differs in both order and actuation, so the gap between the two rows bounds their combined "
          "effect. Its gap-out settings were fitted to Oct 2 records — a test day — which favours real timing on that day.",
          "- Hardware parameters for all controllers come from GDOT's records, partly from a test day: minimum greens "
          "(RL, Webster, real) from the Oct 2 Timing & Actuation records; pedestrian walk/clearance times from the "
          "Oct 2 16:00 charts (cross-checked against all recorded windows).",
          "- Saturdays: not chronologically held out (they fall inside the training/validation calendar span, but none "
          "was used for training or selection); Webster is the weekday-PM design applied unchanged; GDOT's weekend "
          "plans F/G/H run with gap-out settings fitted on a weekday and have no Timing & Actuation record of their own.",
          "- Lane configuration not yet verified against the SR-237 widening construction state (see CLAUDE.md).",
          "- All runs use SUMO 1.27.1, pinned in the project's uv environment (pyproject.toml) regardless of the "
          "system install; matrix.py refuses to run on any other version. An earlier run (archived, not used here) "
          "was on an OS-upgraded SUMO 1.28.0, which segfaulted intermittently; 1.27.1 has hit the same transient "
          "segfault at least once (matrix.py retries a crashed run up to 3x, which is deterministic and verified "
          "to reproduce), so the retry logic -- not the version alone -- is what makes these runs reliable.",
          "- On the hand-built twin, the size of RL's advantage over Webster depends on this calibration; its direction does not. With "
          "sigma 0.5 (archive/v3_2026-10-15_sumo1.27.1_sigma0.5) RL beat Webster by 9.1 s/veh on weekdays and 6.1 on "
          "Saturdays; with sigma 0.2 the margin is smaller (see above) -- mostly because Webster's Peachtree-SW left "
          "was near breakdown at the lower capacity.",
          "- Pedestrians are not simulated; Webster and RL respect pedestrian minimum greens every cycle.",
          f"- SUMO version: {subprocess.run(['sumo', '--version'], capture_output=True, text=True).stdout.splitlines()[0]}.", ""]
    if SITE == "7065osm":
        i = L.index("## Caveats (apply to every number above)")
        L[i + 2:i + 2] = [
            "- **Network (7065osm):** built from OpenStreetMap by tools/osm_build.py with documented tag fixes "
            "(intersections/7065osm/network/osm_tag_fixes.json): the Piedmont north leg (ways 525767115, 964301947, "
            "1377947443) had no lanes/maxspeed tags, so netconvert defaulted to 1 lane and 100 km/h; set to the stop-line "
            "layout from GDOT's detectors (left, 2 through, right), 2 lanes upstream (matching the tagged neighbour) and "
            "35 mph. Before the upstream fix a 1-lane stretch ~130 m upstream throttled this approach.",
            "- **7065osm lane differences from the twin:** Piedmont from S has 2 left lanes (OSM tags 1 left + 3 through, "
            "but only 2 outbound lanes exist, so netconvert turned the 3rd through into a left; low left demand) and the "
            "right turn shares the outer through lane; the Piedmont-N left lane runs the whole 128 m segment (real bay "
            "is short), overstating left-turn storage.",
            "- The twin's 1,920 veh/h/lane discharge figure in the capacity check was measured on the twin; an "
            "independent cyclic test gave ~2,000 on this network's Piedmont-N approach, with the queue reaching upstream.",
            "- **Speeds:** the Piedmont-S approach and the Piedmont-S exit (carrying the Piedmont-N through movement) are "
            "OSM-tagged 40 mph (edges 1014001449#5/#9, 715642217#0, 715642215#0); the posted speed is 35 mph. Left as "
            "tagged; small effect (Piedmont-S delays 1–4 s lower than on the twin, partly also from its second left lane).",
            "- Real timing on this network spills more on the highest-demand day than on the twin (Sep 24: 308 vs 173 "
            "s/veh, reaching movements that don't use Piedmont-N); cause not traced. 3 real-timing runs have one "
            "collision each (twin: none); not traced either. Neither affects the conclusions (weekday real timing is "
            "excluded as evidence on both networks).",
        ]
    if SITE != "7065":
        L.insert(1, f"\n**Network: {SITE}** (`{NET.relative_to(REPO)}`). The twin discharge rate used in the "
                    "capacity check (1,920 veh/h/lane) was measured on the hand-built twin, not on this network.\n")
    (HERE / ("report.md" if SITE == "7065" else f"report_{SITE}.md")).write_text("\n".join(L) + "\n")
    json.dump({"best_seed": best, "validation": val,
               "significance": {f"{x}|{y}|{p}": v for (x, y, p), v in sig.items()}},
              open(HERE / ("results.json" if SITE == "7065" else f"results_{SITE}.json"), "w"), indent=1)
    print("\n".join(L))


SUMO_VERSION = "1.27.1"           # pinned in pyproject.toml (eclipse-sumo); results are only comparable on one version


def check_sumo():
    v = subprocess.run(["sumo", "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    import libsumo
    lv = libsumo.getVersion()[1]
    if SUMO_VERSION not in v or SUMO_VERSION not in lv:
        sys.exit(f"wrong SUMO: binary '{v}', libsumo '{lv}' (need {SUMO_VERSION}). Run via `uv run` from the repo.")


if __name__ == "__main__":
    check_sumo()
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["prepare", "train", "run", "report"])
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) // 2))
    ap.add_argument("--seeds", default="0-4")
    ap.add_argument("--episodes", type=int, default=20)
    ap.add_argument("--only", default="")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--site", default="7065", help="7065 (hand-built twin, default) or e.g. 7065osm")
    a = ap.parse_args()
    set_site(a.site)
    {"prepare": prepare, "train": train, "run": run, "report": report}[a.cmd](a)
