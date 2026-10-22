"""Webster fixed-time on GDOT's own phase structure (8-phase dual ring), for EXP-007.

Same phases, same movements per phase (intersections/7065/timing/phase_map.json), same sequence
(Ring 1: P2 -> P1 | P3 -> P4, Ring 2: P5 -> P6 | P7 -> P8; clearance.json, lead/lag corrected
2026-10-05) and same measured yellow / red clearance per phase as GDOT's controller. Only the cycle
and splits come from Webster, designed on 2026-09-29 (busiest rolling hour per movement in
15:00-18:00, the same volumes as the 4-stage Webster). One plan all day, tested on 2026-10-02.

Webster on a dual ring: y_p = v / (1800 veh/h/lane x lanes) for each phase's movement; in each barrier
group the critical ring is the one with the larger sum of y; lost time per phase = yellow + red
(2 s start-up loss and 2 s of yellow used cancel); C = (1.5 L + 5) / (1 - Y), L and Y summed over the
critical path; group green split by critical y; within each ring, phases share the group time by y.
Displayed green >= GDOT's measured minimum green. No pedestrian minimums -- NOT a like-for-like comparator:
GDOT's real splits already contain the pedestrian-timed greens; use webster_dualring_ped.py for comparison.

  python3 webster_dualring.py      -> webster_dualring.add.xml, ti_webster_dr.xml, results_webster_dr.json
"""
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
E5 = os.path.abspath(os.path.join(HERE, "..", "..", "EXP-005_oct2-real-timing", "data"))
sys.path.insert(0, E5)
import run_exp005 as R  # noqa: E402
import run_exp005_v5 as V5  # noqa: E402  (peak_hour_volumes with corrected labels; imports build_sim as B)
import run_exp007 as X  # noqa: E402
B = V5.B

SAT = 1800.0
# phase -> (twin approach key, movement, lanes) from phase_map.json + the twin's lane table
PH = {1: ("eb", "left", 2), 2: ("wb", "thru", 3), 3: ("sb", "left", 1), 4: ("nb", "thru", 2),
      5: ("wb", "left", 2), 6: ("eb", "thru", 3), 7: ("nb", "left", 1), 8: ("sb", "thru", 2)}
GROUPS = ({1: (2, 1), 2: (5, 6)}, {1: (3, 4), 2: (7, 8)})      # barrier group -> ring -> phases in order


def plan():
    d = B.load("7065")
    c = d["clearance"]
    yel = {int(k): float(v) for k, v in c["yellow"].items()}
    red = {int(k): float(v) for k, v in c["red_clear"].items()}
    mins = B.actuation_params(d, X.TEST)["min_green"]
    vol = V5.peak_hour_volumes(X.TRAIN, R.PEAK_BEGIN, R.PEAK_END)
    y = {p: vol[(a, m)] / (SAT * n) for p, (a, m, n) in PH.items()}
    lost = {p: yel[p] + red[p] for p in PH}
    crit = []
    for g in GROUPS:
        r = max(g, key=lambda k: sum(y[p] for p in g[k]))
        crit.append((sum(y[p] for p in g[r]), sum(lost[p] for p in g[r])))
    Y, L = sum(c_[0] for c_ in crit), sum(c_[1] for c_ in crit)
    C = min(max((1.5 * L + 5) / (1 - Y), 40.0), 180.0)
    splits = {}
    for g, (yc, _) in zip(GROUPS, crit):
        T = (C - L) * yc / Y + sum(lost[p] for p in g[max(g, key=lambda k: sum(y[q] for q in g[k]))])
        for ring, ps in g.items():
            free = T - sum(lost[p] for p in ps)
            ys = sum(y[p] for p in ps)
            for p in ps:
                splits[p] = lost[p] + max(mins.get(p, 5.0), free * y[p] / ys)
    # a minimum-green bump can make one ring longer than the other: the group runs to the longer ring
    info = {"designed_on": X.TRAIN, "Y": round(Y, 3), "L_s": round(L, 1), "cycle_formula_s": round(C, 1),
            "y": {p: round(v, 3) for p, v in y.items()},
            "volumes_veh_h": {p: vol[(PH[p][0], PH[p][1])] for p in PH},
            "splits_s": {p: round(s, 1) for p, s in sorted(splits.items())},
            "greens_s": {p: round(splits[p] - lost[p], 1) for p in sorted(splits)}}
    return d, splits, yel, red, info


def write_add(d, splits, yel, red, path):
    net = B.sumolib.net.readNet(str(d["net_path"]))
    tlid, links = B.link_table("7065", d, net)
    lp = B.link_phases(links, d["phase_map"])
    lead = {k: int(v) for k, v in d["clearance"]["lead"].items()}
    tl, cycle = B.ring_timeline(splits, yel, red, lead)
    phases = B.program_states(tl, cycle, lp, max(links) + 1)
    # whole-second boundaries (SUMO runs 1 s steps), keeping the cycle length exact
    out, t, prev = [], 0.0, 0
    for dur, st in phases:
        t += dur
        b = int(round(t))
        if b > prev:
            out.append((b - prev, st))
            prev = b
    L = ["<additional>", f'  <tlLogic id="{tlid}" type="static" programID="webster_dr" offset="0">'
         f'  <!-- cycle {cycle:.1f} s -->']
    L += [f'    <phase duration="{dur}" state="{st}"/>' for dur, st in out]
    L += ["  </tlLogic>", "</additional>"]
    Path(path).write_text("\n".join(L) + "\n")
    return cycle, out


def main():
    d, splits, yel, red, info = plan()
    add = os.path.join(HERE, "webster_dualring.add.xml")
    cycle, prog = write_add(d, splits, yel, red, add)
    info["cycle_s"] = round(cycle, 1)
    info["cycle_program_s"] = sum(p[0] for p in prog)
    print(json.dumps(info, indent=1), flush=True)
    ti = os.path.join(HERE, "ti_webster_dr.xml")
    subprocess.run(["sumo", "--net-file", X.NET, "--route-files", X.ROU[X.TEST], "--additional-files", add,
                    "--begin", "0", "--end", str(R.END), "--time-to-teleport", "300", "--seed", str(R.SEED),
                    "--no-step-log", "--duration-log.disable", "--tripinfo-output", ti,
                    "--statistic-output", ti.replace(".xml", "_stats.xml")], check=True, capture_output=True)
    X.V.CYCLE_STARTS.clear()
    res = X.summarise(ti, X.ROU[X.TEST], False)
    res["cycle_s"] = info["cycle_program_s"]
    print(X.line("Webster dual ring", res), flush=True)
    json.dump({"plan": info, "test": res}, open(os.path.join(HERE, "results_webster_dr.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
