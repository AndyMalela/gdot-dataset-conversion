"""Draw a reproducible stratified random sample of intersections from a screening file.

Steps
  1. Eligibility: drop signals with too little data or too few detected approaches.
  2. Strata: volume tertile (low/med/high) x complexity (simple/standard/complex).
  3. Within each cell: shuffle with a fixed seed; the first --per-cell are selected.
  4. Replacement: list a failed site in rejections_<label>.csv (signal_id,reason) and
     re-run; the next site in that cell's shuffled order takes its place. Never hand-pick.
  5. Report: frame vs sample counts per cell, balance table, design weights.

Examples
    python3 tools/atspm_signals/sample.py screening_atlanta.csv
    python3 tools/atspm_signals/sample.py screening_atlanta.csv --per-cell 5 --seed 7

Complexity (proxy from detector layout -- check against satellite imagery / signal timing):
    simple    no exclusive left-turn detector on any approach (lefts shared with throughs, or absent)
    standard  exclusive left-turn detectors on 1-2 approaches
    complex   exclusive left-turn detectors on 3+ approaches, or 5+ approaches
  Exclusive left-turn lanes with their own detectors usually mean protected/permitted left
  phases, i.e. more phases. If the screening CSV has a `complexity` column (filled by hand
  or from phase data), it overrides the proxy.

Output (this folder)
    sample_<label>.csv          every eligible signal: cell, rank in cell, selected, weight
    sample_<label>_report.md    eligibility counts, cell table, balance table, settings
"""
import argparse
import csv
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
VOLUME_LEVELS = ["low", "med", "high"]
COMPLEXITY_LEVELS = ["simple", "standard", "complex"]
BALANCE_VARS = ["peak_hour_volume", "hourly_volume", "left_share", "major_share",
                "n_approaches", "n_movements", "daytime_valid_pct"]


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def complexity(row):
    if row.get("complexity"):
        return row["complexity"].strip()
    movs = row.get("movements", "").split()
    approaches = {m.split("_")[0] for m in movs}
    excl_left = {m.split("_")[0] for m in movs if m.endswith("_L")}
    if len(approaches) >= 5 or len(excl_left) >= 3:
        return "complex"
    if excl_left:
        return "standard"
    return "simple"


