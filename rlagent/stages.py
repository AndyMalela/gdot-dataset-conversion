"""Realistic phase table + interstage timing for SIG#7065.

This replaces the paper's free 8-stage *selection* action space with the
ordered NEMA actuated model the real intersection actually runs (see the
field-verification pass in rlagent/regulations.md #8). Two things changed
versus the first replication cut:

1. **Ordered ring-barrier cycle, not free stage selection.** A real signal
   cannot jump to an arbitrary phase; it runs a fixed cyclic order and an
   actuated controller's only freedoms are *how long* to hold the current
   phase and *when* to step to the next. So the action space is now binary
   -- EXTEND the current phase or ADVANCE to the next phase in the cycle
   -- over the fixed lead-left quad-phase order:

       EW_LEFT -> EW_THRU -> [barrier] -> NS_LEFT -> NS_THRU -> [barrier] ->

   The four single-approach "*_ONLY" stages of the old table are gone: they
   have no place in a real ring-barrier cycle (they were an artifact of the
   paper's toy free-selection controller). Independent per-ring timing
   (lead/lag overlap, e.g. EB-left ending while WB-left holds) is a further
   realism refinement deliberately not modeled yet -- both rings advance
   together here, which is how a simpler actuated / fully-coordinated signal
   behaves.

2. **Protected-permissive (FYA) lefts, protected right overlaps, shared
   lanes** -- each phase's per-movement signal states now match the real
   heads photographed at the intersection (regulations.md #4, #8):

   - **EB/NB/SB lefts are protected-permissive (FYA).** They show a
     protected green arrow ('G') in their own street's LEFT phase, and drop
     to a permissive 'g' (flashing yellow arrow -- yield to the opposing
     through) during that street's THRU phase. This is the big behavioural
     change from the protected-*only* first cut, and it matters: these three
     lefts carry 185-272 vph of real demand, so letting them clear
     permissively during the through phase changes queueing/throughput. The
     net's left connections are state="o" (yield-capable), so SUMO enforces
     the permissive yielding automatically from the 'g'.
   - **WB-left is permissive-only** (70-92 vph, never meets the 125 vph /
     50k cross-product warrant -- GDOT does not install protected lefts
     symmetrically, regulations.md #3/#4). It is 'g' in *every* phase where
     it runs and never gets a protected 'G' arrow: in EW_THRU it yields to
     the EB through; in EW_LEFT the opposing EB-through is red so the same
     'g' simply flows unopposed. Same char, correct FYA behaviour either
     way.
   - **NB/SB rights are protected doghouse overlaps** ('G') during NS_THRU
     -- the red-ball+green-arrow "Right Doghouse" heads confirmed on
     Piedmont (regulations.md #8), backed by their exclusive right lanes
     (sumotwin/README.md). Only the sourced overlap window (parent through
     phase) is asserted; additional overlap windows a real controller might
     also run (e.g. shadowing a cross-street left) are left off pending a
     real GDOT timing sheet, per the project's fidelity policy.
   - **EB-right shares the EB-through lane** (SW leg, no exclusive right):
     it is 'g' whenever the EB through is green (circular green on a shared
     lane -- MUTCD requires circular red, never a red arrow, so normal RTOR
     applies; regulations.md #8). Never an overlap arrow.
   - **WB-right is the physical slip lane** (E1), outside the signal
     entirely -- it is not in the signalized link set at all.

   All right-turn treatments are behaviourally moot in training today
   (GDOT never measures right turns, so they carry zero demand -- see
   sumodemand/README.md), but they are encoded correctly so the model is
   faithful and so it stays correct if right-turn counts are ever obtained.

- Interstage timing computed from THIS intersection's geometry + ITE
  formulas (regulations.md #6), not copied from the paper:
    yellow  Y = PRT + v/(2a) = 1.4 + 15.6/(2*3.05)      = 3.96 -> 4.0 s
    all-red R = (W + L_veh)/v = (40.3 m + 6.1 m)/15.6   = 2.98 -> 3.0 s
  where v = 15.6 m/s (35 mph posted, both streets -- confirmed by the user,
  see regulations.md #6), a = 3.05 m/s^2 (10 ft/s^2 ITE deceleration),
  W = 40.3 m = longest signalized crossing, L_veh = 6.1 m (20 ft).

- Clearance is applied *selectively* per transition (see `transition`): only
  movements that actually lose right-of-way (green->red) clear via
  yellow -> all-red; movements that continue across the phase boundary are
  held (a through does not stop, and a left merely downgrading protected->
  permissive keeps flowing). So the two barrier crossings (THRU->LEFT) get a
  full yellow+all-red, while the lead-left->through transitions -- where the
  lefts only downgrade to permissive and the throughs start -- need no
  all-red at all, matching how a real controller flows a lead-left into its
  through. Simplification: a protected->permissive left downgrade is not
  given its own steady-yellow-arrow display frame (SUMO enforces the yield
  by G/g priority regardless); every safety-critical clearance (a movement
  fully stopping, a conflicting movement starting) is modeled.

- Decision interval delta = 1 s and minimum green upsilon = 3 s follow the
  paper's low-signal-constraint setting (its best-performing variant); no
  GDOT-mandated minimum green was found (regulations.md #6). A maximum green
  (paper's 30 s) is defined below but NOT enforced as a hard cap: doing so
  cleanly would require making time-in-phase observable, which would deviate
  from the paper's state (Eq. 12) -- deferred to the extension phase. The
  agent is expected to learn to advance, as in the paper.

Link index map (from sumotwin/7065.net.xml <connection linkIndex=...>):
  0,1,2  WB thru  (NE_in.79 -> SW_out)     3,4   WB left  (NE_in.79 -> S_out)
  5      NB right (S_in -> NE_out)         6,7   NB thru  (S_in -> N_out)
  8      NB left  (S_in -> SW_out)         9     EB right (SW_in -> S_out)
  10,11,12 EB thru (SW_in -> NE_out)       13,14 EB left  (SW_in -> N_out)
  15     SB right (N_near -> SW_out)       16,17 SB thru  (N_near -> S_out)
  18     SB left  (N_near -> NE_out)
"""

