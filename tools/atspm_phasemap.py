#!/usr/bin/env python3
"""
Which approach and movement each signal phase controls, from GDOT ATSPM.

The Purdue Split Failure charts (one per phase/approach) are titled with GDOT's own
configuration, e.g. "Phase 1: SR 141 Peachtree Road NB LT". A grey chart background
marks a permissive phase (e.g. a left turn that may also go on the opposing through
green). The text is too small to read reliably without OCR, so this script saves the
titles as one image, and a person transcribes them into phase_map.json.

  python3 tools/atspm_phasemap.py 7065 --date 2026-10-02 --time 08:00

Output in intersections/<signal>/timing/:
  phase_titles.png      the chart subtitles, one per line, permissive ones marked
  phase_titles.json     per chart: file, permissive (from the background colour)
  split_fail/<date>_<HHMM>/  the downloaded charts

phase_map.json (written by hand from phase_titles.png), e.g.
  {"source": "...", "phases": [
     {"phase": 1, "desc": "SR 141 Peachtree Road NB LT", "street": "Peachtree",
      "dir": "NB", "move": "L", "type": "protected"},
     {"phase": 4, "desc": "SR 237 Piedmont Road EB LT", "street": "Piedmont",
      "dir": "EB", "move": "L", "type": "permissive"}, ...]}
"street"/"dir" are GDOT's description words; build_sim.py matches them to the network
approach by street name and closest heading (GDOT's description directions don't always
match the compass labels used in the count columns).
"""
import argparse
import datetime as dt
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import sig_dir, rel  # noqa: E402

BASE = "https://traffic.dot.ga.gov/ATSPM/DefaultCharts"
HEADERS = {"Content-Type": "application/json; charset=utf-8",
           "X-Requested-With": "XMLHttpRequest",
           "User-Agent": "atspm-tmc-research-puller (academic research)"}


def fetch(sid, start, minutes, outdir):
    fmt = lambda t: t.strftime("%m/%d/%Y %I:%M %p")
    body = json.dumps({"SignalID": str(sid), "StartDate": fmt(start),
                       "EndDate": fmt(start + dt.timedelta(minutes=minutes)),
                       "YAxisMax": "", "Y2AxisMax": "", "MetricTypeID": 12,
                       "FirstSecondsOfRed": "5", "ShowFailLines": True, "ShowAvgLines": True,
                       "ShowPercentFailLines": False}).encode()
    html = urllib.request.urlopen(urllib.request.Request(
        f"{BASE}/GetSplitFailMetric", data=body, method="POST", headers=HEADERS),
        timeout=240).read().decode("utf-8", "replace")
    if "Request Rejected" in html:
        raise RuntimeError("rejected by portal firewall")
    urls = re.findall(r'src="(https://[^"]+\.jpg)"', html)
    outdir.mkdir(parents=True, exist_ok=True)
    for i, u in enumerate(urls, 1):
        img = urllib.request.urlopen(urllib.request.Request(u, headers=HEADERS), timeout=60).read()
        (outdir / f"{i:02d}.jpg").write_bytes(img)
        time.sleep(0.5)
    return len(urls)


def titles(outdir, png):
    files = sorted(outdir.glob("[0-9][0-9].jpg"))
    rows, meta = [], []
    for f in files:
        a = np.asarray(Image.open(f).convert("RGB")).astype(int)
        bg = np.median(a[5:20, 5:200].reshape(-1, 3), axis=0)
        permissive = bool(abs(bg[0] - 211) < 12 and abs(bg[1] - 211) < 12)   # grey (211,211,211)
        rows.append((Image.fromarray(a[120:145, 400:1000].astype("uint8")), permissive))
        meta.append({"file": f.name, "permissive": permissive})
    if not rows:
        return meta
    h = 25
    out = Image.new("RGB", (700, h * len(rows)), "white")
    d = ImageDraw.Draw(out)
    for i, (im, perm) in enumerate(rows):
        out.paste(im, (0, i * h))
        d.text((605, i * h + 7), "PERMISSIVE" if perm else "", fill=(200, 0, 0))
    out.resize((1400, 2 * h * len(rows))).save(png)
    return meta


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("signals", nargs="+")
    ap.add_argument("--date", default=str(dt.date.today() - dt.timedelta(days=1)))
    ap.add_argument("--time", default="08:00", help="window start HH:MM (a coordinated period)")
    ap.add_argument("--minutes", type=int, default=30)
    a = ap.parse_args()
    for sid in a.signals:
        start = dt.datetime.combine(dt.date.fromisoformat(a.date), dt.time.fromisoformat(a.time))
        tdir = sig_dir(sid, "timing")
        outdir = tdir / "split_fail" / f"{start:%Y-%m-%d_%H%M}"
        if not any(outdir.glob("*.jpg")):
            n = fetch(sid, start, a.minutes, outdir)
            print(f"== {sid}: {n} Split Failure charts", flush=True)
        meta = titles(outdir, tdir / "phase_titles.png")
        (tdir / "phase_titles.json").write_text(json.dumps(meta, indent=1))
        print(f"   -> {rel(tdir / 'phase_titles.png')}  ({len(meta)} titles, "
              f"{sum(m['permissive'] for m in meta)} permissive)", flush=True)
        time.sleep(3)


if __name__ == "__main__":
    main()
