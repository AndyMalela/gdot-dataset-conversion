"""Write atsc/sites/7065/signal.json: everything the NEMA engine needs for SIG 7065, with sources.

    uv run python atsc/sites/7065/make_signal.py

Sources (all GDOT ATSPM, read by tools/atspm_plans.py and tools/atspm_timing.py):
  rings / lead-lag / clearances   intersections/7065/timing/clearance.json
  plans + schedule                intersections/7065/timing/timing_plan_7065.json (verified plans only)
  min greens                      intersections/7065/timing/greens_7065.csv ('min green complete' blocks, median)
  ped walk / flashing don't walk  Oct 2 16:00 Timing & Actuation charts (as used in EXP-008/009)
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
T = HERE.parents[2] / "intersections/7065/timing"

WALK = 7.0
FDW = {2: 22.0, 4: 29.9, 6: 25.2, 8: 30.5}
CANONICAL = {   # the schedule read on most days (39 of 64 weekdays, 11 of 12 Saturdays)
    "weekday": [["00:00", "E"], ["06:15", "A"], ["13:30", "B"], ["15:30", "C"], ["19:00", "B"], ["19:30", "D"], ["21:45", "E"]],
    "saturday": [["00:00", "E"], ["08:15", "G"], ["11:30", "F"], ["18:30", "G"], ["20:45", "H"]],
}


def main():
    clr = json.loads((T / "clearance.json").read_text())
    tp = json.loads((T / "timing_plan_7065.json").read_text())
    y = {int(k): float(v) for k, v in clr["yellow"].items()}
    r = {int(k): float(v) for k, v in clr["red_clear"].items()}
    lead = {k: int(v) for k, v in clr["lead"].items()}

    def order(a, b):
        return [a, b] if lead[f"{min(a, b)}/{max(a, b)}"] == a else [b, a]
    rings = {"1": [order(1, 2), order(3, 4)], "2": [order(5, 6), order(7, 8)]}

    mins = defaultdict(list)
    for row in csv.DictReader(open(T / "greens_7065.csv")):
        if row["chart"].startswith("Phase_") and row["min_green_s"]:
            mins[int(row["chart"].split("_")[1].rstrip("b"))].append(float(row["min_green_s"]))
    med = lambda v: sorted(v)[len(v) // 2]

    verified = {k: p for k, p in tp["plans"].items() if p.get("checks") == ["ok"] and p.get("cycle_s")}
    plans = {k: {"cycle": p["cycle_s"], "splits": {int(q): s for q, s in p["splits_s"].items()},
                 "coordinated": [2, 6], "termination": p.get("termination", {})}
             for k, p in verified.items()}
    max_green = {q: max(pl["splits"][q] - y[q] - r[q] for pl in plans.values() if pl["splits"].get(q, 0) > 0)
                 for q in range(1, 9)}

    # GDOT's controller won't run a split shorter than the phase's walk + FDW, so the programmed greens
    # bound the true pedestrian time; the chart-read FDW (+-0.5 s) exceeds them by 0.1-0.5 s in plans B/C/D
    min_prog = {q: min(pl["splits"][q] - y[q] - r[q] for pl in plans.values() if pl["splits"].get(q, 0) > 0)
                for q in range(1, 9)}
    phases, capped = {}, {}
    for q in range(1, 9):
        ped = WALK + FDW[q] if q in FDW else 0.0
        if ped > min_prog[q]:
            capped[q] = (ped, round(min_prog[q], 1))
            ped = round(min_prog[q], 1)
        phases[q] = {"min_green": med(mins[q]), "min_green_n": len(mins[q]), "yellow": y[q], "red": r[q],
                     "ped_min": ped, "recall": q in FDW, "max_green_free": round(max_green[q], 1)}

    schedule, notes = {}, []
    for date, bands in tp["schedule"].items():
        used = [b for b in bands if b["kind"] == "plan"]
        if used and all(b["plan"] in plans for b in used):
            schedule[date] = [[b["start"], b["plan"]] for b in used]
        else:
            schedule[date] = None
            notes.append(date)

    out = {
        "signal": "7065", "tls": "cluster_69536528_69537103",
        "rings": rings, "phases": phases, "plans": plans,
        "schedule_by_date": schedule, "canonical_schedule": CANONICAL,
        "notes": {
            "rings": "service order per barrier group (lead first), from clearance.json lead/lag",
            "recall": "through phases 2/4/6/8 on pedestrian recall: a walk is served every cycle at every hour "
                      "checked (tod_7065.csv walks per 15-min window = cycles per window, 01:00-23:00)",
            "ped_min": f"walk {WALK} s + flashing don't walk per crosswalk (Oct 2 16:00 T&A charts)",
            "ped_min_capped": {str(q): f"measured {a:.1f} s > shortest programmed green {b} s; capped "
                               "(within chart-read error)" for q, (a, b) in capped.items()},
            "max_green_free": "free mode only: largest green any verified plan gives the phase (split - Y - R)",
            "plans": "verified reads A-H only (I-U are failed reads, flagged by the ring check)",
            "schedule": "per date when every band is a verified plan, else null -> use canonical_schedule "
                        f"for the day type ({len(notes)} dates)",
            "offsets": "unknown; isolated intersection, so offset 0 (relative timing within the cycle is exact)",
        },
    }
    (HERE / "signal.json").write_text(json.dumps(out, indent=1))
    print(f"wrote signal.json: plans {sorted(plans)}, {sum(v is not None for v in schedule.values())} dated schedules, "
          f"{len(notes)} -> canonical")
    for q, p in phases.items():
        print(f"  P{q}: min {p['min_green']} (n={p['min_green_n']}), Y {p['yellow']}, R {p['red']}, "
              f"ped {p['ped_min']}, max(free) {p['max_green_free']}, rings {rings}" if q == 1 else
              f"  P{q}: min {p['min_green']} (n={p['min_green_n']}), Y {p['yellow']}, R {p['red']}, "
              f"ped {p['ped_min']}, max(free) {p['max_green_free']}")


if __name__ == "__main__":
    main()
