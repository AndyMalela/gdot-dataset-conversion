"""Build the site network for SIG 7065 from the hand-built aerial twin (replaces the OSM-based 7065v2, 2026-11-02).

Input:  sumotwin/7065_ext.net.xml   (digitized from the georeferenced aerial, extended legs, 2026-10-12)
Output: atsc/sites/7065/network/7065ext.net.xml and junction.json (approach edges + headings for the
        signal-link -> phase table, same format as tools/osm_build.py)

The twin's lane use at the stop line already matches the field detectors (../GEOMETRY.md). Patched here, from the
student's measurements: where the turn lanes begin. Every leg of the twin is straight, so a patch moves or inserts
a node on the leg's line; the stop-line edges, their connections and the signal links stay as they are.

Distances are from the stop line to the node where the lane count changes (netconvert draws the change as a
short junction area around it, standing in for the taper).

  N   (Piedmont, southbound): left + right lane 40 m (twin: left 14.6 m, right lane the whole leg), 2 lanes upstream
  S   (Piedmont, northbound): left + right lane 90 m (twin: 4 lanes the whole 170 m leg), 2 lanes upstream
  SW  (Peachtree, northeastbound): 1st left lane from 62 m, 2nd from 35.5 m (mid-taper of 71 -> 53 m and
      43 -> 28 m; twin: both the whole 89 m leg), 3 lanes upstream (2 T + 1 T/R)
  NE  unchanged (not measured)

    uv run python atsc/sites/7065/network/build_ext.py
"""
import json
import math
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools"))
import osm_build as ob  # noqa: E402

SRC = ROOT / "sumotwin/7065_ext.net.xml"
HERE = Path(__file__).resolve().parent
OUT = HERE / "7065ext.net.xml"
TLS = "J"
APPROACHES = {"NB": "S_in", "EB": "SW_in", "SB": "N_near", "WB": "NE_in.79"}     # direction of travel -> stop-line edge

N_BAY_M = 40.0
S_BAY_M = 90.0
SW_BAY1_M, SW_BAY2_M = 62.0, 35.5


def run(*cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"{cmd[0]} failed:\n{r.stderr}")
    return r.stderr


def point_on(a, b, d):
    """point d m from node a towards node b."""
    ax, ay, bx, by = float(a.get("x")), float(a.get("y")), float(b.get("x")), float(b.get("y"))
    k = d / math.dist((ax, ay), (bx, by))
    return f"{ax + (bx - ax) * k:.2f}", f"{ay + (by - ay) * k:.2f}"


def measured(net):
    """straight-line distance from the stop line to the centre of each bay node, where the lane count changes.
    netconvert draws the change as a short junction area (~8 m on SW) around the node, standing in for the taper."""
    def d(edge, node):
        return math.dist(net.getEdge(edge).getShape()[-1], net.getNode(node).getCoord())
    return {"N": d("N_near", "nNleft"), "S": d("S_in", "nS"), "SW2": d("SW_in", "nSW_b2"), "SW1": d("SW_in", "nSW_b1")}


