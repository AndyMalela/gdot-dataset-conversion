"""Piedmont through phases (P4 = report WB_T, P8 = report EB_T): per 5-min bin, stop-bar presence vs count zones vs report.
Rows in the reference chart (2026-10-02 08:00): 0 VSD; 1-2 stop-bar T1,T2; 3 stop-bar R3; 4-5 count T1,T2; 6 Advance."""
import sys, csv, datetime as dt, re
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from tna_count import rows, row_ids
tmc = {(r["date"], r["time"]): r for r in csv.DictReader(open("intersections/7065/counts/tmc_7065_5min.csv"))}
agg = defaultdict(lambda: defaultdict(int)); nmin = defaultdict(int)
for d in sorted(Path("tools/cache/tna_lanecheck").glob("7065_*_1m_p48")):
    m = re.match(r"7065_(\d{8})_(\d{6})_1m", d.name)
    s = dt.datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S")
    b = s.replace(minute=s.minute // 5 * 5)
    for p in sorted(d.glob("*.jpg")):
        ph = {"01": 4, "02": 8}[p.stem]
        r, _, lines = rows(p)
        ids = row_ids(str(p), lines, f"tools/cache/tna_lanecheck/7065_20261002_080000_1m_p48/{p.name}")
        if max(x for _, x in ids) > 0.02 or len({i for i, _ in ids}) != len(ids):
            print("label mismatch", p, ids); continue
        n = [0] * 7
        for (i, _), x in zip(ids, r):
            n[i] = len(x)
        a = agg[(b, ph)]
        for i, k in enumerate(("vsd", "s1", "s2", "r3", "c1", "c2", "adv")):
            a[k] += n[i]
        nmin[(b, ph)] += 1
print(f"{'bin':16} ph min | stop-bar T1 T2 (R3) | count T1 T2 = sum | adv | report | count/report")
for (b, ph), a in sorted(agg.items(), key=lambda kv: (kv[0][1], kv[0][0])):
    r = tmc.get((f"{b:%Y-%m-%d}", f"{b:%H:%M}"))
    col = "EB_T" if ph == 8 else "WB_T"
    rep = int(r[col]) if r and r[col] else None
    c = a["c1"] + a["c2"]
    print(f"{b:%Y-%m-%d %H:%M} P{ph} {nmin[(b, ph)]} | {a['s1']:3} {a['s2']:3} ({a['r3']:3}) | {a['c1']:3} {a['c2']:3} = {c:3} | {a['adv']:3} | {col} {rep} | "
          f"{c / rep if rep else float('nan'):.2f}")
