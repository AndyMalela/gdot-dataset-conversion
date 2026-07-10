"""Command-line interface.

Approach Volume charts (15-min per-direction volume):
    atspm-digitizer process --image <path>                [--plot] [--dry-run]
    atspm-digitizer process --date MMDD --data-dir <dir>  [--plot] [--dry-run]
    atspm-digitizer process --all       --data-dir <dir>  [--plot] [--dry-run]

Turning Movement Count charts (5-min per-movement TOTAL volume):
    atspm-digitizer tmc --image <path>                [--plot] [--dry-run]
    atspm-digitizer tmc --date MMDD --data-dir <dir>  [--plot] [--dry-run]
    atspm-digitizer tmc --all       --data-dir <dir>  [--plot] [--dry-run]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2

from . import mdtables, output, tmc_output
from .extract import extract_series
from .naming import ChartImage, discover_images, parse_image_path
from .plotbox import find_plot_box
from .tmc_extract import extract_total
from .tmc_naming import discover_charts, parse_chart_path
from .validate import validation_report
from .yaxis import read_y_axis


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="atspm-digitizer",
        description="Digitize ATSPM Approach Volume charts into 15-min volume CSVs",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("process", help="extract volume series from chart image(s)")
    sel = p.add_mutually_exclusive_group(required=True)
    sel.add_argument("--image", type=Path, help="process a single chart image")
    sel.add_argument("--date", help="process the images of one day (MMDD)")
    sel.add_argument("--all", action="store_true",
                     help="process every chart image in the data dir")
    p.add_argument("--data-dir", type=Path,
                   help="intersection data dir, e.g. data/7065 "
                        "(required with --date/--all)")
    p.add_argument("--plot", action="store_true",
                   help="save QA overlay images of the extracted traces")
    p.add_argument("--interpolate", action="store_true",
                   help="linearly bridge short interior gaps (<=3 bins); "
                        "OFF by default — output is otherwise raw, gaps kept as NaN")
    p.add_argument("--dry-run", action="store_true",
                   help="report what would be processed without extracting")

    t = sub.add_parser("tmc", help="extract per-movement TOTAL from TMC chart(s)")
    tsel = t.add_mutually_exclusive_group(required=True)
    tsel.add_argument("--image", type=Path, help="process a single TMC chart image")
    tsel.add_argument("--date", help="process the TMC charts of one day (MMDD)")
    tsel.add_argument("--all", action="store_true",
                      help="process every TMC chart in the data dir")
    t.add_argument("--data-dir", type=Path,
                   help="TMC data dir, e.g. tmc/7065 (required with --date/--all)")
    t.add_argument("--plot", action="store_true",
                   help="save QA overlay images of the extracted total line")
    t.add_argument("--dry-run", action="store_true",
                   help="report what would be processed without extracting")
    return parser


def _select_images(args: argparse.Namespace) -> tuple[list[ChartImage], Path]:
    """Resolve the requested images and the intersection dir they live in."""
    if args.image is not None:
        if not args.image.exists():
            sys.exit(f"error: image not found: {args.image}")
        return [parse_image_path(args.image)], args.image.resolve().parent

    if args.data_dir is None:
        sys.exit("error: --data-dir is required with --date/--all")
    if not args.data_dir.is_dir():
        sys.exit(f"error: not a directory: {args.data_dir}")
    images = discover_images(args.data_dir, date=args.date)
    if not images:
        what = f"date {args.date}" if args.date else "any date"
        sys.exit(f"error: no chart images for {what} in {args.data_dir}")
    return images, args.data_dir


def _process_one(
    img: ChartImage, out_dir: Path, plot: bool, interpolate: bool = False
) -> tuple[str, "output.pd.DataFrame"]:
    bgr = cv2.imread(str(img.path), cv2.IMREAD_COLOR)
    if bgr is None:
        raise RuntimeError(f"cannot read image {img.path}")
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    box = find_plot_box(gray)
    yaxis = read_y_axis(gray, box)
    series = extract_series(bgr, box, yaxis, img.directions, interpolate=interpolate)

    truth = None
    if img.md_path.exists():
        truth = mdtables.parse_md(img.md_path).get(img.stem)
    report = validation_report(img, yaxis, series, truth)

    csv_path = output.write_csv(out_dir, img, series)
    output.write_validation(out_dir, img, report)
    print(report)
    print(f"wrote {csv_path}")
    if plot:
        overlay = output.write_overlay(out_dir, img, bgr, box, series)
        print(f"wrote {overlay}")
    print()
    return img.date, output.series_frame(img, series)


def _select_charts(args: argparse.Namespace):
    """Resolve requested TMC charts and their intersection dir."""
    if args.image is not None:
        if not args.image.exists():
            sys.exit(f"error: image not found: {args.image}")
        return [parse_chart_path(args.image)], args.image.resolve().parent
    if args.data_dir is None:
        sys.exit("error: --data-dir is required with --date/--all")
    if not args.data_dir.is_dir():
        sys.exit(f"error: not a directory: {args.data_dir}")
    charts = discover_charts(args.data_dir, date=args.date)
    if not charts:
        what = f"date {args.date}" if args.date else "any date"
        sys.exit(f"error: no TMC charts for {what} in {args.data_dir}")
    return charts, args.data_dir


def _tmc_process_one(chart, out_dir: Path, plot: bool):
    series = extract_total(chart)
    report = tmc_output.validation_report(chart, series)
    csv_path = tmc_output.write_csv(out_dir, chart, series)
    tmc_output.write_validation(out_dir, chart, report)
    print(report)
    print(f"wrote {csv_path}")
    if plot:
        print(f"wrote {tmc_output.write_overlay(out_dir, chart, series)}")
    print()
    return chart.date, tmc_output.series_frame(chart, series)


def _run_tmc(args: argparse.Namespace) -> None:
    charts, code_dir = _select_charts(args)
    out_dir = tmc_output.result_dir(code_dir)
    if args.dry_run:
        print(f"intersection code: {code_dir.resolve().name}")
        print(f"output dir:        {out_dir}")
        print(f"would process {len(charts)} TMC chart(s):")
        for c in charts:
            print(f"  {c.path.name}  (date {c.date}, {c.approach_name} {c.movement_name})")
        return
    frames, failures = [], []
    for c in charts:
        try:
            frames.append(_tmc_process_one(c, out_dir, args.plot))
        except Exception as e:
            failures.append((c, e))
            print(f"FAILED {c.path.name}: {e}\n", file=sys.stderr)
    if args.all and frames:
        print(f"wrote {tmc_output.write_consolidated(out_dir, frames)}")
    if failures:
        sys.exit(f"{len(failures)} of {len(charts)} chart(s) failed")


def main(argv: list[str] | None = None) -> None:
    args = _build_parser().parse_args(argv)
    if args.command == "tmc":
        _run_tmc(args)
        return
    images, code_dir = _select_images(args)
    out_dir = output.result_dir(code_dir)

    if args.dry_run:
        print(f"intersection code: {code_dir.resolve().name}")
        print(f"output dir:        {out_dir}")
        print(f"would process {len(images)} image(s):")
        for img in images:
            md = "ok" if img.md_path.exists() else "MISSING"
            print(f"  {img.path.name}  (date {img.date}, pair {img.pair}, "
                  f"sensor {img.sensor}, md: {md})")
        return

    frames = []
    failures = []
    for img in images:
        try:
            frames.append(_process_one(img, out_dir, args.plot, args.interpolate))
        except Exception as e:
            failures.append((img, e))
            print(f"FAILED {img.path.name}: {e}\n", file=sys.stderr)

    if args.all and frames:
        path = output.write_consolidated(out_dir, frames)
        print(f"wrote {path}")
    if failures:
        sys.exit(f"{len(failures)} of {len(images)} image(s) failed")


if __name__ == "__main__":
    main()