def main():
    import sumolib
    target = {"N": N_BAY_M, "S": S_BAY_M, "SW1": SW_BAY1_M, "SW2": SW_BAY2_M}
    d = dict(target)                     # node offsets from J's centre; corrected below for netconvert's trimming
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "p"
        run("netconvert", "-s", str(SRC), "--plain-output-prefix", str(p))
        nod0, edg, con = ET.parse(f"{p}.nod.xml"), ET.parse(f"{p}.edg.xml"), ET.parse(f"{p}.con.xml")
        nodes0 = {n.get("id"): n for n in nod0.getroot().iter("node")}
        edges = {e.get("id"): e for e in edg.getroot().iter("edge")}
        J, nN, nS, nSW = (nodes0[k] for k in ("J", "nN", "nS", "nSW"))

        # N: 2 lanes upstream of the bay node, 4 at the stop line
        for e in ("N_far", "N_far_ext"):
            edges[e].set("numLanes", "2")
        nodes0["nNleft"].attrib.pop("shape", None)
        # S: 2 lanes upstream of the bay node
        edges["S_in_ext"].set("numLanes", "2")
        # SW: SW_in (5 lanes) now starts at the 2nd left lane; new 4-lane SW_mid and 3-lane SW_up upstream.
        # The outbound side is split at the same nodes so both directions stay one road.
        er = edg.getroot()
        sw_in = edges["SW_in"]
        for n in ("nSW_b1", "nSW_b2"):
            ET.SubElement(nod0.getroot(), "node", id=n, x="0", y="0", type="priority")
        sw_in.set("from", "nSW_b2")
        common = {k: v for k, v in sw_in.attrib.items() if k not in ("id", "from", "to", "numLanes")}
        ET.SubElement(er, "edge", id="SW_mid", **{"from": "nSW_b1", "to": "nSW_b2", "numLanes": "4"}, **common)
        ET.SubElement(er, "edge", id="SW_up", **{"from": "nSW", "to": "nSW_b1", "numLanes": "3"}, **common)
        edges["SW_out"].set("to", "nSW_b2")
        ET.SubElement(er, "edge", id="SW_out_mid", **{"from": "nSW_b2", "to": "nSW_b1", "numLanes": "3"}, **common)
        ET.SubElement(er, "edge", id="SW_out_up", **{"from": "nSW_b1", "to": "nSW", "numLanes": "3"}, **common)

        root = con.getroot()
        for c in [c for c in root.findall("connection")
                  if c.get("from") in ("N_far", "N_far_ext", "S_in_ext", "SW_out", "S_out", "N_out.37")]:
            root.remove(c)
        for fr, to, pairs in [
                ("S_out", "S_out_ext", [(0, 0), (1, 1)]),                  # the twin left its outbound Piedmont
                ("N_out.37", "N_out_ext", [(0, 0), (1, 1)]),               # extensions unconnected
                ("N_far_ext", "N_far", [(0, 0), (1, 1)]),
                ("N_far", "N_near", [(0, 0), (0, 1), (1, 2), (1, 3)]),      # right lane, 2 through, left
                ("S_in_ext", "S_in", [(0, 0), (0, 1), (1, 2), (1, 3)]),
                ("SW_up", "SW_mid", [(0, 0), (1, 1), (2, 2), (2, 3)]),      # 1st left lane
                ("SW_mid", "SW_in", [(0, 0), (1, 1), (2, 2), (3, 3), (3, 4)]),   # 2nd left lane
                ("SW_out", "SW_out_mid", [(0, 0), (1, 1), (2, 2)]),
                ("SW_out_mid", "SW_out_up", [(0, 0), (1, 1), (2, 2)])]:
            for fl, tl in pairs:
                ET.SubElement(root, "connection", {"from": fr, "to": to, "fromLane": str(fl), "toLane": str(tl)})

        for _ in range(6):
            for nid, ref, key in [("nNleft", nN, "N"), ("nS", nS, "S"), ("nSW_b1", nSW, "SW1"), ("nSW_b2", nSW, "SW2")]:
                n = next(x for x in nod0.getroot().iter("node") if x.get("id") == nid)
                x, y = point_on(J, ref, d[key])
                n.set("x", x)
                n.set("y", y)
            for tree, suffix in [(nod0, "nod"), (edg, "edg"), (con, "con")]:
                tree.write(f"{p}.{suffix}.xml")
            log = run("netconvert", "--node-files", f"{p}.nod.xml", "--edge-files", f"{p}.edg.xml",
                      "--connection-files", f"{p}.con.xml", "--tllogic-files", f"{p}.tll.xml", "-o", str(OUT))
            got = measured(sumolib.net.readNet(str(OUT)))
            if all(abs(got[k] - target[k]) < 0.5 for k in target):
                break
            for k in target:
                d[k] += target[k] - got[k]
        else:
            sys.exit(f"turn lanes begin at {got}, target {target}")
    (HERE / "netconvert_ext.log").write_text(log)
    write_junction(sumolib.net.readNet(str(OUT), withPrograms=True))
    print(f"wrote {OUT.relative_to(ROOT)}  ({log.count('Warning')} netconvert warnings, see netconvert_ext.log); "
          "turn lanes begin at " + ", ".join(f"{k} {v:.1f} m" for k, v in got.items()))


def write_junction(net):
    apps = []
    for lab, eid in APPROACHES.items():
        e = net.getEdge(eid)
        h = ob.approach_heading(e)
        apps.append({"edge": eid, "label": lab, "name": e.getName(), "heading_deg": round(h), "lanes": e.getLaneNumber(),
                     "lane_moves": ["".join(sorted({ob.turn_type(h, ob.exit_heading(c.getToLane().getEdge()))
                                                    for c in l.getOutgoing()}, key="LTRU".index)) for l in e.getLanes()]})
    tl_in = {c[0].getEdge().getID() for c in net.getTLSSecure(TLS).getConnections()}
    assert tl_in == set(APPROACHES.values()), tl_in
    j = {"signal_id": "7065", "net_file": OUT.name, "node": "J", "tls": [TLS], "approaches": apps,
         "source": f"build_ext.py from {SRC.relative_to(ROOT)}"}
    (HERE / "junction.json").write_text(json.dumps(j, indent=1))


if __name__ == "__main__":
    main()
