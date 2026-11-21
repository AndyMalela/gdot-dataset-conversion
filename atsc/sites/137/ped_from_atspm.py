"""Pedestrian call rates for the model from GDOT's Pedestrian Delay report (attempt 15).

    uv run python atsc/sites/137/ped_from_atspm.py      -> signal.json "ped_calls_per_h" (+ notes)

Field: intersections/137/atspm/PedDelay.csv (tools/atspm_charts.py, one window per timing-plan band), train days
only. Per band: cycles with pedestrian requests (CPR) per hour. The model draws Poisson pushes; several pushes in
one cycle give one request, so the push rate that reproduces CPR in a band of cycle C s is
lambda = -(3600 / C) * ln(1 - CPR * C / 3600). Free (no cycle) bands: lambda = CPR. Hourly value = median over
train days of the band covering that hour (a band covering part of the hour counts if it covers >= 30 min).
"""
import csv
import json
import math
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO))


def main():
    from validate import days
    train = {str(d) for d in days("train")}
    sig = json.loads((HERE / "signal.json").read_text())
    plans = sig["plans"]
    sched = sig["schedule_by_date"]
    per_hour = defaultdict(lambda: defaultdict(list))
    used = 0
    for r in csv.DictReader(open(REPO / "intersections/137/atspm/PedDelay.csv")):
        if r["date"] not in train or r["ocr_ok"] != "1" or r["phase"] not in ("4", "8"):
            continue
        t0 = int(r["start"][:2]) * 60 + int(r["start"][3:])
        t1 = t0 + int(r["minutes"])
        cpr_h = float(r["cycles_with_requests"]) / (int(r["minutes"]) / 60)
        band = [n for b0, n in sched.get(r["date"], []) if b0 <= r["start"]]
        plan = band[-1] if band else None
        cyc = plans.get(plan, {}).get("cycle") if plan else None
        if cyc and cpr_h * cyc / 3600 < 0.999:
            lam = -(3600 / cyc) * math.log(1 - cpr_h * cyc / 3600)
        else:
            lam = cpr_h
        for h in range(24):
            if min(t1, (h + 1) * 60) - max(t0, h * 60) >= 30:
                per_hour[r["phase"]][h].append(lam)
        used += 1
    out = {p: [round(st.median(per_hour[p][h]), 2) if per_hour[p][h] else 0.0 for h in range(24)] for p in ("4", "8")}
    print("old:", sig["ped_calls_per_h"])
    print("new:", out, f"({used} band charts)")
    sig["ped_calls_per_h_previous"] = sig["ped_calls_per_h"]
    sig["ped_calls_per_h"] = out
    sig["notes"]["ped_calls_per_h"] = ("2026-11-21 attempt 15 (ped_from_atspm.py): GDOT Pedestrian Delay report, cycles "
                                       "with pedestrian requests per plan band, train days, converted to a Poisson push "
                                       "rate per band cycle; median over train days per hour. Previous rates (48 T&A "
                                       "windows on 3 train days) in ped_calls_per_h_previous")
    (HERE / "signal.json").write_text(json.dumps(sig, indent=1))


if __name__ == "__main__":
    main()
