#!/bin/bash
# Attempt 5 (VALIDATION.md): calibrated vtype impatience 0.5 (rule winner), controller refit, validation; then the
# methods evaluation rerun on this model (stage 1 + demand sweep), pass or fail, as registered.
cd /home/andy/Downloads/GDOT
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
S=atsc/sites/137
py() { uv run python "$@" 2>&1 | grep --line-buffered -v "^Warning"; return ${PIPESTATUS[0]}; }
date
python3 - <<'PY'
import json
p = "atsc/sites/137/sim.json"; c = json.load(open(p))
c["vtype"] = {"impatience": 0.5}
c["vtype_source"] = ("2026-11-16 attempt 5 (VALIDATION.md): calibration grid on train-day windows against the field share of "
                     "left-turners clearing permissively; impatience 0.5 won by the registered rule (mean |diff| 0.135 vs 0.167 default)")
json.dump(c, open(p, "w"), indent=1); print("sim.json vtype -> impatience 0.5")
PY
echo "== attempt 5 fit + validation $(date)"
py $S/validate.py fit-passage | tail -2
py $S/validate.py run | tail -1
py $S/validate.py score
mkdir -p $S/validation/attempt5
cp $S/validation/sim_splitstats.csv $S/validation/health.csv $S/validation/score.md $S/validation/passage_fit.csv $S/validation/attempt5/
cp $S/sim.json $S/validation/attempt5/sim_attempt5.json
echo "== ATTEMPT5 DONE $(date)"
# archive the attempt-1-model results, then rerun the methods evaluation and the sweep on this model
A=$S/archive_attempt1_model_2026-11-16; mkdir -p $A
for x in eval eval_x1.25 eval_x1.5 eval_x1.75 eval_x2.0 eval_x2.5 lstdq learners baselines; do [ -e $S/$x ] && mv $S/$x $A/; done
cp $S/debug/stage1.log $S/debug/stage2.log $A/ 2>/dev/null
echo "== rerun stage 1 $(date)"
bash $S/debug/stage1.sh > $S/debug/stage1_attempt5.log 2>&1
echo "== rerun stage 2 $(date)"
bash $S/debug/stage2_scale.sh > $S/debug/stage2_attempt5.log 2>&1
echo "ALL DONE $(date)"
