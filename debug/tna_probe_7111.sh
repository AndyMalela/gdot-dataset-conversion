#!/bin/bash
# retry the 7111 T&A test window every 15 min (up to 8 h) until the portal's chart service answers
cd /home/andy/Downloads/GDOT
for i in $(seq 1 32); do
  if timeout 900 uv run python -c "
import sys,datetime as dt; sys.path.insert(0,'tools/lanecheck')
from tna_fetch import fetch
d=fetch('7111', dt.datetime(2026,9,16,12,0), 5, phases='1,2,3,4,5,6,8')
print('OK', d, sorted(p.name for p in d.glob('*.jpg')))
" 2>&1 | grep -q '^OK'; then echo "OK at try $i $(date)"; exit 0; fi
  echo "try $i failed $(date)"
  sleep 900
done
exit 1
