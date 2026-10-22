#!/usr/bin/env python3
"""
Build a SUMO network for a GDOT ATSPM signal from OpenStreetMap, and check it.

For each signal ID:
  1. Look up its coordinates (tools/atspm_signals/signals_all.csv) and download the
     roads within --radius metres from the Overpass API.
  2. netconvert: join junction clusters, guess traffic lights from OSM signal tags,
     keep passenger-car roads, drop service roads, crop to the area.
  3. Find the signalised junction nearest to the signal, label each approach EB/WB/NB/SB
     by its direction of travel, and map ATSPM count columns (EB_L, NB_TR, ...) to SUMO
     edge pairs. The column list comes from intersections/<id>/counts/info.txt if it exists.
  4. Smoke test: one vehicle flow per turning movement through the junction for 10 min
     under netconvert's guessed signal program; count insertions, teleports, collisions.
  5. Flag what OSM can't be trusted for: approaches with no lanes tag (netconvert used
     a default), lane counts that conflict with turn:lanes, ATSPM approaches that have
     no matching OSM approach, another signal close by, etc.

  python3 tools/osm_build.py 7065
  python3 tools/osm_build.py 7065 44 337 --radius 250
  python3 tools/osm_build.py 7065 --rebuild      # reuse the downloaded osm.xml

Output in intersections/<signal>/network/:
  report.md            approaches, lanes, flags, movement map, smoke-test result
  <signal>.net.xml     SUMO network
  <signal>.sumocfg     config for the smoke test (opens the net in sumo-gui)
  movement_map.csv     ATSPM column -> SUMO (from_edge, to_edge)
  junction.json        machine-readable summary of the target junction
  preview.png          network drawing, target junction approaches labelled
  osm.xml              raw OSM download

The guessed signal program is netconvert's, NOT the real timing. The real plans come
from tools/atspm_plans.py.
"""
import argparse
import csv
import itertools
import json
import math
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import SIGNALS_CSV, sig_dir  # noqa: E402
OVERPASS = ["https://overpass-api.de/api/interpreter",
            "https://overpass.kumi.systems/api/interpreter",
            "https://overpass.private.coffee/api/interpreter",
            "https://maps.mail.ru/osm/tools/overpass/api/interpreter"]
UA = {"User-Agent": "gdot-atsc-research/0.1 (academic; osm_build.py)"}
DIRS = {"NB": 0, "EB": 90, "SB": 180, "WB": 270}       # direction of travel, compass deg


# =========================================================================== inputs
def signal_location(sid):
    sid = re.sub(r"osm$", "", str(sid))       # "7065osm" = signal 7065 built from OSM (separate folder)
    with open(SIGNALS_CSV) as f:
        for r in csv.DictReader(f):
            if r["signal_id"] == str(sid):
                return float(r["lat"]), float(r["lon"])
    raise SystemExit(f"signal {sid} not in {SIGNALS_CSV}")


def atspm_columns(sid):
    info = sig_dir(sid, "counts") / "info.txt"
    if not info.exists():
        return None
    m = re.search(r"Movements:\s+(.*)", info.read_text())
    return m.group(1).split() if m else None


def download_osm(lat, lon, radius, path):
    q = (f'[out:xml][timeout:90];(way["highway"](around:{radius + 150},{lat},{lon}););'
         f'(._;>;);out body;')
    for attempt in range(6):                          # public servers are often busy
        url = OVERPASS[attempt % len(OVERPASS)]
        try:
            req = urllib.request.Request(url, data=urllib.parse.urlencode({"data": q}).encode(),
                                         headers=UA)
            data = urllib.request.urlopen(req, timeout=180).read()
            if b"<osm" not in data[:500]:
                raise RuntimeError(data[:200])
            path.write_bytes(data)
            return
        except Exception as e:
            if attempt == 5:
                raise
            wait = 30 * (attempt + 1)
            print(f"   overpass error ({e}) from {url.split('/')[2]}; retrying in {wait}s", flush=True)
            time.sleep(wait)


