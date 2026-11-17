#!/bin/bash
# Attempt 7 (VALIDATION.md): floating force-off for P1/P5 (force_off_mode.py); refit passage on train days; validation.
cd /home/andy/Downloads/GDOT
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
S=atsc/sites/137
py() { uv run python "$@" 2>&1 | grep --line-buffered -v "^Warning"; return ${PIPESTATUS[0]}; }
echo "== attempt 7 fit + validation $(date)"
py $S/validate.py fit-passage | tail -2
py $S/validate.py run | tail -1
py $S/validate.py score
mkdir -p $S/validation/attempt7
cp $S/validation/sim_splitstats.csv $S/validation/health.csv $S/validation/score.md $S/validation/passage_fit.csv $S/validation/attempt7/
cp $S/sim.json $S/signal.json $S/neighbours.json $S/force_off.json $S/validation/attempt7/
echo "== ATTEMPT7 DONE $(date)"
