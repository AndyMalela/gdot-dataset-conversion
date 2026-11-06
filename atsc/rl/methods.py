"""Learners other than LSTDQ, on the same controller (atsc/rl/agent.py LSTDQPolicy, v2 state and action): only
the way the decision rule is learnt differs (sites/7065/METHODS.md, fixed before training).

  OnlineLinearQ   linear Q, Watkins Q-learning one transition at a time (semi-gradient, normalised step);
                  the classic online form of linear RL signal control
  MLPQ            neural fitted Q iteration (Riedmiller 2005): same data loop as LSPI, the least-squares fit
                  replaced by a 2-hidden-layer network; tests what the linear form costs
  ars_qfun        linear policy found by augmented random search (Mania et al. 2018) on the delay itself, no
                  value function: end the green when theta . x > 0
"""
from __future__ import annotations

import numpy as np


class OnlineLinearQ:
    """q(s, a) = w_a . x;  w_a += alpha (r + gamma^d max_a' q(s', a') - q(s, a)) x / (x . x)."""
    def __init__(self, m, n_actions=2, alpha=0.05, gamma=0.99, reward_scale=0.01, seed=0):
        self.m, self.n, self.alpha, self.gamma, self.rs = m, n_actions, alpha, gamma, reward_scale
        self.w = np.random.default_rng(seed).uniform(-0.03, 0.03, (n_actions, m))

    def q(self, x):
        return self.w @ x

    def update(self, x, a, r, x2, d):
        td = self.rs * r + self.gamma ** d * np.max(self.w @ x2) - self.w[a] @ x
        self.w[a] += self.alpha * td * x / max(1e-9, x @ x)


class MLPQ:
    """q(s, .) = Q_SCALE * f(x), f: m -> H -> H -> n_actions (ReLU), fitted by Adam on squared TD targets."""
    Q_SCALE = 50.0                     # |q| ~ reward per s (~0.5 after /100) / (1 - gamma); keeps f's outputs ~1

    def __init__(self, m, n_actions=2, hidden=64, seed=0):
        rng = np.random.default_rng(seed)
        sizes = [m, hidden, hidden, n_actions]
        self.W = [rng.normal(0, np.sqrt(2 / a), (a, b)) for a, b in zip(sizes[:-1], sizes[1:])]
        self.W[-1][:] = 0.0
        self.b = [np.zeros(b) for b in sizes[1:]]
        self.rng = rng
        self.opt = [[np.zeros_like(p), np.zeros_like(p)] for p in self.W + self.b]
        self.t = 0

    def forward(self, X):
        h = [X]
        for i, (W, b) in enumerate(zip(self.W, self.b)):
            z = h[-1] @ W + b
            h.append(np.maximum(z, 0) if i < len(self.W) - 1 else z)
        return h

    def q(self, x):
        return self.Q_SCALE * self.forward(np.atleast_2d(x))[-1][0]

    def qs(self, X, batch=65536):
        return np.concatenate([self.Q_SCALE * self.forward(X[i:i + batch])[-1] for i in range(0, len(X), batch)])

    def _step(self, X, A, y, lr):
        h = self.forward(X)
        g = np.zeros_like(h[-1])
        rows = np.arange(len(X))
        g[rows, A] = 2 * (h[-1][rows, A] - y) / len(X)
        grads_W, grads_b = [], []
        for i in range(len(self.W) - 1, -1, -1):
            grads_W.insert(0, h[i].T @ g)
            grads_b.insert(0, g.sum(0))
            if i:
                g = (g @ self.W[i].T) * (h[i] > 0)
        self.t += 1
        b1, b2 = 0.9, 0.999
        for p, gr, st in zip(self.W + self.b, grads_W + grads_b, self.opt):
            st[0] = b1 * st[0] + (1 - b1) * gr
            st[1] = b2 * st[1] + (1 - b2) * gr * gr
            p -= lr * (st[0] / (1 - b1 ** self.t)) / (np.sqrt(st[1] / (1 - b2 ** self.t)) + 1e-8)

    def fit(self, X, A, R, X2, D, gamma, iters=5, epochs=2, batch=512, lr=1e-3):
        """fitted Q iteration: targets r + gamma^d max_a' q(s', a') from the current network, then regression."""
        for _ in range(iters):
            y = (R + gamma ** D * self.qs(X2).max(1)) / self.Q_SCALE
            for _ in range(epochs):
                idx = self.rng.permutation(len(X))
                for i in range(0, len(X), batch):
                    j = idx[i:i + batch]
                    self._step(X[j], A[j], y[j], lr)
        return self

    def state(self):
        return {**{f"W{i}": W for i, W in enumerate(self.W)}, **{f"b{i}": b for i, b in enumerate(self.b)}}

    @classmethod
    def load(cls, path):
        z = np.load(path)
        net = cls.__new__(cls)
        net.W = [z[f"W{i}"] for i in range(3)]
        net.b = [z[f"b{i}"] for i in range(3)]
        return net


def ars_qfun(theta):
    """ARS linear policy as action values: end (1) when theta . x > 0, else extend (0)."""
    return lambda x: np.array([0.0, theta @ x])
