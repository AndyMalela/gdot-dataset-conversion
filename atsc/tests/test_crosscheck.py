"""Engine + link mapping vs the static fixed-time program of tools/build_sim.py (EXP-007..009):
every GDOT plan, all phases called, must give every signal link the same time per state per cycle."""
import collections
import sys
from pathlib import Path

import pytest

from atsc.sim.nema import NemaEngine, Phase, Plan
from atsc.sim.signal import link_state, load_site

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import build_sim as B  # noqa: E402

SITE = ROOT / "atsc/sites/7065"
sig, _, LP, N = load_site(SITE, SITE / "network/7065v2.net.xml")
PH = {int(k): Phase(v["min_green"], v["yellow"], v["red"], v["ped_min"], recall=v["recall"]) for k, v in sig["phases"].items()}
RINGS = {int(r): tuple(tuple(g) for g in gs) for r, gs in sig["rings"].items()}


@pytest.mark.parametrize("name", sorted(sig["plans"]))
def test_plan_matches_static_program(name):
    p = sig["plans"][name]
    splits = {int(k): v for k, v in p["splits"].items()}
    C = p["cycle"]
    eng = NemaEngine(RINGS, PH, Plan(name, C, splits), skip_uncalled=False)
    a, t = collections.Counter(), 0.0
    while t < 3 * C - 1e-9:
        st = link_state(eng.tick(t, set(range(1, 9)), set()), LP, N)
        if C <= t < 2 * C:
            for i, c in enumerate(st):
                a[(i, c)] += 0.1
        t = round(t + 0.1, 6)
    y = {q: ph.yellow for q, ph in PH.items()}
    r = {q: ph.red for q, ph in PH.items()}
    tl, cyc = B.ring_timeline(splits, y, r, {"1/2": 2, "5/6": 5, "3/4": 3, "7/8": 7})
    b = collections.Counter()
    cuts = sorted({0.0, cyc} | {x for rr in tl.values() for seg in rr for x in seg[:2]})
    for t0, t1 in zip(cuts[:-1], cuts[1:]):
        active = {q: s for segs in tl.values() for s0, s1, q, s in segs if s0 <= (t0 + t1) / 2 < s1}
        for i, c in enumerate(link_state(active, LP, N)):
            b[(i, c)] += t1 - t0
    assert max(abs(a[k] - b[k]) for k in set(a) | set(b)) < 0.15
