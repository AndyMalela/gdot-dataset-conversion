"""Write atsc/sites/137/signal.json: everything the NEMA engine needs for SIG 137, with sources.

    uv run python atsc/sites/137/make_signal.py

Sources (all GDOT ATSPM, read by tools/atspm_plans.py and tools/atspm_timing.py):
  rings / lead-lag / clearances   intersections/137/timing/clearance.json  (P1 clearance not read: P5's used)
  plans + schedule                intersections/137/timing/timing_plan_137.json (plans A-D, all checks ok)
  min greens                      intersections/137/timing/greens_137.csv ('min green complete' blocks, median)
  pedestrian timing               NOT read for 137 (2026-11-16): ped_min 0, no ped recall
Night (00:01-06:31, 22:01-24:00) runs Free on the Split Monitor: schedule entries "FREE" -> no plan (engine free mode).
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
T = HERE.parents[2] / "intersections/137/timing"
CANONICAL = {"weekday": [["00:00", "FREE"], ["06:31", "A"], ["10:02", "B"], ["14:01", "C"], ["20:01", "D"], ["22:01", "FREE"]]}


def main():
    clr = json.loads((T / "clearance.json").read_text())
    tp = json.loads((T / "timing_plan_137.json").read_text())
    y = {int(k): float(v) for k, v in clr["yellow"].items()}
    r = {int(k): float(v) for k, v in clr["red_clear"].items()}
    assumed = {}
    if 1 not in y:                       # P1 (WB left) was not in the clearance window: same as P5, the opposite left
        y[1], r[1] = y[5], r[5]
        assumed[1] = "yellow/red not read for P1 (no green in the 5-min clearance window); P5's values used"
    lead = {k: int(v) for k, v in clr["lead"].items()}

    def order(a, b):
        return [a, b] if lead[f"{min(a, b)}/{max(a, b)}"] == a else [b, a]
    rings = {"1": [order(1, 2), order(3, 4)], "2": [order(5, 6), order(7, 8)]}

    mins = defaultdict(list)
    for row in csv.DictReader(open(T / "greens_137.csv")):
        if row["chart"].startswith("Phase_") and row["min_green_s"]:
            mins[int(row["chart"].split("_")[1].rstrip("b"))].append(float(row["min_green_s"]))
    med = lambda v: sorted(v)[len(v) // 2]

    verified = {k: p for k, p in tp["plans"].items() if p.get("checks") == ["ok"] and p.get("cycle_s")
                and all(p["splits_s"].get(str(q), 0) > 0 for q in (2, 6))}   # a plan without the main-street phases is a misread
    plans = {k: {"cycle": p["cycle_s"], "splits": {int(q): s for q, s in p["splits_s"].items()},
                 "coordinated": [2, 6], "termination": p.get("termination", {})}
             for k, p in verified.items()}
    max_green = {q: max(pl["splits"][q] - y[q] - r[q] for pl in plans.values() if pl["splits"].get(q, 0) > 0)
                 for q in range(1, 9)}
    phases = {q: {"min_green": med(mins[q]), "min_green_n": len(mins[q]), "yellow": y[q], "red": r[q],
                  "ped_min": 0.0, "recall": False, "max_green_free": round(max_green[q], 1)} for q in range(1, 9)}
    # pedestrians, measured 2026-11-16 on train days 03-10, 03-24, 04-08, every hour 06-21 (48 Timing & Actuation
    # windows, intervals_137.csv): ped overlap q serves the crossing timed with phase q.
    #   OL2 / OL6 (main-street crossings): a walk in every cycle of every window (rest in walk) -> ped recall;
    #       flashing don't walk 17.1 / 20.5 s; the minimum walk is not observable while resting in walk -> 4.0 s,
    #       the walk measured on the actuated crossings (ASSUMPTION)
    #   OL4 / OL8 (side-street crossings): walk 4.0 s + FDW 20.5 / 18.1 s, served only on a push; hourly rates below
    PED = {2: (4.0, 17.1, "recall"), 6: (4.0, 20.5, "recall"), 4: (4.0, 20.5, "actuated"), 8: (4.0, 18.1, "actuated")}
    PED_RATE = {   # pedestrian services per hour, mean of the 3 days; hours 00-05 and 22-23 not measured -> 0
        4: [0, 0, 0, 0, 0, 0, 0, 0, 4, 4, 4, 1.3, 8, 1.3, 0, 4, 2.7, 2.7, 0, 4, 0, 0, 0, 0],
        8: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2.7, 0, 1.3, 2.7, 0, 5.3, 2.7, 0, 0, 0, 0]}
    for q, (walk, fdw, kind) in PED.items():
        phases[q]["ped_min"] = round(walk + fdw, 1)
        if kind == "recall":
            phases[q]["recall"] = True
        else:
            phases[q]["ped_actuated"] = True

    schedule, unverified_short, bad_days = {}, [], []
    for date, bands in tp["schedule"].items():
        sch = []
        for b in bands:
            if b["kind"] == "plan" and b["plan"] in plans:
                sch.append([b["start"], b["plan"]])
            elif b["kind"] == "free":
                sch.append([b["start"], "FREE"])
            elif b["kind"] == "no data" or (b["kind"] == "plan" and b.get("minutes", 0) < 20):
                unverified_short.append((date, b["start"], b["plan"], b.get("minutes")))   # previous plan continues
            else:
                sch = None
                bad_days.append(date)
                break
        schedule[date] = sch
    # a day whose read failed (a long unverified band) takes the nearest dated day's schedule, not the March canonical
    import datetime as dt
    dated = sorted(d for d, v in schedule.items() if v)
    nearest = {}
    for d in bad_days:
        n = min(dated, key=lambda x: abs((dt.date.fromisoformat(x) - dt.date.fromisoformat(d)).days))
        schedule[d] = schedule[n]
        nearest[d] = n
    # max recall per verified plan: phases the Split Monitor shows gapping out in < 5 % of cycles (not coordinated)
    max_recall = {k: sorted(int(q) for q, t in p["termination"].items()
                            if t.get("gap", 1.0) < 0.05 and int(q) not in (2, 6)) for k, p in plans.items()}

    out = {
        "signal": "137", "tls": "69545429",
        "rings": rings, "phases": phases, "plans": plans,
        "schedule_by_date": schedule, "canonical_schedule": CANONICAL,
        "ped_calls_per_h": {str(k): v for k, v in PED_RATE.items()},
        "notes": {
            "rings": "service order per barrier group (lead first), from clearance.json lead/lag",
            "recall": "P2, P6 on pedestrian recall (a walk in every cycle of all 48 train-day windows); others vehicle-called",
            "ped_min": "walk + flashing don't walk from 48 Timing & Actuation windows on 3 train days (make_signal.py PED); "
                       "P4, P8 only when a pedestrian call is pending (ped_actuated, ped_calls_per_h)",
            "clearance_assumed": assumed,
            "max_green_free": "free mode: largest green any verified plan gives the phase (split - Y - R)",
            "plans": "A-D, every ring check ok (timing_plan_137.md, read 2026-10-02)",
            "schedule": f"dated reads for {sum(v is not None for v in schedule.values())} days (Split Monitor); "
                        f"{len(bad_days)} days with a failed read take the nearest dated day's schedule: {nearest}; 'no data' and unverified bands "
                        f"shorter than 20 min are skipped (previous plan continues): {unverified_short}; FREE = Split Monitor "
                        "'Actuated' band (no programmed splits) -> engine free mode",
            "max_recall": max_recall,
            "offsets": "unknown; modelled isolated, offset 0",
            "wb_left": "P1 (WB left) exists in the plans but its demand is not counted by GDOT (report column WB_L = 0 "
                       "every day; no count in Approach Volume): no WB-left vehicles in the model, so P1 is never called",
        },
    }
    if (HERE / "neighbours.json").exists():          # coordinated with simulated neighbours: absolute offset 0 (attempt 6)
        for p in out["plans"].values():
            p["offset_s"] = 0.0
    if (HERE / "force_off.json").exists():            # floating force-offs measured on train days (attempt 7)
        fl = json.loads((HERE / "force_off.json").read_text())["floating"]
        for p in out["plans"].values():
            p["floating_force_off"] = fl
        out["notes"]["force_off"] = (f"fixed force-offs, except floating (green capped at the split) for P{fl}: "
                                     "force_off_mode.py, Split Monitor p85 split never above the split on train days")
    (HERE / "signal.json").write_text(json.dumps(out, indent=1))
    cal = json.loads((HERE / "sim.json").read_text())
    if cal.get("controller", {}).get("source", "").startswith("fitted on train weekdays"):
        max_recall = cal["controller"]["max_recall"]          # keep the train-day fit (validate.py fit-passage)
    else:
        cal["controller"]["max_recall"] = max_recall
        cal["controller"]["source"] = ("passage times: intersections/137/sim/README.md fit (2026-10-05); max recall per plan "
                                       "from the Split Monitor termination shares (gap-outs < 5 %, make_signal.py)")
        (HERE / "sim.json").write_text(json.dumps(cal, indent=1))
    print(f"wrote signal.json: plans {sorted(plans)}, {sum(v is not None for v in schedule.values())} dated schedules, "
          f"nearest-day fallback {nearest}, short/no-data bands skipped {len(unverified_short)}; max_recall {max_recall}")
    for q, p in phases.items():
        print(f"  P{q}: min {p['min_green']} (n={p['min_green_n']}), Y {p['yellow']}, R {p['red']}, max(free) {p['max_green_free']}")
    print("rings", rings)


if __name__ == "__main__":
    main()
