"""RQ1 evaluation, hour by hour: every controller on the same validation weekdays, several simulation seeds,
scored per (day, hour, movement), next to the traffic conditions GDOT counted in that hour.

    uv run python atsc/sites/7065/evaluate.py run [--seeds 1 2 3] [--only maxpressure lstdq lstdq_s1 lstdq_v2_s0]
        -> eval/hour_mv.csv  (date, controller, seed, hour, movement: vehicles, mean / p95 / max delay, backlog)
    uv run python atsc/sites/7065/evaluate.py conditions
        -> eval/conditions.csv  (date, hour: volume, Y, variability, imbalance, left share, from field counts)
    uv run python atsc/sites/7065/evaluate.py report
        -> eval/report.md  (strengths and weaknesses of each controller, by condition)

Resumable: a (date, controller, seed) already in hour_mv.csv is not run again.

Conditions per hour (field counts, counted movements only; rights are not counted at 7065):
  volume       vehicles counted in the hour
  Y            sum of critical flow ratios on the ring-barrier critical path, y = flow / (lanes x 1,950 veh/h),
               the same definition Webster's design uses (atsc/sim/webster.py); a degree-of-saturation proxy
  cv5          coefficient of variation of the twelve 5-min totals (within-hour variability)
  imbalance    share of the busier road (Piedmont N+S vs Peachtree SW+NE)
  left_share   left-turn vehicles / all vehicles
Hours with any outage bin are left out (status != ok).

Limitation, stated with every result: 7065 runs in GDOT's coordinated Peachtree group (7066, 7071, 7058;
common cycle all day), but the model is isolated, with random arrivals and no platoons, so the field plan
is charged the cost of coordination without its benefit. P2's count (Peachtree from NE) is suspect
(about half of what its neighbours imply, not yet resolved).
"""
import argparse
import csv
import json
import statistics as st
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
sys.path.insert(0, str(HERE))
from baselines import days, webster_schedule  # noqa: E402

OUT = HERE / "eval"
CONTROLLERS = ("gdot", "actuated", "webster", "maxpressure", "lstdq")
LSTDQ_IT = 5
S_LANE = 1950
FIELDS = ["date", "controller", "seed", "hour", "movement", "veh", "mean_s", "p95_s", "max_s", "backlog_max"]


def policy(ctrl):
    from atsc.sim.signal import FixedPolicy, actuated_from_site
    if ctrl == "gdot":
        return actuated_from_site(HERE), {"mode": "plan"}
    if ctrl == "actuated":
        return actuated_from_site(HERE), {"mode": "free"}
    if ctrl == "webster":
        return FixedPolicy(), {"mode": "schedule", "schedule": webster_schedule(), "skip_uncalled": False}
    if ctrl == "maxpressure":
        from atsc.sim.maxpressure import MaxPressurePolicy
        return MaxPressurePolicy(HERE), {"mode": "free"}
    if ctrl.split("_")[0] in ("qlearn", "nfq", "ars"):            # METHODS.md: <method>_s<k>
        from train_methods import load_policy
        method, seed = ctrl.split("_")
        return load_policy(method, int(seed[1:])), {"mode": "free"}
    import numpy as np
    from atsc.rl.agent import LSTDQPolicy
    # lstdq = v1 seed 0; lstdq_s<k> = v1 seed k; lstdq_v2_s<k>, lstdq_v2f_s<k> (LSTDQ_V2.md)
    parts = ctrl.split("_")
    version = next((x for x in parts if x in ("v2", "v2f")), "v1")
    seed = int(next((x[1:] for x in parts if x.startswith("s") and x[1:].isdigit()), 0))
    sys.path.insert(0, str(HERE))
    from train_lstdq import out_dir
    w = np.load(out_dir(seed, version) / f"w_it{LSTDQ_IT}.npy")
    return LSTDQPolicy(HERE, w=w, version=version), {"mode": "free"}


