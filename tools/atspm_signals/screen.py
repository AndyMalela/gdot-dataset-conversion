"""Screen signals for the stratified sample: pull a few days of TMC for each and summarize.

Reads a signals_<label>.csv from atspm_signals.py, downloads N typical weekdays
(Tue-Thu) per signal, and writes one row per signal with measured volume, turning
structure and data completeness. Downloads go into the same cache as atspm_tmc.py
(tools/cache/tmc/<signal>/), not into intersections/.

Examples
    python3 tools/atspm_signals/screen.py signals_atlanta.csv --days 2
    python3 tools/atspm_signals/screen.py signals_atlanta.csv --dates 2026-09-29 2026-09-30
    python3 tools/atspm_signals/screen.py signals_atlanta.csv --limit 5      # quick test
    python3 tools/atspm_signals/screen.py signals_atlanta.csv --rebuild      # summarize cache only

Safe to stop and re-run: cached days are skipped. ~12 s per signal-day at default pacing.

Output: screening_<label>.csv (in this folder), one row per signal. Volume metrics use
06:00-20:00 and valid (non-outage) bins only:
    days_with_data      days where the server returned any counts
    completeness_pct    valid bins / all bins, whole day, all screened days
    daytime_valid_pct   same, 06:00-20:00 only
    hourly_volume       mean vehicles/hour entering, 06:00-20:00
    peak_hour_volume    highest 60-min total among fully valid windows (median across days)
    peak_hour_time      start time of that window on the busiest day
    left_share          left-turn vehicles / all vehicles, from exclusive left-turn (_L) detectors
                        only; understated where lefts share a lane with throughs (see shared_lanes)
    major_share         share of the busier axis (EB+WB vs NB+SB)
    n_approaches        approaches with any detected movement (4 = all legs of a 4-leg intersection)
    n_movements         movement columns reported (e.g. 8 = L+T on 4 approaches)
    has_right           1 if any right-turn movement is detected
    shared_lanes        1 if any movement is a shared lane (TL / TR): left/through split unknown there
"""
import argparse
import csv
import datetime as dt
import gzip
import statistics
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import atspm_tmc as tmc  # noqa: E402

DAY_START, DAY_END = "06:00", "20:00"


def typical_weekdays(n):
    """The n most recent Tuesdays-Thursdays, ending yesterday."""
    d, out = dt.date.today() - dt.timedelta(days=1), []
    while len(out) < n:
        if d.weekday() in (1, 2, 3):
            out.append(d)
        d -= dt.timedelta(days=1)
    return sorted(out)


def summarize(sig, days, bin_size, min_run):
    folder = tmc.CACHE_ROOT / sig["signal_id"]
    base = {k: sig.get(k, "") for k in ("signal_id", "name", "lat", "lon")}
    base.update(days_screened=0, days_with_data=0)
    parsed_days = []
    for d in days:
        f = folder / "raw" / f"{d}_{bin_size}min.html.gz"
        if not f.exists():
            continue
        base["days_screened"] += 1
        p = tmc.parse(gzip.decompress(f.read_bytes()).decode())
        if p and any(sum(v) for _, v in p[1]):
            parsed_days.append((d, p))
    base["days_with_data"] = len(parsed_days)
    if not parsed_days:
        return base

    cols = sorted({c for _, (cs, _) in parsed_days for c in cs}, key=tmc.col_key)
    n_all = n_valid = n_day = n_day_valid = 0
    vol = left = major_ew = major_ns = 0
    peaks = []
    for d, (cs, rows) in parsed_days:
        mask = tmc.outage_mask(rows, min_run)
        n_all += len(rows)
        n_valid += len(rows) - sum(mask)
        best = (-1, "")
        for i, ((t, vals), out) in enumerate(zip(rows, mask)):
            if DAY_START <= t < DAY_END:
                n_day += 1
                if not out:
                    n_day_valid += 1
                    rec = dict(zip(cs, vals))
                    vol += sum(vals)
                    left += sum(v for c, v in rec.items() if c.endswith("_L"))
                    major_ew += sum(v for c, v in rec.items() if c[:2] in ("EB", "WB"))
                    major_ns += sum(v for c, v in rec.items() if c[:2] in ("NB", "SB"))
            win = 60 // bin_size
            if i + win <= len(rows) and not any(mask[i:i + win]):
                s = sum(sum(v) for _, v in rows[i:i + win])
                best = max(best, (s, t))
        if best[0] >= 0:
            peaks.append(best)

    hours = n_day_valid * bin_size / 60
    base.update(
        completeness_pct=round(100 * n_valid / n_all, 1),
        daytime_valid_pct=round(100 * n_day_valid / n_day, 1) if n_day else "",
        hourly_volume=round(vol / hours) if hours else "",
        peak_hour_volume=round(statistics.median(p[0] for p in peaks)) if peaks else "",
        peak_hour_time=max(peaks)[1] if peaks else "",
        left_share=round(left / vol, 3) if vol else "",
        major_share=round(max(major_ew, major_ns) / (major_ew + major_ns), 3) if major_ew + major_ns else "",
        n_approaches=len({c.split('_')[0] for c in cols}),
        n_movements=len(cols),
        has_right=int(any(c.endswith("_R") or c.endswith("TR") for c in cols)),
        shared_lanes=int(any(c.split('_')[1] in ('TL', 'TR') for c in cols)),
        movements=" ".join(cols),
    )
    return base


