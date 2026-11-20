"""Parameter registry: every setting the site model uses, with its value, source and status.

    uv run python -m atsc.registry atsc/sites/137      -> atsc/sites/137/params.json + REGISTRY.md

Status:  measured  read directly from GDOT ATSPM data (or the configuration table)
         fitted    chosen by a rule on training days to match an ATSPM statistic
         estimated computed from ATSPM data with a model (e.g. presence-zone undercount)
         assumed   a value we chose; not in the data
         default   SUMO / engine default, never checked
The model builder should read only this registry (PIPELINE_PLAN.md section 2); for now it is generated from the
site files (signal.json, sim.json, detectors.json, movements.json) so nothing drifts, and REGISTRY.md lists every
row that is not `measured` — that list is the deviations appendix.
"""
import json
import sys
from pathlib import Path

SUMO_DRIVER = ["tau", "sigma", "accel", "decel", "minGap", "speedFactor", "jmTimegapMinor", "lcStrategic"]


def build(site):
    site = Path(site)
    sig = json.loads((site / "signal.json").read_text())
    sim = json.loads((site / "sim.json").read_text())
    det = json.loads((site / "detectors.json").read_text())
    notes = sig.get("notes", {})
    rows = []

    def add(group, name, value, status, source):
        value = round(value, 2) if isinstance(value, float) else value
        rows.append({"group": group, "name": name, "value": value, "status": status, "source": source})

    # ---- controller: phases
    clr_assumed = notes.get("clearance_assumed", {})
    for p, v in sorted(sig["phases"].items(), key=lambda kv: int(kv[0])):
        tag = f"P{p}"
        st = "assumed" if p in clr_assumed else "measured"
        src = clr_assumed.get(p, "Timing & Actuation interval lengths (clearance.json)")
        add("controller", f"{tag} yellow (s)", v["yellow"], st, src)
        add("controller", f"{tag} red clearance (s)", v["red"], st, src)
        add("controller", f"{tag} min green (s)", v["min_green"], "measured" if v.get("min_green_n") else "assumed",
            f"shortest gap-out green, n={v.get('min_green_n')}" if v.get("min_green_n") else "not measured")
        add("controller", f"{tag} ped minimum (s)", v["ped_min"], "measured" if v["ped_min"] else "assumed",
            notes.get("ped_min", "") if v["ped_min"] else "no pedestrian service modelled for this phase")
        add("controller", f"{tag} recall", v["recall"], "measured", notes.get("recall", ""))
        add("controller", f"{tag} max green, free mode (s)", v["max_green_free"], "estimated", notes.get("max_green_free", ""))
    ctl = sim.get("controller", {})
    for p, v in sorted(ctl.get("passage_s", {}).items(), key=lambda kv: int(kv[0])):
        add("controller", f"P{p} passage time (s)", v, "fitted", ctl.get("source", ""))
    add("controller", "passage time, other phases (s)", sim.get("passage_s"), "default", "engine default")
    # direct measurements (atsc/measure.py), shown next to the model value until the model adopts them
    mj = site / "measured.json"
    if mj.exists():
        meas = json.loads(mj.read_text())["phases"]
        for p, m in sorted(meas.items(), key=lambda kv: int(kv[0])):
            if m.get("passage_median_s") is not None:
                add("measured, not yet in model", f"P{p} passage time (s)", m["passage_median_s"], "measured",
                    f"atsc/measure.py: last zone-off -> end of green, median of n={m['passage_n']} (mode "
                    f"{m['passage_mode_s']} s); model uses {ctl.get('passage_s', {}).get(str(p), sim.get('passage_s'))}")
            if p in clr_assumed and m.get("yellow_s") is not None:
                add("measured, not yet in model", f"P{p} yellow / red clearance (s)",
                    f"{m['yellow_s']:.1f} / {m['red_clear_s']:.1f}", "measured",
                    f"atsc/measure.py: display run lengths, n={m['yellow_n']}/{m['red_n']}; model uses an assumed value")
    add("controller", "max recall", ctl.get("max_recall", {}), "fitted", ctl.get("source", ""))
    add("controller", "ring order / lead-lag", sig["rings"], "measured", notes.get("rings", ""))
    add("controller", "plans (cycle, splits, coordinated phases)", sorted(sig["plans"]), "measured", notes.get("plans", ""))
    add("controller", "time-of-day schedule", f"{len(sig.get('schedule_by_date', {}))} dated days", "measured",
        str(notes.get("schedule", ""))[:200])
    flo = {k: p.get("floating_force_off") for k, p in sig["plans"].items() if p.get("floating_force_off")}
    add("controller", "floating force-off phases", flo, "measured", "Split Monitor rule (force_off_mode.py)")
    add("controller", "plan transition", "new plan starts its cycle at the change", "assumed",
        "real controllers transition over several cycles (signal.py _plan_at)")
    add("controller", "detector call delay / extend", 0, "measured",
        "VALIDATION.md finding 2026-11-16 09:30: call registers when the zone turns on and drops when it turns off")
    add("controller", "pedestrian push rates (per hour)", "ped_calls_per_h", "estimated",
        notes.get("ped_min", "") + " — 48 windows on 3 days; to be replaced by Pedestrian Delay counts per window")

    # ---- detectors
    zone = det.get("stopbar_zone_m", {})
    add("detectors", "stop-bar zone length (m)", zone.get("value"), "assumed", zone.get("assumption", ""))
    sb = det.get("setback_m", {})
    if sb:
        add("detectors", "advance detector distance (m)", sb.get("value"), "measured", sb.get("source", ""))
    for d in det["detectors"]:
        if "DEVIATION" in d.get("note", "") or d.get("hardware") == "modelled only":
            add("detectors", f"ch{d['ch']} P{d['phase']} {d['kind']}", "modelled", "assumed", d.get("note", ""))
    add("detectors", "lane layout", det.get("source", "")[:120], "measured", "GDOT configuration table + user check")

    # ---- drivers / discharge
    vt = sim.get("vtype", {})
    for k, v in vt.items():
        add("drivers", k, v, "fitted", sim.get("vtype_source", ""))
    for k in SUMO_DRIVER:
        if k not in vt:
            add("drivers", k, "SUMO default", "default", "never checked against the field")
    add("drivers", "saturation flow (veh/h/ln)", sim.get("sat_flow_veh_h_lane"), "estimated",
        sim.get("sat_flow_source", "") + " — measured on the simulation, not the field")
    add("drivers", "vehicle mix", "passenger cars only", "assumed", "ATSPM has no classification")

    # ---- demand
    add("demand", "turning-movement counts", "tmc 5-min", "measured", "GDOT Turning Movement Counts report")
    add("demand", "presence-zone undercount factors", "intersections/<id>/counts/presence_factors_1900.json",
        "estimated", "time occupied / 1.895 s (HCM headway) on 72 Timing & Actuation windows")
    add("demand", "right turns on the main street", "run as through", "assumed", "no right-turn zone on W Paces Ferry")
    add("demand", "arrivals within a 5-min bin", "random (Poisson)", "assumed", "except platoons from modelled neighbours")
    add("demand", "driveways between signals", "not modelled", "assumed", "not counted by ATSPM")
    add("network", "road geometry", "OpenStreetMap", "assumed", "lanes checked by the user; bay lengths unverified")
    return rows


