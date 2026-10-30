"""Download a signal's configuration from GDOT ATSPM (traffic.dot.ga.gov): approaches and every detector
(channel, phase, detection type, hardware, lane, distance from stop bar).

These are the two requests the public page https://traffic.dot.ga.gov/ATSPM/Signals/SignalDetail makes
when you type a signal ID and press Select; no login is needed.

Examples
    python3 tools/atspm_config.py 7065
    python3 tools/atspm_config.py 7065 191 --refresh      # download again even if cached

Output: intersections/<signal>/config/
    detectors.csv     one row per detector, columns as ATSPM's configuration table
    approaches.csv    one row per approach: direction, description, protected/permissive/ped phases, speed
    signal.txt        name, controller type, latitude/longitude, configuration versions, download date
    raw/              the server responses (gzipped), as downloaded
"""
import argparse
import csv
import datetime as dt
import gzip
import re
import sys
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import sig_dir, rel  # noqa: E402

BASE = "https://traffic.dot.ga.gov/ATSPM"
HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "atspm-config-research-puller (academic research)",
}


def _request(url, timeout=60, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as e:
            if attempt == retries - 1:
                raise
            wait = 30 * (attempt + 1)
            print(f"    network error ({e}); retrying in {wait}s", file=sys.stderr)
            time.sleep(wait)


class _Tables(HTMLParser):
    """every <table> as a list of rows; a row is a list of cell texts (th or td), <br> -> '; '."""
    def __init__(self):
        super().__init__()
        self.tables, self._row, self._cell = [], None, None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.tables.append([])
        elif tag == "tr" and self.tables:
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []
        elif tag == "br" and self._cell is not None:
            self._cell.append("; ")

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._cell is not None:
            self._row.append(re.sub(r"\s+", " ", "".join(self._cell)).strip(" ;"))
            self._cell = None
        elif tag == "tr" and self._row is not None:
            if self._row:
                self.tables[-1].append(self._row)
            self._row = None

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)


def tables(html):
    p = _Tables()
    p.feed(html)
    return p.tables


def as_records(rows):
    """header row + data rows -> dicts; ATSPM's detector table has one empty header cell with no data cell."""
    head, out = rows[0], []
    for r in rows[1:]:
        h = head if len(head) == len(r) else [c for c in head if c]
        if len(h) != len(r):
            raise ValueError(f"header {len(head)} cells, row {len(r)}: {r}")
        out.append(dict(zip(h, r)))
    return out


def fetch(signal, raw, refresh):
    """name, detail html, configuration-table html (cached in raw/)."""
    raw.mkdir(parents=True, exist_ok=True)
    urls = {
        "name.txt": f"{BASE}/DefaultCharts/GetSignalLocation?" + urllib.parse.urlencode({"signalID": signal}),
        "detail.html": f"{BASE}/Signals/SignalDetailResult/{signal}",
        "configuration.html": f"{BASE}/ConfigurationTable?" + urllib.parse.urlencode({"SignalID": signal}),
    }
    out = {}
    for name, url in urls.items():
        f = raw / f"{name}.gz"
        if f.exists() and not refresh:
            out[name] = gzip.decompress(f.read_bytes()).decode("utf-8")
            continue
        out[name] = _request(url)
        f.write_bytes(gzip.compress(out[name].encode("utf-8")))
        time.sleep(3)
    return out


def write_csv(path, rows):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def build(signal, refresh=False):
    out = sig_dir(signal, "config")
    got = fetch(signal, out / "raw", refresh)
    name = re.sub(r"\s+", " ", got["name.txt"]).strip()
    if name == "Signal Not Found":
        print(f"{signal}: not found")
        return

    det = as_records(tables(got["configuration.html"])[0])
    write_csv(out / "detectors.csv", det)

    t = tables(got["detail.html"])
    info = as_records(t[0])[0] if t and len(t[0]) > 1 else {}
    appr = next((as_records(x) for x in t if x and "Direction" in x[0]), [])
    if appr:
        write_csv(out / "approaches.csv", appr)
    versions = re.findall(r"<option[^>]*>([^<]+)</option>", got["detail.html"])

    raw_time = dt.datetime.fromtimestamp((out / "raw" / "configuration.html.gz").stat().st_mtime)
    lines = [f"Signal:        {signal}", f"Name:          {name}",
             *[f"{k + ':':15s}{v}" for k, v in info.items() if v],
             f"Versions:      {' | '.join(v.strip() for v in versions)}",
             f"Source:        {BASE}/Signals/SignalDetail (SignalDetailResult, ConfigurationTable)",
             f"Downloaded:    {raw_time:%Y-%m-%d %H:%M}",
             f"Detectors:     {len(det)}   Approaches: {len(appr)}"]
    (out / "signal.txt").write_text("\n".join(lines) + "\n")
    print(f"{signal}: {name}: {len(det)} detectors, {len(appr)} approaches -> {rel(out)}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("signals", nargs="+")
    p.add_argument("--refresh", action="store_true", help="download again even if cached")
    a = p.parse_args()
    for s in a.signals:
        build(s, a.refresh)


if __name__ == "__main__":
    main()
