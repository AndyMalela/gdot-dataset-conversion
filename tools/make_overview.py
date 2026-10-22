#!/usr/bin/env python3
"""
Slide material for the intersections built so far.

  python3 tools/make_overview.py

Writes intersections/OVERVIEW.md (one table: data collected per intersection) and
intersections/overview.png (grid of SUMO snapshots with captions). Uses the
complete/accepted signals in intersections/signal_list.csv that have a sim/snapshot.png.
"""
import csv
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import INTERSECTIONS, sig_dir, rel  # noqa: E402

WEEK = ("2026-09-26", "2026-10-02")


def font(size, bold=False):
    for f in (f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"):
        if Path(f).exists():
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def info(sid, status):
    c, t, n, s = (sig_dir(sid, x) for x in ("counts", "timing", "network", "sim"))
    days = [d for d in csv.DictReader(open(c / "daily_summary.csv")) if WEEK[0] <= d["date"] <= WEEK[1]]
    full = [int(d["total_volume_valid_bins"]) for d in days if d["status"] == "ok"]
    wk = [int(d["total_volume_valid_bins"]) for d in days
          if d["status"] == "ok" and d["weekday"] not in ("Sat", "Sun")]
    m = re.search(r"Intersection:\s+(.*)", (c / "info.txt").read_text())
    mv = re.search(r"Movements:\s+(.*)", (c / "info.txt").read_text()).group(1).split()
    veh = [x for x in mv if x.split("_")[0] in ("EB", "WB", "NB", "SB")]
    plan = json.loads((t / f"timing_plan_{sid}.json").read_text())
    good = {k: p for k, p in plan["plans"].items() if k != "Actuated" and p["cycle_s"]
            and not any("unverified" in c or "mismatch" in c for c in p["checks"])}
    cyc = sorted({p["cycle_s"] for p in good.values()})
    actuated = "Actuated" in plan["plans"]
    j = json.loads((n / "junction.json").read_text())
    sim = {}
    rd = s / "README.md"
    if rd.exists():
        txt = rd.read_text()
        g = re.search(r"inserted (\d+), still waiting to enter at 09:30 (\d+)", txt)
        tp = re.search(r"teleports (\d+)", txt)
        lo = re.search(r"vehicles loaded (\d+)", txt)
        res = re.search(r"\*\*(PASS|CHECK)\*\*", txt)
        ve = re.search(r"mean absolute error of median green per phase: \*\*([0-9.]+) s", txt)
        if g and lo:
            sim = {"loaded": int(lo.group(1)), "inserted": int(g.group(1)), "waiting": int(g.group(2)),
                   "teleports": int(tp.group(1)), "result": res.group(1) if res else "",
                   "signal_err": float(ve.group(1)) if ve else None}
    return {"sid": sid, "name": re.sub(r"\s+", " ", m.group(1)).strip(), "status": status,
            "days": len(days), "full_days": len(full),
            "weekday_avg": round(sum(wk) / len(wk)) if wk else (round(sum(full) / len(full)) if full else 0),
            "movements": veh, "cycles": cyc, "actuated": actuated,
            "n_plans": len(good),
            "lefts_only": bool(veh) and all(x.endswith("_L") for x in veh),
            "approaches": len(j["approaches"]), "sim": sim,
            "snapshot": next((s / f for f in ("snapshot_wide.png", "snapshot.png") if (s / f).exists()), None)}


def main():
    rows = [r for r in csv.DictReader(open(INTERSECTIONS / "signal_list.csv"))
            if r["status"] in ("complete", "accepted") and (sig_dir(r["signal_id"], "sim") / "demand.rou.xml").exists()]
    data = [info(r["signal_id"], r["status"]) for r in rows]
    data.sort(key=lambda d: -d["weekday_avg"])

    L = ["# Intersections — data collected (as of 2026-10-05)", "",
         "Each intersection has: 7 days of 5-min turning-movement counts (GDOT ATSPM, "
         f"{WEEK[0]} to {WEEK[1]}), its real time-of-day signal timing plans (Split Monitor, "
         "2026-10-02), a SUMO network from OpenStreetMap, and a SUMO simulation running the "
         "measured demand under the real timing.", "",
         "| Signal | Intersection | Status | Count days (full) | Avg weekday vehicles | Movements counted | "
         "Timing plans (cycles, s) | Approaches | Signal vs recorded (median green error) | Sim check 07:00–09:30 |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for d in data:
        cyc = "/".join(map(str, d["cycles"])) or "–"
        tp = f"{d['n_plans']} ({cyc})" + (" + actuated" if d["actuated"] else "")
        sm = d["sim"]
        simtxt = (f"{sm['result']}: {sm['inserted']}/{sm['loaded']} entered, {sm['teleports']} teleports"
                  if sm else "–")
        vol = f"{d['weekday_avg']:,}" + (" (lefts only)" if d["lefts_only"] else "")
        L.append(f"| {d['sid']} | {d['name']} | {d['status']} | {d['days']} ({d['full_days']}) | "
                 f"{vol} | {len(d['movements'])} | {tp} | {d['approaches']} | "
                 f"{(str(sm['signal_err']) + ' s') if sm and sm.get('signal_err') is not None else '–'} | {simtxt} |")
    L += ["", "![overview](overview.png)", "",
          "Signal: SUMO NEMA actuated-coordinated controller built from GDOT's real plans, measured "
          "min greens / clearances / max-outs / recall; the error is the mean absolute difference "
          "between simulated and recorded median green per phase (Timing & Actuation, 2026-10-02 "
          "08:00 and 17:00). Avg weekday vehicles = counted vehicle movements on complete weekdays only. Timing plans "
          "= verified plans (unverified reads excluded). Sim check: PASS = every vehicle entered, no "
          "teleports, no collisions.", "",
          "Details per intersection: `intersections/<id>/sim/README.md` (assumptions, check), "
          "`timing/timing_plan_<id>.md`, `network/report.md`. Status of every signal checked "
          "(incl. rejected ones): `README.md`."]
    (INTERSECTIONS / "OVERVIEW.md").write_text("\n".join(L) + "\n")

    snaps = [d for d in data if d["snapshot"]]
    if snaps:
        cols = 4 if len(snaps) > 4 else len(snaps)
        rows_n = (len(snaps) + cols - 1) // cols
        W, H, CAP = 800, 500, 70
        out = Image.new("RGB", (cols * W, rows_n * (H + CAP)), "white")
        dr = ImageDraw.Draw(out)
        f1, f2 = font(26, True), font(19)
        for i, d in enumerate(snaps):
            x, y = (i % cols) * W, (i // cols) * (H + CAP)
            im = Image.open(d["snapshot"]).convert("RGB")
            tw, th = W - 10, H - 10                       # scale to cover the tile, centre-crop
            k = max(tw / im.width, th / im.height)
            im = im.resize((round(im.width * k), round(im.height * k)))
            l, t = (im.width - tw) // 2, (im.height - th) // 2
            out.paste(im.crop((l, t, l + tw, t + th)), (x + 5, y + 5))
            dr.text((x + 10, y + H), f"#{d['sid']}  {d['name']}", fill=(0, 0, 0), font=f1)
            cyc = ("cycles " + "/".join(map(str, d["cycles"])) + " s") if d["cycles"] else "actuated (no fixed cycle)"
            vol = f"~{d['weekday_avg']:,} veh/weekday" + (" (lefts only)" if d["lefts_only"] else "")
            dr.text((x + 10, y + H + 34), f"{vol} · {len(d['movements'])} counted "
                    f"movements · {cyc}", fill=(70, 70, 70), font=f2)
        out.save(INTERSECTIONS / "overview.png")
    print(f"-> {rel(INTERSECTIONS / 'OVERVIEW.md')}, {rel(INTERSECTIONS / 'overview.png')} "
          f"({len(snaps)} snapshots)")


if __name__ == "__main__":
    main()
