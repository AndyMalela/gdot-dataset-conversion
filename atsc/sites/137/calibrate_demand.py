"""v3 step C: closed-loop calibration of the presence-zone undercount factors.

    uv run python atsc/sites/137/calibrate_demand.py           -> table; writes the counts table + factors json

GDOT's report counts the side streets and the EB left with stop-bar presence zones: one count per zone activation,
so a discharging queue counts as one vehicle. The earlier factors (attempt 4) were estimated from occupancy time
with the HCM headway. Here the factor k of each presence-zone movement is chosen so that the SIMULATED zone
produces as many activations as GDOT reported — the simulation reproduces the measurement process itself.

Setup: model after steps A (measured passage, P1 clearance) and B (tau 1.2). GDOT plan; 06:00-22:00 of a fixed set
of train weekdays (nights stay as reported, as before). Demand = tmc_137_5min_upstream.csv (WB through from 138)
with every presence-zone movement x k in daytime bins (seeded stochastic rounding, as build_upstream_counts_137.py).
Grid: one common k for all seven movements per run, k in GRID (movements barely interact at this level; checked by
a confirmation run with the chosen vector).
Rule (fixed before running): activations rise with demand until a standing queue merges them, then fall. For each
movement, keep the rising branch (grid values up to the one with the most activations) and choose the k whose
ratio sim activations / GDOT count is closest to 1 (log scale). If even the peak stays below 1, choose the peak and
flag the movement (the zone model cannot reproduce the count).
"""
import csv
import hashlib
import json
import math
import os
import random
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(HERE))

SRC = REPO / "intersections/137/counts/tmc_137_5min_upstream.csv"
RAW = REPO / "intersections/137/counts/tmc_137_5min.csv"
OUTDIR = HERE / "calibration_demand"
ZONES = {"NB_L": "ch9", "NB_T": "ch32", "NB_R": "ch31", "SB_L": "ch29", "SB_T": "ch12", "SB_R": "ch11", "EB_L": "ch19"}
GRID = [0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.4, 2.8, 3.2]
# attempt 13: measured share of GDOT's presence-zone activations that are radar dropouts (measure_dropouts.py)
_DP = REPO / "intersections/137/counts/presence_dropouts.json"
DROPOUT = json.loads(_DP.read_text())["share"] if _DP.exists() else {}
N_DAYS = 8
H0, H1 = 6, 22
MV = ["EB_L", "EB_TR", "WB_L", "WB_TR", "NB_L", "NB_T", "NB_R", "SB_L", "SB_T", "SB_R"]


def write_counts(k, path):
    """upstream table with presence-zone movements x k[m] in 06:00-22:00 ok bins."""
    rows = list(csv.DictReader(open(SRC)))
    fields = list(rows[0])
    for b in rows:
        if b["status"] == "ok" and f"{H0:02d}:00" <= b["time"] < f"{H1:02d}:00":
            for c, f in k.items():
                x = int(b[c]) * f
                rng = random.Random(int(hashlib.md5(f"{b['date']}{b['time']}{c}".encode()).hexdigest()[:8], 16))
                b[c] = int(x) + (1 if rng.random() < x - int(x) else 0)
            b["total"] = sum(int(b[c]) for c in MV)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def job(args):
    day, tag, counts_file = args
    os.environ["ATSC_COUNTS_FILE_137"] = str(counts_file)
    from atsc.sim.episode import run_window
    from atsc.sim.signal import actuated_from_site
    from measure_dropouts import ZONES as DZ, is_dropout
    from diag_clear import merge
    res = run_window(HERE, day, float(H0), float(H1), actuated_from_site(HERE), mode="plan", seed=1, record_events=True)
    ev = res["events"]["stopbar"]
    G = defaultdict(list)
    for g in res["greens"]:
        if g["end"] == g["end"]:
            G[g["phase"]].append((g["start"], g["end"]))
    out = {}
    for m, ch in ZONES.items():
        acts = [(a, b) for a, b in ev[ch] if H0 * 3600 <= a < H1 * 3600]
        if m in DROPOUT:                    # attempt 13: count like the field minus its dropouts (both sides)
            acts = [(a, b) for a, b in merge(acts) if not is_dropout(a, b, G, DZ[m][2])]
        out[m] = len(acts)
    return tag, day, out


