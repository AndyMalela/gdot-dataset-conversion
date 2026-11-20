"""Probe every ATSPM DefaultCharts metric once for one signal/day: save html + images, report any text/table data."""
import json, re, sys, time, urllib.request
from pathlib import Path

BASE = "https://traffic.dot.ga.gov/ATSPM/DefaultCharts"
UA = "Mozilla/5.0 (research data pull; ATSPM timing)"
H = {"Content-Type": "application/json; charset=utf-8", "X-Requested-With": "XMLHttpRequest", "User-Agent": UA}
sig, day = sys.argv[1], sys.argv[2]           # 137 03/10/2026
t0, t1 = (sys.argv[3], sys.argv[4]) if len(sys.argv) > 4 else ("12:00 AM", "11:59 PM")
out = Path(f"charts_{sig}"); out.mkdir(exist_ok=True)
common = {"SignalID": sig, "StartDate": f"{day} {t0}", "EndDate": f"{day} {t1}", "YAxisMax": "", "Y2AxisMax": ""}
M = {
    "PhaseTermination": (1, {"SelectedConsecutiveCount": "1", "ShowPlanStripes": True, "ShowPedActivity": True}),
    "PedDelay": (3, {"TimeBuffer": "15", "ShowPedBeginWalk": True, "ShowCycleLength": True, "ShowPercentDelay": True,
                     "ShowPedRecall": True, "PedRecallThreshold": "75"}),
    "Preempt": (4, {}),
    "PCD": (6, {"SelectedBinSize": "15", "SelectedDotSize": "1", "SelectedLineSize": "1", "ShowPlanStatistics": True,
                "ShowVolumes": True}),
    "ApproachDelay": (8, {"SelectedBinSize": "15", "ShowPlanStatistics": True, "ShowTotalDelayPerHour": True,
                          "ShowDelayPerVehicle": True}),
    "AoR": (9, {"SelectedBinSize": "15", "ShowPlanStatistics": True}),
    "ApproachSpeed": (10, {"SelectedBinSize": "15", "ShowPlanStatistics": True, "ShowPostedSpeed": True,
                           "ShowAverageSpeed": True}),
    "YellowAndRed": (11, {"SeverLevel": "4", "ShowRedLightViolations": True, "ShowSevereRedLightViolations": True,
                          "ShowPercentRedLightViolations": True, "ShowPercentSevereRedLightViolations": True,
                          "ShowAverageTimeRedLightViolations": True, "ShowYellowLightOccurrences": True,
                          "ShowPercentYellowLightOccurrences": True, "ShowAverageTimeYellowOccurences": True}),
    "SplitFail": (12, {"FirstSecondsOfRed": "5", "ShowFailLines": True, "ShowAvgLines": True, "ShowPercentFailLines": True}),
    "LeftTurnGapAnalysis": (31, {"Gap1Min": "1", "Gap1Max": "3.3", "Gap2Min": "3.3", "Gap2Max": "3.7", "Gap3Min": "3.7",
                                 "Gap3Max": "7.4", "Gap4Min": "7.4", "TrendLineGapThreshold": "7.4", "BinSize": "15"}),
    "WaitTime": (32, {"ShowPlanStripes": True}),
}
only = sys.argv[5:] if len(sys.argv) > 5 else list(M)
for name in only:
    mid, extra = M[name]
    body = dict(common, MetricTypeID=mid, **extra)
    url = f"{BASE}/Get{name}Metric" if name != "PCD" else f"{BASE}/GetPCDMetric"
    try:
        html = urllib.request.urlopen(urllib.request.Request(url, data=json.dumps(body).encode(), method="POST", headers=H),
                                      timeout=400).read().decode("utf-8", "replace")
    except Exception as e:
        print(f"{name}: ERROR {e}", flush=True); time.sleep(8); continue
    (out / f"{name}.html").write_text(html)
    imgs = re.findall(r'src="(https://[^"]+\.(?:jpg|png))"', html)
    text = re.sub(r"\s+", " ", re.sub(r"<script.*?</script>|<[^>]+>", " ", html, flags=re.S)).strip()
    tables = html.count("<table")
    for i, u in enumerate(imgs[:3]):
        try:
            (out / f"{name}_{i}.jpg").write_bytes(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=120).read())
        except Exception as e:
            print("  img fail", e)
    print(f"{name}: {len(html)} B, {len(imgs)} images, {tables} tables, text: {text[:200]!r}", flush=True)
    time.sleep(8)
