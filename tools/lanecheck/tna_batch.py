import sys, datetime as dt
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, sys.argv[1])
from tna_fetch import fetch
wins = [("2026-10-02", "08:00", 5), ("2026-09-16", "02:00", 10), ("2026-09-16", "08:00", 5), ("2026-09-16", "12:00", 5),
        ("2026-09-16", "17:30", 5), ("2026-09-16", "21:00", 5)]
jobs = []
for d, t, n in wins:
    s = dt.datetime.strptime(f"{d} {t}", "%Y-%m-%d %H:%M")
    jobs += [s + dt.timedelta(minutes=k) for k in range(n)]
def one(s):
    try:
        d = fetch("7065", s, 1)
        return f"{s} {len(list(d.glob('*.jpg')))}"
    except BaseException as e:
        return f"{s} FAILED {e}"
with ThreadPoolExecutor(2) as ex:
    for r in ex.map(one, jobs):
        print(r, flush=True)
print("done")
