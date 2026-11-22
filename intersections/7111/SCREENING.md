# 7111 — SR 9 Peachtree Rd @ Collier Rd: deep check (2026-11-22)

Data: ATSPM configuration (`config/`), turning-movement counts for 10 weekdays Nov 2-13 2026 (`counts/`), one T&A
window (2026-11-11 17:00, `tools/cache/tna_events/7111_20261111_1700_5m_p12345678/`).

- MaxTime controller. Phases: P1 NB left (permissive in P6), P2 SB through, P3 EB left (protected only, **two left
  lanes**), P4 Collier WB (left + through-right lanes; left permissive), P5 SB left (permissive in P2), P6 NB
  through, P8 Collier EB through-right. No P7.
- Lanes from detectors: Peachtree NB 2 through lanes + left; SB 3 through lanes + left; Collier EB 2 left lanes +
  through-right; WB left + through-right.
- **Counting**: every non-right movement has its own count-only Matrix zone in each lane (NB left; NB through x2;
  SB through x3; SB left; EB left x2; EB through-right; WB left; WB through-right). Separate presence zones for
  control. Exit-lane counts on all four legs (SB 3 lanes, NB 2, EB 1, WB 1). Advance radar counts on Peachtree NB/SB.
- **Not counted**: Peachtree NB and SB right turns (no right-lane detector). They can be bounded from the exit
  counts (flow balance below).
- **Data**: 10 of 10 weekdays complete (no outage). Entering ~39,400-45,600 vehicles/day (137: ~33,000-41,000).
  Peachtree through ~11,000-12,800 NB and ~14,200-18,100 SB per day; Collier EB left ~3,800-4,200 (dual lefts).
- **T&A behaviour** (presence zones used for control): one on/off per waiting vehicle, vehicles clear the left
  zone 2-8 s after their arrow starts, no on/off bursts during red in this window (unlike 137, 7130, 7696).
- **Flow balance check** (Nov 11): exits should equal the movements that feed them. North exit 17,342 vs NB through
  11,187 + EB left 4,205 = 15,392 (+ WB rights inside WB through-right 1,103) → up to 16,495, short by ≥ 850 (5 %);
  south exit 21,764 vs SB through 15,609 + WB left 893 = 16,502, leaving 5,262 for EB rights, but EB
  through-right is only 4,777 in total → the south exit counts ≥ 485 (2 %) more than can arrive. West exit 5,768
  vs NB left 3,269 + WB through + SB rights (not counted) → SB rights ≤ ~2,500. So counts agree within a few %,
  and the uncounted Peachtree rights can be estimated from the exits.
- **Neighbours**: 7110 at ~190 m and 7112 at ~210 m on the same corridor (Peachtree Rd, coordinated) → their
  platoons matter; both would need their timing (as 138 for 137).

Verdict: the best-counted candidate so far; simpler phase layout than 7027; busier than 137.
