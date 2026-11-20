"""v3 step A4 (attempt 12): how far each left-turn zone reaches back from the stop line.

    uv run python atsc/sites/137/calibrate_leftzones.py      -> table; writes detectors.json zone_m + rebuilds the add file

The left zones keep their junction part (stop line to SUMO's waiting point for permissive turners, attempt 11) and
reach u m upstream of the stop line. Measurement (train days): occupancy of activations that START in the
permissive period (the permissive phase is green, the arrow is not), i.e. turners passing or waiting for a gap.
Field: cached train-day Timing & Actuation charts; simulation: the same definition, 07:00-21:00 of the same days.
Rule (fixed before running): per zone, the u whose simulated median is closest to the field median.
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
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "tools" / "lanecheck"))
import diag_clear as DC  # noqa: E402

GRID = [0, 3, 6, 9, 12]
PERM = {1: 2, 5: 2, 3: 8, 7: 4}                      # GDOT approaches.csv permissive phase
ZONE = {1: "ch1", 5: "ch19", 3: "ch9", 7: "ch29"}
OUTDIR = HERE / "calibration_leftzones"


def _greens(r):
    gs = []
    for a, b in r["green"]:
        if gs and a - gs[-1][1] < 1.0:
            gs[-1] = (gs[-1][0], b)
        else:
            gs.append((a, b))
    return gs


def _in(t, G):
    return any(a <= t <= b for a, b in G)


def perm_durations(occ, G, p, edge=None):
    return [b - a for a, b in occ if (edge is None or (1 < a and b < edge))
            and _in(a, G[PERM[p]]) and not _in(a, G[p])]


def field():
    from tna_events import read
    days = {d.replace("-", "") for d in DC.TRAIN}
    out = defaultdict(list)
    for d in sorted(DC.CACHE.glob("137_*_5m_p12345678")):
        if d.name.split("_")[1] not in days:
            continue
        try:
            rr = {p: read(d / f"{p:02d}.jpg", None) for p in (1, 2, 3, 4, 5, 7, 8)}
        except Exception:                                       # noqa: BLE001
            continue
        G = {p: _greens(r) for p, r in rr.items()}
        for p in PERM:
            rows = [row for row in rr[p]["rows"] if row["kind"] == "det"]
            if rows:
                out[p] += perm_durations(DC.merge(DC._pairs(rows[0]["on"], rows[0]["off"])), G, p, edge=299)
    return out


def job(args):
    day, u, add = args
    os.environ["ATSC_DETECTORS_ADD_137"] = str(add)
    from atsc.sim.episode import run_window
    from atsc.sim.signal import actuated_from_site
    res = run_window(HERE, day, 7.0, 21.0, actuated_from_site(HERE), mode="plan", seed=1, record_events=True)
    G = defaultdict(list)
    for g in res["greens"]:
        if g["end"] == g["end"]:
            G[g["phase"]].append((g["start"], g["end"]))
    return u, {p: perm_durations(DC.merge(res["events"]["stopbar"][ch]), G, p) for p, ch in ZONE.items()}


def main():
    from atsc.sim.detectors import build
    from atsc.sim.run import net_file
    f = field()
    det = json.loads((HERE / "detectors.json").read_text())
    OUTDIR.mkdir(exist_ok=True)
    adds = {}
    for u in GRID:
        spec = json.loads(json.dumps(det))
        for d in spec["detectors"]:
            if f"ch{d['ch']}" in ZONE.values():
                d["zone_m"] = float(u)
        adds[u] = OUTDIR / f"detectors_u{u}.add.xml"
        build(HERE, net_file(HERE), adds[u], spec=spec)
    sim = defaultdict(lambda: defaultdict(list))
    with ProcessPoolExecutor(22) as pool:
        for u, out in pool.map(job, [(d, u, adds[u]) for u in GRID for d in DC.TRAIN]):
            for p, v in out.items():
                sim[p][u] += v
    print("zone  field median (n) | sim median by upstream extent u (m) | chosen")
    chosen = {}
    for p, ch in ZONE.items():
        fm = st.median(f[p])
        meds = {u: st.median(sim[p][u]) for u in GRID if sim[p][u]}
        best = min(meds, key=lambda u: (abs(meds[u] - fm), u))
        chosen[ch] = best
        print(f"P{p} {ch:5s} {fm:4.1f} ({len(f[p])}) | " + " ".join(f"u{u}:{meds[u]:.1f}" for u in meds) + f" | {best} m")
    for d in det["detectors"]:
        if f"ch{d['ch']}" in chosen:
            d["zone_m"] = float(chosen[f"ch{d['ch']}"])
    det["left_zone_upstream_source"] = ("2026-11-20 v3 attempt 12 (calibrate_leftzones.py): left zones = junction part to "
                                        "the waiting point + zone_m upstream of the stop line, chosen so the simulated "
                                        "median occupancy of permissive-period activations matches the field's "
                                        f"(train-day T&A, {len(DC.TRAIN)} days); grid {GRID} m")
    (HERE / "detectors.json").write_text(json.dumps(det, indent=1))
    build(HERE, net_file(HERE), HERE / "network" / "detectors.add.xml")
    print("detectors.json zone_m written; network/detectors.add.xml rebuilt")


if __name__ == "__main__":
    main()
