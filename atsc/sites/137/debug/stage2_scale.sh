#!/bin/bash
# 137 stage 2 (agreed 2026-11-16 04:00): demand-scale sweep on the preliminary subset of validation days, the
# controllers of the preliminary pass (rule controllers + seed 0 of each learner, trained at x1), simulation seed 1.
# Every 5-min count of the real day is multiplied by k (atsc/sim/demand.py ATSC_DEMAND_SCALE): a labelled sensitivity
# experiment to locate the saturation region (Alegre 2020 capacity factors; Song 2026 capacity region), not real traffic.
# Starts once the preliminary report exists; runs alongside stage 1's seeds 1-4 training (shares the cores).
cd /home/andy/Downloads/GDOT
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
S=atsc/sites/137
py() { uv run python "$@" 2>&1 | grep --line-buffered -v "^Warning"; return ${PIPESTATUS[0]}; }
SUB=2026-04-20,2026-04-24,2026-04-30,2026-05-06,2026-05-12
C="gdot actuated webster maxpressure lstdq_v2_s0 qlearn_s0 ars_s0"
until [ -f $S/eval/report_preliminary.md ]; do sleep 60; done
date
for k in 1.25 1.5 1.75 2.0 2.5; do
  echo "== scale x$k $(date)"
  ATSC_DEMAND_SCALE=$k ATSC_EVAL_DIR=eval_x$k ATSC_DAYS=$SUB py $S/evaluate.py run --seeds 1 --only $C | tail -1
  ATSC_DEMAND_SCALE=$k ATSC_EVAL_DIR=eval_x$k py $S/evaluate.py conditions | tail -1
  ATSC_DEMAND_SCALE=$k ATSC_EVAL_DIR=eval_x$k py $S/evaluate.py report > /dev/null
  py $S/scale_summary.py | tail -12
done
date
echo STAGE2 DONE
