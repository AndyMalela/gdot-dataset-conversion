"""Offset between 137 and 138 from GDOT's Timing & Actuation charts (same 5-min windows at both signals).

    uv run python atsc/sites/137/neighbour138/offset_138.py   -> neighbour138/offsets.json, table

Reference: the end of each signal's westbound coordinated green (137 P6, 138 P2), which the field controller forces off
at a fixed point in the cycle. Per window: delta = (end_138 - end_137) mod C, matched to the nearest pair; per plan
the circular median over windows. Then 138's absolute offset in the engine:
    offset_138 = (fo_137 + delta - fo_138) mod C
with fo = the coordinated phase's force-off position in its own cycle (sum of splits up to it minus yellow and red),
137's plans getting absolute offset 0 (make_signal sets offset_s = 0 for 137 when this file exists).
"""
import datetime as dt
import json
import math
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tools/lanecheck"))
sys.path.insert(0, str(REPO / "tools"))
from tna_events import read  # noqa: E402
from atsc.sim.demand import schedule  # noqa: E402

CACHE = REPO / "tools/cache/tna_events"


def fo(sig, plan, phase):
    """force-off position (s into the cycle) of `phase` with absolute offset 0, as nema._fo_offset computes it"""
    p = sig["plans"][plan]
    for ring, groups in sig["rings"].items():
        t = 0.0
        for g in groups:
            for q in g:
                t += p["splits"].get(str(q), p["splits"].get(q, 0))
                if q == phase:
                    ph = sig["phases"][str(phase)]
                    return t - ph["yellow"] - ph["red"]
    raise KeyError(phase)


def main():
    s137 = json.loads((HERE.parent / "signal.json").read_text())
    s138 = json.loads((HERE / "signal.json").read_text())
    per_plan = defaultdict(list)
    for d138 in sorted(CACHE.glob("138_*_5m_p12345678")):
        tag = "_".join(d138.name.split("_")[1:3])
        d137 = CACHE / f"137_{tag}_5m_p12345678"
        if not d137.exists():
            continue
        st0 = dt.datetime.strptime(tag, "%Y%m%d_%H%M")
        t_mid = st0.hour * 3600 + st0.minute * 60 + 150
        plan137 = [n for t0, n in schedule(s137, st0.date()) if t0 <= t_mid][-1]
        plan138 = [n for t0, n in schedule(s138, st0.date()) if t0 <= t_mid][-1]
        if plan137 not in s137["plans"] or plan138 not in s138["plans"]:
            continue
        C = s137["plans"][plan137]["cycle"]
        if abs(s138["plans"][plan138]["cycle"] - C) > 1:
            print(f"{tag}: cycles differ ({plan137} {C} s vs {plan138} {s138['plans'][plan138]['cycle']} s), skipped")
            continue
        if not (d137 / "06.jpg").exists() or not (d138 / "02.jpg").exists():
            continue
        e137 = [b for a, b in read(d137 / "06.jpg", st0)["green"] if b - a > 5]
        e138 = [b for a, b in read(d138 / "02.jpg", st0)["green"] if b - a > 5]
        for x in e137:
            if not e138:
                break
            y = min(e138, key=lambda v: abs(((v - x + C / 2) % C) - C / 2))
            per_plan[(plan137, plan138)].append((y - x) % C)
    out, rows = {}, []
    for (p137, p138), ds in sorted(per_plan.items()):
        C = s137["plans"][p137]["cycle"]
        ang = [2 * math.pi * x / C for x in ds]
        mean = math.atan2(sum(map(math.sin, ang)), sum(map(math.cos, ang)))
        delta = (mean * C / (2 * math.pi)) % C
        spread = st.pstdev([((x - delta + C / 2) % C) - C / 2 for x in ds])
        off = (fo(s137, p137, 6) + delta - fo(s138, p138, 2)) % C
        out[p138] = round(off, 1)
        rows.append((p137, p138, C, len(ds), round(delta, 1), round(spread, 1), round(off, 1)))
    json.dump({"source": "offset_138.py: field green ends of 137 P6 and 138 P2 in the same Timing & Actuation windows",
               "offset_s": out, "rows": rows}, open(HERE / "offsets.json", "w"), indent=1)
    print("| 137 plan | 138 plan | cycle | pairs | delta = end138 - end137 (s) | spread (s) | 138 offset_s |")
    print("|---|---|---|---|---|---|---|")
    for r in rows:
        print("| " + " | ".join(map(str, r)) + " |")


if __name__ == "__main__":
    main()
