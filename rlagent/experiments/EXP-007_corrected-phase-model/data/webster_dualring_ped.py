"""Webster dual ring + pedestrian minimum greens (EXP-007).

Same as webster_dualring.py, but each through phase's green is at least Walk + Flashing Don't Walk of
its parallel crosswalk, every cycle (Timing & Actuation, Oct 2 16:00: a walk ran every cycle on all
four):  FDW P2 22.0 s, P4 29.9 s, P6 25.2 s, P8 30.5 s (data-timing/7065, overlaps 2/4/6/8);
Walk = 7 s (MUTCD minimum; GDOT's shortest observed walk was 5.3-6.5 s when a ped arrived late).
Each barrier group lasts as long as its longer ring; the other ring's phases share the slack by y.
"""
import json
import os
import subprocess
import webster_dualring as W

WALK = 7.0
FDW = {2: 22.0, 4: 29.9, 6: 25.2, 8: 30.5}
PEDMIN = {p: WALK + f for p, f in FDW.items()}

d, splits, yel, red, info = W.plan()
y = info["y"]
lost = {p: yel[p] + red[p] for p in W.PH}
green = {p: max(splits[p] - lost[p], PEDMIN.get(p, 0)) for p in W.PH}
for g in W.GROUPS:
    T = max(sum(green[p] + lost[p] for p in ps) for ps in g.values())
    for ps in g.values():
        slack = T - sum(green[p] + lost[p] for p in ps)
        ys = sum(y[p] for p in ps)
        for p in ps:
            green[p] += slack * y[p] / ys
sp = {p: green[p] + lost[p] for p in W.PH}
add = os.path.join(W.HERE, "webster_dualring_ped.add.xml")
cycle, prog = W.write_add(d, sp, yel, red, add)
info.update({"ped_min_green_s": PEDMIN, "greens_s": {p: round(g, 1) for p, g in sorted(green.items())},
             "splits_s": {p: round(s, 1) for p, s in sorted(sp.items())}, "cycle_s": round(cycle, 1),
             "cycle_program_s": sum(x[0] for x in prog)})
print(json.dumps({k: info[k] for k in ("greens_s", "cycle_s")}), flush=True)
ti = os.path.join(W.HERE, "ti_webster_dr_ped.xml")
subprocess.run(["sumo", "--net-file", W.X.NET, "--route-files", W.X.ROU[W.X.TEST], "--additional-files", add,
                "--begin", "0", "--end", str(W.R.END), "--time-to-teleport", "300", "--seed", str(W.R.SEED),
                "--no-step-log", "--duration-log.disable", "--tripinfo-output", ti,
                "--statistic-output", ti.replace(".xml", "_stats.xml")], check=True, capture_output=True)
res = W.X.summarise(ti, W.X.ROU[W.X.TEST], False)
res["cycle_s"] = info["cycle_program_s"]
print(W.X.line("Webster dual ring + ped min", res), flush=True)
json.dump({"plan": info, "test": res}, open(os.path.join(W.HERE, "results_webster_dr_ped.json"), "w"), indent=1)
