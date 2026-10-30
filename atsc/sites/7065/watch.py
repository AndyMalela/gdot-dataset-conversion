"""Watch SIG 7065 in sumo-gui: real demand of any non-locked day, any controller, same engine as the experiments,
with the field's own numbers alongside for troubleshooting.

    uv run python atsc/sites/7065/watch.py 2026-09-02                       # GDOT plans, 17:00-18:00
    uv run python atsc/sites/7065/watch.py 2026-09-02 --from 13:45 --to 14:30 --focus N --phases 3,4
    uv run python atsc/sites/7065/watch.py 2026-09-02 --controller actuated
    uv run python atsc/sites/7065/watch.py 2026-09-02 --controller lstdq --it 5

Window: the Delay box sets the speed (0 = fastest); right-click a vehicle or detector for its values.
Left-turners are orange. --focus N|S|SW|NE zooms onto one approach.
Terminal: every ended green (or only --phases), next to GDOT's Split Monitor average for that phase, plan and
day (green = split - yellow - red); a summary at the end, incl. how many left-turners went permissively
(flashing yellow arrow, during the opposing through green) vs. on their own protected arrow.
"""
import argparse
import csv
import json
import statistics as st
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
from atsc.sim import demand, run  # noqa: E402
from atsc.sim.signal import FixedPolicy, SumoSignal, actuated_from_site  # noqa: E402

ORANGE = (255, 140, 0, 255)


def hours(s):
    h, _, m = s.partition(":")
    return int(h) + int(m or 0) / 60


def hm(t):
    t = int(t)
    return f"{t // 3600:02d}:{t % 3600 // 60:02d}:{t % 60:02d}"


def field_for(date, sig):
    """{(phase, band_start_s, band_end_s): row} of GDOT's checked Split Monitor statistics for the day."""
    out = {}
    f = REPO / "intersections/7065/timing/splitstats_7065.csv"
    for r in csv.DictReader(open(f)):
        if r["date"] == date and r["check"] == "ok":
            out[(int(r["phase"]), demand.hm_s(r["band_start"]), demand.hm_s(r["band_end"]))] = r
    return out


