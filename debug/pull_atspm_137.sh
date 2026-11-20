#!/bin/bash
# Pull exact ATSPM chart numbers (5 reports, hourly windows, full day) for every 137 study weekday.
# Resumable: cached windows are skipped. Log: debug/pull_atspm_137.log
cd "$(dirname "$0")/.."
days=$(uv run python -c "
import datetime as d
x=d.date(2026,3,2)
while x<=d.date(2026,5,29):
    if x.weekday()<5 and x!=d.date(2026,5,25): print(x)
    x+=d.timedelta(1)")
for day in $days; do
  echo "== $day $(date +%H:%M)"
  uv run python tools/atspm_charts.py 137 SplitFail ApproachDelay PCD WaitTime PedDelay --date $day --hours 0-24 --window 60 --no-csv 2>&1 | grep -cE " ok$| no chart$" ; true 
done
uv run python tools/atspm_charts.py 137 --reread 2>&1 | grep -v Warning
echo "DONE $(date)"