def osm_way_tags(osm_path):
    tags = {}
    for w in ET.parse(osm_path).getroot().iter("way"):
        tags[w.get("id")] = {t.get("k"): t.get("v") for t in w.findall("tag")}
    return tags


# =========================================================================== build
def bbox(lat, lon, radius):
    dlat = radius / 111_320
    dlon = radius / (111_320 * math.cos(math.radians(lat)))
    return lon - dlon, lat - dlat, lon + dlon, lat + dlat


def netconvert(osm, net, lat, lon, radius, tls_set=None):
    w, s, e, n = bbox(lat, lon, radius)
    cmd = ["netconvert", "--osm-files", str(osm), "-o", str(net),
           "--geometry.remove", "--roundabouts.guess", "--ramps.guess",
           "--junctions.join", "--tls.guess-signals", "--tls.discard-simple", "--tls.join",
           "--keep-edges.by-vclass", "passenger",
           "--remove-edges.by-type", "highway.service,highway.track,highway.services,highway.unsurfaced",
           "--remove-edges.isolated", "--output.street-names", "--osm.turn-lanes",
           "--junctions.corner-detail", "5",
           "--keep-edges.in-geo-boundary", f"{w},{s},{e},{n}",
           "--no-turnarounds.tls"]
    if tls_set:
        cmd += ["--tls.set", tls_set]
    p = subprocess.run(cmd, capture_output=True, text=True)
    warnings = [l for l in (p.stderr + p.stdout).splitlines() if l.startswith("Warning")]
    if p.returncode != 0:
        raise RuntimeError("netconvert failed:\n" + p.stderr[-2000:])
    # per-signal manual fixes (e.g. a turn netconvert guessed wrong), re-applied every build
    manual = Path(net).parent / "manual.con.xml"
    if manual.exists():
        p = subprocess.run(["netconvert", "-s", str(net), "--connection-files", str(manual),
                            "-o", str(net)], capture_output=True, text=True)
        if p.returncode != 0:
            raise RuntimeError("applying manual.con.xml failed:\n" + p.stderr[-2000:])
        warnings += [l for l in (p.stderr + p.stdout).splitlines() if l.startswith("Warning")]
    return warnings


# =========================================================================== analyse
def heading(p_from, p_to):
    """Compass heading (0 = north, clockwise) of travel from p_from to p_to."""
    return math.degrees(math.atan2(p_to[0] - p_from[0], p_to[1] - p_from[1])) % 360


def angdiff(a, b):
    return abs((a - b + 180) % 360 - 180)


def approach_heading(edge):
    shape = edge.getShape()
    # direction over the last ~30 m before the stop line, to ignore far-away curves
    end = shape[-1]
    start = shape[0]
    acc = 0.0
    for p, q in zip(reversed(shape[:-1]), reversed(shape[1:])):
        acc += math.dist(p, q)
        start = p
        if acc >= 30:
            break
    return heading(start, end)


def exit_heading(edge):
    shape = edge.getShape()
    acc, end = 0.0, shape[-1]
    for p, q in zip(shape[:-1], shape[1:]):
        acc += math.dist(p, q)
        end = q
        if acc >= 30:
            break
    return heading(shape[0], end)


def turn_type(h_in, h_out):
    """L / T / R / U from the heading change (SUMO calls a U-turn on a divided road 'l')."""
    d = (h_out - h_in + 360) % 360
    if d <= 40 or d >= 320:
        return "T"
    if 40 < d < 140:
        return "R"
    if 220 < d < 320:
        return "L"
    return "U"


