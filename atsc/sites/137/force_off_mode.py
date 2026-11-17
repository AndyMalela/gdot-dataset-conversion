"""Which of 137's non-coordinated phases the field controller lets run past their programmed split (VALIDATION.md
attempt 7). GDOT's Split Monitor, train weekdays only, plans from signal.json's schedule.

    uv run python atsc/sites/137/force_off_mode.py     -> force_off.json + table

Fixed force-offs (the engine's default, nema.py) let a phase that starts early (the previous phases ended early) run
to its fixed point in the cycle, i.e. longer than its split. Floating force-offs cap every green at its own split
(green = split - yellow - red); unused time goes to the coordinated phases. Rule (fixed before the validation is run):
a phase gets a floating force-off when its 85th-percentile split stays within 0.5 s of the programmed split in every
train-day band where it was served; otherwise it keeps the fixed force-off. Pedestrian minimums (P4, P8) and
partner-skipped greens can legitimately exceed a split under either mode, so those phases are left as measured.
"""
import csv
import datetime as dt
import json
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
from atsc.sim.demand import schedule  # noqa: E402

TOL = 0.5


def main():
    sig = json.loads((HERE / "signal.json").read_text())
    tr = json.loads((HERE / "split.json").read_text())["sets"]["train"]
    g = defaultdict(list)
    for r in csv.DictReader(open(REPO / "intersections/137/timing/splitstats_137.csv")):
        if r["check"] != "ok" or not tr["from"] <= r["date"] <= tr["to"]:
            continue
        d = dt.date.fromisoformat(r["date"])
        if d.weekday() >= 5 or not r["p85_split_s"] or float(r["skip_pct"]) >= 100:
            continue
        t = int(r["band_start"][:2]) * 3600 + int(r["band_start"][3:]) * 60
        plan = [n for t0, n in schedule(sig, d) if t0 <= t + 300][-1]
        q = int(r["phase"])
        if plan not in sig["plans"] or q in sig["plans"][plan]["coordinated"]:
            continue
        g[(q, plan)].append((float(r["avg_split_s"]), float(r["p85_split_s"]), sig["plans"][plan]["splits"][str(q)]))
    rows, over = [], defaultdict(lambda: [0, 0])
    for (q, plan), v in sorted(g.items()):
        n_over = sum(p85 > sp + TOL for _, p85, sp in v)
        over[q][0] += n_over
        over[q][1] += len(v)
        rows.append((q, plan, v[0][2], len(v), round(st.median(a for a, _, _ in v), 1),
                     round(st.median(p for _, p, _ in v), 1), n_over))
    floating = sorted(q for q, (n, m) in over.items() if n == 0)
    print("| phase | plan | split s | train bands | median avg split | median p85 split | bands with p85 > split + 0.5 s |")
    print("|---|---|---|---|---|---|---|")
    for r in rows:
        print("| " + " | ".join(map(str, r)) + " |")
    print(f"floating force-off: {floating}; per phase bands over/served: { {q: tuple(v) for q, v in sorted(over.items())} }")
    json.dump({"source": "force_off_mode.py: GDOT Split Monitor, train weekdays; floating when p85 split <= split + 0.5 s "
                         "in every served band",
               "floating": floating, "bands_over_served": {str(q): v for q, v in sorted(over.items())}},
              open(HERE / "force_off.json", "w"), indent=1)


if __name__ == "__main__":
    main()
