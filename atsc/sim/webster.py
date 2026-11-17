"""Webster pretimed plan for a NEMA dual-ring signal, honouring every phase's minimum service.

    plan = design(sig, flow, lanes, s_lane, name="W-C")
    flow:  {phase: veh/h}  (design-hour demand of the movement the phase serves)
    lanes: {phase: lanes}; s_lane: saturation flow per lane (veh/h of green)

Webster (1958): C0 = (1.5 L + 5) / (1 - Y), Y = sum of critical flow ratios, L = lost time on the critical
path (yellow + red of each critical phase). Effective green C0 - L is split in proportion to flow ratios
along each ring of each barrier group. Every phase must also get its minimum service (min green or ped walk +
flashing don't walk) and enough green to stay below X_MAX saturation; the cycle grows from C0 until both hold
for every phase in both rings (capped at C_MAX), and spare time is then shared by flow ratio.
"""
from __future__ import annotations

from .nema import Plan

C_MIN, C_MAX = 60.0, 180.0      # GDOT's plans at 7065 run 120-180 s
X_MAX = 0.9                     # highest degree of saturation accepted for any phase


def design(sig, flow, lanes, s_lane, name="W"):
    rings = {int(r): [tuple(g) for g in gs] for r, gs in sig["rings"].items()}
    ph = {int(k): v for k, v in sig["phases"].items()}
    clr = {p: v["yellow"] + v["red"] for p, v in ph.items()}
    mins = {p: max(v["min_green"], v["ped_min"]) + clr[p] for p, v in ph.items()}
    sat = s_lane if isinstance(s_lane, dict) else {p: s_lane for p in ph}     # per phase (137) or one value
    y = {p: flow.get(p, 0.0) / (lanes[p] * sat[p]) for p in ph}

    # critical path per barrier group: the ring with the larger sum of flow ratios
    groups = range(len(rings[1]))
    crit = {g: max((1, 2), key=lambda r: sum(y[p] for p in rings[r][g])) for g in groups}
    Y = sum(y[p] for g in groups for p in rings[crit[g]][g])
    L = sum(clr[p] for g in groups for p in rings[crit[g]][g])
    C = (1.5 * L + 5) / (1 - Y) if Y < 0.95 else C_MAX
    C = min(max(C, C_MIN), C_MAX)

    # every phase needs its minimum service and enough green to run at most X_MAX saturated; take the shortest
    # cycle >= C0 in which both hold for every phase of both rings, then share the spare time by flow ratio
    def need(p, c):
        return max(mins[p], y[p] * c / X_MAX + clr[p])

    def groups_len(c):
        return {g: max(sum(need(p, c) for p in rings[r][g]) for r in (1, 2)) for g in groups}

    while sum(groups_len(C).values()) > C + 1e-6 and C < C_MAX:
        C += 1.0
    gl = groups_len(C)
    spare = max(0.0, C - sum(gl.values()))
    ycrit = {g: sum(y[p] for p in rings[crit[g]][g]) for g in groups}
    for g in groups:
        gl[g] += spare * (ycrit[g] / Y if Y > 0 else 1 / len(groups))
    sp = {}
    for g in groups:
        for r in (1, 2):
            seq = rings[r][g]
            free = gl[g] - sum(need(p, C) for p in seq)
            ys = sum(y[p] for p in seq)
            for p in seq:
                sp[p] = need(p, C) + (free * y[p] / ys if ys > 0 else free / len(seq))
    sp = {p: round(v, 1) for p, v in sp.items()}
    return Plan(name, round(sum(gl.values()), 1), sp, coordinated=()), {"Y": round(Y, 3), "L": round(L, 1), "C0": round(C, 1),
                                                                         "y": {p: round(v, 3) for p, v in y.items()}}
