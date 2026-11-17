"""Write atsc/sites/137/neighbour138/signal.json: signal 138 (W Paces Ferry @ Paces Ferry Pl) under its own field timing,
as the upstream neighbour of 137 (VALIDATION.md attempt 6).

    uv run python atsc/sites/137/neighbour138/make_signal.py [offsets.json]

Sources (GDOT ATSPM): plans + schedule per day from intersections/138/timing/timing_plan_138.json (Split Monitor),
clearances and lead/lag from its clearance.json. ASSUMPTIONS (not read for 138): minimum greens as measured at 137 for
the same kind of phase (main 12.0 s, left 5.1 s, side street 7.8 s); no pedestrian timing. Phases 3, 7 do not exist;
P4 (driveway) and P5 (WB left into the driveway) have no modelled demand. offsets.json (from offset_138.py): per plan,
the absolute offset that puts 138's coordinated greens where the field has them relative to 137's.
"""
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
T = HERE.parents[3] / "intersections/138/timing"
MIN = {1: 5.1, 2: 12.0, 4: 7.8, 5: 5.1, 6: 12.0, 8: 7.8, 3: 5.1, 7: 5.1}


def main():
    clr = json.loads((T / "clearance.json").read_text())
    tp = json.loads((T / "timing_plan_138.json").read_text())
    y = {int(k): float(v) for k, v in clr["yellow"].items()}
    r = {int(k): float(v) for k, v in clr["red_clear"].items()}
    for q in range(1, 9):                                   # phases without a read clearance: 137's typical values
        y.setdefault(q, 3.9 if q in (2, 6) else 2.9)
        r.setdefault(q, 2.4 if q in (2, 6) else 2.9)
    lead = {k: int(v) for k, v in clr.get("lead", {}).items()}

    def order(a, b):
        k = f"{min(a, b)}/{max(a, b)}"
        return [a, b] if lead.get(k, min(a, b)) == a else [b, a]
    rings = {"1": [order(1, 2), order(3, 4)], "2": [order(5, 6), order(7, 8)]}
    plans = {k: {"cycle": p["cycle_s"], "splits": {int(q): s for q, s in p["splits_s"].items()},
                 "coordinated": [2, 6], "termination": p.get("termination", {})}
             for k, p in tp["plans"].items()
             if p.get("checks") == ["ok"] and p.get("cycle_s") and all(p["splits_s"].get(str(q), 0) > 0 for q in (2, 6))}
    offs = json.loads(Path(sys.argv[1]).read_text())["offset_s"] if len(sys.argv) > 1 else {}
    for k, p in plans.items():
        if k in offs:
            p["offset_s"] = offs[k]
    max_green = {q: max([pl["splits"].get(q, 0) - y[q] - r[q] for pl in plans.values()] + [0]) for q in range(1, 9)}
    # P2/P6 (main street) on recall: coordinated phases are always served, and 138 has only advance zones on them,
    # which extend but do not call (standard coordinated practice; ASSUMPTION for the free/night bands)
    phases = {q: {"min_green": MIN[q], "min_green_n": 0, "yellow": y[q], "red": r[q], "ped_min": 0.0, "recall": q in (2, 6),
                  "max_green_free": round(max(max_green[q], MIN[q] + 5), 1)} for q in range(1, 9)}
    schedule, bad = {}, []
    for date, bands in tp["schedule"].items():
        sch = []
        for b in bands:
            if b["kind"] == "plan" and b["plan"] in plans:
                sch.append([b["start"], b["plan"]])
            elif b["kind"] == "free":
                sch.append([b["start"], "FREE"])
            elif b["kind"] == "no data" or (b["kind"] == "plan" and b.get("minutes", 0) < 20):
                continue
            else:
                sch = None
                bad.append(date)
                break
        schedule[date] = sch
    dated = sorted(d for d, v in schedule.items() if v)
    for d in bad:
        n = min(dated, key=lambda x: abs((dt.date.fromisoformat(x) - dt.date.fromisoformat(d)).days))
        schedule[d] = schedule[n]
    # 137 and 138 are coordinated: they share the cycle at every time (91 % of daytime 15-min points in the two
    # signals' own reads; the rest are band edges read a few minutes apart and misread bands, e.g. 138 on 03-24 with
    # 14:01-20:01 read as B). So 138 follows 137's schedule, with 138's verified plan of the same cycle.
    s137 = json.loads((HERE.parent / "signal.json").read_text())
    by_cycle = {}
    for k, p in plans.items():
        seen = len(tp["plans"][k].get("seen", []))
        if p["cycle"] not in by_cycle or seen > by_cycle[p["cycle"]][1]:
            by_cycle[p["cycle"]] = (k, seen)
    mapping = {k: by_cycle[p["cycle"]][0] for k, p in s137["plans"].items() if p["cycle"] in by_cycle}
    schedule = {d: ([[t, "FREE" if n == "FREE" else mapping.get(n, "FREE")] for t, n in v] if v else None)
                for d, v in s137["schedule_by_date"].items()}
    canon = [[t, "FREE" if n == "FREE" else mapping.get(n, "FREE")] for t, n in s137["canonical_schedule"]["weekday"]]
    out = {"signal": "138", "tls": "69548021", "rings": rings, "phases": phases, "plans": plans,
           "schedule_by_date": schedule, "canonical_schedule": {"weekday": canon},
           "notes": {"assumptions": "min greens from 137 by phase type; no pedestrian timing; driveway leg absent",
                     "offsets": "offset_s per plan from offset_138.py (field green starts of 137 and 138), else plan start"}}
    (HERE / "signal.json").write_text(json.dumps(out, indent=1))
    print(f"wrote signal.json: plans {sorted(plans)} cycles {[p['cycle'] for p in plans.values()]}, offsets {offs}, "
          f"schedule = 137's with plan mapping {mapping}")


if __name__ == "__main__":
    main()
