"""Final evaluation (TEST_PLAN.md, step 2): the field time-of-day schedule of SIG 137 on the test days, added to the
frozen attempt-7 signal.json (and 138's, which follows 137's schedule) without changing anything else.

    uv run python atsc/sites/137/test_schedule.py fetch     # Split Monitor charts of the test days (GDOT ATSPM)
    uv run python atsc/sites/137/test_schedule.py apply     # -> signal.json / neighbour138/signal.json schedule_by_date

Why: the field program changed inside the validation period (plans E, F, G from late April, A-D on other days);
dated and canonical schedules agree on only 62.9 % of validation-day minutes, so the canonical schedule is not a
fair stand-in for the GDOT plan controller or for 138 on the test days.

Rules (registered in TEST_PLAN.md before any test day was read):
  - charts read with tools/atspm_plans.py exactly as for every other day (--no-clearance); its re-clustered output
    is saved as intersections/137/timing/timing_plan_137_test_read.json and the original timing files are restored,
    so the validated sources stay byte-identical
  - each band's plan is matched to a frozen plan by identical cycle and splits; a verified plan (ring checks ok,
    P2/P6 > 0) with no match is added under a new name (T1, T2, ...) for plan mode only: phase settings (min/max
    greens, passage, floating force-offs) are not changed
  - bands as make_signal.py: free -> FREE; 'no data' or unverified bands shorter than 20 min skipped (previous plan
    continues); any other unreadable band -> the day takes the nearest test day's schedule
  - only performance-free information is read (plan bands and programmed splits); split statistics are not read
"""
import datetime as dt
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
T = REPO / "intersections/137/timing"
FILES = ["timing_plan_137.json", "timing_plan_137.md", "plans_137.csv"]
DATES = ["2026-05-18", "2026-05-19", "2026-05-20", "2026-05-22", "2026-05-26", "2026-05-28", "2026-05-29"]
BACKUP = HERE / "debug" / "timing_backup_before_test_read"


def fetch():
    BACKUP.mkdir(parents=True, exist_ok=True)
    for f in FILES:
        shutil.copy2(T / f, BACKUP / f)
    try:
        subprocess.run([sys.executable, str(REPO / "tools/atspm_plans.py"), "137", "--no-clearance", "--date", *DATES],
                       check=True, cwd=REPO)
        shutil.copy2(T / "timing_plan_137.json", T / "timing_plan_137_test_read.json")
    finally:
        for f in FILES:                                         # validated sources back exactly as they were
            shutil.copy2(BACKUP / f, T / f)
    print(f"saved {T / 'timing_plan_137_test_read.json'}; original timing files restored")


def apply():
    tp = json.loads((T / "timing_plan_137_test_read.json").read_text())
    sig = json.loads((HERE / "signal.json").read_text())
    key = lambda cyc, sp: (round(float(cyc)), tuple(round(float(sp.get(str(q), sp.get(q, 0)))) for q in range(1, 9)))  # noqa: E731
    frozen = {key(p["cycle"], p["splits"]): k for k, p in sig["plans"].items()}
    verified = {k: p for k, p in tp["plans"].items() if p.get("checks") == ["ok"] and p.get("cycle_s")
                and all(p["splits_s"].get(str(q), 0) > 0 for q in (2, 6))}
    name, added = {}, {}
    template = next(iter(sig["plans"].values()))
    for k, p in verified.items():
        kk = key(p["cycle_s"], p["splits_s"])
        if kk in frozen:
            name[k] = frozen[kk]
        elif any(s.split(" ")[0] in DATES for s in p.get("seen", [])):
            n = f"T{len(added) + 1}"
            frozen[kk] = name[k] = n
            added[n] = {"cycle": p["cycle_s"], "splits": {str(q): s for q, s in p["splits_s"].items()},
                        "coordinated": [2, 6], "termination": p.get("termination", {}),
                        "offset_s": template.get("offset_s", 0.0),
                        "floating_force_off": template.get("floating_force_off", [])}
    sched, bad, skipped = {}, [], []
    for d in DATES:
        bands = tp["schedule"].get(d)
        if not bands:
            bad.append(d)
            continue
        out = []
        for b in bands:
            if b["kind"] == "plan" and b["plan"] in name:
                out.append([b["start"], name[b["plan"]]])
            elif b["kind"] == "free":
                out.append([b["start"], "FREE"])
            elif b["kind"] == "no data" or (b["kind"] == "plan" and b.get("minutes", 0) < 20):
                skipped.append((d, b["start"], b["plan"], b.get("minutes")))
            else:
                out = None
                bad.append(d)
                break
        if out:
            sched[d] = out
    nearest = {}
    for d in bad:
        n = min(sched, key=lambda x: abs((dt.date.fromisoformat(x) - dt.date.fromisoformat(d)).days))
        sched[d] = sched[n]
        nearest[d] = n
    assert not set(sched) & {d for d, v in sig["schedule_by_date"].items() if v and d not in DATES}
    sig["plans"].update(added)
    sig["schedule_by_date"].update(sched)
    sig["notes"]["test_schedule"] = (f"test days ({', '.join(DATES)}) from the Split Monitor, test_schedule.py "
                                     f"(TEST_PLAN.md): plans matched by cycle + splits; added for plan mode only: "
                                     f"{ {k: (v['cycle'], v['splits']) for k, v in added.items()} }; nearest-day "
                                     f"fallback {nearest}; skipped short/no-data bands {skipped}")
    (HERE / "signal.json").write_text(json.dumps(sig, indent=1))
    # 138 follows 137's schedule with its own verified plan of the same cycle (neighbour138/make_signal.py)
    n8 = HERE / "neighbour138" / "signal.json"
    s8 = json.loads(n8.read_text())
    mapping = {}                                   # the frozen mapping, as make_signal wrote it for the other days
    for d, v in s8["schedule_by_date"].items():
        if v and d not in DATES and sig["schedule_by_date"].get(d):
            for (_, a), (_, b) in zip(sig["schedule_by_date"][d], v):
                if a != "FREE":
                    assert mapping.setdefault(a, b) == b, (d, a, b)
    by_cycle = {}
    for k, p in s8["plans"].items():               # new plans: 138's plan with the same cycle (most seen first)
        by_cycle.setdefault(round(p["cycle"]), k)
    for k, p in sig["plans"].items():
        mapping.setdefault(k, by_cycle.get(round(p["cycle"]), "FREE"))
    for d in DATES:
        s8["schedule_by_date"][d] = [[t, "FREE" if n == "FREE" else mapping[n]] for t, n in sig["schedule_by_date"][d]]
    s8["notes"]["test_schedule"] = f"test days: 137's test-day schedule with 138's plan of the same cycle {mapping}"
    n8.write_text(json.dumps(s8, indent=1))
    print(f"plans matched {name}; added {list(added)}; nearest-day fallback {nearest}; skipped {skipped}")
    for d in DATES:
        print(d, sig["schedule_by_date"][d], "| 138:", s8["schedule_by_date"][d])


if __name__ == "__main__":
    {"fetch": fetch, "apply": apply}[sys.argv[1]]()
