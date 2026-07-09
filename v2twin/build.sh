#!/usr/bin/env bash
# Build the SUMO digital twin for GDOT SIG#7065 (Peachtree Rd NE x Piedmont Rd NE).
#
# This twin is RE-DIGITIZED FROM THE AERIAL, not imported from OSM: OSM under-maps
# this intersection (the Piedmont-north leg has no lane tags and wrong geometry),
# so we picked the junction center + one centerline point per leg off a
# georeferenced satellite tile and rebuilt clean 100 m approaches with real lane
# counts. See README.md and digitize.py.
#
# Requires: SUMO (netconvert), sumolib + shapely on PYTHONPATH. No network needed
# for the build itself (the aerial picks are baked into digitize.py); the optional
# satellite re-fetch below needs internet.
set -euo pipefail
export SUMO_HOME="${SUMO_HOME:-/usr/share/sumo}"
export PYTHONPATH="$SUMO_HOME/tools:${PYTHONPATH:-}"
cd "$(dirname "$0")/.."          # repo root (GDOT/)

# (optional) refresh the georeference aerial used to pick the geometry:
# curl -s -o 7065twinv2/satellite_ref.png \
#  "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?bbox=-84.373350,33.842115,-84.369458,33.845349&bboxSR=4326&imageSR=4326&size=1000,1000&format=png&f=image"

# 1. Turn the aerial picks into plain node/edge XML (100 m legs, real lane counts).
python3 7065twinv2/digitize.py

# 2. Build the network: manual lane-use on the Peachtree approaches (NE/SW),
#    netconvert defaults elsewhere, actuated signal at J.
netconvert -n 7065twinv2/plain/7065.nod.xml -e 7065twinv2/plain/7065.edg.xml \
  -x 7065twinv2/plain/7065.con.xml \
  -o 7065twinv2/7065.net.xml \
  --no-turnarounds --tls.default-type actuated --default.lanewidth 3.2 \
  --junctions.corner-detail 6

echo "Done. Open with:  sumo-gui -c 7065twinv2/7065.sumocfg"
