#!/usr/bin/env bash
# Multi-seed retrain for confidence intervals (EXP-003c-stat).
# Trains + evals the NEW seeds only (existing s0-4 are read in place by
# aggregate_ci.py). Idempotent/resumable: ci_worker.py skips finished work,
# so re-running after any interruption continues where it left off.
#
# Seed-MAJOR order: all variants' seed 1, then seed 2, ... so n=10 becomes
# available for every variant at roughly the same time (usable partial CIs
# long before the full n=20 finishes).
#
#   bash run_ci_batch.sh          # target n=20 (seeds up to 19)
#   PARALLEL=6 bash run_ci_batch.sh
set -u
cd "$(dirname "$0")"

MAXSEED="${MAXSEED:-19}"          # n = MAXSEED+1 (20 by default)
PARALLEL="${PARALLEL:-8}"         # concurrent workers (RAM-bounded; ~5-8GB each)

gen_tasks() {
  for s in $(seq 1 "$MAXSEED"); do
    echo "phase_gated $s ci/pg_raw/s$s"
    echo "phase_gated_norm $s ci/pg_norm/s$s"
    [ "$s" -ge 5 ] && echo "phase_gated_v3 $s ci/pg_elapsed/s$s"   # has 0-4
  done
}

echo "=== CI batch start $(date) : n=$((MAXSEED+1)), parallel=$PARALLEL ==="
gen_tasks | xargs -n3 -P"$PARALLEL" python3 ci_worker.py
echo "=== CI batch end   $(date) ==="
python3 aggregate_ci.py
