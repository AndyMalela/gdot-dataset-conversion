#!/bin/bash
# Attempt 6 (VALIDATION.md): signal 138 under its field timing upstream; refit, validation; then the methods evaluation.
cd /home/andy/Downloads/GDOT
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
S=atsc/sites/137
py() { uv run python "$@" 2>&1 | grep --line-buffered -v "^Warning"; return ${PIPESTATUS[0]}; }
until grep -q "ALL DONE" $S/debug/attempt5_and_rerun.log; do sleep 30; done
date
# archive the attempt-5 results (methods evaluation + sweep)
A=$S/archive_attempt5_model_2026-11-16; mkdir -p $A
for x in eval eval_x1.25 eval_x1.5 eval_x1.75 eval_x2.0 eval_x2.5 lstdq learners baselines; do [ -e $S/$x ] && mv $S/$x $A/; done
cp $S/sim.json $S/signal.json $A/
echo '{"signals": [{"dir": "neighbour138", "tls": "69548021"}]}' > $S/neighbours.json
py $S/make_signal.py | tail -1
py $S/neighbour138/make_signal.py $S/neighbour138/offsets.json | tail -1
echo "== attempt 6 fit + validation $(date)"
py $S/validate.py fit-passage | tail -2
py $S/validate.py run | tail -1
py $S/validate.py score
mkdir -p $S/validation/attempt6
cp $S/validation/sim_splitstats.csv $S/validation/health.csv $S/validation/score.md $S/validation/passage_fit.csv $S/validation/attempt6/
cp $S/sim.json $S/signal.json $S/neighbours.json $S/validation/attempt6/
echo "== ATTEMPT6 DONE $(date)"
echo "== rerun stage 1 $(date)"
bash $S/debug/stage1.sh > $S/debug/stage1_attempt6.log 2>&1
py $S/analyze.py > /dev/null
echo "ALL DONE $(date)"
