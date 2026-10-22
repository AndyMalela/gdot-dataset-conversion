"""Real GDOT timing as fixed time with GDOT's exact phase order (P1 lagging P2), EXP-007.

tools/build_sim.py --controller fixed logic: each plan's programmed splits, measured yellow/red,
corrected lead/lag (P2 -> P1, P5 -> P6, P3 -> P4, P7 -> P8), Oct 2 time-of-day schedule (WAUT).
No actuation: every phase runs its full split (the PM Timing & Actuation record shows nearly every
phase at its split; minor-phase gap-outs only move slack within a ring). Complements the actuated
NEMA run, where SUMO forces P1 to lead.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "EXP-005_oct2-real-timing", "data")))
import run_exp007 as X  # noqa: E402
import json  # noqa: E402
B = X.V5.B if hasattr(X, "V5") else None
import run_exp005_v5 as V5  # noqa: E402
B = V5.B

d = B.load("7065")
net = B.sumolib.net.readNet(str(d["net_path"]))
add = os.path.join(HERE, "real_fixed_lag.add.xml")
with tempfile.TemporaryDirectory() as tmp:
    B.build_signal("7065", d, net, X.TEST, Path(tmp), controller="fixed")
    s = open(os.path.join(tmp, "signal.add.xml")).read()
import re  # noqa: E402
s = re.sub(r'\s*<timedEvent type="SaveTLSStates"[^>]*/>', "", s)
open(add, "w").write(s)
ti = os.path.join(HERE, "ti_real_fixed_lag.xml")
subprocess.run(["sumo", "--net-file", X.NET, "--route-files", X.ROU[X.TEST], "--additional-files", add,
                "--begin", "0", "--end", str(X.R.END), "--time-to-teleport", "300", "--seed", str(X.R.SEED),
                "--no-step-log", "--duration-log.disable", "--tripinfo-output", ti,
                "--statistic-output", ti.replace(".xml", "_stats.xml")], check=True, capture_output=True)
res = X.summarise(ti, X.ROU[X.TEST], False)
print(X.line("Real timing fixed, exact order", res), flush=True)
json.dump({"test": res}, open(os.path.join(HERE, "results_real_fixed_lag.json"), "w"), indent=1)
