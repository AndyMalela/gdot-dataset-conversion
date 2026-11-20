"""Hand-checked cases for the simulated ATSPM metrics (atsc/sim/atspm_sim.py)."""
from atsc.sim import atspm_sim as A

G = [{"phase": 4, "start": 0.0, "end": 20.0, "how": "force"}, {"phase": 4, "start": 60.0, "end": 70.0, "how": "gap"},
     {"phase": 4, "start": 120.0, "end": 130.0, "how": "gap"}]
EV = {"stopbar": {"d1": [(0.0, 25.0), (40.0, 41.0), (61.0, 62.0)]}, "setback": {"a1": [5.0, 30.0, 100.0]},
      "ped": [(10.0, 4), (30.0, 4), (90.0, 4)], "phases": {4: {"yellow": 4.0, "red": 2.0}},
      "stopbar_by_phase": {4: ["d1"]}, "setback_by_phase": {4: ["a1"]}}


def test_split_failure():
    # cycle 1: green 0-20 fully occupied (GOR 1), red 24-29 occupied 24-25 only (ROR 0.2) -> no failure
    r = A.split_failures(G, EV, 4, 0, 200)
    assert r["cycles"] == 3 and r["split_failures"] == 0
    ev = dict(EV, stopbar={"d1": [(0.0, 30.0)]})                 # red 24-29 occupied -> failure in cycle 1
    assert A.split_failures(G, ev, 4, 0, 200)["split_failures"] == 1


def test_approach_delay_and_pcd():
    # arrivals shifted by 5 s: 10 (green), 35 (red -> waits to 60: 25 s), 105 (red -> 120: 15 s)
    r = A.approach_delay(G, EV, 4, 0, 200, offset_s=5.0)
    assert r["arrivals"] == 3 and abs(r["delay_per_veh_s"] - 40 / 3) < 1e-9
    p = A.pcd(G, EV, 4, 0, 200, offset_s=5.0)
    assert abs(p["aog_pct"] - 100 / 3) < 1e-9 and abs(p["gt_pct"] - 20.0) < 1e-9


def test_wait_time_and_peds():
    # served calls: green 0 has occupancy since 0 -> wait 0; green 60: zone off (41) before it, no served call;
    # with a vehicle waiting 50-61 the green at 60 serves it after 10 s
    w = A.wait_time(G, EV, 4, 0, 200)
    assert w["calls"] == 1 and w["avg_wait_s"] == 0.0
    ev = dict(EV, stopbar={"d1": [(50.0, 61.0)]})
    assert A.wait_time(G, ev, 4, 0, 200)["avg_wait_s"] == 10.0
    pd = A.ped_delay(G, EV, 4, 0, 200)
    assert pd["ped_presses"] == 3 and pd["cycles_with_requests"] == 2
