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

**Relevant to us:** right turn on red is the Georgia *state* legal default —
**but it does not apply here.** Per the research notes in
`approachspeeddottedlinesinfo.txt` (chatbot-sourced, citing Atlanta news
coverage — not independently verified against the ordinance text), the
Atlanta City Council passed an ordinance banning right-turn-on-red across
Downtown, Midtown, and **Buckhead**, effective 2026 — and SIG#7065
(Peachtree @ Piedmont) is in Buckhead. So the local ordinance overrides the
state default: rights should only move on green here. The `stages.py` stage
table already behaves this way (rights are 'g' only within compatible green
stages, never released on red), so no change was needed — recorded so nobody
"fixes" the table toward state-default RTOR later. The same notes also say
3 of the 4 legs have posted "ONLY RIGHT TURN" lane markings (one leg has a
shared through/right lane) — consistent with the twin's lane channelization.

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
