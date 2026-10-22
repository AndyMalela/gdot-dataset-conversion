"""Build the 7065 dataset summary from the pulled counts and daily timing plans.

Inputs (already pulled by atspm_tmc.py / atspm_plans.py):
  intersections/7065/counts/tmc_7065_5min.csv        5-min counts, one row per bin, status ok/outage
  intersections/7065/timing/timing_plan_7065.json    plans + per-day schedule read from Split Monitor
Outputs (processed only; raw data untouched):
  intersections/7065/dataset/days.csv                one row per day: volume, outages, quality, plans
  intersections/7065/dataset/profiles/*.csv, *.svg   typical 15-min profiles by day type, daily totals
  intersections/7065/dataset/README.md               summary + proposed train/validation/test split

Fidelity: counts are used as recorded; outage bins are excluded from sums and profiles, never filled.

  python3 tools/dataset_7065.py [--start 2026-07-06 --end 2026-10-03]
"""
import argparse
import csv
import datetime as dt
import json
import statistics as stt
from collections import Counter, defaultdict

from paths import sig_dir

SID = "7065"
MOVES = ["EB_L", "EB_T", "WB_L", "WB_T", "NB_L", "NB_T", "SB_L", "SB_T"]
# GDOT labels -> roads at 7065 (phase_map.json count_labels; EB/WB = Piedmont, NB/SB = Peachtree)
NAMES = {"EB_T": "Piedmont from N, through", "EB_L": "Piedmont from N, left",
         "WB_T": "Piedmont from S, through", "WB_L": "Piedmont from S, left",
         "NB_T": "Peachtree from SW, through", "NB_L": "Peachtree from SW, left",
         "SB_T": "Peachtree from NE, through", "SB_L": "Peachtree from NE, left"}
HOLIDAYS = {dt.date(2026, 7, 3): "Independence Day (observed)", dt.date(2026, 7, 4): "Independence Day",
            dt.date(2026, 9, 7): "Labor Day"}
DAY0, DAY1 = 6 * 60, 22 * 60          # "daytime" for the quality rule
USABLE_MAX_DAY_OUTAGE = 30            # minutes of daytime outage still counted as usable
STUCK_MIN = 120                       # a movement at 0 for >= 2 h in daytime while others count


def mins(t):
    return int(t[:2]) * 60 + int(t[3:])


def windows(times):
    out = []
    for t in sorted(times, key=mins):
        m = mins(t)
        if out and m - out[-1][2] == 5:
            out[-1][1], out[-1][2] = t, m
        else:
            out.append([t, t, m])
    return [(a, f"{(mins(b) + 5) // 60:02d}:{(mins(b) + 5) % 60:02d}") for a, b, _ in out]


