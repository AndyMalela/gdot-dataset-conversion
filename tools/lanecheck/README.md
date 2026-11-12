# Lane-by-lane detector check (2026-11-10)

Scripts behind OPEN_ISSUES.md item B2: which detector channels feed GDOT's turning-movement report on the
Peachtree through phases of SIG 7065 (P2, P6). Written quickly; paths are relative to the repo root.

    uv run python tools/lanecheck/tna_batch.py tools/lanecheck        # fetch 1-min Timing & Actuation charts (cached)
    uv run python tools/lanecheck/tna_analyze.py tools/lanecheck      # per 5-min bin: stop-bar vs upstream channels vs report
    uv run python tools/lanecheck/tna_5min.py tools/lanecheck 2026-09-16T17:30   # stop-bar channels on one 5-min chart
    uv run python tools/lanecheck/tna_batch_piedmont.py tools/lanecheck     # same for the Piedmont phases P4, P8 (cached as *_p48)
    uv run python tools/lanecheck/tna_analyze_piedmont.py tools/lanecheck
    uv run python tools/lanecheck/av_pull.py 7065,7058 out.csv        # Approach Volume daily totals

- `tna_count.py` counts detector-on markers (black triangles) per chart row. Rows are identified by matching the
  label image against the 2026-10-02 08:00 chart.
- Charts are cached in `tools/cache/tna_lanecheck/`, Approach Volume reports in `tools/cache/av/`.
- Counting from 1-min charts is accurate to a few vehicles per 5 min; dense 5-min charts lose overlapping markers.
