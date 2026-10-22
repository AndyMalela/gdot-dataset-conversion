# Watching the 7065 simulation in sumo-gui

Run from the project root. One command per controller; the window opens and starts playing.

```bash
uv run python tools/watch.py rl         --day 2026-10-02 --from 16:00 --to 18:00   # RL (dual-ring LSTDQ)
uv run python tools/watch.py webster    --day 2026-10-02 --from 16:00 --to 18:00   # Webster + ped minimums
uv run python tools/watch.py real       --day 2026-10-02 --from 16:00 --to 18:00   # GDOT timing (actuated)
uv run python tools/watch.py real-fixed --day 2026-10-02 --from 16:00 --to 18:00   # GDOT timing, exact phase order
```

## Options

| Option | Meaning | Default |
|---|---|---|
| `--day` | which day's counted traffic | 2026-10-02 |
| `--from`, `--to` | time window (HH:MM) | 16:00 – 19:00 |
| `--rep` | random arrival draw (0–9 on test weekdays, 0–2 on Saturdays) | 0 |
| `--seed` | RL training seed (0–4) | best on validation (seed 2) |

The network starts **empty** at `--from`; give it ~15 min before judging queues (e.g. `--from 15:45` to watch 16:00).

## Which days work

- **Webster and RL:** any prepared day — training Jul 10 – Aug 31, validation Sep 1 – 16, test Sep 17 – Oct 2
  (weekdays), and Saturdays Jul 11 – Oct 3.
- **Real timing (`real`, `real-fixed`):** validation and test weekdays and Saturdays (each uses that day's own
  GDOT schedule): Sep 1–5, 8–12, 14, 16, 17–19, 21–26, 28, 29, Oct 2, Oct 3, and Saturdays Jul 11, 18,
  Aug 1, 8, 15, 22, 29.
- Interesting picks: **2026-10-02** (validated weekday), **2026-09-24** (busiest Piedmont day — real timing
  gridlocks in the twin; see EXP-009 audit), **2026-09-26** (Saturday, GDOT weekend plans).

## In the window

- Speed: the **Delay** box (ms per step) — lower is faster; 0 = as fast as possible.
- Pause/resume: the play/stop buttons. Zoom: mouse wheel. Click a vehicle or signal for details.
- RL runs through Python (TraCI), so it plays slower than the others; close the window to stop.

Files used: network `sumotwin/7065_ext.net.xml`, traffic `rlagent/experiments/EXP-009_significance/data/demand/`,
signals `.../data/signals/`, RL weights `.../data/train/s<seed>/`. Script: `tools/watch.py`.

## If the window fails to open

`X Error: ... BadValue` or `Connection closed by SUMO` = sumo-gui itself cannot open an OpenGL window (it
happens with plain `sumo-gui` too). Usual cause: the NVIDIA driver was updated and the machine was not rebooted
(`nvidia-smi` then reports "Driver/library version mismatch"). Reboot and retry.

# Editing the intersection geometry (netedit)

Every simulation uses **`sumotwin/7065_ext.net.xml`** — edit that file directly.

```bash
# 1. back up first
mkdir -p sumotwin/archive && cp sumotwin/7065_ext.net.xml sumotwin/archive/7065_ext_$(date +%F_%H%M).net.xml

# 2. edit
uv run netedit sumotwin/7065_ext.net.xml      # SUMO 1.27.1 from the project env (not the system's)

# 3. check nothing the experiments depend on changed (+ a 1 h test run)
uv run python tools/check_twin.py --run
```

### Straightening the Peachtree through paths (SW leg ↔ NE leg)

The throughs bend because the incoming and outgoing lanes don't line up across the junction
(the approach and exit edges are offset sideways). Options in netedit, simplest first:

1. **Move the edge geometry.** Press **M** (Move mode), click the approach or exit edge (`SW_in`, `NE_out`,
   `NE_in.79`, `SW_out`) near the junction and drag its end / shape point sideways until the through lanes
   line up with the lanes on the other side. Shift + click on an edge adds a shape point.
2. **Edit the edge shape numerically.** Press **I** (Inspect), click the edge, edit `shape` (x,y points);
   the last point is at the junction.
3. **Fix only the path inside the junction.** Press **I**, enable *Show connections* (toolbar), click the
   through connection, set its `shape` to a straight line. This changes the drawn/driven path but not the lanes.

After edits press **F5** (recompute the junction) and check the result, then **Ctrl+S** to save.

### Do not change (or results, phase maps, demand routes and the RL state all break)

- edge IDs, number of lanes, lane permissions (left / through / right lanes), connections that exist,
- the traffic light `J` and its 19 links, the slip lane `NE_in.15 → E1 → N_out.37`.

`check_twin.py` checks exactly these and prints `COMPATIBLE` or what changed. Edge lengths changing is
fine (it just tells you). **After any accepted edit, earlier results are not comparable** — rerun the
experiments (e.g. `cd rlagent/experiments/EXP-009_significance && uv run python matrix.py run --force`).
To undo: copy the backup back over `sumotwin/7065_ext.net.xml`.

## SUMO version

The project pins **SUMO 1.27.1** in its uv environment (`pyproject.toml`: eclipse-sumo, libsumo, sumolib,
traci, sumo-data). Always run SUMO tools through `uv run` (e.g. `uv run sumo-gui ...`, `uv run netedit ...`);
the system `sumo` may be a different version (the OS installed 1.28.0 on 2026-10-09, which crashed intermittently).

# 7065osm (OpenStreetMap network + one lane fix)

Real GDOT timing on Oct 2 traffic (the only controller/day built for it so far). Run from the project root:

```bash
cd intersections/7065osm/sim
uv run sumo-gui -c gui.sumocfg                                   # 07:45-09:00, AM peak, starts paused: press play
uv run sumo-gui -c sim.sumocfg --gui-settings-file view.xml --begin 57600 --end 64800   # 16:00-18:00, PM peak
uv run sumo-gui -n ../network/7065osm.net.xml                    # just the network (inspect lanes)
uv run netedit ../network/7065osm.net.xml                        # inspect/edit (edits are lost on rebuild:
                                                                 #   put lane fixes in network/osm_tag_fixes.json)
```

The window starts empty at `--begin`; start ~15 min earlier to see realistic queues.
Rebuild after changing `network/osm_tag_fixes.json` (reuses the downloaded map):
`uv run python tools/osm_build.py 7065osm --rebuild && uv run python tools/build_sim.py 7065osm`
(see `intersections/7065osm/network/report.md`).
