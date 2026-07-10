"""Visualize extracted volume CSVs as time-series plots.

Scans result/<code>/*.csv for every intersection code and date, plots
each file's per-direction 15-minute series, and writes PNGs to
testing/<code>/ at the repo root. Data gaps (empty bins) stay visible
as breaks in the line.

Usage:
    uv run python scripts/visualize_results.py
    uv run python scripts/visualize_results.py --result-dir ../atspm_digitizerresult/result --out-dir ../atspm_digitizerresult/testing
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MultipleLocator

REPO_ROOT = Path(__file__).resolve().parents[2]

# First listed direction (NB/EB) is the blue line in the source charts,
# second (SB/WB) the red one; keep the same convention here.
_COLORS = ("tab:blue", "tab:red")


def plot_csv(csv_path: Path, out_path: Path) -> None:
    df = pd.read_csv(csv_path)
    fig, ax = plt.subplots(figsize=(16, 6))

    if "total_vph" in df.columns:  # TMC: one movement TOTAL, 5-min bins
        n = len(df)
        bins_per_hr = n // 24  # 12 for 5-min
        ax.plot(range(n), df["total_vph"], color="black", lw=1.0, marker=".",
                ms=2, label=f"{df['approach'].iloc[0]} {df['movement'].iloc[0]} total")
        title = csv_path.stem
        ylabel = "Total volume (vph)"
    else:  # Approach Volume: per-direction, 15-min bins
        n = 96
        bins_per_hr = 4
        for direction, color in zip(df["direction"].unique(), _COLORS):
            s = df[df["direction"] == direction]
            ax.plot(range(len(s)), s["vph_raw"], color=color, lw=1.2,
                    marker=".", ms=3, label=direction)
        title = f"{csv_path.stem}  ({df['sensor'].iloc[0]})"
        ylabel = "Volume (vph)"

    hours = range(0, n + 1, bins_per_hr)  # a tick every hour, including 24:00
    ax.set_xticks(list(hours))
    ax.set_xticklabels([f"{h // bins_per_hr:02d}:00" for h in hours],
                       rotation=45, ha="right")
    ax.set_xlim(0, n - 1)
    ax.set_ylim(bottom=0)
    ax.yaxis.set_major_locator(MultipleLocator(200))  # a gridline every 200 vph
    ax.set_xlabel("Time of day")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--result-dir", type=Path,
                        default=REPO_ROOT / "atspm_digitizerresult" / "result",
                        help="root of extraction results "
                             "(default: <repo>/atspm_digitizerresult/result)")
    parser.add_argument("--out-dir", type=Path,
                        default=REPO_ROOT / "atspm_digitizerresult" / "testing",
                        help="where to write plots "
                             "(default: <repo>/atspm_digitizerresult/testing)")
    args = parser.parse_args()

    if not args.result_dir.is_dir():
        raise SystemExit(f"error: no result dir at {args.result_dir}")

    n = 0
    for code_dir in sorted(p for p in args.result_dir.iterdir() if p.is_dir()):
        for csv_path in sorted(code_dir.glob("*.csv")):
            if csv_path.name == "consolidated.csv":
                continue  # per-image CSVs already cover its contents
            out_path = args.out_dir / code_dir.name / f"{csv_path.stem}.png"
            plot_csv(csv_path, out_path)
            print(f"wrote {out_path}")
            n += 1
    if n == 0:
        raise SystemExit(f"error: no CSVs found under {args.result_dir}")


if __name__ == "__main__":
    main()
