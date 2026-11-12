"""Corrected 5-min counts for SIG 7065: Peachtree through (NB_T, SB_T) from the upstream count zones.

    uv run python tools/lanecheck/build_upstream_counts.py
        -> intersections/7065/counts/tmc_7065_5min_upstream.csv   (same columns as tmc_7065_5min.csv)

Rule (agreed 2026-11-12, OPEN_ISSUES.md B2):
  upstream zones in a 15-min window = Approach Volume(direction) - (left + through in the turning-movement report)
  NB_T, SB_T <- that total, split evenly over the window's 5-min bins that have data
               (remainder 1 -> middle bin, remainder 2 -> first and last; with two bins -> first)
  every other column: as reported. `total` is recomputed. Nothing is scaled.
Only days in av_7065_15min.csv are written (usable train + validation weekdays and Saturdays; never the locked
test set). A window the portal has no Approach Volume for keeps status "outage" for its bins.
"""
import csv, datetime as dt
from collections import defaultdict
SRC = "intersections/7065/counts/tmc_7065_5min.csv"
AV = "intersections/7065/counts/av_7065_15min.csv"
OUT = "intersections/7065/counts/tmc_7065_5min_upstream.csv"
MV = ["EB_L", "EB_T", "WB_L", "WB_T", "NB_L", "NB_T", "SB_L", "SB_T"]

def split(n, k):
    base, rem = divmod(n, k)
    out = [base] * k
    order = {3: [1, 0, 2], 2: [0, 1], 1: [0]}[k]
    for i in order[:rem]:
        out[i] += 1
    return out

av = {(r["date"], r["time"]): r for r in csv.DictReader(open(AV))}
dates = sorted({d for d, _ in av})
assert not any("2026-10-04" <= d <= "2026-10-22" for d in dates)
rows = defaultdict(dict)
fields = None
for r in csv.DictReader(open(SRC)):
    fields = fields or list(r)
    if r["date"] in dates:
        rows[r["date"]][r["time"]] = r
out, n_out, n_noav, piedmont_bad = [], 0, 0, 0
tot = defaultdict(int)
for d in dates:
    for k in range(96):
        t = dt.datetime.strptime(d, "%Y-%m-%d") + dt.timedelta(minutes=15 * k)
        tms = [f"{t + dt.timedelta(minutes=5 * j):%H:%M}" for j in range(3)]
        bins = [dict(rows[d][tm]) for tm in tms]
        ok = [b for b in bins if b["status"] == "ok"]
        a = av[(d, tms[0])]
        if ok and a["NB"] == "":                       # counts but no Approach Volume: cannot correct -> outage
            n_noav += len(ok)
            for b in ok:
                b["status"] = "outage"
                for c in MV + ["total"]:
                    b[c] = ""
            ok = []
        if ok:
            for x in ("EB", "WB"):                     # Piedmont must reproduce the report exactly
                piedmont_bad += int(a[x] or 0) != sum(int(b[x + "_L"]) + int(b[x + "_T"]) for b in ok)
            for x in ("NB", "SB"):
                up = int(a[x]) - sum(int(b[x + "_L"]) + int(b[x + "_T"]) for b in ok)
                assert up >= 0, (d, tms[0], x, up)
                tot[x + "_report"] += sum(int(b[x + "_T"]) for b in ok)
                tot[x + "_upstream"] += up
                for b, v in zip(ok, split(up, len(ok))):
                    b[x + "_T"] = v
            for b in ok:
                b["total"] = sum(int(b[c]) for c in MV)
        n_out += sum(b["status"] != "ok" for b in bins)
        out += bins
w = csv.DictWriter(open(OUT, "w", newline=""), fieldnames=fields)
w.writeheader(); w.writerows(out)
print(f"{OUT}: {len(dates)} days, {len(out)} bins, {n_out} outage bins ({n_noav} newly, no Approach Volume)")
print(f"Piedmont windows not matching the report: {piedmont_bad}")
print({k: v for k, v in sorted(tot.items())})
