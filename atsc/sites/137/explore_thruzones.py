"""Exploration (train days): side-street through zone geometry vs the field's zone behaviour.
Zone = u m upstream of the stop line + d m past it. Field (train-day T&A, diag_clear.py / measure_dropouts.py):
share of greens with the zone occupied at green start, clear time after green start, occupancy of activations
inside one own green (pass_s), dropout share.
    uv run python atsc/sites/137/explore_thruzones.py u,d [u,d ...]
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
for p in (REPO, REPO / "tools", REPO / "tools" / "lanecheck", HERE):
    sys.path.insert(0, str(p))
import diag_clear as DC  # noqa: E402
from measure_dropouts import is_dropout  # noqa: E402

TH = {"ch12": 4, "ch32": 8}
OUTDIR = HERE / "calibration_thruzones"


def job(args):
    day, tag, add = args
    os.environ["ATSC_DETECTORS_ADD_137"] = str(add)
    from atsc.sim.episode import run_window
    from atsc.sim.signal import actuated_from_site
    res = run_window(HERE, day, 7.0, 21.0, actuated_from_site(HERE), mode="plan", seed=1, record_events=True)
    G = defaultdict(list)
    for g in res["greens"]:
        if g["end"] == g["end"]:
            G[g["phase"]].append((g["start"], g["end"]))
    out = {}
    for ch, p in TH.items():
        occ = DC.merge(res["events"]["stopbar"][ch])
        clear, _, n = DC.measure(G[p], occ)
        ps = [b - a for a, b in occ if any(x <= a and b <= y for x, y in G[p])]
        drop = sum(is_dropout(a, b, G, (p,)) for a, b in occ)
        out[ch] = (clear, n, ps, drop, len(occ))
    return tag, out


def main(cfgs):
    from atsc.sim.detectors import build
    from atsc.sim.run import net_file
    det = json.loads((HERE / "detectors.json").read_text())
    OUTDIR.mkdir(exist_ok=True)
    adds = {}
    for u, d in cfgs:
        spec = json.loads(json.dumps(det))
        for x in spec["detectors"]:
            if f"ch{x['ch']}" in TH:
                x["zone_m"], x["into_junction"] = float(u), float(d)
        adds[(u, d)] = OUTDIR / f"thru_u{u}_d{d}.add.xml"
        build(HERE, net_file(HERE), adds[(u, d)], spec=spec)
    agg = defaultdict(lambda: defaultdict(lambda: [[], 0, [], 0, 0]))
    with ProcessPoolExecutor(22) as pool:
        for tag, out in pool.map(job, [(day, c, adds[c]) for c in cfgs for day in DC.TRAIN]):
            for ch, v in out.items():
                a = agg[tag][ch]
                a[0] += v[0]; a[1] += v[1]; a[2] += v[2]; a[3] += v[3]; a[4] += v[4]
    print("field: ch12 occ-at-start 0.29 clear med 3.1 pass_s 2.05 dropout 0.65 | ch32 0.28 3.2 3.52 0.61")
    for c in cfgs:
        line = f"u{c[0]} d{c[1]}:"
        for ch in TH:
            cl, n, ps, dr, na = agg[c][ch]
            line += (f" | {ch} occ-start {len(cl) / max(n, 1):.2f} clear {st.median(cl) if cl else float('nan'):.1f} "
                     f"pass {st.median(ps) if ps else float('nan'):.2f} drop {dr / max(na, 1):.2f}")
        print(line, flush=True)


if __name__ == "__main__":
    main([tuple(float(x) for x in a.split(",")) for a in sys.argv[1:]])
