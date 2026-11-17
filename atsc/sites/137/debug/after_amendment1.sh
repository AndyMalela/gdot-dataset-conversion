#!/bin/bash
# Post hoc, after amendment 1 (user 2026-11-17 "ok lets do it"): validation days only, never test days.
# 1) Isolation of LSTDQ's change (simulation seed 1, 20 validation days, 5 training seeds):
#    (a) eval_iso_oldw: attempt-7 weights (archive_before_amendment1, final iterate 5) on the fixed engine / attempt-8 model
#    (b) eval_iso_last: attempt-8 weights, final iterate 5 instead of the selected one
#    actuated is rerun in each folder so every ratio is paired within one folder.
# 2) Demand-scale sweep on the attempt-8 model, same design as stage 2 (debug/stage2_scale.sh): 5 validation days,
#    simulation seed 1, every 5-min count x k. x1.25 and x1.5 (controllers still comparable): all 19 controllers
#    (learners at their selected iterates); x1.75-2.5 (all oversaturated before): the stage-2 set (seed 0 learners).
#    Learners trained at x1 only: robustness to unseen demand (Chen 2025, Song 2026 design), not control at saturation.
cd /home/andy/Downloads/GDOT
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
S=atsc/sites/137
py() { uv run python "$@" 2>&1 | grep --line-buffered -v "^Warning"; return ${PIPESTATUS[0]}; }
until grep -q "ALL DONE" $S/debug/amendment1.log; do sleep 60; done
L="lstdq_v2_s0 lstdq_v2_s1 lstdq_v2_s2 lstdq_v2_s3 lstdq_v2_s4"
echo "== isolation (a) old weights, fixed engine $(date)"
ATSC_LSTDQ_ROOT=archive_before_amendment1_2026-11-17 ATSC_LSTDQ_IT=5 ATSC_EVAL_DIR=eval_iso_oldw \
  py $S/evaluate.py run --seeds 1 --only actuated $L | tail -1
echo "== isolation (b) new weights, final iterate $(date)"
ATSC_LSTDQ_IT=5 ATSC_EVAL_DIR=eval_iso_last py $S/evaluate.py run --seeds 1 --only actuated $L | tail -1
SUB=2026-04-20,2026-04-24,2026-04-30,2026-05-06,2026-05-12
ALL="gdot actuated webster maxpressure $L qlearn_s0 qlearn_s1 qlearn_s2 qlearn_s3 qlearn_s4 ars_s0 ars_s1 ars_s2 ars_s3 ars_s4"
C7="gdot actuated webster maxpressure lstdq_v2_s0 qlearn_s0 ars_s0"
for k in 1.25 1.5 1.75 2.0 2.5; do
  echo "== scale x$k $(date)"
  C=$C7; [ "$k" = 1.25 -o "$k" = 1.5 ] && C=$ALL
  ATSC_DEMAND_SCALE=$k ATSC_EVAL_DIR=eval_x$k ATSC_DAYS=$SUB py $S/evaluate.py run --seeds 1 --only $C | tail -1
  ATSC_DEMAND_SCALE=$k ATSC_EVAL_DIR=eval_x$k py $S/evaluate.py conditions | tail -1
  ATSC_DEMAND_SCALE=$k ATSC_EVAL_DIR=eval_x$k py $S/evaluate.py report > /dev/null
done
py $S/scale_summary.py | tail -25
echo "AFTER DONE $(date)"
