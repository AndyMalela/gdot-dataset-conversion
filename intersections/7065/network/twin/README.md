# Hand-built network for signal 7065

`sumotwin/7065_ext.net.xml` (referenced, not copied), signal `J`. Used by `tools/build_sim.py` instead of the OSM network in `../`.

| Approach | Edge | Heading | Lanes | Lane use (right→left) |
|---|---|---|---|---|
| NB | S_in | 341° | 4 | R T T L |
| EB | SW_in | 60° | 5 | TR T T L L |
| SB | N_near | 161° | 4 | R T T L |
| WB | NE_in.79 | 241° | 5 | T T T L L |

| ATSPM column | From edge | To edge |
|---|---|---|
| EB_L | SW_in | N_out |
| EB_T | SW_in | NE_out |
| WB_L | NE_in.79 | S_out |
| WB_T | NE_in.79 | SW_out |
| NB_L | S_in | SW_out |
| NB_T | S_in | N_out |
| SB_L | N_near | NE_out |
| SB_T | N_near | S_out |
