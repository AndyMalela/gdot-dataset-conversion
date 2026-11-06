"""Train the other learners of METHODS.md on the LSTDQ v2 controller (same state, action, rules, training days and
windows as train_lstdq.py; only the learning method differs).

    uv run python atsc/sites/7065/train_methods.py train --method qlearn|nfq|ars --seed S
        -> learners/<method>/seed<S>/ (qlearn: w_it<k>.npy, nfq: net_it<k>.npz, ars: theta_it<k>.npy), train_log.csv

qlearn  online linear Q-learning, 110 episodes one after another (= LSTDQ's 5 x 22 fitted episodes): episodes
        1-22 actuated rule + 20 % random (off-policy learning), then greedy on the live weights + 10 % random
nfq     LSPI's loop (train_lstdq.train) with the least-squares fit replaced by neural fitted Q iteration
ars     augmented random search on the linear policy (end if theta . x > 0): per iteration N directions, each
        tried as theta +/- nu delta on the same day, window and simulation seed; the top B directions by
        max(r+, r-) move theta by alpha / (B sigma_r) sum (r+ - r-) delta; r = - mean delay (s/veh) of the window
"""
import argparse
import csv
import os
import random
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
sys.path.insert(0, str(HERE))
from train_lstdq import GAMMA, WINDOWS, train_days  # noqa: E402

OUT = HERE / "learners"
VERSION = "v2"
METHODS = ("qlearn", "nfq", "nfq_conv", "ars")
NFQ_FIT = {"nfq": {"iters": 5, "epochs": 2},                                   # as fixed in METHODS.md
           "nfq_conv": {"iters": 400, "epochs": 1, "tol": 0.005}}             # amendment 1 (METHODS.md)
ITERS, N_EP = 5, 22                     # as LSTDQ
POOL = int(os.environ.get("ATSC_POOL", N_EP))      # episode workers (no effect on results)
QL_ALPHA = 0.05
ARS_ITERS, ARS_N, ARS_B, ARS_ALPHA, ARS_NU = 50, 11, 6, 0.02, 0.03


def out_dir(method, seed):
    return OUT / method / f"seed{seed}"


def _policy(**kw):
    from atsc.rl.agent import LSTDQPolicy
    return LSTDQPolicy(HERE, version=VERSION, **kw)


def _run(pol, date, window, seed):
    from atsc.sim.episode import run_window
    r = run_window(HERE, str(date), *window, pol, mode="free", seed=seed)
    return {"date": str(date), "window": f"{window[0]}-{window[1]}", "delay_all_s": round(r["delay_all_s"], 3),
            "teleports": r["teleports"]}


