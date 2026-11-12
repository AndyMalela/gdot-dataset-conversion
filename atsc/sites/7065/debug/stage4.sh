#!/bin/bash
# Stage 4 of the demand correction: the remaining learners (ARS, NFQ, NFQ to convergence, DQN last) and
# simulation seeds 2-3. Started by hand after stage 3 has been read.
#   a. ARS, NFQ: 5 training seeds one after another (22 episode workers each)
#   b. NFQ to convergence: 5 seeds side by side (4 episode workers each; the fit dominates)
#   c. evaluate ARS, NFQ, NFQ-conv on simulation seed 1
#   d. DQN: 5 seeds side by side (one process each), with the seed 2-3 evaluation of everything else alongside
#   e. evaluate DQN on simulation seeds 1-3
# A hung training run is stopped by its timeout and retried once.
cd /home/andy/Downloads/GDOT
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
S=atsc/sites/7065
py() { uv run python "$@" 2>&1 | grep --line-buffered -v "^Warning"; return ${PIPESTATUS[0]}; }
date
for m in ars nfq; do
  for s in 0 1 2 3 4; do
    echo "== $m seed $s $(date)"
    timeout 7200 uv run python $S/train_methods.py train --method $m --seed $s > $S/debug/${m}_s$s.log 2>&1 \
      || { echo "RETRY $m seed $s"; timeout 7200 uv run python $S/train_methods.py train --method $m --seed $s > $S/debug/${m}_s$s.log 2>&1; }
    grep -v "^Warning" $S/debug/${m}_s$s.log | tail -1
  done
done
echo "== nfq_conv x5 $(date)"
for s in 0 1 2 3 4; do
  (ATSC_POOL=4 timeout 43200 uv run python $S/train_methods.py train --method nfq_conv --seed $s > $S/debug/nfq_conv_s$s.log 2>&1; echo "nfq_conv s$s exit $?") &
done
wait
date
ALL="gdot actuated webster maxpressure lstdq lstdq_s1 lstdq_s2 lstdq_s3 lstdq_s4"
for v in v2 v2f; do for s in 0 1 2 3 4; do ALL="$ALL lstdq_${v}_s$s"; done; done
for m in qlearn ars nfq nfq_conv; do for s in 0 1 2 3 4; do ALL="$ALL ${m}_s$s"; done; done
echo "== evaluation, simulation seed 1 $(date)"
py $S/evaluate.py run --seeds 1 --only $ALL | tail -2
py $S/evaluate.py report | tail -40
echo "== dqn x5 + evaluation seeds 2-3 $(date)"
for s in 0 1 2 3 4; do
  (timeout 86400 uv run python $S/train_methods.py train --method dqn --seed $s > $S/debug/dqn_s$s.log 2>&1; echo "dqn s$s exit $?") &
done
py $S/evaluate.py run --seeds 2 3 --only $ALL | tail -2
py $S/evaluate.py report | tail -40
echo "== seeds 2-3 done $(date); waiting for dqn"
wait
date
py $S/evaluate.py run --seeds 1 2 3 --only dqn_s0 dqn_s1 dqn_s2 dqn_s3 dqn_s4 | tail -2
py $S/evaluate.py report | tail -60
date
echo STAGE4 DONE
