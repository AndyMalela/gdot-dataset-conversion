"""Watch SIG 7065 in sumo-gui with any controller on any prepared day (EXP-009 data).

  uv run python tools/watch.py rl      --day 2026-10-02 --from 16:00 --to 18:00
  uv run python tools/watch.py webster --day 2026-10-02 --from 16:00
  uv run python tools/watch.py real    --day 2026-09-26            # Saturday, GDOT weekend plans
  uv run python tools/watch.py real-fixed --day 2026-10-02 --rep 3

Controllers: real (GDOT timing, actuated), real-fixed (GDOT timing, fixed, exact phase order),
webster (dual ring + pedestrian minimums), rl (dual-ring LSTDQ; --seed, default = best on validation).
The network starts empty at --from, so give it ~15 min of warm-up before judging queues.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
E9 = ROOT / "rlagent" / "experiments" / "EXP-009_significance"
NET = ROOT / "sumotwin" / "7065_ext.net.xml"
VIEW = ROOT / "intersections" / "7065" / "sim" / "view.xml"


def secs(hm):
    h, m = hm.split(":")
    return int(h) * 3600 + int(m) * 60


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("controller", choices=["real", "real-fixed", "webster", "rl"])
    ap.add_argument("--day", default="2026-10-02", help="a prepared day (see EXP-009 data/demand)")
    ap.add_argument("--rep", type=int, default=0, help="demand replication (0 = base draw)")
    ap.add_argument("--from", dest="begin", default="16:00")
    ap.add_argument("--to", dest="end", default="19:00")
    ap.add_argument("--seed", type=int, default=None, help="RL training seed (default: best on validation)")
    a = ap.parse_args()

    rou = E9 / "data" / "demand" / f"{a.day}_r{a.rep}.rou.xml"
    if not rou.exists():
        days = sorted({p.name.split("_r")[0] for p in (E9 / "data" / "demand").glob("*.rou.xml")})
        sys.exit(f"no demand for {a.day} r{a.rep}. Prepared days: {', '.join(days)}")
    b, e = secs(a.begin), secs(a.end)

    if a.controller == "rl":
        sys.path.insert(0, str(ROOT / "rlagent"))
        import numpy as np
        from dualring_env import DualRingEnv, N_ACTIONS
        from lstdq import LinearQ
        seed = a.seed
        if seed is None:
            seed = json.loads((E9 / "results.json").read_text())["best_seed"]
        w = np.load(E9 / "data" / "train" / f"s{seed}" / f"weights_s{seed}.npy")
        env = DualRingEnv(str(rou), begin=b, end=e, seed=9999 + a.rep, gui=True, gui_settings=str(VIEW))
        try:
            obs = env.reset()
        except Exception as ex:
            sys.exit(f"sumo-gui failed to start ({ex.__class__.__name__}). Check that plain `sumo-gui` opens; "
                     "an 'X Error ... BadValue' means a graphics-driver problem (e.g. NVIDIA driver updated "
                     "without a reboot) -- reboot and retry.")
        agent = LinearQ(env.n_state_features, N_ACTIONS)
        agent.w = w
        done = False
        try:
            while not done:
                r = env.step(agent.greedy(obs), compute_reward=False)
                obs, done = r.state, r.done
        except Exception:
            pass                                    # window closed
        env.close()
        return

    sig = E9 / "data" / "signals"
    add = {"real": sig / f"real_nema_{a.day}.add.xml", "real-fixed": sig / f"real_fixed_{a.day}.add.xml",
           "webster": sig / "webster.add.xml"}[a.controller]
    if not add.exists():
        sys.exit(f"no {a.controller} signal file for {a.day} (real timing exists for validation/test days and Saturdays)")
    subprocess.run(["sumo-gui", "-n", str(NET), "-r", str(rou), "-a", str(add), "--begin", str(b), "--end", str(e),
                    "--seed", str(9999 + a.rep), "--time-to-teleport", "300", "--no-step-log",
                    "--gui-settings-file", str(VIEW), "--start"])


if __name__ == "__main__":
    main()
