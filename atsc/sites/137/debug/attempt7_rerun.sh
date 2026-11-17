#!/bin/bash
# Attempt 7 accepted: rerun the controllers the change reaches (gdot: floating force-off; actuated: refit passage).
cd /home/andy/Downloads/GDOT
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
S=atsc/sites/137
py() { uv run python "$@" 2>&1 | grep --line-buffered -v "^Warning"; return ${PIPESTATUS[0]}; }
echo "== rerun gdot, actuated $(date)"
py $S/evaluate.py run --seeds 1 --only gdot actuated | tail -2
py $S/evaluate.py report > /dev/null
py $S/analyze.py > /dev/null
echo "ALL DONE $(date)"
