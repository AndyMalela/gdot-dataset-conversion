"""Diagnostic: is the LSTDQ solve ill-conditioned? (temporary)

Builds A = Sum x(x - g x')^T and b exactly as lstdq_update does, from a real
(short) experience batch, and reports conditioning for each feature mode.
"""
import numpy as np, stages as st
from lstdq import LinearQ
from sumo_env import Sig7065Env
from train import run_episode

RIDGE = 1e-4          # train.py / train_random.py default
GAMMA = 0.99

def collect(mode, episodes=2, begin=54000, end=55800, seed=1):
    env = Sig7065Env('../sumodemand/0507.rou.xml', begin=begin, end=end,
                     seed=seed, label='c', feature_mode=mode)
    env.reset(); agent = LinearQ(env.n_state_features, st.N_ACTIONS, seed=seed); env.close()
    rng = np.random.default_rng(0); exp = []
    for ep in range(episodes):
        env.seed = seed*1000+ep
        tr, *_ = run_episode(env, agent, 0.3, rng)   # high eps -> broad state coverage
        exp += tr
    return exp, env.n_state_features

def build_A(exp, m, n=st.N_ACTIONS, gamma=GAMMA):
    dim = m*n; A = np.zeros((dim, dim)); b = np.zeros(dim)
    W = np.zeros((n, m))   # greedy next-action under zero weights = action 0; fine for conditioning
    for (s,a,r,s2,dur) in exp:
        x = np.zeros(dim); x[a*m:(a+1)*m] = s
        a2 = int(np.argmax(W @ np.asarray(s2)))
        x2 = np.zeros(dim); x2[a2*m:(a2+1)*m] = np.asarray(s2)*(gamma**dur)
        A += np.outer(x, x - x2); b += r*x
    return A, b

for mode in ['phase_gated', 'phase_gated_norm', 'phase_gated_v3']:
    exp, m = collect(mode)
    A, b = build_A(exp, m); dim = A.shape[0]
    I = np.eye(dim)
    condA = np.linalg.cond(A)
    condAr = np.linalg.cond(A + RIDGE*I)
    # symmetric part eigenvalue spread (A is non-symmetric)
    sym = 0.5*(A+A.T); ev = np.linalg.eigvalsh(sym)
    # how much does ridge change the solution? (sensitivity)
    w_r = np.linalg.solve(A + RIDGE*I, b)
    w_big = np.linalg.solve(A + 1e-2*I, b)
    rel = np.linalg.norm(w_r-w_big)/(np.linalg.norm(w_r)+1e-12)
    print(f'--- {mode} (dim={dim}, n_transitions={len(exp)}) ---')
    print(f'  cond(A)            = {condA:.3e}')
    print(f'  cond(A + {RIDGE}I)   = {condAr:.3e}')
    print(f'  symmetric-part eig : min={ev.min():+.3e} max={ev.max():+.3e}  (neg min => not PD)')
    print(f'  ||w||              = {np.linalg.norm(w_r):.3e}')
    print(f'  rel change ridge 1e-4 vs 1e-2 = {rel:.3f}  (large => ridge-sensitive/ill-cond)')
