"""Run one simulated day window of a site with a given controller and measure it.

    res = run_window(site_dir, "2026-07-16", 15.5, 19.0, policy=ActuatedPolicy(2.0))
    res["delay"]        per movement: vehicles, mean delay (s/veh) for vehicles counted in [begin, end)
    res["crossings"]    per movement: stop-line crossing times (s)
    res["greens"]       NemaEngine green records
    res["backlog_max"]  most vehicles waiting to enter the network, per movement
    res["by_hour_mv"]   per (count-bin hour, movement): vehicles, mean / 95th-percentile / max delay, backlog

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


def _tripinfos(ti, site_dir, date, seed):
    """iterparse the tripinfo file; if SUMO wrote it unreadable (seen twice in ~1,000 DQN training episodes,
    2026-11-09), keep a copy in <site>/debug/ for diagnosis and re-raise."""
    try:
        yield from ET.iterparse(ti)
    except ET.ParseError:
        import shutil
        d = Path(site_dir) / "debug"
        d.mkdir(exist_ok=True)
        shutil.copy(ti, d / f"tripinfo_unreadable_{date}_seed{seed}.xml")
        raise


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
        rous = [str(rou)]
        for k, (nd, _) in enumerate(run.neighbours(site_dir)):        # neighbour signals' own counted movements
            nr = Path(tmp) / f"n{k}.rou.xml"
            demand.write_routes(nd, run.net_file(site_dir), date, nr, seed=seed, vtype=vtype, prefix=f"N{k}_")
            rous.append(str(nr))
        conn = run.start(site_dir, ",".join(rous), b0 - warmup_s, b1 + drain_s, gui=gui, step=step, seed=seed,
                         extra=["--tripinfo-output", str(ti), "--tripinfo-output.write-unfinished", "true",
                                "--tripinfo-output.write-undeparted", "true"])   # F2: never-entered vehicles scored too
        from .signal import actuated_from_site
        nsigs = [SumoSignal(conn, nd, run.net_file(site_dir), actuated_from_site(nd), mode="plan", day=str(date), seed=seed)
                 for nd, _ in run.neighbours(site_dir)]             # field timing, whatever controls the site
        sig = SumoSignal(conn, site_dir, run.net_file(site_dir), policy, mode=mode, day=str(date), plan=plan,
                         free_max=free_max, schedule=schedule, skip_uncalled=skip_uncalled, seed=seed)
        prev = {e: set() for e in approach}
        crossings = defaultdict(list)
        backlog = Counter()
        backlog_h = Counter()                                 # (hour, movement) -> most vehicles waiting to enter
        teleports = 0
        while conn.simulation.getTime() < b1 + drain_s:
            conn.simulationStep()
            sig.step()
            for ns in nsigs:
                ns.step()
            t = conn.simulation.getTime()
            teleports += conn.simulation.getStartingTeleportNumber()
            for e in approach:
                now = set(conn.edge.getLastStepVehicleIDs(e))
                for v in prev[e] - now:
                    crossings[v.split(".")[0]].append(t)
                prev[e] = now
            for c, n in Counter(v.split(".")[0] for v in conn.simulation.getPendingVehicles()).items():
                backlog[c] = max(backlog[c], n)
                backlog_h[(int(t // 3600), c)] = max(backlog_h[(int(t // 3600), c)], n)
        greens = sig.greens_table()
        plan_log = sig.plan_log
        cycle_starts = list(sig.engine.cycle_starts)
        conn.close()

        tot, n, unfinished = defaultdict(float), Counter(), Counter()
        hour = defaultdict(lambda: [0.0, 0])                  # count-bin hour -> [delay sum, vehicles]
        hour_mv = defaultdict(list)                           # (count-bin hour, movement) -> vehicle delays
        for _, el in _tripinfos(ti, site_dir, date, seed):
            if el.tag != "tripinfo":
                continue
            vid = el.get("id")
            col, tbin = vid.split(".")[0], int(vid.split(".")[1])
            if col not in mv:                                    # neighbour flows are not scored
                el.clear()
                continue
            if b0 <= tbin < b1:
                dl = float(el.get("timeLoss")) + float(el.get("departDelay"))
                tot[col] += dl
                n[col] += 1
                hour[tbin // 3600][0] += dl
                hour[tbin // 3600][1] += 1
                hour_mv[(tbin // 3600, col)].append(dl)
                if float(el.get("arrival", -1)) < 0:
                    unfinished[col] += 1
            el.clear()
    delay = {c: {"veh": n[c], "mean_s": tot[c] / n[c] if n[c] else None, "unfinished": unfinished[c]} for c in mv}
    allv = sum(n.values())
    by_hour_mv = {}
    for (h, c), ds in sorted(hour_mv.items()):
        ds.sort()
        by_hour_mv[(h, c)] = {"veh": len(ds), "mean_s": sum(ds) / len(ds), "p95_s": ds[int(0.95 * (len(ds) - 1))],
                              "max_s": ds[-1], "backlog_max": backlog_h.get((h, c), 0)}
    return {"date": str(date), "window_h": [begin_h, end_h], "seed": seed, "vtype": vtype or {},
            "delay": delay, "delay_all_s": sum(tot.values()) / allv if allv else None, "vehicles": allv,
            "delay_by_hour": {h: v for h, v in sorted(hour.items())},
            "by_hour_mv": by_hour_mv,
            "crossings": dict(crossings), "greens": greens, "plan_log": plan_log, "cycle_starts": cycle_starts,
            "backlog_max": dict(backlog), "teleports": teleports}
