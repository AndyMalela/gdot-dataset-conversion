#!/bin/bash
# Stage 3 of the demand correction: retrain the core learners on corrected demand (sorted lane insertion), then
# evaluate them and the rule controllers on the 20 validation weekdays, simulation seed 1.
# LSTDQ v2, v1, v2f x 5 training seeds one after another (22 episode workers each); Q-learning's 5 seeds alongside
# (one process each). A hung or crashed training run is stopped after 90 min and retried once.
cd /home/andy/Downloads/GDOT
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
S=atsc/sites/7065
date
for s in 0 1 2 3 4; do
  (timeout 28800 uv run python $S/train_methods.py train --method qlearn --seed $s > $S/debug/qlearn_s$s.log 2>&1; echo "qlearn s$s exit $?" >> $S/debug/stage3_qlearn.done) &
done
for v in v2 v1 v2f; do
  for s in 0 1 2 3 4; do
    echo "== lstdq $v seed $s $(date)"
    timeout 5400 uv run python $S/train_lstdq.py train --seed $s --version $v 2>&1 | grep -v "^Warning" \
      || { echo "RETRY lstdq $v seed $s"; timeout 5400 uv run python $S/train_lstdq.py train --seed $s --version $v 2>&1 | grep -v "^Warning"; }
  done
done
echo "== lstdq done $(date); waiting for qlearn"
wait
cat $S/debug/stage3_qlearn.done
date
C="gdot actuated webster maxpressure lstdq lstdq_s1 lstdq_s2 lstdq_s3 lstdq_s4"
for v in v2 v2f; do for s in 0 1 2 3 4; do C="$C lstdq_${v}_s$s"; done; done
for s in 0 1 2 3 4; do C="$C qlearn_s$s"; done
uv run python $S/evaluate.py run --seeds 1 --only $C 2>&1 | grep -v "^Warning" | tail -5
uv run python $S/evaluate.py conditions 2>&1 | grep -v "^Warning" | tail -3
uv run python $S/evaluate.py report 2>&1 | grep -v "^Warning" | tail -60
date
echo STAGE3 DONE