def write(site, rows):
    site = Path(site)
    (site / "params.json").write_text(json.dumps(rows, indent=1, default=str))
    cnt = {}
    for r in rows:
        cnt[r["status"]] = cnt.get(r["status"], 0) + 1
    md = [f"# Parameter registry — {site.name}", "",
          "Generated by `uv run python -m atsc.registry " + str(site) + "` from the site files. Do not edit by hand.", "",
          "Counts: " + ", ".join(f"{k} {v}" for k, v in sorted(cnt.items())), "",
          "## Every value that is not measured (deviations to disclose)", "",
          "| group | parameter | value | status | source / reason |", "|---|---|---|---|---|"]
    for r in rows:
        if r["status"] != "measured":
            md.append(f"| {r['group']} | {r['name']} | {str(r['value'])[:60]} | {r['status']} | {str(r['source'])[:160]} |")
    md += ["", "## Measured", "", "| group | parameter | value | source |", "|---|---|---|---|"]
    for r in rows:
        if r["status"] == "measured":
            md.append(f"| {r['group']} | {r['name']} | {str(r['value'])[:60]} | {str(r['source'])[:120]} |")
    (site / "REGISTRY.md").write_text("\n".join(md) + "\n")
    print(f"{len(rows)} parameters: " + ", ".join(f"{k} {v}" for k, v in sorted(cnt.items())))


if __name__ == "__main__":
    s = sys.argv[1]
    write(s, build(s))
