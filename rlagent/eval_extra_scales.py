"""Eval-only: add 0.5x/0.8x tripinfos to already-trained EXP-004 arms (no
retraining -- reuses saved weights). Must match each arm's exact TRAINED
config (feature_mode, enforce_max_green, max_greens) so the policy sees the
same features/constraints it was trained under; reward_mode is training-only
and irrelevant to a greedy eval.

Usage: python3 eval_extra_scales.py <feature_mode> <weights_path> <outdir> \
           [enforce] [mg15,92,30,70]
"""
from __future__ import annotations

import os
import sys

import numpy as np

from eval_heldout import eval_rl

SCALES = (0.5, 0.8)


def main():
    mode, wpath, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
    rest = sys.argv[4:]
    enforce = "enforce" in rest
    mg = next((a for a in rest if a.startswith("mg")), None)
    max_greens = [float(x) for x in mg[2:].split(",")] if mg else None

    if not os.path.exists(wpath):
        print(f"[{outdir}] NO WEIGHTS at {wpath}", flush=True)
        return
    w = np.load(wpath)
    for s in SCALES:
        ti = os.path.join(outdir, f"ti_heldout_rl_x{s}.xml")
        if os.path.exists(ti):
            continue
        eval_rl(w, s, feature_mode=mode, out=outdir,
                enforce_max_green=enforce, max_greens=max_greens)
    print(f"[{outdir}] DONE extra scales {SCALES}", flush=True)


if __name__ == "__main__":
    main()
