"""7111 Step 3 (MODEL_LOG.md, rule + amendment 1): through/right split of the driveway (P4, WB_TR) and Collier
(P8, EB_TR) shared lanes from exit-zone hits timed against the phase display. Train days only.

    uv run python atsc/sites/7111/exit_split.py        -> atsc/sites/7111/turn_split/exit_split.{json,md}

Charts: tools/cache/tna_lanecheck/7111_<day>_<hhmm>00_5m_p1234568/0N.jpg, phases 1,2,3,4,5,6,8 -> files 01..07.
Rows used (top to bottom, from the format test window):
  04 (P4): ch11, ch12, ch85, ch91 = west exit (Collier out), ch86 = driveway TR count
  07 (P8): ch31, ch123 = east exit (driveway in), ch117 = Collier TR count
  06 (P6): ch107 = north exit lane 1, ch101, ch108 = north exit lane 2, ch102, ch21
  03 (P3): ch9, ch10, ch81, ch82 = Collier left counts
A window is dropped (and listed) when a chart is missing or its row count differs.
"""
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
import tna_read  # noqa: E402

CACHE = REPO / "tools/cache/tna_lanecheck"
DAYS = ["2026-08-31", "2026-09-02", "2026-09-04", "2026-09-09", "2026-09-11", "2026-09-15", "2026-09-17",
        "2026-09-21", "2026-09-23", "2026-09-25", "2026-09-29", "2026-10-06", "2026-10-08"]
TIMES = ["07:00", "08:30", "10:00", "12:00", "13:30", "15:00", "17:00", "18:30"]
EXTRA = [("2026-09-16", "12:00")]                      # format test window (train day)
NROWS = {"03": 4, "04": 5, "06": 5, "07": 3}
LAG, START = 3.0, 1.0
OUT = HERE / "turn_split"


def train_guard(days):
    sp = json.load(open(HERE / "split.json"))
    lo, hi = sp["sets"]["train"]["from"], sp["sets"]["train"]["to"]
    bad = [d for d in days if not (lo <= d <= hi) or d in sp["holidays"]]
    if bad:
        raise SystemExit(f"non-train days requested: {bad}")


def episodes(disp):
    """[(green_start, clearance_end)] of complete green-yellow-red episodes inside the chart"""
    eps, i = [], 0
    while i < len(disp):
        a, b, s = disp[i]
        if s == "G":
            gs = a
            j = i
            while j < len(disp) and disp[j][2] == "G":
                j += 1
            k = j
            while k < len(disp) and disp[k][2] in ("Y", "R"):
                k += 1
            if j < len(disp) and k > j and k < len(disp) and gs > 0.5 and disp[k - 1][2] == "R":
                eps.append((gs, disp[k - 1][1]))
            i = max(k, i + 1)
        else:
            i += 1
    return eps


def hits(row, a, b):
    return sum(a < t <= b for t in row)


def window(day, hhmm):
    d = CACHE / f"7111_{day.replace('-', '')}_{hhmm.replace(':', '')}00_5m_p1234568"
    charts = {}
    for f, n in NROWS.items():
        p = d / f"{f}.jpg"
        if not p.exists():
            return None, "missing chart"
        r = tna_read.read(p)
        if len(r["rows"]) != n:
            return None, f"{f}: {len(r['rows'])} rows, expected {n}"
        charts[f] = r
    return charts, ""


def analyse(c):
    p3, p4, p8 = (episodes(c[f]["phase_display"]) for f in ("03", "04", "07"))
    west, dw_cnt = c["04"]["rows"][3], c["04"]["rows"][4]
    east, co_cnt = c["07"]["rows"][1], c["07"]["rows"][2]
    north = sorted(c["06"]["rows"][0] + c["06"]["rows"][2])
    col_l = sorted(c["03"]["rows"][2] + c["03"]["rows"][3])
    w4 = [(g + START, e + LAG) for g, e in p4]
    w8 = [(g + START, e + LAG) for g, e in p8]
    w3 = [(g + START, e + LAG) for g, e in p3]
    r = {"p4": [], "p8": [], "p3": [], "rtor_hits": 0, "rtor_s": 0.0}
    # rule 2: west-exit hits during P3-only time (after the P4 service window), lagged
    for g, e in p3:
        a = g + LAG
        for (x, y) in w4:
            if x <= a < y:
                a = y
        b = e + LAG
        if b > a:
            r["rtor_hits"] += hits(west, a, b)
            r["rtor_s"] += b - a
    for wins, ex, cnt, key in ((w4, west, dw_cnt, "p4"), (w8, east, co_cnt, "p8"), (w3, north, col_l, "p3")):
        for k in range(1, len(wins)):
            a, b = wins[k]
            r[key].append({"exit": hits(ex, a, b), "len": b - a, "arrivals": hits(cnt, wins[k - 1][1], b)})
    return r


