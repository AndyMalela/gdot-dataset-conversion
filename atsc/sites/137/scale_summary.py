"""Demand-scale sweep summary for 137: one table across eval/ (x1) and eval_x<k>/ folders.

    uv run python atsc/sites/137/scale_summary.py            -> eval/scale_summary.md

Per controller and scale: vehicle-weighted mean delay over the days run at that scale (same days for every
controller at a scale, else the cell is marked), total teleports, share of hours with a backlog >= 10 vehicles
at the leg end (queue reaching the modelled entry). The scaled runs multiply every 5-min count of the real days
by k (atsc/sim/demand.py ATSC_DEMAND_SCALE): a sensitivity experiment on the real profile, not real traffic.
"""
import csv
import re
import statistics as st
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPILL = 10
folders = {1.0: HERE / "eval"}
for f in HERE.glob("eval_x*"):
    folders[float(f.name[6:])] = f
scales = sorted(folders)
delay, tele, spill, days = {}, {}, {}, {}
for k in scales:
    fr, fh = folders[k] / "runs.csv", folders[k] / "hour_mv.csv"
    if not fr.exists():
        continue
    per = defaultdict(lambda: [0.0, 0, 0, set()])
    for r in csv.DictReader(open(fr)):
        if r["delay_all_s"] == "":
            continue
        a = per[r["controller"]]
        a[0] += float(r["delay_all_s"]) * int(r["vehicles"])
        a[1] += int(r["vehicles"])
        a[2] += int(r["teleports"])
        a[3].add(r["date"])
    hours = defaultdict(lambda: [0, 0])
    if fh.exists():
        seen = defaultdict(dict)
        for r in csv.DictReader(open(fh)):
            key = (r["date"], r["hour"])
            seen[r["controller"]][key] = max(seen[r["controller"]].get(key, 0), int(r["backlog_max"]))
        for c, hs in seen.items():
            hours[c] = [sum(v >= SPILL for v in hs.values()), len(hs)]
    for c, (s, n, t, ds) in per.items():
        delay[(c, k)] = s / n if n else None
        tele[(c, k)] = t
        spill[(c, k)] = hours[c]
        days[(c, k)] = len(ds)
ctrls = sorted({c for c, _ in delay}, key=lambda c: (not c.startswith(("gdot", "actuated", "webster", "maxpressure")), c))
L = ["# Demand-scale sweep (137, preliminary subset of validation days, simulation seed 1)", "",
     "Every 5-min count of the real day multiplied by k (labelled sensitivity experiment, not real traffic). Cell: "
     "vehicle-weighted mean delay s/veh (days run) · teleports · hours with a queue reaching the leg end / hours. "
     "Controllers trained at x1 only.", "",
     "| Controller | " + " | ".join(f"x{k:g}" for k in scales) + " |", "|---|" + "---|" * len(scales)]
for c in ctrls:
    cells = []
    for k in scales:
        if (c, k) not in delay or delay[(c, k)] is None:
            cells.append("-")
        else:
            h = spill[(c, k)]
            cells.append(f"{delay[(c, k)]:.1f} ({days[(c, k)]}d) · {tele[(c, k)]} tp · {h[0]}/{h[1]} h")
    L.append(f"| {c} | " + " | ".join(cells) + " |")
(HERE / "eval" / "scale_summary.md").write_text("\n".join(L) + "\n")
print("\n".join(L))
