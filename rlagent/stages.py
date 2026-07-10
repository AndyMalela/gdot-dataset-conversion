"""Stage table (action space) + interstage timing for SIG#7065.

This is rlagent/plan.md Phase 0's deliverable: Sahachaiseree's 8-stage
stage-selection action space (2 paired-through stages, 2 dual-left stages,
4 single-approach stages -- their Fig. 5 structure), instantiated for this
intersection's real geometry and Georgia practice (see regulations.md).

Design decisions, with sources:

- The 8 stages are exactly the 8 conflict-free combinations of a standard
  NEMA dual-ring (regulations.md #3): {2+6, 1+5, 1+6, 2+5} on the major
  street (Peachtree, EB/WB) and {4+8, 3+7, 3+8, 4+7} on the minor
  (Piedmont, NB/SB). This is also a 1:1 translation of Sahachaiseree's
  Fig. 5 stage set -- their environment is left-hand-drive Japan, so their
  "left" (near-side turn) maps to our right turn and their "right"
  (crossing turn) to our left turn.

- Left-turn treatment is asymmetric, per GDOT Policy 6785-2 warrants
  computed from the calibrated demand (all 4 days, rolling peak hour):
    EB-left: 187-261 vph peak (>=125 warrant met all days), cross-product
             39k-58k (>50k met 3/4 days)      -> protected
    NB-left: 185-272 vph, cross-product 75k-127k (met all days) -> protected
    SB-left: 228-264 vph, cross-product 47k-75k (met 3/4 days)  -> protected
    WB-left: 70-92 vph -- NEVER meets the 125 vph leading-left warrant;
             cross-product 28k-54k (met only 1/4 days)  -> PERMISSIVE-ONLY
  GDOT explicitly does not install left phases symmetrically
  (regulations.md #3), so WB-left gets no protected requirement: it runs
  permissive ('g', yield to oncoming EB through) during EW_THRU -- the FYA
  treatment -- and happens to be unopposed (so 'G') in EW_LEFT and WB_ONLY.

- Right turns carry zero demand (never measured by GDOT -- see
  sumodemand/README.md) and Georgia right-turn-on-red is the legal default
  anyway (regulations.md #2). They are set 'g' in stages where their target
  edge has no active conflicting protected movement, 'r' otherwise. The WB
  right is the physical slip lane (E1), outside the signal entirely.

- Interstage timing computed from THIS intersection's geometry + ITE
  formulas (regulations.md #6), not copied from the paper:
    yellow  Y = PRT + v/(2a) = 1.4 + 15.6/(2*3.05)      = 3.96 -> 4.0 s
    all-red R = (W + L_veh)/v = (40.3 m + 6.1 m)/15.6   = 2.98 -> 3.0 s
  where v = 15.6 m/s (35 mph posted, both streets), a = 3.05 m/s^2
  (10 ft/s^2 ITE deceleration), W = 40.3 m = longest signalized crossing
  (NB/SB through across Peachtree, measured from the net's internal lane
  lengths), L_veh = 6.1 m (20 ft). Paper used 3 s + 1 s on a much smaller
  box; ours is honestly bigger.

- Decision interval delta = 1 s and minimum green upsilon = 3 s follow the
  paper's low-signal-constraint setting (its best-performing variant); no
  GDOT-mandated minimum green was found (regulations.md #6).

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

# stage -> {movement: signal char}. Anything unlisted is 'r'.
# 'G' = protected green (priority), 'g' = permissive green (yields).
STAGES = [
    ("EW_THRU", {"EBt": "G", "WBt": "G", "WBl": "g"}),          # NEMA 2+6
    ("EW_LEFT", {"EBl": "G", "WBl": "G"}),                      # NEMA 1+5
    ("EB_ONLY", {"EBt": "G", "EBl": "G", "EBr": "g"}),          # NEMA 1+6
    ("WB_ONLY", {"WBt": "G", "WBl": "G"}),                      # NEMA 2+5
    ("NS_THRU", {"NBt": "G", "SBt": "G", "NBr": "g", "SBr": "g"}),  # 4+8
    ("NS_LEFT", {"NBl": "G", "SBl": "G"}),                      # NEMA 3+7
    ("NB_ONLY", {"NBt": "G", "NBl": "G", "NBr": "g"}),          # NEMA 3+8
    ("SB_ONLY", {"SBt": "G", "SBl": "G", "SBr": "g"}),          # NEMA 4+7
]
N_STAGES = len(STAGES)
STAGE_NAMES = [name for name, _ in STAGES]

# signal timing (seconds) -- see module docstring for derivations
YELLOW = 4.0
ALL_RED = 3.0
INTERSTAGE = YELLOW + ALL_RED   # tau = 7 s
MIN_GREEN = 3.0                 # upsilon (paper's low-constraint setting)
DELTA = 1.0                     # decision interval (paper: delta = 1 s)


def _state_string(moves: dict) -> str:
    chars = ["r"] * N_LINKS
    for mv, ch in moves.items():
        for idx in LINKS[mv]:
            chars[idx] = ch
    return "".join(chars)


GREEN_STATE = [_state_string(m) for _, m in STAGES]
# yellow transition: every non-red link of the outgoing stage shows 'y'
YELLOW_STATE = [s.replace("G", "y").replace("g", "y") for s in GREEN_STATE]
ALL_RED_STATE = "r" * N_LINKS

# inbound lanes whose per-lane vehicle counts form the state vector, and
# over which the queue reward is summed. Ordered, stop-bar edges first.
# (E1, the uncontrolled slip lane, is excluded: it bypasses the signal.)
APPROACH_EDGES = [
    "S_in",                              # NB, 4 lanes
    "N_near", "N_far",                   # SB, 4 + 3 lanes
    "SW_in",                             # EB, 5 lanes
    "NE_in.79", "NE_in.15", "NE_in",     # WB, 5 + 6 + 5 lanes
]
