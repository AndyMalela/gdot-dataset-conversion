"""v3 step B: calibrate queue discharge (saturation flow) of the driver model.

    uv run python atsc/sites/137/calibrate_discharge.py          -> table; writes sim.json vtype.tau + source

Why a standard target: GDOT ATSPM shows no per-vehicle stop-line count for any 137 phase in Timing & Actuation
(probe 2026-11-20: lane-by-lane count zones 13769/13775 are not drawn; presence zones merge a discharging queue
into one activation), so the field saturation headway cannot be measured here. The target is therefore the HCM
base saturation flow, 1,900 veh/h/lane (headway 1.895 s) — the same value the presence-zone undercount estimate
uses, so demand estimation and simulated discharge are now consistent (PIPELINE_PLAN.md W2).

Measurement (as sat_flow.py): GDOT plan, 15:30-19:30, headways from the 5th queued vehicle in protected greens,
pooled over through phases, on a fixed set of train weekdays. Grid over SUMO's `tau` (desired time headway,
default 1.0 s); impatience stays at its calibrated 0.5. Rule (fixed before running): the tau whose pooled through
saturation flow is closest to 1,900; ties within 25 veh/h go to the smaller change from default.
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
import sat_flow  # noqa: E402

TARGET = 1900
TAUS = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5]
N_DAYS = 8


def job(args):
    day, tau, *extra = args                      # extra: optional dict of further vType attributes
    import atsc.sim.episode as ep
    cal = json.loads((HERE / "sim.json").read_text())
    vt = dict(cal.get("vtype", {}), tau=tau, **(extra[0] if extra else {}))
    orig = ep.run_window

    def with_vtype(*a, **k):                  # sat_flow.job imports run_window at call time: give it this vtype
        k["vtype"] = vt
        return orig(*a, **k)
    ep.run_window = with_vtype
    try:
        h = sat_flow.job(day)
    finally:
        ep.run_window = orig
    return tau, h


def main():
    from baselines import days
    ds = [str(d) for d in days("train")]
    ds = ds[:: max(1, len(ds) // N_DAYS)][:N_DAYS]
    jobs = [(d, t) for t in TAUS for d in ds]
    res = defaultdict(lambda: defaultdict(list))
    with ProcessPoolExecutor(22) as pool:
        for tau, h in pool.map(job, jobs):
            for p, v in h.items():
                res[tau][p] += v
    rows = []
    for tau in TAUS:
        thr = [x for p, v in res[tau].items() if p % 2 == 0 for x in v]
        lef = [x for p, v in res[tau].items() if p % 2 == 1 for x in v]
        s_thr = 3600 / st.mean(thr) if thr else None
        s_lef = 3600 / st.mean(lef) if lef else None
        rows.append((tau, len(thr), s_thr, len(lef), s_lef))
        print(f"tau {tau:.1f}: through {s_thr:.0f} veh/h/ln (n={len(thr)}), left {s_lef:.0f} (n={len(lef)})", flush=True)
    best = min(rows, key=lambda r: (abs(r[2] - TARGET), r[0]))
    near = [r for r in rows if abs(r[2] - TARGET) <= abs(best[2] - TARGET) + 25]
    chosen = min(near, key=lambda r: abs(r[0] - 1.0))
    print(f"chosen tau {chosen[0]} (through {chosen[2]:.0f}, left {chosen[4]:.0f})")
    cal = json.loads((HERE / "sim.json").read_text())
    cal.setdefault("vtype", {})["tau"] = chosen[0]
    cal["vtype_tau_source"] = (f"2026-11-20 v3 step B (calibrate_discharge.py): HCM base 1,900 veh/h/ln target (field "
                               f"headways not measurable at 137); grid {TAUS} on {len(ds)} train weekdays 15:30-19:30; "
                               f"through {chosen[2]:.0f}, left {chosen[4]:.0f} veh/h/ln at tau {chosen[0]}")
    cal["discharge_grid"] = [{"tau": r[0], "through_veh_h_ln": round(r[2]), "left_veh_h_ln": round(r[4]),
                              "n_through": r[1], "n_left": r[3]} for r in rows]
    (HERE / "sim.json").write_text(json.dumps(cal, indent=1))


if __name__ == "__main__":
    main()
