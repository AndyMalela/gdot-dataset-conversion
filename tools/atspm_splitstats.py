"""Read GDOT's own per-plan statistics from saved Split Monitor charts (OCR of the chart header).

Each Split Monitor chart (one per phase per day, saved by atspm_plans.py) prints, for every plan band:
85th-percentile split, average split, % force-offs (or max-outs), % gap-outs, % skips. These are exact
values computed by ATSPM from the controller's event log; the dots themselves can't be counted reliably
(they overlap at ~70 s per pixel). The header is enlarged 4x and read with RapidOCR; a band is kept only
as verified when the three percentages add up to 100 +- 0.5 (truncated text in narrow bands fails this).

    uv run python tools/atspm_splitstats.py 7065                 # every saved day
    uv run python tools/atspm_splitstats.py 7065 --exclude-from 2026-10-04   # keep a held-out period unread

Output: intersections/<signal>/timing/splitstats_<signal>.csv
    date, phase, band_start, band_end, plan_no, p85_split_s, avg_split_s, force_pct, gap_pct, skip_pct, check
"""
import argparse
import csv
import re
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import atspm_plans as AP  # noqa: E402
from paths import rel, sig_dir  # noqa: E402

HEADER = (120, 185, 1320, 248)       # x0, y0, x1, y1 of the statistics block (fixed chart layout)
SCALE = 4
ROWS = {"plan": 192, "p85": 202, "avg": 212, "force": 223, "gap": 233, "skip": 243}   # rule row of each text line
NUM = r"(\d{1,3}\.\d)"
PAT = {"p85": re.compile(NUM + r"\s*-\s*85"), "avg": re.compile(NUM + r"\s*Avg"),
       "force": re.compile(NUM + r"\s*%\s*(?:Force|Max)"), "gap": re.compile(NUM + r"\s*%\s*G"),
       "skip": re.compile(NUM + r"\s*%\s*Sk"), "plan": re.compile(r"P\w{2,3}\s*-?\s*(\d{1,3})")}

_ocr = None


def ocr():
    global _ocr
    if _ocr is None:
        from rapidocr_onnxruntime import RapidOCR
        _ocr = RapidOCR()
    return _ocr


def read_chart(path):
    rgb_img = Image.open(path).convert("RGB")
    rgb = np.asarray(rgb_img).astype(int)
    try:
        top, bottom, x0, x1 = AP.plot_frame(rgb.mean(2))
    except (ValueError, IndexError):
        return []                                   # no plot: phase never ran that day
    bands = AP.bands_from_background(rgb, top, bottom, x0, x1)
    hx0, hy0, hx1, hy1 = HEADER
    big = rgb_img.crop(HEADER).resize(((hx1 - hx0) * SCALE, (hy1 - hy0) * SCALE), Image.LANCZOS)
    res, _ = ocr()(np.asarray(big))
    cells = {}
    for box, txt, _conf in res or []:
        xs = [p[0] / SCALE + hx0 for p in box]
        ys = [p[1] / SCALE + hy0 for p in box]
        xc, yc = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        line = min(ROWS, key=lambda k: abs(ROWS[k] - 2 - yc))
        band = next((i for i, (a, b) in enumerate(bands) if a <= xc < b), None)
        if band is None or abs(ROWS[line] - 2 - yc) > 5:
            continue
        m = PAT[line].search(txt)
        if m:
            cells[(band, line)] = float(m.group(1))
    out = []
    for i, (a, b) in enumerate(bands):
        v = {k: cells.get((i, k)) for k in ROWS}
        r = {"band_start": AP.x_to_time(a, x0, x1), "band_end": AP.x_to_time(b, x0, x1),
             "plan_no": int(v["plan"]) if v["plan"] is not None else "",
             "p85_split_s": v["p85"], "avg_split_s": v["avg"], "force_pct": v["force"],
             "gap_pct": v["gap"], "skip_pct": v["skip"]}
        r["check"] = check(r)
        out.append(r)
    return out


def check(r):
    """ok: all three percentages read and they add up to 100 +- 0.5 (every cycle gapped out, was forced off
    or skipped), which also verifies the OCR. sum<100: read, but some cycles ended another way (e.g. the
    coordinated phases' 'unknown' terminations), so the reading is not verified. unread: something missing."""
    pct = [r["force_pct"], r["gap_pct"], r["skip_pct"]]
    if any(x in (None, "") for x in pct) or r["avg_split_s"] in (None, ""):
        return "unread"
    tot = sum(float(x) for x in pct)
    return "ok" if abs(tot - 100) <= 0.5 else ("sum<100" if tot < 100 else "sum>100")


def job(args):
    date, phase, path = args
    return [{"date": date, "phase": phase, **r} for r in read_chart(path)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("signal")
    ap.add_argument("--exclude-from", help="skip dates on/after this (YYYY-MM-DD), e.g. a locked test set")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--recheck", action="store_true", help="re-apply check() to the existing CSV, no OCR")
    a = ap.parse_args()
    out = sig_dir(a.signal, "timing") / f"splitstats_{a.signal}.csv"
    if a.recheck:
        rows = list(csv.DictReader(open(out)))
        for r in rows:
            r["check"] = check(r)
        write(out, rows)
        return
    root = sig_dir(a.signal, "timing") / "split_monitor"
    jobs = []
    for d in sorted(p for p in root.iterdir() if p.is_dir() and re.fullmatch(r"\d{4}-\d\d-\d\d", p.name)):
        if a.exclude_from and d.name >= a.exclude_from:
            continue
        for f in sorted(d.glob("Phase_*.jpg")):
            jobs.append((d.name, int(f.stem.split("_")[1]), f))
    with Pool(a.workers) as pool:
        rows = [r for rs in pool.map(job, jobs, chunksize=4) for r in rs]
    write(out, rows)


def write(out, rows):
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    ok = sum(r["check"] == "ok" for r in rows)
    print(f"{len(rows)} plan bands, {ok} read and checked ({100 * ok / len(rows):.0f} %) -> {rel(out)}")


if __name__ == "__main__":
    main()
