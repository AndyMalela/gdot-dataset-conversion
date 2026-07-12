# SIG#7065 — authoritative lane configuration (per leg, per movement)

Ground-truth lane counts for each physical leg, confirmed by the user
(2026-07-12) and cross-checked against the SUMO twin (`7065.net.xml`), the
demand routing (`../sumodemand/build_demand.py`), and the node coordinates
below. This is the canonical reference — earlier scattered mentions
(`README.md`, `../rlagent/fixed_time.py`) should defer to this file.

## Physical legs (from node coordinates; SUMO +x = East, +y = North, J = 150,150)

| Node | x | y | Position rel. to J | Road | Leg | Inbound travel dir |
|------|-----|-----|-----|------|-----|-----|
| nNE | 237.0 | 208.7 | **NorthEast** | Peachtree Rd NE | NE | heads SW → **Westbound (WB)** |
| nSW |  88.8 | 116.1 | **SouthWest** | Peachtree Rd NE | SW | heads NE → **Eastbound (EB)** |
| nN  | 118.2 | 244.8 | **North**     | Piedmont Rd NE  | N  | heads S → **Southbound (SB)** |
| nS  | 172.3 |  83.6 | **South**     | Piedmont Rd NE  | S  | heads N → **Northbound (NB)** |

Direction↔leg mapping (confirmed with user 2026-07-12, matches code &
`build_demand.py`): **EB = SW leg, WB = NE leg, NB = S leg, SB = N leg.**

## Lanes per leg, split by movement

Right turns carry **zero demand** (GDOT never measures them) — listed for
geometric completeness only. "Through" counts are what matter for capacity.

| Leg (compass) | Inbound edge | Left | Through | Right | Total | Notes |
|---|---|---:|---:|---:|---:|---|
| **NE** = **WB** (Peachtree) | `NE_in`  | 2 | 3 | — (slip) | 5 | right handled by the free-flow **slip lane** `E1` (bypasses signal) |
| **SW** = **EB** (Peachtree) | `SW_in`  | 2 | 2 + 1 shared | (shared) | 5 | rightmost lane is shared through+right; right-demand 0 → carries through. **Heaviest through movement (~2,105 veh/h) enters here.** |
| **S** = **NB** (Piedmont)  | `S_in`   | 1 | 2 | 1 | 4 | dedicated right (doghouse protected-overlap head) |
| **N** = **SB** (Piedmont)  | `N_near` | 1 | 2 | 1 | 4 | dedicated right (doghouse protected-overlap head); late left pocket (see README) |

Through-lane capacity (@ 1800 veh/h/lane saturation flow): **NE 3, SW 3
(2 dedicated + 1 shared, all carrying through since right=0), S 2, N 2.**

## Demand routing (movement → edges) as built in `build_demand.py`

| GDOT data movement | route edges | through lanes used |
|---|---|---|
| EB thru | `SW_in → NE_out` | SW lanes 0–2 (3) |
| EB left | `SW_in → N_out`  | SW lanes 3–4 (2) |
| WB thru | `NE_in → … → SW_out` | NE lanes (3) |
| WB left | `NE_in → … → S_out`  | NE lanes (2) |
| NB thru | `S_in → N_out` | S (2) |  NB left `S_in → SW_out` (1) |
| SB thru | `N_near → S_out` | N (2) | SB left `N_near → NE_out` (1) |

## ✓ Resolved: EB/WB direction-label convention (2026-07-12)

Confirmed with the user: **the NE (top-right) leg's traffic heads West**, so
the NE leg is the **Westbound** approach and the SW leg is the **Eastbound**
approach. This matches the geometry (SW→NE traversal = travelling east) and
`build_demand.py`'s existing `eb → SW_in` / `wb → NE_in` mapping — so the
demand routing is correct and the heavy Eastbound-through flow correctly loads
the SW leg's 3 through-capable lanes. No code change needed.
