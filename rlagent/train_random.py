"""Domain-randomized LSTDQ training: demand SCALE x DAY per episode.

Rationale (confirmed against the data, not just asserted): the 4 calibrated
days differ in *shape*, not only level -- e.g. 0507/0508 carry heavy
late-night traffic (56-132 veh/bin overnight) while 0505 is light -- so a
single day scaled up/down would freeze one day's directional split / burst
shape at every demand level and never cover the others. Each episode
therefore draws BOTH a random real day (shape variation) AND a random scale
(saturation-level variation).

- Train days: 0505, 0506, 0507 (sampled per episode).
- Held out entirely: 0508 -- used only for the generalization eval at the
  end, never seen during training at any scale.
- Window: FULL DAY (00:00-24:00). Training on the whole day (not just the
  PM peak) fixes the earlier unfairness where a peak-trained agent was
  evaluated across ~20 h of off-peak it had never seen and degenerated on
  near-empty roads. The agent now trains on light, building, peak, and
  overnight conditions -- which also injects within-day shape variation
  (AM inbound vs PM outbound vs balanced midday) on top of the cross-day
  variation.
- Sensor-outage masking: 0505 (23:05-24:00) and 0506 (00:00-04:10) read a
  false exact-zero across all movements -- a ~5 h detector blackout
  spanning the midnight rollover, NOT genuine zero traffic (0505's own
  3 AM shows 6-12 veh/bin; 0507/0508 overnight 56-132; verified 2026-07-11
  against the raw portal files). Those transitions are dropped from the fit
  so the agent doesn't learn ~5 h of false-empty road. See OUTAGE below.
- Scale range 0.5-1.3; the held-out eval additionally probes 1.5-1.8 to see
  how far the policy extrapolates beyond the trained range -- flagged as
  extrapolation, not validated generalization.

Same accumulated-experience LSTDQ loop as train.py; only the per-episode
demand source changes. NOTE: full-day episodes carry ~8x the transitions of
the old 3 h peak window, and experience accumulates LSPI-style across
episodes, so runtime/memory grow with episode count -- the default episode
count is lowered accordingly (raise it if you have the budget).
"""

from __future__ import annotations

import argparse
import csv
import os
import time

import numpy as np

import metrics
import stages as st
from lstdq import LinearQ
from sumo_env import Sig7065Env
from train import run_episode
from trainutil import Progress, load_checkpoint, save_checkpoint

HERE = os.path.dirname(os.path.abspath(__file__))
TRAIN_DATES = ["0505", "0506", "0507"]
HELD_OUT_DATE = "0508"
DRAIN_END = 108000   # 30:00 -- drain scaled full-day demand for a clean eval

# Sensor-outage windows (seconds past midnight) to exclude from the fit --
# false exact-zero blocks, not genuine demand (see module docstring).
OUTAGE = {"0505": (83100, 86400), "0506": (0, 15300)}


def outage_skip(date: str):
    w = OUTAGE.get(date)
    if w is None:
        return None
    lo, hi = w
    return lambda t: lo <= t < hi