def upstream_length(edge, limit=500):
    """Length of road before the stop line: this edge plus the straight-ahead chain of
    predecessors, stopping at a signal or the edge of the network."""
    total, e, seen = edge.getLength(), edge, {edge.getID()}
    while total < limit:
        n = e.getFromNode()
        if n.getType().startswith("traffic_light"):
            break
        preds = [p for p in n.getIncoming() if p.getID() not in seen and p.allows("passenger")]
        if not preds:
            break
        h = approach_heading(e) if len(e.getShape()) > 1 else 0
        p = min(preds, key=lambda p: angdiff(approach_heading(p), h))
        if angdiff(approach_heading(p), h) > 45:
            break
        seen.add(p.getID())
        total += p.getLength()
        e = p
    return round(min(total, limit))


def label_approaches(incoming):
    """Assign EB/WB/NB/SB to incoming edges by travel heading (one label each)."""
    hs = {e.getID(): approach_heading(e) for e in incoming}
    ids = list(hs)
    best, best_cost = None, 1e9
    for labels in itertools.permutations(DIRS, len(ids)) if len(ids) <= 4 else []:
        cost = sum(angdiff(hs[i], DIRS[l]) ** 2 for i, l in zip(ids, labels))
        if cost < best_cost:
            best, best_cost = dict(zip(ids, labels)), cost
    if best is None:                                  # >4 approaches: nearest label, may repeat
        best = {i: min(DIRS, key=lambda l: angdiff(hs[i], DIRS[l])) for i in ids}
    return best, hs


def way_id(edge_id):
    return edge_id.lstrip("-").split("#")[0]


def analyse(sid, net_path, osm_path, lat, lon):
    net = sumolib.net.readNet(str(net_path), withPrograms=True)
    tags = osm_way_tags(osm_path)
    x, y = net.convertLonLat2XY(lon, lat)
    tls_nodes = [n for n in net.getNodes() if n.getType().startswith("traffic_light")]
    flags = []
    if not tls_nodes:
        return None, ["no signalised junction in the OSM area (no traffic_signals tag nearby)"]
    dist = lambda n: math.dist(n.getCoord(), (x, y))
    tls_nodes.sort(key=dist)
    node = tls_nodes[0]
    d0 = dist(node)
    if d0 > 40:
        flags.append(f"nearest signalised junction is {d0:.0f} m from the ATSPM location; "
                     "check it is the right one")
    others = [n for n in tls_nodes[1:] if math.dist(n.getCoord(), node.getCoord()) < 80]
    if others:
        flags.append(f"{len(others)} other signalised junction(s) within 80 m "
                     f"({', '.join(n.getID() for n in others)}): may be one intersection split "
                     "in OSM (e.g. divided road)")

    incoming = [e for e in node.getIncoming() if e.allows("passenger")]
    labels, hs = label_approaches(incoming)
    approaches = []
    for e in incoming:
        t = tags.get(way_id(e.getID()), {})
        lanes_tag = t.get("lanes")
        turn = t.get("turn:lanes") or t.get("turn:lanes:forward") or t.get("turn:lanes:backward")
        oneway = t.get("oneway") in ("yes", "1", "-1")
        moves = {}
        h_in = hs[e.getID()]
        mv_of = lambda c: turn_type(h_in, exit_heading(c.getToLane().getEdge()))
        for lane in e.getLanes():
            for c in lane.getOutgoing():
                moves.setdefault(mv_of(c), set()).add(c.getToLane().getEdge().getID())
        lane_moves = []
        for lane in e.getLanes():
            ds = sorted({mv_of(c) for c in lane.getOutgoing()}, key="LTRU".index)
            lane_moves.append("".join(ds) or "-")
        ap = {"edge": e.getID(), "osm_way": way_id(e.getID()), "name": e.getName(),
              "label": labels[e.getID()], "heading_deg": round(hs[e.getID()]),
              "lanes": e.getLaneNumber(), "lanes_tag": lanes_tag, "turn_lanes_tag": turn,
              "lane_moves": lane_moves,   # rightmost lane first (SUMO lane 0)
              "movements": {k: sorted(v) for k, v in moves.items()},
              "length_m": round(e.getLength()), "upstream_m": upstream_length(e)}
        dev = angdiff(hs[e.getID()], DIRS[ap["label"]])
        if dev > 40:
            flags.append(f"{ap['label']} approach ({e.getName() or e.getID()}) heads "
                         f"{ap['heading_deg']}°, {dev:.0f}° off the compass label; check the label")
        if not lanes_tag:
            flags.append(f"{ap['label']} approach ({e.getName() or e.getID()}): OSM way "
                         f"{ap['osm_way']} has no lanes tag; {e.getLaneNumber()} lane(s) is a "
                         "netconvert default")
        elif not oneway and lanes_tag and not any(k in t for k in ("lanes:forward", "lanes:backward")):
            flags.append(f"{ap['label']} approach ({e.getName() or e.getID()}): two-way way with "
                         f"lanes={lanes_tag} total and no lanes:forward/backward; per-direction "
                         "split guessed by netconvert")
        if ap["upstream_m"] < 100:
            flags.append(f"{ap['label']} approach has only {ap['upstream_m']} m of road before "
                         "the network edge or the next signal (little queue space)")
        approaches.append(ap)
    approaches.sort(key=lambda a: list(DIRS).index(a["label"]))
    return {"node": node.getID(), "node_type": node.getType(), "dist_m": round(d0, 1),
            "tls": [t.getID() for t in net.getTrafficLights()
                    if any(c[0].getEdge().getToNode().getID() == node.getID()
                           for c in t.getConnections())],
            "approaches": approaches}, flags


