#!/usr/bin/env python3
"""
Rebuild a signal's time-of-day timing plans from GDOT ATSPM charts.

For each signal and date:
  1. Split Monitor, one full-day request. Each plan is a shaded band on the chart,
     and the controller's programmed split per phase is drawn as an orange line.
     The y axis is pinned to 0-200 s (YAxisMax) so every chart has the same scale.
     Where the orange line is hidden under force-off dots, the dots are used: in a
     coordinated plan a non-coordinated phase is forced off exactly at its split.
  2. Timing & Actuation, one 5-min window in the busiest daytime plan (reuses
     atspm_timing.py): yellow, red clearance, and which phase of each pair leads.

Plan numbers are NOT read (the chart prints them in a 6-px font that can't be told
apart reliably without OCR). Bands with the same splits get the same letter (A, B, ...);
the saved charts show the controller's plan numbers if you need them.

  python3 tools/atspm_plans.py 7065 --date 2026-09-29
  python3 tools/atspm_plans.py 7065 44 337 --date 2026-09-29 2026-09-30
  python3 tools/atspm_plans.py 7065 --date 2026-09-29 --no-clearance
  python3 tools/atspm_plans.py 7065 --rebuild          # re-parse saved charts

Output in intersections/<signal>/timing/:
  timing_plan_<signal>.md     readable summary: schedule, splits, clearances, checks
  timing_plan_<signal>.json   same, machine-readable (for a SUMO fixed-time baseline)
  plans_<signal>.csv          one row per plan band per date, raw and rounded splits
  split_monitor/<date>/       Split Monitor charts, Phase_<n>.jpg
  raw/<date>_<HHMM>_5min/     Timing & Actuation charts used for clearances

Assumes standard NEMA dual-ring structure (ring 1 = 1-4, ring 2 = 5-8, barrier
between 2|3 and 6|7). Every plan is checked against it; failures are flagged, never
adjusted.

Requires Pillow and numpy.
"""
import argparse
import csv
import datetime as dt
import json
import re
import sys
import time
import urllib.request
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import atspm_timing as tna  # noqa: E402  (Timing & Actuation fetch/parse)

BASE = "https://traffic.dot.ga.gov/ATSPM/DefaultCharts"
from paths import sig_dir, rel  # noqa: E402
HEADERS = {"Content-Type": "application/json; charset=utf-8",
           "X-Requested-With": "XMLHttpRequest",
           "User-Agent": "atspm-tmc-research-puller (academic research)"}
Y_MAX = 200                       # pinned y axis, seconds
RING1, RING2 = (1, 2, 3, 4), (5, 6, 7, 8)
MIN_BAND_MIN = 10                 # bands shorter than this are reported as transitions

# "Phase <n>" header digits (bold, 9 rows), taken from signal 7065's charts
_D = {
    "1": (4, "..######..##..##..##..##..##..##..##"),
    "2": (6, ".#####.##.##.....#....##....##...##...##...##...######"),
    "3": (6, "####..##.##....##....##...##.....##.....####.##.#####."),
    "4": (7, "....#.....##....###....###...#..#...#..#..#######....#......#.."),
    "5": (6, "#####.##....##....#####.##.##.#...##....####.##.####.."),
    "6": (6, ".####.##.##.##....#.....#####.##.##.#...####.##..####."),
    "7": (6, "######....#....##....#....##....##....#....##....##..."),
    "8": (6, ".####.##.##.##.##.##.##..###..##.##.#...####.##.#####."),
    "0": (6, ".####.##.##.##..#.#...###...###...####..#.##.##..####."),
    "9": (6, "####..##.##.#...#.##.#########....#....##.##.##.####.."),   # from 7130
}
DIGIT_T = {k: np.array([c == "#" for c in s]).reshape(9, w) for k, (w, s) in _D.items()}


