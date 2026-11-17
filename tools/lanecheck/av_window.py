"""Approach Volume (lane-by-lane detection) totals per direction for an arbitrary window, cached.
fetch(sig, start, minutes) -> {"NB": n, "SB": n, "EB": n, "WB": n}"""
import json, re, sys, gzip, urllib.request, datetime as dt, time
from pathlib import Path
BASE = "https://traffic.dot.ga.gov/ATSPM/DefaultCharts"
H = {"Content-Type": "application/json; charset=utf-8", "X-Requested-With": "XMLHttpRequest",
     "User-Agent": "atspm-tmc-research-puller (academic research)"}
CACHE = Path("tools/cache/av_window"); CACHE.mkdir(parents=True, exist_ok=True)

def raw(sig, start, minutes, binsize="15", detection="tmc"):
    """detection: 'tmc' = lane-by-lane count zones (7065's upstream zones), 'adv' = Advance count zones (137's EB/WB)."""
    suffix = "" if detection == "tmc" else f"_{detection}"
    f = CACHE / f"{sig}_{start:%Y%m%d_%H%M}_{minutes}m_b{binsize}{suffix}.html.gz"
    if f.exists():
        return gzip.open(f, "rt").read()
    end = start + dt.timedelta(minutes=minutes)
    fmt = lambda t: t.strftime("%m/%d/%Y %I:%M %p")
    body = json.dumps({"SignalID": str(sig), "StartDate": fmt(start), "EndDate": fmt(end), "YAxisMax": "",
        "Y2AxisMax": "", "MetricTypeID": 7, "SelectedBinSize": binsize, "ShowTotalVolume": True,
        "ShowDirectionalSplits": False, "ShowSbWbVolume": True, "ShowNbEbVolume": True, "ShowTMCDetection": detection == "tmc",
        "ShowAdvanceDetection": detection == "adv"}).encode()
    for a in range(4):
        try:
            r = urllib.request.urlopen(urllib.request.Request(f"{BASE}/GetApproachVolumeMetric", data=body, headers=H,
                                                              method="POST"), timeout=400).read().decode()
            if "ShowMetricUrl" not in r:                      # error page ("The underlying provider failed on Open.")
                raise RuntimeError("error page")              # a report page without totals = no data (outage): kept
            break
        except Exception as e:
            if a == 3: raise
            time.sleep(10 * (a + 1))
    gzip.open(f, "wt").write(r)
    return r

def totals(html):
    out = {}
    for d, v in re.findall(r'leftAlign">(Northbound|Southbound|Eastbound|Westbound) Total Volume</td><td align="center">(\d+)', html):
        out[d[0] + "B"] = out.get(d[0] + "B", 0) + int(v)
    return out

def fetch(sig, start, minutes, binsize="15", detection="tmc"):
    return totals(raw(sig, start, minutes, binsize, detection))

if __name__ == "__main__":
    s = dt.datetime.strptime(sys.argv[2], "%Y-%m-%dT%H:%M")
    t0 = time.time()
    print(fetch(sys.argv[1], s, int(sys.argv[3])), f"{time.time() - t0:.0f}s")
