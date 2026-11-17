"""Saturation discharge of 137's simulated network, per phase (TEST_PLAN.md amendment 1, F3).

    uv run python atsc/sites/137/sat_flow.py          -> table; writes sim.json "sat_flow_veh_h_lane"

HCM-style measurement on the simulation: for every protected green of a phase, the vehicles standing on its
stop-line lanes when the green starts (speed < 1 m/s) are followed until they leave the lane; the headways
between consecutive departures from the 5th queued vehicle onward are saturation headways. Pooled per phase over
the GDOT plan on every train weekday, 15:30-19:30 (the busiest train-day window). Saturation flow per lane =
3600 / mean headway. A phase with fewer than MIN_N headways takes the pooled value of its kind (left / through).
Train days only. Used by the queue estimate (MaxPressure, LSTDQ v2 state) and by Webster's design; nothing else.
"""
import json
import statistics as st
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
sys.path.insert(0, str(HERE))
WINDOW = (15.5, 19.5)
FIRST = 4            # headways from the 5th queued vehicle on (index 4 = 5th departure minus 4th)
MIN_N = 30


def job(day):
    from atsc.sim.episode import run_window
    from atsc.sim.signal import ActuatedPolicy, actuated_from_site
    base = actuated_from_site(HERE)

    class Meas(ActuatedPolicy):
        def __init__(self):
            super().__init__(base.passage, {k: list(v) for k, v in base.max_recall.items()})
            self.lanes, self.state, self.h = None, {}, defaultdict(list)

        def end_requests(self, sig):
            conn = sig.conn
            if self.lanes is None:                    # stop-line lane -> phases giving it a protected green
                self.lanes = defaultdict(set)
                for i, links in enumerate(conn.trafficlight.getControlledLinks(sig.tls)):
                    prot = sig.lp.get(i, (set(), set(), False))[0]
                    for ln in links:
                        self.lanes[ln[0]] |= set(prot)
            disp = sig.engine.display()
            for ln, prot in self.lanes.items():
                green = [p for p in prot if disp.get(p) == "G"]
                st_ = self.state.get(ln)
                on = set(conn.lane.getLastStepVehicleIDs(ln))
                if green and st_ is None:
                    q = sorted((v for v in on if conn.vehicle.getSpeed(v) < 1.0),
                               key=lambda v: -conn.vehicle.getLanePosition(v))
                    self.state[ln] = {"phase": green[0], "queue": q, "out": {}}
                elif green and st_:
                    for v in st_["queue"]:
                        if v not in on and v not in st_["out"]:
                            st_["out"][v] = sig.now
                elif not green and st_:
                    t = sorted(st_["out"].values())
                    self.h[st_["phase"]] += [b - a for a, b in zip(t[FIRST - 1:], t[FIRST:])]
                    self.state[ln] = None
            return super().end_requests(sig)

    pol = Meas()
    run_window(HERE, day, *WINDOW, pol, mode="plan", seed=1, warmup_s=900, drain_s=0)
    return dict(pol.h)


def main():
    from baselines import days
    ds = [str(d) for d in days("train")]
    h = defaultdict(list)
    with ProcessPoolExecutor(22) as pool:
        for r in pool.map(job, ds):
            for p, v in r.items():
                h[p] += v
    kind = lambda p: "left" if p % 2 else "through"         # NEMA: odd = left  # noqa: E731
    pooled = {k: [x for p, v in h.items() if kind(p) == k for x in v] for k in ("left", "through")}
    out, rows = {}, []
    for p in range(1, 9):
        v = h.get(p, [])
        src = v if len(v) >= MIN_N else (pooled[kind(p)] if len(pooled[kind(p)]) >= MIN_N else
                                          pooled["left"] + pooled["through"])
        s = round(3600 / st.mean(src)) if src else None
        out[str(p)] = s
        rows.append((p, kind(p), len(v), round(st.mean(v), 2) if v else "", s, "own" if len(v) >= MIN_N else
                     (f"pooled {kind(p)}" if len(pooled[kind(p)]) >= MIN_N else "pooled all")))
    print("| phase | kind | headways | mean headway s | sat flow veh/h/lane | source |\n|---|---|---|---|---|---|")
    for r in rows:
        print("| " + " | ".join(map(str, r)) + " |")
    for k, v in pooled.items():
        print(f"pooled {k}: {len(v)} headways, {3600 / st.mean(v):.0f} veh/h/lane" if v else f"pooled {k}: none")
    cal = json.loads((HERE / "sim.json").read_text())
    cal["sat_flow_veh_h_lane"] = out
    cal["sat_flow_source"] = (f"sat_flow.py (TEST_PLAN.md amendment 1, F3): simulated discharge, headways from the "
                              f"5th queued vehicle in protected greens, GDOT plan, {len(ds)} train weekdays "
                              f"{WINDOW[0]}-{WINDOW[1]} h")
    (HERE / "sim.json").write_text(json.dumps(cal, indent=1))


if __name__ == "__main__":
    main()
