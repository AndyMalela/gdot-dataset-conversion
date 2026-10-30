"""Demand from GDOT turning-movement counts: day quality, physical-capacity flags, SUMO routes.

    days = load_counts(site_dir)                       # {date: [Bin]}, locked test days refused
    q = day_quality(bins)                              # complete | usable | suspect | bad
    bound = BinBound(site_dir); bound.limit(date, t, col)   # most vehicles a 5-min bin can physically count
    write_routes(site_dir, net_file, date, "demand.rou.xml", seed=1)

Counts are used as recorded: outage bins generate no traffic (and are listed for masking), bins above
the physical bound are flagged, never capped or rescaled (fidelity policy, /CLAUDE.md).
"""
from __future__ import annotations

import datetime as dt
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path

import csv

from .nema import NemaEngine, Phase, Plan

REPO = Path(__file__).resolve().parents[2]
BIN = 300
DAY0, DAY1 = 6 * 3600, 22 * 3600        # "daytime" for the quality rules (as tools/dataset_7065.py)
USABLE_MAX_DAY_OUTAGE = 30 * 60
STUCK_MIN = 2 * 3600
S_MAX = 2400            # veh/h/lane of green: a physical ceiling (1.5 s headway), well above HCM's 1,900 base
JAM_SPACING = 7.0       # m per queued car (5 m car + 2 m gap): storage between a setback loop and the stop line


@dataclass
class Bin:
    t: int                      # seconds after midnight, bin start
    status: str                 # ok | outage
    counts: dict[str, int]      # column -> vehicles (empty for outage bins)


def _site(site_dir):
    site_dir = Path(site_dir)
    sig = json.loads((site_dir / "signal.json").read_text())
    mv = json.loads((site_dir / "movements.json").read_text())
    split = json.loads((site_dir / "split.json").read_text())
    return sig, mv, split


def day_set(split, date):
    for name, s in split["sets"].items():
        if s["from"] <= str(date) <= s["to"]:
            return name
    return None


def is_locked(split, date):
    s = day_set(split, date)
    return s is not None and split["sets"][s].get("locked", False)


def load_counts(site_dir, allow_locked=False):
    """{date: [Bin]} from intersections/<sig>/counts/tmc_<sig>_5min.csv. Rows of locked test days are
    skipped without reading their values unless allow_locked (final evaluation only)."""
    sig, mv, split = _site(site_dir)
    cols = list(mv["movements"])
    out = {}
    path = REPO / "intersections" / sig["signal"] / "counts" / f"tmc_{sig['signal']}_5min.csv"
    for r in csv.DictReader(open(path)):
        d = dt.date.fromisoformat(r["date"])
        if is_locked(split, d) and not allow_locked:
            continue
        h, m = map(int, r["time"].split(":"))
        ok = r["status"] == "ok"
        out.setdefault(d, []).append(Bin(h * 3600 + m * 60, r["status"],
                                         {c: int(r[c]) for c in cols} if ok else {}))
    return out


