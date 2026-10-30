"""Phase 1.4 demand audit for SIG 7065 (train + validation days only; the locked test set is not read).

    uv run python atsc/sites/7065/audit_demand.py

Writes demand_audit/days.csv (quality per day) and demand_audit/flagged_bins.csv (5-min counts above
what the detectors can physically count), and prints the summary used in DEMAND.md.
"""
import csv
import datetime as dt
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
from atsc.sim.demand import BIN, S_MAX, BinBound, day_quality, day_set, load_counts  # noqa: E402

HCM = 1900


def hhmm(t):
    return f"{t // 3600:02d}:{t % 3600 // 60:02d}"


def main():
    split = json.loads((HERE / "split.json").read_text())
    holidays = set(split["holidays"])
    days = load_counts(HERE)
    bound = BinBound(HERE)
    cols = list(bound.mv["movements"])
    out = HERE / "demand_audit"
    out.mkdir(exist_ok=True)

    day_rows, flags = [], []
    veh_all, veh_flag = Counter(), Counter()
    above_hcm = Counter()
    for d in sorted(days):
        s = day_set(split, d)
        if s is None:
            continue
        kind = "holiday" if str(d) in holidays else {5: "saturday", 6: "sunday"}.get(d.weekday(), "weekday")
        q, info = day_quality(days[d])
        bins = {b.t: b for b in days[d]}
        nflag = 0
        if kind in ("weekday", "saturday"):
            for t, b in sorted(bins.items()):
                if b.status != "ok":
                    continue
                for c in cols:
                    lim = bound.limit(d, t, c)
                    n = b.counts[c]
                    if q in ("complete", "usable"):
                        veh_all[c] += n
                    if lim is None:
                        continue
                    if n > lim:
                        nflag += 1
                        nb = lambda k: bins[k].counts.get(c, "") if k in bins and bins[k].status == "ok" else ""
                        flags.append({"date": d, "set": s, "time": hhmm(t), "movement": c, "count": n,
                                      "limit": round(lim), "ratio": round(n / lim, 2),
                                      "plans": " ".join(bound.plans_in_bin(d, t)),
                                      "prev": nb(t - BIN), "next": nb(t + BIN)})
                        if q in ("complete", "usable"):
                            veh_flag[c] += n
                    if q in ("complete", "usable") and n > lim * HCM / S_MAX:
                        above_hcm[c] += 1
        day_rows.append({"date": d, "weekday": d.strftime("%a"), "set": s, "day_type": kind, "quality": q,
                         "vehicles": sum(sum(b.counts.values()) for b in days[d] if b.status == "ok"),
                         "outage_bins": info["outage_bins"], "daytime_outage_min": info["daytime_outage_min"],
                         "stuck": "; ".join(f"{k} {v} min" for k, v in info["stuck_min"].items()),
                         "flagged_bins": nflag})

    for name, rows in [("days.csv", day_rows), ("flagged_bins.csv", flags)]:
        with open(out / name, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)

    # ---- summary
    tab = defaultdict(Counter)
    for r in day_rows:
        tab[(r["set"], r["day_type"])][r["quality"]] += 1
    print("days by set / type / quality")
    for k in sorted(tab):
        print(f"  {k[0]:10s} {k[1]:9s} " + "  ".join(f"{q} {n}" for q, n in sorted(tab[k].items())))
    good = [r for r in day_rows if r["quality"] in ("complete", "usable") and r["day_type"] in ("weekday", "saturday")]
    print(f"usable days: {len(good)}  (weekday {sum(r['day_type'] == 'weekday' for r in good)}, "
          f"saturday {sum(r['day_type'] == 'saturday' for r in good)})")
    print(f"\nbins above the physical bound ({S_MAX} veh/h/lane of green+yellow, + setback storage), "
          "complete/usable weekday+Saturday days:")
    fl = [f for f in flags if any(r["date"] == f["date"] and r in good for r in good)]
    for c in cols:
        fc = [f for f in fl if f["movement"] == c]
        print(f"  {c}: {len(fc):4d} bins on {len({f['date'] for f in fc}):2d} days, "
              f"{veh_flag[c]:6d} of {veh_all[c]:7d} veh ({100 * veh_flag[c] / max(1, veh_all[c]):.2f} %); "
              f"bins above the same bound at {HCM}: {above_hcm[c]}")
    by_hour = Counter(f["time"][:2] for f in fl)
    print("  flagged bins by hour:", dict(sorted(by_hour.items())))
    print(f"\nwrote {out.relative_to(HERE.parents[2])}/days.csv, flagged_bins.csv ({len(flags)} rows)")


if __name__ == "__main__":
    main()
