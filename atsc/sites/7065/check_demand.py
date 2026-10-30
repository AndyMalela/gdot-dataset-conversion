"""Phase 1.4 check: does the generated demand reach the detectors as counted, spread across lanes, without
being held back at the network entry?  Real GDOT plans + gap-out (passage 2 s), one train weekday.

    uv run python atsc/sites/7065/check_demand.py 2026-07-16 [--hours 14.5 19.5] [--vtype '{"lcSpeedGain": 5}']
"""
import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
from atsc.sim import demand, run                    # noqa: E402
from atsc.sim.signal import ActuatedPolicy, SumoSignal  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("date")
    ap.add_argument("--hours", nargs=2, type=float, default=[14.5, 19.5])
    ap.add_argument("--vtype", type=json.loads, default={})
    ap.add_argument("--tag", default="")
    ap.add_argument("--depart-lane", default="random")
    a = ap.parse_args()
    date, (b0, b1) = a.date, (a.hours[0] * 3600, a.hours[1] * 3600)
    out = HERE / "demand_audit" / "check"
    out.mkdir(parents=True, exist_ok=True)
    rou = out / f"{date}{a.tag}.rou.xml"
    meta = demand.write_routes(HERE, run.net_file(HERE), date, rou, seed=1, vtype=a.vtype, depart_lane=a.depart_lane)
    conn = run.start(HERE, rou, b0 - 900, b1)               # 15 min warm-up
    sig = SumoSignal(conn, HERE, run.net_file(HERE), ActuatedPolicy(2.0), mode="plan", day=date)
    det = json.loads((HERE / "detectors.json").read_text())
    mv = json.loads((HERE / "movements.json").read_text())["movements"]
    det["detectors"] = [d for d in det["detectors"] if d.get("modelled", True)]

    seen = defaultdict(set)                 # detector -> vehicle ids (counted from b0)
    by_mv = defaultdict(set)                # (detector, movement column) -> ids
    backlog = Counter()
    teleports = 0
    while conn.simulation.getTime() < b1:
        conn.simulationStep()
        sig.step()
        t = conn.simulation.getTime()
        teleports += conn.simulation.getStartingTeleportNumber()
        pend = Counter(v.split(".")[0] for v in conn.simulation.getPendingVehicles())
        for c, n in pend.items():
            backlog[c] = max(backlog[c], n)
        if t < b0:
            continue
        for d in det["detectors"]:
            ch = f"ch{d['ch']}"
            ids = (conn.inductionloop.getLastStepVehicleIDs(ch) if d["kind"] == "setback"
                   else conn.lanearea.getLastStepVehicleIDs(ch))
            for v in ids:
                seen[ch].add(v)
                by_mv[(ch, v.split(".")[0])].add(v)
    conn.close()

    # counted vehicles in [b0, b1) per movement
    bins = demand.load_counts(HERE)[__import__("datetime").date.fromisoformat(date)]
    counted = Counter()
    for b in bins:
        if b.status == "ok" and b0 <= b.t < b1:
            counted.update(b.counts)

    L = [f"# Demand check {date} {b0 / 3600:.1f}-{b1 / 3600:.1f} h (real plans, gap-out 2 s), vType {meta['vtype']}, departLane {meta['depart_lane']}", "",
         f"vehicles in file {meta['vehicles']}, teleports {teleports}", "",
         "## Max vehicles waiting to enter the network (insertion backlog)", ""]
    L += [f"- {c}: {backlog.get(c, 0)}" for c in mv]
    L += ["", "## Counting detectors vs GDOT counts", "",
          "| Movement | GDOT count | sim detectors (counting set) | per lane | other movements on those detectors | stop-bar per lane (this movement) |",
          "|---|---|---|---|---|---|"]
    for c, m in mv.items():
        kind = m["counted_at"]
        chans = [d for d in det["detectors"] if d["phase"] == m["phases"][0] and d["kind"] == kind
                 and "right" not in d.get("note", "")]
        own = [len(by_mv[(f"ch{d['ch']}", c)]) for d in chans]
        other = Counter()
        for d in chans:
            for (ch, col), ids in by_mv.items():
                if ch == f"ch{d['ch']}" and col != c:
                    other[col] += len(ids)
        sb = [len(by_mv[(f"ch{d['ch']}", c)]) for d in sorted(det["detectors"], key=lambda d: d["lane"])
              if d["phase"] == m["phases"][0] and d["kind"] == "stopbar" and "right" not in d.get("note", "")]
        L.append(f"| {c} | {counted[c]} | {sum(own)} | {' / '.join(map(str, own))} | "
                 f"{', '.join(f'{k} {v}' for k, v in other.items()) or '-'} | {' / '.join(map(str, sb))} |")
    (out / f"{date}{a.tag}.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