def job(args):
    from atsc.sim.episode import run_window
    date, ctrl, seed = args
    try:
        pol, kw = policy(ctrl)
        r = run_window(HERE, str(date), 0.0, 24.0, pol, seed=seed, warmup_s=0, **kw)
    except Exception as e:                      # noqa: BLE001
        import traceback
        print(f"FAILED {args}: {e}\n{traceback.format_exc()}", file=sys.stderr, flush=True)
        return []
    return [{"date": str(date), "controller": ctrl, "seed": seed, "hour": h, "movement": c,
             **{k: round(v, 1) if isinstance(v, float) else v for k, v in m.items()}}
            for (h, c), m in r["by_hour_mv"].items()]


def run(seeds, only):
    OUT.mkdir(exist_ok=True)
    f = OUT / "hour_mv.csv"
    done = {(r["date"], r["controller"], int(r["seed"])) for r in csv.DictReader(open(f))} if f.exists() else set()
    jobs = [(d, c, s) for s in seeds for d in days("validation") for c in (only or CONTROLLERS)
            if (str(d), c, s) not in done]
    print(f"{len(jobs)} full-day runs ({len(done)} already done)", flush=True)
    new = not f.exists()
    with open(f, "a", newline="") as fh, Pool(22) as pool:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if new:
            w.writeheader()
        for k, rows in enumerate(pool.imap_unordered(job, jobs), 1):
            w.writerows(rows)
            fh.flush()
            print(f"  {k}/{len(jobs)}", flush=True)


