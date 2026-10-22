#!/usr/bin/env python3
"""
Infer time-of-day (TOD) timing plans from parsed Timing & Actuation windows.

Reads intersections/<signal>/timing/greens_<signal>.csv (written by
atspm_timing.py), and for every window estimates:
  - cycle length   median green-to-green spacing across phases
  - mode           "coord" if green starts repeat at a fixed cycle, else "free"
  - split / phase  ~90th percentile of (green + yellow + red clearance);
                   non-coordinated phases gap out early, so the upper end of
                   the observed range approximates the programmed split
Consecutive windows with the same mode, cycle (+-3 s) and splits (+-tol s)
are merged into one plan, and plans that recur on different days get the
same letter.

  python3 tools/tod_plans.py 7065
  python3 tools/tod_plans.py 7065 --split-tol 10

Output: plans_<signal>.csv and plans_<signal>.md next to the input.
Plan boundaries are only as precise as the window spacing (hourly by default).
"""
import argparse
import csv
import statistics as st
from collections import defaultdict
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import sig_dir  # noqa: E402


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def pct(xs, q):
    xs = sorted(xs)
    if not xs:
        return None
    k = (len(xs) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def phase_key(chart):
    return chart.replace("Phase_", "P").replace("Overlap_", "OL")


RINGS = {"P1": 1, "P2": 1, "P3": 1, "P4": 1, "P5": 2, "P6": 2, "P7": 2, "P8": 2}


COORD = ["P2", "P6"]          # set from --coord


def window_stats(rows):
    """rows: greens of one window -> dict(cycle, mode, splits, greens, coord)."""
    by = defaultdict(list)
    for r in rows:
        if r["chart"].startswith("Phase_"):
            by[phase_key(r["chart"])].append(r)
    spac = {p: [fnum(r["to_next_green_s"]) for r in g if fnum(r["to_next_green_s"])] for p, g in by.items()}
    meds = [st.median(v) for v in spac.values() if v]
    if not meds:
        return None
    cycle = st.median(meds)
    # coordinated: green starts land on multiples of one cycle (skips -> 2C)
    allsp = [x for v in spac.values() for x in v]
    on_grid = sum(min(abs(x - m * cycle) for m in (1, 2, 3)) <= 3 for x in allsp)
    mode = "coord" if allsp and on_grid / len(allsp) >= 0.8 else "free"
    coord = {RINGS[p]: p for p in COORD if p in by} if mode == "coord" else {}
    splits, greens, counts = {}, {}, {}
    for p, g in by.items():
        full = [r for r in g if r["truncated"] == "0"]
        gs = [fnum(r["green_s"]) for r in full]
        y = st.median([fnum(r["yellow_s"]) for r in g if fnum(r["yellow_s"])] or [0])
        rc = st.median([fnum(r["red_clear_s"]) for r in g if fnum(r["red_clear_s"])] or [0])
        if gs:
            # coordinated phase gets the slack -> its programmed split is the
            # low end; other phases gap out -> their split is the high end
            q = 0.1 if p in coord.values() else 0.9
            splits[p] = pct(gs, q) + y + rc
            greens[p] = st.median(gs)
        counts[p] = len(g)
    return {"cycle": cycle, "mode": mode, "splits": splits, "greens": greens,
            "counts": counts, "coord": coord}


def same_plan(a, b, tol):
    if a["mode"] != b["mode"]:
        return False
    if a["mode"] == "free":
        return True
    if abs(a["cycle"] - b["cycle"]) > 3:
        return False
    common = set(a["splits"]) & set(b["splits"])
    return all(abs(a["splits"][p] - b["splits"][p]) <= tol for p in common)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("signal")
    ap.add_argument("--split-tol", type=float, default=8, help="max split difference within a plan, s (default 8)")
    ap.add_argument("--coord", default="2,6", help="coordinated phases (default 2,6 — US main-street convention)")
    args = ap.parse_args()
    COORD[:] = [f"P{x.strip()}" for x in args.coord.split(",") if x.strip()]
    sdir = sig_dir(args.signal, "timing")
    rows = list(csv.DictReader(open(sdir / f"greens_{args.signal}.csv")))

    lens = defaultdict(int)
    for r in rows:
        lens[r.get("window_min", "15")] += 1
    main_len = max(lens, key=lens.get)               # e.g. ignore 5-min calibration windows
    win = defaultdict(list)
    for r in rows:
        if r.get("window_min", "15") == main_len:
            win[(r["date"], r["window_start"])].append(r)
    stats = {k: s for k, v in win.items() if (s := window_stats(v))}

    # segment each day into plans
    segs = []
    for date in sorted({d for d, _ in stats}):
        keys = sorted(k for k in stats if k[0] == date)
        cur = None
        for k in keys:
            s = stats[k]
            if cur and same_plan(cur["ref"], s, args.split_tol):
                cur["windows"].append(k)
            else:
                cur = {"date": date, "windows": [k], "ref": s}
                segs.append(cur)

    # pool windows per segment
    for sg in segs:
        ws = [stats[k] for k in sg["windows"]]
        sg["mode"] = ws[0]["mode"]
        sg["cycle"] = st.median([w["cycle"] for w in ws])
        phases = sorted({p for w in ws for p in w["splits"]}, key=lambda p: int(p[1:]))
        sg["coord"] = sorted({p for w in ws for p in w["coord"].values()}, key=lambda p: int(p[1:]))
        sg["splits"] = {p: (min if p in sg["coord"] else max)(w["splits"][p] for w in ws if p in w["splits"])
                        for p in phases}
        sg["greens"] = {p: st.median([w["greens"][p] for w in ws if p in w["greens"]]) for p in phases}

    # label recurring plans across days
    labels = []
    for sg in segs:
        for lab, ref in labels:
            if same_plan(ref, sg, args.split_tol):
                sg["plan"] = lab
                break
        else:
            sg["plan"] = "Free" if sg["mode"] == "free" else chr(ord("A") + sum(1 for l, _ in labels if l != "Free"))
            labels.append((sg["plan"], sg))

    phases = sorted({p for sg in segs for p in sg["splits"]}, key=lambda p: int(p[1:]))
    out = []
    for sg in segs:
        first, last = sg["windows"][0][1], sg["windows"][-1][1]
        r = {"date": sg["date"], "plan": sg["plan"], "from": first, "to_last_window": last,
             "n_windows": len(sg["windows"]), "mode": sg["mode"],
             "cycle_s": round(sg["cycle"], 1) if sg["mode"] == "coord" else "",
             "coord_phases": " ".join(sg["coord"])}
        for ring, ps in ((1, ["P1", "P2", "P3", "P4"]), (2, ["P5", "P6", "P7", "P8"])):
            r[f"ring{ring}_sum"] = round(sum(sg["splits"].get(p, 0) for p in ps), 1)
        for p in phases:
            r[f"{p}_split"] = round(sg["splits"][p], 1) if p in sg["splits"] else ""
            r[f"{p}_green_med"] = round(sg["greens"][p], 1) if p in sg["greens"] else ""
        out.append(r)
    with open(sdir / f"plans_{args.signal}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)

    # readable markdown
    name = ""
    info = sdir / "info.txt"
    if info.exists():
        for line in info.read_text().splitlines():
            if line.startswith("Intersection:"):
                name = line.split(":", 1)[1].strip()
    md = [f"# TOD plans — signal {args.signal} ({name})", "",
          "Split = green + yellow + red clearance: 90th percentile for actuated phases (they gap out), "
          "10th percentile for the coordinated phase (it absorbs the slack). Ring sums should be close to the "
          "cycle. Times are window starts, so plan boundaries are ±1 sampling interval.", ""]
    hdr = ["date", "plan", "windows", "mode", "cycle", "coord"] + phases + ["ring1 Σ", "ring2 Σ"]
    md += ["| " + " | ".join(hdr) + " |", "|" + "---|" * len(hdr)]
    for r, sg in zip(out, segs):
        span = r["from"] if r["n_windows"] == 1 else f"{r['from']}–{r['to_last_window']}"
        md.append("| " + " | ".join([r["date"], r["plan"], span, r["mode"], str(r["cycle_s"]), r["coord_phases"]] +
                                    [str(r[f"{p}_split"]) for p in phases] +
                                    [str(r["ring1_sum"]), str(r["ring2_sum"])]) + " |")
    (sdir / f"plans_{args.signal}.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