def raw_counts(days):
    """GDOT counts per day; movements with a measured dropout share are reduced by it (attempt 13)."""
    out = defaultdict(lambda: defaultdict(float))
    for r in csv.DictReader(open(RAW)):
        if r["date"] in days and r["status"] == "ok" and f"{H0:02d}:00" <= r["time"] < f"{H1:02d}:00":
            for m in ZONES:
                out[r["date"]][m] += int(r[m]) * (1 - DROPOUT.get(m, 0.0))
    return out


def run(configs, days):
    """configs: {tag: {movement: k}} -> {tag: {movement: (sim activations, GDOT count)}} summed over days"""
    OUTDIR.mkdir(exist_ok=True)
    files = {}
    for tag, k in configs.items():
        files[tag] = OUTDIR / f"counts_{tag}.csv"
        write_counts(k, files[tag])
    raw = raw_counts(set(days))
    agg = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    with ProcessPoolExecutor(22) as pool:
        for tag, day, act in pool.map(job, [(d, t, files[t]) for t in configs for d in days]):
            for m, n in act.items():
                agg[tag][m][0] += n
                agg[tag][m][1] += raw[day][m]
    return agg


def main():
    from baselines import days as split_days
    ds = [str(d) for d in split_days("train")]
    ds = ds[1:: max(1, len(ds) // N_DAYS)][:N_DAYS]                # different subset from the discharge step
    print("days:", ds, flush=True)
    agg = run({f"k{v}": {m: v for m in ZONES} for v in GRID}, ds)
    print("ratio sim activations / GDOT count, by common factor k:")
    print("k    " + " ".join(f"{m:>6}" for m in ZONES))
    ratio = {}
    for v in GRID:
        r = {m: agg[f"k{v}"][m][0] / agg[f"k{v}"][m][1] for m in ZONES}
        ratio[v] = r
        print(f"{v:<4} " + " ".join(f"{r[m]:6.2f}" for m in ZONES), flush=True)
    chosen, flags = {}, {}
    for m in ZONES:
        acts = [agg[f"k{v}"][m][0] for v in GRID]
        peak = max(range(len(GRID)), key=lambda i: acts[i])
        rising = GRID[:peak + 1]
        best = min(rising, key=lambda v: abs(math.log(ratio[v][m])))
        chosen[m] = best
        if max(ratio[v][m] for v in rising) < 1:
            flags[m] = "peak below 1: zone model cannot reproduce the count"
    print("chosen:", chosen, "flags:", flags, flush=True)
    conf = run({"chosen": chosen}, ds)
    print("confirmation (chosen vector):", {m: round(conf["chosen"][m][0] / conf["chosen"][m][1], 2) for m in ZONES})
    out = {"factor": chosen, "flags": flags, "days": ds, "window_h": [H0, H1], "grid": GRID,
           "ratio_by_k": {str(v): {m: round(r[m], 3) for m in ZONES} for v, r in ratio.items()},
           "confirmation_ratio": {m: round(conf["chosen"][m][0] / conf["chosen"][m][1], 3) for m in ZONES},
           "dropout_share": DROPOUT,
           "source": "atsc/sites/137/calibrate_demand.py (v3 step C, 2026-11-20): closed loop, simulated presence-zone "
                     "activations = GDOT reported counts; model after steps A and B; from attempt 13 both sides "
                     "without radar dropouts (count x (1 - dropout share); model activations that are dropouts removed)"}
    (REPO / "intersections/137/counts/presence_factors_closedloop.json").write_text(json.dumps(out, indent=1))
    write_counts(chosen, REPO / "intersections/137/counts/tmc_137_5min_closedloop.csv")
    print("wrote presence_factors_closedloop.json and tmc_137_5min_closedloop.csv")


if __name__ == "__main__":
    main()