def conditions():
    from atsc.sim.demand import load_counts
    sig = json.loads((HERE / "signal.json").read_text())
    mv = json.loads((HERE / "movements.json").read_text())["movements"]
    rings = {int(r): [tuple(g) for g in gs] for r, gs in sig["rings"].items()}
    lanes = {m["phases"][0]: m["lanes"] for m in mv.values()}
    cnt = load_counts(HERE)
    rows = []
    for d in days("validation"):
        by_h = defaultdict(list)
        for b in cnt[d]:
            by_h[b.t // 3600].append(b)
        for h, bs in sorted(by_h.items()):
            if len(bs) != 12 or any(b.status != "ok" for b in bs):
                continue
            flow = defaultdict(float)
            for b in bs:
                for c, n in b.counts.items():
                    flow[c] += n
            y = defaultdict(float)
            for c, n in flow.items():
                y[mv[c]["phases"][0]] += n / (lanes[mv[c]["phases"][0]] * S_LANE)
            Y = sum(max(sum(y[p] for p in rings[r][g]) for r in rings) for g in range(len(rings[1])))
            tot = [sum(b.counts.values()) for b in bs]
            vol = sum(flow.values())
            pied = sum(n for c, n in flow.items() if mv[c]["leg"] in ("N", "S"))
            rows.append({"date": str(d), "hour": h, "volume": round(vol), "Y": round(Y, 3),
                         "cv5": round(st.pstdev(tot) / st.mean(tot), 3) if st.mean(tot) else "",
                         "imbalance": round(max(pied, vol - pied) / vol, 3) if vol else "",
                         "left_share": round(sum(n for c, n in flow.items() if mv[c]["move"] == "L") / vol, 3) if vol else ""})
    OUT.mkdir(exist_ok=True)
    with open(OUT / "conditions.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} clean hours on {len(days('validation'))} validation weekdays -> {OUT / 'conditions.csv'}")


SPILL_VEH = 10
Y_BINS = [(0.0, 0.15, "light (Y < 0.15)"), (0.15, 0.30, "moderate (0.15-0.30)"),
          (0.30, 0.40, "busy (0.30-0.40)"), (0.40, 9.0, "heavy (Y >= 0.40)")]


def boot_ci(per_day, n=2000, seed=0):
    """95 % interval of the mean over days, resampling days (hours of one day are not independent)."""
    import random
    rng = random.Random(seed)
    vals = list(per_day.values())
    means = sorted(st.mean(rng.choice(vals) for _ in vals) for _ in range(n))
    return means[int(0.025 * n)], means[int(0.975 * n)]


def report():
    rows = list(csv.DictReader(open(OUT / "hour_mv.csv")))
    cond = {(r["date"], int(r["hour"])): r for r in csv.DictReader(open(OUT / "conditions.csv"))}
    present = {r["controller"] for r in rows}
    ctrls = [c for c in CONTROLLERS if c in present] + sorted(present - set(CONTROLLERS))
    seeds = sorted({int(r["seed"]) for r in rows})
    # per (date, hour, controller): seed-averaged hour delay (s/veh), worst movement p95, backlog
    acc = defaultdict(lambda: [0.0, 0])
    worst = defaultdict(list)
    backlog = defaultdict(int)
    for r in rows:
        k = (r["date"], int(r["hour"]), r["controller"])
        acc[k][0] += float(r["mean_s"]) * int(r["veh"])
        acc[k][1] += int(r["veh"])
        worst[k].append(float(r["p95_s"]))
        backlog[k] = max(backlog[k], int(r["backlog_max"]))
    nseed = defaultdict(set)
    for r in rows:
        nseed[(r["date"], int(r["hour"]), r["controller"])].add(r["seed"])
    D = {k: v[0] / v[1] for k, v in acc.items() if v[1]}
    # main tables: controllers run with every simulation seed (extra LSTDQ training seeds have seed 1 only and
    # appear in the training-seed table); hours with clean field counts, run by all of them with every seed
    all_ctrls = ctrls
    seeds_of = defaultdict(set)
    for r in rows:
        seeds_of[r["controller"]].add(int(r["seed"]))
    ctrls = [c for c in all_ctrls if len(seeds_of[c]) == len(seeds)]
    hours = sorted({(d, h) for d, h, _ in D if (d, h) in cond
                    and all(len(nseed[(d, h, c)]) == len(seeds) for c in ctrls)})
    ybin = {dh: next(lab for lo, hi, lab in Y_BINS if lo <= float(cond[dh]["Y"]) < hi) for dh in hours}
    best = {dh: min(D[(*dh, c)] for c in ctrls) for dh in hours}

    L = ["# RQ1 evaluation: strengths and weaknesses by traffic condition (7065, validation weekdays)", "",
         f"{len(hours)} clean hours on {len({d for d, _ in hours})} days x {len(seeds)} simulation seeds "
         f"(seed-averaged per hour). Y = sum of critical flow ratios from the field counts. Intervals: 95 % "
         "day-bootstrap. **Limitations:** isolated model of a signal in GDOT's coordinated Peachtree group "
         "(field plan charged coordination's cost without its benefit); P2 count suspect (~half its neighbours'); "
         "right turns uncounted; LSTDQ = one training seed.", ""]

    def table(title, metric, fmt="{:.1f}"):
        L.extend([f"## {title}", "", "| Controller | all hours | " + " | ".join(lab for _, _, lab in Y_BINS) + " |",
                  "|---|---|" + "---|" * len(Y_BINS)])
        for c in ctrls:
            cells = []
            for sel in [None] + [lab for _, _, lab in Y_BINS]:
                hs = [dh for dh in hours if sel is None or ybin[dh] == sel]
                per_day = defaultdict(list)
                for dh in hs:
                    v = metric(dh, c)
                    if v is not None:
                        per_day[dh[0]].append(v)
                per_day = {d: st.mean(v) for d, v in per_day.items()}
                if not per_day:
                    cells.append("-")
                    continue
                m = st.mean(per_day.values())
                lo, hi = boot_ci(per_day)
                cells.append(fmt.format(m) + f" ({fmt.format(lo)} to {fmt.format(hi)})")
            L.append(f"| {c} | " + " | ".join(cells) + " |")
        L.append("")

    L.append("Hours per condition: " + ", ".join(f"{lab} {sum(ybin[dh] == lab for dh in hours)}" for _, _, lab in Y_BINS))
    L.append("")
    # overall, every vehicle weighted equally (the tables below weight every hour equally)
    L += ["## Overall mean delay, vehicle-weighted (s/veh)", "", "| Controller | mean delay (95 % interval) |", "|---|---|"]
    for c in ctrls:
        per_day = defaultdict(lambda: [0.0, 0])
        for d, h in hours:
            per_day[d][0] += acc[(d, h, c)][0]
            per_day[d][1] += acc[(d, h, c)][1]
        per_day = {d: s / n for d, (s, n) in per_day.items()}
        lo, hi = boot_ci(per_day)
        L.append(f"| {c} | {st.mean(per_day.values()):.1f} ({lo:.1f} to {hi:.1f}) |")
    L.append("")
    # LSTDQ training seeds: spread of each version's overall delay, on simulation seed 1 (all of them have it)
    groups = defaultdict(list)
    for c in all_ctrls:
        if c.startswith("lstdq"):
            groups[next((x for x in c.split("_") if x in ("v2", "v2f")), "v1")].append(c)
    if any(len(v) > 1 for v in groups.values()):
        s1 = defaultdict(lambda: [0.0, 0])
        for r in rows:
            if r["seed"] == "1" and (r["date"], int(r["hour"])) in cond:
                s1[r["controller"]][0] += float(r["mean_s"]) * int(r["veh"])
                s1[r["controller"]][1] += int(r["veh"])
        L += ["## LSTDQ versions over training seeds (overall vehicle-weighted delay, simulation seed 1, s/veh)", "",
              "| Version | training seeds | median | min | max | per seed |", "|---|---|---|---|---|---|"]
        for v, cs in sorted(groups.items()):
            vals = {c: s1[c][0] / s1[c][1] for c in cs if s1[c][1]}
            if vals:
                L.append(f"| {v} | {len(vals)} | {st.median(vals.values()):.1f} | {min(vals.values()):.1f} | "
                         f"{max(vals.values()):.1f} | " + ", ".join(f"{c} {x:.1f}" for c, x in sorted(vals.items())) + " |")
        for c in ("maxpressure", "webster", "actuated"):
            if s1[c][1]:
                L.append(f"| {c} (reference) | - | {s1[c][0] / s1[c][1]:.1f} | | | |")
        L.append("")
    table("Mean delay (s/veh)", lambda dh, c: D[(*dh, c)])
    if "webster" in ctrls:
        table("Gain vs Webster (%, negative = less delay than Webster)",
              lambda dh, c: 100 * (D[(*dh, c)] / D[(*dh, "webster")] - 1))
    if "actuated" in ctrls:
        table("Gain vs actuated (%, negative = less delay than actuated)",
              lambda dh, c: 100 * (D[(*dh, c)] / D[(*dh, "actuated")] - 1))
    table("Regret: delay above the best controller in the same hour (s/veh)", lambda dh, c: D[(*dh, c)] - best[dh])
    table("Worst-off movement: highest 95th-percentile delay of any movement in the hour (s)",
          lambda dh, c: max(worst[(*dh, c)]))
    # SUMO holds 1-2 vehicles at entry whenever two arrive on a lane in the same step (median hourly maximum 2
    # for every controller, also at night), so only a backlog well above that counts as a queue reaching the leg end
    table(f"Hours with a queue reaching the leg end (share of hours with >= {SPILL_VEH} vehicles unable to enter)",
          lambda dh, c: 1.0 if backlog[(*dh, c)] >= SPILL_VEH else 0.0, fmt="{:.2f}")
    L += ["## How often each controller is best in an hour", "", "| Controller | " + " | ".join(lab for _, _, lab in Y_BINS) + " |",
          "|---|" + "---|" * len(Y_BINS)]
    for c in ctrls:
        L.append(f"| {c} | " + " | ".join(
            f"{100 * st.mean(D[(*dh, c)] == best[dh] for dh in hours if ybin[dh] == lab):.0f} %"
            if any(ybin[dh] == lab for dh in hours) else "-" for _, _, lab in Y_BINS) + " |")
    (OUT / "report.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "conditions", "report"])
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--only", nargs="+")
    a = ap.parse_args()
    {"run": lambda: run(a.seeds, a.only), "conditions": conditions, "report": report}[a.cmd]()
