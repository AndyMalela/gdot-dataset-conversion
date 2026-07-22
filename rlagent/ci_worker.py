"""One CI worker: train (resumable) + eval one (feature_mode, seed) into its own
dir, measured through the canonical peak-delay pipeline. Idempotent -- re-running
skips finished steps, so the whole batch is restartable after any interruption.

Usage:  python3 ci_worker.py <feature_mode> <seed> <out_reldir> [reward_mode]
  e.g.  python3 ci_worker.py phase_gated 3 ci/pg_raw/s3
        python3 ci_worker.py phase_gated_norm 3 ci/exp004a/s3 system
"""
from __future__ import annotations

import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from eval_heldout import eval_rl  # noqa: E402
sys.path.insert(0, os.path.join(
    HERE, "experiments", "EXP-003_spillback-features", "data"))
from peak_delay import peak_total_delay  # noqa: E402

SCALES = (1.0, 1.3, 1.8)


def main():
    mode, seed, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    reward_mode = sys.argv[4] if len(sys.argv) > 4 else "queue"
    # optional trailing flags: "enforce" (hard max-green), "hi<scale>"
    # (training scale-hi override), e.g. ... system enforce hi1.6
    enforce = "enforce" in sys.argv[5:]
    scale_hi = next((a[2:] for a in sys.argv[5:] if a.startswith("hi")), None)
    ridge = next((a[1:] for a in sys.argv[5:]
                  if a.startswith("r") and a != "ridge"), None)
    max_greens = next((a[2:] for a in sys.argv[5:] if a.startswith("mg")), None)
    absdir = os.path.join(HERE, out)
    os.makedirs(absdir, exist_ok=True)
    weights = os.path.join(absdir, f"weights_random_s{seed}.npy")
    tis = {s: os.path.join(absdir, f"ti_heldout_rl_x{s}.xml") for s in SCALES}

    # --- train to a VERIFIED 20 episodes -----------------------------------
    # Always run train_random with --resume (idempotent: resumes to 20 via the
    # per-episode checkpoint, or a fast no-op if already complete). Do NOT skip
    # on the weights file existing -- train_random saves weights EVERY episode,
    # so a partially-trained seed has a weights file but only k<20 episodes;
    # skipping on it would silently evaluate an UNDER-trained agent (fidelity
    # bug). After training, verify the episode count before trusting it.
    csv = os.path.join(absdir, f"train_random_s{seed}.csv")

    def episodes_done() -> int:
        if not os.path.exists(csv):
            return 0
        with open(csv) as fh:
            return max(0, sum(1 for _ in fh) - 1)   # minus header

    if episodes_done() < 20:
        cmd = [sys.executable, os.path.join(HERE, "train_random.py"),
               "--seed", str(seed), "--feature-mode", mode,
               "--reward-mode", reward_mode,
               "--out", out, "--episodes", "20", "--no-eval",
               "--checkpoint-every", "1", "--resume"]
        if enforce:
            cmd.append("--enforce-max-green")
        if scale_hi:
            cmd += ["--scale-hi", scale_hi]
        if ridge:
            cmd += ["--ridge", ridge]
        if max_greens:
            cmd += ["--max-greens", max_greens]
        print(f"[{mode} s{seed}] TRAIN -> {out} (from ep {episodes_done()})",
              flush=True)
        r = subprocess.run(cmd, cwd=HERE)
        if r.returncode != 0 or episodes_done() < 20 or not os.path.exists(weights):
            print(f"[{mode} s{seed}] TRAIN INCOMPLETE "
                  f"(rc={r.returncode}, eps={episodes_done()}); resume next run",
                  flush=True)
            sys.exit(1)

    # --- eval RL at each scale (skip existing tripinfos) --------------------
    w = np.load(weights)
    for s in SCALES:
        if not os.path.exists(tis[s]):
            print(f"[{mode} s{seed}] EVAL x{s}", flush=True)
            eval_rl(w, s, feature_mode=mode, out=out,
                    enforce_max_green=enforce,
                    max_greens=([float(x) for x in max_greens.split(",")]
                                if max_greens else None))

    # --- report canonical peak total delay ----------------------------------
    row = " ".join(f"x{s}={peak_total_delay(tis[s])[1]:.0f}" for s in SCALES)
    print(f"[{mode} s{seed}] DONE  {row}", flush=True)


if __name__ == "__main__":
    main()