# =========================================================================== fetch
def fetch_split_monitor(sid, day, outdir):
    """Download the full-day Split Monitor charts into outdir. Returns n charts."""
    d = day.strftime("%m/%d/%Y")
    # NB: sending empty YAxisMin / Y2AxisMin (as the website does) gets the request
    # rejected by the portal's firewall, so they are left out.
    body = json.dumps({
        "SignalID": str(sid), "StartDate": f"{d} 12:00 AM", "EndDate": f"{d} 11:59 PM",
        "YAxisMax": str(Y_MAX), "Y2AxisMax": "", "MetricTypeID": 2,
        "SelectedPercentileSplit": "85", "ShowPlanStripes": True, "ShowPedActivity": False,
        "ShowAverageSplit": True, "ShowPercentMaxOutForceOff": True,
        "ShowPercentGapOuts": True, "ShowPercentSkip": True}).encode()
    for attempt in range(3):
        try:
            req = urllib.request.Request(f"{BASE}/GetSplitMonitorMetric", data=body,
                                         method="POST", headers=HEADERS)
            html = urllib.request.urlopen(req, timeout=240).read().decode("utf-8", "replace")
            break
        except Exception as e:
            if attempt == 2:
                raise
            print(f"      ({e}); retrying in {30 * (attempt + 1)}s", flush=True)
            time.sleep(30 * (attempt + 1))
    if "Request Rejected" in html:
        raise RuntimeError("rejected by portal firewall")
    urls = re.findall(r'src="(https://[^"]+\.jpg)"', html)
    if not urls:
        return 0
    tmp = outdir.with_name(outdir.name + ".part")
    tmp.mkdir(parents=True, exist_ok=True)
    for i, u in enumerate(urls, 1):
        img = urllib.request.urlopen(urllib.request.Request(u, headers=HEADERS), timeout=60).read()
        (tmp / f"{i:02d}.jpg").write_bytes(img)
    name_charts(tmp)
    tmp.rename(outdir)
    return len(urls)


def name_charts(ddir):
    """Rename downloaded NN.jpg files to Phase_<n>.jpg / legend.jpg where readable."""
    for p in sorted(ddir.glob("[0-9][0-9].jpg")):
        ph = read_phase(np.asarray(Image.open(p).convert("L")).astype(int))
        if ph is not None and not (ddir / f"Phase_{ph}.jpg").exists():
            p.rename(ddir / f"Phase_{ph}.jpg")
        elif ph is None and p.name == "01.jpg":
            p.rename(ddir / "legend.jpg")


# =========================================================================== parse
def read_phase(gray):
    """Phase number from the 'Phase <n>' header, or None (legend / unreadable)."""
    band = gray[120:145, 400:1000] < 128
    ys = np.where(band.any(1))[0]
    if len(ys) == 0:
        return None
    y0 = 120 + ys.min()
    b = gray[y0:y0 + 9, 400:1000] < 128
    cols = np.where(b.any(0))[0]
    r = cols[-1]
    l = r
    while l > 0 and b[:, l - 1].any():
        l -= 1
    glyph = b[:, l:r + 1]

    def pad(m):                                       # right-align in a 9 x 10 box
        out = np.zeros((9, 10), bool)
        w = min(m.shape[1], 10)
        out[:, 10 - w:] = m[:, m.shape[1] - w:]
        return out
    g = pad(glyph)
    dist = {}
    for k, t in DIGIT_T.items():
        tp = pad(t)
        dist[k] = min(int((np.roll(tp, s, axis=1) != g).sum()) for s in (-1, 0, 1))
    ranked = sorted(dist, key=dist.get)
    best, best_d = ranked[0], dist[ranked[0]]
    if best_d > 12 or dist[ranked[1]] - best_d < 4:   # no clear winner
        return None
    # phases 10-16 have a "1" before the last digit (the "e" of "Phase" never matches it)
    k = l - 1
    while k > 0 and not b[:, k].any():
        k -= 1
    j = k
    while j > 0 and b[:, j - 1].any():
        j -= 1
    prev = pad(b[:, j:k + 1])
    if min(int((np.roll(pad(DIGIT_T["1"]), s, axis=1) != prev).sum()) for s in (-1, 0, 1)) <= 6:
        return 10 + int(best)
    return int(best)


def plot_frame(gray):
    rows = [y for y in range(150, gray.shape[0]) if (gray[y, 300:1200] < 60).sum() > 800]
    top, bottom = max(zip(rows[:-1], rows[1:]), key=lambda p: p[1] - p[0])
    cols = [x for x in range(gray.shape[1]) if (gray[top + 40:bottom - 40, x] < 60).mean() > 0.6]
    return top, bottom, cols[0], cols[-1]            # top, bottom, x(00:00), x(24:00)


def bands_from_background(rgb, top, bottom, x0, x1):
    """Plan bands from the alternating blue / gray background. -> [(xa, xb)]"""
    blue = np.array([216, 236, 240])
    gray = np.array([232, 232, 232])
    sub = rgb[top + 3:bottom - 2, x0 + 1:x1]
    db = np.abs(sub - blue).sum(2) < 18
    dg = np.abs(sub - gray).sum(2) < 18
    lab = np.where(db.sum(0) >= dg.sum(0), 1, 0)
    # vertical grid lines carry no background; inherit from the left
    nobg = (db.sum(0) + dg.sum(0)) < 10
    for i in range(1, len(lab)):
        if nobg[i]:
            lab[i] = lab[i - 1]
    out, s = [], 0
    for i in range(1, len(lab) + 1):
        if i == len(lab) or lab[i] != lab[s]:
            out.append((x0 + 1 + s, x0 + 1 + i))
            s = i
    return out


