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
    """(lane, pos) that lies `dist` m upstream of the end of `lane`, following straight predecessors.
    The junction area between two edges (e.g. a lane-count change) counts too, as the gap between their shapes."""
    left = dist
    while left > lane.getLength():
        left -= lane.getLength()
        preds = [p for p in lane.getIncoming() if p.getConnection(lane).getDirection() == "s"]
        if not preds:
            raise ValueError(f"lane {lane.getID()} has no straight predecessor; {left:.1f} m short")
        pred = min(preds, key=lambda l: abs(l.getIndex() - lane.getIndex()))
        left -= sumolib.geomhelper.distance(pred.getShape()[-1], lane.getShape()[0])
        lane = pred
    return lane, min(lane.getLength() - 0.1, max(0.0, lane.getLength() - left))


def build(site_dir, net_file, out_file, zone_override=None, spec=None):
    """zone_override: stop-bar zone length in m for every zone (calibration runs); otherwise a detector's own
    "zone_m" if set, else the site default stopbar_zone_m."""
    spec = spec or json.loads((Path(site_dir) / "detectors.json").read_text())
    net = sumolib.net.readNet(str(net_file), withInternal=True)
    default_zone = spec["stopbar_zone_m"]["value"]
    rows, lines = [], ["<additional>"]
    for d in [d for d in spec["detectors"] if d.get("modelled", True)]:     # advance radar: not modelled yet
        zone = zone_override if zone_override is not None else d.get("zone_m", default_zone)
        edge = net.getEdge(spec["approaches"][d["leg"]]["edge"])
        lane = edge.getLane(d["lane"])
        did = f"ch{d['ch']}"
        into = d.get("into_junction")
        if d["kind"] == "stopbar" and into == "waiting_point":
            # zone continues past the stop line over the turn's first internal lane, up to SUMO's waiting point for
            # permissive turners (where a left turner stops to wait for a gap inside the junction)
            via = next(c.getViaLaneID() for c in lane.getOutgoing() if c.getDirection() in ("l", "L"))
            vl = net.getLane(via)
            pos = max(0.0, lane.getLength() - zone)
            lines.append(f'  <laneAreaDetector id="{did}" lanes="{lane.getID()} {via}" pos="{pos:.2f}" '
                         f'endPos="{vl.getLength():.2f}" period="86400" file="NUL"/>')
            rows.append((did, d["phase"], "stopbar", f"{lane.getID()}+{via}", round(pos, 1)))
        elif d["kind"] == "stopbar" and zone <= lane.getLength() - 0.1:
            lines.append(f'  <laneAreaDetector id="{did}" lane="{lane.getID()}" endPos="{lane.getLength():.2f}" '
                         f'length="{zone:.2f}" period="86400" file="NUL"/>')
            rows.append((did, d["phase"], "stopbar", lane.getID(), round(lane.getLength() - zone, 1)))
        elif d["kind"] == "stopbar":         # stop-line edge shorter than the zone (NE: slip-lane split 6 m upstream)
            up, pos = upstream_position(lane, zone)
            lines.append(f'  <laneAreaDetector id="{did}" lanes="{up.getID()} {lane.getID()}" pos="{pos:.2f}" '
                         f'endPos="{lane.getLength():.2f}" period="86400" file="NUL"/>')
            rows.append((did, d["phase"], "stopbar", f"{up.getID()}+{lane.getID()}", round(pos, 1)))
        else:
            ln, pos = upstream_position(lane, d["dist_m"])
            lines.append(f'  <inductionLoop id="{did}" lane="{ln.getID()}" pos="{pos:.2f}" period="86400" file="NUL"/>')
            rows.append((did, d["phase"], "setback", ln.getID(), round(pos, 1)))
    lines.append("</additional>")
    Path(out_file).write_text("\n".join(lines) + "\n")
    return rows


if __name__ == "__main__":
    site = Path(sys.argv[1])
    from atsc.sim.run import net_file
    net = net_file(site) if len(sys.argv) < 3 else Path(sys.argv[2])
    out = site / "network" / "detectors.add.xml"
    for r in build(site, net, out):
        print("  %-5s P%d %-8s %-24s pos %6.1f" % r)
    print(f"wrote {out}")
