"""Reader for 7111 Timing & Actuation charts (5-min windows, DotAndBarSize 4, lane-by-lane count rows shown),
as fetched by tools/lanecheck/tna_fetch.py. Step 3 of MODEL_LOG.md.

read(path) -> {"phase_display": [(t0, t1, state)], "rows": [[t_on, ...] per detector row, top to bottom]}
  state: "G" green (incl. the darker 'min green' shade), "Y" yellow, "R" red clearance (dark red), "r" red.
  t in seconds from the window start (0..300).
Detector events: each vehicle is drawn as a dark triangle (detector on) followed by a grey square (off). Marker
pixels = low-saturation pixels (backgrounds are saturated red/green/yellow); runs of marker columns are bridged over
gaps <= 2 px; each dark core inside a run is one on event. Checked against 1-min charts (Step 3, MODEL_LOG.md).
"""
import numpy as np
from PIL import Image
from scipy import ndimage

WIN = 300.0
DARK = 300        # pixel sum below which a marker pixel is a triangle core (on event)


def _frame(a):
    blk = a.sum(2) < 150
    H, W = blk.shape
    # horizontal grid lines: long dark runs
    hl = [y for y in range(H) if blk[y].mean() > 0.5]
    lines = []
    for y in hl:
        if not lines or y - lines[-1] > 2:
            lines.append(y)
    ya, yb = lines[0], lines[-1]
    vl = [x for x in range(W) if blk[ya + 1:yb, x].mean() > 0.8]
    return lines, vl


def _state(px):
    r, g, b = px
    if g > 150 and r < 150:
        return "G"
    if r > 200 and g > 200 and b < 120:
        return "Y"
    if r > 150 and g < 60:
        return "R"
    if r > 190 and 90 < g < 160:
        return "r"
    if 30 < r < 120 and 140 < g < 200:          # darker green shade (min green)
        return "G"
    return None


def read(path, minutes=5):
    a = np.asarray(Image.open(path).convert("RGB")).astype(int)
    lines, vl = _frame(a)
    x0, x1 = vl[0], vl[-1]
    win = minutes * 60.0
    sec = (x1 - x0) / win
    grid = np.zeros(a.shape[1], bool)
    for x in vl:
        grid[max(0, x - 2):x + 3] = True
    out = {"phase_display": [], "rows": [], "px_per_s": sec}
    # display row = first band
    ya, yb = lines[0], lines[1]
    y = (ya + yb) // 2
    states, cur = [], None
    for x in range(x0 + 1, x1):
        s = None if grid[x] else _state(a[y, x])
        s = s or cur
        states.append(s)
        cur = s
    t = lambda x: (x - x0) / sec  # noqa: E731
    seg_s, seg_a = states[0], x0 + 1
    for i, s in enumerate(states[1:], start=x0 + 2):
        if s != seg_s:
            out["phase_display"].append((t(seg_a), t(i), seg_s))
            seg_s, seg_a = s, i
    out["phase_display"].append((t(seg_a), win, seg_s))
    for i in range(1, len(states)):                   # colour edges blend into grey: not markers
        if states[i] != states[i - 1]:
            grid[x0 + 1 + i - 2:x0 + 1 + i + 3] = True
    # detector rows
    for ya, yb in zip(lines[1:-1], lines[2:]):
        band = a[ya + 2:yb - 1, x0 + 2:x1 - 1]
        g = grid[x0 + 2:x1 - 1]
        mx, mn = band.max(2), band.min(2)
        mark = (mx - mn < 70) & (mx < 200)               # grey / dark marker pixels; backgrounds are saturated
        mark[:, g] = False
        col = mark.any(0)
        dark = (band.sum(2) < DARK).any(0) & ~g          # triangle cores (detector on) are darker than the squares
        cl = col.copy()                                  # bridge gaps <= 2 px (JPEG, grid lines)
        for x in range(1, len(col) - 1):
            if not col[x] and col[max(0, x - 2):x].any() and col[x + 1:x + 3].any():
                cl[x] = True
        on, x = [], 0
        while x < len(cl):
            if cl[x]:
                s0 = x
                while x < len(cl) and cl[x]:
                    x += 1
                cores, y = [], s0                        # dark sub-runs inside this run = vehicles
                while y < x:
                    if dark[y]:
                        c0 = y
                        while y < x and dark[y]:
                            y += 1
                        cores.append((c0 + y - 1) / 2)
                    y += 1
                if not cores:
                    cores = [s0 + 1.0]                  # faint marker: one vehicle at the run start
                on += [t(x0 + 2 + c) for c in cores]
            x += 1
        out["rows"].append(sorted(on))
    return out


if __name__ == "__main__":
    import sys
    for p in sys.argv[1:]:
        r = read(p)
        print(p, "display", [(round(a), round(b), s) for a, b, s in r["phase_display"]])
        for i, row in enumerate(r["rows"]):
            print("  row", i, len(row), [round(x) for x in row])
