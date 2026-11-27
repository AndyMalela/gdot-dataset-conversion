"""Critical flow ratio Y (Webster / HCM) per hour of day, 137 vs 7111, from TRAIN-day counts only.

    uv run python atsc/sites/y_compare.py      -> atsc/sites/Y_COMPARISON.md

Y = sum over the two barrier groups of max over the rings of the sum of phase flow ratios; a phase's flow ratio is
the largest v / (lanes x s) of the lane groups it serves. s = 1,900 veh/h/lane (HCM base saturation flow, no
adjustments; a standard constant, flagged). Simplifications, the same for both sites: protected-permissive lefts
counted as fully protected; right turns on red not deducted; shared through-right lanes as counted.
Hourly volume = mean over usable train days of the hour's 5-min counts (blank bins -> day skipped for that hour).
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
S = 1900.0

SITES = {
    "137": {
        "files": {"as reported (WB through from 138)": "intersections/137/counts/tmc_137_5min_upstream.csv",
                  "with presence-zone undercount estimate (model input, attempt 8)":
                      "intersections/137/counts/tmc_137_5min_estimated.csv"},
        "train": ("2026-03-02", "2026-04-17"), "summary": "intersections/137/counts/daily_summary.csv",
        # barrier groups: ring -> list of phases; phase -> [(column(s), lanes)]
        "barriers": [{1: [1, 2], 2: [5, 6]}, {1: [3, 4], 2: [7, 8]}],
        "phases": {1: [("WB_L", 1)], 2: [("EB_TR", 1)], 5: [("EB_L", 1)], 6: [("WB_TR", 1)],
                   3: [("NB_L", 1)], 4: [("SB_T", 1), ("SB_R", 1)], 7: [("SB_L", 1)], 8: [("NB_T", 1), ("NB_R", 1)]},
    },
    "7111": {
        "files": {"as reported": "intersections/7111/counts/tmc_7111_5min.csv"},
        "train": None, "summary": "intersections/7111/counts/daily_summary.csv",
        "barriers": [{1: [1, 2], 2: [5, 6]}, {1: [3, 4], 2: [8]}],
        "phases": {1: [("NB_L", 1)], 2: [("SB_T", 3)], 5: [("SB_L", 1)], 6: [("NB_T", 2)],
                   3: [("EB_L", 2)], 4: [("WB_L", 1), ("WB_TR", 1)], 8: [("EB_TR", 1)]},
    },
}


def train_days(site):
    cfg = SITES[site]
    summ = {r["date"]: r for r in csv.DictReader(open(REPO / cfg["summary"]))}
    if site == "7111":
        sp = json.load(open(REPO / "atsc/sites/7111/split.json"))
        lo, hi = sp["sets"]["train"]["from"], sp["sets"]["train"]["to"]
        hol = set(sp["holidays"])
    else:
        lo, hi = cfg["train"]
        hol = set()
    ok = set()
    for d, r in summ.items():
        if lo <= d <= hi and d not in hol and (r["status"] == "ok" or
                                               (r["status"] == "partial" and float(r["outage_pct"]) <= 10)):
            ok.add(d)
    return ok


def hourly(path, days, cols):
    acc = defaultdict(lambda: defaultdict(int))          # (day, hour) -> col -> veh
    nbin = defaultdict(int)
    for r in csv.DictReader(open(REPO / path)):
        if r["date"] not in days:
            continue
        if any(r[c] == "" for c in cols):
            continue
        k = (r["date"], int(r["time"][:2]))
        nbin[k] += 1
        for c in cols:
            acc[k][c] += float(r[c])
    out = defaultdict(lambda: defaultdict(list))
    for k, v in acc.items():
        if nbin[k] == 12:
            for c in cols:
                out[k[1]][c].append(v[c])
    return {h: {c: sum(x) / len(x) for c, x in d.items()} for h, d in out.items()}, \
        {h: len(next(iter(d.values()))) for h, d in out.items()}


def y_of(site, vol):
    cfg = SITES[site]
    yp = {p: max(vol[c] / (n * S) for c, n in g) for p, g in cfg["phases"].items()}
    tot, crit = 0.0, []
    for b in cfg["barriers"]:
        ring_sum = {r: sum(yp[p] for p in ph) for r, ph in b.items()}
        r = max(ring_sum, key=ring_sum.get)
        tot += ring_sum[r]
        crit += b[r]
    return tot, crit


def force_section():
    """Second measure, from the signal's own behaviour: share of cycles where a non-coordinated phase ended by
    force-off or max-out (GDOT Split Monitor), train days, bands within 06:00-20:30, checked readings only,
    weighted by band length."""
    out = ["## Second measure: how often phases run to their limit (GDOT Split Monitor, train days)", "",
           "Share of cycles where the phase ended by force-off or max-out, and share skipped; non-coordinated",
           "phases, plan bands inside 06:00-20:30, readings marked ok, weighted by band length. More force-offs and",
           "fewer skips = demand fills the green GDOT gives. Note: it also depends on how generous GDOT's splits are.",
           "", "| site | phase | force-off + max-out % | skip % |", "|---|---|---|---|"]
    tomin = lambda t: int(t[:2]) * 60 + int(t[3:])  # noqa: E731
    for site, phs in (("137", (1, 3, 4, 5, 7, 8)), ("7111", (1, 3, 4, 5, 8))):
        days = train_days(site)
        acc = defaultdict(lambda: [0.0, 0.0, 0.0])
        for r in csv.DictReader(open(REPO / f"intersections/{site}/timing/splitstats_{site}.csv")):
            if r["date"] not in days or r["check"] != "ok" or int(r["phase"]) not in phs:
                continue
            if r["band_start"] < "06:00" or r["band_end"] > "20:30":
                continue
            w = tomin(r["band_end"]) - tomin(r["band_start"])
            a = acc[int(r["phase"])]
            a[0] += w * float(r["force_pct"] or 0)
            a[1] += w
            a[2] += w * float(r["skip_pct"] or 0)
        for ph, a in sorted(acc.items()):
            out.append(f"| {site} | P{ph} | {a[0] / a[1]:.0f} | {a[2] / a[1]:.0f} |")
    return out + [""]


def main():
    lines = ["# Critical flow ratio Y: 137 vs 7111 (train days only)", "",
             "Written by `atsc/sites/y_compare.py` (2026-11-27). Y = sum of the critical phases' flow ratios v/s",
             "(Webster; HCM). s = 1,900 veh/h/lane, the HCM base saturation flow with no adjustments (standard constant,",
             "flagged). Simplifications, the same at both sites: protected-permissive lefts counted as fully protected,",
             "right turns on red not deducted, shared through-right lanes as counted. Y near 1 = the intersection cannot",
             "serve its demand even with no lost time; with lost time L per cycle the practical limit is about 1 - L/C.", ""]
    res = {}
    for site, cfg in SITES.items():
        days = train_days(site)
        cols = sorted({c for g in cfg["phases"].values() for c, _ in g})
        for label, f in cfg["files"].items():
            h, n = hourly(f, days, cols)
            rows = []
            for hr in sorted(h):
                y, crit = y_of(site, h[hr])
                rows.append((hr, y, crit, n[hr], sum(h[hr].values())))
            res[(site, label)] = rows
            lines += [f"## {site} — {label}", "",
                      f"Train days used: {len(days)} ({min(days)} .. {max(days)}); counts `{f}`.", "",
                      "| hour | Y | critical phases | entering veh/h (counted movements) | days |",
                      "|---|---|---|---|---|"]
            for hr, y, crit, nd, v in rows:
                lines.append(f"| {hr:02d} | {y:.2f} | {'-'.join(f'P{p}' for p in crit)} | {v:,.0f} | {nd} |")
            pk = max(rows, key=lambda r: r[1])
            lines += ["", f"Peak hour Y: **{pk[1]:.2f}** at {pk[0]:02d}:00 (critical {'-'.join(f'P{p}' for p in pk[2])}).",
                      ""]
    lines += ["## Summary", "", "| site / counts | peak Y | hour | hours with Y >= 0.6 | hours with Y >= 0.8 |",
              "|---|---|---|---|---|"]
    for (site, label), rows in res.items():
        pk = max(rows, key=lambda r: r[1])
        lines.append(f"| {site} — {label} | {pk[1]:.2f} | {pk[0]:02d}:00 | {sum(r[1] >= .6 for r in rows)} | "
                     f"{sum(r[1] >= .8 for r in rows)} |")
    lines += force_section()
    out = REPO / "atsc/sites/Y_COMPARISON.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines[-6:]))


if __name__ == "__main__":
    main()
