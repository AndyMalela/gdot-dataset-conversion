"""Controller statistics computed the way ATSPM's Split Monitor computes them, from simulated green records.

    split_stats(res["greens"], res["cycle_starts"], phases, bands)
    -> {(band_start, band_end, phase): {"cycles", "avg_split_s", "p85_split_s", "gap_pct", "force_pct", "skip_pct"}}

split = green + yellow + red clearance; per cycle a phase is gapped out, forced off (incl. max-out) or
skipped, so the three percentages add up to 100 (as on the Split Monitor chart).
"""
from __future__ import annotations


def hhmm_s(t):
    h, m = map(int, t.split(":"))
    return h * 3600 + m * 60


def split_stats(greens, cycle_starts, phases, bands):
    """phases: {p: (yellow, red)}; bands: [(\"HH:MM\", \"HH:MM\")]; a cycle belongs to the band holding its start."""
    starts = sorted(cycle_starts)
    cycles = list(zip(starts, starts[1:]))
    by_cycle = {}
    for g in greens:
        k = next((i for i, (a, b) in enumerate(cycles) if a <= g["start"] < b), None)
        if k is not None:
            by_cycle.setdefault((k, g["phase"]), g)
    out = {}
    for b0, b1 in bands:
        s0, s1 = hhmm_s(b0), hhmm_s(b1)
        ks = [i for i, (a, _) in enumerate(cycles) if s0 <= a < s1]
        if not ks:
            continue
        for p, (y, r) in phases.items():
            served = [by_cycle[(k, p)] for k in ks if (k, p) in by_cycle]
            splits = sorted(g["end"] - g["start"] + y + r for g in served)
            gap = sum(g["how"] == "gap" for g in served)
            out[(b0, b1, p)] = {
                "cycles": len(ks),
                "avg_split_s": sum(splits) / len(splits) if splits else None,
                "p85_split_s": splits[min(len(splits) - 1, int(0.85 * len(splits)))] if splits else None,
                "gap_pct": 100 * gap / len(ks),
                "force_pct": 100 * (len(served) - gap) / len(ks),
                "skip_pct": 100 * (len(ks) - len(served)) / len(ks)}
    return out
