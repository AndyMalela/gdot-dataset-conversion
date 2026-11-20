"""Measure controller settings directly from GDOT Timing & Actuation event charts (no fitting).

    uv run python -m atsc.measure 137            -> table on stdout + atsc/sites/<id>/measured.json

Source: the 5-min Timing & Actuation charts with stop-bar occupancy cached by tools/lanecheck/tna_events.py
(tools/cache/tna_events/<id>_<YYYYmmdd>_<HHMM>_5m_p12345678/NN.jpg, one chart per phase, ~0.29 s per pixel).

- yellow, red clearance: run lengths of the yellow / dark-red fill in the vehicle signal display row.
- passage (vehicle extension) time: for greens that end while the phase's stop-bar zones are empty, the time
  from the last zone-off to the end of green. With non-locking presence detection and no other reason to end,
  that is the passage time; force-offs that happen to fall in an empty period add a spread of larger values,
  so the estimate is the mode of the distribution (0.25 s bins), reported with its share and the median.
Pixel resolution limits every value to about +-0.3 s.
"""
import datetime as dt
import itertools
import json
import re
import statistics as st
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "lanecheck"))
from tna_events import frame, read  # noqa: E402

CACHE = ROOT / "tools" / "cache" / "tna_events"


def _cls(p):
    r, g, b = p
    if g > 150 and r < 140:
        return "G"
    if r > 200 and g > 180 and b < 120:
        return "Y"
    if r > 120 and g < 60 and b < 60 or (r < 80 and g < 30 and b < 30 and r > 20):
        return "R"                                   # red clearance: dark red
    return "."


def display_runs(path, minutes=5):
    """[(class, t0, t1)] along the vehicle signal display row; edges flagged by t0 == 0 or t1 == window."""
    (x0, x1), lines = frame(path)
    im = np.asarray(Image.open(path).convert("RGB")).astype(int)
    ya, yb = lines[0], lines[1]
    mid = im[(ya + yb) // 2, x0 + 2:x1 - 1]
    s_per_px = minutes * 60 / (x1 - x0)
    out, x = [], 0
    for k, grp in itertools.groupby(_cls(p) for p in mid):
        n = len(list(grp))
        out.append((k, x * s_per_px, (x + n) * s_per_px, x == 0 or x + n >= len(mid) - 1))
        x += n
    return out, s_per_px


def clearances(sig):
    ys, rs = defaultdict(list), defaultdict(list)
    for d in sorted(CACHE.glob(f"{sig}_*_5m_p12345678")):
        for f in sorted(d.glob("0[1-8].jpg")):
            p = int(f.stem)
            try:
                runs, _ = display_runs(f)
            except (ValueError, IndexError):
                continue
            for (k0, *_), (k1, a, b, edge), (k2, *_) in zip(runs, runs[1:], runs[2:]):
                if edge:
                    continue
                if k1 == "Y" and k0 == "G":
                    ys[p].append(b - a)
                elif k1 == "R" and k0 == "Y":
                    rs[p].append(b - a)
    return ys, rs


def _pairs(on, off):
    """pair each 'on' with the next 'off' after it."""
    out, offs = [], sorted(off)
    for a in sorted(on):
        b = next((x for x in offs if x >= a), None)
        out.append((a, b if b is not None else float("inf")))
    return out


def passage(sig, phases):
    gaps = defaultdict(list)
    for d in sorted(CACHE.glob(f"{sig}_*_5m_p12345678")):
        m = re.match(rf"{sig}_(\d{{8}})_(\d{{4}})_5m", d.name)
        st0 = dt.datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M")
        for p in phases:
            f = d / f"{p:02d}.jpg"
            if not f.exists():
                continue
            try:
                r = read(f, st0)
            except (ValueError, IndexError):
                continue
            occ = sorted(iv for row in r["rows"] if row["kind"] == "det" for iv in _pairs(row["on"], row["off"]))
            for ga, gb in r["green"]:
                if ga < 1 or gb > 299:                    # green cut by the window edge
                    continue
                if any(a <= gb <= b for a, b in occ):     # zone occupied when green ended: not a gap-out
                    continue
                last = max((b for a, b in occ if ga <= b <= gb), default=None)
                if last is not None:
                    gaps[p].append(gb - last)
    return gaps


def mode(v, w=0.25):
    c = Counter(round(x / w) * w for x in v)
    k, n = c.most_common(1)[0]
    return k, n / len(v)


def main():
    sig = sys.argv[1]
    site = ROOT / "atsc" / "sites" / sig
    model = json.loads((site / "signal.json").read_text())["phases"]
    simj = json.loads((site / "sim.json").read_text())
    fitted = simj.get("controller", {}).get("passage_s", {})
    ys, rs = clearances(sig)
    gaps = passage(sig, [int(p) for p in model])
    out = {}
    print("phase | yellow: measured (n) vs model | red clear: measured (n) vs model | passage: mode (share), median, n vs fitted")
    for p in sorted(int(k) for k in model):
        y = st.median(ys[p]) if ys[p] else None
        r = st.median(rs[p]) if rs[p] else None
        g = [x for x in gaps[p] if x <= 15]
        pm = mode(g) if g else (None, 0)
        out[p] = {"yellow_s": y, "yellow_n": len(ys[p]), "red_clear_s": r, "red_n": len(rs[p]),
                  "passage_mode_s": pm[0], "passage_mode_share": pm[1], "passage_median_s": st.median(g) if g else None,
                  "passage_n": len(g)}
        fy = lambda v: f"{v:.1f}" if v is not None else "-"
        print(f"P{p} | {fy(y)} ({len(ys[p])}) vs {model[str(p)]['yellow']} | {fy(r)} ({len(rs[p])}) vs {model[str(p)]['red']} | "
              f"{fy(pm[0])} ({pm[1]:.0%}), {fy(out[p]['passage_median_s'])}, n={len(g)} vs {fitted.get(str(p), '-')}")
    (site / "measured.json").write_text(json.dumps({"source": "atsc/measure.py on " + str(CACHE.relative_to(ROOT)),
                                                    "phases": out}, indent=1))


if __name__ == "__main__":
    main()
