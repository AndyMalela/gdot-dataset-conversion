GDOT ATSPM Turning Movement Count charts, signal 7065, 2026-10-02 07:00-09:00 (GetTMCMetric, chart mode).
Each chart is one labelled movement with its lanes (subtitles.png stacks titles + lane legends):

  Eastbound Left 1 lane,  Eastbound Thru 2 lanes   -> Piedmont Rd (1 left + 2 through)
  Westbound Left 1 lane,  Westbound Thru 2 lanes   -> Piedmont Rd
  Northbound Left 2 lanes, Northbound Thru 3 lanes -> Peachtree Rd (dual lefts + 3 through)
  Southbound Left 2 lanes, Southbound Thru 3 lanes -> Peachtree Rd

So GDOT's count labels EB/WB = Piedmont, NB/SB = Peachtree (road-based, from the state routes),
not compass directions. Same conclusion as the phase titles (timing/phase_titles.png) and the
detector actuation counts (timing/dircheck/). Used by timing/phase_map.json "count_labels".
