#!/bin/bash
# attempt 5 calibration grid (VALIDATION.md): permissive left-turn share, train-day windows, GDOT plan
cd /home/andy/Downloads/GDOT
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
O=atsc/sites/137/validation/attempt5; mkdir -p $O
run() { uv run python tools/lanecheck/left_turn_clearance_137.py sim "$2" 2>&1 | grep -v "^Warning" > $O/calib_$1.txt; echo "$1 done"; }
run default '{}' &
run tgm05 '{"jmTimegapMinor": 0.5}' &
run imp05 '{"impatience": 0.5}' &
run imp10 '{"impatience": 1.0}' &
run tgm05_imp05 '{"jmTimegapMinor": 0.5, "impatience": 0.5}' &
wait
echo CALIB DONE
