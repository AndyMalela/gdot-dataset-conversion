"""RQ1 evaluation, hour by hour: every controller on the same validation weekdays, several simulation seeds,
scored per (day, hour, movement), next to the traffic conditions GDOT counted in that hour.

    uv run python atsc/sites/7065/evaluate.py run [--seeds 1 2 3] [--only maxpressure lstdq]
        -> eval/hour_mv.csv  (date, controller, seed, hour, movement: vehicles, mean / p95 / max delay, backlog)
    uv run python atsc/sites/7065/evaluate.py conditions
        -> eval/conditions.csv  (date, hour: volume, Y, variability, imbalance, left share, from field counts)

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
    import numpy as np
    from atsc.rl.agent import LSTDQPolicy
    return LSTDQPolicy(HERE, w=np.load(HERE / "lstdq" / f"w_it{LSTDQ_IT}.npy")), {"mode": "free"}


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


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "conditions"])
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--only", nargs="+")
    a = ap.parse_args()
    run(a.seeds, a.only) if a.cmd == "run" else conditions()