def rou_path(date: str) -> str:
    return os.path.join(HERE, "..", "sumodemand", f"{date}.rou.xml")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--begin", type=int, default=0)        # 00:00 (full day)
    p.add_argument("--end", type=int, default=86400)      # 24:00
    p.add_argument("--episodes", type=int, default=20)
    p.add_argument("--scale-lo", type=float, default=0.5)
    p.add_argument("--scale-hi", type=float, default=1.3)
    p.add_argument("--eps", type=float, default=0.05)
    p.add_argument("--gamma", type=float, default=0.99)
    p.add_argument("--ridge", type=float, default=1e-4)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", default="results")
    p.add_argument("--resume", action="store_true",
                   help="resume from checkpoint_s<seed>.pkl if present")
    p.add_argument("--checkpoint-every", type=int, default=1,
                   help="save a resumable checkpoint every N episodes")
    p.add_argument("--feature-mode", default="phase_gated",
                   help="state features: flat | phase_gated | "
                        "phase_gated_norm | phase_gated_v3 (see sumo_env)")
    args = p.parse_args()

    outdir = os.path.join(HERE, args.out)
    os.makedirs(outdir, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    env = Sig7065Env(rou_path(TRAIN_DATES[0]), begin=args.begin, end=args.end,
                     seed=args.seed, label="train_rand",
                     feature_mode=args.feature_mode)
    env.reset()
    agent = LinearQ(env.n_state_features, st.N_ACTIONS, seed=args.seed)
    env.close()
    print(f"feature_mode={args.feature_mode}  n_features={env.n_state_features}"
          f"  params={env.n_state_features * st.N_ACTIONS}")

    log_path = os.path.join(outdir, f"train_random_s{args.seed}.csv")
    weights_path = os.path.join(outdir, f"weights_random_s{args.seed}.npy")
    ckpt_path = os.path.join(outdir, f"checkpoint_s{args.seed}.pkl")

    # --- resume or start fresh -------------------------------------------
    experience = []
    start_ep = 1
    prog = Progress(args.episodes)
    if args.resume and os.path.exists(ckpt_path):
        done_ep, w_ckpt, experience, rng_state, best = load_checkpoint(ckpt_path)
        agent.w = np.asarray(w_ckpt)
        rng.bit_generator.state = rng_state
        prog.best, prog.done = best, done_ep
        start_ep = done_ep + 1
        print(f"resumed from checkpoint: {done_ep} episodes done, "
              f"{len(experience)} transitions, best={best:.0f}")
    elif args.resume:
        print("--resume given but no checkpoint found; starting fresh")

    log_mode = "a" if start_ep > 1 and os.path.exists(log_path) else "w"
    f = open(log_path, log_mode, newline="")
    writer = csv.writer(f)
    if log_mode == "w":
        writer.writerow(["episode", "date", "scale", "total_reward",
                         "decisions", "switches", "wall_s"])

    span = max(1, args.end - args.begin)
    completed = start_ep - 1   # episodes whose transitions are in `experience`
    try:
        for ep in range(start_ep, args.episodes + 1):
            date = TRAIN_DATES[rng.integers(len(TRAIN_DATES))]
            scale = float(rng.uniform(args.scale_lo, args.scale_hi))
            env.reset(rou_xml=rou_path(date), scale=scale,
                      seed=args.seed * 1000 + ep)
            prog.start_episode(ep, date, scale)
            t0 = time.time()
            tr, tot_r, n_steps, n_sw = run_episode(
                env, agent, args.eps, rng, skip=outage_skip(date),
                on_step=lambda t: prog.step((t - args.begin) / span, t))
            experience.extend(tr)
            agent.lstdq_update(experience, gamma=args.gamma, ridge=args.ridge)
            completed = ep
            wall = time.time() - t0
            writer.writerow([ep, date, f"{scale:.2f}", f"{tot_r:.0f}",
                             n_steps, n_sw, f"{wall:.1f}"])
            f.flush()
            prog.end_episode(tot_r, n_steps, n_sw)
            # weights every episode (cheap); full resumable checkpoint per N
            np.save(weights_path, agent.w)
            if ep % args.checkpoint_every == 0:
                save_checkpoint(ckpt_path, ep, agent.w, experience, rng, prog.best)
    except KeyboardInterrupt:
        # `completed` (not the in-progress ep) is the last episode actually in
        # `experience`, so resume re-runs the interrupted one rather than
        # skipping it. rng state is saved as-of now; the re-drawn day/scale for
        # the interrupted episode differs, which is fine (it was never used).
        if completed >= 1:
            save_checkpoint(ckpt_path, completed, agent.w, experience, rng,
                            prog.best)
        f.close()
        env.close()
        print(f"\ninterrupted; {completed} episodes checkpointed to "
              f"{os.path.basename(ckpt_path)}. Resume with --resume.")
        return
    f.close()

    np.save(weights_path, agent.w)
    save_checkpoint(ckpt_path, ep, agent.w, experience, rng, prog.best)

    # Held-out generalization: 0508 was never seen during training, at
    # in-range (1.0) and beyond-range (1.5, 1.8 -- extrapolation) scales.
    # Full day, drained to DRAIN_END so scaled demand clears and metrics
    # aren't truncation-biased (the bug eval_heldout.py was built to fix).
    # 0508 has no outage window, so no masking needed here.
    print("\n--- held-out generalization: 0508 (never trained on) ---")
    for eval_scale in (1.0, 1.5, 1.8):
        ti = os.path.join(outdir, f"tripinfo_random_0508_x{eval_scale}.xml")
        eval_env = Sig7065Env(
            rou_path(HELD_OUT_DATE), begin=0, end=DRAIN_END,
            seed=9999, scale=eval_scale, label=f"eval_{eval_scale}", tripinfo=ti,
            feature_mode=args.feature_mode)
        obs = eval_env.reset()
        done = False
        while not done:
            res = eval_env.step(agent.greedy(obs))
            obs, done = res.state, res.done
        eval_env.close()
        m = metrics.read_tripinfo(ti)
        tag = "in-range" if eval_scale <= args.scale_hi else "EXTRAPOLATION"
        print(f"  scale={eval_scale:.1f} ({tag:13s}): {m.row()}")

    print(f"\nlog: {log_path}")
    print("For the rigorous RL-vs-fixed-time held-out comparison, run "
          "eval_heldout.py (also full-day, drained).")


if __name__ == "__main__":
    main()
