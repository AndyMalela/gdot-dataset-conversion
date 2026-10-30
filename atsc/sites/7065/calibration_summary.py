"""Summarise calibration/grid.csv + quarters.csv against the field (uv run python atsc/sites/7065/calibration_summary.py)."""
import csv
import statistics as st
from collections import defaultdict
from pathlib import Path

D = Path(__file__).resolve().parent / "calibration"
G8 = 55 - 3.6 - 3.0                       # plan C P8 green, s
KEY = ("sigma", "tau", "minGap", "step")
OVERFLOW_S = 100        # P8-through mean delay above ~1.5x the cycle (uniform) delay at x = 1: an overflow queue


def pc(v, p):
    v = sorted(v)
    return round(v[int(p * (len(v) - 1))])


def flagged_days():
    """train days whose PM window holds a physically impossible bin (demand_audit/flagged_bins.csv)."""
    fl = D.parent / "demand_audit" / "flagged_bins.csv"
    return {r["date"] for r in csv.DictReader(open(fl)) if "15:30" <= r["time"] < "19:00"}


def main():
    g = list(csv.DictReader(open(D / "grid.csv")))
    q = list(csv.DictReader(open(D / "quarters.csv")))
    f = list(csv.DictReader(open(D / "field_quarters.csv")))
    fr = [int(r["count"]) / (2 * 5 * G8) * 3600 for r in f]
    print(f"field P8 served per lane of nominal green (plan C quarters, n={len(fr)}): "
          f"p25 {pc(fr, .25)}  median {pc(fr, .5)}  p75 {pc(fr, .75)}  p90 {pc(fr, .9)}")
    k = lambda r: tuple(r.get(x) or "-" for x in KEY)
    gs, qs = defaultdict(list), defaultdict(list)
    for r in g:
        gs[k(r)].append(r)
    for r in q:
        qs[k(r)].append(r)
    bad = flagged_days()
    print("sigma tau minGap step | overflow days (excl. flagged " + ",".join(sorted(d[5:] for d in bad)) + ") | teleports | EB_T delay med/max s | EB_T backlog max | all delay med s | "
          "sim served/lane-nominal-green p25/med/p75/p90 | per lane of actual green med")
    for key, rows in gs.items():
        qq = qs[key]
        sr = [int(r["served"]) / (2 * 5 * G8) * 3600 for r in qq]
        ar = [int(r["served"]) / (2 * float(r["green_s"])) * 3600 for r in qq if float(r["green_s"]) > 0]
        d8 = [float(r["delay_EB_T_s"]) for r in rows]
        da = [float(r["delay_all_s"]) for r in rows]
        over = sum(float(r["delay_EB_T_s"]) > OVERFLOW_S for r in rows if r["date"] not in bad)
        print(" ".join(key), "|", over, "|", sum(int(r["teleports"]) for r in rows), "|", round(st.median(d8)), round(max(d8)), "|",
              max(int(r["backlog_EB_T"]) for r in rows), "|", round(st.median(da)), "|",
              pc(sr, .25), pc(sr, .5), pc(sr, .75), pc(sr, .9), "|", pc(ar, .5))


if __name__ == "__main__":
    main()
