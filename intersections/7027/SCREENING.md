# 7027 — SR 8 Ponce de Leon Ave @ SR 42 Moreland Ave / Briarcliff Rd: deep check (2026-11-22)

Data: configuration, counts for 10 weekdays Nov 2-13 2026, one T&A window (2026-11-11 17:00).

- MaxTime. Eight standard phases (all four lefts protected-permissive) plus three extra left-turn phases 11, 16, 17
  ("EBLT DS", "WBLT DS", "NBLT DS") with their own presence zones (ch2, ch20, ch30) — not explained by the config;
  probably MaxTime pseudo-phases for a second left-turn zone.
- Counting: count-only zones per lane for every left and through(-right) lane; exit counts on all legs (NB 1 lane);
  advance counts WB (radar) and EB (loops, 300 ft). Rights inside the through-right counts.
- Data: 10 of 10 weekdays complete; entering ~37,000-46,300 vehicles/day.
- **Flags**: (1) the NB-left presence zone ch29 shows no activations at all in the T&A window while the phase gets
  calls (from another input, probably the DS zone) and NB left counts ~3,700/day; (2) the north exit count drifts
  from ~2,100 to ~9,000 per day within two weeks while the movements feeding it stay flat → a counting problem
  on that exit zone.
- Neighbours: 7028 at ~175 m, 7458 at ~180 m.

Verdict: well counted on paper, but more complex control (pseudo-phases) and two data-quality flags.

## Check against neighbouring signals (2026-11-22, Nov 2-13 weekdays)

7028 (Briarcliff @ St Charles Pl) ~175 m north, Wavetronix with count-only and exit zones.
- 7027 north exit vs 7028 NB arrivals (NB left + through-right): ratio 0.24-0.34 until Nov 6, then rises to
  0.96-0.98 by Nov 12-13 → 7027's north exit zone was miscounting and seems to have been fixed around Nov 9-12.
- 7027 SB arrivals (left + through + through-right) vs 7028 south exit: 1.15-1.75 → 7027 counts 15-75 % more SB
  traffic than 7028 sends; one of the two is wrong (St Charles Pl turns cannot explain 40-75 %).
Verdict: **rejected** for now — counts not consistent with the neighbour.