def day_type(d):
    if d in HOLIDAYS:
        return "holiday"
    return {5: "saturday", 6: "sunday"}.get(d.weekday(), "weekday")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2026-07-06")
    ap.add_argument("--end", default="2026-10-03")
    a = ap.parse_args()
    d0, d1 = dt.date.fromisoformat(a.start), dt.date.fromisoformat(a.end)
    cdir, tdir = sig_dir(SID, "counts"), sig_dir(SID, "timing")
    out = sig_dir(SID, "dataset")
    (out / "profiles").mkdir(parents=True, exist_ok=True)

    rows = defaultdict(list)
    for r in csv.DictReader(open(cdir / f"tmc_{SID}_5min.csv")):
        d = dt.date.fromisoformat(r["date"])
        if d0 <= d <= d1:
            rows[d].append(r)
    plan = json.loads((tdir / f"timing_plan_{SID}.json").read_text())
    sched, plans = plan.get("schedule", {}), plan.get("plans", {})
    bad_plans = {k for k, p in plans.items() if any("unverified" in c or "mismatch" in c for c in p.get("checks", []))}

    days, prof = [], defaultdict(lambda: defaultdict(list))   # prof[type][(move, quarter)] -> values
    peak = []
    for n in range((d1 - d0).days + 1):
        d = d0 + dt.timedelta(n)
        rs = rows.get(d, [])
        ok = [r for r in rs if r["status"] == "ok"]
        out_t = [r["time"] for r in rs if r["status"] != "ok"]
        day_out = sum(5 for t in out_t if DAY0 <= mins(t) < DAY1)
        tot = sum(int(r[m] or 0) for r in ok for m in MOVES)
        if not rs:
            quality = "missing"
        elif not out_t:
            quality = "complete"
        elif day_out <= USABLE_MAX_DAY_OUTAGE:
            quality = "usable"
        else:
            quality = "bad"
        # stuck detector: one movement at zero for >= 2 h of daytime while the others count
        stuck = []
        for m in MOVES:
            run = best = 0
            for r in sorted(ok, key=lambda r: mins(r["time"])):
                if not (DAY0 <= mins(r["time"]) < DAY1):
                    continue
                others = sum(int(r[x] or 0) for x in MOVES if x != m)
                run = run + 5 if int(r[m] or 0) == 0 and others > 0 else 0
                best = max(best, run)
            if best >= STUCK_MIN:
                stuck.append(f"{m} {best} min")
        if stuck and quality in ("complete", "usable"):
            quality = "suspect"
        sc = sched.get(str(d))
        bands = [b for b in (sc or []) if b.get("kind") in ("plan", "free") and b.get("minutes", 0) >= 10]
        # schedule signature: switch times rounded to 5 min (the chart reads at ~1.2 min per pixel)
        r5 = lambda t: f"{(mins(t) + 2) // 5 * 5 // 60:02d}:{(mins(t) + 2) // 5 * 5 % 60:02d}"
        sig = " ".join(f"{r5(b['start'])} {b['plan']}" for b in bands)
        used = sorted({b["plan"] for b in bands})
        days.append({"date": str(d), "weekday": d.strftime("%a"), "day_type": day_type(d),
                     "holiday": HOLIDAYS.get(d, ""), "quality": quality, "total_vehicles": tot,
                     "valid_bins": len(ok), "outage_bins": len(out_t),
                     "outage_pct": round(100 * len(out_t) / 288, 1) if rs else "",
                     "daytime_outage_min": day_out,
                     "outage_windows": "; ".join(f"{x}-{y}" for x, y in windows(out_t)),
                     "stuck_movements": "; ".join(stuck),
                     "schedule_read": "yes" if bands else ("no chart" if sc is None else "unreadable"),
                     "plans_used": " ".join(used), "unverified_plan_used": "yes" if set(used) & bad_plans else "",
                     "schedule": sig})
        if quality in ("complete", "usable"):
            tp = day_type(d)
            q = defaultdict(lambda: defaultdict(int))
            qok = defaultdict(int)
            for r in ok:
                k = mins(r["time"]) // 15
                qok[k] += 1
                for m in MOVES:
                    q[m][k] += int(r[m] or 0)
            for m in MOVES:
                for k in range(96):
                    if qok[k] == 3:                     # full quarter-hour only
                        prof[tp][(m, k)].append(q[m][k])
            # busiest rolling hour (all movements) between 15:00 and 19:00, complete hours only
            bins = {mins(r["time"]): sum(int(r[m] or 0) for m in MOVES) for r in ok}
            best = max(((sum(bins[t + 5 * i] for i in range(12)), t) for t in range(15 * 60, 18 * 60 + 5, 5)
                        if all(t + 5 * i in bins for i in range(12))), default=None)
            if best:
                peak.append((d, tp, best[0], best[1]))

    with open(out / "days.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(days[0]))
        w.writeheader()
        w.writerows(days)

    # typical profiles: median 15-min count per movement by day type (veh per 15 min)
    types = [t for t in ("weekday", "saturday", "sunday") if prof[t]]
    for t in types:
        with open(out / "profiles" / f"{t}_15min_median.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["time"] + MOVES + ["n_days"])
            for k in range(96):
                vals = [prof[t][(m, k)] for m in MOVES]
                w.writerow([f"{k // 4:02d}:{k % 4 * 15:02d}"] + [stt.median(v) if v else "" for v in vals]
                           + [len(vals[0])])
    plot_profiles(out, prof, types)
    plot_days(out, days)

    # plan schedules: most common per day type, and days that differ
    sig_by_type = defaultdict(Counter)
    for x in days:
        if x["schedule"]:
            sig_by_type[x["day_type"]][x["schedule"]] += 1
    write_readme(out, days, peak, sig_by_type, plans, bad_plans, types, d0, d1)
    print(f"-> {out}  ({len(days)} days)")


SURF, INK, INK2, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#b5b4ad"
COL = {"weekday": "#2a78d6", "saturday": "#eb6834", "sunday": "#1baf7a"}   # validated categorical slots 1-3


def _svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'font-family="sans-serif"><rect width="{w}" height="{h}" fill="{SURF}"/>{body}</svg>')


def _panel(x0, y0, w, h, ymax, title, series, xticks=(0, 6, 12, 18, 24)):
    """one small-multiple line panel; series = [(label, color, [y per quarter-hour])]"""
    g = [f'<text x="{x0}" y="{y0 - 8}" font-size="12" fill="{INK}">{title}</text>']
    for i in range(5):
        v = ymax * i / 4
        y = y0 + h - h * i / 4
        g.append(f'<line x1="{x0}" x2="{x0 + w}" y1="{y:.1f}" y2="{y:.1f}" stroke="{GRID}" stroke-width="0.6"/>')
        g.append(f'<text x="{x0 - 4}" y="{y + 3:.1f}" font-size="9" fill="{INK2}" text-anchor="end">{v:.0f}</text>')
    for t in xticks:
        x = x0 + w * t / 24
        g.append(f'<text x="{x:.1f}" y="{y0 + h + 12}" font-size="9" fill="{INK2}" text-anchor="middle">{t}</text>')
    g.append(f'<line x1="{x0}" x2="{x0 + w}" y1="{y0 + h}" y2="{y0 + h}" stroke="{AXIS}"/>')
    for _, c, ys in series:
        pts, segs = [], []
        for k, v in enumerate(ys):
            if v is None:
                if pts:
                    segs.append(pts)
                pts = []
                continue
            pts.append(f"{x0 + w * (k + 0.5) / 96:.1f},{y0 + h - h * min(v, ymax) / ymax:.1f}")
        if pts:
            segs.append(pts)
        for sgm in segs:
            g.append(f'<polyline points="{" ".join(sgm)}" fill="none" stroke="{c}" stroke-width="2" '
                     f'stroke-linejoin="round" stroke-linecap="round"/>')
    return "".join(g)


def plot_profiles(out, prof, types):
    W, H, pw, ph = 1280, 620, 260, 200
    body = [f'<text x="20" y="28" font-size="16" fill="{INK}">SIG 7065 — typical demand by movement '
            f'(veh/h, median 15-min rate over complete/usable days; x = hour of day)</text>']
    for i, t in enumerate(types):                                   # legend
        body.append(f'<line x1="{20 + 130 * i}" x2="{44 + 130 * i}" y1="48" y2="48" stroke="{COL[t]}" stroke-width="3"/>'
                    f'<text x="{50 + 130 * i}" y="52" font-size="12" fill="{INK}">{t.capitalize()}</text>')
    for j, m in enumerate(MOVES):
        series = [(t, COL[t], [stt.median(prof[t][(m, k)]) * 4 if prof[t][(m, k)] else None for k in range(96)])
                  for t in types]
        ymax = max([v for _, _, ys in series for v in ys if v is not None] + [1])
        ymax = ((ymax // 100) + 1) * 100
        x0, y0 = 60 + (j % 4) * (pw + 50), 100 + (j // 4) * (ph + 70)
        body.append(_panel(x0, y0, pw, ph, ymax, f"{NAMES[m]} ({m})", series))
    (out / "profiles" / "profiles_by_daytype.svg").write_text(_svg(W, H, "".join(body)))


def plot_days(out, days):
    n = len(days)
    W, H, x0, y0, w, h = 1280, 340, 70, 60, 1180, 220
    ymax = max([x["total_vehicles"] for x in days] + [1])
    ymax = ((ymax // 10000) + 1) * 10000
    bw = w / n
    body = [f'<text x="20" y="26" font-size="16" fill="{INK}">SIG 7065 — vehicles counted per day '
            f'(hatched = outage / suspect / missing; partial total)</text>',
            '<defs><pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" '
            f'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" stroke="{INK2}" stroke-width="1.2"/></pattern></defs>']
    for i in range(5):
        v = ymax * i / 4
        y = y0 + h - h * i / 4
        body.append(f'<line x1="{x0}" x2="{x0 + w}" y1="{y:.1f}" y2="{y:.1f}" stroke="{GRID}" stroke-width="0.6"/>'
                    f'<text x="{x0 - 6}" y="{y + 3:.1f}" font-size="10" fill="{INK2}" text-anchor="end">{v:,.0f}</text>')
    for i, x in enumerate(days):
        v = x["total_vehicles"]
        bh = h * v / ymax
        good = x["quality"] in ("complete", "usable")
        fill = COL["weekday"] if good else "url(#hatch)"
        body.append(f'<rect x="{x0 + i * bw + 1:.1f}" y="{y0 + h - bh:.1f}" width="{max(1, bw - 2):.1f}" height="{bh:.1f}" '
                    f'rx="2" fill="{fill}" stroke="{"none" if good else INK2}" stroke-width="0.6">'
                    f'<title>{x["date"]} {x["weekday"]}: {v:,} veh, {x["quality"]}</title></rect>')
        d = dt.date.fromisoformat(x["date"])
        if d.weekday() == 0:
            body.append(f'<text x="{x0 + i * bw + bw / 2:.1f}" y="{y0 + h + 14}" font-size="9" fill="{INK2}" '
                        f'text-anchor="middle">{d:%b %d}</text>')
    (out / "profiles" / "daily_totals.svg").write_text(_svg(W, H, "".join(body)))


def write_readme(out, days, peak, sig_by_type, plans, bad_plans, types, d0, d1):
    q = Counter((x["day_type"], x["quality"]) for x in days)
    L = [f"# SIG 7065 dataset — {d0} to {d1} ({len(days)} days)", "",
         "Processed from GDOT ATSPM exports (`../counts/tmc_7065_5min.csv`, `../timing/timing_plan_7065.json`) "
         "by `tools/dataset_7065.py`. Counts are used as recorded; sensor-outage bins are excluded, never filled.", "",
         "## Day quality", "",
         "complete = no outage bin · usable = ≤ 30 min of outage between 06:00 and 22:00 · "
         "suspect = a movement reads 0 for ≥ 2 h of daytime while the others count · bad = more daytime outage · "
         "missing = no export", "",
         "| Day type | complete | usable | suspect | bad | missing |", "|---|---|---|---|---|---|"]
    for t in ("weekday", "saturday", "sunday", "holiday"):
        L.append(f"| {t} | " + " | ".join(str(q[(t, k)]) for k in ("complete", "usable", "suspect", "bad", "missing")) + " |")
    L += ["", "Per-day details: `days.csv`. Chart: `profiles/daily_totals.svg`.", "",
          "## Typical demand", "", "![profiles](profiles/profiles_by_daytype.svg)", "",
          "Median 15-minute counts per movement: `profiles/<daytype>_15min_median.csv`.", ""]
    pk = defaultdict(list)
    for d, tp, v, t in peak:
        pk[tp].append((v, t))
    L += ["## PM peak hour (busiest rolling hour 15:00–19:00, all movements)", "",
          "| Day type | days | median veh/h | min | max | typical start |", "|---|---|---|---|---|---|"]
    for tp, v in pk.items():
        vv = [x for x, _ in v]
        st = Counter(f"{t // 60:02d}:{t % 60:02d}" for _, t in v).most_common(1)[0][0]
        L.append(f"| {tp} | {len(v)} | {stt.median(vv):.0f} | {min(vv)} | {max(vv)} | {st} |")
    L += ["", "## GDOT timing schedules", "",
          f"Plans read: {', '.join(f'{k} ({p.get('cycle_s')} s)' for k, p in plans.items())}. "
          + (f"Flagged reads (rings don't close or partly read from force-off dots): {', '.join(sorted(bad_plans))}." if bad_plans else ""), ""]
    for tp, c in sig_by_type.items():
        L.append(f"**{tp}** — {sum(c.values())} days, {len(c)} distinct schedule(s):")
        for s, n in c.most_common(4):
            L.append(f"- {n} day(s): `{s}`")
        L.append("")
    noread = [x["date"] for x in days if x["schedule_read"] != "yes"]
    L += [f"Days without a readable schedule: {', '.join(noread) if noread else 'none'}.", ""]
    # keep the hand-written interpretation / split section (from "## Interpretation" on) across rebuilds
    old = (out / "README.md").read_text() if (out / "README.md").exists() else ""
    tail = old[old.index("\n## Interpretation"):] if "\n## Interpretation" in old else ""
    (out / "README.md").write_text("\n".join(L) + "\n" + tail)


if __name__ == "__main__":
    main()
