"""Download turning movement counts (TMC) from GDOT ATSPM (traffic.dot.ga.gov).

Examples
    python3 tools/atspm_tmc.py 7065                            # yesterday
    python3 tools/atspm_tmc.py 7065 183 --days 30 --weekdays   # last 30 days, Mon-Fri only
    python3 tools/atspm_tmc.py 7065 --start 2026-09-01 --end 2026-09-30
    python3 tools/atspm_tmc.py 7065 --rebuild                  # re-make CSVs from cache, no download

Output: intersections/<signal>/counts/
    info.txt                 intersection name, movements, date range, outage rule
    tmc_<signal>_5min.csv    one row per bin: date, weekday, time, EB_L, EB_T, ..., total, status
    daily_summary.csv        one row per day: total volume, how much of the day is outage
    raw/                     cached server responses (gzipped); a day is never downloaded twice

Outages: the server reports 0 for every movement when the controller wasn't logging.
A run of >= --outage-bins all-zero bins (default 3 = 15 min) is marked status=outage
and its counts are left blank, so they can't be mistaken for an empty road.
Right turns only appear if the intersection has right-turn detectors.
"""
import argparse
import csv
import datetime as dt
import gzip
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

BASE = "https://traffic.dot.ga.gov/ATSPM/DefaultCharts"
HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "atspm-tmc-research-puller (academic research)",
}
from paths import INTERSECTIONS, CACHE, sig_dir, rel  # noqa: E402
OUT_ROOT = INTERSECTIONS           # one folder per signal: intersections/<id>/counts
CACHE_ROOT = CACHE / "tmc"         # screening downloads (tools/atspm_signals/screen.py)
DIRS = {"Eastbound": "EB", "Westbound": "WB", "Northbound": "NB", "Southbound": "SB"}
MOVES = {"L": 0, "T": 1, "TL": 2, "TR": 3, "R": 4}  # column order within an approach


# ---------------------------------------------------------------- network

def _request(url, body=None, timeout=180, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=body, headers=HEADERS,
                                         method="POST" if body else "GET")
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as e:
            if attempt == retries - 1:
                raise
            wait = 30 * (attempt + 1)
            print(f"    network error ({e}); retrying in {wait}s", file=sys.stderr)
            time.sleep(wait)


def fetch_name(signal):
    try:
        q = urllib.parse.urlencode({"signalID": signal})
        name = _request(f"{BASE}/GetSignalLocation?{q}", timeout=30).strip()
        return re.sub(r"\s+", " ", name) or "unknown"
    except Exception:
        return "unknown"


def fetch_day(signal, day, bin_size):
    d = day.strftime("%m/%d/%Y")
    body = json.dumps({
        "SignalID": str(signal), "StartDate": f"{d} 12:00 AM", "EndDate": f"{d} 11:59 PM",
        "YAxisMax": "", "Y2AxisMax": "", "MetricTypeID": 5, "SelectedBinSize": str(bin_size),
        "ShowLaneVolumes": True,  # "Show Movement Type Volume" -> per-movement columns
        "ShowTotalVolumes": False, "ShowDataTable": True,
    }).encode()
    return _request(f"{BASE}/GetTMCMetric", body)


# ---------------------------------------------------------------- parsing

def _cells(row_html, tag):
    out = []
    for attrs, text in re.findall(rf"<{tag}([^>]*)>(.*?)</{tag}>", row_html, re.S):
        m = re.search(r'colspan="(\d+)"', attrs)
        out.append((re.sub(r"<[^>]+>", "", text).strip(), int(m.group(1)) if m else 1))
    return out


def parse(html):
    """-> (columns, rows) or None if the response has no data table.

    columns: names like "EB_L"; per-approach and grand totals are dropped.
    rows: [(HH:MM, [counts])], excluding the server's Total row.
    """
    m = re.search(r'<div class="TMCTable">(.*?)</table>', html, re.S)
    if not m:
        return None
    trs = re.findall(r"<tr>(.*?)</tr>", m.group(1), re.S)
    head = [tr for tr in trs if "<th" in tr]
    body = [tr for tr in trs if "<th" not in tr]
    if len(head) < 3:
        return None

    # Header row 1 = sections ("Vehicle", and at some signals "Exit", "Light Rail Transit",
    # ...), row 2 = approaches, row 3 = movements, all with colspans. The leading "-" cell
    # spans all header rows, so rows 2 and 3 start at the first data column. Only the
    # Vehicle section is turning movements; other sections (exit-lane detectors, light
    # rail) get a prefix so they can't be mistaken for a vehicle movement.
    sections = []
    for name, span in _cells(head[0], "th")[1:]:
        sections += [name] * span
    approaches = []
    for name, span in _cells(head[1], "th"):
        approaches += [name] * span
    movements = [name for name, _ in _cells(head[2], "th")]
    if not (len(sections) == len(approaches) == len(movements)):
        raise ValueError(f"TMC header doesn't line up: {len(sections)} section, "
                         f"{len(approaches)} approach, {len(movements)} movement columns")
    prefix = {"Vehicle": ""}
    keep = [i for i, mv in enumerate(movements) if mv != "Total" and not mv.endswith(" Total")]
    columns = []
    for i in keep:
        sec = sections[i]
        pre = prefix.get(sec, "LRT_" if sec == "Light Rail Transit" else re.sub(r"\W+", "", sec).upper() + "_")
        columns.append(f"{pre}{DIRS.get(approaches[i], approaches[i])}_{movements[i]}")

    rows = []
    for tr in body:
        tds = [t for t, _ in _cells(tr, "td")]
        if not tds or tds[0] == "Total":
            continue
        t = dt.datetime.strptime(tds[0], "%I:%M %p").strftime("%H:%M")
        rows.append((t, [int(tds[1:][i]) for i in keep]))
    return columns, rows