def service_legs(osm_path, out_path, lat, lon, max_m=20):
    """Copy of the OSM file where service roads touching the junction are retagged as
    roads, so netconvert keeps them. -> list of retagged way ids."""
    tree = ET.parse(osm_path)
    root = tree.getroot()
    nodes = {n.get("id"): (float(n.get("lat")), float(n.get("lon"))) for n in root.iter("node")}
    def dist(n):
        la, lo = nodes[n]
        return math.hypot((la - lat) * 111_320, (lo - lon) * 111_320 * math.cos(math.radians(lat)))
    changed = []
    for w in root.iter("way"):
        tags = {t.get("k"): t for t in w.findall("tag")}
        if tags.get("highway") is None or tags["highway"].get("v") != "service":
            continue
        refs = [nd.get("ref") for nd in w.findall("nd") if nd.get("ref") in nodes]
        if refs and min(dist(n) for n in refs) <= max_m:
            tags["highway"].set("v", "unclassified")
            changed.append(w.get("id"))
    if changed:
        tree.write(out_path)
    return changed


def nearest_junction(net_path, lat, lon, max_m=60):
    net = sumolib.net.readNet(str(net_path))
    x, y = net.convertLonLat2XY(lon, lat)
    cands = [n for n in net.getNodes() if len(n.getIncoming()) >= 3 and n.getType() != "dead_end"]
    cands.sort(key=lambda n: math.dist(n.getCoord(), (x, y)))
    if cands and math.dist(cands[0].getCoord(), (x, y)) <= max_m:
        return cands[0]
    return None


