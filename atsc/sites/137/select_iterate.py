"""Which saved iterate of each learner is evaluated (TEST_PLAN.md amendment 1, F4). Train days only.

    uv run python atsc/sites/137/select_iterate.py      -> <seed dir>/selected.json per learner seed, table

Every saved iterate of LSTDQ v2 (w_it1..5), Q-learning (w_it1..5) and ARS (theta_it10..50) runs greedily on the
same fixed selection windows: 3 train weekdays (first, middle, last usable) x the 4 training windows of
train_lstdq.py, simulation seed 1, free mode. The iterate with the lowest vehicle-weighted delay over the 12 windows
is evaluated. Before amendment 1 the final iterate was evaluated whatever it did (Q-learning diverged).
"""
import json
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
sys.path.insert(0, str(HERE))
SEEDS = range(5)


def candidates():
    from train_lstdq import out_dir as lstdq_dir
    from train_methods import out_dir
    out = []
    for s in SEEDS:
        out += [("lstdq_v2", s, k, lstdq_dir(s, "v2") / f"w_it{k}.npy") for k in range(1, 6)]
        out += [("qlearn", s, k, out_dir("qlearn", s) / f"w_it{k}.npy") for k in range(1, 6)]
        out += [("ars", s, k, out_dir("ars", s) / f"theta_it{k}.npy") for k in (10, 20, 30, 40, 50)]
    return [c for c in out if c[3].exists()]


def windows():
    from train_lstdq import WINDOWS, train_days
    ds = train_days()
    pick = [ds[0], ds[len(ds) // 2], ds[-1]]
    return [(str(d), w) for d in pick for w in WINDOWS]


def job(args):
    method, seed, k, path, day, win = args
    from atsc.rl.agent import LSTDQPolicy
    from atsc.rl.methods import ars_qfun
    from atsc.sim.episode import run_window
    if method == "ars":
        pol = LSTDQPolicy(HERE, version="v2", qfun=ars_qfun(np.load(path)))
    else:
        pol = LSTDQPolicy(HERE, version="v2", w=np.load(path))
    r = run_window(HERE, day, *win, pol, mode="free", seed=1)
    return method, seed, k, str(path.parent), r["delay_all_s"] * r["vehicles"], r["vehicles"]


def main():
    jobs = [(*c, d, w) for c in candidates() for d, w in windows()]
    print(f"{len(jobs)} selection runs", flush=True)
    acc = defaultdict(lambda: [0.0, 0])
    where = {}
    with ProcessPoolExecutor(22) as pool:
        for i, (m, s, k, d, dl, n) in enumerate(pool.map(job, jobs, chunksize=1), 1):
            acc[(m, s, k)][0] += dl
            acc[(m, s, k)][1] += n
            where[(m, s)] = d
            if i % 100 == 0:
                print(f"  {i}/{len(jobs)}", flush=True)
    print("| learner | seed | delay per iterate (s/veh) | selected |\n|---|---|---|---|")
    for (m, s), d in sorted(where.items()):
        ks = sorted(k for mm, ss, k in acc if (mm, ss) == (m, s))
        v = {k: acc[(m, s, k)][0] / acc[(m, s, k)][1] for k in ks}
        best = min(v, key=v.get)
        json.dump({"iterate": best, "selection_delay_s": {str(k): round(x, 2) for k, x in v.items()},
                   "source": "select_iterate.py (TEST_PLAN.md amendment 1, F4): 3 train weekdays x 4 windows, seed 1"},
                  open(Path(d) / "selected.json", "w"), indent=1)
        print(f"| {m} | {s} | " + ", ".join(f"it{k} {x:.1f}" for k, x in v.items()) + f" | it{best} |")


if __name__ == "__main__":
    main()
