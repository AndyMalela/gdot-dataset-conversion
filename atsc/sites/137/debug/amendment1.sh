#!/bin/bash
# TEST_PLAN.md amendment 1: post-test bug-fix pass (F1 engine, F2 scoring, F3 saturation flow, F4 iterate selection).
cd /home/andy/Downloads/GDOT
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
S=atsc/sites/137
A=$S/archive_before_amendment1_2026-11-17
py() { uv run python "$@" 2>&1 | grep --line-buffered -v "^Warning"; return ${PIPESTATUS[0]}; }
set -o pipefail
echo "== archive $(date)"
mkdir -p $A/learners $A/lstdq
mv $S/eval $S/eval_test $S/eval_simseeds $A/
cp -r $S/lstdq/v2 $A/lstdq/ && cp -r $S/learners/qlearn $S/learners/ars $A/learners/
cp $S/sim.json $S/signal.json $S/baselines/webster.json $A/
echo "== F3 saturation flow $(date)"
py $S/sat_flow.py || exit 1
echo "== attempt 8: fit + validation $(date)"
py $S/validate.py fit-passage | tail -2
py $S/validate.py run | tail -1
py $S/validate.py score | tail -60
mkdir -p $S/validation/attempt8
cp $S/validation/sim_splitstats.csv $S/validation/health.csv $S/validation/score.md $S/validation/passage_fit.csv $S/validation/attempt8/
cp $S/sim.json $S/signal.json $S/neighbours.json $S/force_off.json $S/validation/attempt8/
echo "== Webster redesign $(date)"
py $S/baselines.py design | tail -8
echo "== LSTDQ v2 seeds 0-4 $(date)"
for s in 0 1 2 3 4; do
  timeout 3600 uv run python $S/train_lstdq.py train --seed $s --version v2 2>&1 | grep -v "^Warning" | tail -1
  echo "lstdq s$s exit ${PIPESTATUS[0]}"
done
echo "== Q-learning x5 (parallel) + ARS seeds 0-4 $(date)"
for s in 0 1 2 3 4; do
  (timeout 7200 uv run python $S/train_methods.py train --method qlearn --seed $s > $S/debug/qlearn_a8_s$s.log 2>&1; echo "qlearn s$s exit $?") &
done
for s in 0 1 2 3 4; do
  timeout 7200 uv run python $S/train_methods.py train --method ars --seed $s > $S/debug/ars_a8_s$s.log 2>&1; echo "ars s$s exit $?"
done
wait
echo "== F4 iterate selection $(date)"
py $S/select_iterate.py | tail -20
ALL="gdot actuated webster maxpressure"
for m in lstdq_v2 qlearn ars; do for s in 0 1 2 3 4; do ALL="$ALL ${m}_s$s"; done; done
echo "== validation evaluation, seed 1 $(date)"
py $S/evaluate.py conditions | tail -1
py $S/evaluate.py run --seeds 1 --only $ALL | tail -1
py $S/evaluate.py report > /dev/null
py $S/analyze.py > /dev/null
echo "== test evaluation, seeds 1-5 $(date)"
export ATSC_SET=test ATSC_EVAL_DIR=eval_test ATSC_FINAL_TEST=1
py $S/evaluate.py conditions | tail -1
py $S/evaluate.py run --seeds 1 2 3 4 5 --only $ALL | tail -1
py $S/evaluate.py report > /dev/null
py $S/analyze.py > /dev/null
echo "ALL DONE $(date)"
