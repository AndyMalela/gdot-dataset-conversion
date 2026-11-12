import sys, csv, datetime as dt
sys.path.insert(0, sys.argv[1])
from tna_fetch import fetch
from tna_count import rows, row_ids
tmc = {(r["date"], r["time"]): r for r in csv.DictReader(open("intersections/7065/counts/tmc_7065_5min.csv"))}
wins = sys.argv[2:]
print("bin               ph | stop-bar rows (T1 T2 T3) sum | same channels drawn as count rows | report")
for w in wins:
    s = dt.datetime.strptime(w, "%Y-%m-%dT%H:%M")
    d = fetch("7065", s, 5)
    for p, ph, col in ((d / "01.jpg", 2, "SB_T"), (d / "02.jpg", 6, "NB_T")):
        r, _, lines = rows(p)
        ids = row_ids(str(p), lines, f"tools/cache/tna_lanecheck/7065_20261002_080000_1m/{p.name}")
        n = {i: len(x) for (i, dd), x in zip(ids, r) if dd < 0.008}
        if len(n) != len(r):
            print("  label problem", p, ids)
        a = [n.get(i, 0) for i in (1, 2, 3)]; b = [n.get(i, 0) for i in (5, 7, 9)]
        rep = tmc[(f"{s:%Y-%m-%d}", f"{s:%H:%M}")][col]
        print(f"{s:%Y-%m-%d %H:%M}  P{ph} | {a} {sum(a):3} | {b} {sum(b):3} | {col} {rep}")
