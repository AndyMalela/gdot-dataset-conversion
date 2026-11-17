"""Corrected 5-min counts for SIG 137: WB through from the upstream signal 138 (W Paces Ferry @ Paces Ferry Pl).

    uv run python tools/lanecheck/build_upstream_counts_137.py
        -> intersections/137/counts/tmc_137_5min_upstream.csv

Rule (agreed with the user 2026-11-16 03:40):
  137's own WB_TR zone (Wavetronix Advance, 13721) is unreliable: daily totals swing 8.8k-20.7k between ordinary
  weekdays, 1.4-2.8x what the upstream signal 138 sends, while every other movement is steady.
  WB_TR(137) = WB_T(138) + NB_TL(138) - WB_L(137)   per 5-min bin, both signals' bins ok
      (138's WB through plus what enters W Paces Ferry westbound from the Paces Pl driveway, minus the vehicles
      that turn left at 137; NB_TL also contains the few driveway-through vehicles: upper bound)
  negative -> 0 (counted below); a bin with an outage at either signal -> outage at 137 (not filled)
  every other column as 137 reports it; EB_TR (always 0 after July) and EXIT_EB_T are dropped (study period is
  2026-03..05, where EB_TR is counted). `total` recomputed. Nothing is scaled.
Only dates present in both reports are written; the locked test set (2026-05-18..29) is written but never read
(atsc/sim/demand.py refuses it).
"""
import csv
from collections import defaultdict

SRC = "intersections/137/counts/tmc_137_5min.csv"
UP = "intersections/138/counts/tmc_138_5min.csv"
OUT = "intersections/137/counts/tmc_137_5min_upstream.csv"
MV = ["EB_L", "EB_TR", "WB_L", "WB_TR", "NB_L", "NB_T", "NB_R", "SB_L", "SB_T", "SB_R"]
D0, D1 = "2026-03-02", "2026-05-29"

up = {(r["date"], r["time"]): r for r in csv.DictReader(open(UP)) if D0 <= r["date"] <= D1}
rows = [r for r in csv.DictReader(open(SRC)) if D0 <= r["date"] <= D1 and (r["date"], r["time"]) in up]
fields = ["date", "weekday", "time"] + MV + ["total", "status"]
out, neg, n_out, n_up_out = [], 0, 0, 0
tot = defaultdict(int)
for r in rows:
    u = up[(r["date"], r["time"])]
    b = {"date": r["date"], "weekday": r["weekday"], "time": r["time"], "status": r["status"]}
    if r["status"] == "ok" and u["status"] != "ok":
        b["status"] = "outage"
        n_up_out += 1
    if b["status"] == "ok":
        for c in MV:
            b[c] = int(float(r[c] or 0))
        tot["WB_TR_report"] += b["WB_TR"]
        w = int(float(u["WB_T"] or 0)) + int(float(u["NB_TL"] or 0)) - b["WB_L"]
        if w < 0:
            neg += 1
            w = 0
        b["WB_TR"] = w
        tot["WB_TR_upstream"] += w
        b["total"] = sum(b[c] for c in MV)
    else:
        n_out += 1
        for c in MV + ["total"]:
            b[c] = ""
    out.append(b)
w = csv.DictWriter(open(OUT, "w", newline=""), fieldnames=fields)
w.writeheader()
w.writerows(out)

# ---- presence-zone estimate (agreed 2026-11-16 10:00; estimate_137_presence.py, VALIDATION.md "Attempt 4")
# daytime bins (06:00-22:00) of the movements counted by stop-bar presence zones are multiplied by the movement's
# factor k (estimated / reported vehicles over sampled train-day windows, HCM saturation flow); the fractional part
# is rounded up with probability = fraction, seeded per (date, time, movement), so totals are unbiased and the run
# is reproducible. Night bins are left as reported (not sampled). Columns from count-only zones are unchanged.
import hashlib, json, random
FAC = json.load(open("intersections/137/counts/presence_factors_1900.json"))["factor"]
EST = "intersections/137/counts/tmc_137_5min_estimated.csv"
est_rows, added = [], defaultdict(int)
for b in out:
    b = dict(b)
    if b["status"] == "ok" and "06:00" <= b["time"] < "22:00":
        for c, k in FAC.items():
            x = b[c] * k
            rng = random.Random(int(hashlib.md5(f"{b['date']}{b['time']}{c}".encode()).hexdigest()[:8], 16))
            n = int(x) + (1 if rng.random() < x - int(x) else 0)
            added[c] += n - b[c]
            b[c] = n
        b["total"] = sum(b[c] for c in MV)
    est_rows.append(b)
w = csv.DictWriter(open(EST, "w", newline=""), fieldnames=fields)
w.writeheader()
w.writerows(est_rows)
print(f"{EST}: presence-zone movements x factor in daytime bins; vehicles added over the period: {dict(added)}")
days = sorted({b["date"] for b in out})
print(f"{OUT}: {len(days)} days ({days[0]}..{days[-1]}), {len(out)} bins, {n_out} outage bins ({n_up_out} because 138 had an outage)")
print(f"bins where 138's WB + NB_TL < 137's WB_L (set to 0): {neg}")
print(f"WB_TR total over the period: 137's zone {tot['WB_TR_report']} -> from 138 {tot['WB_TR_upstream']}")
per = defaultdict(lambda: [0, 0])
for b in out:
    if b["status"] == "ok":
        per[b["date"]][0] += b["WB_TR"]
for r in rows:
    if r["status"] == "ok":
        per[r["date"]][1] += int(float(r["WB_TR"] or 0))
TEST0, TEST1 = "2026-05-18", "2026-05-29"           # locked test set (atsc/sites/137/split.json): never printed
print("per day WB_TR, train + validation only (from 138 / 137's zone): " + "  ".join(
    f"{d[5:]}:{a}/{b}" for d, (a, b) in sorted(per.items()) if not TEST0 <= d <= TEST1))
