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

### 2026-11-27 — 7111 Peachtree Rd @ Collier Rd (user, Google Maps: Street View dated 2025; aerial)

User's notes and five screenshots (aerial of the north leg, plus the signal heads on each mast arm, clockwise from
the north leg). Screenshots not stored in the repo (Google imagery); described here.

- **Legs**: four physical legs. The east leg (GDOT "Collier Rd WB", P4) is the **Chick-fil-A drive-through and
  parking**. Street View from 2018 looks very different, but the driveway was already there.
- **Collier Rd (west leg, GDOT "EB")**: 3 lanes inbound, 1 lane outbound. Inbound = **2 left-only lanes** + **1
  through-right lane**. The two left lanes run the full **86 m** back from the stop line (user's measurement).
- **Peachtree**: 3 lanes southbound, 2 lanes northbound, and a centre lane between them.
  - The centre lane is a **two-way left-turn lane** (aerial: yellow solid outer line + yellow dashed inner line,
    left-turn arrows painted for both directions). Between the signals, drivers from both directions use it to
    turn left into driveways.
  - Near the intersection, the centre lane becomes a **left-turn bay** (solid white line, left arrow at the stop
    line).
- **Signal heads** (Street View 2025), mapped by mast arm. Heads hung over a leg face the traffic coming toward it.
  - Over the north leg (faces **Peachtree NB**): flashing-yellow-arrow left head + sign "LEFT TURN YIELD ON
    FLASHING YELLOW ARROW" + 2 ball heads.
  - Over the east leg (faces **Collier EB**): **2 left-arrow heads (red arrow, 3-section) and no flashing-yellow
    sign** → the dual left is **protected only** + 2 ball heads.
  - Over the south leg (faces **Peachtree SB**): flashing-yellow-arrow left head + sign + 3 ball heads; street sign
    "Collier Rd NW →".
  - Over the west leg (faces the **driveway**): flashing-yellow-arrow left head + sign + 2 ball heads; street
    sign "Peachtree".
- **Agreement with GDOT's configuration**: matches in every point. P1 NB left and P5 SB left are protected +
  permissive (permissive in P6 / P2) = flashing yellow arrow; P3 EB left is protected only on 2 lanes; P4
  driveway left is permissive. Lanes match the detector lanes: NB 2 through + left, SB 3 through + left, EB
  2 left + through-right, driveway left + through-right.
- **Pedestrians**: push buttons and zebra crosswalks on **all four legs**.
- **Speed limit**: no sign seen. GDOT's configuration gives 35 mph for Peachtree NB and SB; Collier and the
  driveway are blank.
- **Bus stop**: the aerial shows a bus-stop icon on the east side of the north leg, just past the intersection
  (Peachtree NB, far side).

Follow-up answers (user, 2026-11-27):
- [x] Peachtree left-turn bays: the two-way left-turn lane **runs the whole way** between the signals; there is no
      separate bay with a fixed length.
- [x] Peachtree right turns: **no right-turn lane**; rights are made from the outer through lane (shared
      through-right).
- [x] Collier EB: the two left lanes are full width for **86 m**, plus a **12 m taper** before that (98 m in total).
- [x] Driveway (Chick-fil-A) exit: **2 lanes** — left-only on the left, through-right on the right (as GDOT's
      configuration says).
- [x] No "No Turn on Red" signs (right turn on red allowed everywhere). No U-turn signs seen.
- [x] No bus signs seen at the stop marked by Google Maps (the icon is from Google's transit layer; not confirmed
      on the ground).

7111 manual checks are complete for the model. Not checked: driveways along the blocks to 7110 and 7112 (section C),
bike lanes, detector mounts.
