# 7130 — SR 237 (Piedmont Ave) @ Monroe Dr: sensor screening (2026-11-22)

Checked as a candidate site for a fully measured model (MODEL_LOG lesson from 137: every lane needs a count-only
detector). Data: GDOT ATSPM configuration (`config/`), TMC for 12 days (`counts/`), one T&A window
(2026-11-11 17:00, `tools/cache/tna_events/7130_20261111_1700_5m_p12345678/`).

- Controller MaxTime, 8 phases, NEMA standard: P1 NB left, P2 SB through, P3 EB left, P4 WB through, P5 SB left,
  P6 NB through, P7 WB left, P8 EB through. All four lefts protected-permissive.
- Lanes per approach (from detectors): left bay + 2 through lanes (lane 2 through-right).
- Detection:
  - Through lanes: stop-bar presence zones (control) + **lane-by-lane count zones on the EXIT lanes of all four legs**
    (2 lanes each, "with speed restriction": moving vehicles only). Piedmont NB/SB also have an advance count at 260 ft.
  - Left turns: one zone each, "Lane-by-lane Count; Stop Bar Presence" — the same zone type as 137's problem counts.
    The T&A chart shows the same behaviour: the EB-left zone held through a whole arrow, and a burst of short
    on/off activations during red (radar dropouts).
  - Right turns: no detector (shared through-right lane).
- TMC report gives only EB_L, WB_L, NB_L, SB_L and EXIT_EB/NB/SB/WB_T. No approach through or right counts.
- Volumes (Tue-Thu, 12 days): exits ~4,000-7,800 (EB), ~8,000-10,100 (NB), ~6,700-12,400 (SB), ~4,600-7,200 (WB)
  vehicles/day; left "counts" 900-2,800/day. Roughly 30,000-37,000 vehicles/day enter: much busier than 137.
- Completeness: 8 of 12 days complete; 4 partial (outages 4-22 % of the day).

Verdict: busier and better counted than 137 for through traffic (all four exits counted from moving vehicles), but
not complete: left-turn counts are presence-zone activations with the same radar problems as 137, right turns are
not detected, and each exit count mixes the through movement with turns from the other approaches. Turning
movements would have to be estimated (exit counts + Piedmont advance counts + left counts), with the right-turn
split not observable.
