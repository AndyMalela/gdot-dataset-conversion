"""One-off bootstrap: extract 0-9 digit templates from a sample ATSPM chart.

The ATSPM portal renders every chart with the same font, so templates
extracted once work for all charts. We use a chart whose y-axis label
sequence is known (top label down in fixed steps), which lets each glyph
be auto-labeled: row k's label value is known, and its glyphs sorted by
x spell that number.

The portal uses (at least) two font sizes depending on label density, so
pass one known chart per font size; all variants land in one template set.

Usage:
    uv run python scripts/make_digit_templates.py \
        <chart.jpg> <top_value> <step> [<chart.jpg> <top_value> <step> ...]

e.g.  uv run python scripts/make_digit_templates.py \
          ../data/7065/0506_nbsb_matrix.jpg 10000 200 \
          ../data/7065/0506_ebwb_matrix.jpg 3400 200
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from atspm_digitizer.plotbox import find_plot_box
from atspm_digitizer.yaxis import LABEL_STRIP_WIDTH, label_glyphs

OUT_DIR = Path(__file__).resolve().parents[1] / "src" / "atspm_digitizer" / "digits"


def main() -> None:
    args = sys.argv[1:]
    assert args and len(args) % 3 == 0, "args: <chart> <top_value> <step> ..."
    samples: dict[str, list[np.ndarray]] = defaultdict(list)

    for i in range(0, len(args), 3):
        img_path, top_value, step = Path(args[i]), int(args[i + 1]), int(args[i + 2])
        gray = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
        box = find_plot_box(gray)

        rows = label_glyphs(gray, box)
        print(f"{img_path.name}: found {len(rows)} label rows")

        # Assign values by chaining y-gaps rather than by row index or a
        # global spacing fit: each consecutive gap rounds to an integer
        # number of label steps, so spurious rows (stray text) collapse
        # onto a neighbor (0 steps) instead of shifting everything, and
        # there is no cumulative drift. Anchor: the bottom row is the 0
        # label at the box bottom edge.
        # Single-glyph rows are stray title letters — except the 0 label
        # at the box bottom, the only genuine one-digit label.
        rows_sorted = sorted(
            (r for r in rows
             if len(r[1]) >= 2 or abs(r[0] - box.bottom) < 5),
            key=lambda r: r[0],
        )
        ys = np.array([y for y, _ in rows_sorted])
        diffs = np.diff(ys)
        med = np.median(diffs)
        spacing = float(np.median(diffs[(diffs > 0.7 * med) & (diffs < 1.3 * med)]))
        chain = np.concatenate([[0], np.cumsum(np.round(diffs / spacing))])
        n_above_bottom = chain[-1] - chain  # steps above the bottom row
        if abs(ys[-1] - box.bottom) > spacing / 2:
            print(f"  WARNING: bottom row y={ys[-1]:.0f} is not at box "
                  f"bottom {box.bottom} — anchor suspect, skipping image")
            continue
        if n_above_bottom[0] * step != top_value:
            print(f"  WARNING: top row works out to "
                  f"{n_above_bottom[0] * step:.0f}, expected {top_value} "
                  f"— skipping image")
            continue
        used = 0
        for n, (ycenter, glyphs) in zip(n_above_bottom, rows_sorted):
            text = str(int(n) * step)
            if len(glyphs) != len(text):
                print(f"  row at y={ycenter:.0f} (expect {text}): "
                      f"{len(glyphs)} glyphs, skipping")
                continue
            for ch, (gx, bitmap) in zip(text, glyphs):
                samples[ch].append(bitmap)
            used += 1
        print(f"  used {used} rows")

    OUT_DIR.mkdir(exist_ok=True)
    for old in OUT_DIR.glob("*.png"):
        old.unlink()
    for ch in "0123456789":
        if not samples[ch]:
            print(f"digit {ch}: NO SAMPLES")
            continue
        # The tiny JPEG-degraded font renders each digit in a few
        # distinct variants (sometimes split or filled differently).
        # Save a representative per bounding-box shape so the runtime
        # matcher can hit whichever variant a chart produced.
        by_shape: dict[tuple, list[np.ndarray]] = defaultdict(list)
        for b in samples[ch]:
            by_shape[b.shape].append(b)
        variants = sorted(by_shape.items(), key=lambda kv: -len(kv[1]))[:5]
        for k, (shape, group) in enumerate(variants):
            stack = np.stack(group).astype(np.float32)
            med = np.median(stack, axis=0)
            best = group[int(np.argmin([np.abs(b - med).sum() for b in stack]))]
            cv2.imwrite(str(OUT_DIR / f"{ch}_{k}.png"), best)
        print(
            f"digit {ch}: {len(samples[ch])} samples, "
            + ", ".join(f"{s[1]}x{s[0]}(n={len(g)})" for s, g in variants)
        )


if __name__ == "__main__":
    main()
