"""Demand for EXP-007 on the extended twin (sumotwin/7065_ext.net.xml).

Same rules as intersections/7065/sim (tools/build_sim.py): corrected GDOT count labels,
Poisson arrivals with the exact count per movement per 5-min bin (seed 12345), trips start
on the upstream edges. One file per day: train 2026-09-29, validate 2026-09-30, test 2026-10-02.
"""
import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import build_sim as B  # noqa: E402

DAYS = ["2026-09-29", "2026-09-30", "2026-10-02"]

d = B.load("7065")
net = B.sumolib.net.readNet(str(d["net_path"]))
print("net:", d["net_path"])
for day in DAYS:
    with tempfile.TemporaryDirectory() as tmp:
        B.build_demand("7065", d, day, net, Path(tmp), "poisson")
        shutil.copy(os.path.join(tmp, "demand.rou.xml"), os.path.join(HERE, "demand", f"{day}.rou.xml"))
    print(day, "written")