def movement_map(junction, columns):
    """ATSPM column -> list of (from_edge, to_edge). Returns rows + flags."""
    by_label = {a["label"]: a for a in junction["approaches"]}
    rows, flags = [], []
    atspm_dirs = {m.group(1) for c in columns or [] for m in [re.match(r"^(NB|SB|EB|WB)_", c)] if m}
    extra = sorted(set(by_label) - atspm_dirs) if columns else []
    if extra:
        flags.append(f"OSM approach(es) {' '.join(extra)} have no ATSPM vehicle counts "
                     "(no detector, or the compass labels differ from GDOT's)")
    for col in columns or []:
        m = re.match(r"^(?:([A-Z]+)_)?(NB|SB|EB|WB)_([A-Z]+)$", col)
        if not m or m.group(1):
            continue                                  # EXIT_ / LRT_ / totals: not a movement
        lab, mv = m.group(2), m.group(3)
        ap = by_label.get(lab)
        if not ap:
            flags.append(f"ATSPM counts {col} but OSM has no {lab} approach")
            rows.append({"atspm_column": col, "approach": lab, "from_edge": "", "to_edge": "",
                         "sumo_dir": "", "note": "no matching approach"})
            continue
        found = False
        for part in mv:                               # TL -> T and L, TR -> T and R
            for to in ap["movements"].get(part, []):
                rows.append({"atspm_column": col, "approach": lab, "from_edge": ap["edge"],
                             "to_edge": to, "sumo_dir": part,
                             "note": "shared-lane detector" if len(mv) > 1 else ""})
                found = True
            if not ap["movements"].get(part):
                flags.append(f"ATSPM counts {col} but the OSM {lab} approach has no '{part}' movement")
        if not found:
            rows.append({"atspm_column": col, "approach": lab, "from_edge": ap["edge"], "to_edge": "",
                         "sumo_dir": "", "note": "movement missing in OSM net"})
    return rows, flags


# =========================================================================== smoke test
def smoke_test(sdir, sid, junction):
    """One flow per turning movement through the junction for 10 min."""
    rou = sdir / "smoke.rou.xml"
    lines = ['<routes>', '  <vType id="car" vClass="passenger"/>']
    k = 0
    for ap in junction["approaches"]:
        for mv, tos in ap["movements"].items():
            if mv == "U":
                continue
            for to in tos:
                lines.append(f'  <flow id="f{k}_{ap["label"]}_{mv}" type="car" begin="0" end="600" '
                             f'vehsPerHour="120" from="{ap["edge"]}" to="{to}" '
                             f'departLane="best" departSpeed="max"/>')
                k += 1
    lines.append("</routes>")
    rou.write_text("\n".join(lines) + "\n")
    cfg = sdir / f"{sid}.sumocfg"
    cfg.write_text(f"""<configuration>
  <input>
    <net-file value="{sid}.net.xml"/>
    <route-files value="smoke.rou.xml"/>
  </input>
  <time><begin value="0"/><end value="1200"/></time>
  <processing><time-to-teleport value="120"/></processing>
  <report><no-step-log value="true"/></report>
</configuration>
""")
    p = subprocess.run(["sumo", "-c", str(cfg), "--duration-log.statistics",
                        "--statistic-output", str(sdir / "smoke_stats.xml")],
                       capture_output=True, text=True, cwd=sdir)
    out = p.stdout + p.stderr
    stats = {"flows": k, "returncode": p.returncode}
    try:
        r = ET.parse(sdir / "smoke_stats.xml").getroot()
        v = r.find("vehicles")
        t = r.find("teleports")
        s = r.find("safety")
        stats.update(loaded=int(v.get("loaded")), inserted=int(v.get("inserted")),
                     running=int(v.get("running")), waiting=int(v.get("waiting")),
                     teleports=int(t.get("total")), jams=int(t.get("jam")),
                     collisions=int(s.get("collisions")))
    except Exception as e:
        stats["error"] = str(e)
    stats["warnings"] = len([l for l in out.splitlines() if l.startswith("Warning")])
    stats["errors"] = [l for l in out.splitlines() if l.startswith("Error")][:5]
    return stats


