"""Fetch Timing & Actuation charts for given phases in short windows (cached)."""
import sys, datetime as dt, re, time, json
from pathlib import Path
sys.path.insert(0, "tools")
import atspm_timing as tna
OUT = Path("tools/cache/tna_lanecheck")

def fetch(sid, start, minutes, phases="2,6", size="4"):
    d = OUT / (f"{sid}_{start:%Y%m%d_%H%M%S}_{minutes}m" + ("" if phases == "2,6" else "_p" + phases.replace(",", "")))
    if d.exists() and any(d.glob("*.jpg")):
        return d
    payload = {"SignalID": str(sid), "StartDate": tna.fmt(start), "EndDate": tna.fmt(start + dt.timedelta(minutes=minutes)),
      "MetricTypeID": 17, "ShowLegend": False, "ShowHeaderForEachPhase": True, "CombineLanesForEachGroup": False,
      "DotAndBarSize": size, "PhaseFilter": phases, "PhaseEventCodes": "", "GlobalCustomEventCodes": "",
      "GlobalCustomEventParams": "", "ShowAllLanesInfo": True, "ShowLinesStartEnd": False, "ShowEventPairs": False,
      "ShowRawEventData": False, "ShowPermissivePhases": False, "ExtendVsdSearch": "5", "ShowVehicleSignalDisplay": True,
      "ShowPedestrianIntervals": False, "ExtendStartStopSearch": "2", "ShowPedestrianActuation": False,
      "ShowStopBarPresence": True, "ShowLaneByLaneCount": True, "ShowAdvancedDilemmaZone": False,
      "ShowAdvancedCount": True, "AdvancedOffset": "0"}
    for k in range(4):
        try:
            html = tna.post_json(f"{tna.BASE}/GetTimingAndActuations", payload, timeout=400)
            break
        except Exception as e:
            time.sleep(15 * (k + 1))
    else:
        raise SystemExit("portal unavailable")
    if not isinstance(html, str):
        html = html.decode()
    urls = re.findall(r'src="(https://[^"]+\.jpg)"', html)
    d.mkdir(parents=True, exist_ok=True)
    for i, u in enumerate(urls, 1):
        (d / f"{i:02d}.jpg").write_bytes(tna.get(u))
    return d

if __name__ == "__main__":
    start = dt.datetime.strptime(sys.argv[1], "%Y-%m-%dT%H:%M")
    t0 = time.time()
    d = fetch("7065", start, int(sys.argv[2]))
    print(d, len(list(d.glob("*.jpg"))), f"{time.time() - t0:.0f}s")
