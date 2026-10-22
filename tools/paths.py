"""Where everything lives. Change folder layout here only.

intersections/<id>/counts    turning-movement counts   (atspm_tmc.py)
intersections/<id>/timing    timing plans + charts     (atspm_plans.py, atspm_timing.py)
intersections/<id>/network   SUMO network from OSM     (osm_build.py)
intersections/<id>/sim       SUMO simulation           (build_sim.py)
intersections/<id>/dataset   processed day table + profiles (dataset_7065.py)
tools/cache/                 screening downloads, not curated
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INTERSECTIONS = ROOT / "intersections"
CACHE = ROOT / "tools" / "cache"
SIGNALS_CSV = ROOT / "tools" / "atspm_signals" / "signals_all.csv"


def sig_dir(sid, stage):
    """intersections/<id>/<stage>"""
    return INTERSECTIONS / str(sid) / stage


def rel(p):
    """Path relative to the project root, for printing."""
    return Path(p).resolve().relative_to(ROOT)
