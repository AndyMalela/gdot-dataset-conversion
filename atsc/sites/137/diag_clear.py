"""v3 diagnosis (train days only): how long a left-arrow / side-street stop-bar zone stays occupied after the
phase turns green, field vs simulation.

Field: cached train-day Timing & Actuation charts (tools/cache/tna_events, 5-min windows). For every green of the
phase whose zone is occupied at green start (+0.3 s), the time from green start until that occupancy ends
("clear time"; the waiting queue has left the zone). Also the share of greens that end with the zone occupied.
Simulation: the same quantities from the recorded stop-bar intervals, same days, 07:00-21:00.

    uv run python atsc/sites/137/diag_clear.py field
    uv run python atsc/sites/137/diag_clear.py sim [startupDelay ...]
"""
import json
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "tools" / "lanecheck"))
CACHE = REPO / "tools" / "cache" / "tna_events"
TRAIN = ["2026-03-03", "2026-03-05", "2026-03-10", "2026-03-12", "2026-03-18", "2026-03-24", "2026-03-31",
         "2026-04-08", "2026-04-14"]
ZONE = {1: "ch1", 3: "ch9", 5: "ch19", 7: "ch29", 4: "ch12", 8: "ch32"}   # phase -> its (through/left) lane zone
MERGE = 0.6


def merge(iv):
    m = []
    for a, b in sorted(iv):
        if m and a <= m[-1][1] + MERGE:
            m[-1] = (m[-1][0], max(m[-1][1], b))
        else:
            m.append((a, b))
    return m


def measure(greens, occ, edge=None):
    """greens [(a, b)], occ merged [(a, b)] -> (clear times, ends occupied, greens)"""
    clear, endocc, n = [], 0, 0
    for ga, gb in greens:
        n += 1
        if any(a <= gb <= b for a, b in occ):
            endocc += 1
        c = [(a, b) for a, b in occ if a <= ga + 0.3 <= b]
        if c and (edge is None or c[0][1] < edge):
            clear.append(c[0][1] - ga)
    return clear, endocc, n


def field():
    from tna_events import read
    days = {d.replace("-", "") for d in TRAIN}
    out = defaultdict(lambda: [[], 0, 0])
    for d in sorted(CACHE.glob("137_*_5m_p12345678")):
        if d.name.split("_")[1] not in days:
            continue
        for p in ZONE:
            try:
                r = read(d / f"{p:02d}.jpg", None)
            except Exception:                                   # noqa: BLE001
                continue
            rows = [row for row in r["rows"] if row["kind"] == "det"]
            if not rows:
                continue
            row = rows[0]                                       # through charts: T zone is drawn first, R second
            occ = merge(_pairs(row["on"], row["off"]))
            gs = []
            for a, b in r["green"]:
                if gs and a - gs[-1][1] < 1.0:
                    gs[-1] = (gs[-1][0], b)
                else:
                    gs.append((a, b))
            gs = [(a, b) for a, b in gs if a >= 1 and b <= 299]
            c, e, n = measure(gs, occ, edge=299)
            out[p][0] += c
            out[p][1] += e
            out[p][2] += n
    return out


def _pairs(on, off):
    out, offs = [], sorted(off)
    for a in sorted(on):
        b = next((x for x in offs if x >= a), None)
        out.append((a, b if b is not None else 300.0))
    return out


def sim_job(args):
    day, vt = args
    from atsc.sim.episode import run_window
    from atsc.sim.signal import actuated_from_site
    res = run_window(HERE, day, 7.0, 21.0, actuated_from_site(HERE), mode="plan", seed=1, record_events=True, vtype=vt)
    ev = res["events"]
    out = {}
    for p, ch in ZONE.items():
        occ = merge(ev["stopbar"][ch])
        gs = [(g["start"], g["end"]) for g in res["greens"] if g["phase"] == p and g["end"] == g["end"]]
        out[p] = measure(gs, occ)
    return out


def q(v, f):
    v = sorted(v)
    return v[int(f * (len(v) - 1))] if v else float("nan")


def show(name, out):
    for p in ZONE:
        c, e, n = out[p]
        print(f"{name} P{p} {ZONE[p]:5s} greens {n:5d} ends occupied {100 * e / max(n, 1):3.0f} % | clear n={len(c):4d} "
              f"p10 {q(c, .1):4.1f} p25 {q(c, .25):4.1f} med {q(c, .5):4.1f} p75 {q(c, .75):4.1f} p90 {q(c, .9):5.1f}")


def sim(delays):
    base = json.loads((HERE / "sim.json").read_text())["vtype"]
    for sd in delays:
        vt = dict(base, startupDelay=sd) if sd else dict(base)
        tot = defaultdict(lambda: [[], 0, 0])
        with ProcessPoolExecutor(9) as ex:
            for o in ex.map(sim_job, [(d, vt) for d in TRAIN]):
                for p, (c, e, n) in o.items():
                    tot[p][0] += c
                    tot[p][1] += e
                    tot[p][2] += n
        show(f"sim sd={sd}", tot)


if __name__ == "__main__":
    if sys.argv[1] == "field":
        show("field", field())
    else:
        sim([float(x) for x in sys.argv[2:]] or [0.0])
