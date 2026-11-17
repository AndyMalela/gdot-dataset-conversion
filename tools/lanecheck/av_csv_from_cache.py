"""Rebuild the 15-min Approach Volume csv of a signal from the cached window downloads (tools/cache/av_window),
complete days only (96 windows). Use after parallel pulls, so no pull's rows are lost.

    uv run python tools/lanecheck/av_csv_from_cache.py <signal> <tmc|adv> <out.csv>
"""
import csv
import gzip
import re
import sys
from pathlib import Path

sys.path.insert(0, "tools/lanecheck")
from av_window import totals  # noqa: E402

sig, det, out = sys.argv[1], sys.argv[2], sys.argv[3]
suffix = "" if det == "tmc" else f"_{det}"
rows = []
for f in sorted(Path("tools/cache/av_window").glob(f"{sig}_*_14m_b15{suffix}.html.gz")):
    m = re.match(rf"{sig}_(\d{{4}})(\d{{2}})(\d{{2}})_(\d{{2}})(\d{{2}})_14m_b15{suffix}\.html\.gz$", f.name)
    if not m:
        continue
    av = totals(gzip.open(f, "rt").read())
    rows.append([f"{m[1]}-{m[2]}-{m[3]}", f"{m[4]}:{m[5]}"] + [av.get(d, "") for d in ("NB", "SB", "EB", "WB")])
n = {}
for r in rows:
    n[r[0]] = n.get(r[0], 0) + 1
full = {d for d, k in n.items() if k == 96}
rows = [r for r in rows if r[0] in full]
w = csv.writer(open(out, "w", newline=""))
w.writerow(["date", "time", "NB", "SB", "EB", "WB"])
w.writerows(rows)
print(f"{out}: {len(full)} complete days, {len(rows)} rows; partial days left out: {sorted(set(n) - full)}")
