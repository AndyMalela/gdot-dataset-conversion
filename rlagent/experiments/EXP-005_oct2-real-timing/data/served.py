"""Served vs counted volume per movement in the peak (15:00-18:00).
counted = vehicles the demand file sends in the window (= measured counts);
served  = vehicles of that movement that completed their trip (arrived) inside the window.
Usage: python3 served.py ti_a.xml [ti_b.xml ...]"""
import sys
import xml.etree.ElementTree as ET
from collections import Counter
import os
HERE = os.path.dirname(os.path.abspath(__file__))
ROU = os.path.join(HERE, "..", "..", "..", "..", "intersections", "7065", "sim", "demand.rou.xml")
B, E = 54000, 64800
mv = lambda vid: "_".join(vid.split("_")[:2])


def counted(rou=ROU):
    c = Counter()
    for f in ET.parse(rou).getroot().iter("flow"):
        if B <= float(f.get("begin")) < E:
            c[mv(f.get("id"))] += int(f.get("number"))
    return c


def served(ti):
    c = Counter()
    for t in ET.parse(ti).getroot().iter("tripinfo"):
        if B <= float(t.get("arrival")) < E:
            c[mv(t.get("id"))] += 1
    return c


if __name__ == "__main__":
    dem = counted()
    hrs = (E - B) / 3600
    print(f"{'movement':8s} {'counted veh/h':>14s}" + "".join(f"{os.path.basename(p)[3:-4]:>16s}" for p in sys.argv[1:]))
    res = [served(p) for p in sys.argv[1:]]
    for k in sorted(dem):
        print(f"{k:8s} {dem[k] / hrs:14.0f}" + "".join(f"{r[k] / hrs:9.0f} ({100 * r[k] / dem[k]:3.0f}%)" for r in res))