def split_in_band(rgb, top, bottom, xa, xb):
    """Programmed split (s) inside one band -> (value or None, source, coverage)."""
    spp = Y_MAX / (bottom - top)
    lo, hi = xa + 4, xb - 4                          # skip the step lines at plan changes
    if hi - lo < 4:
        lo, hi = xa + 1, xb - 1
    R, G, B = (rgb[top + 1:bottom, lo:hi, k] for k in range(3))
    orange = (R > 140) & (R - B > 80) & (G > 60) & (G < 170)
    # max-out dots are pure red with JPEG-blurred edges that also look orange; the split
    # line never has a pure-red core, so drop orange pixels within 3 px of pure red
    core = (R > 150) & (G < 60) & (B < 60)
    near = core.copy()
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            near |= np.roll(np.roll(core, dy, 0), dx, 1)
    orange &= ~near
    forceoff = (B > 110) & (R < 80) & (G < 80)
    ncols = hi - lo

    def level(mask):
        ys, xs = np.nonzero(mask)
        if len(ys) == 0:
            return None, 0, 0.0
        # the row seen in the most distinct columns (a horizontal line), not the most pixels
        y_mode, n = Counter(y for y, _ in set(zip(ys, xs))).most_common(1)[0]
        near = ys[np.abs(ys - y_mode) <= 1]
        return round((bottom - (top + 1 + near.mean())) * spp, 1), n, mask.any(0).sum() / ncols

    # The orange programmed-split line is the truth, but dots are drawn over it, so in
    # busy plans only a few pixels of it may show. Force-off dots sit near the split
    # (not exactly on it for coordinated phases), so they are used to confirm a sparse
    # orange read, and only as a last resort on their own.
    olive = (G > 110) & (G - B > 60) & (R < 160) & (R > 60)      # gap-out dots
    red = (R > 200) & (G < 60) & (B < 60)                          # max-out dots
    v_or, n_or, cov_or = level(orange)
    v_fo, _, cov_fo = level(forceoff)
    if v_or is not None and (n_or >= 2 or (v_fo is not None and abs(v_or - v_fo) <= 3)):
        return v_or, "programmed", round(float(cov_or), 2)
    if v_fo is not None and cov_fo >= 0.3:
        return v_fo, "force-off (approx)", round(float(cov_fo), 2)
    # Fixed-time-like operation: every cycle ends at the same time ("unknown termination",
    # black dots), drawn exactly on top of the split line. Black gridlines are excluded:
    # horizontal ones every 1/10 of the plot height, vertical ones (hour lines) by column.
    black = (R < 60) & (G < 60) & (B < 60)
    black[:, black.mean(0) > 0.5] = False             # vertical hour lines
    # horizontal gridlines are 1 px tall; dots are blobs: keep pixels with a black
    # neighbour directly above or below (so a split that sits on a gridline still reads)
    vert = np.zeros_like(black)
    vert[1:-1] = black[1:-1] & (black[:-2] | black[2:])
    black = vert
    if black.any():
        ys, xs = np.nonzero(black)
        cols = {}
        for y, x in zip(ys, xs):
            cols.setdefault(x, []).append(y)
        y_mode = Counter(int(np.median(v)) for v in cols.values()).most_common(1)[0][0]
        tight = sum(abs(np.median(v) - y_mode) <= 2 for v in cols.values()) / len(cols)
        if len(cols) / ncols >= 0.3 and tight >= 0.8:
            near = [y for v in cols.values() for y in v if abs(y - y_mode) <= 2]
            v_bk = round((bottom - (top + 1 + float(np.mean(near)))) * spp, 1)
            return v_bk, "fixed (dots on split)", round(len(cols) / ncols, 2)
    dots = olive | red | forceoff
    if ncols and dots.any(0).sum() / ncols >= 0.05:
        ys, _ = np.nonzero(dots)
        return round((bottom - (top + 1 + float(np.median(ys)))) * spp, 1), "observed", \
            round(float(dots.any(0).sum() / ncols), 2)
    return None, "none", 0.0


def x_to_time(x, x0, x1):
    m = round((x - x0) / (x1 - x0) * 1440)
    return f"{m // 60:02d}:{m % 60:02d}"