# =========================================================================== preview
def preview(net_path, junction, png, radius):
    from PIL import Image, ImageDraw
    net = sumolib.net.readNet(str(net_path))
    node = net.getNode(junction["node"])
    cx, cy = node.getCoord()
    size, scale = 900, 900 / (2.2 * radius)
    img = Image.new("RGB", (size, size), (250, 250, 248))
    d = ImageDraw.Draw(img)
    P = lambda p: (size / 2 + (p[0] - cx) * scale, size / 2 - (p[1] - cy) * scale)
    ap_edges = {a["edge"]: a for a in junction["approaches"]}
    for e in net.getEdges():
        for lane in e.getLanes():
            pts = [P(p) for p in lane.getShape()]
            col = (40, 110, 200) if e.getID() in ap_edges else (150, 150, 150)
            d.line(pts, fill=col, width=max(2, int(lane.getWidth() * scale * 0.8)))
    for n in net.getNodes():
        if n.getType().startswith("traffic_light"):
            px, py = P(n.getCoord())
            r = 5 if n.getID() != junction["node"] else 9
            d.ellipse([px - r, py - r, px + r, py + r], fill=(220, 50, 40))
    for a in junction["approaches"]:
        back = math.radians(a["heading_deg"] + 180)        # upstream side of the junction
        px = size / 2 + 150 * math.sin(back) - 60
        py = size / 2 - 150 * math.cos(back) - 12
        d.line([size / 2, size / 2, px + 60, py + 12], fill=(40, 110, 200), width=1)
        d.rectangle([px - 4, py - 4, px + 124, py + 26], fill=(255, 255, 255), outline=(40, 110, 200))
        d.text((px, py - 2), f"{a['label']}  {a['lanes']} ln", fill=(0, 0, 0))
        d.text((px, py + 12), f"{a['name'][:20]}", fill=(80, 80, 80))
    d.text((10, 10), f"red = signals (big = target), blue = target approaches, "
                     f"{radius} m radius", fill=(0, 0, 0))
    img.save(png)


# =========================================================================== report
def write_report(sdir, sid, name, lat, lon, junction, flags, mrows, stats, nc_warnings, columns):
    L = [f"# SUMO network — signal {sid} ({name})", "",
         f"Built from OpenStreetMap by `tools/osm_build.py`. ATSPM location {lat}, {lon}.", ""]
    if junction is None:
        L += ["**No signalised junction found.**", ""] + [f"- {f}" for f in flags]
        (sdir / "report.md").write_text("\n".join(L) + "\n")
        return
    L += [f"Target junction `{junction['node']}` ({junction['node_type']}), "
          f"{junction['dist_m']} m from the ATSPM location.", "",
          "![preview](preview.png)", "", "## Approaches", "",
          "| Approach | Street | Heading | Lanes | OSM lanes tag | OSM turn:lanes | Lane use (right→left) | Road upstream |",
          "|---|---|---|---|---|---|---|---|"]
    for a in junction["approaches"]:
        L.append(f"| {a['label']} | {a['name']} | {a['heading_deg']}° | {a['lanes']} | "
                 f"{a['lanes_tag'] or '**missing**'} | {a['turn_lanes_tag'] or ''} | "
                 f"{' '.join(a['lane_moves'])} | {a['upstream_m']} m |")
    L += ["", "## Flags", ""]
    L += [f"- {f}" for f in flags] or ["- none"]
    if nc_warnings:
        L.append(f"- netconvert printed {len(nc_warnings)} warning(s) (see netconvert.log)")
    L += ["", "## ATSPM movement → SUMO edges", ""]
    if columns is None:
        L.append("_No TMC data for this signal yet (run tools/atspm_tmc.py), so no columns to map._")
    else:
        L += ["| ATSPM column | From edge | To edge | Note |", "|---|---|---|---|"]
        for r in mrows:
            L.append(f"| {r['atspm_column']} | {r['from_edge']} | {r['to_edge']} | {r['note']} |")
        skipped = [c for c in columns if re.match(r"^[A-Z]+_(NB|SB|EB|WB)_", c)]
        if skipped:
            L.append(f"\nNot mapped (not vehicle turning movements): {' '.join(skipped)}")
    L += ["", "## Smoke test", "",
          "One flow per turning movement (120 veh/h each, 10 min) under netconvert's guessed "
          "signal program, run to 20 min."]
    if "error" in stats:
        L.append(f"\n**Failed:** {stats['error']} {stats.get('errors')}")
    else:
        ok = (stats["inserted"] == stats["loaded"] and stats["teleports"] == 0
              and stats["collisions"] == 0 and stats["running"] == 0)
        L += ["", f"- flows: {stats['flows']}, vehicles loaded {stats['loaded']}, inserted "
              f"{stats['inserted']}, still running at 20 min {stats['running']}",
              f"- teleports {stats['teleports']}, collisions {stats['collisions']}, "
              f"SUMO warnings {stats['warnings']}",
              f"- **{'PASS' if ok else 'CHECK'}**"]
    L += ["", "## What this network does not have", "",
          "- The real signal timing (netconvert guesses a program; real plans: "
          "`tools/atspm_plans.py`).",
          "- Lane counts or turn bays that OSM doesn't tag; see Flags. Verify against aerial "
          "imagery before trusting capacity results.",
          "- Calibrated demand (the smoke test only checks every movement can be driven)."]
    (sdir / "report.md").write_text("\n".join(L) + "\n")


