#!/bin/bash
# 137 stage 1 (2026-11-16, agreed 03:50): methods comparison on the March-May data with WB through from signal 138.
#   A. data: corrected counts, signal from the per-day plan reads, demand audit, Webster design
#   B. preliminary: one training seed per learner (LSTDQ, linear Q-learning, ARS), evaluated with the rule
#      controllers on a pre-chosen subset of validation weekdays (every 4th usable one), report
#   C. full: seeds 1-4 of each learner, every usable validation weekday, report
# DQN held until after the midterm; NFQ dropped (decision 2026-11-16 03:45).
cd /home/andy/Downloads/GDOT
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
S=atsc/sites/137
py() { uv run python "$@" 2>&1 | grep --line-buffered -v "^Warning"; return ${PIPESTATUS[0]}; }
date
until ! pgrep -f "[a]tspm_tmc.py 13[78]" >/dev/null && ! pgrep -f "[a]tspm_plans.py 137" >/dev/null; do sleep 30; done
echo "== A. data $(date)"
py tools/lanecheck/build_upstream_counts_137.py
py $S/make_signal.py | tail -2
py $S/audit_demand.py | tail -22
py $S/baselines.py design
SUB=$(uv run python - <<'EOF' 2>/dev/null
import sys; sys.path.insert(0, "atsc/sites/137"); sys.path.insert(0, ".")
from baselines import days
v = days("validation"); print(",".join(str(d) for d in v[::4]))
EOF
)
echo "preliminary validation subset: $SUB"
echo "== B. preliminary, seed 0 $(date)"
timeout 3600 uv run python $S/train_lstdq.py train --seed 0 --version v2 2>&1 | grep -v "^Warning" | tail -2
(timeout 7200 uv run python $S/train_methods.py train --method qlearn --seed 0 > $S/debug/qlearn_s0.log 2>&1; echo "qlearn s0 exit $?") &
timeout 7200 uv run python $S/train_methods.py train --method ars --seed 0 > $S/debug/ars_s0.log 2>&1; echo "ars s0 exit $?"
wait
echo "== B. evaluation on the subset $(date)"
ATSC_DAYS=$SUB py $S/evaluate.py run --seeds 1 --only gdot actuated webster maxpressure lstdq_v2_s0 qlearn_s0 ars_s0 | tail -2
py $S/evaluate.py conditions | tail -1
py $S/evaluate.py report > /dev/null && cp $S/eval/report.md $S/eval/report_preliminary.md
echo "== B. DONE: $S/eval/report_preliminary.md $(date)"
echo "== C. full, seeds 1-4 $(date)"
for s in 1 2 3 4; do
  timeout 3600 uv run python $S/train_lstdq.py train --seed $s --version v2 2>&1 | grep -v "^Warning" | tail -1
done
for s in 1 2 3 4; do
  (timeout 7200 uv run python $S/train_methods.py train --method qlearn --seed $s > $S/debug/qlearn_s$s.log 2>&1; echo "qlearn s$s exit $?") &
done
for s in 1 2 3 4; do
  timeout 7200 uv run python $S/train_methods.py train --method ars --seed $s > $S/debug/ars_s$s.log 2>&1; echo "ars s$s exit $?"
done
wait
C="gdot actuated webster maxpressure"
for s in 0 1 2 3 4; do C="$C lstdq_v2_s$s qlearn_s$s ars_s$s"; done
echo "== C. evaluation, all validation weekdays $(date)"
py $S/evaluate.py run --seeds 1 --only $C | tail -2
py $S/evaluate.py conditions | tail -1
py $S/evaluate.py report | head -40
date
echo STAGE1 DONE