def maxout_in_band(rgb, top, bottom, xa, xb):
    """Observed upper end of a phase's time in a band: the max-out level (red dots all
    end at max green + clearance) if any, else the 95th percentile of all termination
    dots (a lower bound on the max). -> (seconds or None, 'max-out'|'p95'|'none')"""
    spp = Y_MAX / (bottom - top)
    lo, hi = xa + 4, xb - 4
    if hi - lo < 4:
        lo, hi = xa + 1, xb - 1
    R, G, B = (rgb[top + 1:bottom, lo:hi, k] for k in range(3))
    core = (R > 150) & (G < 60) & (B < 60)                    # max-out dot cores
    ys, xs = np.nonzero(core)
    if len(set(xs)) >= 3:
        y_mode = Counter(y for y, _ in set(zip(ys, xs))).most_common(1)[0][0]
        near = ys[np.abs(ys - y_mode) <= 2]
        return round((bottom - (top + 1 + near.mean())) * spp, 1), "max-out"
    dots = ((G > 110) & (G - B > 60) & (R < 160) & (R > 60)) | core | ((B > 110) & (R < 80) & (G < 80))
    ys, xs = np.nonzero(dots)
    if len(set(xs)) >= 5:
        return round((bottom - (top + 1 + float(np.percentile(ys, 5)))) * spp, 1), "p95"
    return None, "none"


def termination_mix(rgb, top, bottom, xa, xb):
    """Share of cycles in the band by how the phase ended, from the dot colours:
    gap-out (olive), max-out (red), force-off (blue), unknown/fixed (black).
    -> {"gap": f, "max": f, "force": f, "fixed": f, "n": columns with a dot}"""
    lo, hi = xa + 4, xb - 4
    if hi - lo < 4:
        lo, hi = xa + 1, xb - 1
    R, G, B = (rgb[top + 1:bottom, lo:hi, k] for k in range(3))
    masks = {"gap": (G > 110) & (G - B > 60) & (R < 160) & (R > 60),
             "max": (R > 150) & (G < 60) & (B < 60),
             "force": (B > 110) & (R < 80) & (G < 80)}
    black = (R < 60) & (G < 60) & (B < 60)
    black[:, black.mean(0) > 0.5] = False
    vert = np.zeros_like(black)
    vert[1:-1] = black[1:-1] & (black[:-2] | black[2:])
    masks["fixed"] = vert
    cols = {k: m.any(0) for k, m in masks.items()}
    n = int(np.logical_or.reduce(list(cols.values())).sum())
    if n == 0:
        return {"n": 0}
    return {"n": n, **{k: round(float(v.sum()) / n, 2) for k, v in cols.items()}}


def parse_day(ddir):
    """-> list of bands: {start, end, minutes, splits_raw{ph: (v, src, cov)}}"""
    name_charts(ddir)
    charts = {int(p.stem.split("_")[1]): p for p in ddir.glob("Phase_*.jpg")}
    if not charts:
        return [], []
    geo, bands, per_phase, empty = None, None, {}, []
    for ph, p in sorted(charts.items()):
        rgb = np.asarray(Image.open(p).convert("RGB")).astype(int)
        g = rgb.mean(2)
        try:
            top, bottom, x0, x1 = plot_frame(g)
        except (ValueError, IndexError):
            empty.append(ph)          # no plot area drawn: the phase never ran that day
            continue
        own = bands_from_background(rgb, top, bottom, x0, x1)
        if bands is None:
            geo, bands = (top, bottom, x0, x1), own
        # use this chart's own band edges (they can sit a pixel or two off the reference
        # chart's), matched to the reference bands by overlap
        reads = []
        for a, b in bands:
            oa, ob = max(own, key=lambda o: min(b, o[1]) - max(a, o[0]))
            reads.append(split_in_band(rgb, top, bottom, oa, ob) + maxout_in_band(rgb, top, bottom, oa, ob)
                         + (termination_mix(rgb, top, bottom, oa, ob),))
        per_phase[ph] = reads
    if geo is None:
        return [], sorted(charts)
    for ph in empty:
        per_phase[ph] = [(None, "none", 0.0, None, "none", {"n": 0})] * len(bands)
    top, bottom, x0, x1 = geo
    out = []
    for i, (a, b) in enumerate(bands):
        out.append({
            "start": x_to_time(a, x0, x1), "end": x_to_time(b, x0, x1),
            "minutes": round((b - a) / (x1 - x0) * 1440),
            "splits_raw": {ph: per_phase[ph][i][:3] for ph in per_phase},
            "maxout": {ph: per_phase[ph][i][3:5] for ph in per_phase},
            "term": {ph: per_phase[ph][i][5] for ph in per_phase}})
    return out, sorted(charts)


