#!/usr/bin/env python3
"""Sort checked signals into complete / incomplete for turning-movement counts.

Complete (like 7065) = all four approaches (EB, WB, NB, SB) have their own left-turn
count (L) plus a through count, either alone (T) or together with right turns (TR), and the
detectors actually log data (not every day all zeros). A left counted together with the
through (TL) is incomplete: the left/through split is what drives permissive-left blocking.

Accepted = incomplete by that rule, but accepted by decision; listed in
intersections/signal_overrides.csv (signal_id, status, note).

Reads intersections/counts_index.csv (written by atspm_tmc.py), so run atspm_tmc.py on a signal
first. Screening caches (raw downloads with no CSV) are skipped.

  python3 tools/check_complete.py

Output: intersections/README.md (status table) and intersections/signal_list.csv
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import INTERSECTIONS  # noqa: E402
HERE = INTERSECTIONS
INDEX = INTERSECTIONS / "counts_index.csv"
APPROACHES = ["EB", "WB", "NB", "SB"]


def classify(r):
    if r["complete"] == "":
        return None, None                              # screening cache, never built
    days, nodata = int(r["days"]), int(r["no_data"] or 0)
    if days == 0 or nodata == days:
        return "incomplete", "detectors log nothing (every day all zeros)"
    cols = r["vehicle_movements"].split()
    moves = {a: {c.split("_", 1)[1] for c in cols if c.startswith(a + "_")} for a in APPROACHES}
    reasons = []
    missing = [a for a in APPROACHES if not moves[a]]
    if missing:
        reasons.append(f"no counts on {'/'.join(missing)}")
    shared = [f"{a}_{m}" for a in APPROACHES for m in sorted(moves[a]) if m in ("TL", "LT")]
    if shared:
        reasons.append(f"left and through counted together: {' '.join(shared)}")
    for a in APPROACHES:
        if moves[a] and not any(x.startswith(a + "_") for x in shared):
            lack = []
            if "L" not in moves[a]:
                lack.append("left")
            if not moves[a] & {"T", "TR"}:
                lack.append("through")
            if lack:
                reasons.append(f"{a} has no {' or '.join(lack)} count")
    if reasons:
        return "incomplete", "; ".join(reasons)
    return "complete", ""


def main():
    over = {}
    ofile = HERE / "signal_overrides.csv"
    if ofile.exists():
        over = {o["signal_id"]: o for o in csv.DictReader(open(ofile))}
    rows = []
    for r in csv.DictReader(open(INDEX)):
        status, why = classify(r)
        if status is None:
            continue
        if r["signal_id"] in over and status == "incomplete":
            status = over[r["signal_id"]]["status"]
            why = f"{why} — {over[r['signal_id']]['note']}"
        rows.append({"signal_id": r["signal_id"], "name": r["name"], "status": status,
                     "dates_checked": f"{r['first']} to {r['last']}", "days": r["days"],
                     "days_complete_partial_nodata": f"{r['complete']}/{r['partial']}/{r['no_data']}",
                     "vehicle_movements": r["vehicle_movements"], "reason": why})
    # keep signals checked earlier whose data folders were later deleted
    seen = {r["signal_id"] for r in rows}
    prev = HERE / "signal_list.csv"
    if prev.exists():
        for r in csv.DictReader(open(prev)):
            if r["signal_id"] not in seen:
                if r["signal_id"] in over and r["status"] == "incomplete":
                    r["status"] = over[r["signal_id"]]["status"]
                rows.append(r)
    order = {"complete": 0, "accepted": 1, "on hold": 2, "incomplete": 3}
    rows.sort(key=lambda x: (order.get(x["status"], 3), int(x["signal_id"])))
    with open(HERE / "signal_list.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    comp = [x for x in rows if x["status"] == "complete"]
    acc = [x for x in rows if x["status"] == "accepted"]
    hold = [x for x in rows if x["status"] == "on hold"]
    inc = [x for x in rows if x["status"] == "incomplete"]
    L = ["# Signal list — turning-movement count completeness", "",
         "Complete (like 7065) = every approach has its own left-turn count plus a through count "
         "(alone, or together with right turns), and the detectors log data. Accepted = fails "
         "that rule but was accepted by decision (`signal_overrides.csv`). Incomplete signals "
         "can't be used for a calibrated twin. "
         "Regenerate with `python3 tools/check_complete.py` after pulling a new signal with "
         "`atspm_tmc.py`.", "",
         f"## Complete ({len(comp)})", "",
         "| Signal | Intersection | Dates checked | Days ok/partial/none | Movements |",
         "|---|---|---|---|---|"]
    L += [f"| {x['signal_id']} | {x['name']} | {x['dates_checked']} | "
          f"{x['days_complete_partial_nodata']} | {x['vehicle_movements']} |" for x in comp]
    L += ["", f"## Accepted by decision ({len(acc)})", "",
          "| Signal | Intersection | Dates checked | Movements | Limitation / decision |", "|---|---|---|---|---|"]
    L += [f"| {x['signal_id']} | {x['name']} | {x['dates_checked']} | "
          f"{x['vehicle_movements']} | {x['reason']} |" for x in acc]
    L += ["", f"## On hold ({len(hold)})", "",
          "| Signal | Intersection | Dates checked | Movements | Why / what's needed |", "|---|---|---|---|---|"]
    L += [f"| {x['signal_id']} | {x['name']} | {x['dates_checked']} | "
          f"{x['vehicle_movements']} | {x['reason']} |" for x in hold]
    L += ["", f"## Incomplete ({len(inc)})", "",
          "| Signal | Intersection | Dates checked | Movements | Why |", "|---|---|---|---|---|"]
    L += [f"| {x['signal_id']} | {x['name']} | {x['dates_checked']} | "
          f"{x['vehicle_movements'] or '–'} | {x['reason']} |" for x in inc]
    (HERE / "README.md").write_text("\n".join(L) + "\n")
    print(f"{len(comp)} complete, {len(acc)} accepted, {len(hold)} on hold, {len(inc)} incomplete "
          "-> intersections/README.md")


if __name__ == "__main__":
    main()
