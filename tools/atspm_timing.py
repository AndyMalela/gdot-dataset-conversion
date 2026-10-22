#!/usr/bin/env python3
"""
Extract signal timing from GDOT ATSPM "Timing and Actuation" charts.

The portal only returns chart images, so this script requests short windows
(default 15 min, ~0.86 s per pixel), downloads the charts, and reads the
coloured bars column by column: green / yellow / red clearance / red per
phase and overlap, plus pedestrian walk / clearance / don't-walk. No OCR —
chart identity comes from template-matching the header digits, and the time
axis comes from the requested window.

Sampling is meant for time-of-day (TOD) plans, not full days: by default one
15-min window at the start of every hour (24 requests/day, ~15 min/day).

Examples:
  python3 tools/atspm_timing.py 7065 --date 2026-05-08
  python3 tools/atspm_timing.py 7065 --date 2026-05-05 2026-05-06 --hours 6-21
  python3 tools/atspm_timing.py 7065 --date 2026-05-08 --times 07:30 17:15
  python3 tools/atspm_timing.py 7065 --rebuild      # re-parse saved images

Output: intersections/<signal>/timing/
  info.txt                       intersection, windows, phases found
  tod_<signal>.csv               one row per window: cycle + per-phase green/yellow/red-clear
  greens_<signal>.csv            one row per green interval (per phase/overlap)
  intervals_<signal>.csv         every coloured interval (vehicle + pedestrian)
  raw/<date>_<HHMM>_<W>min/      downloaded charts, renamed by phase

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
from pathlib import Path

import numpy as np
from PIL import Image

BASE = "https://traffic.dot.ga.gov/ATSPM/DefaultCharts"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import sig_dir, rel  # noqa: E402
UA = "Mozilla/5.0 (research data pull; ATSPM timing)"

# ---- chart geometry (constant for this renderer) --------------------------
PLOT_X_RIGHT_FALLBACK = 1357

# ---- legend colours -------------------------------------------------------
PALETTE = {
    "G_begin":   (60, 179, 113),   # phase begin green (event 1) until min green done
    "G_min":     (0, 250, 154),    # phase min complete (event 3)
    "OG":        (50, 205, 50),    # overlap green (61)
    "OG_trail":  (144, 238, 144),  # overlap trailing green (62)
    "Y":         (255, 255, 0),    # yellow (8, 63)
    "R_clr":     (178, 34, 34),    # red clearance (9, 64)
    "R":         (240, 128, 128),  # red (11, 65)
    "nodata":    (220, 220, 220),  # no vehicle display cycles found
    "walk":      (135, 206, 250),  # ped walk (21, 67)
    "ped_clr":   (0, 191, 255),    # ped clearance (22, 68)
    "dw":        (128, 128, 128),  # ped solid don't walk (23, 69)
    "black":     (0, 0, 0),        # grid lines
    "white":     (255, 255, 255),
}
NAMES = list(PALETTE)
PAL = np.array([PALETTE[n] for n in NAMES])
INTERVAL = {"G_begin": "green", "G_min": "green", "OG": "green", "OG_trail": "green",
            "Y": "yellow", "R_clr": "red_clear", "R": "red", "nodata": "no_data",
            "walk": "walk", "ped_clr": "ped_clear", "dw": "dont_walk"}
VEH = {"G_begin", "G_min", "OG", "OG_trail", "Y", "R_clr", "R"}
PED = {"walk", "ped_clr", "dw"}

# ---- header glyph templates (bold header font, 8 px wide x 11 rows) --------
_T = {
    "1": "..##....####......##......##......##......##......##......##......##....................",
    "2": "..####...##.##.......##......#......##.....##.....##.....##.....######..................",
    "3": ".###....##.##......##......##.....##........#.......##..##..#...#####...................",
    "4": "....##.....##.....###.....###....#..##...#..#...#######.....#.......#...................",
    "5": "#####...##......##......#####...##.##...#...##......##..##.##....###....................",
    "6": ".####...##..#...##......#.......#####...##.##...#...##..##.##....####...................",
    "7": "######......#......##......#.......#......##......#......##......##.....................",
    "8": ".####...##.##...##.##...##.##....###....##.##...#...##..##..#...#####...................",
    "P": "######..##...##.##...##.##...##.######..##......##......##......##......................",
    "O": ".#####..##...##.##....###.....###.....###.....####....####...##..######.................",
}
TEMPLATES = {k: np.array([c == "#" for c in v]).reshape(11, 8) for k, v in _T.items()}
DIGITS = [k for k in TEMPLATES if k.isdigit()]


# ===========================================================================
# image parsing
# ===========================================================================
def frame_lines(gray):
    """Rows that are full-width horizontal lines (plot frame / row separators)."""
    dark = (gray[:, 500:900] < 110).sum(1)
    return [y for y in range(50, gray.shape[0]) if dark[y] >= 390]


def match(bits, keys, max_shift=1):
    best, best_d = None, 1e9
    h, w = bits.shape
    for k in keys:
        t = TEMPLATES[k]
        for s in range(-max_shift, max_shift + 1):
            sh = np.zeros_like(t)
            if s >= 0:
                sh[:, s:] = t[:, :8 - s]
            else:
                sh[:, :8 + s] = t[:, -s:]
            d = int((sh != bits[:, :8]).sum())
            if d < best_d:
                best, best_d = k, d
    return best, best_d


def read_header(gray, top):
    """Return ('Phase'|'Overlap', number) from the bold header above the plot."""
    band = gray[top - 24:top - 1, :] < 128
    ys = np.where(band.any(1))[0]
    xs = np.where(band.any(0))[0]
    if len(ys) == 0:
        return None, None
    y0 = top - 24 + ys.min()
    b = gray[y0:y0 + 11, :] < 128
    left, right = xs.min(), xs.max()
    kind_ch, kd = match(b[:, left:left + 8], ["P", "O"])
    kind = {"P": "Phase", "O": "Overlap"}[kind_ch] if kd < 25 else None
    # digits sit just before the fixed " (Raw Data)" suffix; read right-to-left
    cols = b.any(0)
    digits, x_end = [], right - 58
    for _ in range(2):
        x = x_end - 8
        while x <= x_end and not cols[x]:
            x += 1
        if x > x_end:
            break
        d, dd = match(b[:, x:x + 8], DIGITS)
        if dd > 20:
            break
        digits.insert(0, d)
        x_end = x - 1
        if not cols[x - 2] and not cols[x - 1]:
            break
    num = int("".join(digits)) if digits else None
    return kind, num


ALLOWED = {
    "Phase":   {"G_begin", "G_min", "Y", "R_clr", "R", "nodata", "black", "white"},
    "Overlap": {"OG", "OG_trail", "Y", "R_clr", "R", "nodata", "black", "white"},
    "ped":     {"walk", "ped_clr", "dw", "nodata", "black", "white"},
    None:      set(NAMES),
}


def column_colours(rgb_band):
    return np.median(rgb_band, axis=0)                      # (W, 3)


def classify(med, allowed):
    """Nearest legend colour per column, restricted to the allowed set."""
    idx = [i for i, n in enumerate(NAMES) if n in allowed]
    d = ((med[:, None, :] - PAL[None, idx, :]) ** 2).sum(2)
    return [NAMES[idx[j]] for j in d.argmin(1)]


def runs(lab, med):
    """Run-length encode with sub-pixel boundaries.

    Grid lines are absorbed into the left neighbour. Each boundary between
    runs A|B is refined from the blended pixels around it: a pixel whose
    colour is a fraction t of the way from A to B contributes (1 - t) of a
    pixel to A. JPEG blur then averages out instead of costing whole pixels.
    """
    lab = list(lab)
    for i, v in enumerate(lab):
        if v == "black" and i > 0:
            lab[i] = lab[i - 1]
    raw, s = [], 0
    for i in range(1, len(lab) + 1):
        if i == len(lab) or lab[i] != lab[s]:
            raw.append([lab[s], s, i])
            s = i
    bounds = [0.0]
    for k in range(1, len(raw)):
        (a, sa, _), (b, _, eb) = raw[k - 1], raw[k]
        i = raw[k][1]
        A, B = np.array(PALETTE[a], float), np.array(PALETTE[b], float)
        AB = B - A
        x0, x1 = max(i - 2, sa), min(i + 2, eb)
        p = float(x0)
        for x in range(x0, x1):
            c = med[x]
            if c.sum() < 150:                                # grid line pixel
                t = 0.0 if x < i else 1.0
            else:
                t = float(np.clip(np.dot(c - A, AB) / max(np.dot(AB, AB), 1.0), 0, 1))
            p += 1.0 - t
        bounds.append(min(max(p, bounds[-1]), float(eb)))
    bounds.append(float(len(lab)))
    n = len(lab)
    return [[raw[k][0], bounds[k], bounds[k + 1], raw[k][1] <= 2, raw[k][2] >= n - 2]
            for k in range(len(raw)) if raw[k][2] - raw[k][1] > 1 or 2 < raw[k][1] < n - 3]


def parse_chart(path, win_start, win_min):
    """Parse one chart image -> dict(kind, num, rows=[(type, intervals)])."""
    im = Image.open(path).convert("RGB")
    rgb = np.asarray(im).astype(int)
    gray = rgb.mean(2)
    lines = frame_lines(gray)
    if len(lines) < 2:
        return None
    kind, num = read_header(gray, lines[0])

    # time axis: first tick under the plot = window start, frame right edge = end
    yb = lines[-1]
    ticks = np.where(gray[yb + 1, 280:1380] < 128)[0] + 280
    x_left = int(ticks[0]) if len(ticks) else 305
    xr = np.where(gray[lines[0]] < 110)[0]
    x_right = int(xr.max()) + 1 if len(xr) else PLOT_X_RIGHT_FALLBACK
    sec_per_px = win_min * 60.0 / (x_right - x_left)

    # rows: the first row with signal colours is the Vehicle Signal Display;
    # later rows with signal colours are detector rows drawn over the same
    # background (skipped); rows of ped colours are Pedestrian Intervals.
    rows, have_vsd = [], False
    for a, b in zip(lines[:-1], lines[1:]):
        h = b - a - 1
        if h < 6:
            continue
        y0, y1 = a + 1 + h // 4, b - h // 4
        med = column_colours(rgb[y0:y1, x_left:x_right])
        lab = classify(med, ALLOWED[None])
        n = len(lab)
        veh = sum(v in VEH for v in lab)
        ped = sum(v in PED for v in lab)
        if veh > 0.6 * n and not have_vsd:
            rtype, have_vsd = "vehicle", True
            lab = classify(med, ALLOWED[kind])
        elif ped > 0.6 * n:
            rtype = "ped"
            lab = classify(med, ALLOWED["ped"])
        else:
            continue
        ivs = []
        for name, s, e, at_start, at_end in runs(lab, med):
            if name not in INTERVAL:
                continue
            t0 = win_start + dt.timedelta(seconds=s * sec_per_px)
            t1 = win_start + dt.timedelta(seconds=e * sec_per_px)
            ivs.append({"cls": name, "interval": INTERVAL[name], "t0": t0, "t1": t1,
                        "dur": (e - s) * sec_per_px, "trunc": int(at_start or at_end)})
        rows.append((rtype, ivs))
    return {"kind": kind, "num": num, "rows": rows, "sec_per_px": sec_per_px}


def merge_greens(ivs):
    """Merge adjacent green sub-intervals (begin + min-complete) into one green."""
    out = []
    for iv in ivs:
        if out and iv["interval"] == "green" and out[-1]["interval"] == "green":
            g = out[-1]
            g["parts"].append(iv["cls"])
            g["t1"], g["dur"] = iv["t1"], g["dur"] + iv["dur"]
            g["trunc"] = max(g["trunc"], iv["trunc"])
        else:
            iv = dict(iv, parts=[iv["cls"]], first_dur=iv["dur"])
            out.append(iv)
    for g in out:
        # min green = the leading begin-green block, when followed by min-complete
        ok = g["interval"] == "green" and g["parts"][:2] == ["G_begin", "G_min"] and not g["trunc"]
        g["min_green"] = g["first_dur"] if ok else None
    return out


# ===========================================================================
# server
# ===========================================================================
def post_json(url, payload, timeout=180):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST",
                                 headers={"Content-Type": "application/json; charset=utf-8",
                                          "X-Requested-With": "XMLHttpRequest", "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "X-Requested-With": "XMLHttpRequest"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def signal_name(sid):
    try:
        return get(f"{BASE}/GetSignalLocation?signalID={sid}").decode().strip() or "?"
    except Exception:
        return "?"


def fmt(t):
    return t.strftime("%m/%d/%Y %I:%M %p")


def fetch_window(sid, start, win_min, outdir, retries=3):
    payload = {
        "SignalID": str(sid), "StartDate": fmt(start),
        "EndDate": fmt(start + dt.timedelta(minutes=win_min)), "MetricTypeID": 17,
        "ShowLegend": False, "ShowHeaderForEachPhase": True, "CombineLanesForEachGroup": False,
        "DotAndBarSize": "6", "PhaseFilter": "", "PhaseEventCodes": "",
        "GlobalCustomEventCodes": "", "GlobalCustomEventParams": "",
        "ShowAllLanesInfo": False, "ShowLinesStartEnd": False, "ShowEventPairs": False,
        "ShowRawEventData": True, "ShowPermissivePhases": True, "ExtendVsdSearch": "5",
        "ShowVehicleSignalDisplay": True, "ShowPedestrianIntervals": True,
        "ExtendStartStopSearch": "2", "ShowPedestrianActuation": True,
        "ShowStopBarPresence": False, "ShowLaneByLaneCount": False,
        "ShowAdvancedDilemmaZone": False, "ShowAdvancedCount": False, "AdvancedOffset": "0",
    }
    for k in range(retries):
        try:
            html = post_json(f"{BASE}/GetTimingAndActuations", payload)
            urls = re.findall(r'src="(https://[^"]+\.jpg)"', html)
            if not urls:
                return "no_charts", 0
            # download into a temp dir and rename when complete, so an
            # interrupted run never leaves a half-filled window that looks cached
            tmp = outdir.with_name(outdir.name + ".part")
            tmp.mkdir(parents=True, exist_ok=True)
            for i, u in enumerate(urls, 1):
                (tmp / f"{i:02d}.jpg").write_bytes(get(u))
            tmp.rename(outdir)
            return "ok", len(urls)
        except Exception as e:
            err = str(e)
            time.sleep(10 * (k + 1))
    return f"error: {err[:60]}", 0


# ===========================================================================
# per-window parse -> records
# ===========================================================================
def parse_window(wdir, win_start, win_min):
    """Parse all charts in one window dir; rename files by phase. Returns charts list."""
    charts, seen = [], {}
    for p in sorted(wdir.glob("*.jpg")):
        if p.stem.endswith("_dup"):
            continue
        try:
            c = parse_chart(p, win_start, win_min)
        except Exception:
            c = None
        if not c or not c["rows"]:
            continue                                   # legend or unreadable
        label = f"{c['kind'] or 'Unknown'}_{c['num'] if c['num'] is not None else p.stem}"
        veh = [r for t, r in c["rows"] if t == "vehicle"]
        sig = [iv["t0"] for iv in merge_greens(veh[0]) if iv["interval"] == "green"] if veh else []
        if label in seen:
            prev = seen[label]
            same = len(prev) == len(sig) and all(abs((a - b).total_seconds()) <= 2 for a, b in zip(prev, sig))
            if same:                                   # duplicate chart (e.g. permissive copy)
                dup = p.with_name(f"{label}_dup.jpg")
                if p.name[:2].isdigit() and not dup.exists():
                    p.rename(dup)
                continue
            label += "b"
        seen[label] = sig
        new = p.with_name(f"{label}.jpg")
        if p.name[:2].isdigit() and not new.exists():
            p.rename(new)
        c["label"] = label
        charts.append(c)
    return charts


def window_records(sid, date, win_start, win_min, charts):
    intervals, greens = [], []
    for c in charts:
        for rtype, ivs in c["rows"]:
            if rtype == "vehicle":
                ivs = merge_greens(ivs)
            for iv in ivs:
                intervals.append({
                    "signal_id": sid, "date": date, "window_start": win_start.strftime("%H:%M"),
                    "chart": c["label"], "row": rtype, "interval": iv["interval"],
                    "start": iv["t0"].strftime("%H:%M:%S.%f")[:10],
                    "end": iv["t1"].strftime("%H:%M:%S.%f")[:10],
                    "duration_s": round(iv["dur"], 1), "truncated": iv["trunc"]})
            if rtype != "vehicle":
                continue
            for i, iv in enumerate(ivs):
                if iv["interval"] != "green":
                    continue
                nxt = [x for x in ivs[i + 1:]]
                yel = next((x for x in nxt[:1] if x["interval"] == "yellow"), None)
                rc = next((x for x in nxt[1:2] if x["interval"] == "red_clear"), None)
                ng = next((x for x in nxt if x["interval"] == "green"), None)
                greens.append({
                    "signal_id": sid, "date": date, "window_start": win_start.strftime("%H:%M"),
                    "window_min": win_min, "chart": c["label"], "green_start": iv["t0"].strftime("%H:%M:%S.%f")[:10],
                    "green_s": round(iv["dur"], 1),
                    "min_green_s": round(iv["min_green"], 1) if iv.get("min_green") else "",
                    "yellow_s": round(yel["dur"], 1) if yel and not yel["trunc"] else "",
                    "red_clear_s": round(rc["dur"], 1) if rc and not rc["trunc"] else "",
                    # spacing only from a green whose start is inside the window
                    "to_next_green_s": round((ng["t0"] - iv["t0"]).total_seconds(), 1)
                    if ng and (iv["t0"] - win_start).total_seconds() > 3 else "",
                    "truncated": iv["trunc"]})
    return intervals, greens


def med(xs):
    xs = sorted(x for x in xs if x != "" and x is not None)
    if not xs:
        return ""
    n = len(xs)
    return round(xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2, 1)


def tod_row(sid, date, win_start, win_min, charts, greens, intervals):
    row = {"signal_id": sid, "date": date,
           "weekday": dt.date.fromisoformat(date).strftime("%a"),
           "window_start": win_start.strftime("%H:%M"), "window_min": win_min}
    labels = [c["label"] for c in charts if any(t == "vehicle" for t, _ in c["rows"])]
    spacings, total_walks = [], 0
    for lab in labels:
        g = [x for x in greens if x["chart"] == lab]
        full = [x for x in g if not x["truncated"]]
        sp = [x["to_next_green_s"] for x in g if x["to_next_green_s"] != ""]
        if lab.startswith("Phase") and len(sp) >= 1:
            spacings.append(med(sp))
        key = lab.replace("Phase_", "P").replace("Overlap_", "OL")
        walks = [x for x in intervals if x["chart"] == lab and x["row"] == "ped"
                 and x["interval"] == "walk" and x["duration_s"] >= 2]
        if any(x["chart"] == lab and x["row"] == "ped" for x in intervals):
            row[f"{key}_walks"] = len(walks)
            total_walks += len(walks)
        row[f"{key}_n"] = len(g)
        row[f"{key}_green_med"] = med([x["green_s"] for x in full])
        row[f"{key}_green_max"] = max([x["green_s"] for x in full], default="")
        row[f"{key}_yellow"] = med([x["yellow_s"] for x in g])
        row[f"{key}_red_clear"] = med([x["red_clear_s"] for x in g])
    row["cycle_s_est"] = med(spacings)
    row["ped_walks"] = total_walks
    return row


# ===========================================================================
# main
# ===========================================================================
def window_starts(dates, args):
    if args.times:
        tods = [dt.time.fromisoformat(t) for t in args.times]
    else:
        h0, h1 = (int(x) for x in args.hours.split("-"))
        tods = [dt.time(h, args.offset) for h in range(h0, h1 + 1)]
    return [dt.datetime.combine(d, t) for d in dates for t in tods]


def write_csv(path, rows, fields=None):
    if not rows:
        return
    if fields is None:
        fields = []
        for r in rows:
            for k in r:
                if k not in fields:
                    fields.append(k)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, restval="")
        w.writeheader()
        w.writerows(rows)


def rebuild(sid, sdir, name):
    all_iv, all_g, tod, phases = [], [], [], set()
    wdirs = sorted(d for d in (sdir / "raw").glob("*_*_*min") if d.is_dir())
    for wd in wdirs:
        date_s, hhmm, w = wd.name.split("_")
        win_min = int(w.replace("min", ""))
        ws = dt.datetime.strptime(date_s + hhmm, "%Y-%m-%d%H%M")
        charts = parse_window(wd, ws, win_min)
        if not charts:
            continue
        iv, g = window_records(sid, date_s, ws, win_min, charts)
        all_iv += iv
        all_g += g
        tod.append(tod_row(sid, date_s, ws, win_min, charts, g, iv))
        phases |= {c["label"] for c in charts}
    write_csv(sdir / f"intervals_{sid}.csv", all_iv)
    write_csv(sdir / f"greens_{sid}.csv", all_g)
    # order TOD columns: id/time, cycle, then phases in natural order
    def pkey(k):
        m = re.match(r"(P|OL)(\d+)(b?)_(\w+)", k)
        order = ["n", "green_med", "green_max", "yellow", "red_clear", "walks"]
        return (m.group(1) != "P", int(m.group(2)), m.group(3), order.index(m.group(4))) if m else (9, 0, "", 0)
    base = ["signal_id", "date", "weekday", "window_start", "window_min", "cycle_s_est", "ped_walks"]
    rest = sorted({k for r in tod for k in r} - set(base), key=pkey)
    write_csv(sdir / f"tod_{sid}.csv", tod, base + rest)

    dates = sorted({r["date"] for r in tod})
    nat = sorted(phases, key=lambda s: (not s.startswith("Phase"), int(re.sub(r"\D", "", s) or 0), s))
    (sdir / "info.txt").write_text(
        f"Signal:        {sid}\n"
        f"Intersection:  {name}\n"
        f"Source:        GDOT ATSPM, Timing and Actuation charts ({BASE})\n"
        f"Windows:       {len(tod)} parsed across {len(dates)} day(s): {', '.join(dates)}\n"
        f"Charts found:  {' '.join(nat)}\n"
        f"Resolution:    ~{tod and round(60 * tod[0]['window_min'] / 1052, 2)} s per pixel\n"
        f"Notes:         durations are quantised to the pixel size; truncated=1 means the\n"
        f"               interval touches the window edge (excluded from medians).\n"
        f"               cycle_s_est = median green-start spacing across phases.\n"
        f"Updated:       {dt.datetime.now():%Y-%m-%d %H:%M}\n")
    return len(tod)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("signals", nargs="+", help="ATSPM signal IDs, e.g. 7065")
    ap.add_argument("--date", nargs="*", default=[], help="dates YYYY-MM-DD (default: yesterday)")
    ap.add_argument("--hours", default="0-23", help="hour range to sample, e.g. 6-21 (default 0-23)")
    ap.add_argument("--offset", type=int, default=0, help="minute past each hour to start (default 0)")
    ap.add_argument("--times", nargs="*", help="explicit window start times HH:MM (overrides --hours)")
    ap.add_argument("--window", type=int, default=15, choices=[5, 10, 15], help="minutes per chart")
    ap.add_argument("--sleep", type=float, default=5, help="seconds between requests (default 5)")
    ap.add_argument("--rebuild", action="store_true", help="only re-parse saved images, no downloads")
    args = ap.parse_args()

    dates = [dt.date.fromisoformat(d) for d in args.date] or [dt.date.today() - dt.timedelta(days=1)]
    for sid in args.signals:
        sdir = sig_dir(sid, "timing")
        (sdir / "raw").mkdir(parents=True, exist_ok=True)
        name = signal_name(sid)
        print(f"== Signal {sid}: {name}")
        if not args.rebuild:
            todo = []
            for ws in window_starts(dates, args):
                wd = sdir / "raw" / f"{ws:%Y-%m-%d_%H%M}_{args.window}min"
                if not (wd.exists() and any(wd.glob("*.jpg"))):
                    todo.append((ws, wd))
            n_all = len(window_starts(dates, args))
            print(f"   {n_all} window(s), {n_all - len(todo)} cached, {len(todo)} to download "
                  f"(~{round(len(todo) * (35 + args.sleep) / 60)} min)")
            for i, (ws, wd) in enumerate(todo, 1):
                t = time.time()
                status, n = fetch_window(sid, ws, args.window, wd)
                print(f"   [{i}/{len(todo)}] {ws:%Y-%m-%d %a %H:%M}  {status}  {n} charts  "
                      f"{time.time() - t:.0f}s", flush=True)
                if i < len(todo):
                    time.sleep(args.sleep)
        n = rebuild(sid, sdir, name)
        print(f"   -> {rel(sdir)}/tod_{sid}.csv  ({n} windows parsed)")


if __name__ == "__main__":
    sys.exit(main())
