#!/bin/bash
# 7111 Step 3 (MODEL_LOG.md): T&A windows on every other usable train day; retries a window that returns no charts
cd /home/andy/Downloads/GDOT
for d in 2026-08-31 2026-09-02 2026-09-04 2026-09-09 2026-09-11 2026-09-15 2026-09-17 2026-09-21 2026-09-23 2026-09-25 2026-09-29 2026-10-06 2026-10-08; do
 for t in 07:00 08:30 10:00 12:00 13:30 15:00 17:00 18:30; do
  for k in 1 2 3 4; do
   out=$(timeout 1800 uv run python -c "
import sys,datetime as dt; sys.path.insert(0,'tools/lanecheck')
from tna_fetch import fetch
d=fetch('7111', dt.datetime.strptime('${d}T${t}','%Y-%m-%dT%H:%M'), 5, phases='1,2,3,4,5,6,8')
print('N', len(list(d.glob('*.jpg'))), flush=True)
" 2>&1 | grep -E "^N" )
   n=${out#N }
   if [ "$n" = "7" ]; then echo "OK $d $t"; break; fi
   echo "retry $k $d $t got '${out}'"; sleep $((60*k))
  done
  sleep 3
 done
done
echo "DONE $(date)"