TLS_ID = "J"
N_LINKS = 19

# movement -> linkIndex set
LINKS = {
    "WBt": (0, 1, 2), "WBl": (3, 4),
    "NBr": (5,), "NBt": (6, 7), "NBl": (8,),
    "EBr": (9,), "EBt": (10, 11, 12), "EBl": (13, 14),
    "SBr": (15,), "SBt": (16, 17), "SBl": (18,),
}

# The fixed ring-barrier CYCLE, in order. Advancing steps to the next entry
# and wraps. phase -> {movement: signal char}; anything unlisted is 'r'.
# 'G' = protected green (priority), 'g' = permissive green (yields to foes).
PHASES = [
    ("EW_LEFT", {"EBl": "G", "WBl": "g"}),                      # NEMA 1(+5 perm)
    ("EW_THRU", {"EBt": "G", "WBt": "G",
                 "EBl": "g", "WBl": "g", "EBr": "g"}),          # NEMA 2+6 (+FYA)
    ("NS_LEFT", {"NBl": "G", "SBl": "G"}),                      # NEMA 3+7
    ("NS_THRU", {"NBt": "G", "SBt": "G",
                 "NBl": "g", "SBl": "g",
                 "NBr": "G", "SBr": "G"}),                      # 4+8 (+FYA+OL)
]
N_PHASES = len(PHASES)
PHASE_NAMES = [name for name, _ in PHASES]

# action space: at each decision point, hold or step forward one phase.
EXTEND = 0
ADVANCE = 1
N_ACTIONS = 2

# signal timing (seconds) -- see module docstring for derivations
YELLOW = 4.0
ALL_RED = 3.0
INTERSTAGE = YELLOW + ALL_RED   # tau = 7 s (full clearance; barrier crossings)
MIN_GREEN = 3.0                 # upsilon (paper's low-constraint setting)
MAX_GREEN = 30.0               # paper's value; defined, not hard-enforced (see docstring)
DELTA = 1.0                     # decision interval (paper: delta = 1 s)


def _state_string(moves: dict) -> str:
    chars = ["r"] * N_LINKS
    for mv, ch in moves.items():
        for idx in LINKS[mv]:
            chars[idx] = ch
    return "".join(chars)


GREEN_STATE = [_state_string(m) for _, m in PHASES]
ALL_RED_STATE = "r" * N_LINKS


def transition(cur_idx: int, nxt_idx: int):
    """Selective clearance between two phases.

    Returns (yellow_str, allred_str) for the interstage, or None when no
    movement loses right-of-way (so the advance needs no yellow/all-red --
    the lead-left->through case, where lefts only downgrade to permissive
    and throughs start). Movements that continue across the boundary are
    held at their outgoing char through the clearance; only movements going
    green->red show 'y' then 'r'.
    """
    cur, nxt = GREEN_STATE[cur_idx], GREEN_STATE[nxt_idx]
    clearing = {i for i in range(N_LINKS) if cur[i] in "Gg" and nxt[i] == "r"}
    if not clearing:
        return None

    def held(i: int) -> bool:
        return cur[i] in "Gg" and nxt[i] in "Gg"

    yellow = "".join(
        "y" if i in clearing else (cur[i] if held(i) else "r")
        for i in range(N_LINKS)
    )
    allred = "".join(cur[i] if held(i) else "r" for i in range(N_LINKS))
    return yellow, allred


# inbound lanes whose per-lane vehicle counts form the state vector, and
# over which the queue reward is summed. Ordered, stop-bar edges first.
# (E1, the uncontrolled slip lane, is excluded: it bypasses the signal.)
APPROACH_EDGES = [
    "S_in",                              # NB, 4 lanes
    "N_near", "N_far",                   # SB, 4 + 3 lanes
    "SW_in",                             # EB, 5 lanes
    "NE_in.79", "NE_in.15", "NE_in",     # WB, 5 + 6 + 5 lanes
]
