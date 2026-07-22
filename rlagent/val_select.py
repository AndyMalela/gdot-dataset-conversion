"""Validation-based seed selection (EXP-004 final protocol).

Seed variance is the residual problem: the winning policy exists in the
hypothesis class (S8 seed4 = 507 s at 1.3x, beating tuned-actuated) but is
found by only some seeds. The base paper resolves this the same way --
Sahachaiseree Table 6 reports the *best-performing agent* of 16 independently
trained agents. Protocol here, kept honest:

  1. VALIDATE: evaluate every trained seed on a TRAINING day (0507) at the
     target load (1.3x) -- data the training process was allowed to see.
  2. SELECT: argmin validation peak delay.
  3. REPORT: the selected seed's HELD-OUT (0508) numbers as the deployed-
     policy result. 0508 is never used for selection -> no test peeking.

Usage: python3 val_select.py --dir ci/race/ratemg --feature-mode pg_glob_rate \
           --max-greens 15,92,30,70 [--scale 1.3]
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import sys

import numpy as np

import stages as st
from lstdq import LinearQ
from sumo_env import Sig7065Env

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(
    HERE, "experiments", "EXP-003_spillback-features", "data"))
from peak_delay import peak_total_delay  # noqa: E402

VAL_DAY = "0507"        # training day -> legal for selection
DRAIN_END = 108000


def run_greedy(rou, w, scale, ti, feature_mode, max_greens):
    env = Sig7065Env(rou, begin=0, end=DRAIN_END, seed=9999, scale=scale,
                     label="valsel", tripinfo=ti, feature_mode=feature_mode,
                     enforce_max_green=True, max_greens=max_greens)
    obs = env.reset()
    agent = LinearQ(env.n_state_features, st.N_ACTIONS)
    agent.w = w
    done = False
    while not done:
        res = env.step(agent.greedy(obs), compute_reward=False)
        obs, done = res.state, res.done
    env.close()
    return peak_total_delay(ti)[1]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dir", default="ci/race/ratemg")
    p.add_argument("--feature-mode", default="pg_glob_rate")
    p.add_argument("--max-greens", default="15,92,30,70")
    p.add_argument("--scale", type=float, default=1.3)
    args = p.parse_args()
    mg = [float(x) for x in args.max_greens.split(",")]
    rou = os.path.join(HERE, "..", "sumodemand", f"{VAL_DAY}.rou.xml")

    rows = []
    for wpath in sorted(glob.glob(os.path.join(HERE, args.dir,
                                               "s*/weights_random_s*.npy"))):
        seed = int(re.search(r"_s(\d+)\.npy$", wpath).group(1))
        sdir = os.path.dirname(wpath)
        # only seeds with COMPLETE training (20 eps) are candidates
        csv = os.path.join(sdir, f"train_random_s{seed}.csv")
        if not os.path.exists(csv) or sum(1 for _ in open(csv)) - 1 < 20:
            continue
        ti = os.path.join(sdir, f"ti_val_{VAL_DAY}_x{args.scale}.xml")
        if not os.path.exists(ti):
            d = run_greedy(rou, np.load(wpath), args.scale, ti,
                           args.feature_mode, mg)
        else:
            d = peak_total_delay(ti)[1]
        # held-out number, if its eval exists
        hti = os.path.join(sdir, f"ti_heldout_rl_x{args.scale}.xml")
        held = peak_total_delay(hti)[1] if os.path.exists(hti) else float("nan")
        rows.append((seed, d, held))
        print(f"  seed {seed:2d}: val({VAL_DAY} x{args.scale}) = {d:7.1f} s"
              f"   heldout(0508) = {held:7.1f} s", flush=True)

    if rows:
        best = min(rows, key=lambda r: r[1])
        print(f"\nSELECTED seed {best[0]} (val {best[1]:.0f} s)"
              f" -> HELD-OUT 0508 result: {best[2]:.0f} s")
        print("Rank correlation val<->heldout is the protocol's sanity check:")
        v = np.array([r[1] for r in rows]); h = np.array([r[2] for r in rows])
        ok = ~np.isnan(h)
        if ok.sum() >= 3:
            rv = np.argsort(np.argsort(v[ok])); rh = np.argsort(np.argsort(h[ok]))
            rho = np.corrcoef(rv, rh)[0, 1]
            print(f"  Spearman rho over {ok.sum()} seeds: {rho:.2f}")


if __name__ == "__main__":
    main()