def check_plan(splits):
    """splits: {ph: int or 0} for phases 1-8. -> (cycle, ring1, ring2, flags[])

    Cycle = sum over the two barrier groups of the longer ring in that group. Where both
    rings serve phases in a group, their sums must match (that is what a barrier means);
    a group served by only one ring (e.g. a one-way side street) is not a mismatch.
    A 1 s difference is reported as rounding (charts are read at ~0.5 s per pixel)."""
    s = lambda phs: sum(splits.get(p, 0) for p in phs)
    groups = (((1, 2), (5, 6)), ((3, 4), (7, 8)))
    extra = {p: v for p, v in splits.items() if p > 8 and v}
    used = set()
    cycle, flags = 0, []
    for a, b in groups:
        sa, sb = s(a), s(b)
        if sa and sb and abs(sa - sb) > 1:
            # an extra phase (9-16) whose split exactly fills the gap: report where it fits
            short = b if sa > sb else a
            fit = next((p for p, v in extra.items() if p not in used and abs(abs(sa - sb) - v) <= 1), None)
            if fit is not None:
                used.add(fit)
                ring = 1 if short[0] <= 4 else 2
                if short == a:
                    sa += extra[fit]
                else:
                    sb += extra[fit]
                flags.append(f"closes with P{fit} in ring {ring} beside "
                             f"{'+'.join(map(str, short))} (inferred from the splits)")
        cycle += max(sa, sb)
        if sa and sb and sa != sb:
            msg = f"{'+'.join(map(str, a))}={sa} vs {'+'.join(map(str, b))}={sb}"
            flags.append(f"closes within 1 s ({msg})" if abs(sa - sb) == 1 else f"barrier mismatch ({msg})")
    return cycle, s(RING1), s(RING2), flags


