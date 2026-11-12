"""Approach Volume (ATSPM metric 7) daily totals per site, direction and detection type (advance vs lane-by-lane)."""
import json, re, sys, gzip, urllib.request, datetime as dt, csv
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
BASE = "https://traffic.dot.ga.gov/ATSPM/DefaultCharts"
H = {"Content-Type": "application/json; charset=utf-8", "X-Requested-With": "XMLHttpRequest",
     "User-Agent": "atspm-tmc-research-puller (academic research)"}
CACHE = Path("tools/cache/av"); CACHE.mkdir(parents=True, exist_ok=True)

def fetch(sig, day, det):
    f = CACHE / f"{sig}_{day:%Y%m%d}_{det}.html.gz"
    if f.exists():
        return gzip.open(f, "rt").read()
    d = f"{day:%m/%d/%Y}"
    body = json.dumps({"SignalID": str(sig), "StartDate": f"{d} 12:00 AM", "EndDate": f"{d} 11:59 PM", "YAxisMax": "",
        "Y2AxisMax": "", "MetricTypeID": 7, "SelectedBinSize": "15", "ShowTotalVolume": True, "ShowDirectionalSplits": False,
        "ShowSbWbVolume": True, "ShowNbEbVolume": True, "ShowTMCDetection": det == "tmc",
        "ShowAdvanceDetection": det == "adv"}).encode()
    for a in range(3):
        try:
            r = urllib.request.urlopen(urllib.request.Request(f"{BASE}/GetApproachVolumeMetric", data=body, headers=H,
                                                              method="POST"), timeout=400).read().decode()
            break
        except Exception as e:
            if a == 2: raise
    gzip.open(f, "wt").write(r)
    return r

def totals(html):
    out = {}
    for d, v in re.findall(r'leftAlign">(Northbound|Southbound|Eastbound|Westbound) Total Volume</td><td align="center">(\d+)', html):
        out[d[0] + "B"] = out.get(d[0] + "B", 0) + int(v)
    return out

sigs = sys.argv[1].split(",")
days = [dt.date(2026, 9, 14) + dt.timedelta(k) for k in range(12)]
days = [d for d in days if d.weekday() < 5]
jobs = [(s, d, det) for s in sigs for d in days for det in ("tmc", "adv")]
w = csv.writer(open(sys.argv[2], "w", newline="")); w.writerow(["signal", "date", "detection", "direction", "veh_day"])
with ThreadPoolExecutor(3) as ex:
    for (s, d, det), html in zip(jobs, ex.map(lambda j: fetch(*j), jobs)):
        t = totals(html)
        imgs = len(re.findall(r"approachVolumeImage", html))
        for k, v in sorted(t.items()):
            w.writerow([s, d, det, k, v])
        print(s, d, det, imgs, t, flush=True)
