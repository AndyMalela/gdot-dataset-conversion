#!/usr/bin/env python3
"""
Use a hand-built SUMO network for an intersection instead of the OSM one.

  python3 tools/adopt_network.py 7065 sumotwin/7065.net.xml --tls J \\
      --approach EB=SW_in WB=NE_in.79 NB=S_in SB=N_near

Writes intersections/<id>/network/twin/ (junction.json, movement_map.csv, README.md) in the
same format osm_build.py produces. build_sim.py uses network/twin/ when it exists, so the
simulation runs on the hand-built network; the OSM build in network/ is kept for reference.
The network file itself is referenced, not copied (one source of truth, e.g. shared with
rlagent/).

--approach maps the compass labels used in the counts / phase map (direction of travel)
to the incoming edge at the signal.
"""
import argparse
import csv
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import ROOT, sig_dir, rel  # noqa: E402
import osm_build as ob  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("signal")
    ap.add_argument("net")
    ap.add_argument("--tls", required=True)
    ap.add_argument("--approach", nargs="+", required=True, help="LABEL=edge, e.g. EB=SW_in")
    a = ap.parse_args()
    net_path = (ROOT / a.net).resolve()
    net = ob.sumolib.net.readNet(str(net_path), withPrograms=True)
    tls = net.getTLSSecure(a.tls)
    labels = dict(x.split("=", 1) for x in a.approach)
    edge_label = {e: l for l, e in labels.items()}
    in_edges = {c[0].getEdge().getID() for c in tls.getConnections()}
    missing = sorted(in_edges - set(edge_label))
    if missing:
        raise SystemExit(f"signal {a.tls} has incoming edges with no label: {missing}")

    approaches = []
    for lab, eid in labels.items():
        e = net.getEdge(eid)
        h = ob.approach_heading(e)
        moves, lane_moves = {}, []
        for lane in e.getLanes():
            ds = set()
            for c in lane.getOutgoing():
                mv = ob.turn_type(h, ob.exit_heading(c.getToLane().getEdge()))
                moves.setdefault(mv, set()).add(c.getToLane().getEdge().getID())
                ds.add(mv)
            lane_moves.append("".join(sorted(ds, key="LTRU".index)) or "-")
        approaches.append({"edge": eid, "label": lab, "name": e.getName(), "heading_deg": round(h),
                           "lanes": e.getLaneNumber(), "lane_moves": lane_moves,
                           "movements": {k: sorted(v) for k, v in moves.items()},
                           "upstream_m": ob.upstream_length(e)})
    order = list(ob.DIRS)
    approaches.sort(key=lambda x: order.index(x["label"]))
    node = net.getEdge(labels[next(iter(labels))]).getToNode()

    out = sig_dir(a.signal, "network") / "twin"
    out.mkdir(parents=True, exist_ok=True)
    junction = {"signal_id": a.signal, "net_file": os.path.relpath(net_path, out), "node": node.getID(),
                "tls": [a.tls], "approaches": approaches, "source": f"hand-built network {rel(net_path)}"}
    (out / "junction.json").write_text(json.dumps(junction, indent=1))

    columns = ob.atspm_columns(a.signal)
    rows, flags = ob.movement_map(junction, columns)
    with open(out / "movement_map.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["atspm_column", "approach", "from_edge", "to_edge", "sumo_dir", "note"])
        w.writeheader()
        w.writerows(rows)
    L = [f"# Hand-built network for signal {a.signal}", "",
         f"`{rel(net_path)}` (referenced, not copied), signal `{a.tls}`. Used by "
         "`tools/build_sim.py` instead of the OSM network in `../`.", "",
         "| Approach | Edge | Heading | Lanes | Lane use (right→left) |", "|---|---|---|---|---|"]
    L += [f"| {x['label']} | {x['edge']} | {x['heading_deg']}° | {x['lanes']} | {' '.join(x['lane_moves'])} |"
          for x in approaches]
    L += ["", "| ATSPM column | From edge | To edge |", "|---|---|---|"]
    L += [f"| {r['atspm_column']} | {r['from_edge']} | {r['to_edge']} |" for r in rows]
    if flags:
        L += ["", "Flags:"] + [f"- {x}" for x in flags]
    (out / "README.md").write_text("\n".join(L) + "\n")
    print(f"-> {rel(out)}/  ({len(approaches)} approaches, {len(rows)} mapped columns, {len(flags)} flags)")
    for x in flags:
        print("   ", x)


if __name__ == "__main__":
    main()
