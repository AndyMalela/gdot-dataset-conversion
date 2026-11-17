#!/bin/bash
# Retrain the learners that use the actuated controller during training (LSTDQ: behaviour policy every iteration;
# Q-learning: iteration 0) on the accepted attempt-7 model, 5 seeds each; re-evaluate on all validation weekdays.
# ARS uses no behaviour policy: its attempt-6 weights and runs stand. Old weights: archive_attempt6_model_2026-11-17/.
cd /home/andy/Downloads/GDOT
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
S=atsc/sites/137
py() { uv run python "$@" 2>&1 | grep --line-buffered -v "^Warning"; return ${PIPESTATUS[0]}; }
echo "== LSTDQ v2 seeds 0-4 $(date)"
for s in 0 1 2 3 4; do
  timeout 3600 uv run python $S/train_lstdq.py train --seed $s --version v2 2>&1 | grep -v "^Warning" | tail -1; echo "lstdq s$s exit ${PIPESTATUS[0]}"
done
echo "== Q-learning seeds 0-4 $(date)"
for s in 0 1 2 3 4; do
  (timeout 7200 uv run python $S/train_methods.py train --method qlearn --seed $s > $S/debug/qlearn_a7_s$s.log 2>&1; echo "qlearn s$s exit $?") &
done
wait
C=""
for s in 0 1 2 3 4; do C="$C lstdq_v2_s$s qlearn_s$s"; done
echo "== evaluation, all validation weekdays $(date)"
py $S/evaluate.py run --seeds 1 --only $C | tail -2
py $S/evaluate.py report > /dev/null
py $S/analyze.py > /dev/null
echo "ALL DONE $(date)"