# =========================================================================== main
def apply_tag_fixes(sdir, osm):
    """Optional hand corrections to OSM tags, kept separate from the raw download:
    network/osm_tag_fixes.json = [{"way": "<id>", "set": {"lanes:backward": "4", ...}, "why": "..."}].
    Writes osm_fixed.xml and returns it; returns the raw osm.xml unchanged if there is no fix file."""
    fx = sdir / "osm_tag_fixes.json"
    if not fx.exists():
        return osm
    import xml.etree.ElementTree as ET
    fixes = {str(f["way"]): f for f in json.loads(fx.read_text())}
    tree = ET.parse(osm)
    found = set()
    for w in tree.getroot().iter("way"):
        f = fixes.get(w.get("id"))
        if not f:
            continue
        found.add(w.get("id"))
        tags = {t.get("k"): t for t in w.findall("tag")}
        for k, v in f["set"].items():
            if k in tags:
                tags[k].set("v", str(v))
            else:
                ET.SubElement(w, "tag", {"k": k, "v": str(v)})
    missing = set(fixes) - found
    if missing:
        raise SystemExit(f"osm_tag_fixes.json: way(s) {sorted(missing)} not in {osm.name}")
    out = sdir / "osm_fixed.xml"
    tree.write(out, encoding="utf-8", xml_declaration=True)
    return out


