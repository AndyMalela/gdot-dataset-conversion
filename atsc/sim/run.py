"""Start a SUMO run of a site: network + field detectors + demand, neighbouring signals switched off.

    conn = start(site_dir, routes, begin=15 * 3600, end=19.5 * 3600)      # libsumo (fast)
    conn = start(site_dir, routes, begin, end, gui=True)                  # sumo-gui via TraCI
"""
from __future__ import annotations

from pathlib import Path


def net_file(site_dir):
    """the site's network, named by network/junction.json (written by the network build script)."""
    import json
    net = Path(site_dir) / "network"
    return net / json.loads((net / "junction.json").read_text())["net_file"]


def neighbours(site_dir):
    """[(neighbour site dir, tls id)] from <site>/neighbours.json: signals simulated under their own field timing
    (e.g. 137's upstream signal 138, VALIDATION.md attempt 6). Without the file every other signal is off."""
    import json
    f = Path(site_dir) / "neighbours.json"
    if not f.exists():
        return []
    return [(Path(site_dir) / n["dir"], n["tls"]) for n in json.loads(f.read_text())["signals"]]


def start(site_dir, routes, begin, end, gui=False, step=1.0, seed=1, extra=()):
    site_dir = Path(site_dir)
    if gui:
        import traci as conn
        binary = "sumo-gui"
    else:
        import libsumo as conn
        binary = "sumo"
    import json as _json
    import os
    nb = neighbours(site_dir)
    sid = _json.loads((site_dir / "signal.json").read_text())["signal"]
    own_add = os.environ.get(f"ATSC_DETECTORS_ADD_{sid}") or str(site_dir / "network" / "detectors.add.xml")  # calibration runs
    adds = [own_add] + [str(Path(d) / "network" / "detectors.add.xml") for d, _ in nb]
    cmd = [binary, "-n", str(net_file(site_dir)), "-r", str(routes),
           "-a", ",".join(adds),
           "-b", str(begin), "-e", str(end), "--step-length", str(step), "--seed", str(seed),
           "--no-step-log", "true", "--duration-log.disable", "true",
           "--time-to-teleport", "300", *extra]
    conn.start(cmd)
    import json
    tls = json.loads((site_dir / "signal.json").read_text())["tls"]
    # any other signal in the network is outside the study: unsignalised (GEOMETRY.md)
    keep = {tls} | {t for _, t in nb}
    for t in conn.trafficlight.getIDList():
        if t not in keep:
            conn.trafficlight.setProgram(t, "off")
    return conn
