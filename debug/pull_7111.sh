#!/bin/bash
# 7111 corridor (7112 - 7111 - 7110): base data for weekdays 2026-08-31 .. 2026-11-20. Resumable (tools cache).
cd /home/andy/Downloads/GDOT
S=2026-08-31; E=2026-11-20
echo "== TMC $(date)"
uv run python tools/atspm_tmc.py 7111 7110 7112 --start $S --end $E --weekdays
echo "== Split Monitor + timing plans $(date)"
DAYS=$(python3 -c "
import datetime as d
a=d.date(2026,8,31);b=d.date(2026,11,20)
print(' '.join(str(a+d.timedelta(i)) for i in range((b-a).days+1) if (a+d.timedelta(i)).weekday()<5))")
for s in 7111 7110 7112; do
  uv run python tools/atspm_plans.py $s --date $DAYS
  uv run python tools/atspm_splitstats.py $s
done
echo "DONE $(date)"