def _write_log(out, log):
    with open(out / "train_log.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in log for k in r)))
        wr.writeheader()
        wr.writerows(log)


def train_qlearn(seed):
    from atsc.rl.agent import dims
    from atsc.rl.methods import OnlineLinearQ
    from atsc.sim.signal import actuated_from_site
    out = out_dir("qlearn", seed)
    out.mkdir(parents=True, exist_ok=True)
    rng, ds = random.Random(seed), train_days()
    learner = OnlineLinearQ(dims(VERSION)[2], alpha=QL_ALPHA, gamma=GAMMA, seed=seed)
    log = []
    for it in range(ITERS):
        for k in range(N_EP):
            date, window = rng.choice(ds), rng.choice(WINDOWS)
            ep_seed = 100000 * seed + 1000 * it + k
            pol = _policy(eps=0.2 if it == 0 else 0.1, behaviour=actuated_from_site(HERE) if it == 0 else None,
                          seed=ep_seed, learner=learner)
            log.append({"iter": it, "episode": k, **_run(pol, date, window, ep_seed),
                        "w_norm": round(float(np.linalg.norm(learner.w)), 3)})
        np.save(out / f"w_it{it + 1}.npy", learner.w.ravel())
        print(f"qlearn s{seed} iter {it}: mean delay {np.mean([r['delay_all_s'] for r in log[-N_EP:]]):.1f} s/veh, "
              f"|w| {log[-1]['w_norm']}", flush=True)
    _write_log(out, log)


def _nfq_episode(args):
    from atsc.sim.signal import actuated_from_site
    date, window, net, eps, seed = args
    pol = _policy(eps=eps, behaviour=actuated_from_site(HERE) if net is None else None, seed=seed, record=True,
                  qfun=None if net is None else net.q)
    info = _run(pol, date, window, seed)
    return pol.samples(), info


def train_nfq(seed, method="nfq"):
    from atsc.rl.agent import dims
    from atsc.rl.methods import MLPQ
    out = out_dir(method, seed)
    out.mkdir(parents=True, exist_ok=True)
    rng, ds = random.Random(seed), train_days()
    net, data, log, fitted = MLPQ(dims(VERSION)[2], seed=seed), [], [], None
    for it in range(ITERS + 1):
        eps = 0.2 if it == 0 else 0.1
        jobs = [(rng.choice(ds), rng.choice(WINDOWS), fitted, eps, 100000 * seed + 1000 * it + k) for k in range(N_EP)]
        with Pool(POOL) as pool:
            res = pool.map(_nfq_episode, jobs, chunksize=1)
        data += [s for s, _ in res if s is not None]
        log += [{"iter": it, **i} for _, i in res]
        print(f"{method} s{seed} iter {it}: mean delay {np.mean([i['delay_all_s'] for _, i in res]):.1f} s/veh", flush=True)
        if it == ITERS:
            break
        X, A, R, X2, D = (np.concatenate([d[i] for d in data]) for i in range(5))
        k = net.fit(X, A, R / 100.0, X2, D, GAMMA, **NFQ_FIT[method])
        q = net.qs(X)
        print(f"{method} s{seed} fit {it + 1}: {k} backups, mean Q {q.mean():.1f}, share end {np.mean(q[:, 1] > q[:, 0]):.2f}",
              flush=True)
        np.savez(out / f"net_it{it + 1}.npz", **net.state())
        fitted = net
    _write_log(out, log)


def _ars_episode(args):
    from atsc.rl.methods import ars_qfun
    date, window, theta, seed = args
    return _run(_policy(qfun=ars_qfun(theta)), date, window, seed)


def train_ars(seed):
    from atsc.rl.agent import dims
    out = out_dir("ars", seed)
    out.mkdir(parents=True, exist_ok=True)
    rng, ds = random.Random(seed), train_days()
    nrng = np.random.default_rng(seed)
    theta = np.zeros(dims(VERSION)[2])
    log = []
    with Pool(2 * ARS_N) as pool:
        for it in range(ARS_ITERS):
            delta = nrng.standard_normal((ARS_N, len(theta)))
            setting = [(rng.choice(ds), rng.choice(WINDOWS), 100000 * seed + 1000 * it + k) for k in range(ARS_N)]
            jobs = [(d, w, theta + sgn * ARS_NU * delta[k], s) for k, (d, w, s) in enumerate(setting) for sgn in (1, -1)]
            res = pool.map(_ars_episode, jobs, chunksize=1)
            r = -np.array([x["delay_all_s"] for x in res]).reshape(ARS_N, 2)        # columns: +, -
            top = np.argsort(-r.max(1))[:ARS_B]
            sigma = r[top].std() or 1.0
            theta = theta + ARS_ALPHA / (ARS_B * sigma) * ((r[top, 0] - r[top, 1]) @ delta[top])
            log += [{"iter": it, "direction": k, "sign": "+-"[j], **res[2 * k + j]} for k in range(ARS_N) for j in (0, 1)]
            if (it + 1) % 10 == 0:
                np.save(out / f"theta_it{it + 1}.npy", theta)
            print(f"ars s{seed} iter {it}: mean delay {-r.mean():.1f} s/veh, sigma {sigma:.2f}, "
                  f"|theta| {np.linalg.norm(theta):.3f}", flush=True)
    _write_log(out, log)


def load_policy(method, seed):
    """the evaluated policy of a method: the final iterate, no selection on validation days."""
    from atsc.rl.methods import MLPQ, ars_qfun
    d = out_dir(method, seed)
    if method == "qlearn":
        return _policy(w=np.load(d / f"w_it{ITERS}.npy"))
    if method.startswith("nfq"):
        return _policy(qfun=MLPQ.load(d / f"net_it{ITERS}.npz").q)
    return _policy(qfun=ars_qfun(np.load(d / f"theta_it{ARS_ITERS}.npy")))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["train"])
    ap.add_argument("--method", required=True, choices=METHODS)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    {"qlearn": train_qlearn, "nfq": train_nfq, "nfq_conv": lambda s: train_nfq(s, "nfq_conv"),
     "ars": train_ars}[a.method](a.seed)
