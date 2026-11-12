"""Approach Volume (lane-by-lane detection) per 15-min window for SIG 7065, train + validation days only.

The window [t, t + 14 min] reproduces the turning-movement report's three 5-min bins exactly on Piedmont
(checked 2026-11-12), so on Peachtree  AV - (left + through in the report) = the upstream count zones.
The locked test set (2026-10-04..22) is never requested. Output: one row per day and 15-min window.

    uv run python tools/lanecheck/av_pull_15min.py [threads]
"""
import sys, csv, datetime as dt
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "tools/lanecheck")
from av_window import fetch
OUT = "intersections/7065/counts/av_7065_15min.csv"
days = [r for r in csv.DictReader(open("atsc/sites/7065/demand_audit/days.csv"))
        if r["set"] in ("train", "validation") and r["quality"] in ("complete", "usable")
        and r["day_type"] in ("weekday", "saturday")]
assert not any("2026-10-04" <= r["date"] <= "2026-10-22" for r in days)
# validation weekdays first (needed first), then train weekdays, then Saturdays
days.sort(key=lambda r: (r["day_type"] != "weekday", r["set"] != "validation", r["date"]))
jobs = [dt.datetime.strptime(r["date"], "%Y-%m-%d") + dt.timedelta(minutes=15 * k) for r in days for k in range(96)]
def one(t):
    try:
        return t, fetch("7065", t, 14)
    except BaseException as e:
        return t, None
n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
done, failed, rows = 0, 0, []
with ThreadPoolExecutor(n) as ex:
    for t, av in ex.map(one, jobs):
        done += 1
        if av is None:
            failed += 1
        else:
            rows.append([f"{t:%Y-%m-%d}", f"{t:%H:%M}"] + [av.get(d, "") for d in ("NB", "SB", "EB", "WB")])
        if done % 96 == 0:
            print(f"{t:%Y-%m-%d} done ({done}/{len(jobs)}, failed {failed})", flush=True)
rows.sort()
# blank = the portal has no data for that direction in the window (detector outage)
w = csv.writer(open(OUT, "w", newline="")); w.writerow(["date", "time", "NB", "SB", "EB", "WB"]); w.writerows(rows)
print("wrote", OUT, len(rows), "rows; failed", failed)
