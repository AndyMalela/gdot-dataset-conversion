"""List every signal in GDOT ATSPM (traffic.dot.ga.gov) with coordinates and available reports.

The ATSPM map page loads all signal pins from /ATSPM/Scripts/AddData.js; this script
downloads that file and turns it into a CSV.

Examples
    python3 tools/atspm_signals/atspm_signals.py                          # statewide -> signals_all.csv
    python3 tools/atspm_signals/atspm_signals.py --area atlanta --names   # -> signals_atlanta.csv
    python3 tools/atspm_signals/atspm_signals.py --bbox 33.83 -84.39 33.86 -84.35 --label buckhead --names

Output (in this folder)
    signals_<label>.csv   signal_id, name, lat, lon, region, has_tmc, metrics
    names_cache.csv       intersection names already looked up (one request per signal, done once)

Notes
    has_tmc = the signal is configured for Turning Movement Counts. It does not guarantee
    the data is there; use screen.py to check.
    The "atlanta" area is a rough bounding box around the City of Atlanta, not the city limits.
"""
import argparse
import csv
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE = "https://traffic.dot.ga.gov/ATSPM"
UA = {"User-Agent": "atspm-tmc-research-puller (academic research)", "X-Requested-With": "XMLHttpRequest"}
AREAS = {  # south, west, north, east
    "atlanta": (33.64, -84.55, 33.89, -84.29),
}
METRICS = {
    "1": "Purdue Phase Termination", "2": "Split Monitor", "3": "Pedestrian Delay",
    "4": "Preemption Details", "5": "Turning Movement Counts", "6": "Purdue Coordination Diagram",
    "7": "Approach Volume", "8": "Approach Delay", "9": "Arrivals on Red", "10": "Approach Speed",
    "11": "Yellow and Red Actuations", "12": "Purdue Split Failure", "17": "Timing and Actuation",
    "31": "Left Turn Gap Analysis", "32": "Wait Time",
}
PIN = re.compile(
    r"PinFilterCheck\([^)]*?,\s*(\d+),\s*(\d+),\s*'([^']*)',\s*'([^']*)'\)\)\s*\{"
    r"var pin\w+ = new Microsoft\.Maps\.Pushpin\(new Microsoft\.Maps\.Location\(([-\d.]+),\s*([-\d.]+)\)\);"
    r"pin\w+\.SignalID = '([^']+)'")


def get(url, timeout=120):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def dropdown(html, select_id):
    """{value: label} for a <select id=...> on the ATSPM home page."""
    m = re.search(rf'<select[^>]*id="{select_id}"[^>]*>(.*?)</select>', html, re.S)
    if not m:
        return {}
    return {v: t.strip() for v, t in re.findall(r'<option value="([^"]+)">([^<]*)', m.group(1))}


def load_signals():
    print("Downloading signal list (AddData.js, ~4 MB)...")
    js = get(f"{SITE}/Scripts/AddData.js")
    home = get(f"{SITE}/")
    regions = dropdown(home, "Regions")  # (jurisdiction labels are unreliable, e.g. Buckhead = "Cobb")
    out, seen = [], set()
    for region, _jur, _areas, actions, lat, lon, sid in PIN.findall(js):
        if sid in seen:
            continue
        seen.add(sid)
        ids = [a for a in dict.fromkeys(actions.split(",")) if a]  # de-duplicate, keep order
        out.append({
            "signal_id": sid, "name": "", "lat": float(lat), "lon": float(lon),
            "region": regions.get(region, region),
            "has_tmc": int("5" in ids),
            "metrics": "; ".join(METRICS.get(a, a) for a in sorted(ids, key=int)),
        })
    return out


def add_names(rows, sleep):
    cache_path = HERE / "names_cache.csv"
    cache = {}
    if cache_path.exists():
        cache = {r["signal_id"]: r["name"] for r in csv.DictReader(open(cache_path))}
    todo = [r for r in rows if r["signal_id"] not in cache]
    if todo:
        print(f"Looking up {len(todo)} intersection names (~{len(todo) * (sleep + 0.3) / 60:.0f} min)...")
    new = not cache_path.exists()
    with open(cache_path, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["signal_id", "name"])
        for k, r in enumerate(todo, 1):
            try:
                q = urllib.parse.urlencode({"signalID": r["signal_id"]})
                name = re.sub(r"\s+", " ", get(f"{SITE}/DefaultCharts/GetSignalLocation?{q}", 30)).strip()
            except Exception as e:
                print(f"  {r['signal_id']}: lookup failed ({e})", file=sys.stderr)
                continue
            cache[r["signal_id"]] = name
            w.writerow([r["signal_id"], name]); f.flush()
            if k % 100 == 0:
                print(f"  {k}/{len(todo)}")
            time.sleep(sleep)
    for r in rows:
        r["name"] = cache.get(r["signal_id"], "")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--area", choices=sorted(AREAS), help="preset bounding box")
    p.add_argument("--bbox", type=float, nargs=4, metavar=("SOUTH", "WEST", "NORTH", "EAST"))
    p.add_argument("--label", help="output name: signals_<label>.csv (default: area name, or 'all')")
    p.add_argument("--all-signals", action="store_true", help="keep signals without TMC (default: TMC only when filtering by area)")
    p.add_argument("--names", action="store_true", help="look up intersection names (1 request per signal, cached)")
    p.add_argument("--sleep", type=float, default=0.5, help="pause between name lookups, seconds")
    a = p.parse_args()

    rows = load_signals()
    print(f"  {len(rows)} signals statewide, {sum(r['has_tmc'] for r in rows)} with TMC")

    bbox = AREAS.get(a.area) if a.area else a.bbox
    label = a.label or a.area or ("bbox" if a.bbox else "all")
    if bbox:
        s, w, n, e = bbox
        rows = [r for r in rows if s <= r["lat"] <= n and w <= r["lon"] <= e]
        if not a.all_signals:
            rows = [r for r in rows if r["has_tmc"]]
        print(f"  {len(rows)} in {label} ({'all' if a.all_signals else 'TMC only'})")
    if a.names:
        add_names(rows, a.sleep)

    rows.sort(key=lambda r: int(r["signal_id"]) if r["signal_id"].isdigit() else 10**9)
    out = HERE / f"signals_{label}.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["signal_id"])
        w.writeheader()
        w.writerows(rows)
    print(f"-> {out.relative_to(HERE.parent.parent)}  ({len(rows)} signals)")


if __name__ == "__main__":
    main()
