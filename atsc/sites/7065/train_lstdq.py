"""Train the LSTDQ controller (atsc/rl/agent.py) on TRAIN weekdays, fully actuated rules (no cycle), and
evaluate the greedy policy like the baselines.

    uv run python atsc/sites/7065/train_lstdq.py train [--iters 5] [--episodes 22]   -> lstdq/w_it<k>.npy, train_log.csv
    uv run python atsc/sites/7065/train_lstdq.py eval  --it K                         -> appends to baselines/runs.csv as 'lstdq'

Policy iteration (LSPI with LSTDQ): iteration 0 collects transitions with the actuated gap-out rule plus 20 %
random actions; each later iteration runs the greedy policy of the previous fit with 10 % random actions and
refits on all transitions so far. Windows: AM 06-10, midday 11-15, PM 15:30-19:30, evening 19:30-23.
"""
import argparse
import csv
import json
import random
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))

OUT = HERE / "lstdq"
WINDOWS = [(6.0, 10.0), (11.0, 15.0), (15.5, 19.5), (19.5, 23.0)]
GAMMA = 0.99            # per second
RIDGE = 1e-2


def train_days():
    sys.path.insert(0, str(HERE))
    from baselines import days
    return days("train")


def episode(args):
    from atsc.rl.agent import LSTDQPolicy
    from atsc.sim.episode import run_window
    from atsc.sim.signal import ActuatedPolicy
    date, (b0, b1), w, eps, seed = args
    cal = json.loads((HERE / "sim.json").read_text())
    pol = LSTDQPolicy(HERE, w=w, eps=eps, behaviour=ActuatedPolicy(cal["passage_s"]), seed=seed, record=True)
    r = run_window(HERE, str(date), b0, b1, pol, mode="free", seed=seed)
    return pol.samples(), {"date": str(date), "window": f"{b0}-{b1}", "eps": eps, "delay_all_s": round(r["delay_all_s"], 2),
                           "teleports": r["teleports"]}


def train(iters, n_ep):
    from atsc.rl.agent import M
    from atsc.rl.lstdq import LinearQ
    OUT.mkdir(exist_ok=True)
    rng = random.Random(0)
    ds = train_days()
    data, log, w = [], [], None
    q = LinearQ(M, 2)
    for it in range(iters + 1):
        eps = 0.2 if it == 0 else 0.1
        jobs = [(rng.choice(ds), rng.choice(WINDOWS), w, eps, 1000 * it + k) for k in range(n_ep)]
        with Pool(min(22, n_ep)) as pool:
            res = pool.map(episode, jobs, chunksize=1)
        for s, info in res:
            if s is not None:
                data.append(s)
            log.append({"iter": it, **info})
        dl = [i["delay_all_s"] for _, i in res]
        print(f"iter {it}: {'actuated+random' if w is None else 'greedy(w)+random'} episodes, "
              f"mean delay {np.mean(dl):.1f} s/veh, transitions so far {sum(len(d[0]) for d in data)}", flush=True)
        if it == iters:
            break
        X, A, R, X2, D = (np.concatenate([d[i] for d in data]) for i in range(5))
        q.fit(X, A, R / 100.0, X2, D, np.zeros(len(X), bool), GAMMA, ridge=RIDGE, iters=5)
        w = q.w.copy()
        np.save(OUT / f"w_it{it + 1}.npy", w)
    with open(OUT / "train_log.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(log[0]))
        wr.writeheader()
        wr.writerows(log)


def eval_job(args):
    from atsc.rl.agent import LSTDQPolicy
    from atsc.sim.episode import run_window
    date, w = args
    r = run_window(HERE, str(date), 0.0, 24.0, LSTDQPolicy(HERE, w=w), mode="free", warmup_s=0)
    row = {"date": str(date), "controller": "lstdq", "vehicles": r["vehicles"], "delay_all_s": round(r["delay_all_s"], 2),
           "teleports": r["teleports"], **{f"delay_{c}_s": round(v["mean_s"], 1) for c, v in r["delay"].items()},
           **{f"backlog_{c}": v for c, v in r["backlog_max"].items()}}
    hourly = [{"date": str(date), "controller": "lstdq", "hour": h, "delay_sum_s": round(v[0], 1), "vehicles": v[1]}
              for h, v in r["delay_by_hour"].items()]
    return row, hourly


def evaluate(it):
    sys.path.insert(0, str(HERE))
    from baselines import OUT as BOUT, days
    w = np.load(OUT / f"w_it{it}.npy")
    ds = days("validation")
    with Pool(22) as pool:
        res = pool.map(eval_job, [(d, w) for d in ds], chunksize=1)
    for name, rows in [("runs.csv", [r for r, _ in res]), ("hourly.csv", [h for _, hs in res for h in hs])]:
        old = [r for r in csv.DictReader(open(BOUT / name)) if r["controller"] != "lstdq"]
        allr = old + rows
        with open(BOUT / name, "w", newline="") as f:
            wr = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in allr for k in r)))
            wr.writeheader()
            wr.writerows(allr)
    print(f"lstdq it{it}: validation mean of daily delay {np.mean([float(r['delay_all_s']) for r, _ in res]):.1f} s/veh")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--iters", type=int, default=5)
    ap.add_argument("--episodes", type=int, default=22)
    ap.add_argument("--it", type=int)
    a = ap.parse_args()
    train(a.iters, a.episodes) if a.cmd == "train" else evaluate(a.it)
