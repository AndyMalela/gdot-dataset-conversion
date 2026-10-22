#!/bin/bash
# Full rerun after the sigma 0.5 -> 0.2 calibration: recalibrate real timing, then EXP-009 (resumable).
cd "$(dirname "$0")/.."
set -e
(cd ../../.. && uv run python tools/build_sim.py 7065 --no-snapshot) > data/build_sim.log 2>&1
uv run python matrix.py prepare > data/prepare.log 2>&1
uv run python matrix.py train --seeds 0-4 --episodes 20 > data/train.log 2>&1 &
TP=$!
uv run python matrix.py run --only real_nema,real_fixed,webster --workers 7 > data/run_baselines.log 2>&1
wait $TP
uv run python matrix.py run --workers 12 > data/run_rl.log 2>&1
uv run python matrix.py report > data/report.log 2>&1
echo "DONE $(date)" >> data/run_all.status
