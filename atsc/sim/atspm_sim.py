"""ATSPM metrics computed from a simulation's own event log, with the portal's definitions, so validation compares
like with like (simulated "ATSPM" numbers vs the numbers the GDOT portal prints; tools/atspm_charts.py).

Inputs: res = episode.run_window(..., record_events=True) -> res["greens"], res["events"]
    greens: [{"phase", "start", "end", "how"}]       (green interval; yellow starts at "end")
    events: {"stopbar": {det: [(on, off)]}, "setback": {det: [arrival t]}, "ped": [(t, phase)],
             "phases": {p: {"yellow", "red"}}, "stopbar_by_phase": {p: [det]}, "setback_by_phase": {p: [det]}}

Definitions (ATSPM 4.x, as printed on GDOT's charts):
- Split Failure: per served cycle of a phase, GOR = share of the green with any of the phase's stop-bar zones
  occupied; ROR5 = same share over the first 5 s of red (red starts at the end of yellow, `red_start`);
  a split failure when GOR > 0.79 and ROR5 > 0.79.
- Approach Delay (simplified, advance detector): each advance-detector arrival, shifted to the stop bar by
  distance / approach speed, that falls in red waits until the next green start; AD = total / all arrivals
  (s/veh), TD = total (h).
- PCD: AoG = share of shifted arrivals during green; GT = green time / window; PR = AoG / GT.
- Wait Time: the stop-bar zones are non-locking, so a call lasts only while a zone is occupied. For each green
  start, if the phase's zones are occupied just before it, wait = green start - start of that continuous
  occupancy (the call that was served); average and maximum. Calls that left without being served (e.g.
  left-turners clearing on the flashing yellow) do not count.
- Pedestrian Delay: presses (PP) and cycles with a press (CPR) per phase.
Window: [t0, t1) in simulation seconds; a cycle/arrival belongs to the window holding its start/arrival.
"""
from __future__ import annotations

import bisect

THRESH = 0.79


def _greens(greens, p):
    return sorted((g["start"], g["end"]) for g in greens if g["phase"] == p and g["end"] == g["end"])  # drop NaN


def _union(intervals):
    out = []
    for a, b in sorted(intervals):
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def _occupied(union, a, b):
    """seconds of [a, b) covered by the merged intervals."""
    return sum(max(0.0, min(b, y) - max(a, x)) for x, y in union if y > a and x < b)


def red_start(g_end, ph):
    """ATSPM's 'red' for split failure starts at the end of yellow (red clearance is red)."""
    return g_end + ph["yellow"]


def split_failures(greens, ev, phase, t0, t1, dets=None, first_red=5.0):
    dets = dets if dets is not None else ev["stopbar_by_phase"].get(phase, [])
    occ = _union([iv for d in dets for iv in ev["stopbar"].get(d, [])])
    ph = ev["phases"][phase]
    n = sf = 0
    for gs, ge in _greens(greens, phase):
        if not t0 <= gs < t1 or ge <= gs:
            continue
        n += 1
        gor = _occupied(occ, gs, ge) / (ge - gs)
        r0 = red_start(ge, ph)
        ror = _occupied(occ, r0, r0 + first_red) / first_red
        sf += gor > THRESH and ror > THRESH
    return {"cycles": n, "split_failures": sf, "sf_pct": 100 * sf / n if n else None}


def _arrivals(ev, phase, offset_s, dets=None):
    dets = dets if dets is not None else ev["setback_by_phase"].get(phase, [])
    return sorted(t + offset_s for d in dets for t in ev["setback"].get(d, []))


def approach_delay(greens, ev, phase, t0, t1, offset_s, dets=None):
    gr = _greens(greens, phase)
    starts = [a for a, _ in gr]
    arr = [t for t in _arrivals(ev, phase, offset_s, dets) if t0 <= t < t1]
    total = 0.0
    for t in arr:
        k = bisect.bisect_right(starts, t) - 1
        if k >= 0 and gr[k][0] <= t < gr[k][1]:
            continue                                    # arrived on green: no delay
        nxt = bisect.bisect_right(starts, t)
        if nxt < len(starts):
            total += starts[nxt] - t
    return {"arrivals": len(arr), "delay_per_veh_s": total / len(arr) if arr else None, "total_delay_h": total / 3600}


def pcd(greens, ev, phase, t0, t1, offset_s, dets=None):
    gr = _greens(greens, phase)
    arr = [t for t in _arrivals(ev, phase, offset_s, dets) if t0 <= t < t1]
    on_green = sum(any(a <= t < b for a, b in gr) for t in arr)
    green_t = sum(max(0.0, min(b, t1) - max(a, t0)) for a, b in gr)
    aog = 100 * on_green / len(arr) if arr else None
    gt = 100 * green_t / (t1 - t0)
    return {"arrivals": len(arr), "aog_pct": aog, "gt_pct": gt, "platoon_ratio": aog / gt if aog is not None and gt else None}


def wait_time(greens, ev, phase, t0, t1, dets=None):
    dets = dets if dets is not None else ev["stopbar_by_phase"].get(phase, [])
    occ = _union([iv for d in dets for iv in ev["stopbar"].get(d, [])])
    starts = [a for a, _ in occ]
    waits = []
    for gs, _ in _greens(greens, phase):
        if not t0 <= gs < t1:
            continue
        k = bisect.bisect_right(starts, gs) - 1            # occupancy that began at or before the green ...
        if k >= 0 and occ[k][1] >= gs - 0.5:               # ... and was still on when it started (0.5 s = step)
            waits.append(gs - occ[k][0])
    return {"calls": len(waits), "avg_wait_s": sum(waits) / len(waits) if waits else None,
            "max_wait_s": max(waits) if waits else None}


def ped_delay(greens, ev, phase, t0, t1):
    presses = [t for t, p in ev["ped"] if p == phase and t0 <= t < t1]
    gr = _greens(greens, phase)
    cycles = {next((i for i, (a, _) in enumerate(gr) if a > t), None) for t in presses}
    return {"ped_presses": len(presses), "cycles_with_requests": len(cycles - {None})}