FIELDS = ["signal_id", "name", "lat", "lon", "days_screened", "days_with_data", "completeness_pct",
          "daytime_valid_pct", "hourly_volume", "peak_hour_volume", "peak_hour_time", "left_share",
          "major_share", "n_approaches", "n_movements", "has_right", "shared_lanes", "movements"]


def write(out, results):
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, restval="")
        w.writeheader()
        w.writerows(results)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("signals_csv", help="signals_<label>.csv from atspm_signals.py (path or name in this folder)")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--days", type=int, default=2, help="number of recent Tue-Thu days (default 2)")
    g.add_argument("--dates", type=dt.date.fromisoformat, nargs="+", help="explicit dates, YYYY-MM-DD")
    p.add_argument("--limit", type=int, help="only the first N signals (for testing)")
    p.add_argument("--sleep", type=float, default=5.0, help="pause between requests, seconds (default 5)")
    p.add_argument("--outage-bins", type=int, default=3)
    p.add_argument("--rebuild", action="store_true", help="don't download; summarize cached days only")
    a = p.parse_args()

    src = Path(a.signals_csv)
    if not src.exists():
        src = HERE / a.signals_csv
    signals = list(csv.DictReader(open(src)))[: a.limit]
    days = sorted(a.dates) if a.dates else typical_weekdays(a.days)
    label = src.stem.replace("signals_", "")
    out = HERE / f"screening_{label}.csv"
    bin_size = 5

    todo = [] if a.rebuild else [
        (s, d) for s in signals for d in days
        if not (tmc.CACHE_ROOT / s["signal_id"] / "raw" / f"{d}_{bin_size}min.html.gz").exists()]
    print(f"{len(signals)} signals x {len(days)} days ({', '.join(map(str, days))})")
    print(f"{len(todo)} downloads needed (~{len(todo) * (7 + a.sleep) / 3600:.1f} h); output -> {out.name}")

    t_start = time.time()
    for k, (s, d) in enumerate(todo, 1):
        folder = tmc.CACHE_ROOT / s["signal_id"] / "raw"
        folder.mkdir(parents=True, exist_ok=True)
        try:
            html = tmc.fetch_day(s["signal_id"], d, bin_size)
            (folder / f"{d}_{bin_size}min.html.gz").write_bytes(gzip.compress(html.encode()))
            note = "ok"
        except Exception as e:
            note = f"FAILED ({e})"
        eta = (time.time() - t_start) / k * (len(todo) - k) / 60
        print(f"  [{k}/{len(todo)}] {s['signal_id']} {d}  {note}   ~{eta:.0f} min left")
        if k % 50 == 0:  # write progress so partial results are usable
            write(out, [summarize(x, days, bin_size, a.outage_bins) for x in signals])
        if k < len(todo):
            time.sleep(a.sleep)

    results = [summarize(s, days, bin_size, a.outage_bins) for s in signals]
    write(out, results)
    covered = [r for r in results if r.get("daytime_valid_pct") not in ("", None) and r["daytime_valid_pct"] >= 90]
    print(f"-> {out.relative_to(HERE.parent.parent)}  "
          f"({sum(r['days_with_data'] > 0 for r in results)}/{len(results)} signals returned data, "
          f"{len(covered)} with >=90% daytime coverage, "
          f"{sum(r['n_approaches'] >= 4 for r in covered)} of those with 4+ approaches detected)")


if __name__ == "__main__":
    main()
