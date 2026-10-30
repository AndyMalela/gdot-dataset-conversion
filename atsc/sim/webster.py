"""Webster pretimed plan for a NEMA dual-ring signal, honouring every phase's minimum service.

    plan = design(sig, flow, lanes, s_lane, name="W-C")
    flow:  {phase: veh/h}  (design-hour demand of the movement the phase serves)
    lanes: {phase: lanes}; s_lane: saturation flow per lane (veh/h of green)

Webster (1958): C0 = (1.5 L + 5) / (1 - Y), Y = sum of critical flow ratios, L = lost time on the critical
path (yellow + red of each critical phase). Effective green C0 - L is split in proportion to flow ratios
along each ring of each barrier group. Phases then get at least their minimum service (min green or ped
walk + flashing don't walk) plus clearance; where that is binding the cycle grows, never the minimum shrinks.
"""
from __future__ import annotations

from .nema import Plan

C_MIN, C_MAX = 60.0, 180.0      # GDOT's plans at 7065 run 120-180 s


def design(sig, flow, lanes, s_lane, name="W"):
    rings = {int(r): [tuple(g) for g in gs] for r, gs in sig["rings"].items()}
    ph = {int(k): v for k, v in sig["phases"].items()}
    clr = {p: v["yellow"] + v["red"] for p, v in ph.items()}
    mins = {p: max(v["min_green"], v["ped_min"]) + clr[p] for p, v in ph.items()}
    y = {p: flow.get(p, 0.0) / (lanes[p] * s_lane) for p in ph}

    # critical path per barrier group: the ring with the larger sum of flow ratios
    groups = range(len(rings[1]))
    crit = {g: max((1, 2), key=lambda r: sum(y[p] for p in rings[r][g])) for g in groups}
    Y = sum(y[p] for g in groups for p in rings[crit[g]][g])
    L = sum(clr[p] for g in groups for p in rings[crit[g]][g])
    C = (1.5 * L + 5) / (1 - Y) if Y < 0.95 else C_MAX
    C = min(max(C, C_MIN), C_MAX)

    # group lengths: clearances of the critical path + effective green shared by its flow ratios
    g_eff = C - L
    gl = {g: sum(clr[p] for p in rings[crit[g]][g])
          + (g_eff * sum(y[p] for p in rings[crit[g]][g]) / Y if Y > 0 else g_eff / len(groups)) for g in groups}
    # every ring of a group must fit its phases' minimum services; extra time comes from groups with slack,
    # and only if there is not enough slack does the cycle grow
    need = {g: max(sum(mins[p] for p in rings[r][g]) for r in (1, 2)) for g in groups}
    short = sum(max(0.0, need[g] - gl[g]) for g in groups)
    slack = {g: max(0.0, gl[g] - need[g]) for g in groups}
    take = min(short, sum(slack.values()))
    for g in groups:
        gl[g] = max(gl[g], need[g]) - (take * slack[g] / sum(slack.values()) if take > 0 else 0.0)
    sp = {}
    for g in groups:
        for r in (1, 2):
            seq = rings[r][g]
            free = gl[g] - sum(mins[p] for p in seq)
            ys = sum(y[p] for p in seq)
            for p in seq:
                sp[p] = mins[p] + (free * y[p] / ys if ys > 0 else free / len(seq))
    sp = {p: round(v, 1) for p, v in sp.items()}
    return Plan(name, round(sum(gl.values()), 1), sp, coordinated=()), {"Y": round(Y, 3), "L": round(L, 1), "C0": round(C, 1),
                                                                         "y": {p: round(v, 3) for p, v in y.items()}}
