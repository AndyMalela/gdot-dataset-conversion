# Manual checks before building the 7111 corridor model (7112 – 7111 – 7110)

Things GDOT ATSPM does not publish and OpenStreetMap often gets wrong. Use the aerial (Google Maps satellite)
and Street View; write the answer next to each box and the date of the imagery you used.

## A. Lanes (most important — the network is built from these)

For **each of the three intersections** (7111 Collier Rd, 7110 Brighton Rd, 7112 Palisades Rd), every approach:
- [ ] Number of lanes at the stop line, and what each lane may do (arrows painted / signs): left only, through,
      through-right, right only, shared through-left.
- [ ] Turn bays: how long the left-turn bay and any right-turn bay are (count car lengths or measure on the aerial).
- [ ] Number of lanes on each exit leg (where they go after the intersection).

Specific questions from the ATSPM configuration of 7111:
- [ ] Peachtree NB: 2 through lanes + 1 left bay?
- [ ] Peachtree SB: 3 through lanes + 1 left bay?
- [ ] Peachtree NB and SB right turns: own right-turn lane, or from the outer through lane?
- [ ] Collier EB: really 2 left-turn lanes, plus 1 through-right lane?
- [ ] East leg (GDOT "Collier Rd WB"): OpenStreetMap shows only service roads there, so it is a driveway — what
      does it serve, and is it 1 left lane + 1 through-right lane leaving the property?
- [ ] 7112 Palisades: NB lane 1 is shared through-left (no left bay)?

## B. Turning rules

- [ ] Any "No Turn on Red" signs (which approaches)?
- [ ] Left-turn signal heads: flashing yellow arrow, or 5-section / green ball (protected-permissive)? Collier EB
      left: protected only (red arrow)?
- [ ] U-turns allowed on Peachtree at these signals?
- [ ] Any turn prohibited at certain hours (signs)?

## C. What happens between the signals (~190-210 m)

- [ ] Driveways and side entrances on Peachtree between 7112 and 7111, and between 7111 and 7110 — especially
      Piedmont Hospital entrances. Which are busy, and do any have their own signal?
- [ ] Any midblock crosswalk, bus stop or bus bay on Peachtree in these blocks?
- [ ] On-street parking or loading zones near the stop lines?

## D. Pedestrians and bikes

- [ ] Which legs have crosswalks (all four at each signal?).
- [ ] Bike lanes on Peachtree or Collier?

## E. Speeds

- [ ] Posted speed limit on Peachtree and on Collier (signs in Street View). ATSPM's approach-speed field may be
      blank.

## F. Where the detectors are (only partly visible)

- [ ] Where the Wavetronix Matrix radars are mounted (which pole, facing which approach) and the Advance radars.
      Zones themselves are not visible; if you can ask GDOT for one thing, ask for the Matrix zone configuration
      (zone positions and lengths) of 7111.

## G. Anything unusual

- [ ] Skewed or offset legs, a channelized (island) right turn, a second stop bar for lefts, a railway or
      driveway inside the intersection, construction in the Street View imagery date range.

---
For 8185 (Perimeter Center Pkwy @ Hammond Dr) the same list applies later, plus: confirm dual left lanes on all
four approaches and the right-turn lanes on NB, SB, WB, and look at the MARTA station access between 8185 and 8186.

---
## Answers so far

- 2026-11-22 (user, Google Maps): **7111 Collier Rd** and **7112 Palisades Rd** are physically four-leg; at each,
  one leg only leads to a building / complex (a driveway). **7110 Brighton Rd** is three-leg.
  - OpenStreetMap agrees for 7111 (east leg = service roads) and 7112 (Palisades Rd NE from the east; the west leg
    is a 3-lane service road).
  - Open question: GDOT's configuration at 7110 has both an EB and a WB Brighton approach, each with counts
    (EB ~990 vehicles/day: left ~360 + through-right ~630; WB ~2,400/day). If Brighton is a T, which side is the
    EB approach — a driveway, or does Brighton cross?
