#!/usr/bin/env python3
"""
Build a SUMO simulation of one intersection from its real data, as a quality check:
the OSM network, one day of measured turning-movement counts, and the real time-of-day
signal timing plans.

  python3 tools/build_sim.py 7065                    # date 2026-10-02
  python3 tools/build_sim.py 7065 137 --date 2026-10-02
  python3 tools/build_sim.py 7065 --no-run           # write files only

Inputs (all in intersections/<id>/):
  network/<id>.net.xml, junction.json, movement_map.csv   (osm_build.py)
  counts/tmc_<id>_5min.csv                                 (atspm_tmc.py)
  timing/timing_plan_<id>.json, clearance.json             (atspm_plans.py)
  timing/phase_map.json   which approach/movement each phase controls (atspm_phasemap.py,
                          transcribed by hand)

Output in intersections/<id>/sim/:
  demand.rou.xml       one flow per counted movement per 5-min bin (exact counts)
  signal.add.xml       one signal program per timing plan + time-of-day switching (WAUT)
  sim.sumocfg          full day, headless:   sumo -c sim.sumocfg
  gui.sumocfg          07:45-09:00 in the GUI: sumo-gui -c gui.sumocfg
  peak.sumocfg         07:00-09:30 headless (the quality check)
  view.xml             GUI view centred on the intersection
  snapshot.png         GUI picture at 08:30 (for slides), made by --run
  README.md            what was built, every assumption, quality-check results

Rules (fidelity: nothing is invented silently; every assumption is listed in README.md):
  - Demand = the measured counts. Movements GDOT doesn't count get no traffic.
    Outage bins get no traffic. A shared-lane column (e.g. NB_TL) is split equally
    between its movements (ASSUMPTION, listed). Where an approach has no through count
    but GDOT has an exit-lane count for that direction (EXIT_*), the through flow is
    derived as exit count minus the counted movements into that leg (an upper bound,
    since uncounted right turns are included; listed).
  - Signal = NEMA dual ring (ring 1: 1-4, ring 2: 5-8, barrier after 2|6) built from
    each plan's splits, the measured yellow / red clearance, and lead/lag. Permissive
    lefts yield ('g'); right turns go with their through phase and may turn on red.
    'Actuated' bands (Free / uncoordinated) use observed median phase times as fixed
    splits (APPROXIMATION, listed). Offsets are unknown (0).
"""
import argparse
import csv
import random
import re
import datetime as dt
import json
import math
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import sig_dir, rel  # noqa: E402
import osm_build as ob  # noqa: E402  (sumolib, turn classification)

sumolib = ob.sumolib
RING = {1: (1, 2), 2: (5, 6)}, {1: (3, 4), 2: (7, 8)}      # barrier group -> ring -> phases
DEFAULT_YELLOW, DEFAULT_RED = 3.5, 2.0
GUI_BEGIN, GUI_END, SNAP_T = 7 * 3600 + 45 * 60, 9 * 3600, 8 * 3600 + 30 * 60
CHECK_BEGIN, CHECK_END = 7 * 3600, 9 * 3600 + 30 * 60      # quality check: morning peak


# =========================================================================== inputs
def load(sid):
    n, c, t = sig_dir(sid, "network"), sig_dir(sid, "counts"), sig_dir(sid, "timing")
    twin = n / "twin"
    if (twin / "junction.json").exists():          # hand-built network (tools/adopt_network.py)
        j = json.loads((twin / "junction.json").read_text())
        net_path, mm_dir = (twin / j["net_file"]).resolve(), twin
    else:                                          # OSM network (tools/osm_build.py)
        j = json.loads((n / "junction.json").read_text())
        net_path, mm_dir = n / f"{sid}.net.xml", n
    d = {"junction": j, "net_path": net_path,
         "network_source": j.get("source", "OpenStreetMap (tools/osm_build.py)"),
         "movement_map": list(csv.DictReader(open(mm_dir / "movement_map.csv"))),
         "tmc": list(csv.DictReader(open(c / f"tmc_{sid}_5min.csv"))),
         "plan": json.loads((t / f"timing_plan_{sid}.json").read_text()),
         "phase_map": json.loads((t / "phase_map.json").read_text())}
    cf = t / "clearance.json"
    d["clearance"] = json.loads(cf.read_text()) if cf.exists() else {}
    d["greens_csv"] = t / f"greens_{sid}.csv"
    # GDOT's count report labels approaches with its road-based directions (= phase descriptions),
    # not the compass; phase_map.json's count_labels says which network approach each label is.
    lab = d["phase_map"].get("count_labels") or {k: k for k in ("NB", "EB", "SB", "WB")}
    def tr(col):
        parts = col.split("_")
        for i, x in enumerate(parts):
            if x in lab:
                parts[i] = lab[x]
                return "_".join(parts)
        return col
    cols = [c for c in d["tmc"][0] if re.match(r"^(?:[A-Z]+_)?(NB|SB|EB|WB)_[A-Z]+$", c)] if d["tmc"] else []
    d["col_to_net"] = {c: tr(c) for c in cols}
    net_to_col = {v: k for k, v in d["col_to_net"].items()}
    if any(k != v for k, v in d["col_to_net"].items()):
        rows, _ = ob.movement_map(j, [d["col_to_net"][c] for c in cols])
        for r in rows:
            r["atspm_column"] = net_to_col.get(r["atspm_column"], r["atspm_column"])
        d["movement_map"] = rows
    d["count_labels"] = lab
    return d


