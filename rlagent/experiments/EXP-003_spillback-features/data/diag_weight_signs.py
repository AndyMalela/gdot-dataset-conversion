"""Diagnostic: do learned v3 weights have counter-intuitive signs? (temporary)

v3 feature layout (136): [onehot(4), gated occupancy(4x32=128), gated elapsed(4)].
Preference toward EXTEND for a feature = w[EXTEND] - w[ADVANCE] (>0 => that
feature pushes the agent to keep extending the current phase).

Intuition:
  - occupancy of the CURRENT phase's served lanes high -> EXTEND is reasonable
    (keep discharging the queue you're serving).
  - elapsed time high -> should push ADVANCE (you've served long enough);
    a POSITIVE extend-preference on elapsed is counter-intuitive (self-parking).
"""
import numpy as np, stages as st
NP = st.N_PHASES; NL = 32
def load(p): return np.load(p).reshape(st.N_ACTIONS, -1)
def occ_pref(w, ph):   # sum extend-preference over phase ph's 32 occupancy weights
    s = NP + ph*NL
    return (w[st.EXTEND, s:s+NL] - w[st.ADVANCE, s:s+NL]).sum()
def elapsed_pref(w, ph):
    idx = NP + NP*NL + ph
    return w[st.EXTEND, idx] - w[st.ADVANCE, idx]

seeds = {0:('results/exp003_v3/weights_random_s0.npy','PARK NS_LEFT'),
         1:('results/exp003b_v3/weights_random_s1.npy','healthy'),
         2:('results/exp003b_v3/weights_random_s2.npy','PARK NS_THRU'),
         3:('results/exp003b_v3/weights_random_s3.npy','healthy'),
         4:('results/exp003b_v3/weights_random_s4.npy','healthy')}
print("v3 EXTEND-preference (w_EXTEND - w_ADVANCE); >0 = pushes to keep extending")
print("elapsed >0 is COUNTER-INTUITIVE (should push advance).")
print(f"{'seed':>4} {'behav':>12} | "+" ".join(f"{n[:5]:>7}" for n in st.PHASE_NAMES)+"  <- ELAPSED pref per phase")
for s,(p,lab) in seeds.items():
    w=load(p)
    print(f"{s:>4} {lab:>12} | "+" ".join(f"{elapsed_pref(w,ph):>7.1f}" for ph in range(NP)))
print()
print(f"{'seed':>4} {'behav':>12} | "+" ".join(f"{n[:5]:>7}" for n in st.PHASE_NAMES)+"  <- OCCUPANCY pref per phase (sum of 32)")
for s,(p,lab) in seeds.items():
    w=load(p)
    print(f"{s:>4} {lab:>12} | "+" ".join(f"{occ_pref(w,ph):>7.0f}" for ph in range(NP)))
