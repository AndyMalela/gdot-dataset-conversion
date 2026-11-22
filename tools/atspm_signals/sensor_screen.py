"""Screen GDOT signals by what their detectors can COUNT (site selection for fully measured models).

    uv run python tools/atspm_signals/sensor_screen.py --region "District 7"      # metro Atlanta
    uv run python tools/atspm_signals/sensor_screen.py --all
    uv run python tools/atspm_signals/sensor_screen.py --rebuild                  # summarize the cache only

Input: signals_all.csv (atspm_signals.py); only signals with Turning Movement Counts, Timing and Actuation and
Split Monitor. One request per signal: the ATSPM configuration table (same as tools/atspm_config.py), cached
gzipped in tools/cache/config/<id>.html.gz; safe to stop and re-run. Pacing ~3 s between requests.

Why (MODEL_LOG.md of site 137): a turning movement is only known when a detector counts MOVING vehicles. Per
movement group (approach x movement type of the vehicle lanes; right-only lanes left out, rights are inferred at
every site because of right turn on red) the best count source is graded:
  A  count from moving vehicles: count-only zone/loop (Lane-by-lane Count without Stop Bar Presence) or an
     Advanced Count detector on that approach's through movement
  B  inductive loop that is count + stop-bar presence on one channel (no radar dropouts; queues may merge)
  C  radar zone that is count + stop-bar presence (137's problem: queues merge AND stopped cars are dropped)
  -  nothing counts it
Exit-lane count zones are listed separately (they count a leg's departures, i.e. a mix of movements).

Output: sensor_screening.csv (this folder), one row per signal, ranked: every group A or B first, then by number
of C/- groups, then by hardware (loops first).
"""
import argparse
import csv
import gzip
import re
import sys
import time
import urllib.parse
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from atspm_config import BASE, _request, as_records, tables  # noqa: E402

CACHE = ROOT / "tools" / "cache" / "config"
OUT = HERE / "sensor_screening.csv"
NEED = ("Timing and Actuation", "Split Monitor")


def candidates(region=None):
    rows = list(csv.DictReader(open(HERE / "signals_all.csv")))
    return [r for r in rows if r["has_tmc"] == "1" and all(n in r["metrics"] for n in NEED)
            and (region is None or r["region"] == region)]


def config_html(sig):
    f = CACHE / f"{sig}.html.gz"
    if f.exists():
        return gzip.decompress(f.read_bytes()).decode("utf-8"), False
    html = _request(f"{BASE}/ConfigurationTable?" + urllib.parse.urlencode({"SignalID": sig}))
    CACHE.mkdir(parents=True, exist_ok=True)
    f.write_bytes(gzip.compress(html.encode("utf-8")))
    return html, True


def grade(det):
    """detector records -> summary dict"""
    groups = defaultdict(set)              # (direction, movement) -> grades
    hw, exits = Counter(), Counter()
    adv_dirs = set()
    for d in det:
        types = d.get("Detection Types", "")
        h = d.get("Detection Hardware", "").strip() or "?"
        hw[h] += 1
        mv = d.get("Movement Type", "").strip()
        dr = d.get("Direction", "").strip()
        if d.get("Enabled", "True") == "False":
            continue
        if d.get("Lane Type", "") == "Exit":
            exits[dr] += 1
            continue
        if "Advanced Count" in types:
            adv_dirs.add(dr)
        if not mv or mv == "Right":
            continue
        cnt = "Lane-by-lane Count" in types or "Advanced Count" in types
        pres = "Stop Bar Presence" in types
        loop = "Loop" in h
        g = "A" if cnt and not pres else ("B" if cnt and loop else ("C" if cnt else "-"))
        groups[(dr, mv)].add(g)
    for (dr, mv) in list(groups):                     # an advance count covers its approach's through movement
        if dr in adv_dirs and "Thru" in mv and "Left" not in mv:
            groups[(dr, mv)].add("A")
    # best grade per group ("A" < "B" < "C"); "-" only when nothing counts it
    best = {k: (min(x for x in groups[k] if x != "-") if groups[k] - {"-"} else "-") for k in groups}
    c = Counter(best.values())
    return {"groups": len(best), "A": c["A"], "B": c["B"], "C": c["C"], "none": c["-"],
            "all_A_or_B": int(len(best) > 0 and c["C"] == 0 and c["-"] == 0),
            "hardware": "; ".join(f"{k} {v}" for k, v in hw.most_common()),
            "exit_legs": len(exits),
            "detail": " ".join(f"{dr}_{mv.replace('-', '')}:{g}" for (dr, mv), g in sorted(best.items()))}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--region")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--rebuild", action="store_true", help="no requests; use cached tables only")
    a = ap.parse_args()
    sigs = candidates(None if (a.all or a.rebuild) else a.region)
    rows, fetched, failed = [], 0, 0
    for i, s in enumerate(sigs):
        sid = s["signal_id"]
        if a.rebuild and not (CACHE / f"{sid}.html.gz").exists():
            continue
        try:
            html, new = config_html(sid)
        except Exception as e:                                   # noqa: BLE001
            failed += 1
            print(f"[{i + 1}/{len(sigs)}] {sid} FAILED {e}", flush=True)
            if "rejected" in str(e).lower():
                time.sleep(300)
            continue
        if new:
            fetched += 1
            time.sleep(3)
        try:
            t = tables(html)
            det = as_records(t[0]) if t and len(t[0]) > 1 else []
        except ValueError:
            det = []
        if not det:
            continue
        g = grade(det)
        rows.append({"signal_id": sid, "name": s.get("name", ""), "lat": s["lat"], "lon": s["lon"],
                     "region": s["region"], "jurisdiction": s.get("jurisdiction", ""), "detectors": len(det), **g})
        if new and fetched % 50 == 0:
            print(f"[{i + 1}/{len(sigs)}] fetched {fetched}, failed {failed}", flush=True)
    loops_first = lambda r: 0 if "Loop" in r["hardware"].split(";")[0] else 1  # noqa: E731
    rows.sort(key=lambda r: (-r["all_A_or_B"], r["C"] + r["none"], -r["A"], loops_first(r)))
    if rows:
        with open(OUT, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    print(f"{len(rows)} signals screened ({fetched} fetched, {failed} failed) -> {OUT}")
    print("all movement groups counted (A/B):", sum(r["all_A_or_B"] for r in rows))


if __name__ == "__main__":
    main()
