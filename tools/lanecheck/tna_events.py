"""Timing & Actuation charts with detector occupancy and phase-call events (code 43 call registered, 44 call
dropped), and a reader that turns them into event times. For measuring controller settings GDOT does not publish
(call handling on left-turn zones, detection-zone occupancy), independently of the Split Monitor statistics.

    fetch(sig, start, minutes=5, phases="1,2,3,4,5,6,7,8") -> folder of charts (cached in tools/cache/tna_events)
    read(chart, start, minutes) -> {"green": [(t0, t1)], "rows": [{"kind": "det"|"43"|"44", "on": [t], "off": [t]}]}
"""
import datetime as dt
import re
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, "tools")
sys.path.insert(0, "tools/lanecheck")
import atspm_timing as tna  # noqa: E402
from tna_count import rows as _bands  # noqa: E402

OUT = Path("tools/cache/tna_events")


def fetch(sig, start, minutes=5, phases="1,2,3,4,5,6,7,8"):
    d = OUT / f"{sig}_{start:%Y%m%d_%H%M}_{minutes}m_p{phases.replace(',', '')}"
    if d.exists() and any(d.glob("*.jpg")):
        return d
    payload = {"SignalID": str(sig), "StartDate": tna.fmt(start), "EndDate": tna.fmt(start + dt.timedelta(minutes=minutes)),
               "MetricTypeID": 17, "ShowLegend": False, "ShowHeaderForEachPhase": True, "CombineLanesForEachGroup": False,
               "DotAndBarSize": "6", "PhaseFilter": phases, "PhaseEventCodes": "43,44", "GlobalCustomEventCodes": "",
               "GlobalCustomEventParams": "", "ShowAllLanesInfo": True, "ShowLinesStartEnd": True, "ShowEventPairs": True,
               "ShowRawEventData": False, "ShowPermissivePhases": False, "ExtendVsdSearch": "5",
               "ShowVehicleSignalDisplay": True, "ShowPedestrianIntervals": False, "ExtendStartStopSearch": "2",
               "ShowPedestrianActuation": False, "ShowStopBarPresence": True, "ShowLaneByLaneCount": False,
               "ShowAdvancedDilemmaZone": False, "ShowAdvancedCount": False, "AdvancedOffset": "0"}
    for k in range(4):
        try:
            html = tna.post_json(f"{tna.BASE}/GetTimingAndActuations", payload, timeout=400)
            break
        except Exception:
            time.sleep(15 * (k + 1))
    else:
        raise RuntimeError("portal unavailable")
    html = html if isinstance(html, str) else html.decode()
    urls = re.findall(r'src="(https://[^"]+\.jpg)"', html)
    d.mkdir(parents=True, exist_ok=True)
    for i, u in enumerate(urls, 1):
        (d / f"{i:02d}.jpg").write_bytes(tna.get(u))
    return d


def _blobs(mask):
    """x centres of column runs where mask has pixels (markers)"""
    col = mask.any(axis=0)
    out, x = [], 0
    while x < len(col):
        if col[x]:
            a = x
            while x < len(col) and col[x]:
                x += 1
            if mask[:, a:x].sum() >= 4:
                out.append((a + x - 1) / 2)
        x += 1
    return out


def frame(path):
    """(x0, x1), horizontal grid lines. A grid line is dark across the whole plot (> 97 %); a long occupancy line
    (detector on for minutes) is not, so it is not mistaken for a row boundary (tna_count's 60 % rule did)."""
    im = np.asarray(Image.open(path).convert("RGB")).astype(int)
    dark = im.sum(axis=2) < 200
    H, W = dark.shape
    colrun = dark.sum(axis=0)
    xs = [x for x in range(W) if colrun[x] > 0.35 * H]
    x0, x1 = xs[0], xs[-1]
    if x1 - x0 < 0.6 * W:
        # charts with few rows (e.g. coordinated phases: display + two event rows) can miss the 35 % column rule;
        # take the plot edges from the longest horizontal dark run instead (a grid line spans the whole plot)
        best = (0, 0, 0)
        for y in range(H):
            r = np.flatnonzero(dark[y])
            if len(r) > best[0] and len(r) > 0.5 * W:
                best = (len(r), r[0], r[-1])
        if best[0]:
            ys = [y for y in range(H) if dark[y, best[1]:best[2] + 1].mean() > 0.97]
            band = dark[ys[0]:ys[-1] + 1]
            cols = np.flatnonzero(band.mean(axis=0) > 0.9)     # vertical plot border / grid lines
            x0, x1 = int(cols[0]), int(cols[-1])
    inner = dark[:, x0 + 2:x1 - 1]
    lines = []
    for y in range(H):
        if inner[y].mean() > 0.97 and (not lines or y - lines[-1] > 2):
            lines.append(y)
    return (x0, x1), lines


def read(path, start, minutes=5):
    im = np.asarray(Image.open(path).convert("RGB")).astype(int)
    (x0, x1), lines = frame(path)
    W = x1 - x0
    t = lambda x: (x + x0 + 2 - x0) / W * minutes * 60          # band x is relative to x0 + 2
    res = {"green": [], "rows": []}
    for i, (ya, yb) in enumerate(zip(lines[:-1], lines[1:])):
        sub = im[ya + 2:yb - 1, x0 + 2:x1 - 1]
        if i == 0:                                              # vehicle signal display: green fill (dark / spring / lime)
            mid = sub[sub.shape[0] // 2]
            g = (mid[:, 1] > 150) & (mid[:, 0] < 140)
            x = 0
            while x < len(g):
                if g[x]:
                    a = x
                    while x < len(g) and g[x]:
                        x += 1
                    res["green"].append((t(a), t(x)))
                x += 1
            continue
        dark = sub.sum(axis=2) < 200
        grid = dark.mean(axis=0) > 0.8                          # vertical grid lines run through the whole band
        black = sub.sum(axis=2) < 110
        black[:, grid] = False
        # a connecting line is 1-2 px tall; a marker is taller: keep columns with >= 3 dark pixels
        tall = black & (black.sum(axis=0) >= 3)[None, :]
        grey = (np.abs(sub[:, :, 0] - 120) < 30) & (np.abs(sub[:, :, 1] - 140) < 30) & (np.abs(sub[:, :, 2] - 150) < 30)
        res["rows"].append({"on": [t(x) for x in _blobs(tall)], "off": [t(x) for x in _blobs(grey)]})
    n = len(res["rows"])
    for j, r in enumerate(res["rows"]):                        # last two rows: phase events 43, 44 (request order)
        r["kind"] = "43" if j == n - 2 else ("44" if j == n - 1 else "det")
    return res


if __name__ == "__main__":
    st = dt.datetime.strptime(sys.argv[2], "%Y-%m-%dT%H:%M")
    d = fetch(sys.argv[1], st, int(sys.argv[3]) if len(sys.argv) > 3 else 5)
    for f in sorted(d.glob("*.jpg")):
        r = read(f, st)
        print(f.name, "green", [(round(a, 1), round(b, 1)) for a, b in r["green"]])
        for row in r["rows"]:
            print("   ", row["kind"], "on", [round(x, 1) for x in row["on"]], "off", [round(x, 1) for x in row["off"]])
