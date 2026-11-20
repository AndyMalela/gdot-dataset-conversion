"""Simulated vs field ATSPM numbers for one site/day/window set (first, exploratory comparison).

    uv run python -m atsc.sim.atspm_compare atsc/sites/137 2026-03-10 7 9 [--seed 1]

Runs the GDOT plan (validated controller) for the window with event recording, computes the ATSPM metrics per
hour and phase (atsc/sim/atspm_sim.py) and prints them next to the portal numbers read by tools/atspm_charts.py
(intersections/<id>/atspm/<metric>.csv). Field charts are matched by phase number; where the portal draws two
charts for one phase (own movement + a permissive left), both field rows are shown with their titles.
"""
import argparse
import csv
import json
from pathlib import Path

from atsc.sim import atspm_sim as A
from atsc.sim.episode import run_window
from atsc.sim.signal import actuated_from_site

FT_PER_S_PER_MPH = 5280 / 3600


def offsets(site_dir, sig_id):
    """seconds from the advance detector to the stop bar per phase: GDOT distance / GDOT approach speed."""
    det = json.loads((Path(site_dir) / "detectors.json").read_text())
    root = Path("intersections") / str(sig_id) / "config"
    speed = {}
    for r in csv.DictReader(open(root / "approaches.csv")):
        if r["Protected Phase"] and r["Approach Speed (MPH)"]:
            speed[int(r["Protected Phase"])] = float(r["Approach Speed (MPH)"])
    out = {}
    for d in det["detectors"]:
        if d["kind"] == "setback" and d["phase"] in speed:
            out[d["phase"]] = d["dist_m"] / 0.3048 / (speed[d["phase"]] * FT_PER_S_PER_MPH)
    return out


def zone_movement(site):
    """stop-bar zone -> GDOT count column it produces (presence zones count one per activation)."""
    det = json.loads((Path(site) / "detectors.json").read_text())
    out = {}
    for d in det["detectors"]:
        if d["kind"] != "stopbar" or d.get("hardware") == "modelled only":
            continue
        lanes = det["approaches"][d["leg"]]["lanes"].split()          # right -> left, index = SUMO lane
        role = lanes[d["lane"]] if d["lane"] < len(lanes) else "?"
        out[f"ch{d['ch']}"] = (f"{d['leg']}_{role}", "count" in d.get("note", "").lower())
    return out


def count_check(site, sig_id, date, ev, h0, h1):
    """Closed loop: simulated stop-bar activations vs GDOT's raw report count for the same zone's movement.
    Valid only where the report counts presence-zone activations (137: side streets and EB_L)."""
    raw = [r for r in csv.DictReader(open(Path("intersections") / str(sig_id) / "counts" / f"tmc_{sig_id}_5min.csv"))
           if r["date"] == date and f"{h0:02d}:00" <= r["time"] < f"{h1:02d}:00"]
    print(f"\n=== closed-loop count check {date} {h0:02d}-{h1:02d}: sim activations vs GDOT raw count")
    for ch, (mv, count_zone) in zone_movement(site).items():
        n = sum(1 for a, _ in ev["stopbar"].get(ch, []) if h0 * 3600 <= a < h1 * 3600)
        col = mv if raw and mv in raw[0] else None
        f = sum(int(float(r[col] or 0)) for r in raw) if col else None
        ratio = f"{n / f:.2f}" if f else "-"
        flag = "  (report column also fed by a count zone: ratio not meaningful)" if count_zone else ""
        print(f"  {ch:5s} {mv:6s} sim {n:5d}  GDOT {f if f is not None else '-':>5}  ratio {ratio}{flag}")


def field(sig_id, metric):
    p = Path("intersections") / str(sig_id) / "atspm" / f"{metric}.csv"
    return list(csv.DictReader(open(p))) if p.exists() else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("site")
    ap.add_argument("date")
    ap.add_argument("h0", type=int)
    ap.add_argument("h1", type=int)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    site = Path(a.site)
    sig_id = site.name
    res = run_window(site, a.date, float(a.h0), float(a.h1), actuated_from_site(site), mode="plan", seed=a.seed,
                     record_events=True)
    g, ev = res["greens"], res["events"]
    off = offsets(site, sig_id)
    phases = sorted(ev["phases"])
    print(f"offsets (s): {off}")
    count_check(site, sig_id, a.date, ev, a.h0, a.h1)
    for h in range(a.h0, a.h1):
        t0, t1 = h * 3600, (h + 1) * 3600
        key = f"{h:02d}:00"
        print(f"\n=== {a.date} {key}")
        for metric, fn, cols in [
            ("SplitFail", lambda p: A.split_failures(g, ev, p, t0, t1), ["split_failures"]),
            ("WaitTime", lambda p: A.wait_time(g, ev, p, t0, t1), ["avg_wait_s", "max_wait_s"]),
            ("ApproachDelay", lambda p: A.approach_delay(g, ev, p, t0, t1, off[p]) if p in off else None,
             ["delay_per_veh_s", "total_delay_h"]),
            ("PCD", lambda p: A.pcd(g, ev, p, t0, t1, off[p]) if p in off else None, ["aog_pct", "gt_pct", "platoon_ratio"]),
            ("PedDelay", lambda p: A.ped_delay(g, ev, p, t0, t1), ["ped_presses", "cycles_with_requests"]),
        ]:
            fr = [r for r in field(sig_id, metric) if r["date"] == a.date and r["start"] == key]
            print(f"  {metric}")
            for p in phases:
                s = fn(p)
                frs = [r for r in fr if r["phase"] == str(p)]
                if s is None and not frs:
                    continue
                sim = ", ".join(f"{c}={s[c]:.2f}" if isinstance(s.get(c), float) else f"{c}={s.get(c)}" for c in cols) if s else "-"
                fld = " | ".join(f"{r['title']}: " + ", ".join(f"{c}={r[c]}" for c in cols) for r in frs) or "-"
                print(f"    P{p}  sim {sim}\n         field {fld}")


if __name__ == "__main__":
    main()