def outage_mask(rows, min_run):
    """True for bins inside a run of >= min_run consecutive all-zero bins."""
    zero = [sum(v) == 0 for _, v in rows]
    mask, i = [False] * len(zero), 0
    while i < len(zero):
        if zero[i]:
            j = i
            while j < len(zero) and zero[j]:
                j += 1
            if j - i >= min_run:
                mask[i:j] = [True] * (j - i)
            i = j
        else:
            i += 1
    return mask


def col_key(c):
    appr, _, mv = c.partition("_")
    order = list(DIRS.values())
    return (order.index(appr) if appr in order else 9, MOVES.get(mv, 9), c)


# ---------------------------------------------------------------- output

def build(signal, folder, bin_size, min_run, name):
    """Re-make the CSVs and info.txt from every cached day of this signal."""
    days = []
    for f in sorted((folder / "raw").glob(f"*_{bin_size}min.html.gz")):
        day = dt.date.fromisoformat(f.name.split("_")[0])
        try:
            days.append((day, parse(gzip.decompress(f.read_bytes()).decode())))
        except ValueError as e:
            print(f"   {day}: can't parse cached table ({e}); left out", file=sys.stderr)
    if not days:
        return None

    columns = sorted({c for _, p in days if p for c in p[0]}, key=col_key)
    tmc_path = folder / f"tmc_{signal}_{bin_size}min.csv"
    summary = []
    with open(tmc_path, "w", newline="") as tf:
        w = csv.writer(tf)
        w.writerow(["date", "weekday", "time"] + columns + ["total", "status"])
        for day, parsed in days:
            wd = day.strftime("%a")
            if not parsed or all(sum(v) == 0 for _, v in parsed[1]):
                summary.append([day, wd, "no_data", "", 0, "", ""])
                continue
            cols, rows = parsed
            mask = outage_mask(rows, min_run)
            total, n_out = 0, sum(mask)
            for (t, vals), out in zip(rows, mask):
                rec = dict(zip(cols, vals))
                if out:
                    w.writerow([day, wd, t] + [""] * len(columns) + ["", "outage"])
                else:
                    # vehicle movements only: EXIT_/LRT_ columns would double-count
                    s = sum(v for c, v in zip(cols, vals) if c.split("_")[0] in DIRS.values())
                    total += s
                    w.writerow([day, wd, t] + [rec.get(c, "") for c in columns] + [s, "ok"])
            pct = round(100 * n_out / len(rows), 1)
            status = "ok" if n_out == 0 else ("partial" if pct < 100 else "no_data")
            summary.append([day, wd, status, total, len(rows) - n_out, n_out, pct])

    with open(folder / "daily_summary.csv", "w", newline="") as sf:
        w = csv.writer(sf)
        w.writerow(["date", "weekday", "status", "total_volume_valid_bins",
                    "valid_bins", "outage_bins", "outage_pct"])
        w.writerows(summary)

    n_ok = sum(1 for s in summary if s[2] == "ok")
    n_part = sum(1 for s in summary if s[2] == "partial")
    (folder / "info.txt").write_text(
        f"Signal:        {signal}\n"
        f"Intersection:  {name}\n"
        f"Source:        GDOT ATSPM, Turning Movement Counts ({BASE})\n"
        f"Bin size:      {bin_size} min\n"
        f"Days cached:   {len(summary)} ({days[0][0]} to {days[-1][0]})\n"
        f"Complete days: {n_ok}   partial: {n_part}   no data: {len(summary) - n_ok - n_part}\n"
        f"Movements:     {' '.join(columns)}\n"
        f"Outage rule:   >= {min_run} consecutive all-zero bins -> status=outage, counts blank\n"
        f"Updated:       {dt.datetime.now():%Y-%m-%d %H:%M}\n"
    )
    return tmc_path, n_ok, n_part, len(summary)


