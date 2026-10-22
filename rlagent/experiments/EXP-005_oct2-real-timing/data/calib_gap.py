"""Calibrate SUMO driver gap acceptance for permissive left turns (EXP-005 §3.2).

Target: under the real GDOT timing, the Piedmont NB left must be served at the counted
rate without a growing queue -- the counts ARE what got through in reality. The driver
setting is a vType property, so the chosen value is then applied to every controller.

Grid: impatience x jmTimegapMinor. For each: real-timing run (full day + drain), report the
NB-left mean depart delay (day and peak), its served share in the peak, and the overall peak
total delay. Writes calib_gap.json.
"""
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_exp005 as R  # noqa: E402
from served import counted, served  # noqa: E402

GRID = [(0.0, 1.0), (0.5, 1.0), (1.0, 1.0), (0.0, 0.5), (0.5, 0.5), (1.0, 0.5)]


def rou_variant(imp, tg):
    s = open(R.ROU).read()
    s = re.sub(r'<vType id="car"[^>]*/>',
               f'<vType id="car" vClass="passenger" sigma="0.5" impatience="{imp}" jmTimegapMinor="{tg}"/>', s, 1)
    p = os.path.join(HERE, f"_rou_imp{imp}_tg{tg}.xml")
    open(p, "w").write(s)
    return p


def nbl_stats(ti):
    day, pk = [0, 0.0], [0, 0.0]
    for t in ET.parse(ti).getroot().iter("tripinfo"):
        if t.get("id").startswith("NB_L"):
            dd = float(t.get("departDelay"))
            it = float(t.get("depart")) - dd
            day[0] += 1
            day[1] += dd
            if R.PEAK_BEGIN <= it < R.PEAK_END:
                pk[0] += 1
                pk[1] += dd
    return round(day[1] / day[0], 1), round(pk[1] / pk[0], 1)


def main():
    out, cnt = {}, counted()
    for imp, tg in GRID:
        rou = rou_variant(imp, tg)
        ti = os.path.join(HERE, f"_ti_real_imp{imp}_tg{tg}.xml")
        cmd = ["sumo", "--net-file", R.NET, "--route-files", rou, "--additional-files", R.REAL,
               "--begin", "0", "--end", str(R.END), "--time-to-teleport", "300", "--seed", str(R.SEED),
               "--no-step-log", "--duration-log.disable", "--no-warnings", "--tripinfo-output", ti]
        subprocess.run(cmd, check=True, capture_output=True)
        d_day, d_pk = nbl_stats(ti)
        sv = served(ti)
        r = R.realised(ti)
        out[f"impatience={imp},jmTimegapMinor={tg}"] = {
            "nb_left_depart_delay_day_s": d_day, "nb_left_depart_delay_peak_s": d_pk,
            "nb_left_served_peak_pct": round(100 * sv["NB_L"] / cnt["NB_L"]),
            "peak_total_delay_s": r["peak"]["total_delay_s"], "unserved_day": R.demand_total() - r["day"]["trips"]}
        print(f"impatience {imp}  timegap {tg}:  NB-left depart delay day {d_day:7.1f} s, peak {d_pk:7.1f} s, "
              f"served {out[list(out)[-1]]['nb_left_served_peak_pct']}% | all-movement peak total delay "
              f"{r['peak']['total_delay_s']} s", flush=True)
        os.remove(rou)
        os.remove(ti)
    json.dump(out, open(os.path.join(HERE, "calib_gap.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
