"""Place field-style detectors in a SUMO network from a site's detectors.json.

Stop-bar presence  -> lane-area detector (e2) of the zone length, ending at the stop line.
Setback count loop -> induction loop (e1) at `dist_m` upstream of the stop line, found by walking
                      the lane upstream through its straight predecessors, so lane-count changes
                      (turn bays, edge splits) are followed correctly.

    uv run python -m atsc.sim.detectors atsc/sites/7065
"""
import json
import sys
from pathlib import Path

import sumolib


def upstream_position(lane, dist):
    """(lane, pos) that lies `dist` m upstream of the end of `lane`, following straight predecessors."""
    left = dist
    while left > lane.getLength():
        left -= lane.getLength()
        preds = [p for p in lane.getIncoming() if p.getConnection(lane).getDirection() == "s"]
        if not preds:
            raise ValueError(f"lane {lane.getID()} has no straight predecessor; {left:.1f} m short")
        lane = min(preds, key=lambda l: abs(l.getIndex() - lane.getIndex()))
    return lane, lane.getLength() - left


def build(site_dir, net_file, out_file):
    spec = json.loads((Path(site_dir) / "detectors.json").read_text())
    net = sumolib.net.readNet(str(net_file), withInternal=False)
    zone = spec["stopbar_zone_m"]["value"]
    rows, lines = [], ["<additional>"]
    for d in spec["detectors"]:
        edge = net.getEdge(spec["approaches"][d["leg"]]["edge"])
        lane = edge.getLane(d["lane"])
        did = f"ch{d['ch']}"
        if d["kind"] == "stopbar":
            length = min(zone, lane.getLength() - 0.1)
            lines.append(f'  <laneAreaDetector id="{did}" lane="{lane.getID()}" endPos="{lane.getLength():.2f}" '
                         f'length="{length:.2f}" period="86400" file="NUL"/>')
            rows.append((did, d["phase"], "stopbar", lane.getID(), round(lane.getLength() - length, 1)))
        else:
            ln, pos = upstream_position(lane, d["dist_m"])
            lines.append(f'  <inductionLoop id="{did}" lane="{ln.getID()}" pos="{pos:.2f}" period="86400" file="NUL"/>')
            rows.append((did, d["phase"], "setback", ln.getID(), round(pos, 1)))
    lines.append("</additional>")
    Path(out_file).write_text("\n".join(lines) + "\n")
    return rows


if __name__ == "__main__":
    site = Path(sys.argv[1])
    net = site / "network" / "7065v2.net.xml" if len(sys.argv) < 3 else Path(sys.argv[2])
    out = site / "network" / "detectors.add.xml"
    for r in build(site, net, out):
        print("  %-5s P%d %-8s %-24s pos %6.1f" % r)
    print(f"wrote {out}")
