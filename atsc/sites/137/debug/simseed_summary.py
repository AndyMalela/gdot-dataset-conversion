"""Simulation-seed check (validation days): how much does a day's delay move with the SUMO seed, compared with the
differences between methods? Seed 1 from eval/runs.csv, seeds 2-4 from eval_simseeds/runs.csv.

    uv run python atsc/sites/137/debug/simseed_summary.py
"""
import csv
import math
import statistics as st
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
CTRL = ["actuated", "maxpressure", "lstdq_v2_s0"]
d = defaultdict(dict)                                       # (date, ctrl) -> {seed: delay}
for f in [HERE / "eval/runs.csv", HERE / "eval_simseeds/runs.csv"]:
    for r in csv.DictReader(open(f)):
        if r["controller"] in CTRL and r["delay_all_s"]:
            d[(r["date"], r["controller"])][int(r["seed"])] = float(r["delay_all_s"])
days = sorted({k[0] for k in d if len(d[k]) == 4})
seeds = [1, 2, 3, 4]
print(f"{len(days)} days x seeds {seeds}; teleports in seeds 2-4: "
      f"{sum(int(r['teleports'] or 0) for r in csv.DictReader(open(HERE / 'eval_simseeds/runs.csv')))}")
print("\n| controller | mean delay, seed 1 | mean delay, seeds 1-4 | within-day seed SD (median over days) | max | between-day SD |")
print("|---|---|---|---|---|---|")
for c in CTRL:
    sd = [st.stdev(d[(x, c)][s] for s in seeds) for x in days]
    m1 = st.mean(d[(x, c)][1] for x in days)
    m4 = st.mean(st.mean(d[(x, c)][s] for s in seeds) for x in days)
    bd = st.stdev(st.mean(d[(x, c)][s] for s in seeds) for x in days)
    print(f"| {c} | {m1:.1f} | {m4:.1f} | {st.median(sd):.2f} | {max(sd):.2f} | {bd:.2f} |")
print("\nDifference with actuated (log ratio per day): seed noise vs the effect")
print("| method | ratio, seed 1 | ratio, seeds 1-4 mean | within-day seed SD of log ratio (median) | between-day SD of log ratio | days won seed 1 | days won seeds 1-4 | seed-1 day verdicts that flip with the 4-seed mean |")
print("|---|---|---|---|---|---|---|---|")
for c in CTRL[1:]:
    lr = {x: [math.log(d[(x, c)][s] / d[(x, "actuated")][s]) for s in seeds] for x in days}
    l1 = [lr[x][0] for x in days]
    l4 = [math.log(st.mean(d[(x, c)][s] for s in seeds) / st.mean(d[(x, "actuated")][s] for s in seeds)) for x in days]
    flips = sum((a < 0) != (b < 0) for a, b in zip(l1, l4))
    print(f"| {c} | {math.exp(st.mean(l1)):.3f} | {math.exp(st.mean(l4)):.3f} | "
          f"{st.median(st.stdev(v) for v in lr.values()):.3f} | {st.stdev(l4):.3f} | "
          f"{sum(x < 0 for x in l1)}/{len(days)} | {sum(x < 0 for x in l4)}/{len(days)} | {flips} |")
