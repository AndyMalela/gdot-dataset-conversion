
## Ground-truth lane configuration (inbound → J / outbound ← J)
| Leg | Road | Inbound | Outbound |
|---|---|---|---|
| N  | Piedmont Rd NE | **4** | 2 |
| S  | Piedmont Rd NE | **4** | 2 |
| NE | Peachtree Rd NE | **5** | 3 |
| SW | Peachtree Rd NE | **5** | 3 |

S/SW/NE lane-use is netconvert's default (1 right + n straight + 1 left) except
NE (2 left, 3 straight, no right — see `digitize.py`) and SW (2 left, 2
straight, 1 shared straight/right). (Lane counts from Google Maps + the
correctly-tagged OSM south & Peachtree legs.)

## N-leg (top): late left-turn pocket
Rather than a left-turn lane running the full 100 m, the N approach is split
into 2 segments: `N_far` (`nN`→`nNleft`, 100→40 m, 3 lanes) and `N_near`
(`nNleft`→`J`, 40→0 m, 4 lanes) — the dedicated left-turn lane only exists on
`N_near` (last **40 m**, see `N_LEFT_DIST` in `digitize.py`); for the first
60 m there are just 3 lanes.

## Open it
```bash
sumo-gui -c 7065twin/7065.sumocfg      # View → "real world" scheme
sumo     -c 7065twin/7065.sumocfg      # headless (loads clean, no demand yet)
netedit  7065twin/7065.net.xml         # inspect/adjust lanes, connections, TLS
```

## Files
| File | What it is |
|---|---|
| `7065.net.xml` | **Final network** — 1 signal, 100 m legs, real lane counts |
| `7065.sumocfg` / `7065.view.xml` | Runnable config + sumo-gui view |
| `digitize.py` | Turns the aerial picks into `plain/7065.nod.xml` + `.edg.xml` |
| `plain/` | Digitized node/edge source fed to netconvert |
| `preview.png` | SUMO-style render of the final twin |
| `redigitized_overlay.png` | **Final net overlaid on the satellite** (fidelity check) |
| `satellite_ref.png` | Georeferenced aerial the geometry was picked from |
| `fidelity_osm_vs_sat.png`, `northleg_check.png` | Evidence of the OSM data gap |
| `osm_raw.osm.xml` | The rejected OSM download (kept for reference) |

## To adjust geometry
Edit the pixel picks / lane counts at the top of `digitize.py` (`J_PX`, `LEG_PX`,
`LANES`) and re-run `build.sh`; re-check against `redigitized_overlay.png`. For
finer curvature, open `7065.net.xml` in NETEDIT.

