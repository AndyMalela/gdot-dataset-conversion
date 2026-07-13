"""Canonical peak-window total-delay extractor (reconstructs the metric whose
generating script was not saved -- only its .txt output survived).

Definition (from EXP-002 3.4 "peak-window 15-18h, by intended depart"):
  over trips whose INTENDED departure (depart - departDelay, i.e. when the
  vehicle WANTED to enter, before any insertion wait) falls in 15:00-18:00,
  report mean TOTAL delay = timeLoss + departDelay.

This script both (a) VERIFIES it reproduces the recorded per-seed v3 numbers
from the saved tripinfos, and (b) is the single canonical pipeline every seed
(old and new) is measured through, so the CI comparison is apples-to-apples.
"""

import os
import sys
import xml.etree.ElementTree as ET

PEAK_BEGIN, PEAK_END = 54000, 64800   # 15:00-18:00


def peak_total_delay(path: str):
    """Return (n_peak_trips, mean_total_delay) over intended-depart peak trips."""
    root = ET.parse(path).getroot()
    tot, n = 0.0, 0
    for ti in root.iter("tripinfo"):
        depart = float(ti.get("depart"))
        dd = float(ti.get("departDelay"))
        intended = depart - dd
        if PEAK_BEGIN <= intended < PEAK_END:
            tot += float(ti.get("timeLoss")) + dd
            n += 1
    return n, (tot / n if n else float("nan"))


HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "..", "..", "..", "results")

# recorded per-seed v3 peak total delay to verify against
# (data/multiseed_per_seed_delay.txt)
RECORDED = {
    1.0: [786, 489, 185, 575, 430],
    1.3: [8910, 1403, 4420, 1855, 1673],
    1.8: [7149, 5899, 5842, 6899, 3042],
}
SEED_DIR = {0: "exp003b_v3/s0", 1: "exp003b_v3/s1", 2: "exp003b_v3/s2",
            3: "exp003b_v3/s3", 4: "exp003b_v3/s4"}


def verify():
    print("VERIFY canonical peak-delay vs recorded v3 numbers")
    print(f"{'scale':>5} {'seed':>4} {'recorded':>9} {'recomputed':>11} "
          f"{'n_peak':>7}  match?")
    ok = True
    for scale in (1.0, 1.3, 1.8):
        for seed in range(5):
            ti = os.path.join(RESULTS, SEED_DIR[seed],
                              f"ti_heldout_rl_x{scale}.xml")
            n, d = peak_total_delay(ti)
            rec = RECORDED[scale][seed]
            close = abs(d - rec) <= max(2.0, 0.01 * rec)  # <=1% or 2s
            ok = ok and close
            print(f"{scale:>5.1f} {seed:>4} {rec:>9} {d:>11.1f} {n:>7}  "
                  f"{'OK' if close else 'MISMATCH'}")
    print("ALL MATCH" if ok else "*** SOME MISMATCH -- metric definition differs ***")
    return ok


if __name__ == "__main__":
    if len(sys.argv) > 1:                 # measure an arbitrary tripinfo
        for p in sys.argv[1:]:
            n, d = peak_total_delay(p)
            print(f"{d:10.1f} s  (n_peak={n})  {p}")
    else:
        verify()
