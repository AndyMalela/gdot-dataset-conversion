"""Exact summary numbers printed on GDOT ATSPM charts, read by OCR, per requested window.

The portal returns chart images only, but several charts print exact per-phase / per-plan statistics as text
(probe 2026-11-20, atsc/probe_2026-11-20/README.md). Requesting short windows (e.g. 15 or 60 min) gives exact
numbers per window. One chart image = one phase (or approach).

    uv run python tools/atspm_charts.py 137 SplitFail --date 2026-03-10 --hours 6-21 --window 60
    uv run python tools/atspm_charts.py 137 PedDelay ApproachDelay PCD WaitTime --date 2026-03-10 2026-03-11
    uv run python tools/atspm_charts.py 137 --reread            # re-OCR every cached chart, rebuild the CSVs

Cache:  intersections/<id>/atspm/<metric>/<YYYYmmdd_HHMM>_<W>m/   payload.json, chart_<k>.jpg
Output: intersections/<id>/atspm/<metric>.csv   one row per chart (= phase/approach) per window:
        date, start, minutes, phase, title, n_plans, <metric fields>, ocr_ok
A field is left blank when OCR could not read it; ocr_ok = 1 only when every expected field was read.
Rounding is the portal's (e.g. Approach Delay prints whole seconds, PCD whole percent).
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import sig_dir  # noqa: E402

BASE = "https://traffic.dot.ga.gov/ATSPM/DefaultCharts"
UA = "Mozilla/5.0 (research data pull; ATSPM timing)"
HEADERS = {"Content-Type": "application/json; charset=utf-8", "X-Requested-With": "XMLHttpRequest", "User-Agent": UA}
PAUSE_S = 5                     # be polite: one request at a time

# metric -> (MetricTypeID, endpoint, extra payload, fields: name -> regex (first group = value))
NUM = r"(\d+(?:\.\d+)?)"
METRICS = {
    "SplitFail": (12, "GetSplitFailMetric",
                  {"FirstSecondsOfRed": "5", "ShowFailLines": True, "ShowAvgLines": True, "ShowPercentFailLines": True},
                  {"split_failures": (r"Total Split Failures\s*=\s*" + NUM, r"(?<![\d.%])" + NUM + r"SF\b")}),
    "ApproachDelay": (8, "GetApproachDelayMetric",
                      {"SelectedBinSize": "15", "ShowPlanStatistics": True, "ShowTotalDelayPerHour": True,
                       "ShowDelayPerVehicle": True},
                      # summary line first; the plan stripe ("4AD", "0.8TD") as fallback when OCR misses the line
                      {"delay_per_veh_s": (r"\(AD\)\s*=\s*" + NUM + r"\s*sec", r"(?<![\d.])" + NUM + r"AD\b"),
                       "total_delay_h": (r"\(TD\)\s*=\s*" + NUM + r"\s*hour", r"(?<![\d.])" + NUM + r"TD\b")}),
    "PCD": (6, "GetPCDMetric",
            {"SelectedBinSize": "15", "SelectedDotSize": "1", "SelectedLineSize": "1", "ShowPlanStatistics": True,
             "ShowVolumes": True},
            {"aog_pct": r"AoG\s*=\s*" + NUM + r"\s*%", "gt_pct": NUM + r"\s*%\s*GT", "platoon_ratio": NUM + r"\s*PR"}),
    "WaitTime": (32, "GetWaitTimeMetric", {"ShowPlanStripes": True},
                 {"avg_wait_s": r"Avg\s*Wait:?\s*" + NUM, "max_wait_s": r"Max\s*Wait:?\s*" + NUM}),
    "PedDelay": (3, "GetPedDelayMetric",
                 {"TimeBuffer": "15", "ShowPedBeginWalk": True, "ShowCycleLength": True, "ShowPercentDelay": True,
                  "ShowPedRecall": True, "PedRecallThreshold": "75"},
                 {"ped_presses": r"\(PP\)\s*=\s*" + NUM, "cycles_with_requests": r"\(CPR\)\s*=\s*" + NUM,
                  "buffered_presses": r"\(TBP\)\s*=\s*" + NUM, "min_delay_s": r"Min\s*Delay\s*=\s*" + NUM,
                  "max_delay_s": r"Max\s*Delay\s*=\s*" + NUM, "avg_delay_s": r"Average\s*Delay\s*\(AD\)\s*=\s*" + NUM,
                  "avg_cycle_s": r"avg\s*CL:?\s*" + NUM}),
}
HEADER_BOX = (0, 110, 1400, 285)     # title block + summary line + plan stripes, above the plot (1400 x 720 charts)
SCALE = 3
_ocr = None


def ocr():
    global _ocr
    if _ocr is None:
        from rapidocr_onnxruntime import RapidOCR
        _ocr = RapidOCR()
    return _ocr


# ---------------------------------------------------------------- fetch
def fmt(t):
    return t.strftime("%m/%d/%Y %I:%M %p")


def fetch(sig, metric, start, minutes):
    """Request one chart set for [start, start+minutes); cached. Returns the cache folder (or None if no charts)."""
    mid, endpoint, extra, _ = METRICS[metric]
    d = sig_dir(sig, "atspm") / metric / f"{start:%Y%m%d_%H%M}_{minutes}m"
    if d.exists() and (any(d.glob("chart_*.jpg")) or (d / "none.txt").exists()):
        return (d if any(d.glob("chart_*.jpg")) else None), False
    d.mkdir(parents=True, exist_ok=True)
    body = {"SignalID": str(sig), "StartDate": fmt(start), "EndDate": fmt(start + dt.timedelta(minutes=minutes)),
            "YAxisMax": "", "Y2AxisMax": "", "MetricTypeID": mid, **extra}
    (d / "payload.json").write_text(json.dumps(body, indent=1))
    html = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(f"{BASE}/{endpoint}", data=json.dumps(body).encode(), method="POST", headers=HEADERS)
            html = urllib.request.urlopen(req, timeout=400).read().decode("utf-8", "replace")
            break
        except Exception as e:                      # noqa: BLE001 — network: retry, then give up loudly
            if attempt == 2:
                raise
            time.sleep(30 * (attempt + 1))
    if "Request Rejected" in html:
        raise RuntimeError("rejected by the portal firewall")
    urls = re.findall(r'src="(https://[^"]+\.jpg)"', html)
    if not urls:
        (d / "none.txt").write_text(html[:2000])    # e.g. no detection for this metric at this signal
        return None, True
    for k, u in enumerate(urls):
        img = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=120).read()
        (d / f"chart_{k:02d}.jpg").write_bytes(img)
        time.sleep(1)
    return d, True


# ---------------------------------------------------------------- read
def header_text(path):
    """OCR the header block; returns the text lines top to bottom (boxes on one row joined left to right)."""
    im = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = HEADER_BOX
    x1, y1 = min(x1, im.width), min(y1, im.height)
    big = im.crop((x0, y0, x1, y1)).resize(((x1 - x0) * SCALE, (y1 - y0) * SCALE), Image.LANCZOS)
    res, _ = ocr()(np.asarray(big))
    boxes = sorted(((min(p[1] for p in b), min(p[0] for p in b), t) for b, t, _c in res or []))
    lines, cur, cur_y = [], [], None
    for y, x, t in boxes:
        if cur_y is not None and abs(y - cur_y) > 6 * SCALE:
            lines.append(" ".join(s for _, s in sorted(cur)))
            cur = []
        cur_y = y if not cur else cur_y
        cur.append((x, t))
    if cur:
        lines.append(" ".join(s for _, s in sorted(cur)))
    return lines


PARSER_V = 2                    # bump when read_chart changes, so cached OCR results are redone


def read_chart_cached(path, metric, force=False):
    """read_chart with the result stored next to the image (chart_xx.json)."""
    js = Path(path).with_suffix(".json")
    if js.exists() and not force:
        r = json.loads(js.read_text())
        if r.pop("_v", None) == PARSER_V:
            return r
    r = read_chart(path, metric)
    js.write_text(json.dumps({"_v": PARSER_V, **r}))
    return r


def read_chart(path, metric):
    lines = header_text(path)
    text = " | ".join(lines)
    row = {"title": "", "phase": "", "n_plans": len(re.findall(r"\bPlan\s*\w+", text))}
    m = re.search(r"Phase\s*(\d+)\s*:?\s*([^|]*)", text) or re.search(r"Phase\s*(\d+)", text)
    if m:
        row["phase"] = int(m.group(1))
        row["title"] = (m.group(2) if m.lastindex and m.lastindex > 1 else "").strip()
    fields = METRICS[metric][3]
    flat = text.replace(" ", "").replace("\uff08", "(").replace("\uff09", ")").replace("\uff1a", ":")
    ok = True
    for name, pats in fields.items():
        pats = (pats,) if isinstance(pats, str) else pats
        v = None
        for k, pat in enumerate(pats):
            if k > 0 and row["n_plans"] != 1:       # plan-stripe fallbacks equal the window total only with one plan
                break
            v = re.search(pat.replace(r"\s*", "").replace(r"\s", "").replace(" ", ""), flat, re.I)
            if v:
                break
        row[name] = float(v.group(1)) if v else ""
        ok &= v is not None
    row["ocr_ok"] = int(ok and row["phase"] != "")
    row["ocr_text"] = text
    return row


def plan_windows(sig, dates):
    """One window per timing-plan band of each day (atsc/sites/<id>/signal.json schedule_by_date), so every window
    holds a single plan and the chart's single plan stripe equals the window total. Yields (start, minutes)."""
    sched = json.loads((Path(__file__).resolve().parents[1] / "atsc" / "sites" / str(sig) / "signal.json")
                       .read_text())["schedule_by_date"]
    for d in dates:
        bands = sched.get(str(d))
        if not bands:
            continue
        starts = [dt.datetime.combine(d, dt.time(*map(int, b[0].split(":")))) for b in bands]
        ends = starts[1:] + [dt.datetime.combine(d, dt.time(23, 59))]
        for a, b in zip(starts, ends):
            if (b - a).total_seconds() >= 600:
                yield a, int((b - a).total_seconds() // 60)


def windows(dates, hours, minutes):
    h0, h1 = hours
    for d in dates:
        t = dt.datetime.combine(d, dt.time(h0))
        end = dt.datetime.combine(d, dt.time(0)) + dt.timedelta(hours=h1)
        while t < end:
            yield t
            t += dt.timedelta(minutes=minutes)


def rebuild_csv(sig, metric, force=False):
    root = sig_dir(sig, "atspm") / metric
    rows = []
    for d in sorted(p for p in root.iterdir() if p.is_dir()):
        m = re.match(r"(\d{8})_(\d{4})_(\d+)m", d.name)
        if not m:
            continue
        for img in sorted(d.glob("chart_*.jpg")):
            r = read_chart_cached(img, metric, force)
            rows.append({"date": f"{m.group(1)[:4]}-{m.group(1)[4:6]}-{m.group(1)[6:]}",
                         "start": f"{m.group(2)[:2]}:{m.group(2)[2:]}", "minutes": int(m.group(3)),
                         "chart": img.name, **r})
    out = sig_dir(sig, "atspm") / f"{metric}.csv"
    cols = ["date", "start", "minutes", "chart", "phase", "title", "n_plans", *METRICS[metric][3], "ocr_ok", "ocr_text"]
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    bad = sum(1 for r in rows if not r["ocr_ok"])
    print(f"{metric}: {len(rows)} charts -> {out} ({bad} not fully read)")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("signal")
    ap.add_argument("metrics", nargs="*", default=list(METRICS), help=f"any of {list(METRICS)}")
    ap.add_argument("--date", nargs="+", type=dt.date.fromisoformat, default=[])
    ap.add_argument("--hours", default="0-24", help="e.g. 6-21")
    ap.add_argument("--window", type=int, default=60, help="minutes per request")
    ap.add_argument("--reread", action="store_true", help="no requests; rebuild the CSVs from the cache")
    ap.add_argument("--force-ocr", action="store_true", help="with --reread: redo OCR even where a result is cached")
    ap.add_argument("--no-csv", action="store_true", help="only fetch (for long pulls; rebuild once at the end)")
    ap.add_argument("--plan-bands", action="store_true", help="one window per timing-plan band (overrides --hours/--window)")
    a = ap.parse_args()
    hours = tuple(int(x) for x in a.hours.split("-"))
    for metric in a.metrics:
        if not a.reread:
            wins = plan_windows(a.signal, a.date) if a.plan_bands else ((t, a.window) for t in windows(a.date, hours, a.window))
            for t, mins in wins:
                d, requested = fetch(a.signal, metric, t, mins)
                if requested:
                    print(f"  {metric} {t:%Y-%m-%d %H:%M} {'ok' if d else 'no chart'}", flush=True)
                    time.sleep(PAUSE_S)
        if not a.no_csv and (sig_dir(a.signal, "atspm") / metric).exists():
            rebuild_csv(a.signal, metric, force=a.force_ocr)


if __name__ == "__main__":
    main()
