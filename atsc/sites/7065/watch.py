"""Watch SIG 7065 in sumo-gui: real demand of any non-locked day, any controller, same engine as the experiments.

    uv run python atsc/sites/7065/watch.py 2026-09-02                       # GDOT plans, 17:00-18:00
    uv run python atsc/sites/7065/watch.py 2026-09-02 --from 7:30 --to 9 --controller actuated
    uv run python atsc/sites/7065/watch.py 2026-09-02 --controller webster
    uv run python atsc/sites/7065/watch.py 2026-09-02 --controller lstdq --it 5

In the window: the delay slider sets the speed (0 = as fast as possible); right-click a detector or vehicle
for its values. The terminal prints the plan, the phases shown and each ended green as it happens.
"""
import argparse
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
from atsc.sim import demand, run  # noqa: E402
from atsc.sim.signal import FixedPolicy, SumoSignal, actuated_from_site  # noqa: E402


def hours(s):
    h, _, m = s.partition(":")
    return int(h) + int(m or 0) / 60


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("date")
    ap.add_argument("--from", dest="b", default="17:00")
    ap.add_argument("--to", dest="e", default="18:00")
    ap.add_argument("--controller", default="gdot", choices=["gdot", "actuated", "webster", "lstdq"])
    ap.add_argument("--it", type=int, help="LSTDQ iteration (lstdq/w_it<k>.npy)")
    ap.add_argument("--warmup", type=float, default=10, help="minutes simulated before the window")
    ap.add_argument("--nogui", action="store_true", help="run without the window (test)")
    a = ap.parse_args()
    b0, b1 = hours(a.b) * 3600, hours(a.e) * 3600
    cal = json.loads((HERE / "sim.json").read_text())
    with tempfile.TemporaryDirectory() as tmp:
        rou = Path(tmp) / "d.rou.xml"
        demand.write_routes(HERE, run.net_file(HERE), a.date, rou, vtype=cal["vtype"])
        extra = [] if a.nogui else ["--gui-settings-file", str(HERE / "network" / "view.xml"), "--start"]
        conn = run.start(HERE, rou, max(0, b0 - a.warmup * 60), b1, gui=not a.nogui, step=cal["step"], extra=extra)
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
        shown = 0
        try:
            while conn.simulation.getTime() < b1:
                conn.simulationStep()
                sig.step()
                for g in sig.engine.greens[shown:]:
                    t = int(g.end)
                    print(f"{t // 3600:02d}:{t % 3600 // 60:02d}:{t % 60:02d}  plan {sig._cur_plan_name or '-':4s} "
                          f"P{g.phase} green {g.green:5.1f} s  ({g.how})", flush=True)
                shown = len(sig.engine.greens)
        except Exception as e:                          # closing the window ends the run
            print(f"stopped: {e.__class__.__name__}")
        finally:
            try:
                conn.close()
            except Exception:
                pass


if __name__ == "__main__":
    main()
