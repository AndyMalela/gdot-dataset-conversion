"""Linear Q-function + LSTDQ (Sahachaiseree & Oguchi's base method; v2 rewrite of rlagent/lstdq.py).

q(s, a) = w . phi(s, a), phi = the state features in the a-th block (one weight block per action).
LSTDQ, Bellman-optimality form with semi-MDP discounting (gamma per second, d = seconds between decisions):

    A = sum phi(s,a) (phi(s,a) - gamma^d phi(s', a*))^T,   a* = argmax_a q(s', a; w_k)
    b = sum r phi(s,a),     w_{k+1} = (A + ridge I)^-1 b
"""
from __future__ import annotations

import numpy as np


class LinearQ:
    def __init__(self, m, n_actions=2, seed=0):
        self.m, self.n = m, n_actions
        self.w = np.random.default_rng(seed).uniform(-0.03, 0.03, m * n_actions)

    def q(self, x):
        return self.w.reshape(self.n, self.m) @ x

    def greedy(self, x):
        return int(np.argmax(self.q(x)))

    def fit(self, X, A, R, X2, D, done, gamma, ridge=1e-3, iters=1):
        """X, X2: (N, m) state features; A: actions; R: rewards; D: durations (s); done: terminal flags."""
        N, m = X.shape
        for _ in range(iters):
            a2 = np.argmax(X2 @ self.w.reshape(self.n, m).T, axis=1)
            Amat = np.zeros((m * self.n, m * self.n))
            b = np.zeros(m * self.n)
            disc = np.where(done, 0.0, gamma ** D)
            for a in range(self.n):
                ia = A == a
                sl = slice(a * m, (a + 1) * m)
                b[sl] += X[ia].T @ R[ia]
                Amat[sl, sl] += X[ia].T @ X[ia]
                for a_ in range(self.n):
                    j = ia & (a2 == a_)
                    if j.any():
                        Amat[sl, a_ * m:(a_ + 1) * m] -= X[j].T @ (disc[j, None] * X2[j])
            self.w = np.linalg.solve(Amat + ridge * np.eye(m * self.n), b)
        return self
