"""Run one simulated day window of a site with a given controller and measure it.

    res = run_window(site_dir, "2026-07-16", 15.5, 19.0, policy=ActuatedPolicy(2.0))
    res["delay"]        per movement: vehicles, mean delay (s/veh) for vehicles counted in [begin, end)
    res["crossings"]    per movement: stop-line crossing times (s)
    res["greens"]       NemaEngine green records
    res["backlog_max"]  most vehicles waiting to enter the network, per movement

Delay = SUMO timeLoss + departDelay (time lost to the signal, to queues and to waiting for entry),
from tripinfo output incl. vehicles still in the network at the end (written as unfinished).
Vehicles are scored by the count bin they belong to (id = MOVEMENT.bin.k), so a window's score covers
exactly the vehicles GDOT counted in that window.
"""
from __future__ import annotations

import json
import tempfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

from . import demand, run
from .signal import SumoSignal


def run_window(site_dir, date, begin_h, end_h, policy, mode="plan", plan=None, free_max=None, vtype=None,
               seed=1, warmup_s=900, drain_s=900, step=None, gui=False, schedule=None, skip_uncalled=True):
    """vtype / step default to the site's calibrated sim.json."""
    site_dir = Path(site_dir)
    cal = json.loads((site_dir / "sim.json").read_text()) if (site_dir / "sim.json").exists() else {}
    vtype = cal.get("vtype", {}) if vtype is None else vtype
    step = cal.get("step", 1.0) if step is None else step
    b0, b1 = begin_h * 3600, end_h * 3600
    mv = json.loads((site_dir / "movements.json").read_text())["movements"]
    approach = {m["from"] for m in mv.values()}
    with tempfile.TemporaryDirectory() as tmp:
        rou = Path(tmp) / "d.rou.xml"
        ti = Path(tmp) / "ti.xml"
        demand.write_routes(site_dir, run.net_file(site_dir), date, rou, seed=seed, vtype=vtype)
        conn = run.start(site_dir, rou, b0 - warmup_s, b1 + drain_s, gui=gui, step=step, seed=seed,
                         extra=["--tripinfo-output", str(ti), "--tripinfo-output.write-unfinished", "true"])
        sig = SumoSignal(conn, site_dir, run.net_file(site_dir), policy, mode=mode, day=str(date), plan=plan,
                         free_max=free_max, schedule=schedule, skip_uncalled=skip_uncalled)
        prev = {e: set() for e in approach}
        crossings = defaultdict(list)
        backlog = Counter()
        teleports = 0
        while conn.simulation.getTime() < b1 + drain_s:
            conn.simulationStep()
            sig.step()
            t = conn.simulation.getTime()
            teleports += conn.simulation.getStartingTeleportNumber()
            for e in approach:
                now = set(conn.edge.getLastStepVehicleIDs(e))
                for v in prev[e] - now:
                    crossings[v.split(".")[0]].append(t)
                prev[e] = now
            for c, n in Counter(v.split(".")[0] for v in conn.simulation.getPendingVehicles()).items():
                backlog[c] = max(backlog[c], n)
        greens = sig.greens_table()
        plan_log = sig.plan_log
        cycle_starts = list(sig.engine.cycle_starts)
        conn.close()

        tot, n, unfinished = defaultdict(float), Counter(), Counter()
        hour = defaultdict(lambda: [0.0, 0])                  # count-bin hour -> [delay sum, vehicles]
        for _, el in ET.iterparse(ti):
            if el.tag != "tripinfo":
                continue
            vid = el.get("id")
            col, tbin = vid.split(".")[0], int(vid.split(".")[1])
            if b0 <= tbin < b1:
                dl = float(el.get("timeLoss")) + float(el.get("departDelay"))
                tot[col] += dl
                n[col] += 1
                hour[tbin // 3600][0] += dl
                hour[tbin // 3600][1] += 1
                if float(el.get("arrival", -1)) < 0:
                    unfinished[col] += 1
            el.clear()
    delay = {c: {"veh": n[c], "mean_s": tot[c] / n[c] if n[c] else None, "unfinished": unfinished[c]} for c in mv}
    allv = sum(n.values())
    return {"date": str(date), "window_h": [begin_h, end_h], "seed": seed, "vtype": vtype or {},
            "delay": delay, "delay_all_s": sum(tot.values()) / allv if allv else None, "vehicles": allv,
            "delay_by_hour": {h: v for h, v in sorted(hour.items())},
            "crossings": dict(crossings), "greens": greens, "plan_log": plan_log, "cycle_starts": cycle_starts,
            "backlog_max": dict(backlog), "teleports": teleports}