def build_one(sid, radius, rebuild):
    sdir = sig_dir(sid, "network")
    sdir.mkdir(parents=True, exist_ok=True)
    lat, lon = signal_location(sid)
    name = "?"
    info = sig_dir(sid, "counts") / "info.txt"
    if info.exists():
        m = re.search(r"Intersection:\s+(.*)", info.read_text())
        name = m.group(1).strip() if m else name
    osm = sdir / "osm.xml"
    if not (rebuild and osm.exists()):
        download_osm(lat, lon, radius, osm)
        time.sleep(2)
    net = sdir / f"{sid}.net.xml"
    osm = apply_tag_fixes(sdir, osm)          # every later step uses the corrected tags
    nc_warn = netconvert(osm, net, lat, lon, radius)
    (sdir / "netconvert.log").write_text("\n".join(nc_warn) + "\n")
    junction, flags = analyse(sid, net, osm, lat, lon)
    added_tls = None
    if junction is None or junction["dist_m"] > 60:
        # OSM has no traffic_signals tag here: signalise the nearest real junction instead.
        # If the side leg is a driveway (highway=service) it was dropped, so the junction
        # looks like a plain road; re-include driveways touching the signal location first.
        src, extra = osm, []
        n = nearest_junction(net, lat, lon)
        if n is None:
            patched = sdir / "osm_with_service_legs.xml"
            ways = service_legs(osm, patched, lat, lon, max_m=40)
            if ways:
                netconvert(patched, net, lat, lon, radius)
                n = nearest_junction(net, lat, lon)
                if n is not None:
                    src, extra = patched, [f"side leg(s) are driveways in OSM (service road(s) "
                                           f"{', '.join(ways)}); included as legs"]
        if n is not None:
            nc_warn = netconvert(src, net, lat, lon, radius, tls_set=n.getID())
            (sdir / "netconvert.log").write_text("\n".join(nc_warn) + "\n")
            junction, flags = analyse(sid, net, osm, lat, lon)
            if junction is not None:
                added_tls = (f"OSM has no traffic_signals tag at this intersection; junction "
                             f"{n.getID()} was made signalised by the script")
                flags = [added_tls] + extra + flags
                osm_used = src
        if junction is None or junction["dist_m"] > 60:
            far = f" (nearest signal is {junction['dist_m']} m away)" if junction else ""
            junction, flags = None, [f"could not identify the intersection in OSM{far}: no "
                                     "signal tag and no junction with 3+ approaches within 60 m"]
    columns = atspm_columns(sid)
    mrows, stats = [], {}
    if junction:
        mrows, mflags = movement_map(junction, columns)
        if any("but OSM has no" in f for f in mflags) and not any("driveways in OSM" in f for f in flags):
            # GDOT counts an approach OSM lacks: often a driveway tagged highway=service,
            # which netconvert drops. Re-include service roads touching the junction only.
            patched = sdir / "osm_with_service_legs.xml"
            ways = service_legs(osm, patched, lat, lon)
            if ways:
                nc_warn = netconvert(patched, net, lat, lon, radius,
                                     tls_set=junction["node"] if added_tls else None)
                (sdir / "netconvert.log").write_text("\n".join(nc_warn) + "\n")
                j2, f2 = analyse(sid, net, osm, lat, lon)
                if j2 is not None:
                    junction, flags = j2, f2 + [f"GDOT counts an approach missing from OSM roads; "
                                                f"service road(s) {', '.join(ways)} touching the "
                                                "junction (driveways in OSM) were included as legs"]
                    if added_tls:
                        flags.insert(0, added_tls)
                    mrows, mflags = movement_map(junction, columns)
        flags += mflags
        with open(sdir / "movement_map.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["atspm_column", "approach", "from_edge", "to_edge",
                                              "sumo_dir", "note"])
            w.writeheader()
            w.writerows(mrows)
        stats = smoke_test(sdir, sid, junction)
        preview(net, junction, sdir / "preview.png", radius)
        (sdir / "junction.json").write_text(json.dumps(
            {"signal_id": sid, "name": name, "lat": lat, "lon": lon, **junction,
             "flags": flags, "smoke_test": stats}, indent=1))
    if (sdir / "manual.con.xml").exists():
        flags.append("manual connection fixes applied from manual.con.xml (see the comments in it)")
    write_report(sdir, sid, name, lat, lon, junction, flags, mrows, stats, nc_warn, columns)
    return junction, flags, stats


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("signals", nargs="+")
    ap.add_argument("--radius", type=int, default=300, help="metres around the signal (default 300)")
    ap.add_argument("--rebuild", action="store_true", help="reuse downloaded osm.xml")
    a = ap.parse_args()
    for sid in a.signals:
        print(f"== Signal {sid}", flush=True)
        try:
            j, flags, stats = build_one(sid, a.radius, a.rebuild)
        except Exception as e:
            print(f"   FAILED: {e}", flush=True)
            continue
        if not j:
            print(f"   no signalised junction found: {flags}", flush=True)
            continue
        apps = " ".join(f"{x['label']}:{x['lanes']}" for x in j["approaches"])
        st = (f"inserted {stats.get('inserted')}/{stats.get('loaded')}, teleports "
              f"{stats.get('teleports')}, collisions {stats.get('collisions')}")
        print(f"   junction {j['node']} ({j['dist_m']} m)  approaches {apps}  flags {len(flags)}  "
              f"smoke: {st}", flush=True)


if __name__ == "__main__":
    main()