def pooled(rows, rate, sub):
    ex = sum(x["exit"] for x in rows)
    ln = sum(x["len"] for x in rows)
    arr = sum(x["arrivals"] for x in rows)
    thr = ex - (rate * ln if sub else 0.0)
    return thr, arr, (thr / arr if arr else float("nan"))


def main():
    train_guard(DAYS + [d for d, _ in EXTRA])
    per, dropped = [], []
    for day, hh in [(d, t) for d in DAYS for t in TIMES] + EXTRA:
        c, why = window(day, hh)
        if c is None:
            dropped.append((day, hh, why))
            continue
        per.append((day, hh, analyse(c)))
    rate = sum(x["rtor_hits"] for *_, x in per) / max(1e-9, sum(x["rtor_s"] for *_, x in per))

    def shares(sel):
        p4 = [c for *_, x in sel for c in x["p4"]]
        p8 = [c for *_, x in sel for c in x["p8"]]
        p3 = [c for *_, x in sel for c in x["p3"]]
        rt = sum(x["rtor_hits"] for *_, x in sel) / max(1e-9, sum(x["rtor_s"] for *_, x in sel))
        d_thr, d_arr, d_sh = pooled(p4, rt, True)
        cu = pooled(p8, rt, False)
        cl = pooled(p8, rt, True)
        n_ex = sum(c["exit"] for c in p3)
        n_ar = sum(c["arrivals"] for c in p3)
        return {"driveway_through_share": d_sh, "driveway_cycles": len(p4), "driveway_arrivals": d_arr,
                "driveway_through": d_thr, "collier_through_share_upper": cu[2], "collier_through_share_lower": cl[2],
                "collier_cycles": len(p8), "collier_arrivals": cu[1], "sb_rtor_per_h": rt * 3600,
                "detection_ratio_collier_left": n_ex / n_ar if n_ar else float("nan"), "p3_cycles": len(p3)}

    allr = shares(per)
    days = sorted({d for d, *_ in per})
    random.seed(7111)
    boot = []
    for _ in range(2000):
        pick = [random.choice(days) for _ in days]
        sel = [x for dd in pick for x in per if x[0] == dd]
        boot.append(shares(sel))

    def ci(k):
        v = sorted(b[k] for b in boot if b[k] == b[k])
        return (v[int(.025 * len(v))], v[int(.975 * len(v)) - 1]) if v else (None, None)

    keys = ["driveway_through_share", "collier_through_share_upper", "collier_through_share_lower",
            "detection_ratio_collier_left", "sb_rtor_per_h"]
    by_time = {t: shares([x for x in per if x[1] == t]) for t in TIMES}
    OUT.mkdir(exist_ok=True)
    res = {"pooled": allr, "ci95_bootstrap_days": {k: ci(k) for k in keys}, "by_time": by_time,
           "windows_used": len(per), "days": days, "dropped": dropped,
           "rule": "MODEL_LOG.md Step 3 + amendment 1", "lag_s": LAG, "start_s": START}
    json.dump(res, open(OUT / "exit_split.json", "w"), indent=1)
    f = lambda v: "—" if v is None or v != v else f"{v:.2f}"  # noqa: E731
    md = ["# 7111 through/right split from exit zones (Step 3)", "",
          f"Train days {len(days)}, windows used {len(per)}, dropped {len(dropped)}. Bootstrap over days (2,000).", "",
          "| quantity | pooled | 95 % CI |", "|---|---|---|"]
    for k in keys:
        lo, hi = ci(k)
        md.append(f"| {k} | {f(allr[k])} | {f(lo)} – {f(hi)} |")
    md += ["", f"Driveway: {allr['driveway_cycles']} cycles, {allr['driveway_arrivals']} TR-lane arrivals; Collier: "
           f"{allr['collier_cycles']} cycles, {allr['collier_arrivals']} arrivals; Collier-left check: "
           f"{allr['p3_cycles']} cycles.", "", "By time of day (pooled within the window):", "",
           "| window | driveway through share | Collier through share (lower – upper) | SB RTOR veh/h | detection ratio |",
           "|---|---|---|---|---|"]
    for t, s in by_time.items():
        md.append(f"| {t} | {f(s['driveway_through_share'])} | {f(s['collier_through_share_lower'])} – "
                  f"{f(s['collier_through_share_upper'])} | {f(s['sb_rtor_per_h'])} | "
                  f"{f(s['detection_ratio_collier_left'])} |")
    if dropped:
        md += ["", "Dropped windows: " + "; ".join(f"{d} {t} ({w})" for d, t, w in dropped)]
    (OUT / "exit_split.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