def focus_point(net, edge_id, back=45.0):
    """a point `back` m upstream of the approach's stop line."""
    sh = net.getEdge(edge_id).getShape()
    (x0, y0), (x1, y1) = sh[0], sh[-1]
    d = max(1e-6, ((x0 - x1) ** 2 + (y0 - y1) ** 2) ** 0.5)
    return x1 + (x0 - x1) / d * back, y1 + (y0 - y1) / d * back


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("date")
    ap.add_argument("--from", dest="b", default="17:00")
    ap.add_argument("--to", dest="e", default="18:00")
    ap.add_argument("--controller", default="gdot", choices=["gdot", "actuated", "webster", "lstdq"])
    ap.add_argument("--it", type=int, help="LSTDQ iteration (lstdq/w_it<k>.npy)")
    ap.add_argument("--warmup", type=float, default=10, help="minutes simulated before the window")
    ap.add_argument("--focus", choices=["N", "S", "SW", "NE"], help="zoom onto one approach")
    ap.add_argument("--phases", help="print only these phases, e.g. 3,5")
    ap.add_argument("--nogui", action="store_true", help="run without the window (test)")
    a = ap.parse_args()
    b0, b1 = hours(a.b) * 3600, hours(a.e) * 3600
    only = {int(x) for x in a.phases.split(",")} if a.phases else None
    cal = json.loads((HERE / "sim.json").read_text())
    sigspec = json.loads((HERE / "signal.json").read_text())
    mv = json.loads((HERE / "movements.json").read_text())["movements"]
    field = field_for(a.date, sigspec)
    with tempfile.TemporaryDirectory() as tmp:
        rou = Path(tmp) / "d.rou.xml"
        demand.write_routes(HERE, run.net_file(HERE), a.date, rou, vtype=cal["vtype"])
        extra = [] if a.nogui else ["--gui-settings-file", str(HERE / "network" / "view.xml"), "--start"]
        conn = run.start(HERE, rou, max(0, b0 - a.warmup * 60), b1, gui=not a.nogui, step=cal["step"], extra=extra)
        if a.focus and not a.nogui:
            import sumolib
            net = sumolib.net.readNet(str(run.net_file(HERE).resolve()))
            edge = json.loads((HERE / "detectors.json").read_text())["approaches"][a.focus]["edge"]
            conn.gui.setOffset("View #0", *focus_point(net, edge))
            conn.gui.setZoom("View #0", 1500)
        kw = {}
        if a.controller == "gdot":
            pol, kw["mode"] = actuated_from_site(HERE), "plan"
        elif a.controller == "actuated":
            pol, kw["mode"] = actuated_from_site(HERE), "free"
        elif a.controller == "webster":
            sys.path.insert(0, str(HERE))
            from baselines import webster_schedule
            pol, kw = FixedPolicy(), {"mode": "schedule", "schedule": webster_schedule(), "skip_uncalled": False}
        else:
            import numpy as np
            from atsc.rl.agent import LSTDQPolicy
            pol, kw["mode"] = LSTDQPolicy(HERE, w=np.load(HERE / "lstdq" / f"w_it{a.it}.npy")), "free"
        sig = SumoSignal(conn, HERE, run.net_file(HERE), pol, day=a.date, **kw)

        lefts = {c: m for c, m in mv.items() if m["move"] == "L"}
        approach_of = {m["from"]: c for c, m in lefts.items()}
        on_edge = {m["from"]: set() for m in lefts.values()}
        turned = defaultdict(Counter)             # left column -> {"protected", "permissive"}
        greens = defaultdict(list)                # phase -> (green s, how) inside the window
        shown, disp = 0, {}
        try:
            while conn.simulation.getTime() < b1:
                conn.simulationStep()
                disp = sig.step()
                t = conn.simulation.getTime()
                for v in conn.simulation.getDepartedIDList():
                    if v.split(".")[0] in lefts and not a.nogui:
                        conn.vehicle.setColor(v, ORANGE)
                if t >= b0:
                    for e, prev in on_edge.items():
                        now = {v for v in conn.edge.getLastStepVehicleIDs(e) if v.startswith(approach_of[e] + ".")}
                        col = approach_of[e]
                        for _ in prev - now:          # left-turner crossed the stop line
                            prot = lefts[col]["phases"][0]
                            turned[col]["protected" if disp.get(prot) in ("G", "y") else "permissive"] += 1
                        on_edge[e] = now
                for g in sig.engine.greens[shown:]:
                    if g.end < b0:
                        continue
                    greens[g.phase].append((g.green, g.how))
                    if only and g.phase not in only:
                        continue
                    f = next((r for (p, s0, s1), r in field.items() if p == g.phase and s0 <= g.start < s1), None)
                    ph = sigspec["phases"][str(g.phase)]
                    fs = (f"field avg {float(f['avg_split_s']) - ph['yellow'] - ph['red']:5.1f} s, "
                          f"gap {float(f['gap_pct']):3.0f}% force {float(f['force_pct']):3.0f}% skip {float(f['skip_pct']):3.0f}%"
                          if f else "field: no checked reading")
                    print(f"{hm(g.end)}  plan {sig._cur_plan_name or '-':4s} P{g.phase} green {g.green:5.1f} s "
                          f"({g.how:5s}) | {fs}", flush=True)
                shown = len(sig.engine.greens)
        except Exception as e:                          # closing the window ends the run
            print(f"stopped: {e.__class__.__name__}")
        finally:
            try:
                conn.close()
            except Exception:
                pass

    print(f"\nSummary {a.date} {a.b}-{a.e}, controller {a.controller}")
    print("phase | sim greens | sim mean green s | sim gap % | field (band of window start)")
    for p in sorted(greens):
        gs = greens[p]
        f = next((r for (q, s0, s1), r in field.items() if q == p and s0 <= b0 < s1), None)
        ph = sigspec["phases"][str(p)]
        fs = (f"avg green {float(f['avg_split_s']) - ph['yellow'] - ph['red']:.1f} s, gap {float(f['gap_pct']):.0f}%, "
              f"skip {float(f['skip_pct']):.0f}%" if f else "-")
        print(f"P{p} | {len(gs):3d} | {st.mean(g for g, _ in gs):5.1f} | {100 * sum(h == 'gap' for _, h in gs) / len(gs):4.0f} | {fs}")
    print("left turns crossing the stop line: protected arrow vs permissive (flashing yellow)")
    for c, n in turned.items():
        tot = sum(n.values())
        print(f"  {c} (P{lefts[c]['phases'][0]}): {tot} vehicles, permissive {n['permissive']} ({100 * n['permissive'] / max(1, tot):.0f} %)")


if __name__ == "__main__":
    main()
