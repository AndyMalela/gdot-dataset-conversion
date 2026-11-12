"""Count detector-on markers (black triangles) per row of a Timing & Actuation chart."""
import sys
import numpy as np
from PIL import Image

def rows(path, debug=False):
    im = np.asarray(Image.open(path).convert("RGB")).astype(int)
    H, W = im.shape[:2]
    dark = im.sum(axis=2) < 200
    colrun = dark.sum(axis=0)
    xs = [x for x in range(W) if colrun[x] > 0.35 * H]
    x0, x1 = xs[0], xs[-1]
    inner = dark[:, x0 + 2:x1 - 1]
    hl = [y for y in range(H) if inner[y].mean() > 0.6]
    lines = []
    for y in hl:
        if not lines or y - lines[-1] > 2:
            lines.append(y)
    out = []
    for i, (ya, yb) in enumerate(zip(lines[:-1], lines[1:])):
        sub = dark[ya + 2:yb - 1, x0 + 2:x1 - 1].copy()
        grid = sub.mean(axis=0) > 0.8
        col = sub.any(axis=0)
        col[grid] = False
        for x in np.flatnonzero(grid):                        # a marker lying across a grid line stays one blob
            if 0 < x < len(col) - 1:
                l = x - 1
                while l > 0 and grid[l]:
                    l -= 1
                r = x + 1
                while r < len(col) - 1 and grid[r]:
                    r += 1
                if col[l] and col[r]:
                    col[x] = True
        black = (im[ya + 2:yb - 1, x0 + 2:x1 - 1].sum(axis=2) < 110)      # marker core, not JPEG ringing at colour edges
        black[:, grid] = False
        widths, w, start = [], 0, 0
        for x, v in enumerate(list(col) + [False]):
            if v:
                if not w:
                    start = x
                w += 1
            elif w:
                if black[:, start:x].sum() >= 3:
                    widths.append(w)
                w = 0
        out.append(widths)
    return out, (x0, x1), lines

if __name__ == "__main__":
    r, fr, lines = rows(sys.argv[1])
    print("frame", fr, "bands", len(r))
    for i, w in enumerate(r):
        print(i, len(w), sorted(set(w)), w if len(w) < 25 else "")


def labels(path, lines):
    """binary label crop per band (text left of the plot frame)"""
    im = np.asarray(Image.open(path).convert("L")).astype(int)
    return [(im[ya + 3:ya + 19, 60:300] < 128) for ya in lines[:-1]]

_REF = {}
def row_ids(path, lines, ref_path):
    """index of each band in the reference (full, 11-row) chart, by label image match"""
    if ref_path not in _REF:
        _, _, rl = rows(ref_path)
        _REF[ref_path] = labels(ref_path, rl)
    ref = _REF[ref_path]
    out = []
    for lab in labels(path, lines):
        d = [np.mean(lab != r) if lab.shape == r.shape else 1.0 for r in ref]
        out.append((int(np.argmin(d)), float(min(d))))
    return out