def day_quality(bins):
    """complete / usable (<= 30 min daytime outage) / bad, and suspect when one movement reads 0 for
    >= 2 h of daytime while the others count. Same rules as tools/dataset_7065.py."""
    outage = [b for b in bins if b.status != "ok"]
    day_out = sum(BIN for b in outage if DAY0 <= b.t < DAY1)
    q = "complete" if not outage else ("usable" if day_out <= USABLE_MAX_DAY_OUTAGE else "bad")
    stuck = {}
    cols = next((list(b.counts) for b in bins if b.counts), [])
    for c in cols:
        run = best = 0
        for b in sorted(bins, key=lambda b: b.t):
            if b.status != "ok" or not (DAY0 <= b.t < DAY1):
                continue
            others = sum(v for k, v in b.counts.items() if k != c)
            run = run + BIN if b.counts[c] == 0 and others > 0 else 0
            best = max(best, run)
        if best >= STUCK_MIN:
            stuck[c] = best // 60
    if stuck and q in ("complete", "usable"):
        q = "suspect"
    return q, {"outage_bins": len(outage), "daytime_outage_min": day_out // 60, "stuck_min": stuck}


# ---------------------------------------------------------------------------- physical bound
def schedule(sig, date):
    """[(start s, plan name)] for the day: dated read if verified, else the canonical day type."""
    s = sig["schedule_by_date"].get(str(date))
    if not s:
        kind = "saturday" if date.weekday() == 5 else ("weekday" if date.weekday() < 5 else None)
        s = sig["canonical_schedule"].get(kind) if kind else None
    if not s:
        return None
    return sorted((int(t[:2]) * 3600 + int(t[3:]) * 60, n) for t, n in s)


def max_service(sig, plan_name, serving, window=BIN, dt_=0.5):
    """Most seconds of green + yellow the `serving` phases can get in any `window` s under the plan,
    with the NEMA rules of nema.py: the serving phases always called and never asked to end, every
    other phase called only if on recall and ended as soon as its minimum allows."""
    ph = {int(k): Phase(v["min_green"], v["yellow"], v["red"], v["ped_min"], recall=v["recall"])
          for k, v in sig["phases"].items()}
    rings = {int(r): tuple(tuple(g) for g in gs) for r, gs in sig["rings"].items()}
    p = sig["plans"][plan_name]
    plan = Plan(plan_name, p["cycle"], {int(k): v for k, v in p["splits"].items()}, tuple(p["coordinated"]))
    eng = NemaEngine(rings, ph, plan)
    calls, on = set(serving), []
    t, end = 0.0, 12 * plan.cycle
    while t < end:
        ends = {r for r in (1, 2) if r in eng.r and eng.r[r].phase not in serving}
        disp = eng.tick(t, calls, ends)
        on.append(any(disp.get(q) in ("G", "y") for q in serving))
        t = round(t + dt_, 6)
    n, k0 = int(window / dt_), int(2 * plan.cycle / dt_)          # skip the first two cycles
    s = sum(on[k0:k0 + n])
    best = s
    for i in range(k0 + n, len(on)):
        s += on[i] - on[i - n]
        best = max(best, s)
    return best * dt_


class BinBound:
    """Most vehicles a movement's detectors can count in one 5-min bin, given the plan(s) in effect:
    lanes x S_MAX x max green+yellow in the bin, plus (setback-counted movements) the queue that fits
    between the setback loop and the stop line, counted but not yet discharged."""
    def __init__(self, site_dir):
        self.sig, self.mv, _ = _site(site_dir)
        det = json.loads((Path(site_dir) / "detectors.json").read_text())
        self.setback_m = {d["phase"]: d["dist_m"] for d in det["detectors"] if d["kind"] == "setback"}
        self._svc = {}

    def service(self, plan, col):
        key = (plan, col)
        if key not in self._svc:
            self._svc[key] = max_service(self.sig, plan, set(self.mv["movements"][col]["phases"]))
        return self._svc[key]

    def plans_in_bin(self, date, t):
        sch = schedule(self.sig, date)
        if sch is None:
            return []
        cur = [n for t0, n in sch if t0 <= t][-1:] or [sch[0][1]]
        return cur + [n for t0, n in sch if t < t0 < t + BIN]

    def limit(self, date, t, col):
        plans = self.plans_in_bin(date, t)
        if not plans:
            return None
        m = self.mv["movements"][col]
        svc = max(self.service(p, col) for p in plans)
        lim = m["lanes"] * S_MAX / 3600 * svc
        if m["counted_at"] == "setback":
            lim += m["lanes"] * self.setback_m[m["phases"][0]] / JAM_SPACING
        return lim


# ---------------------------------------------------------------------------- routes
def write_routes(site_dir, net_file, date, out, seed=1, vtype=None, depart_lane="random", allow_locked=False):
    """One vehicle per counted vehicle, at a uniformly random time in its 5-min bin (Poisson arrivals
    with the measured count), departing early by its free-flow time from the network entry to the
    detector that counted it, so it reaches that detector inside its bin. Outage bins: no vehicles.
    Writes `out` and `out`.meta.json (outage windows, per-movement totals)."""
    import sumolib
    sig, mv, split = _site(site_dir)
    date = dt.date.fromisoformat(str(date))
    if is_locked(split, date) and not allow_locked:
        raise PermissionError(f"{date} is in the locked test set")
    bins = load_counts(site_dir, allow_locked)[date]
    net = sumolib.net.readNet(str(Path(net_file).resolve()))
    det = json.loads((Path(site_dir) / "detectors.json").read_text())
    setback_m = {d["phase"]: d["dist_m"] for d in det["detectors"] if d["kind"] == "setback"}
    tls = sig["tls"]
    tl_in = {c[0].getEdge().getID() for c in net.getTLS(tls).getConnections()}

    routes, lead = {}, {}
    for col, m in mv["movements"].items():
        entry = net.getEdge(mv["entry_edges"][m["leg"]])
        p1, _ = net.getShortestPath(entry, net.getEdge(m["from"]), vClass="passenger")
        p2, _ = net.getShortestPath(net.getEdge(m["from"]), net.getEdge(m["to"]), vClass="passenger")
        edges = [e.getID() for e in p1] + [e.getID() for e in p2[1:]]
        if sum(e in tl_in for e in edges) != 1:
            raise ValueError(f"route for {col} crosses {tls} {sum(e in tl_in for e in edges)} times")
        routes[col] = " ".join(edges)
        # free-flow time from the entry to the counting detector (setback loop or stop line)
        to_stop = sum(e.getLength() / e.getSpeed() for e in p1)
        back = setback_m[m["phases"][0]] if m["counted_at"] == "setback" else 0.0
        lead[col] = to_stop - back / net.getEdge(m["from"]).getSpeed()

    rng = random.Random(seed)
    veh, outage, total = [], [], {c: 0 for c in mv["movements"]}
    for b in sorted(bins, key=lambda b: b.t):
        if b.status != "ok":
            outage.append(b.t)
            continue
        for col, n in b.counts.items():
            total[col] += n
            for i in range(n):
                veh.append((max(0.0, round(b.t + rng.uniform(0, BIN) - lead[col], 2)), f"{col}.{b.t}.{i}", col))
    veh.sort()

    va = {"vClass": "passenger", **(vtype or {})}
    L = ["<routes>", '  <vType id="car" ' + " ".join(f'{k}="{v}"' for k, v in va.items()) + "/>"]
    L += [f'  <route id="{c}" edges="{e}"/>' for c, e in routes.items()]
    L += [f'  <vehicle id="{v}" type="car" route="{c}" depart="{t}" departLane="{depart_lane}" departSpeed="max"/>'
          for t, v, c in veh]
    L.append("</routes>")
    Path(out).write_text("\n".join(L) + "\n")

    wins = []
    for t in outage:
        if wins and wins[-1][1] == t:
            wins[-1][1] = t + BIN
        else:
            wins.append([t, t + BIN])
    meta = {"date": str(date), "seed": seed, "vtype": va, "depart_lane": depart_lane, "vehicles": len(veh), "per_movement": total,
            "outage_windows_s": wins, "lead_s": {c: round(v, 1) for c, v in lead.items()},
            "rights": "not counted by GDOT: no right-turn demand"}
    Path(str(out) + ".meta.json").write_text(json.dumps(meta, indent=1))
    return meta
