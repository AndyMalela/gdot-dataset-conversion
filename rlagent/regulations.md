# Regulations & standards tracker — signal phasing/timing for SIG#7065 (Atlanta, GA)

Tracks the legal/regulatory basis for how the RL agent's **action space**
(stage table, interstage timing) should be designed, so it reflects how a
real Georgia signal is actually allowed to operate rather than an arbitrary
scheme. Feeds `rlagent/plan.md` Phase 0. Add to this file as more
GDOT/MUTCD specifics are found — don't let design decisions in the plan
silently assume something that isn't sourced here.

---

## 1. Governing hierarchy

1. **National MUTCD (11th Edition)** — Georgia adopted the national MUTCD
   **directly, with no separate state supplement** (unlike ~13 states that
   layered a supplement, or California/Texas which maintain their own full
   state MUTCD). So national MUTCD sections apply to SIG#7065 as-is.
   [MUTCD by State](https://roadsigns.com/blogs/resources/mutcd-by-state),
   [GDOT MUTCD presentation](https://www.dot.ga.gov/AboutGeorgia/Board/Presentations/MUTCD.pdf)
2. **Georgia Code Title 40, Chapter 6, Article 2 (§§ 40-6-20–28)** — state
   statute defining what each signal indication legally *means* (this is
   law, not just guidance).
   [§ 40-6-21](https://law.justia.com/codes/georgia/title-40/chapter-6/article-2/section-40-6-21/)
3. **GDOT Office of Traffic Operations policies** (the "6785-" series) —
   GDOT's own operational policy layer on top of MUTCD, e.g. left-turn
   phasing warrants. These are what a GDOT engineer would actually apply
   when designing/approving a phasing scheme for a real intersection.
4. **GDOT Traffic Signal Design Guidelines** (currently v7.0, April 2025) —
   physical/electrical/geometric design guidance (pole placement, detector
   hardware, phase-numbering *convention* for plans). **Not** a timing/
   operations manual — GDOT's own "Traffic Signal Operations Guide" (which
   would hold the timing specifics) is, per the Design Guidelines
   themselves, still "under process of preparation and publication" as of
   this version — not yet public. Timing values below therefore come from
   MUTCD/ITE, which is what GDOT's own documents say to fall back on.
   [PDF](https://www.dot.ga.gov/PartnerSmart/DesignManuals/SignalDesignManual/Traffic%20Signal%20Design%20Guidelines.pdf)
   *(blocked by GDOT's WAF for direct/automated fetches — retrieved via
   `r.jina.ai` reader proxy)*

---

## 2. Georgia statutory signal meanings (§ 40-6-21)

Legally binding, not just convention:

- **Circular green**: proceed straight/right/left (unless signed otherwise),
  turning traffic yields to oncoming/pedestrians.
- **Green arrow**: protected movement in that direction only; other traffic
  at the intersection must yield to it.
- **Circular yellow / yellow arrow**: warning the related green is ending;
  do not enter after red shows.
- **Flashing yellow arrow (FYA)**: may proceed in the arrow's direction
  **but must yield to oncoming traffic and pedestrians** — i.e. this is
  the statutory basis for *permissive* left turns.
- **Circular red**: stop; **right turn on red permitted by default** after
  stopping, yielding to pedestrians/cross traffic, *unless a sign
  specifically prohibits it*. Left turn on red is only legal from a
  one-way onto a one-way (not applicable at SIG#7065 — both Peachtree and
  Piedmont are two-way).
- **Red arrow**: that specific movement is fully prohibited, no
  right-on-red-style exception.
- **Flashing red arrow**: right turn permitted after stop (same idea as
  circular red's right-on-red, but for a channelized/overlap right-turn
  head).

**Relevant to us:** right turn on red is the Georgia *state* legal default.
**Correction (verified 2026-07-11 via web search, superseding the anecdotal
note formerly here):** the actual Atlanta City Council RTOR ban — passed
Feb 2024, signage deadline 2025-12-31 — covers only **Downtown, Midtown,
and Castleberry Hill**. Buckhead is explicitly *not* included. SIG#7065
(Peachtree @ Piedmont) is in Buckhead, so this ordinance does not apply to
it. [Atlanta City Council notice](https://citycouncil.atlantaga.gov/Home/Components/News/News/3749/),
[AJC summary](https://www.ajc.com/news/atlanta-news/what-you-need-to-know-about-atlantas-right-on-red-ban/6WQP7QE3QFDNZKYP2KSWYKOLII/)

User notes: **as of now there are no "NO TURN ON RED" signs posted at this
intersection (checked via Google Maps)**, consistent with the correction
above — so the standard US RTOR rule applies here — rights may turn on red
after stopping and yielding. GDOT's sensor data carries no right-turn
counts anyway.

**Open question, not yet resolved per-leg (added 2026-07-11):** the note
above was a blanket, intersection-wide check, and it's since come into
doubt specifically for the **EB approach (SW leg)** — the one with the
*shared* thru/right lane rather than an exclusive lane (§8). Shared-lane
right-turners who stop for a gap block the thru lane behind them, which is
a common real-world reason an agency restricts RTOR specifically on a
shared lane even when it's allowed elsewhere at the same intersection. A
web search for anything specific to this intersection's signage came back
empty (only general Buckhead/SR 237 context, no sign-level detail) — this
is a fact that only a direct look at that specific approach (Street View or
in person) can settle, not something inferable from policy or geometry.
Until confirmed, don't assume EB definitely has RTOR just because the
intersection-wide check found no signs elsewhere.

**Practical effect on the model: none either way.** Because the sensor data
has no right-turn movement, the three real right turns + the WB slip carry
zero demand in the twin — there are no right-turning vehicles for an
RTOR-vs-green-only distinction to act on. `stages.py` releases rights as 'g'
within compatible green stages and does not additionally model RTOR-on-red,
which is harmless here since the demand is zero regardless. If right-turn
counts are ever obtained, revisit this (add RTOR permissive-on-red link
states) rather than leaving rights green-only. Separately, 3 of the 4 legs
have posted "ONLY RIGHT TURN" lane markings (one leg is a shared
through/right lane) — consistent with the twin's lane channelization.

---

## 3. NEMA ring-and-barrier phase numbering — generic vs. GDOT's convention

**Generic NEMA** (used nationally as the textbook baseline): major-street
through movements = phases 2/6, major-street lefts = 1/5; minor-street
throughs = 4/8, minor-street lefts = 3/7. Ring 1 = phases 1–4, Ring 2 =
phases 5–8; a **barrier** separates the major-street group (1,2,5,6) from
the minor-street group (3,4,7,8) — both rings must clear to red together at
the barrier.
[Ring-and-barrier background](https://www.researchgate.net/figure/Typical-example-of-a-signal-phase-sequence-NEMA-ring-and-barrier-diagram-in-the-United_fig2_345034437)

**GDOT's specific convention** (Design Guidelines §2.7, Figure 2-4/2-6):

- **Phase 2 is assigned to the main street's westbound or southbound
  direction.** Remaining phases are numbered **counterclockwise** around
  the intersection from there — this is a specific starting-point/direction
  choice, not just "pick any major-street through as 2."
- **Odd phases (1,3,5,7) = left turns** under standard concurrent phasing
  (matches generic NEMA).
- **Phases 3 & 4 are preferred for split-phasing** a minor street
  specifically because they're inherently mutually exclusive in the
  standard ring structure ("cannot cause a conflict for the intersection").
  Lower-volume side gets phase 3, higher-volume side gets phase 4.
- **GDOT does not install left-turn phases symmetrically.** If NB warrants
  a left-turn phase and SB doesn't, SB does *not* get one by default — it
  gets a 3-section permissive-only FYA head instead, specifically to avoid
  creating a "left-turn trap" (a driver assumes the opposing approach is
  also protected/stopped when it isn't).
- **Right-turn overlaps** (a protected right coincident with a
  non-conflicting phase, e.g. paired with the adjacent left) are legal and
  common; labeled OL1, OL2, ... in sequence.

---

## 4. GDOT Policy 6785-2 — Left-Turn Phasing (the concrete warrant criteria)

[Full text](https://mydocs.dot.ga.gov/info/gdotpubs/Publications/6785-2.pdf)
(fetched via reader proxy; direct fetch blocked). Reviewed 8/13/2020.

**Default posture:** left-turn phases are *not* installed at new/upgraded
signals unless justified below, and never without a dedicated left-turn
lane already existing.

### A. Protected/permissive (FYA) — installed if *any* of:
1. **Cross-product > 50,000** (leading left) or **> 30,000** (lagging
   left), where
   `Cross Product = left-turn volume × (opposing through volume / number of opposing through lanes)`
2. **Left-turn volume ≥ 125 veh/h** (leading) or **≥ 75 veh/h** (lagging)
3. **≥ 4 left-turn crashes in 12 months**, or **≥ 6 in 24 months**, under
   permissive operation
4. Engineering judgment factors: insufficient turn-lane storage, delay,
   turn angle, number of opposing lanes, opposing speed, coordinated-system
   membership

*(If only the lagging thresholds are met, the phase must run lagging-only,
and the opposing left needs its own 3-section permissive-only FYA.)*

### B. Protected-only — installed if:
1. Sight distance permanently obstructed below the required minimum (GDOT
   provides a lookup table by design speed × red-clearance interval, e.g.
   at 35 mph / 3.0 s RCI the minimum sight distance is 260 ft)
2. Conflicting left-turn paths (may need lead/lag)
3. Unusual geometry or high pedestrian volume
4. ≥ 5 left-turn angle crashes with opposing traffic in 24 months under
   protected/permissive operation

### C. Sight-distance formulas given directly in the policy:
```
Red Clearance Interval = (W + L) / V_LT
LTSD = V_major × (2 + (W + L) / V_LT)
```
where `W` = distance from stop bar to the far conflicting movement's
outside travel-lane edge, `L` = vehicle length (20 ft typical), `V_LT` =
85th-percentile left-turning speed (25 mph typical), `V_major` = opposing
through design speed. **Note this RCI formula is structurally identical**
to the general ITE red-clearance formula below — GDOT's left-turn policy
and general ITE practice agree, not two different rules.

### D. Right-turn phasing (same policy document, Part III):
- Protected right-turn phase only if an exclusive right-turn lane exists.
- Single lane → single (non-overlap) protected indication typical; dual
  right-turn lanes → prefer permissive (with RTOR) if sight distance
  allows.
- Red right arrow (fully prohibiting the movement) only where
  right-turn-on-red itself is prohibited.

### E. Split phasing (Part IV) — only justified by:
side street has a shared through/left lane; crash history tied to that
shared lane; unbalanced opposing volumes where one direction needn't be
served every cycle; unusual/offset geometry; conflicting left paths where
lead/lag isn't viable; sight-distance issues where protected-only left
isn't desirable.

---

## 5. GDOT Policy 6785-1 — Traffic Signals (general/warrant context)

[Full text](https://mydocs.dot.ga.gov/info/gdotpubs/PolicyandProcedures/6785-1.pdf).
Less directly relevant to *phasing design* (SIG#7065 already exists as a
signal), but useful background: GDOT prefers only installing/keeping
signals meeting **MUTCD Warrant 1 (Eight-Hour Vehicular Volume)** or
**Warrant 7 (Crash Experience)** at 100%. Left-turn lanes are policy-favored
generally ("shown to reduce crashes by 50% on average... should be added on
all approaches"), and lack of a left-turn lane is itself grounds to deny a
left-turn-phase request — consistent with §4 above.

---

## 6. MUTCD / ITE clearance-interval and pedestrian-timing standards

These are national engineering standards Georgia follows directly (no GA
override found).

### Yellow change interval (MUTCD §4D.26 + ITE formula)
- Range: **3.0–6.0 s** (MUTCD-permitted bounds; longer for higher-speed
  approaches).
- Standard (ITE) kinematic formula:
  `Y = t + v / (2a + 2·G·g)`
  where `t` = perception-reaction time (**1.4 s** per FDOT/ITE practice —
  no GA-specific PRT value found, 1.4 s is the general ITE-recommended
  figure), `v` = approach speed (ft/s, use posted speed limit), `a` =
  deceleration rate (~10 ft/s² typical), `G` = grade (decimal, + upgrade /
  − downgrade), `g` = 32.2 ft/s².
- Computed values are commonly floored at ~3.4 s in practice (FDOT
  standard; no confirmed GA-specific floor, treat as a reasonable default).
  [FDOT yellow/red clearance training](https://fdotwww.blob.core.windows.net/sitefinity/docs/default-source/content/roadway/training/webinar14/1-4.pdf)

### Red clearance interval (MUTCD §4D.26 + ITE formula)
- Range: **0–6.0 s** (some agencies use 0 s by policy, most compute a
  value; MUTCD caps at 6 s).
- Formula (matches GDOT policy 6785-2 exactly, §4C above):
  `R = (W + L) / v`
  `W` = intersection width to be cleared (ft), `L` = vehicle length
  (20 ft typical), `v` = clearing speed (ft/s).
- Practical floor of **2.0 s** is common (FDOT/NCHRP 731 guidance); no
  GA-specific floor confirmed.

### Minimum/maximum green
- **No single MUTCD-mandated number for standard vehicular phases** — set
  by engineering judgment per approach/agency. (MUTCD *does* give an
  explicit formula for the bicycle-phase case:
  `G_min + Y + R_clear ≥ 6 sec + (W + 6 ft)/14.7 ft/s` — not directly
  applicable to our vehicular phases, noted for completeness.)
- No GDOT-specific minimum/maximum green value was found publicly
  (again, likely lives in the not-yet-published Traffic Signal Operations
  Guide). Treat Sahachaiseree's own values (`υ_min = 3 s`, `max = 30 s`) as
  a starting assumption to *validate*, not a Georgia-sourced number.

### Pedestrian timing (MUTCD)
- **Walk interval ≥ 7 s** minimum.
- **Pedestrian clearance time = crosswalk length ÷ walking speed**, using
  **3.5 ft/s** (current MUTCD standard, reduced from the older 4.0 ft/s).
- **3.0 ft/s** used instead when sizing the combined walk + clearance
  time; **2.8 ft/s** where older/disabled pedestrians routinely cross.
  [MUTCD pedestrian crossing standards](https://mutcd.info/mutcd-pedestrian-crossing-crosswalk-standards/)

---

## 7. Implications for `rlagent/plan.md` Phase 0 (stage table design)

- **Left-turn phase type per approach is not a free design choice — it's
  computable from our own calibrated data.** SIG#7065 has real dedicated
  left-turn lanes on all 4 approaches (ground-truth lane config in
  `sumotwin/README.md`), so §4's cross-product/volume criteria can be
  evaluated directly against `sumodemand/0507.rou.xml` / `0508.rou.xml`'s
  per-movement volumes — this decides, per approach, whether it should be
  modeled as protected/permissive, protected-only, or permissive-only,
  rather than assuming a uniform treatment for all 4 like Sahachaiseree's
  toy intersection does. **Follow-up task**: compute the cross-product and
  left-turn volume for each approach from the calibrated demand before
  finalizing the stage table.
- **GDOT's asymmetric-left-turn-phase practice matters for the stage
  table.** Don't force all 4 approaches to have identical
  protected-left-eligible stages if the real warrant criteria only justify
  it on some.
- **Right turns likely don't need their own stage at all.** Georgia's
  right-turn-on-red default (§2) means, absent a posted prohibition (not
  confirmed either way — flag to verify), the 3 unmeasured real right-turn
  movements (NB/SB/EB) and the WB slip lane can all be treated as
  continuously available rather than gated by a stage, similar to how the
  slip lane already bypasses the signal entirely. Simplifies the action
  space versus needing a dedicated right-turn phase per approach.
- **Interstage timing should be computed, not borrowed wholesale from the
  paper.** `sumotwin`'s real approach speed (15.6 m/s ≈ 35 mph) and real
  intersection width (derivable from the net.xml geometry) can be plugged
  directly into the ITE yellow-change and red-clearance formulas in §6 to
  get Georgia-consistent amber/all-red values, rather than reusing
  Sahachaiseree's flat 3 s amber / 1 s all-red assumption as-is.
- **Phase-numbering convention** (§3: phase 2 = WB/SB major street,
  counterclockwise, odd = left) is worth adopting when labeling our custom
  stage table, purely for realism/documentation clarity — our controller
  is a direct TraCI stage-selector, not a literal NEMA dual-ring
  controller, so nothing here is a hard technical constraint, but it makes
  the design legible to anyone who knows US signal conventions.

---

## 8. Field verification — photographed signal heads at SIG#7065 (2026-07-11)

User-supplied photos of the actual signal heads at Peachtree Rd & Piedmont
Rd, cross-checked against `sumotwin/README.md`'s ground-truth lane table
and a round of web research. Directions confirmed by the user mid-review
(not assumed): **photo 1 (3 heads: left-arrow head with a "LEFT TURN YIELD
ON FLASHING YELLOW ARROW" sign, a through head, and a head showing a red
ball + green right-turn arrow simultaneously) is the Piedmont Rd
(NB/SB) approach; photo 2 (5 heads: two left-arrow heads, three through
heads, plus a "NO U-TURN" sign) is the Peachtree Rd (EB/WB) approach.**

- **FYA sign confirms photo 1's left is protected/permissive, not
  protected-only** — matches this doc's §4A read exactly: MUTCD IA-10 and
  Georgia's incorporation of it mean a "LEFT TURN YIELD ON FLASHING YELLOW
  ARROW" sign is only posted where the head can display the flashing
  yellow arrow, i.e. the FYA/protected-permissive mode this project already
  assigned to NB-left and SB-left in `stages.py` (§4A warrant: both clear
  the cross-product/volume thresholds). No change needed — this is
  confirmation, not a correction.
  [FHWA IA-10](https://mutcd.fhwa.dot.gov/resources/interim_approval/ia_10_flashyellarrow.htm),
  [LegalClarity: LT Yield on FYA sign](https://legalclarity.org/left-turn-yield-on-flashing-yellow-arrow-sign-mutcd-rules/)

- **The rightmost head in photo 1 is a "Right Doghouse" 5-lamp signal
  head (user-confirmed layout: 1 top, 2 middle, 2 bottom) — not a generic
  4-section head as first described.** It's two independent 3-lamp faces
  sharing one red lens: a circular ball face (through) and a right-turn
  arrow face, side by side, arrow stack on the right. This exists because
  MUTCD requires a green arrow to clear via a yellow *arrow* (not a yellow
  ball), which doesn't fit in a single vertical column with a ball face —
  doghouses split it into two side-by-side columns instead.
  [Doghouse signal head reference](https://www.trafficsignalmuseum.com/pages/doghouse.htm),
  [5-light doghouse detail](https://www.kbrhorse.net/signals/marbdh.html)
  This is real protected-right-turn-overlap hardware — **not modeled in
  `stages.py` today** (which gives all rights plain `'g'`). GDOT Policy
  6785-2 Part III (§4D above) only allows a protected right-turn overlap
  where an **exclusive** right-turn lane exists, and requires prohibiting
  U-turns from whichever left-turn phase the overlap is paired with (the
  U-turn would conflict with the protected right arrow).
  [GDOT 6785-2 PDF](https://mydocs.dot.ga.gov/info/gdotpubs/Publications/6785-2.pdf)
  Cross-checking `sumotwin/README.md`'s lane table confirms this is
  geometrically consistent, not a coincidence:
  - **N leg (SB) and S leg (NB)**: netconvert-default lane use = exclusive
    right + n straight + left → **both have an exclusive right lane**,
    i.e. both are eligible for the overlap under Policy 6785-2, matching
    what photo 1 shows for whichever of the two it is.
  - **SW leg (EB)**: "2 left, 2 straight, 1 **shared** straight/right" →
    *not* eligible for a protected overlap (a shared lane can't be pulled
    into its own phase without blocking the through vehicles stacked
    behind it) — consistent with photo 2 (EB/WB) showing no green arrows
    at all.
  - **NE leg (WB)**: "2 left, 3 straight, **no right**" — the WB right is
    the hand-traced slip lane (`E1`) that bypasses the signal entirely
    (per `CLAUDE.md` #3), so there's no head to photograph there either
    way. Consistent.
  - Net effect: this photographic + policy + geometry cross-check all
    agree that **NB-right and SB-right are real protected-overlap
    movements, EB-right is a real shared-lane permissive movement, and
    WB-right is genuinely signal-free** — a cleaner three-way split than
    `stages.py`'s current blanket "all rights get plain `'g'` in
    compatible stages" treatment.
  - **Not yet resolved:** which stage the NB/SB overlap runs concurrent
    with (i.e. its exact `OL` pairing) isn't confirmed from a real GDOT
    timing sheet — only one approach's head was photographed, and generic
    NEMA practice ("right overlap shadows a compatible cross-street left,
    displays ball-green during the parent through phase too") is a
    plausible pattern, not a sourced fact for *this* intersection. Per
    this project's fidelity policy, don't hardcode a specific overlap
    pairing into `stages.py` without that source — the safe, sourced
    change is only upgrading NB-right/SB-right from `'g'` to `'G'` in the
    stages where they're already active (they're real protected arrows,
    not yield-permissive), leaving EB-right and the WB slip as they are.
    Since right-turn demand is zero in the calibrated data regardless
    (§2), this has no effect on current training runs either way — same
    "harmless but should be fixed for correctness" status as the RTOR
    note in §2 already had. **Applied** (2026-07-11): the action-space
    redesign sets NB/SB rights `'G'` in the NS_THRU parent-through phase
    only; the additional (unsourced) overlap windows are still left off.
    [right-turn-overlap phase pairing background](https://oboe.com/learn/traffic-signal-engineering-and-control-systems-1knlj7s/intersection-phasing-engineering-0)

- **The "NO U-TURN" sign in photo 2 (EB/WB) is very likely unrelated to a
  right-turn overlap** — EB/WB has no overlap arrow in the photo, and
  photo 2 shows **two** left-arrow heads (a dual left-turn lane), which is
  itself a standard, independent reason to post "NO U-TURN": a U-turn from
  the inner of two left-turn lanes sweeps through the outer lane's path.
  Not confirmed against a GDOT plan sheet, flagged here rather than
  asserted as fact.

- **EB's shared thru/right lane (SW leg) still gets normal RTOR — the
  shared geometry doesn't remove the legal right, only the practical
  ability to use it.** MUTCD requires a lane shared between thru and
  right-turn movements to display a **circular red**, never a red arrow
  (arrows are reserved for lanes with one exclusive movement) — and
  Georgia's RTOR rule (§2) is keyed entirely off *which indication is
  shown*: circular red → RTOR allowed by default after stop + yield; red
  arrow → prohibited outright. Since EB's shared lane is required to show
  circular red, its right-turners get the same default legal RTOR as
  anyone else, absent a posted "NO TURN ON RED" sign (confirmed not
  present here). What actually differs from NB/SB is operational, not
  legal: sharing a lane with thru traffic means a right-turner can't pass
  a queued thru vehicle ahead of them the way an exclusive/slip lane
  would let them — they can only act on RTOR once *they* reach the stop
  line, so the shared lane sees it exercised far less often in practice
  than NB/SB's exclusive-lane/overlap or WB's slip. This is consistent
  with, not a contradiction of, GDOT Policy 6785-2 Part III's general
  preference for exclusive lanes/overlaps over shared ones where volume
  justifies it.
  [MUTCD shared-lane signal indication rule](https://up.codes/s/signal-indications-for-approaches-with-shared-left-turn-right-turn-lanes-and-no)

### Worked example — one full cycle in action

Putting §§2–8 together into a chronological walkthrough. **Sourced parts**:
the stage sequence/structure, which movements are protected vs. permissive
vs. overlap vs. signal-free, and the 4.0 s yellow / 3.0 s all-red clearance
(§6/§7). **Not sourced**: the actual green durations below (no GDOT timing
sheet for SIG#7065 exists in this project) — they're illustrative round
numbers, not a claimed real cycle length or split. Barrier order (Piedmont
first, then Peachtree) is arbitrary for this example; a real coordinated
signal's actual barrier order isn't confirmed either.

**Piedmont Rd (NB/SB) — barrier 1**
1. `NS_LEFT` (NEMA 3+7, ~12 s green + 4.0 s yellow arrow + 3.0 s all-red):
   both NB-left and SB-left arrow heads show a **solid green arrow**
   (both independently warrant protection, §4/§7). Both thru balls are
   red. The doghouse heads' shared top red stays lit; whether the arrow
   column also shows green here (right-turner riding the same-approach
   protected left) is the one unconfirmed timing detail flagged in §8.
2. `NS_THRU` (NEMA 4+8, ~20 s green + 4.0 s yellow + 3.0 s all-red): both
   thru balls go **green**; both left-arrow heads drop to **flashing
   yellow arrow** (§2, the FYA sign's literal meaning); the doghouse ball
   column goes green with the thru lane.

**Peachtree Rd (EB/WB) — barrier 2**
3. `EW_LEFT` (NEMA 1+5, ~12 s green + 4.0 s yellow arrow + 3.0 s all-red):
   EB-left (both lanes) shows a **solid green arrow** (warrants
   protection). WB-left showing a green arrow here too — because it's
   simply unopposed while EB is held red, not because it independently
   warrants one — is `stages.py`'s current assumption, not a field-checked
   fact (§7).
4. `EW_THRU` (NEMA 2+6, ~20 s green + 4.0 s yellow + 3.0 s all-red): EB
   and WB thru balls go **green**. Both left-arrow heads drop to
   **flashing yellow arrow** — for WB this is the one point in the whole
   cycle where its real, sourced permissive-only treatment is actually
   exercised (§7). EB's shared thru/right lane ball goes green alongside
   its two dedicated thru balls; right-turners there merge in on an
   ordinary green with normal RTOR rights (just less usable than an
   exclusive lane, per the bullet above). WB's right-turners were never
   signal-gated at all — `E1` has been flowing continuously the entire
   cycle, all 4 stages, since it bypasses `J` entirely (§8's slip-lane
   finding).

Cycle then returns to `NS_LEFT`. **Not part of a normal cycle:**
`stages.py`'s other 4 stages (`EB_ONLY`, `WB_ONLY`, `NB_ONLY`, `SB_ONLY`)
are single-approach combinations that exist so the RL agent can hold an
uneven green split (serve one approach alone under light cross-traffic) —
a real pretimed/coordinated signal at a corridor intersection like this
one very likely never displays them as a planned stage; they're an
RL-action-space affordance beyond what a real fixed-time controller here
would do, not a discrepancy to fix.

**Contradiction check (per user request to flag doc drift) — status as of
this pass:** §2's Buckhead RTOR claim is fixed above. The gap between the
old design intent (rights need no dedicated stage, plain `'g'`) and the
field photos (NB/SB rights are protected overlaps) is now **closed**: the
2026-07-11 action-space redesign encodes NB/SB rights as protected `'G'`
overlaps in NS_THRU, EB-right as shared-lane `'g'`, and the WB slip as
signal-free. That redesign also **replaced the free 8-stage selection
action space with the realistic ordered-actuated model** described in the
worked example above — the agent now runs the fixed
`EW_LEFT→EW_THRU→NS_LEFT→NS_THRU` cycle with a binary extend/advance
action and FYA protected-permissive lefts, so this section's worked
example is now a literal description of `stages.py`, not an aspiration.
`CLAUDE.md`'s previously-stale status section has also been corrected.
