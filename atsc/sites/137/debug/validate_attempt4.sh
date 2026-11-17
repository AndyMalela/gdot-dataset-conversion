#!/bin/bash
# Attempt 4 (VALIDATION.md, registered 10:20): estimated presence-zone demand, then the attempt-2/3 procedure.
cd /home/andy/Downloads/GDOT
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
S=atsc/sites/137
LOG=/tmp/claude-1000/-home-andy-Downloads-GDOT/06c3c70e-5256-438b-a5d8-3dfca0e16d6a/scratchpad/events137b.log
py() { uv run python "$@" 2>&1 | grep --line-buffered -v "^Warning"; return ${PIPESTATUS[0]}; }
until grep -q DONE $LOG; do sleep 30; done
date
echo "== factors"
py tools/lanecheck/estimate_137_presence.py 1650
py tools/lanecheck/estimate_137_presence.py 1900
echo "== counts"
py tools/lanecheck/build_upstream_counts_137.py | grep -v "per day"
python3 - <<'PY'
import json
p = "atsc/sites/137/movements.json"; m = json.load(open(p))
m["counts_file_before_attempt4"] = m.get("counts_file")
m["counts_file"] = "tmc_137_5min_estimated.csv"
m["counts_note_attempt4"] = ("2026-11-16 attempt 4 (VALIDATION.md): daytime NB_L, NB_T, NB_R, SB_L, SB_T, SB_R, EB_L multiplied by "
    "per-movement factors estimated from stop-bar zone occupancy (presence_factors_1900.json); model-based estimates, not GDOT's numbers")
json.dump(m, open(p, "w"), indent=1)
print("movements.json -> tmc_137_5min_estimated.csv")
PY
echo "== audit"
py $S/audit_demand.py | tail -16
echo "== fit + validation $(date)"
py $S/validate.py fit-passage | tail -3
py $S/validate.py run | tail -2
py $S/validate.py score
mkdir -p $S/validation/attempt4
cp $S/validation/sim_splitstats.csv $S/validation/health.csv $S/validation/score.md $S/validation/passage_fit.csv $S/validation/attempt4/
cp $S/sim.json $S/validation/attempt4/sim_attempt4.json
date
echo ATTEMPT4 DONE
