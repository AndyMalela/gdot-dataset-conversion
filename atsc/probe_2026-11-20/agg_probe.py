"""Probe GDOT ATSPM AggregateDataExport: one small request, see what comes back (image? table? csv?)."""
import http.cookiejar, re, sys, time, urllib.parse, urllib.request

BASE = "https://traffic.dot.ga.gov/ATSPM"
UA = "Mozilla/5.0 (research data pull; ATSPM timing)"
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))


def get(url):
    r = op.open(urllib.request.Request(url, headers={"User-Agent": UA, "X-Requested-With": "XMLHttpRequest"}), timeout=120)
    return r.read().decode("utf-8", "replace")


def post(url, fields):
    data = urllib.parse.urlencode(fields).encode()
    r = op.open(urllib.request.Request(url, data=data, headers={"User-Agent": UA, "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}), timeout=400)
    return r.headers.get("Content-Type"), r.read()


sig, day, metric, agg = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]  # e.g. 137 03/10/2026 20 0
series = sys.argv[5] if len(sys.argv) > 5 else "PhaseNumber"
page = get(f"{BASE}/AggregateDataExport")
token = re.search(r'name="__RequestVerificationToken" type="hidden" value="([^"]+)"', page).group(1)
time.sleep(2)
frag = get(f"{BASE}/AggregateDataExport/GetSignal?signalId={sig}&index=0")
fields = [("__RequestVerificationToken", token)]
for m in re.finditer(r'<input[^>]*name="([^"]+)"[^>]*value="([^"]*)"', frag):
    fields.append((m.group(1), m.group(2)))
fields = [(k, v) for k, v in fields if not (k.endswith("Exclude") and v == "true")]  # checkboxes unchecked = include
for i, d in enumerate([3, 4, 1, 2, 5, 6, 7, 8]):
    fields += [(f"FilterDirections[{i}].Include", "true"), (f"FilterDirections[{i}].DirectionTypeId", str(d))]
for i, mv in enumerate([3, 5, 1, 4, 2, 6]):
    fields += [(f"FilterMovements[{i}].Include", "true"), (f"FilterMovements[{i}].MovementTypeId", str(mv))]
fields += [("SelectedMetricTypeId", metric), ("SelectedAggregatedData", agg), ("SelectedXAxisType", "Time"),
           ("SelectedSeriesType", series), ("SelectedAggregationType", "Sum"), ("SelectedChartType", "Column"),
           ("SelectedSeriesWidth", "1"), ("SelectedBinSize", "0"), ("SelectedDimension", "TwoDimensional"),
           ("ShowEventCount", "false"), ("StartDateDay", day), ("EndDateDay", day), ("Weekdays", "true"),
           ("Weekends", "true"), ("StartTime", "12:00"), ("SelectedStartAMPM", "AM"), ("EndTime", "11:59"),
           ("SelectedEndAMPM", "PM")]
time.sleep(2)
ct, body = post(f"{BASE}/AggregateDataExport/CreateMetric", fields)
open(f"create_{metric}_{agg}.out", "wb").write(body)
print("CreateMetric:", ct, len(body))
txt = body.decode("utf-8", "replace")
print(re.findall(r'(?:src|href)="([^"]+)"', txt)[:10])
print(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", txt))[:1500])
