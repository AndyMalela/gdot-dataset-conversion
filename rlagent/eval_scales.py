"""Eval-only: run an already-trained seed's greedy policy at extra demand
scales (default 0.5, 0.8), writing tripinfos into the same dir the aggregator
reads. No training -- reuses the saved weights from the n=20 batch. Idempotent
(skips scales whose tripinfo already exists).

Usage:  python3 eval_scales.py <variant> <seed> [scale ...]
  e.g.  python3 eval_scales.py pg_raw 7 0.5 0.8
"""
from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from eval_heldout import eval_rl  # noqa: E402

FEATMODE = {"pg_raw": "phase_gated", "pg_norm": "phase_gated_norm",
            "pg_elapsed": "phase_gated_v3"}


def resolve(variant, seed):
    """(weights_reldir/file, out_reldir) -- existing seeds live under results/,
    new seeds under ci/. Must match aggregate_ci.py / finalize_ci.py LOC."""
    if variant == "pg_raw":
        if seed == 0:
            return "results/weights_random_s0.npy", "results/exp002_phasegated"
        return (f"ci/pg_raw/s{seed}/weights_random_s{seed}.npy",
                f"ci/pg_raw/s{seed}")
    if variant == "pg_norm":
        if seed == 0:
            return ("results/exp003_norm/weights_random_s0.npy",
                    "results/exp003_norm")
        return (f"ci/pg_norm/s{seed}/weights_random_s{seed}.npy",
                f"ci/pg_norm/s{seed}")
    if variant == "pg_elapsed":
        if seed == 0:
            return ("results/exp003_v3/weights_random_s0.npy",
                    "results/exp003b_v3/s0")
        if 1 <= seed <= 4:
            return (f"results/exp003b_v3/weights_random_s{seed}.npy",
                    f"results/exp003b_v3/s{seed}")
        return (f"ci/pg_elapsed/s{seed}/weights_random_s{seed}.npy",
                f"ci/pg_elapsed/s{seed}")
    raise SystemExit(f"unknown variant {variant}")


def main():
    variant, seed = sys.argv[1], int(sys.argv[2])
    scales = [float(x) for x in sys.argv[3:]] or [0.5, 0.8]
    wrel, outdir = resolve(variant, seed)
    wpath = os.path.join(HERE, wrel)
    if not os.path.exists(wpath):
        print(f"[{variant} s{seed}] NO WEIGHTS at {wrel}", flush=True)
        sys.exit(1)
    w = np.load(wpath)
    for sc in scales:
        ti = os.path.join(HERE, outdir, f"ti_heldout_rl_x{sc}.xml")
        if os.path.exists(ti):
            continue
        eval_rl(w, sc, feature_mode=FEATMODE[variant], out=outdir)
    print(f"[{variant} s{seed}] DONE scales={scales}", flush=True)


if __name__ == "__main__":
    main()
