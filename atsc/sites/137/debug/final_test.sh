#!/bin/bash
# Final evaluation on the locked test days (TEST_PLAN.md). Run once, after test_schedule.py fetch + apply.
cd /home/andy/Downloads/GDOT
export ATSC_SET=test ATSC_EVAL_DIR=eval_test ATSC_FINAL_TEST=1
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
S=atsc/sites/137
ALL="gdot actuated webster maxpressure"
for m in lstdq_v2 qlearn ars; do for s in 0 1 2 3 4; do ALL="$ALL ${m}_s$s"; done; done
echo "== conditions $(date)"
uv run python $S/evaluate.py conditions
echo "== runs, simulation seeds 1-5 $(date)"
uv run python $S/evaluate.py run --seeds 1 2 3 4 5 --only $ALL 2>&1 | grep --line-buffered -v "^Warning"
echo "run exit ${PIPESTATUS[0]}"
uv run python $S/evaluate.py report > /dev/null
uv run python $S/analyze.py > /dev/null
echo "ALL DONE $(date)"
