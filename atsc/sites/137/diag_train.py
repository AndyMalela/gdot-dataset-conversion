"""v3 diagnosis on TRAIN days only (no validation statistic is looked at): simulate train weekdays with the current
model and compare per phase x plan with GDOT's Split Monitor (gap / force / skip shares, average split, and the
gap-out share among served cycles).

    uv run python atsc/sites/137/diag_train.py run [tag]     -> calibration_diag/train_<tag>.csv
    uv run python atsc/sites/137/diag_train.py show [tag]
"""
import csv
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import validate as V  # noqa: E402

OUT = HERE / "calibration_diag"


def run(tag):
    sim, _, health = V.run("train", [None])
    OUT.mkdir(exist_ok=True)
    with open(OUT / f"train_{tag}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(sim[0]))
        w.writeheader()
        w.writerows(sim)
    print("teleports:", sum(h["teleports"] for h in health))


def show(tag):
    sim = list(csv.DictReader(open(OUT / f"train_{tag}.csv")))
    days = {s["date"] for s in sim}
    fi = {(r["date"], r["band_start"], int(r["phase"])): r for r in V.field_rows() if r["date"] in days}
    d = defaultdict(lambda: defaultdict(list))
    for s in sim:
        f = fi.get((s["date"], s["band_start"], int(s["phase"])))
        if f is None or s["plan"] not in V.WEEKDAY_PLANS or int(s["phase"]) not in V.SCORED:
            continue
        k = (int(s["phase"]), s["plan"])
        for src, r in (("s", s), ("f", f)):
            for q in ("gap_pct", "force_pct", "skip_pct"):
                d[k][src + q].append(float(r[q]))
            if r["avg_split_s"] not in ("", None) and float(f["skip_pct"]) < 99.5:
                d[k][src + "split"].append(float(r["avg_split_s"]))
            srv = 100 - float(r["skip_pct"])
            if srv > 5:
                d[k][src + "gap_served"].append(100 * float(r["gap_pct"]) / srv)
    m = lambda v: st.median(v) if v else float("nan")
    print("ph plan n | split f/s | gap f/s | force f/s | skip f/s | gap-of-served f/s")
    for k in sorted(d):
        v = d[k]
        if len(v["sgap_pct"]) < 5:
            continue
        print(f"P{k[0]} {k[1]} {len(v['sgap_pct']):3d} | {m(v['fsplit']):5.1f} {m(v['ssplit']):5.1f} | "
              f"{m(v['fgap_pct']):4.0f} {m(v['sgap_pct']):4.0f} | {m(v['fforce_pct']):4.0f} {m(v['sforce_pct']):4.0f} | "
              f"{m(v['fskip_pct']):4.0f} {m(v['sskip_pct']):4.0f} | {m(v['fgap_served']):4.0f} {m(v['sgap_served']):4.0f}")


if __name__ == "__main__":
    tag = sys.argv[2] if len(sys.argv) > 2 else "a10"
    {"run": run, "show": show}[sys.argv[1]](tag)
