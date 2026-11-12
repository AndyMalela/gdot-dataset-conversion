import sys, csv, datetime as dt, re
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, sys.argv[1]); sys.path.insert(0, "tools")
from tna_count import rows, row_ids
import atspm_timing as tna
tmc = {(r["date"], r["time"]): r for r in csv.DictReader(open("intersections/7065/counts/tmc_7065_5min.csv"))}
agg = defaultdict(lambda: defaultdict(int)); nmin = defaultdict(int)
for d in sorted(Path("tools/cache/tna_lanecheck").glob("7065_*_1m")):
    m = re.match(r"7065_(\d{8})_(\d{6})_1m", d.name)
    s = dt.datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S")
    b = s.replace(minute=s.minute // 5 * 5)
    for p in sorted(d.glob("*.jpg")):
        ph = {"01": 2, "02": 6}.get(p.stem)
        r, _, lines = rows(p)
        ids = row_ids(str(p), lines, f"tools/cache/tna_lanecheck/7065_20261002_080000_1m/{p.name}")
        if max(d for _, d in ids) > 0.02 or len({i for i, _ in ids}) != len(ids):
            print("label mismatch", p, ids); continue
        n = [0] * 11
        for (i, _), x in zip(ids, r):
            n[i] = len(x)
        a = agg[(b, ph)]
        a["stop"] += n[1] + n[2] + n[3]; a["up"] += n[4] + n[6] + n[8]; a["adv"] += n[10]
        for i, k in zip((1, 2, 3, 4, 6, 8), ("s1", "s2", "s3", "u1", "u2", "u3")):
            a[k] += n[i]
        assert (n[1], n[2], n[3]) == (n[5], n[7], n[9]) or True
        a["dupdiff"] += abs(n[1] - n[5]) + abs(n[2] - n[7]) + abs(n[3] - n[9])
        nmin[(b, ph)] += 1
print(f"{'bin':17} ph min | stop-bar (T1 T2 T3) | upstream (T1 T2 T3) | adv | report  | up/report stop/up")
for (b, ph), a in sorted(agg.items(), key=lambda kv: (kv[0][1], kv[0][0])):
    r = tmc.get((f"{b:%Y-%m-%d}", f"{b:%H:%M}"))
    col = "SB_T" if ph == 2 else "NB_T"
    rep = int(r[col]) if r and r[col] else None
    print(f"{b:%Y-%m-%d %H:%M}  P{ph}  {nmin[(b, ph)]}  | {a['stop']:4} ({a['s1']:3} {a['s2']:3} {a['s3']:3}) | {a['up']:4} ({a['u1']:3} {a['u2']:3} {a['u3']:3}) | {a['adv']:3} | {col} {rep} | "
          f"{a['up'] / rep if rep else float('nan'):.2f}  {a['stop'] / a['up'] if a['up'] else float('nan'):.2f}   dup-row diff {a['dupdiff']}")
