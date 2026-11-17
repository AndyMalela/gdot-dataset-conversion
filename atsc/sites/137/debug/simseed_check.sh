#!/bin/bash
# Simulation-seed check (validation days): seeds 2-4 for actuated, MaxPressure, LSTDQ v2 seed 0; seed 1 is in eval/.
cd /home/andy/Downloads/GDOT
echo "== start $(date)"
ATSC_EVAL_DIR=eval_simseeds uv run python atsc/sites/137/evaluate.py run --seeds 2 3 4 --only actuated maxpressure lstdq_v2_s0
echo "exit $?"
echo "ALL DONE $(date)"
