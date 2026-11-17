"""Approach Volume per 15-min window for any signal, given dates: the upstream-count reconstruction input
(as av_pull_15min.py did for 7065). The locked test set (2026-10-04..22) is refused.

    uv run python tools/lanecheck/av_pull_15min_site.py <signal> <out.csv> <threads> [tmc|adv] <date> [<date> ...]
    (dates YYYY-MM-DD; a range as YYYY-MM-DD..YYYY-MM-DD, weekdays only)

Appends to <out.csv> (existing rows kept, re-requested windows are served from the cache).
"""
import csv
import datetime as dt
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, "tools/lanecheck")
from av_window import fetch  # noqa: E402

sig, out, n = sys.argv[1], Path(sys.argv[2]), int(sys.argv[3])
detection = "tmc"
dates = []
for a in sys.argv[4:]:
    if a in ("tmc", "adv"):
        detection = a
        continue
    if ".." in a:
        d0, d1 = (dt.date.fromisoformat(x) for x in a.split(".."))
        d = d0
        while d <= d1:
            if d.weekday() < 5:
                dates.append(d)
            d += dt.timedelta(1)
    else:
        dates.append(dt.date.fromisoformat(a))
assert not any(dt.date(2026, 10, 4) <= d <= dt.date(2026, 10, 22) for d in dates), "locked test set"
have = set()
rows = []
if out.exists():
    rows = list(csv.reader(open(out)))[1:]
    have = {(r[0], r[1]) for r in rows}
jobs = [dt.datetime.combine(d, dt.time()) + dt.timedelta(minutes=15 * k) for d in dates for k in range(96)
        if (str(d), f"{15 * k // 60:02d}:{15 * k % 60:02d}") not in have]


def one(t):
    try:
        return t, fetch(sig, t, 14, detection=detection)
    except BaseException:
        return t, None


done = failed = 0
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
w = csv.writer(open(out, "w", newline=""))
w.writerow(["date", "time", "NB", "SB", "EB", "WB"])
w.writerows(rows)
print("wrote", out, len(rows), "rows; failed", failed, flush=True)
