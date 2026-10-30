"""Start a SUMO run of a site: network + field detectors + demand, neighbouring signals switched off.

    conn = start(site_dir, routes, begin=15 * 3600, end=19.5 * 3600)      # libsumo (fast)
    conn = start(site_dir, routes, begin, end, gui=True)                  # sumo-gui via TraCI
"""
from __future__ import annotations

from pathlib import Path


def net_file(site_dir):
    return next((Path(site_dir) / "network").glob("*v2.net.xml"))


def start(site_dir, routes, begin, end, gui=False, step=1.0, seed=1, extra=()):
    site_dir = Path(site_dir)
    if gui:
        import traci as conn
        binary = "sumo-gui"
    else:
        import libsumo as conn
        binary = "sumo"
    cmd = [binary, "-n", str(net_file(site_dir)), "-r", str(routes),
           "-a", str(site_dir / "network" / "detectors.add.xml"),
           "-b", str(begin), "-e", str(end), "--step-length", str(step), "--seed", str(seed),
           "--no-step-log", "true", "--duration-log.disable", "true",
           "--time-to-teleport", "300", *extra]
    conn.start(cmd)
    import json
    tls = json.loads((site_dir / "signal.json").read_text())["tls"]
    # the neighbouring signals (7066, 7058, 7071, 7057) are outside the study: unsignalised (GEOMETRY.md)
    for t in conn.trafficlight.getIDList():
        if t != tls:
            conn.trafficlight.setProgram(t, "off")
    return conn
