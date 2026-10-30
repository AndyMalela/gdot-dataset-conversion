"""Build the v2 network for SIG 7065 from the audited OSM network.

Input:  intersections/7065osm/network/7065osm.net.xml  (tools/osm_build.py + osm_tag_fixes.json)
Output: atsc/sites/7065/network/7065v2.net.xml

Every patch below comes from ../GEOMETRY.md (field detectors 2026-10-02 + student check 2026-10-23).
The target signal's program is left for netconvert to guess; atsc's NEMA engine sets the signal state
at run time, so the guessed program is never used.

    uv run python atsc/sites/7065/network/build_net.py
"""
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / "intersections/7065osm/network/7065osm.net.xml"
OUT = Path(__file__).resolve().parent / "7065v2.net.xml"
TLS = "cluster_69536528_69537103"

N_IN, N_UP = "-525767115#1", "-525767115#3"      # N leg: stop-line edge (19 m) and the one upstream
S_IN = "715642217#0"                              # S leg approach
S_LEG = ["715642217#0", "1014001449#9", "1014001449#5"]
SW_IN = "96433201#0"
NE_MICRO = ("1153256545#1", "1153256544#0")       # NE leg: 4-lane -> 6-lane micro-edge (1.9 m) before the bay
# outbound edges
TO_N, TO_S, TO_NE, TO_SW = "525767115#0", "715642215#0", "1049518251#0", "1474278653#0"

MPH35 = "15.65"
N_BAY_M = 40.0                                    # N leg left bay + right lane length (student check)
SW_MID = "1118649821#0"                           # SW leg edge from 7066 towards the bay (46-92.5 m from the stop line)
SW_BAY1_M = 62.0                                  # SW first left lane: taper 71 -> 53 m, modelled from mid-taper


def run(*cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"{cmd[0]} failed:\n{r.stderr}")
    return r.stderr


def main():
    import sumolib
    net = sumolib.net.readNet(str(SRC))
    n_in_len = net.getEdge(N_IN).getLength()
    n_up_len = net.getEdge(N_UP).getLength()
    split_pos = n_up_len - (N_BAY_M - n_in_len)   # position on N_UP where the 4-lane section starts
    sw_dist = sum(net.getEdge(e).getLength() for e in (SW_IN, "1474278659"))   # stop line -> SW_MID's end
    sw_pos = net.getEdge(SW_MID).getLength() - (SW_BAY1_M - sw_dist)

    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "p"
        run("netconvert", "-s", str(SRC), "--plain-output-prefix", str(p))
        edg, con, tll = ET.parse(f"{p}.edg.xml"), ET.parse(f"{p}.con.xml"), ET.parse(f"{p}.tll.xml")

        edges = {e.get("id"): e for e in edg.getroot().iter("edge")}
        # 1. N leg: 4 lanes only for the last 40 m. Upstream part keeps lanes 1, 2 (the two through lanes).
        e = edges[N_UP]
        ET.SubElement(e, "split", pos="0", lanes="1 2")
        ET.SubElement(e, "split", pos=f"{split_pos:.2f}", lanes="0 1 2 3")
        # 5. SW leg: first left lane from 62 m (student check 2026-10-30: taper 71 -> 53 m; OSM had 46 m)
        e = edges[SW_MID]
        e.set("numLanes", "4")
        ET.SubElement(e, "split", pos="0", lanes="0 1 2")
        sw_split = ET.SubElement(e, "split", pos=f"{sw_pos:.2f}", lanes="0 1 2 3")
        # 3. S leg speed: posted 35 mph
        for eid in S_LEG:
            edges[eid].set("speed", MPH35)

        root = con.getroot()
        # the split renames N_UP's pieces, so connections into/out of it are re-guessed by netconvert
        for c in [c for c in root.findall("connection") if N_UP in (c.get("from"), c.get("to"))]:
            root.remove(c)
        for c in [c for c in root.findall("connection") if c.get("from") == SW_MID]:      # now leaves the split's 2nd piece
            root.remove(c)
        # 1b. S leg lane use: lane 0 right only, lanes 1-2 through, lane 3 left, no U-turn
        for c in [c for c in root.findall("connection") if c.get("from") == S_IN]:
            root.remove(c)
        for fl, to, tl in [(0, TO_NE, 0), (1, TO_N, 0), (2, TO_N, 1), (3, TO_SW, 1)]:
            ET.SubElement(root, "connection", {"from": S_IN, "to": to, "fromLane": str(fl), "toLane": str(tl)})
        # 2. SW leg: rightmost through lane also takes the right turn (onto Piedmont southbound)
        ET.SubElement(root, "connection", {"from": SW_IN, "to": TO_S, "fromLane": "0", "toLane": "0"})
        # 4. NE leg: OSM widens 4 -> 6 lanes on a 1.9 m edge just before the bay, with lane 0 fanning out to
        # stop-bar through lanes 0 and 1; SUMO sends every vehicle to the first, so through lane 1 starved
        # (demand check 2026-10-30). Each upstream lane now feeds one through lane; lane 3 feeds the left bay.
        for c in [c for c in root.findall("connection") if (c.get("from"), c.get("to")) == NE_MICRO]:
            root.remove(c)
        for fl, tl in [(0, 0), (0, 1), (1, 2), (2, 3), (3, 4), (3, 5)]:
            ET.SubElement(root, "connection", {"from": NE_MICRO[0], "to": NE_MICRO[1],
                                               "fromLane": str(fl), "toLane": str(tl)})

        # let netconvert re-guess the target's program (link indices change with the connections)
        troot = tll.getroot()
        for t in [t for t in troot.findall("tlLogic") if t.get("id") == TLS]:
            troot.remove(t)
        for c in [c for c in troot.findall("connection") if c.get("tl") == TLS]:
            troot.remove(c)

        # netconvert trims edges at junctions, so the split lands off target: measure and correct (fix 5)
        for _ in range(5):
            for tree, suffix in [(edg, "edg"), (con, "con"), (tll, "tll")]:
                tree.write(f"{p}.{suffix}.xml")
            log = run("netconvert", "--node-files", f"{p}.nod.xml", "--edge-files", f"{p}.edg.xml",
                      "--connection-files", f"{p}.con.xml", "--tllogic-files", f"{p}.tll.xml",
                      "--type-files", f"{p}.typ.xml", "-o", str(OUT))
            got = sw_bay_start(sumolib.net.readNet(str(OUT)))
            if abs(got - SW_BAY1_M) < 0.5:
                break
            sw_pos += got - SW_BAY1_M
            sw_split.set("pos", f"{sw_pos:.2f}")
        else:
            sys.exit(f"SW bay start {got:.1f} m, target {SW_BAY1_M} m")
    (OUT.parent / "netconvert.log").write_text(log)
    print(f"wrote {OUT.relative_to(ROOT)}  ({log.count('Warning')} netconvert warnings, see netconvert.log); "
          f"SW first left lane from {got:.1f} m")


def sw_bay_start(net):
    """distance from the SW stop line to where the approach widens from 3 to 4 lanes."""
    e, d = net.getEdge(SW_IN), 0.0
    while e.getLaneNumber() >= 4:
        d += e.getLength()
        e = max(e.getFromNode().getIncoming(), key=lambda x: x.getLaneNumber())
    return d


if __name__ == "__main__":
    main()