# =========================================================================== clearance
def clearance(sid, sdir, day, bands):
    """One 5-min Timing & Actuation window inside the longest daytime band."""
    def mins(hhmm):
        h, m = map(int, hhmm.split(":"))
        return h * 60 + m
    # a coordinated daytime plan: midpoint 07:00-19:00, and a programmed-split line on
    # most phases (so not Free, where minor phases may not run at all)
    def coordinated(b):
        raw = b["splits_raw"].values()
        return sum(src in ("programmed", "fixed (dots on split)") for _, src, _ in raw) >= \
            max(2, len(raw) // 2)
    day_bands = [b for b in bands if 7 * 60 <= (mins(b["start"]) + mins(b["end"])) // 2 <= 19 * 60
                 and b["minutes"] >= 30 and coordinated(b)]
    if day_bands:
        b = max(day_bands, key=lambda b: b["minutes"])
        mid = (mins(b["start"]) + mins(b["end"])) // 2
    else:
        mid = 12 * 60          # no coordinated plan (e.g. Free all day): clearances are fixed anyway
    ws = dt.datetime.combine(day, dt.time(mid // 60, (mid % 60) // 5 * 5))
    wd = sdir / "raw" / f"{ws:%Y-%m-%d_%H%M}_5min"
    if not (wd.exists() and any(wd.glob("*.jpg"))):
        status, n = tna.fetch_window(sid, ws, 5, wd)
        if status != "ok":
            return {"window": f"{ws:%Y-%m-%d %H:%M}", "error": status}
    charts = tna.parse_window(wd, ws, 5)
    _, greens = tna.window_records(sid, str(day), ws, 5, charts)
    res = {"window": f"{ws:%Y-%m-%d %H:%M} (5 min)", "yellow": {}, "red_clear": {}, "lead": {}}
    starts, ends = {}, {}
    for g in greens:
        m = re.match(r"Phase_(\d+)$", g["chart"])
        if not m:
            continue
        ph = int(m.group(1))
        t0 = dt.datetime.strptime(g["green_start"][:8], "%H:%M:%S")
        starts.setdefault(ph, []).append(t0)
        if g["yellow_s"] != "" and g["red_clear_s"] != "" and not g.get("truncated") in ("1", 1, True):
            ends.setdefault(ph, []).append(t0 + dt.timedelta(
                seconds=float(g["green_s"]) + float(g["yellow_s"]) + float(g["red_clear_s"])))
        for key in ("yellow", "red_clear"):
            if g[f"{key}_s"] != "":
                res[key].setdefault(ph, []).append(g[f"{key}_s"])
    for key in ("yellow", "red_clear"):
        res[key] = {ph: tna.med(v) for ph, v in sorted(res[key].items())}
    # lead/lag: within a ring, the leading phase's clearance ends exactly when the other phase of
    # its pair starts. (Comparing nearest green starts is ambiguous with ~2 cycles per window:
    # the lagging phase sits about half a cycle from the leading one on both sides.)
    for a, b in ((1, 2), (5, 6), (3, 4), (7, 8)):
        votes = Counter()
        for x, y in ((a, b), (b, a)):
            for te in ends.get(x, []):
                if any(abs((ty - te).total_seconds()) <= 2.5 for ty in starts.get(y, [])):
                    votes[x] += 1
        if votes:
            res["lead"][f"{a}/{b}"] = votes.most_common(1)[0][0]
    return res


# =========================================================================== output
def build(sid, sdir, name):
    days = sorted(d for d in (sdir / "split_monitor").glob("????-??-??") if d.is_dir())
    recs, phases_seen = [], set()
    for ddir in days:
        bands, phases = parse_day(ddir)
        phases_seen |= set(phases)
        for b in bands:
            raw = b["splits_raw"]
            prog = {ph: x for ph, x in raw.items()
                    if x[1] in ("programmed", "force-off (approx)", "fixed (dots on split)")}
            splits = {ph: (round(v) if v is not None and v >= 3 else 0)
                      for ph, (v, src, _) in raw.items() if src != "observed"}
            cycle, r1, r2, flags = check_plan(splits)
            n_obs = sum(src == "observed" for _, src, _ in raw.values())
            half = max(2, -(-len(raw) // 2))
            if b["minutes"] < MIN_BAND_MIN:
                kind = "transition"
            elif len(prog) >= half:
                kind = "plan"
            elif not prog and n_obs >= half:
                kind = "free"        # no split line readable: Free or uncoordinated actuated
                cycle = 0
            else:
                kind = "no data"     # too little on the chart (no cycles logged)
            recs.append(dict(date=ddir.name, b=b, raw=raw, splits=splits, cycle=cycle,
                             r1=r1, r2=r2, flags=flags, kind=kind, label="", note=""))

    # Pass 1: bands whose rounded splits close (barrier groups match, within 1 s) define
    # the plans. Pass 2: other bands join a plan if every phase agrees: within 1 s where
    # the value came from the programmed-split line, within 3 s where it came from
    # force-off dots (which sit slightly off the split for coordinated phases). Anything
    # else stays its own, flagged plan -- values are never adjusted to make a check pass.
    allph = sorted(phases_seen)
    hard = lambda fl: [f for f in fl if not f.startswith("closes")]
    plans = {}
    sig = lambda s: tuple(s.get(p, 0) for p in allph)
    for r in recs:
        if r["kind"] != "plan" or hard(r["flags"]):
            continue
        lab = next((k for k, p in plans.items()
                    if all(abs(x - y) <= 1 for x, y in zip(sig(r["splits"]), p["sig"]))), None)
        if lab is None:
            lab = chr(ord("A") + len(plans))
            plans[lab] = {"sig": sig(r["splits"]), "cycle_s": r["cycle"], "splits_s": r["splits"],
                          "flags": r["flags"], "seen": []}
        r["label"] = lab
    for r in recs:
        if r["kind"] != "plan" or r["label"]:
            continue
        for lab, p in plans.items():
            ok, compared, unread = True, 0, []
            for i, ph in enumerate(allph):
                v, src, _ = r["raw"].get(ph, (None, "absent", 0))
                if src in ("none", "observed") and p["sig"][i]:
                    unread.append(f"P{ph}")          # unreadable, not a contradiction
                    continue
                tol = 1 if src == "programmed" else 3
                compared += 1
                if abs(r["splits"].get(ph, 0) - p["sig"][i]) > tol:
                    ok = False
                    break
            if ok and compared >= max(2, len(allph) - 2):
                r["label"] = lab
                r["note"] = "matched; some values from force-off dots" + \
                    (f"; {' '.join(unread)} unreadable" if unread else "")
                break
        if not r["label"]:
            lab = chr(ord("A") + len(plans))
            why = "unverified: read partly from force-off dots" if any(
                src.startswith("force") for _, src, _ in r["raw"].values()) else "unverified"
            plans[lab] = {"sig": sig(r["splits"]), "cycle_s": r["cycle"], "splits_s": r["splits"],
                          "flags": r["flags"] + [why], "seen": []}
            r["label"] = lab
    # free operation: one entry, with observed (not programmed) median phase times
    for r in recs:
        if r["kind"] == "free":
            if "Actuated" not in plans:
                plans["Actuated"] = {"sig": (), "cycle_s": "", "splits_s": {}, "observed_s": {},
                                     "flags": ["no programmed-split line readable: Free or an "
                                               "uncoordinated actuated plan (the chart's band label "
                                               "says which); values are observed median phase times"],
                                     "seen": []}
            for ph, (v, src, _) in r["raw"].items():
                if v is not None:
                    plans["Actuated"]["observed_s"].setdefault(ph, []).append(v)
            for ph, (v, src) in r["b"].get("maxout", {}).items():
                if v is not None:
                    plans["Actuated"].setdefault("max_obs", {}).setdefault(ph, []).append((v, src))
            r["label"] = "Actuated"
    if "Actuated" in plans:
        plans["Actuated"]["observed_s"] = {ph: round(float(np.median(v)))
                                           for ph, v in sorted(plans["Actuated"]["observed_s"].items())}
        mo = {}
        for ph, vs in sorted(plans["Actuated"].get("max_obs", {}).items()):
            hard = [v for v, src in vs if src == "max-out"]
            mo[ph] = {"s": round(float(np.median(hard if hard else [v for v, _ in vs]))),
                      "source": "max-out dots" if hard else "95th percentile of phase times (lower bound)"}
        plans["Actuated"]["max_obs"] = mo
    for r in recs:
        if r["label"]:
            plans[r["label"]]["seen"].append(f"{r['date']} {r['b']['start']}-{r['b']['end']}")
            for ph, t in r["b"].get("term", {}).items():
                if t.get("n", 0) >= 5:
                    plans[r["label"]].setdefault("_term", {}).setdefault(ph, []).append((t["n"], t))
    for k, p in plans.items():
        agg = {}
        for ph, lst in p.pop("_term", {}).items():
            tot = sum(n for n, _ in lst)
            agg[ph] = {c: round(sum(n * t.get(c, 0) for n, t in lst) / tot, 2) for c in ("gap", "max", "force", "fixed")}
        p["termination"] = agg

    rows, schedule = [], {}
    for r in recs:
        b = r["b"]
        schedule.setdefault(r["date"], []).append(
            {"start": b["start"], "end": b["end"], "minutes": b["minutes"],
             "kind": r["kind"], "plan": r["label"]})
        row = {"signal_id": sid, "date": r["date"], "start": b["start"], "end": b["end"],
               "minutes": b["minutes"], "kind": r["kind"], "plan": r["label"], "cycle_s": r["cycle"],
               "ring1_s": r["r1"], "ring2_s": r["r2"],
               "checks": "; ".join(r["flags"]) or "ok", "note": r["note"]}
        for ph in allph:
            v, src, cov = r["raw"].get(ph, (None, "absent", 0))
            row[f"P{ph}"] = r["splits"].get(ph, "")
            row[f"P{ph}_raw"] = "" if v is None else v
            row[f"P{ph}_src"] = src
        rows.append(row)

    clr = {}
    cfile = sdir / "clearance.json"
    if cfile.exists():
        clr = json.loads(cfile.read_text())

    if rows:
        with open(sdir / f"plans_{sid}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)

    out = {"signal_id": sid, "name": name,
           "source": "GDOT ATSPM Split Monitor (programmed splits) + Timing & Actuation (clearances)",
           "structure": {"ring1": list(RING1), "ring2": list(RING2),
                         "barriers": [[1, 2, 5, 6], [3, 4, 7, 8]],
                         "phases_with_charts": allph,
                         "note": "phases above 8 are listed but not part of the ring check"},
           "plans": {k: {"cycle_s": v["cycle_s"],
                         "splits_s": {str(p): x for p, x in sorted(v["splits_s"].items())},
                         **({"observed_s": {str(p): x for p, x in v["observed_s"].items()}}
                            if "observed_s" in v else {}),
                         **({"max_obs": {str(p): x for p, x in v["max_obs"].items()}}
                            if v.get("max_obs") else {}),
                         "termination": {str(p): x for p, x in sorted(v.get("termination", {}).items())},
                         "checks": v["flags"] or ["ok"], "seen": v["seen"]}
                     for k, v in plans.items()},
           "schedule": schedule, "clearance": clr}
    (sdir / f"timing_plan_{sid}.json").write_text(json.dumps(out, indent=1))
    write_md(sdir / f"timing_plan_{sid}.md", out)
    return len(plans), len(days)


def write_md(path, d):
    phs = d["structure"]["phases_with_charts"]
    L = [f"# Timing plans — signal {d['signal_id']} ({d['name']})", "",
         "Read from GDOT ATSPM Split Monitor (programmed split per phase, one full-day chart "
         "per date) and one 5-min Timing & Actuation window (clearances, lead/lag). "
         "Generated by `tools/atspm_plans.py`; plan letters group bands with the same "
         "splits (±1 s); the controller's own plan numbers are printed on the charts in "
         "`split_monitor/<date>/`.", ""]
    if not d["schedule"]:
        L += ["**No Split Monitor charts were returned for the requested date(s).** The portal "
              "has no phase data for this signal then.", ""]
    L += ["## Schedule", ""]
    for day, bands in d["schedule"].items():
        wd = dt.date.fromisoformat(day).strftime("%a")
        parts = []
        for b in bands:
            if b["kind"] in ("plan", "free"):
                parts.append(f"{b['start']}–{b['end']} **{b['plan']}**")
            elif b["kind"] == "no data":
                parts.append(f"{b['start']}–{b['end']} _no data_")
        L.append(f"- **{day} ({wd})**: " + " · ".join(parts))
        if bands and bands[0]["kind"] == "no data" and bands[0]["start"] == "00:01" and \
                any(b["kind"] == "plan" for b in bands[1:]):
            L.append("  - The first band may be a plan carried over from the previous day: the "
                     "portal doesn't draw the split line for it. Its band label on the chart "
                     "gives the plan number; often it is the same plan as the day's last band.")
    L += ["", "Times are read from the chart at ~1.2 min per pixel. Bands under "
          f"{MIN_BAND_MIN} min (plan transitions) are left out here; they are in the CSV.", ""]
    L += ["## Plans (programmed split, s = green + yellow + red clearance)", ""]
    hdr = "| Plan | Cycle | " + " | ".join(f"P{p}" for p in phs) + " | Checks |"
    L += [hdr, "|" + "---|" * (len(phs) + 3)]
    for k, p in d["plans"].items():
        vals = p.get("observed_s") or p["splits_s"]
        cells = [str(vals.get(str(ph), "")) or "–" for ph in phs]
        cells = ["–" if c == "0" else c for c in cells]
        if "observed_s" in p:
            cells = [f"~{c}" if c != "–" else c for c in cells]
        L.append(f"| {k} | {p['cycle_s'] or '–'} | " + " | ".join(cells) + f" | {'; '.join(p['checks'])} |")
    L += ["", "`–` = phase not served in that plan; `~` = observed, not programmed. Checks: in each "
          "barrier group (1+2 | 5+6 and 3+4 | 7+8) the two rings must sum to the same time, "
          "and the cycle is the sum of the two groups. Phases above 8 are shown but not checked. "
          "Values are rounded from the chart (0.52 s per pixel), so a 1 s miss is reported as "
          "rounding; raw reads are in the CSV. A failed check is reported, not corrected.", ""]
    c = d.get("clearance") or {}
    L += ["## Clearances and phase order", ""]
    if not c:
        L.append("_Not measured (run without `--no-clearance`)._")
    elif "error" in c:
        L.append(f"_Timing & Actuation window {c['window']} failed: {c['error']}_")
    else:
        L.append(f"From the Timing & Actuation window {c['window']}.")
        L += ["", "| | " + " | ".join(f"P{p}" for p in range(1, 9)) + " |", "|" + "---|" * 9]
        for key, lab in (("yellow", "Yellow (s)"), ("red_clear", "Red clearance (s)")):
            L.append(f"| {lab} | " + " | ".join(str(c[key].get(str(p), "")) for p in range(1, 9)) + " |")
        if c.get("lead"):
            L += ["", "Leading phase of each pair: " +
                  ", ".join(f"{pair} → P{ph} leads" for pair, ph in c["lead"].items())]
    L += ["", "## Not available from these charts", "",
          "Offsets, min/max green, passage (gap) times, pedestrian timing, and the controller's "
          "plan numbers (visible on the charts, not parsed)."]
    path.write_text("\n".join(L) + "\n")


# =========================================================================== main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("signals", nargs="+", help="ATSPM signal IDs")
    ap.add_argument("--date", nargs="*", default=[], help="dates YYYY-MM-DD (default: yesterday)")
    ap.add_argument("--no-clearance", action="store_true", help="skip the Timing & Actuation window")
    ap.add_argument("--sleep", type=float, default=5, help="seconds between requests (default 5)")
    ap.add_argument("--rebuild", action="store_true", help="only re-parse saved charts")
    a = ap.parse_args()
    dates = [dt.date.fromisoformat(d) for d in a.date] or [dt.date.today() - dt.timedelta(days=1)]

    for sid in a.signals:
        sdir = sig_dir(sid, "timing")
        (sdir / "split_monitor").mkdir(parents=True, exist_ok=True)
        name = tna.signal_name(sid)
        print(f"== Signal {sid}: {name}", flush=True)
        if not a.rebuild:
            for day in dates:
                ddir = sdir / "split_monitor" / str(day)
                if ddir.exists() and any(ddir.glob("Phase_*.jpg")):
                    print(f"   {day} split monitor cached")
                    continue
                t = time.time()
                try:
                    n = fetch_split_monitor(sid, day, ddir)
                    print(f"   {day} split monitor  {n} charts  {time.time() - t:.0f}s", flush=True)
                except Exception as e:
                    print(f"   {day} split monitor FAILED ({e})", flush=True)
                time.sleep(a.sleep)
            if not a.no_clearance and dates:
                ddir = sdir / "split_monitor" / str(dates[0])
                bands, _ = parse_day(ddir) if ddir.exists() else ([], [])
                t = time.time()
                c = clearance(sid, sdir, dates[0], bands) if bands else None
                if c:
                    (sdir / "clearance.json").write_text(json.dumps(c, indent=1))
                    print(f"   clearance window {c['window']}  "
                          f"{'FAILED ' + c['error'] if 'error' in c else 'ok'}  {time.time() - t:.0f}s",
                          flush=True)
        n_plans, n_days = build(sid, sdir, name)
        print(f"   -> {rel(sdir)}/timing_plan_{sid}.md  "
              f"({n_plans} distinct plans over {n_days} day(s))", flush=True)


if __name__ == "__main__":
    sys.exit(main())
