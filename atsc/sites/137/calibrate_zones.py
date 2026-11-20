"""v3 step A2: stop-bar presence-zone length per zone, from the measured single-vehicle occupancy time.

    uv run python atsc/sites/137/calibrate_zones.py        -> table; writes detectors.json zone_m + rebuilds the add file

Why: attempt 9 (measured passage ~2 s) gapped out far more often than the field (V2 10/35). Gap-out depends on the
passage time AND on how long a vehicle keeps the zone occupied, i.e. the zone length, which GDOT does not publish
(12 m was assumed). The field occupancy of one free-moving vehicle is measured (intersections/137/counts/
presence_factors_1900.json "pass_s": median duration of activations that start and end inside one green of the
zone's phase, 72 train-day Timing & Actuation windows). The simulated zone gets the length whose simulated
median, measured the same way, is closest to the field value. Nothing here looks at gap-out shares or any other
validation statistic.

Grid: zone length L in GRID for every zone at once (zones on different lanes do not interact); GDOT plan,
06:00-22:00 on a fixed set of train weekdays. Zones without a field measurement (modelled-only P2/P6 zones, the WB
left zone counted by a count zone) keep the default.
"""
import json
import os
import statistics as st
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(HERE))
OUTDIR = HERE / "calibration_zones"
GRID = [8, 12, 16, 20, 24, 30, 36]
N_DAYS = 6
H0, H1 = 6, 22
FIELD = json.loads((REPO / "intersections/137/counts/presence_factors_1900.json").read_text())["pass_s"]
ZONE_MV = {"ch9": "NB_L", "ch32": "NB_T", "ch31": "NB_R", "ch29": "SB_L", "ch12": "SB_T", "ch11": "SB_R", "ch19": "EB_L"}


def job(args):
    day, L, add = args
    os.environ["ATSC_DETECTORS_ADD_137"] = str(add)
    from atsc.sim.episode import run_window
    from atsc.sim.signal import actuated_from_site
    res = run_window(HERE, day, float(H0), float(H1), actuated_from_site(HERE), mode="plan", seed=1, record_events=True)
    ev = res["events"]
    greens = defaultdict(list)
    for g in res["greens"]:
        if g["end"] == g["end"]:
            greens[g["phase"]].append((g["start"], g["end"]))
    phase_of = {d: p for p, ids in ev["stopbar_by_phase"].items() for d in ids}
    out = {}
    for ch in ZONE_MV:
        gs = greens[phase_of[ch]]
        out[ch] = [b - a for a, b in ev["stopbar"][ch] if H0 * 3600 <= a < H1 * 3600
                   and any(x <= a and b <= y for x, y in gs)]
    return L, out


def main():
    from atsc.sim.detectors import build
    from atsc.sim.run import net_file
    from baselines import days as split_days
    ds = [str(d) for d in split_days("train")]
    ds = ds[2:: max(1, len(ds) // N_DAYS)][:N_DAYS]
    OUTDIR.mkdir(exist_ok=True)
    adds = {}
    for L in GRID:
        adds[L] = OUTDIR / f"detectors_{L}m.add.xml"
        build(HERE, net_file(HERE), adds[L], zone_override=float(L))
    occ = defaultdict(lambda: defaultdict(list))
    with ProcessPoolExecutor(22) as pool:
        for L, out in pool.map(job, [(d, L, adds[L]) for L in GRID for d in ds]):
            for ch, v in out.items():
                occ[ch][L] += v
    print("days:", ds)
    print("zone  movement  field PASS s | sim median by zone length (m) | chosen")
    det = json.loads((HERE / "detectors.json").read_text())
    chosen = {}
    for ch, mv in ZONE_MV.items():
        sims = {L: st.median(v) if v else None for L, v in occ[ch].items()}
        f = FIELD.get(mv)
        best = min((L for L in GRID if sims.get(L) is not None), key=lambda L: abs(sims[L] - f))
        chosen[ch] = best
        print(f"{ch:5s} {mv:6s} {f:5.2f} | " + " ".join(f"{L}m:{sims[L]:.2f}" for L in GRID if sims.get(L)) + f" | {best} m")
    for d in det["detectors"]:
        c = f"ch{d['ch']}"
        if c in chosen:
            d["zone_m"] = float(chosen[c])
    det["zone_m_source"] = ("2026-11-20 v3 (calibrate_zones.py): per-zone length whose simulated single-vehicle "
                            "occupancy (median, activations inside one own green) matches the field's (pass_s, 72 "
                            f"train-day T&A windows); grid {GRID} m on {len(ds)} train weekdays; other zones keep "
                            f"stopbar_zone_m")
    (HERE / "detectors.json").write_text(json.dumps(det, indent=1))
    build(HERE, net_file(HERE), HERE / "network" / "detectors.add.xml")
    print("detectors.json zone_m written; network/detectors.add.xml rebuilt")


if __name__ == "__main__":
    main()
