"""Estimate how many vehicles 137's stop-bar presence zones miss (agreed with the user 2026-11-16 10:00, option 2).

GDOT's report counts one vehicle per zone activation (VALIDATION.md, finding 09:30). A queue discharging over the
zone keeps it occupied, so several vehicles register as one. From Timing & Actuation charts with zone occupancy
(tools/lanecheck/tna_events.py, train days only), per activation [on, off]:

    vehicles = 1 + max(0, floor((green overlap - PASS) / H))

  green overlap  time the zone stays occupied while its own phase shows a protected green (vehicles can discharge);
                 permissive left turns and right turns on red are counted 1 per activation (not at saturation)
  PASS           time one free-moving vehicle occupies the zone: median of activations that start and end inside
                 green, per zone (measured)
  H              saturation headway 3600 / 1,900 s (HCM base saturation flow; sensitivity: 1,650 = the simulated
                 discharge of this network)

Per movement, k = sum(estimated) / sum(reported) over the sampled daytime windows. Output: the table below and
intersections/137/counts/presence_factors.json. Nothing is applied here (build_upstream_counts_137.py applies it).

    uv run python tools/lanecheck/estimate_137_presence.py [H_sat=1900]
"""
import csv
import datetime as dt
import json
import math
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, "tools/lanecheck")
sys.path.insert(0, "tools")
from tna_count import labels, rows as bands  # noqa: E402
from tna_events import frame, read  # noqa: E402

SAT = float(sys.argv[1]) if len(sys.argv) > 1 else 1900.0
H = 3600 / SAT
# chart file (phase order 1..8) -> its stop-bar presence rows, in chart order, and the report column each one counts
ZONES = {"03.jpg": ["NB_L"], "04.jpg": ["SB_T", "SB_R"], "05.jpg": ["EB_L"], "07.jpg": ["SB_L"], "08.jpg": ["NB_T", "NB_R"]}
PROTECTED_ONLY = {"NB_L", "SB_L", "EB_L"}           # permissive service not at saturation: 1 per activation
REF = sorted(Path("tools/cache/tna_events").glob("137_20260310_1700_5m_*"))[0]   # reference row labels
TEST0, TEST1 = "2026-05-18", "2026-05-29"


def intervals(row):
    """[(on, off)] pairing each on with the next off; an off with no on starts at 0, an on with no off ends at 300."""
    ons, offs, out = sorted(row["on"]), sorted(row["off"]), []
    if offs and (not ons or offs[0] < ons[0]):
        out.append((0.0, offs.pop(0)))
    for a in ons:
        b = next((o for o in offs if o > a), 300.0)
        if offs and b in offs:
            offs.remove(b)
        out.append((a, b))
    return out


def overlap(a, b, greens):
    return sum(max(0.0, min(b, g1) - max(a, g0)) for g0, g1 in greens)


def main():
    rep = {(r["date"], r["time"]): r for r in csv.DictReader(open("intersections/137/counts/tmc_137_5min.csv"))}
    ref_labels = {f: labels(str(REF / f), frame(REF / f)[1]) for f in ZONES}
    samples = []                       # (date, time, column, reported, activations, estimated, intervals, greens)
    skipped = 0
    for d in sorted(Path("tools/cache/tna_events").glob("137_*_5m_p12345678")):
        st0 = dt.datetime.strptime(d.name.split("_")[1] + d.name.split("_")[2], "%Y%m%d%H%M")
        key = (f"{st0:%Y-%m-%d}", f"{st0:%H:%M}")
        assert not TEST0 <= key[0] <= TEST1, "locked test set"
        if key not in rep or rep[key]["status"] != "ok":
            continue
        for f, cols in ZONES.items():
            if not (d / f).exists():
                continue
            lines = frame(d / f)[1]
            lab = labels(str(d / f), lines)
            if len(lab) != len(ref_labels[f]) or any(np.mean(a != b) > 0.08 for a, b in zip(lab, ref_labels[f]) if a.shape == b.shape):
                skipped += 1                                        # rows not in the reference order: not used
                continue
            r = read(d / f, st0)
            dets = [x for x in r["rows"] if x["kind"] == "det"]
            for col, row in zip(cols, dets):
                iv = intervals(row)
                samples.append((key[0], key[1], col, int(rep[key][col]), len(iv), iv, r["green"]))
    # PASS per zone: activations fully inside one green interval
    passes = defaultdict(list)
    for _, _, col, _, _, iv, gr in samples:
        for a, b in iv:
            if any(g0 <= a and b <= g1 for g0, g1 in gr) and b - a < 10:
                passes[col].append(b - a)
    allp = [x for v in passes.values() for x in v]
    PASS = {c: (st.median(passes[c]) if len(passes[c]) >= 5 else st.median(allp)) for c in {s[2] for s in samples}}
    tot = defaultdict(lambda: [0, 0, 0])
    out_rows = []
    for date, tm, col, reported, acts, iv, gr in samples:
        est = 0
        for a, b in iv:
            ov = overlap(a, b, gr)
            first = 0 if a <= 0.0 else 1          # occupied at the window start: that vehicle was counted in the previous bin
            est += first + max(0, math.floor((ov - (PASS[col] if first else 0.0)) / H))
        tot[col][0] += reported
        tot[col][1] += sum(1 for a, _ in iv if a > 0.0)
        tot[col][2] += est
        out_rows.append({"date": date, "time": tm, "movement": col, "reported": reported, "activations": sum(1 for a, _ in iv if a > 0.0), "estimated": est})
    print(f"saturation flow {SAT:.0f} veh/h/lane (H = {H:.2f} s); windows skipped for row order: {skipped}")
    print("| movement | windows | reported | zone activations | estimated vehicles | factor k | PASS s |")
    print("|---|---|---|---|---|---|---|")
    fac = {}
    for col in sorted(tot):
        rp, ac, es = tot[col]
        n = sum(1 for s in samples if s[2] == col)
        fac[col] = round(es / rp, 3) if rp else None
        print(f"| {col} | {n} | {rp} | {ac} | {es} | {fac[col]} | {PASS[col]:.1f} |")
    Path("intersections/137/counts").mkdir(exist_ok=True)
    with open(f"intersections/137/counts/presence_estimate_{int(SAT)}.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0]))
        w.writeheader()
        w.writerows(out_rows)
    json.dump({"saturation_flow": SAT, "headway_s": round(H, 3), "pass_s": {k: round(v, 2) for k, v in PASS.items()},
               "factor": fac, "windows": len({(s[0], s[1]) for s in samples}),
               "days": sorted({s[0] for s in samples}), "method": __doc__.split("\n\n")[1]},
              open(f"intersections/137/counts/presence_factors_{int(SAT)}.json", "w"), indent=1)


if __name__ == "__main__":
    main()
