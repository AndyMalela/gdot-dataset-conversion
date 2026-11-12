"""Checks on the 15-min Approach Volume pull (validation weekdays; add "all" for train days and Saturdays), read from the cache:
1. Piedmont: AV == report (left + through) per window  -> the window method is exact
2. Peachtree: upstream zones = AV - report (left + through); negatives, outages, size against the report
Prints a summary; changes nothing."""
import sys, csv, datetime as dt, statistics as st
from collections import defaultdict
sys.path.insert(0, "tools/lanecheck")
from av_window import CACHE, totals
import gzip
tmc = {(r["date"], r["time"]): r for r in csv.DictReader(open("intersections/7065/counts/tmc_7065_5min.csv"))}
days = [r["date"] for r in csv.DictReader(open("atsc/sites/7065/demand_audit/days.csv"))
        if r["set"] in (("train", "validation") if "all" in sys.argv else ("validation",))
        and r["day_type"] in (("weekday", "saturday") if "all" in sys.argv else ("weekday",))
        and r["quality"] in ("complete", "usable")]
MV = ["EB_L", "EB_T", "WB_L", "WB_T", "NB_L", "NB_T", "SB_L", "SB_T"]
pied_n = pied_bad = 0; pied_diffs = []
neg = []; outage_w = 0; missing = 0
day_tot = defaultdict(lambda: defaultdict(int)); hour = defaultdict(lambda: defaultdict(list)); peak15 = defaultdict(list)
for d in days:
    for k in range(96):
        t = dt.datetime.strptime(d, "%Y-%m-%d") + dt.timedelta(minutes=15 * k)
        f = CACHE / f"7065_{t:%Y%m%d_%H%M}_14m_b15.html.gz"
        if not f.exists():
            missing += 1; continue
        av = totals(gzip.open(f, "rt").read())
        rs = [tmc.get((d, f"{t + dt.timedelta(minutes=5 * j):%H:%M}")) for j in range(3)]
        if any(r is None or r["status"] != "ok" for r in rs):
            outage_w += 1; continue
        s = {m: sum(int(r[m]) for r in rs) for m in MV}
        for a in ("EB", "WB"):
            pied_n += 1; df = av.get(a, 0) - s[a + "_L"] - s[a + "_T"]
            if df: pied_bad += 1; pied_diffs.append((d, f"{t:%H:%M}", a, df))
        for a in ("NB", "SB"):
            up = av.get(a, 0) - s[a + "_L"] - s[a + "_T"]
            if up < 0: neg.append((d, f"{t:%H:%M}", a, up))
            day_tot[d][a + "_up"] += up; day_tot[d][a + "_rep"] += s[a + "_T"]
            hour[a][t.hour].append((up, s[a + "_T"])); peak15[a].append((up, d, f"{t:%H:%M}"))
print(f"windows missing {missing}, skipped for outage/absent bins {outage_w}")
print(f"1. Piedmont AV == report: {pied_n - pied_bad}/{pied_n} windows exact; mismatches: {pied_diffs[:10]}")
print(f"2. Peachtree negative upstream windows: {len(neg)} {neg[:10]}")
print("   daily through, upstream zones vs report (veh/day):")
for a, nm in (("SB", "from NE (P2)"), ("NB", "from SW (P6)")):
    u = [day_tot[d][a + "_up"] for d in days]; r = [day_tot[d][a + "_rep"] for d in days]
    print(f"   {nm}: upstream median {st.median(u):.0f} (min {min(u)}, max {max(u)}); report median {st.median(r):.0f}; ratio median {st.median([x / y for x, y in zip(u, r)]):.2f}")
print("   by hour, median over days of 15-min sums x4 (veh/h): hour | NE up, rep | SW up, rep")
for h in range(24):
    row = []
    for a in ("SB", "NB"):
        byday = defaultdict(lambda: [0, 0])
        v = hour[a][h]
        up = st.mean(x for x, _ in v) * 4; rp = st.mean(y for _, y in v) * 4
        row += [up, rp]
    print(f"   {h:02d} | {row[0]:5.0f} {row[1]:5.0f} | {row[2]:5.0f} {row[3]:5.0f}")
for a in ("SB", "NB"):
    top = sorted(peak15[a], reverse=True)[:5]
    print(f"   largest 15-min upstream totals {a}: {top}  (3 lanes; 15 min of permanent green at 1,900/lane = 1,425)")