def write_index():
    """intersections/counts_index.csv: one row per signal with counts (read by
    check_complete.py, which writes the readable status table intersections/README.md)."""
    rows = []
    folders = [p / "counts" for p in INTERSECTIONS.iterdir() if (p / "counts").is_dir()]
    for folder in sorted(folders, key=lambda p: int(p.parent.name) if p.parent.name.isdigit() else 0):
        info = folder / "info.txt"
        n_raw = len(list((folder / "raw").glob("*.html.gz"))) if (folder / "raw").exists() else 0
        if not info.exists():
            rows.append({"signal_id": folder.parent.name, "name": "", "days": n_raw, "first": "", "last": "",
                         "complete": "", "partial": "", "no_data": "", "vehicle_movements": "",
                         "other_columns": "", "note": "raw downloads only (screening cache); "
                         "run atspm_tmc.py on it to build CSVs"})
            continue
        if not (folder / "daily_summary.csv").exists():      # copied counts (e.g. 7065osm), not a download folder
            continue
        txt = info.read_text()
        get = lambda k: (re.search(rf"{k}:\s+(.*)", txt) or [None, ""])[1].strip()
        days = list(csv.DictReader(open(folder / "daily_summary.csv")))
        cols = get("Movements").split()
        veh = [c for c in cols if c.split("_")[0] in DIRS.values()]
        other = [c for c in cols if c not in veh]
        st = [d["status"] for d in days]
        note = ""
        if days and all(s == "no_data" for s in st):
            note = "detectors configured but every day is all zeros: no usable counts"
        elif veh and all(c.endswith("_L") for c in veh):
            note = "left turns only in the Vehicle section"
        rows.append({"signal_id": folder.parent.name, "name": get("Intersection"), "days": len(days),
                     "first": days[0]["date"] if days else "", "last": days[-1]["date"] if days else "",
                     "complete": st.count("ok"), "partial": st.count("partial"),
                     "no_data": st.count("no_data"), "vehicle_movements": " ".join(veh),
                     "other_columns": " ".join(other), "note": note})
    if not rows:
        return
    with open(INTERSECTIONS / "counts_index.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


# ---------------------------------------------------------------- main

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("signals", nargs="+", help="ATSPM signal IDs, e.g. 7065 183")
    g = p.add_argument_group("date range (default: yesterday)")
    g.add_argument("--start", type=dt.date.fromisoformat, help="YYYY-MM-DD")
    g.add_argument("--end", type=dt.date.fromisoformat, help="YYYY-MM-DD (default: --start, or yesterday)")
    g.add_argument("--days", type=int, help="last N days ending yesterday (instead of --start/--end)")
    p.add_argument("--weekdays", action="store_true", help="skip Saturdays and Sundays")
    p.add_argument("--bin", type=int, default=5, choices=[5, 15], help="bin size in minutes (default 5)")
    p.add_argument("--outage-bins", type=int, default=3, help="all-zero run length marked as outage (default 3)")
    p.add_argument("--sleep", type=float, default=5.0, help="pause between requests, seconds (default 5)")
    p.add_argument("--rebuild", action="store_true", help="don't download; re-make CSVs from cache")
    a = p.parse_args()

    yesterday = dt.date.today() - dt.timedelta(days=1)
    if a.days:
        start, end = yesterday - dt.timedelta(days=a.days - 1), yesterday
    else:
        start = a.start or yesterday
        end = a.end or (a.start or yesterday)
    if end < start:
        p.error("--end is before --start")
    days = [start + dt.timedelta(n) for n in range((end - start).days + 1)]
    if a.weekdays:
        days = [d for d in days if d.weekday() < 5]

    for signal in a.signals:
        folder = sig_dir(signal, "counts")
        (folder / "raw").mkdir(parents=True, exist_ok=True)
        name = fetch_name(signal) if not a.rebuild else "unknown"
        if name == "unknown" and (folder / "info.txt").exists():
            m = re.search(r"Intersection:\s+(.*)", (folder / "info.txt").read_text())
            name = m.group(1).strip() if m else name
        print(f"\n== Signal {signal}: {name}")

        todo = [] if a.rebuild else [
            d for d in days if not (folder / "raw" / f"{d}_{a.bin}min.html.gz").exists()]
        if days and not a.rebuild:
            print(f"   {len(days)} day(s) requested, {len(days) - len(todo)} already cached, "
                  f"{len(todo)} to download (~{len(todo) * (20 + a.sleep) / 60:.0f} min)")
        for k, day in enumerate(todo, 1):
            t0 = time.time()
            try:
                html = fetch_day(signal, day, a.bin)
                parsed = parse(html)
                if parsed is None:
                    # no TMC table (firewall rejection, server error page, ...): don't cache,
                    # so the day is requested again next run instead of being stored as empty
                    snippet = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()[:60]
                    raise RuntimeError(f"no TMC table in response: {snippet!r}")
                (folder / "raw" / f"{day}_{a.bin}min.html.gz").write_bytes(gzip.compress(html.encode()))
                note = "ok" if any(sum(v) for _, v in parsed[1]) else "no data"
            except Exception as e:
                note = f"FAILED ({e}) - will retry next run"
            print(f"   [{k}/{len(todo)}] {day} {day:%a}  {note}  {time.time() - t0:.0f}s")
            if k < len(todo):
                time.sleep(a.sleep)

        result = build(signal, folder, a.bin, a.outage_bins, name)
        if result:
            path, n_ok, n_part, n = result
            print(f"   -> {rel(path)}  "
                  f"({n} days: {n_ok} complete, {n_part} partial, {n - n_ok - n_part} no data)")
        else:
            print("   no cached data for this signal")
    write_index()


if __name__ == "__main__":
    main()
