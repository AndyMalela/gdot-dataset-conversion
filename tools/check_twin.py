"""Check that an edited 7065 twin network is still compatible with everything built on it.

Geometry edits (moving lanes, straightening through paths, junction shape) are fine. What must NOT change:
the signal's 19 links (linkIndex -> from lane, to lane, turn), the edge IDs and lane counts the demand routes
and the RL state use, and the free-right slip lane NE_in -> E1 -> N_out.37.

  uv run python tools/check_twin.py --save           # snapshot the current net as the reference (done once)
  uv run python tools/check_twin.py                   # compare sumotwin/7065_ext.net.xml with the reference
  uv run python tools/check_twin.py --net other.net.xml --run   # also run a 1 h PM simulation (teleports etc.)
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# SUMO: prefer the version pinned in the project's uv environment (eclipse-sumo, pyproject.toml) over the
# system install, so OS upgrades can't change results; fall back to $SUMO_HOME/tools.
try:
    import sumo as _sumo_pkg
    SUMO_HOME = _sumo_pkg.SUMO_HOME
    os.environ["SUMO_HOME"] = SUMO_HOME
except ImportError:
    SUMO_HOME = os.environ.get("SUMO_HOME", "/usr/share/sumo")
    sys.path.insert(0, os.path.join(SUMO_HOME, "tools"))
import sumolib  # noqa: E402

NET = ROOT / "sumotwin" / "7065_ext.net.xml"
REF = ROOT / "sumotwin" / "twin_reference.json"
TLS = "J"


def signature(path):
    net = sumolib.net.readNet(str(path), withInternal=False)
    links = sorted((idx, a.getID(), b.getID(), net.getEdge(a.getEdge().getID()).getConnections(b.getEdge())[0].getDirection()
                    if net.getEdge(a.getEdge().getID()).getConnections(b.getEdge()) else "?")
                   for a, b, idx in net.getTLS(TLS).getConnections())
    edges = {e.getID(): e.getLaneNumber() for e in net.getEdges() if not e.getID().startswith(":")}
    slip = [[e, to.getID()] for e in ("NE_in", "NE_in.15", "E1") if e in edges for to in net.getEdge(e).getOutgoing()]
    info = {e: round(net.getEdge(e).getLength(), 1) for e in edges}
    return {"tls_links": [list(x) for x in links], "edges_lanes": edges, "slip_connections": sorted(slip),
            "edge_length_m": info}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--net", default=str(NET))
    ap.add_argument("--save", action="store_true")
    ap.add_argument("--run", action="store_true")
    a = ap.parse_args()
    sig = signature(a.net)
    if a.save:
        REF.write_text(json.dumps(sig, indent=1))
        print(f"reference saved: {REF}  ({len(sig['tls_links'])} signal links, {len(sig['edges_lanes'])} edges)")
        return
    ref = json.loads(REF.read_text())
    ok = True
    for key in ("tls_links", "edges_lanes", "slip_connections"):
        a_, b_ = ref[key], sig[key]
        if a_ != b_:
            ok = False
            print(f"CHANGED {key}:")
            if isinstance(a_, dict):
                for k in sorted(set(a_) | set(b_)):
                    if a_.get(k) != b_.get(k):
                        print(f"   {k}: {a_.get(k)} -> {b_.get(k)}")
            else:
                for x in a_:
                    if x not in b_:
                        print("   removed", x)
                for x in b_:
                    if x not in a_:
                        print("   added  ", x)
    moved = {e: (ref["edge_length_m"][e], sig["edge_length_m"][e]) for e in sig["edge_length_m"]
             if e in ref["edge_length_m"] and abs(ref["edge_length_m"][e] - sig["edge_length_m"][e]) > 0.5}
    if moved:
        print("edge lengths changed (fine for geometry edits, just know it):")
        for e, (x, y) in sorted(moved.items()):
            print(f"   {e}: {x} -> {y} m")
    import math
    net = sumolib.net.readNet(a.net)
    geo = lambda l: sum(math.dist(p, q) for p, q in zip(l.getShape(), l.getShape()[1:]))
    mism = [(e.getID(), e.getLength(), geo(e.getLanes()[0])) for e in net.getEdges()
            if abs(e.getLength() - geo(e.getLanes()[0])) > 1]
    for e, L_, g in mism:
        print(f"WARNING {e}: simulated length {L_:.1f} m but drawn {g:.1f} m (a fixed 'length' attribute) -- "
              "sumo-gui will show false gaps/overlaps and queue storage differs from the drawing")
    print("COMPATIBLE: signal links, edges, lane counts and slip lane unchanged" if ok else
          "NOT COMPATIBLE: fix the changes above (or every phase map / demand / RL state must be redone)")
    if a.run:
        e9 = ROOT / "rlagent" / "experiments" / "EXP-009_significance" / "data"
        r = subprocess.run(["sumo", "-n", a.net, "-r", str(e9 / "demand" / "2026-10-02_r0.rou.xml"),
                            "-a", str(e9 / "signals" / "webster.add.xml"), "--begin", "57600", "--end", "61200",
                            "--no-step-log", "--duration-log.statistics", "--time-to-teleport", "300"],
                           capture_output=True, text=True)
        lines = [l for l in (r.stdout + r.stderr).splitlines() if "Teleports" in l or "Collisions" in l or "Error" in l]
        print("1 h PM run (Webster):", "; ".join(lines) if lines else "no teleports/collisions reported")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