def actuation_params(d, date):
    """Min greens measured in the Timing & Actuation windows ('min green complete' block),
    max greens for actuated periods from Split Monitor max-out dots."""
    mins, rec = defaultdict(list), defaultdict(list)
    if d["greens_csv"].exists():
        for r in csv.DictReader(open(d["greens_csv"])):
            if not r["chart"].startswith("Phase_"):
                continue
            p = int(r["chart"].split("_")[1].rstrip("b"))
            if r["min_green_s"]:
                mins[p].append(float(r["min_green_s"]))
            if r["date"] == date and r["window_min"] == "15" and r["truncated"] == "0":
                rec[(r["window_start"], p)].append(float(r["green_s"]))
    med = lambda v: sorted(v)[len(v) // 2]
    act = {"min_green": {p: med(v) for p, v in mins.items()}, "recorded_greens": dict(rec)}
    mo = d["plan"]["plans"].get("Actuated", {}).get("max_obs", {})
    c = d["clearance"] or {}
    y = {int(k): float(v) for k, v in (c.get("yellow") or {}).items() if v != ""}
    r_ = {int(k): float(v) for k, v in (c.get("red_clear") or {}).items() if v != ""}
    act["max_green"] = {int(p): max(1.0, x["s"] - y.get(int(p), DEFAULT_YELLOW) - r_.get(int(p), DEFAULT_RED))
                        for p, x in mo.items()}
    act["max_source"] = {int(p): x["source"] for p, x in mo.items()}
    return act


# =========================================================================== demand
def upstream_start(net, edge_id, limit=500):
    """First edge of the straight-ahead chain before the approach (more queue space)."""
    e = net.getEdge(edge_id)
    total, seen = e.getLength(), {edge_id}
    while total < limit:
        n = e.getFromNode()
        if n.getType().startswith("traffic_light"):
            break
        preds = [p for p in n.getIncoming() if p.getID() not in seen and p.allows("passenger")]
        if not preds:
            break
        h = ob.approach_heading(e)
        p = min(preds, key=lambda p: ob.angdiff(ob.approach_heading(p), h))
        if ob.angdiff(ob.approach_heading(p), h) > 45:
            break
        seen.add(p.getID())
        total += p.getLength()
        e = p
    return e.getID()


def build_demand(sid, d, date, net, sdir, arrivals="poisson", seed=12345):
    rows = [r for r in d["tmc"] if r["date"] == date]
    if not rows:
        raise SystemExit(f"{sid}: no counts for {date}")
    notes, mm = [], defaultdict(list)
    for m in d["movement_map"]:
        if m["to_edge"]:
            mm[m["atspm_column"]].append(m)
    cols = [c for c in rows[0] if c in mm]
    shared = {c: len(v) for c, v in mm.items() if len(v) > 1}
    for c, k in shared.items():
        notes.append(f"ASSUMPTION: shared-lane column {c} is split equally between its "
                     f"{k} movements ({', '.join(m['sumo_dir'] for m in mm[c])}); the real split is not measured.")
    unmapped = [m["atspm_column"] for m in d["movement_map"] if not m["to_edge"]]
    if unmapped:
        notes.append(f"Counted but not in the network (no traffic generated): {', '.join(sorted(set(unmapped)))}.")

    # derived throughs from exit-lane counts
    apps = {a["label"]: a for a in d["junction"]["approaches"]}
    net_of = d.get("col_to_net", {})
    col_of = {v: k for k, v in net_of.items()}
    if any(k != v for k, v in net_of.items()):
        notes.append("Count-report direction labels translated to network approaches (GDOT labels "
                     "approaches by road-based direction): " +
                     ", ".join(f"{k} -> {v}" for k, v in d["count_labels"].items() if k != v) +
                     ". Vehicle ids keep GDOT's column names.")
    derived = {}
    for lab, a in apps.items():
        has_t = any(net_of.get(c, c).startswith(lab + "_") and ("T" in net_of.get(c, c).split("_")[1]) for c in cols)
        ex = col_of.get(f"EXIT_{lab}_T", f"EXIT_{lab}_T")
        if not has_t and a["movements"].get("T") and ex in rows[0]:
            derived[lab] = (ex, a["movements"]["T"][0])
    for lab, (ex, to) in derived.items():
        notes.append(f"DERIVED: {lab} through = {ex} (exit-lane count leaving {lab}) minus the counted "
                     f"movements into that leg; an upper bound (uncounted right turns into the leg are included).")

    starts = {a["edge"]: upstream_start(net, a["edge"]) for a in apps.values()}
    flows, outage, total = [], 0, defaultdict(float)
    for r in rows:
        h, m = map(int, r["time"].split(":"))
        b = h * 3600 + m * 60
        if r["status"] != "ok":
            outage += 1
            continue
        into = defaultdict(float)
        bin_flows = []
        for c in cols:
            n = int(r[c] or 0)
            for mv in mm[c]:
                share = n / len(mm[c])
                bin_flows.append((c, mv["from_edge"], mv["to_edge"], share))
                into[mv["to_edge"]] += share
        for lab, (ex, to) in derived.items():
            v = max(0.0, float(r[ex] or 0) - into[to])
            bin_flows.append((f"{lab}_T*", apps[lab]["edge"], to, v))
        for c, fr, to, v in bin_flows:
            if v <= 0:
                continue
            total[c] += v
            flows.append((b, c, fr, to, v))
    if outage:
        notes.append(f"{outage} five-minute bin(s) on {date} are sensor outages: no traffic generated there.")

    # number per flow must be an integer: carry fractional parts forward per movement
    carry = defaultdict(float)
    # sigma 0.2 (SUMO default 0.5): calibrated 2026-10-15 so a through lane discharges ~1,920 veh/h of green,
    # close to the HCM base saturation flow (1,900); sigma 0.5 gave 1,640, too low for the counted PM flows
    # (intersections/7065/timing/capacity_check/README.md)
    L = ['<routes>', '  <vType id="car" vClass="passenger" sigma="0.2"/>']
    k, trips, rng = 0, [], random.Random(seed)
    for b, c, fr, to, v in sorted(flows):
        key = (c, fr, to)
        v += carry[key]
        n = int(v)
        carry[key] = v - n
        if n == 0:
            continue
        k += 1
        if arrivals == "even":
            L.append(f'  <flow id="{c}_{to}_{b}" type="car" begin="{b}" end="{b + 300}" number="{n}" '
                     f'from="{starts[fr]}" via="{fr}" to="{to}" departLane="best" departSpeed="max"/>')
        else:
            # Poisson arrivals with the measured count: given n arrivals in a 5-min bin, a Poisson
            # process places them independently and uniformly in it
            for i in range(n):
                trips.append((round(rng.uniform(b, b + 300), 2), f"{c}_{to}_{b}.{i}", fr, to))
    # explicit routes: SUMO otherwise routes each trip at insertion with current travel times, and
    # under congestion it can pick a detour that crosses the signal twice through a movement with no
    # green (found at 7100: Lindbergh WB trips looped through Peachtree NB's prohibited left).
    # Every route must cross the target signal exactly once.
    tl_in = set()
    for t in net.getTrafficLights():
        if any(c[0].getEdge().getID() in starts for c in t.getConnections()):
            tl_in = {c[0].getEdge().getID() for c in t.getConnections()}
    routes = {}
    for fr, to in sorted({(fr, to) for _, _, fr, to in trips}):
        p1, _ = net.getShortestPath(net.getEdge(starts[fr]), net.getEdge(fr), vClass="passenger")
        p2, _ = net.getShortestPath(net.getEdge(fr), net.getEdge(to), vClass="passenger")
        if not p1 or not p2:
            raise SystemExit(f"{sid}: no passenger route {starts[fr]} -> {fr} -> {to}")
        edges = [e.getID() for e in p1] + [e.getID() for e in p2[1:]]
        if sum(e in tl_in for e in edges) != 1:
            raise SystemExit(f"{sid}: route {fr} -> {to} crosses the signal {sum(e in tl_in for e in edges)} times")
        routes[(fr, to)] = (f"r{len(routes)}", " ".join(edges))
    for rid, edges in routes.values():
        L.append(f'  <route id="{rid}" edges="{edges}"/>')
    for t, vid, fr, to in sorted(trips):
        L.append(f'  <vehicle id="{vid}" type="car" depart="{t}" route="{routes[(fr, to)][0]}" '
                 f'departLane="best" departSpeed="max"/>')
    if arrivals != "even":
        notes.append(f"Arrivals: Poisson within each 5-min bin with the measured count (random times, "
                     f"seed {seed}); counts per movement per bin are exact.")
    L.append("</routes>")
    (sdir / "demand.rou.xml").write_text("\n".join(L) + "\n")
    return notes, {c: round(v) for c, v in total.items()}, k


# =========================================================================== signal
def link_table(sid, d, net):
    """linkIndex -> (approach label, movement L/T/R/U) for the target signal."""
    j = d["junction"]
    by_edge = {a["edge"]: a for a in j["approaches"]}
    tls = None
    for t in net.getTrafficLights():
        if any(c[0].getEdge().getID() in by_edge for c in t.getConnections()):
            tls = t
            break
    links = {}
    for in_lane, out_lane, idx in tls.getConnections():
        a = by_edge.get(in_lane.getEdge().getID())
        if a is None:
            links[idx] = (None, None)
            continue
        mv = ob.turn_type(a["heading_deg"], ob.exit_heading(out_lane.getEdge()))
        links[idx] = (a["label"], mv)
    return tls.getID(), links


def link_phases(links, phase_map):
    """linkIndex -> (protected phases, permissive phases, right-on-red)"""
    out = {}
    for idx, (lab, mv) in links.items():
        prot, perm = set(), set()
        for p in phase_map["phases"]:
            if p["approach"] != lab:
                continue
            m = p["move"]
            hit = (m == "all" or (m == "L" and mv in ("L", "U")) or (m == "T" and mv in ("T", "R")))
            if hit:
                (prot if p["type"] == "protected" else perm).add(p["phase"])
        # a U-turn with no left phase follows the through phase, yielding
        if mv == "U" and not prot and not perm:
            perm = {p["phase"] for p in phase_map["phases"] if p["approach"] == lab and p["move"] == "T"}
        out[idx] = (prot, perm, mv == "R")
    return out


def ring_timeline(splits, yellow, red, lead):
    """Per ring: list of (t0, t1, phase, 'G'|'y'|'r') over one cycle; and cycle length."""
    tl = {1: [], 2: []}
    t = 0.0
    for grp in RING:
        seqs = {}
        for ring, (a, b) in grp.items():
            order = (a, b) if lead.get(f"{a}/{b}", a) == a else (b, a)
            seqs[ring] = [p for p in order if splits.get(p, 0) > 0]
        glen = max(sum(splits[p] for p in s) for s in seqs.values()) if any(seqs.values()) else 0
        for ring, seq in seqs.items():
            tt = t
            for i, p in enumerate(seq):
                s = splits[p]
                if i == len(seq) - 1:                       # last phase absorbs slack to the barrier
                    s += glen - sum(splits[q] for q in seq)
                y, r = yellow.get(p, DEFAULT_YELLOW), red.get(p, DEFAULT_RED)
                g = max(1.0, s - y - r)
                tl[ring] += [(tt, tt + g, p, "G"), (tt + g, tt + g + y, p, "y"), (tt + g + y, tt + s, p, "r")]
                tt += s
        t += glen
    return tl, t


def program_states(tl, cycle, lp, n_links):
    cuts = sorted({0.0, cycle} | {x for r in tl.values() for seg in r for x in seg[:2]})
    phases = []
    for t0, t1 in zip(cuts[:-1], cuts[1:]):
        if t1 - t0 < 0.05:
            continue
        mid = (t0 + t1) / 2
        active = {}                                          # phase -> 'G'|'y'|'r'
        for segs in tl.values():
            for a, b, p, st in segs:
                if a <= mid < b:
                    active[p] = st
        state = []
        for i in range(n_links):
            prot, perm, rtor = lp.get(i, (set(), set(), False))
            if any(active.get(p) == "G" for p in prot):
                c = "G"
            elif any(active.get(p) == "G" for p in perm):
                c = "g"
            elif any(active.get(p) == "y" for p in prot | perm):
                c = "y"
            elif rtor and (prot or perm):
                c = "s"
            else:
                c = "r"
            state.append(c)
        s = "".join(state)
        if phases and phases[-1][1] == s:
            phases[-1][0] += t1 - t0
        else:
            phases.append([t1 - t0, s])
    return phases


def nema_program(tlid, name, splits, coordinated, cycle, lp, n_links, yellow, red, lead,
                 mins, maxg, ext, used_default, term=None, rec_med=None):
    """SUMO NEMA (actuated, dual ring) program for one plan.

    Coordinated plans: splits are force-offs (maxDur = split - yellow - red) within the
    real cycle; phases 2/6 are the coordinated phases on recall. Actuated (Free) plans:
    maxDur from the observed max-out (maxg) where known. Other phases are called and
    extended by SUMO's stop-bar detectors (gap-out, skip when nobody waits)."""
    present = [p for p in range(1, 9) if splits.get(p, 0) > 0]
    splits = dict(splits)
    padded = []
    if coordinated:
        # SUMO requires both rings to add up to the cycle. Where a plan's rings don't close
        # (unverified read, or an unmodelled phase above 8), give the shortfall in each barrier
        # group to that ring's coordinated phase (else its last phase) -- what a controller
        # does with slack. Reported in the README.
        for g1, g2 in (((1, 2), (5, 6)), ((3, 4), (7, 8))):
            s1, s2 = sum(splits.get(p, 0) for p in g1), sum(splits.get(p, 0) for p in g2)
            if s1 and s2 and abs(s1 - s2) > 0.01:
                short = g2 if s1 > s2 else g1
                tgt = next((p for p in short if p in (2, 6) and p in present), None) or \
                    [p for p in short if p in present][-1]
                splits[tgt] += abs(s1 - s2)
                padded.append(f"P{tgt} +{abs(s1 - s2):.0f} s")
    if padded:
        used_default.add(("pad", name, ", ".join(padded)))
    rings = []
    for ring, (g1, g2) in ((1, ((1, 2), (3, 4))), (2, ((5, 6), (7, 8)))):
        seq = []
        for a, b in (g1, g2):
            order = (a, b) if lead.get(f"{a}/{b}", a) == a else (b, a)
            # SUMO's NEMA controller (1.27, TS2 coordinated, as configured here) does not serve a phase
            # that lags a coordinated phase (tested at 7065: lagging P1 got 1 green in 30 min, P2 took
            # its time; Type 170 serves it but mis-applies the force-offs). Run it leading
            # instead -- same splits, order within the barrier differs. Reported in the README.
            if coordinated and order[0] in (2, 6) and order[1] in present:
                order = (order[1], order[0])
                used_default.add(("leadfix", name, f"P{order[0]}"))
            seq += [p if p in present else 0 for p in order]
        rings.append(seq)
    # A ring with no phase in a barrier group (split-phased side street, one-way street, a
    # 2-phase signal) gets an all-red dummy phase there, as in real controller setups: it runs
    # its 1 s minimum and then rests at the barrier while the other ring finishes.
    dummies = {}
    for gi, (pos, even) in enumerate((((0, 1), (2, 6)), ((2, 3), (4, 8)))):
        filled = [any(rings[r][i] for i in pos) for r in (0, 1)]
        if filled[0] != filled[1]:
            r = 0 if not filled[0] else 1
            ph = even[r]
            other = sum(splits.get(p, 0) for p in (rings[1 - r][i] for i in pos) if p)
            rings[r][pos[1]] = ph
            dummies[ph] = other
            present.append(ph)
            splits[ph] = other
    coord = [p for p in (2, 6) if p in present] or [p for p in (1, 2, 5, 6) if p in present][:2]
    # max recall: phases that essentially never gap out in this plan (Split Monitor dot colours:
    # < 5% gap-outs) run their full split every cycle, as GDOT runs them
    term = term or {}
    recall = sorted(p for p in present if p not in coord and p not in dummies and coordinated
                    and str(p) in term and term[str(p)].get("gap", 1) < 0.05)
    if recall:
        used_default.add(("recall", name, ",".join(map(str, recall))))
    # SUMO only puts detectors on lanes with a full green ('G') in some phase. If a plan
    # omits a left's protected phase, its lane has no detector and can't call the phase that
    # serves it permissively -- left-turners would wait for a cross call. A real cabinet's
    # left-lane detector calls that phase; closest equivalent: min recall on it.
    perm_recall = set()
    for i, (prot, perm, _) in lp.items():
        if perm and prot and not (prot & set(present)):
            perm_recall |= {p for p in perm if p in present and p not in coord}
    # if GDOT's recorded green for such a phase (same plan) is at >= 90% of its max, it runs to
    # force-off in reality: max recall reproduces that (a long minDur instead makes SUMO's
    # coordinated controller skip the phase when the window is short)
    for p in sorted(perm_recall):
        y, r = yellow.get(p, DEFAULT_YELLOW), red.get(p, DEFAULT_RED)
        mx = splits.get(p, 0) - y - r
        if rec_med and p in rec_med and coordinated and mx > 0 and rec_med[p] >= 0.9 * mx:
            recall.append(p)
            used_default.add(("permmax", name, f"P{p} (recorded {rec_med[p]:.1f} of {mx:.1f} s)"))
    perm_recall -= set(recall)
    if perm_recall:
        used_default.add(("permrecall", name, ",".join(map(str, sorted(perm_recall)))))
    barrier = []
    for seq in rings:
        g2 = [p for p in seq[2:] if p]
        if g2:
            barrier.append(g2[-1])
    # Free/actuated: no real cycle; SUMO still needs a nominal one (0 makes it hang)
    free_cycle = max(sum(maxg.get(p, splits[p]) + yellow.get(p, DEFAULT_YELLOW) + red.get(p, DEFAULT_RED)
                         for p in seq if p) for seq in rings)
    L = [f'  <tlLogic id="{tlid}" type="NEMA" programID="{name}" offset="0">']
    prm = {"detector-length": 20, "detector-length-leftTurnLane": 20, "show-detectors": "true",
           "total-cycle-length": int(round(cycle)) if coordinated else int(round(free_cycle)),
           "ring1": ",".join(map(str, rings[0])), "ring2": ",".join(map(str, rings[1])),
           "barrierPhases": ",".join(map(str, barrier)), "coordinatePhases": ",".join(map(str, coord)),
           "coordinate-mode": "true" if coordinated else "false",
           "minRecall": ",".join(map(str, sorted(set(coord) | set(dummies) | perm_recall))),
           "maxRecall": ",".join(map(str, recall)),
           "fixForceOff": "false"}
    L += [f'    <param key="{k}" value="{v}"/>' for k, v in prm.items()]
    for p in sorted(present):
        if p in dummies:
            L.append(f'    <phase duration="99" minDur="1.0" maxDur="{max(1.0, dummies[p] - 2):.1f}" '
                     f'vehext="0.5" yellow="1.0" red="1.0" name="{p}" state="{"r" * n_links}"/>'
                     f'  <!-- dummy: rests at the barrier -->')
            continue
        y, r = yellow.get(p, DEFAULT_YELLOW), red.get(p, DEFAULT_RED)
        if p not in yellow or p not in red:
            used_default.add(p)
        mx = (splits[p] - y - r) if coordinated else maxg.get(p, splits[p] - y - r)
        mn = min(mins.get(p, 5.0), max(1.0, mx))

        st = "".join("G" if p in lp.get(i, (set(), set(), 0))[0] else
                     "g" if p in lp.get(i, (set(), set(), 0))[1] else "r" for i in range(n_links))
        e = (ext[1] if p % 2 else ext[0]) if isinstance(ext, tuple) else ext
        L.append(f'    <phase duration="99" minDur="{mn:.1f}" maxDur="{max(mn, mx):.1f}" '
                 f'vehext="{e:.1f}" yellow="{y:.1f}" red="{r:.1f}" name="{p}" state="{st}"/>')
    L.append("  </tlLogic>")
    return L


def build_signal(sid, d, net, date, sdir, controller="fixed", ext=2.0):
    notes = []
    tlid, links = link_table(sid, d, net)
    n_links = max(links) + 1
    lp = link_phases(links, d["phase_map"])
    dark = [i for i, (p, q, _) in lp.items() if not p and not q]
    if dark:
        names = sorted({f"{links[i][0]}_{links[i][1]}" for i in dark if links[i][0]})
        notes.append(f"Links with no phase (always red): {', '.join(names)} — movements with no "
                     "signal phase in GDOT's configuration (prohibited or not modelled).")
    mapped = {p["phase"] for p in d["phase_map"]["phases"]}
    c = d["clearance"] or {}
    yellow = {int(k): float(v) for k, v in (c.get("yellow") or {}).items() if v != ""}
    red = {int(k): float(v) for k, v in (c.get("red_clear") or {}).items() if v != ""}
    lead = {k: int(v) for k, v in (c.get("lead") or {}).items()}
    used_default = set()

    plans = d["plan"]["plans"]
    progs = {}
    for name, p in plans.items():
        sp = p.get("observed_s") if name == "Actuated" else p["splits_s"]
        splits = {int(k): float(v) for k, v in sp.items() if v not in ("", 0) and int(k) <= 8}
        for ph in splits:
            if ph not in yellow or ph not in red:
                used_default.add(ph)
        unmapped = sorted(set(splits) - mapped)
        if unmapped:
            notes.append(f"Plan {name}: phase(s) {unmapped} have splits but no movement in the phase "
                         "map; their time shows as red.")
        extra = sorted(int(k) for k, v in sp.items() if int(k) > 8 and v)
        if extra:
            notes.append(f"Plan {name}: phase(s) {extra} (above 8) are not modelled; ring time "
                         "they occupy is red.")
        tl, cycle = ring_timeline(splits, yellow, red, lead)
        progs[name] = (program_states(tl, cycle, lp, n_links), cycle)
    if used_default:
        notes.append(f"Yellow/red clearance not measured for phase(s) {sorted(x for x in used_default if isinstance(x, int))}: "
                     f"defaults {DEFAULT_YELLOW} s / {DEFAULT_RED} s used.")
    if "Actuated" in plans and controller != "nema":
        notes.append("APPROXIMATION: 'Actuated' periods (Free or uncoordinated) run as fixed "
                     "splits equal to the observed median phase times.")
    notes.append("Offsets unknown (coordination with neighbouring signals not modelled).")

    # time-of-day schedule for the date
    sched = d["plan"]["schedule"].get(date)
    if sched is None:
        fb = sorted(d["plan"]["schedule"])[-1]
        print(f"   WARNING: no timing schedule read for {date}; using {fb}'s "
              f"(run atspm_plans.py {sid} --date {date})", flush=True)
        notes.append(f"No timing schedule read for {date}: used {fb}'s schedule instead.")
        sched = d["plan"]["schedule"][fb]
    bands = [b for b in sched if b["kind"] in ("plan", "free") and b["plan"] in progs]
    if not bands:
        raise SystemExit(f"{sid}: no usable plan bands")
    # a band whose plan is an unverified read: if another day has a verified plan in the same
    # time slot (+-10 min), use that one (same clock schedule, chart line just hidden that day)
    bad = {k for k, p in plans.items() if any("unverified" in c or "mismatch" in c for c in p["checks"])}
    mins_ = lambda hm: int(hm[:2]) * 60 + int(hm[3:])
    def substitute(b):
        for day, bs in d["plan"]["schedule"].items():
            for o in bs:
                if o["kind"] == "plan" and o["plan"] not in bad and \
                        abs(mins_(o["start"]) - mins_(b["start"])) <= 10 and abs(mins_(o["end"]) - mins_(b["end"])) <= 10:
                    return o["plan"], day
        return None, None
    switches = []
    for b in sched:
        h, m = map(int, b["start"].split(":"))
        t = 0 if (h, m) == (0, 1) else h * 3600 + m * 60
        if b["kind"] == "plan" and b["plan"] in bad:
            alt, day = substitute(b)
            if alt:
                notes.append(f"{b['start']}-{b['end']}: plan {b['plan']} is an unverified read on {date}; "
                             f"used plan {alt}, read for the same time slot on {day}.")
                switches.append((t, alt))
                continue
        if b["kind"] in ("plan", "free") and b["plan"] in progs:
            switches.append((t, b["plan"]))
        elif b["kind"] == "no data" and t == 0:
            switches.append((0, bands[-1]["plan"]))
            notes.append(f"00:00-{b['end']} has no readable plan (carried over from the previous "
                         f"day); ASSUMED the day's last plan ({bands[-1]['plan']}).")
    switches.sort()
    dedup = []
    for t, p in switches:
        if not dedup or dedup[-1][1] != p:
            dedup.append((t, p))
    if dedup[0][0] != 0:
        dedup.insert(0, (0, dedup[0][1]))

    L = ["<additional>"]
    if controller == "nema":
        tim = d.get("actuation", {})
        mins, maxg = tim.get("min_green", {}), tim.get("max_green", {})
        # recorded greens are matched to plans using the schedule of the day they were recorded on
        sch = d["plan"]["schedule"].get(d.get("actuation_date", date), [])
        hm = lambda x: int(x[:2]) * 60 + int(x[3:])
        rec_by_plan = defaultdict(lambda: defaultdict(list))
        for (ws, ph), v in tim.get("recorded_greens", {}).items():
            band = next((b for b in sch if b["kind"] == "plan" and hm(b["start"]) <= hm(ws) < hm(b["end"])), None)
            if band:
                rec_by_plan[band["plan"]][ph] += v
        rec_med = {pl: {ph: sorted(v)[len(v) // 2] for ph, v in d_.items()} for pl, d_ in rec_by_plan.items()}
        for name, p in plans.items():
            sp = p.get("observed_s") if name == "Actuated" else p["splits_s"]
            splits = {int(k): float(v) for k, v in sp.items() if v not in ("", 0) and int(k) <= 8
                      and int(k) in mapped}
            L += nema_program(tlid, name, splits, name != "Actuated", progs[name][1], lp, n_links,
                              yellow, red, lead, mins, maxg, ext, used_default, p.get("termination"),
                              rec_med.get(name))
        for x in sorted(x for x in used_default if isinstance(x, tuple) and x[0] == "pad"):
            notes.append(f"Plan {x[1]}: rings don't add up to one cycle (unverified read or an "
                         f"unmodelled phase); slack given to {x[2]} so SUMO's controller accepts it.")
        pr = sorted(x for x in used_default if isinstance(x, tuple) and x[0] == "permrecall")
        if pr:
            notes.append("Min recall on phases serving a left only permissively when the plan omits that "
                         "left's protected phase (SUMO generates no detector for permissive-only lanes): " +
                         "; ".join(f"plan {x[1]}: P{x[2].replace(',', ', P')}" for x in pr) + ".")
        pm = sorted(x for x in used_default if isinstance(x, tuple) and x[0] == "permmax")
        if pm:
            notes.append("Max recall on phases that are the only service of a permissive-only left and ran at "
                         ">= 90% of their max in GDOT's recorded greens (Timing & Actuation, same plan): " +
                         "; ".join(f"plan {x[1]}: {x[2]}" for x in pm) + ".")
        rec = sorted(x for x in used_default if isinstance(x, tuple) and x[0] == "recall")
        if rec:
            notes.append("Max recall (full split every cycle, < 5% gap-outs on the Split Monitor): " +
                         "; ".join(f"plan {x[1]}: P{x[2].replace(',', ', P')}" for x in rec) + ".")
        lf = sorted({x[2] for x in used_default if isinstance(x, tuple) and x[0] == "leadfix"})
        if lf:
            notes.append(f"SUMO LIMITATION: GDOT runs {', '.join(lf)} after the coordinated phase (lagging); "
                         "SUMO's NEMA controller (TS2, coordinated, as configured here) does not serve a phase "
                         "that lags a coordinated phase, so it runs leading here (same splits). Type 170 serves "
                         "it but mis-applies these force-offs; other controller types untested. A fixed-time run with GDOT's exact order is in "
                         "rlagent/experiments/EXP-007_corrected-phase-model.")
        if "Actuated" in plans:
            notes.append("'Actuated' periods (Free or uncoordinated) run actuated, uncoordinated, "
                         "with max greens from Split Monitor max-outs where seen, otherwise the 95th "
                         "percentile of observed phase times (a lower bound on the real max).")
        notes.append(f"Controller: SUMO NEMA actuated dual ring. Coordinated plans use the real "
                     f"splits as force-offs within the real cycle, phases 2/6 coordinated; other "
                     f"phases gap out / skip on 20 m stop-bar detectors. Vehicle extension "
                     + (f"{ext[0]:.1f} s through phases, {ext[1]:.1f} s left-turn phases"
                        if isinstance(ext, tuple) else f"{ext:.1f} s")
                     + " (not published by GDOT; fitted to the recorded greens).")
    else:
        for name, (phases, cycle) in progs.items():
            L.append(f'  <tlLogic id="{tlid}" type="static" programID="{name}" offset="0">'
                     f'  <!-- cycle {cycle:.0f} s -->')
            for dur, st in phases:
                L.append(f'    <phase duration="{dur:.1f}" state="{st}"/>')
            L.append("  </tlLogic>")
    # neighbouring signals in the OSM area run netconvert's guessed programs and would throttle
    # traffic leaving the target; switch them off (unsignalised, priority rules) so the check
    # measures this intersection only
    others = [t for t in net.getTrafficLights() if t.getID() != tlid]
    for t in others:
        L.append(f'  <tlLogic id="{t.getID()}" type="static" programID="off" offset="0"/>')
    if others:
        notes.append(f"{len(others)} neighbouring signal(s) in the network area switched off "
                     "(their timing is unknown); only the target signal is controlled.")
    L.append(f'  <WAUT id="tod" refTime="0" startProg="{dedup[0][1]}">')
    for t, p in dedup[1:]:
        L.append(f'    <wautSwitch time="{t}" to="{p}"/>')
    L += ["  </WAUT>", f'  <wautJunction wautID="tod" junctionID="{tlid}"/>',
          f'  <timedEvent type="SaveTLSStates" source="{tlid}" dest="states.xml"/>', "</additional>"]
    (sdir / "signal.add.xml").write_text("\n".join(L) + "\n")
    return notes, tlid, progs, dedup, links, lp


# =========================================================================== configs
def write_configs(sid, d, net, sdir):
    netrel = os.path.relpath(d["net_path"], sdir)
    for name, begin, end, gui in (("sim", 0, 86400, False), ("peak", CHECK_BEGIN, CHECK_END, False),
                                  ("gui", GUI_BEGIN, GUI_END, True)):
        extra = '\n    <gui-settings-file value="view.xml"/>' if gui else ""
        (sdir / f"{name}.sumocfg").write_text(f"""<configuration>
  <input>
    <net-file value="{netrel}"/>
    <route-files value="demand.rou.xml"/>
    <additional-files value="signal.add.xml"/>{extra}
  </input>
  <time><begin value="{begin}"/><end value="{end}"/></time>
  <processing><time-to-teleport value="300"/><ignore-route-errors value="true"/></processing>
  <report><no-step-log value="true"/></report>
</configuration>
""")
    node = net.getNode(d["junction"]["node"])
    x, y = node.getCoord()
    (sdir / "view.xml").write_text(f"""<viewsettings>
  <scheme name="real world"/>
  <delay value="40"/>
  <viewport zoom="600" x="{x:.1f}" y="{y:.1f}"/>
</viewsettings>
""")


def snapshot(sid, sdir, tlid):
    cfg = sdir / "snap_view.xml"
    v = (sdir / "view.xml").read_text().replace('<delay value="40"/>', '<delay value="0"/>')
    v = v.replace("</viewsettings>", f'  <snapshot file="snapshot.png" time="{SNAP_T}"/>\n</viewsettings>')
    cfg.write_text(v)
    (sdir / "snapshot.png").unlink(missing_ok=True)
    try:
        p = subprocess.run(["sumo-gui", "-c", "gui.sumocfg", "--gui-settings-file", "snap_view.xml",
                            "--start", "--quit-on-end", "--end", str(SNAP_T + 2),
                            "--window-size", "1600,1000", "--window-pos", "0,0"],
                           cwd=sdir, capture_output=True, text=True, timeout=300)
        err = p.stderr[-500:]
    except subprocess.TimeoutExpired:
        err = "sumo-gui did not finish within 5 min"
    cfg.unlink(missing_ok=True)
    return (sdir / "snapshot.png").exists(), err


def run_check(sdir):
    p = subprocess.run(["sumo", "-c", "peak.sumocfg", "--statistic-output", "stats.xml",
                        "--duration-log.statistics"],
                       cwd=sdir, capture_output=True, text=True, timeout=3600)
    out = p.stdout + p.stderr
    r = ET.parse(sdir / "stats.xml").getroot()
    v, t, s, ts = r.find("vehicles"), r.find("teleports"), r.find("safety"), r.find("vehicleTripStatistics")
    res = {k: int(v.get(k)) for k in ("loaded", "inserted", "running", "waiting")}
    res.update(teleports=int(t.get("total")), jams=int(t.get("jam")), collisions=int(s.get("collisions")),
               mean_wait_s=float(ts.get("waitingTime")), mean_timeloss_s=float(ts.get("timeLoss")),
               mean_depart_delay_s=float(ts.get("departDelay")),
               warnings=len([l for l in out.splitlines() if l.startswith("Warning")]))
    return res


# =========================================================================== validation
EXT_CANDIDATES = (1.0, 2.0, 3.0, 4.0)                 # through phases (even)
EXT_LEFT_CANDIDATES = (2.0, 3.0, 4.0, 6.0, 8.0)             # left-turn phases (odd)
VAL_WINDOWS = (("08:00", 7 * 3600 + 30 * 60, 8 * 3600 + 20 * 60), ("17:00", 16 * 3600 + 30 * 60, 17 * 3600 + 20 * 60))


def sim_greens(sdir, net, tlid, lp, begin, end):
    """Run [begin, end] and return {(window, phase): [protected green durations]} from the
    recorded signal states (G only, so a permissive 'g' after a protected left isn't counted)."""
    (sdir / "states.xml").unlink(missing_ok=True)
    subprocess.run(["sumo", "-c", "sim.sumocfg", "--begin", str(begin), "--end", str(end),
                    "--no-warnings"], cwd=sdir, capture_output=True, text=True, timeout=1800)
    rep = {}
    for p in range(1, 9):
        only = [i for i, (pr, pm, _) in lp.items() if pr == {p} and not pm]
        anyp = [i for i, (pr, pm, _) in lp.items() if p in pr]
        if only or anyp:
            rep[p] = (only or anyp)[0]
    out = defaultdict(list)
    if not (sdir / "states.xml").exists():
        return out
    seq = [(float(e.get("time")), e.get("state")) for e in ET.parse(sdir / "states.xml").getroot()
           if e.get("state")]
    for p, li in rep.items():
        start = None
        for (t, st), nxt in zip(seq, seq[1:] + [(float(end), "")]):
            g = li < len(st) and st[li] == "G"
            if g and start is None:
                start = t
            if start is not None and not (li < len(nxt[1]) and nxt[1][li] == "G"):
                for wname, wb, _ in VAL_WINDOWS:
                    h, m = map(int, wname.split(":"))
                    w0 = h * 3600 + m * 60
                    if w0 <= start < w0 + 900:
                        out[(wname, p)].append(nxt[0] - start)
                start = None
    return out


def compare(simg, recg):
    """rows per (window, phase): recorded median, simulated median; and mean abs error."""
    med = lambda v: sorted(v)[len(v) // 2] if v else None
    rows, errs = [], []
    simulated = {w for w, _, _ in VAL_WINDOWS}
    for key in sorted(k for k in set(recg) | set(simg) if k[0] in simulated):
        r, s_ = med(recg.get(key, [])), med(simg.get(key, []))
        rows.append((key[0], key[1], r, len(recg.get(key, [])), s_, len(simg.get(key, []))))
        if r is not None and s_ is not None:
            errs.append(abs(r - s_))
        elif r is not None:                      # phase ran in reality but never in the sim
            errs.append(r)
    return rows, (sum(errs) / len(errs) if errs else float("inf"))


def calibrate(sid, d, net, date, sdir):
    best = None
    for ext in [(t, l) for t in EXT_CANDIDATES for l in EXT_LEFT_CANDIDATES]:
        notes, tlid, progs, sched, links, lp = build_signal(sid, d, net, date, sdir, "nema", ext)
        simg = defaultdict(list)
        for wname, wb, we in VAL_WINDOWS:
            for k, v in sim_greens(sdir, net, tlid, lp, wb, we).items():
                simg[k] += v
        rows, err = compare(simg, d["actuation"]["recorded_greens"])
        print(f"   extension through {ext[0]:.1f} s / left {ext[1]:.1f} s: mean |green error| {err:.1f} s",
              flush=True)
        if best is None or err < best[1]:
            best = (ext, err, rows)
    return best


# =========================================================================== report
def write_readme(sid, d, date, sdir, dnotes, totals, nflows, snotes, tlid, progs, sched, res, snap_ok,
                 val=None, controller="fixed"):
    name = d["plan"]["name"]
    L = [f"# Simulation — signal {sid} ({name})", "",
         f"Quality-check simulation built by `tools/build_sim.py` from the real data for "
         f"**{date}**: network = {d['network_source']}, measured 5-min turning-movement counts, "
         "and the real time-of-day signal plans.", "",
         "```bash", f"cd {rel(sdir)}", "sumo-gui -c gui.sumocfg     # 07:45-09:00, press play",
         "sumo -c sim.sumocfg         # full day, headless", "```", ""]
    if snap_ok:
        L += ["![snapshot at 08:30](snapshot.png)", ""]
    L += ["## Demand (measured counts)", "", "| Movement | Vehicles in the day |", "|---|---|"]
    L += [f"| {c} | {v} |" for c, v in sorted(totals.items())]
    L += ["", f"{sum(totals.values())} vehicles in {nflows} five-minute flows. Each flow starts "
          "upstream of the approach and passes the intersection.", ""]
    L += ["## Signal (real plans)", "", f"Signal `{tlid}`. Schedule:", ""]
    hm = lambda t: f"{t // 3600:02d}:{t % 3600 // 60:02d}"
    L += [" · ".join(f"{hm(t)} **{p}** ({progs[p][1]:.0f} s)" for t, p in sched), ""]
    L += ["Phase → movement: `../timing/phase_map.json` (from GDOT's Split Failure chart titles); "
          "splits: `../timing/timing_plan_" + sid + ".md`.", ""]
    if controller == "nema":
        act = d["actuation"]
        L += ["### Actuation parameters", "",
              "| Phase | Min green (s, measured) | Max green in actuated periods (s) |", "|---|---|---|"]
        for p in sorted(set(act["min_green"]) | set(act["max_green"])):
            mg = act["max_green"].get(p)
            L.append(f"| P{p} | {act['min_green'].get(p, '5.0 (default)')} | "
                     f"{(f'{mg:.0f} (' + act['max_source'][p] + ')') if mg else '–'} |")
        L.append("")
    if val:
        ext, err, rows = val
        L += ["## Validation against the recorded signal (2026-10-02)", "",
              f"Vehicle extension chosen: **{ext[0]:.1f} s through phases, {ext[1]:.1f} s left-turn "
              f"phases** (grid {', '.join(map(str, EXT_CANDIDATES))} × {', '.join(map(str, EXT_LEFT_CANDIDATES))}), "
              f"mean absolute error of median green per phase: **{err:.1f} s**.", "",
              "| Window | Phase | Recorded median green (s) | n | Simulated median green (s) | n |",
              "|---|---|---|---|---|---|"]
        f = lambda v: "–" if v is None else f"{v:.1f}"
        L += [f"| {w} | P{p} | {f(r)} | {nr} | {f(s_)} | {ns} |" for w, p, r, nr, s_, ns in rows]
        L.append("")
    L += ["## Assumptions and gaps", ""] + [f"- {n}" for n in dnotes + snotes] + [""]
    L += ["## Quality check (07:00-09:30, headless)", ""]
    if res:
        ok = res["teleports"] == 0 and res["collisions"] == 0 and res["waiting"] == 0
        L += [f"- vehicles loaded {res['loaded']}, inserted {res['inserted']}, still waiting to "
              f"enter at 09:30 {res['waiting']}, still running {res['running']}",
              f"- teleports {res['teleports']} (jams {res['jams']}), collisions {res['collisions']}, "
              f"SUMO warnings {res['warnings']}",
              f"- mean per trip: waiting {res['mean_wait_s']:.1f} s, time loss "
              f"{res['mean_timeloss_s']:.1f} s, departure delay {res['mean_depart_delay_s']:.1f} s",
              f"- **{'PASS' if ok else 'CHECK'}** (pass = no teleports, no collisions, no entry backlog at 09:30)"]
    else:
        L.append("_Not run (--no-run)._")
    (sdir / "README.md").write_text("\n".join(L) + "\n")


# =========================================================================== main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("signals", nargs="+")
    ap.add_argument("--date", default="2026-10-02")
    ap.add_argument("--no-run", action="store_true", help="write files only")
    ap.add_argument("--no-snapshot", action="store_true")
    ap.add_argument("--arrivals", choices=["poisson", "even"], default="poisson",
                    help="poisson (default): measured count per 5-min bin at random times; even: evenly spaced")
    ap.add_argument("--controller", choices=["nema", "fixed"], default="nema",
                    help="nema = actuated-coordinated, calibrated to the recorded signal (default); "
                         "fixed = programmed splits as fixed time")
    a = ap.parse_args()
    for sid in a.signals:
        print(f"== {sid}", flush=True)
        d = load(sid)
        net = sumolib.net.readNet(str(d["net_path"]), withPrograms=True)
        sdir = sig_dir(sid, "sim")
        sdir.mkdir(parents=True, exist_ok=True)
        d["actuation"] = actuation_params(d, a.date)
        dnotes, totals, nflows = build_demand(sid, d, a.date, net, sdir, a.arrivals)
        write_configs(sid, d, net, sdir)
        val = None
        if a.controller == "nema" and not a.no_run:
            val = calibrate(sid, d, net, a.date, sdir)
            snotes, tlid, progs, sched, _, _ = build_signal(sid, d, net, a.date, sdir, "nema", val[0])
        else:
            snotes, tlid, progs, sched, _, _ = build_signal(sid, d, net, a.date, sdir, a.controller)
        res, snap_ok = None, False
        if not a.no_run:
            res = run_check(sdir)
            print(f"   check: inserted {res['inserted']}/{res['loaded']}, waiting {res['waiting']}, "
                  f"teleports {res['teleports']}, collisions {res['collisions']}, "
                  f"time loss {res['mean_timeloss_s']:.0f} s", flush=True)
            if not a.no_snapshot:
                snap_ok, err = snapshot(sid, sdir, tlid)
                print(f"   snapshot: {'ok' if snap_ok else 'FAILED ' + err}", flush=True)
        write_readme(sid, d, a.date, sdir, dnotes, totals, nflows, snotes, tlid, progs, sched, res, snap_ok,
                     val, a.controller)
        print(f"   -> {rel(sdir)}/README.md", flush=True)


if __name__ == "__main__":
    main()
