"""Linear FA + LSTDQ, replicating Sahachaiseree Eqs. 9-11.

q_hat(s, a; W) = w_a . x(s)  -- implemented as one flat weight vector over
state-action features x(s,a) of size m*n (Eq. 9-10): x(s) occupies the
a-th m-sized block, zeros elsewhere.

LSTDQ update (Eq. 11), the Bellman-OPTIMALITY variant -- the next-state
feature uses argmax_a q_hat(S', a; w_k) under the CURRENT weights, so policy
improvement is inside the least-squares solve (no separate LSPI wrapper):

  A = sum_t x(S_t,A_t) (x(S_t,A_t) - gamma * x(S_{t+1}, a*_{t+1}))^T
  b = sum_t R_{t+1} x(S_t,A_t)
  w_{k+1} = (A + ridge*I)^-1 b

The ridge term is ours, not the paper's: their 20-feature toy state keeps A
well-conditioned; our 40 real-lane features are strongly correlated during
congestion, so a small Tikhonov term is cheap insurance (documented in
plan.md Phase 2). ridge=0 recovers the paper exactly.
"""

from __future__ import annotations

import numpy as np


class LinearQ:
    def __init__(self, n_features: int, n_actions: int, seed: int = 0):
        self.m, self.n = n_features, n_actions
        rng = np.random.default_rng(seed)
        # paper: w ~ U(-0.03, +0.03), no bias term
        self.w = rng.uniform(-0.03, 0.03, size=self.m * self.n)

    def q_values(self, state) -> np.ndarray:
        x = np.asarray(state)
        return self.w.reshape(self.n, self.m) @ x

    def greedy(self, state) -> int:
        return int(np.argmax(self.q_values(state)))

    def act_eps_greedy(self, state, eps: float, rng: np.random.Generator) -> int:
        if rng.random() < eps:
            return int(rng.integers(self.n))
        return self.greedy(state)

    def phi(self, state, action: int) -> np.ndarray:
        out = np.zeros(self.m * self.n)
        out[action * self.m:(action + 1) * self.m] = state
        return out

    def lstdq_update(self, transitions, gamma: float = 0.9,
                     ridge: float = 1e-6, chunk: int = 8192) -> None:
        """transitions: iterable of (state, action, reward, next_state) or
        (state, action, reward, next_state, duration).

        With a 5th element, the semi-MDP form is used: the next-state term
        is discounted gamma**duration (gamma is per SECOND), so decisions
        that consume more simulated time (stage changes: interstage + min
        green) are discounted accordingly instead of counting as one step
        like a 1 s extension does. Without it, plain per-decision
        discounting (the paper's Eq. 11) applies.

        Vectorized + chunked so the accumulated-experience batch (all
        episodes so far, LSPI-style) stays fast as it grows.
        """
        trs = list(transitions)
        S = np.asarray([t[0] for t in trs], dtype=np.float64)
        Aact = np.asarray([t[1] for t in trs], dtype=np.intp)
        R = np.asarray([t[2] for t in trs], dtype=np.float64)
        S2 = np.asarray([t[3] for t in trs], dtype=np.float64)
        G = (gamma ** np.asarray([t[4] for t in trs], dtype=np.float64)
             if len(trs[0]) > 4 else np.full(len(trs), gamma))

        dim = self.m * self.n
        A = np.zeros((dim, dim))
        b = np.zeros(dim)
        W = self.w.reshape(self.n, self.m)
        for lo in range(0, len(trs), chunk):
            hi = min(lo + chunk, len(trs))
            s, a, r = S[lo:hi], Aact[lo:hi], R[lo:hi]
            s2, g = S2[lo:hi], G[lo:hi]
            a2 = np.argmax(s2 @ W.T, axis=1)          # greedy next action
            n_rows = hi - lo
            Xa = np.zeros((n_rows, dim))
            X2 = np.zeros((n_rows, dim))
            rows = np.arange(n_rows)[:, None]
            cols_a = a[:, None] * self.m + np.arange(self.m)[None, :]
            cols_2 = a2[:, None] * self.m + np.arange(self.m)[None, :]
            Xa[rows, cols_a] = s
            X2[rows, cols_2] = s2 * g[:, None]
            A += Xa.T @ (Xa - X2)
            b += Xa.T @ r
        self.w = np.linalg.solve(A + ridge * np.eye(dim), b)


def _toy_check():
    """2-state, 2-action chain with known optimum: from either state,
    action 1 pays +1 and action 0 pays 0. Greedy must learn action 1."""
    rng = np.random.default_rng(1)
    agent = LinearQ(n_features=2, n_actions=2, seed=1)
    s = [np.array([1.0, 0.0]), np.array([0.0, 1.0])]
    for _ in range(5):
        batch = []
        cur = 0
        for _ in range(200):
            a = agent.act_eps_greedy(s[cur], 0.2, rng)
            r = 1.0 if a == 1 else 0.0
            nxt = 1 - cur
            batch.append((s[cur], a, r, s[nxt]))
            cur = nxt
        agent.lstdq_update(batch, gamma=0.9, ridge=1e-8)
    assert agent.greedy(s[0]) == 1 and agent.greedy(s[1]) == 1, agent.w
    # optimal Q: Q(s,1) = 1/(1-.9) = 10, Q(s,0) = 0 + .9*10 = 9
    q = agent.q_values(s[0])
    assert abs(q[1] - 10.0) < 0.5 and abs(q[0] - 9.0) < 0.5, q
    print(f"toy MDP: greedy=action-1 everywhere, Q(s0)={q.round(2)} "
          "(theory: [9, 10]) -- OK")


if __name__ == "__main__":
    _toy_check()
