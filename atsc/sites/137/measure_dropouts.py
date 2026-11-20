"""Share of stop-bar zone activations that are radar dropouts (VALIDATION.md, finding 2026-11-20).

    uv run python atsc/sites/137/measure_dropouts.py     -> intersections/137/counts/presence_dropouts.json

An activation that starts and ends while its movement has no green (own or permissive phase green, or the 3 s
after it) and spans no green start cannot be a vehicle leaving: a stopped vehicle lost and found again by the
radar. Field: cached train-day Timing & Actuation charts. Used by calibrate_demand.py (attempt 13).
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
for p in (REPO, REPO / "tools", REPO / "tools" / "lanecheck", HERE):
    sys.path.insert(0, str(p))
import diag_clear as DC  # noqa: E402

# movement -> (zone, chart phase, phases whose green lets it go)
ZONES = {"EB_L": ("ch19", 5, (5, 2)), "NB_L": ("ch9", 3, (3, 8)), "SB_L": ("ch29", 7, (7, 4)),
         "SB_T": ("ch12", 4, (4,)), "NB_T": ("ch32", 8, (8,))}
MARGIN = 3.0


def is_dropout(a, b, G, go):
    near = lambda t: any(x <= t <= y + MARGIN for p in go for x, y in G.get(p, []))  # noqa: E731
    return not near(a) and not near(b) and not any(a <= x <= b for p in go for x, _ in G.get(p, []))


def greens(r):
    gs = []
    for a, b in r["green"]:
        if gs and a - gs[-1][1] < 1.0:
            gs[-1] = (gs[-1][0], b)
        else:
            gs.append((a, b))
    return gs


def main():
    from tna_events import read
    days = {d.replace("-", "") for d in DC.TRAIN}
    n, fl = defaultdict(int), defaultdict(int)
    for d in sorted(DC.CACHE.glob("137_*_5m_p12345678")):
        if d.name.split("_")[1] not in days:
            continue
        try:
            rr = {p: read(d / f"{p:02d}.jpg", None) for p in (2, 3, 4, 5, 7, 8)}
        except Exception:                                       # noqa: BLE001
            continue
        G = {p: greens(r) for p, r in rr.items()}
        for m, (ch, cp, go) in ZONES.items():
            rows = [row for row in rr[cp]["rows"] if row["kind"] == "det"]
            if not rows:
                continue
            for a, b in DC.merge(DC._pairs(rows[0]["on"], rows[0]["off"])):
                if a <= 1 or b >= 299:
                    continue
                n[m] += 1
                fl[m] += is_dropout(a, b, G, go)
    out = {"share": {m: round(fl[m] / n[m], 3) for m in ZONES}, "n": dict(n), "dropouts": dict(fl),
           "days": DC.TRAIN, "source": "atsc/sites/137/measure_dropouts.py: train-day T&A charts; activation that "
           f"starts and ends with no green for its movement (+{MARGIN} s) and spans no green start"}
    (REPO / "intersections/137/counts/presence_dropouts.json").write_text(json.dumps(out, indent=1))
    print(out["share"], out["n"])


if __name__ == "__main__":
    main()
