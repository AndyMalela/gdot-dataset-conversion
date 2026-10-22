"""Direction-label check: GDOT detector counts per phase vs the count report's columns.

GDOT's turning-movement report labels approaches with road-based direction words. This pulls one
Timing & Actuation window with the lane-by-lane count detectors shown, counts detector actuations per
phase chart, and compares them with the report's columns for the same 5 minutes, using each phase's
GDOT description (phase_map.json) to say which column it should match. If the labels were rotated
(as first assumed at 7065), the matches fail.

  python3 tools/atspm_dircheck.py 7130 [--date 2026-10-02 --time 08:00]
Writes intersections/<id>/timing/dircheck/<date>_<HHMM>/ (charts + dircheck.json).
"""
import argparse
import csv
import datetime as dt
import json
import re
import sys
from collections import defaultdict

import numpy as np
from PIL import Image

sys.path.insert(0, __import__("os").path.dirname(__file__))
import atspm_timing as tna  # noqa: E402
from paths import sig_dir  # noqa: E402

DIRS = ("NB", "SB", "EB", "WB")


def fetch(sid, start, outdir):
    payload = {
        "SignalID": str(sid), "StartDate": tna.fmt(start),
        "EndDate": tna.fmt(start + dt.timedelta(minutes=5)), "MetricTypeID": 17,
        "ShowLegend": False, "ShowHeaderForEachPhase": True, "CombineLanesForEachGroup": False,
        "DotAndBarSize": "6", "PhaseFilter": "", "PhaseEventCodes": "",
        "GlobalCustomEventCodes": "", "GlobalCustomEventParams": "",
        "ShowAllLanesInfo": True, "ShowLinesStartEnd": False, "ShowEventPairs": False,
        "ShowRawEventData": False, "ShowPermissivePhases": True, "ExtendVsdSearch": "5",
        "ShowVehicleSignalDisplay": True, "ShowPedestrianIntervals": False,
        "ExtendStartStopSearch": "2", "ShowPedestrianActuation": False,
        "ShowStopBarPresence": True, "ShowLaneByLaneCount": True,
        "ShowAdvancedDilemmaZone": False, "ShowAdvancedCount": False, "AdvancedOffset": "0",
    }
    import time
    for k in range(5):
        try:
            html = tna.post_json(f"{tna.BASE}/GetTimingAndActuations", payload, timeout=400)
            break
        except Exception as e:
            print(f"   portal error ({e.__class__.__name__}), retry {k + 1}/5", flush=True)
            time.sleep(20 * (k + 1))
    else:
        raise SystemExit("portal unavailable")
    urls = re.findall(r'src="(https://[^"]+\.jpg)"', html)
    outdir.mkdir(parents=True, exist_ok=True)
    for i, u in enumerate(urls, 1):
        (outdir / f"{i:02d}.jpg").write_bytes(tna.get(u))
    return len(urls)


def count_triangles(path):
    """Detector-on triangles per chart row below the vehicle display. Rows are found from the
    horizontal grid lines inside the plot frame; triangles are small black blobs."""
    im = np.asarray(Image.open(path).convert("RGB")).astype(int)
    H, W = im.shape[:2]
    dark = (im.sum(axis=2) < 150)
    # plot frame: columns with a long dark vertical run (left / right border)
    colrun = dark.sum(axis=0)
    xs = [x for x in range(W) if colrun[x] > 40]
    if len(xs) < 2:
        return []
    x0, x1 = xs[0], xs[-1]
    inner = dark[:, x0 + 2:x1 - 1]
    rowfrac = inner.mean(axis=1)
    hl = [y for y in range(H) if rowfrac[y] > 0.6]                    # horizontal grid/frame lines
    lines = []
    for y in hl:
        if not lines or y - lines[-1] > 2:
            lines.append(y)
    bands = list(zip(lines[:-1], lines[1:]))
    out = []
    for i, (ya, yb) in enumerate(bands):
        if i == 0:
            continue                                                    # vehicle signal display
        sub = dark[ya + 2:yb - 1, x0 + 2:x1 - 1].copy()
        # remove vertical grid lines (dark through nearly the whole band height)
        full = sub.mean(axis=0) > 0.7
        sub[:, full] = False
        # connected blobs along x (triangles ~5-9 px wide)
        colany = sub.any(axis=0)
        n, inblob = 0, False
        for v in colany:
            if v and not inblob:
                n += 1
            inblob = v
        out.append(n)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sid")
    ap.add_argument("--date", default="2026-10-02")
    ap.add_argument("--time", default="08:00")
    a = ap.parse_args()
    start = dt.datetime.strptime(f"{a.date} {a.time}", "%Y-%m-%d %H:%M")
    tdir = sig_dir(a.sid, "timing")
    wd = tdir / "dircheck" / f"{start:%Y-%m-%d_%H%M}_lanecount"
    if not (wd.exists() and any(wd.glob("*.jpg"))):
        print("charts:", fetch(a.sid, start, wd))
    pm = json.loads((tdir / "phase_map.json").read_text())
    det = defaultdict(int)
    for p in sorted(wd.glob("*.jpg")):
        c = tna.parse_chart(p, start, 5)
        if not c or c.get("kind") != "Phase" or c.get("num") is None:
            continue
        rows_n = count_triangles(p)
        # rows below the signal display: stop-bar presence rows, then the same number of
        # lane-by-lane count rows -> count only the second half
        det[int(c["num"])] += sum(rows_n[len(rows_n) // 2:])
    rows = [r for r in csv.DictReader(open(sig_dir(a.sid, "counts") / f"tmc_{a.sid}_5min.csv"))
            if r["date"] == a.date and r["time"] == a.time]
    tmc = rows[0] if rows else {}
    net_to_gdot = {v: k for k, v in pm.get("count_labels", {}).items()}   # network approach -> report label
    res = []
    for e in pm["phases"]:
        if e["type"] != "protected":
            continue
        m = re.search(r"\b(NB|SB|EB|WB)\b", e.get("desc", "")) or re.search(r"(NB|SB|EB|WB)(LT?|L)?\b", e.get("desc", ""))
        word = m.group(1) if m else None
        cols = {"L": ["L"], "T": ["T", "TR", "R"], "all": ["L", "T", "TR", "R", "TL"]}[e["move"]]
        def vol(lab):
            return sum(int(tmc.get(f"{lab}_{c}", 0) or 0) for c in cols if f"{lab}_{c}" in tmc)
        res.append({"phase": e["phase"], "desc": e.get("desc", ""), "approach": e["approach"], "move": e["move"],
                    "gdot_word": word, "detector_count": det.get(e["phase"]),
                    "report_by_word": vol(word) if word else None,
                    "report_by_approach_label": vol(net_to_gdot.get(e["approach"], e["approach"])),
                    "report_all_dirs": {d: vol(d) for d in DIRS if any(f"{d}_{c}" in tmc for c in cols)}})
    out = {"signal": a.sid, "window": f"{a.date} {a.time} (5 min)", "tmc_found": bool(tmc), "phases": res}
    (wd / "dircheck.json").write_text(json.dumps(out, indent=1))
    print(f"== {a.sid} {a.date} {a.time}  (report row found: {bool(tmc)})")
    for r in res:
        print(f"  P{r['phase']:<2} {r['desc'][:34]:34s} net {r['approach']} {r['move']:3s} detectors {r['detector_count']}"
              f" | report[{r['gdot_word']}] {r['report_by_word']} | report via count_labels {r['report_by_approach_label']}"
              f" | all {r['report_all_dirs']}")


if __name__ == "__main__":
    main()