def tertile_cuts(values):
    v = sorted(values)
    return v[len(v) // 3], v[2 * len(v) // 3]


def volume_level(x, cuts):
    return "low" if x < cuts[0] else ("med" if x < cuts[1] else "high")


def summary(rows, var):
    vals = [num(r[var]) for r in rows if num(r.get(var)) is not None]
    return f"{statistics.median(vals):.3g}" if vals else "-"


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("screening_csv", help="screening_<label>.csv from screen.py (path or name in this folder)")
    p.add_argument("--per-cell", type=int, default=4, help="sites selected per cell (default 4)")
    p.add_argument("--seed", type=int, default=20261004, help="random seed (default 20261004); keep it fixed")
    p.add_argument("--min-daytime-valid", type=float, default=90, help="min %% valid 06-20h bins (default 90)")
    p.add_argument("--min-approaches", type=int, default=3, help="min detected approaches (default 3)")
    a = p.parse_args()

    src = Path(a.screening_csv)
    if not src.exists():
        src = HERE / a.screening_csv
    label = src.stem.replace("screening_", "")
    rows = list(csv.DictReader(open(src)))

    rej_path = HERE / f"rejections_{label}.csv"
    rejected = {}
    if rej_path.exists():
        rejected = {r["signal_id"]: r.get("reason", "") for r in csv.DictReader(open(rej_path))}

    # 1. eligibility
    reasons = Counter()
    eligible = []
    for r in rows:
        if num(r.get("days_with_data")) in (None, 0):
            reasons["no data returned"] += 1
        elif (num(r.get("daytime_valid_pct")) or 0) < a.min_daytime_valid:
            reasons[f"daytime coverage < {a.min_daytime_valid:g}%"] += 1
        elif (num(r.get("n_approaches")) or 0) < a.min_approaches:
            reasons[f"fewer than {a.min_approaches} approaches detected"] += 1
        elif num(r.get("peak_hour_volume")) is None:
            reasons["no complete peak hour"] += 1
        else:
            eligible.append(r)
    if not eligible:
        raise SystemExit("No eligible signals -- screen more signals or relax the filters.")

    # 2. strata
    cuts = tertile_cuts([num(r["peak_hour_volume"]) for r in eligible])
    cells = defaultdict(list)
    for r in eligible:
        r["volume_level"] = volume_level(num(r["peak_hour_volume"]), cuts)
        r["complexity_level"] = complexity(r)
        r["cell"] = f"{r['volume_level']}/{r['complexity_level']}"
        cells[r["cell"]].append(r)

    # 3-4. shuffle within cell (sorted first so the order doesn't depend on input order), select
    rng = random.Random(a.seed)
    for cell in sorted(cells):
        members = sorted(cells[cell], key=lambda r: r["signal_id"])
        rng.shuffle(members)
        taken = 0
        for rank, r in enumerate(members, 1):
            r["rank_in_cell"] = rank
            r["rejected_reason"] = rejected.get(r["signal_id"], "")
            r["selected"] = int(not r["rejected_reason"] and taken < a.per_cell)
            taken += r["selected"]
        n_sel = max(taken, 1)
        for r in members:
            r["weight"] = round(len(members) / n_sel, 3) if r["selected"] else ""
        cells[cell] = members

    ordered = [r for cell in sorted(cells) for r in cells[cell]]
    out = HERE / f"sample_{label}.csv"
    lead = ["selected", "cell", "rank_in_cell", "weight", "rejected_reason", "signal_id", "name",
            "volume_level", "complexity_level"]
    rest = [k for k in rows[0] if k not in lead]
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=lead + rest, extrasaction="ignore")
        w.writeheader()
        w.writerows(ordered)

    # 5. report
    selected = [r for r in ordered if r["selected"]]
    L = [f"# Stratified sample — {label}", "",
         f"Seed `{a.seed}` · {a.per_cell} per cell · source `{src.name}`", "",
         "## Eligibility", "",
         f"- Screened: {len(rows)}", f"- Eligible: {len(eligible)}"]
    L += [f"- Excluded, {k}: {v}" for k, v in reasons.most_common()]
    L += [f"- Rejected after selection (replaced): {sum(1 for r in ordered if r['rejected_reason'])}", "",
          f"Peak-hour volume tertile cuts: low < {cuts[0]:.0f} ≤ med < {cuts[1]:.0f} ≤ high (veh/h)", "",
          "## Cells (frame → selected)", "",
          "| complexity \\ volume | " + " | ".join(VOLUME_LEVELS) + " |",
          "|---|" + "---|" * len(VOLUME_LEVELS)]
    short = []
    for c in COMPLEXITY_LEVELS:
        line = []
        for v in VOLUME_LEVELS:
            m = cells.get(f"{v}/{c}", [])
            s = sum(r["selected"] for r in m)
            line.append(f"{len(m)} → {s}")
            if s < a.per_cell:
                short.append(f"{v}/{c}")
        L.append(f"| {c} | " + " | ".join(line) + " |")
    L.append("")
    if short:
        L += [f"**Short cells** (fewer than {a.per_cell} available): {', '.join(short)}. "
              "Screen more signals, merge with a neighbouring cell, or move the cut points.", ""]
    L += ["## Balance (medians): frame vs sample", "",
          "| variable | frame | sample |", "|---|---|---|"]
    L += [f"| {v} | {summary(eligible, v)} | {summary(selected, v)} |" for v in BALANCE_VARS]
    L += ["", "## Selected sites", "", "| cell | rank | signal | name | weight |", "|---|---|---|---|---|"]
    L += [f"| {r['cell']} | {r['rank_in_cell']} | {r['signal_id']} | {r.get('name', '')} | {r['weight']} |"
          for r in selected]
    L += ["", "Weight = eligible signals in the cell / selected in the cell. Use it to turn "
          "per-cell results into city-wide estimates.",
          f"To replace a site: add `signal_id,reason` to `{rej_path.name}` and re-run."]
    rep = HERE / f"sample_{label}_report.md"
    rep.write_text("\n".join(L) + "\n")

    print(f"{len(rows)} screened, {len(eligible)} eligible, {len(selected)} selected "
          f"in {len(cells)} cells (seed {a.seed})")
    if short:
        print(f"short cells: {', '.join(short)}")
    print(f"-> {out.relative_to(HERE.parent.parent)}\n-> {rep.relative_to(HERE.parent.parent)}")


if __name__ == "__main__":
    main()
