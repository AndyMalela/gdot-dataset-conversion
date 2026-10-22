#!/bin/bash
# EXP-009 on the OSM network (intersections/7065osm), same days/seeds/metric as the twin run. Resumable.
cd "$(dirname "$0")/.."
set -e
S="--site 7065osm"
(cd ../../.. && uv run python tools/build_sim.py 7065osm --no-snapshot) > data_7065osm/build_sim.log 2>&1
uv run python matrix.py prepare $S > data_7065osm/prepare.log 2>&1
uv run python matrix.py train --seeds 0-4 --episodes 20 $S > data_7065osm/train.log 2>&1 &
TP=$!
uv run python matrix.py run --only real_nema,real_fixed,webster --workers 7 $S > data_7065osm/run_baselines.log 2>&1
wait $TP
uv run python matrix.py run --workers 12 $S > data_7065osm/run_rl.log 2>&1
uv run python matrix.py report $S > data_7065osm/report.log 2>&1
echo "DONE $(date)" >> data_7065osm/run_all.status
