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

    def fit(self, X, A, R, X2, D, gamma, iters=5, epochs=2, batch=512, lr=1e-3, tol=None):
        """fitted Q iteration: targets r + gamma^d max_a' q(s', a') from the current network, then regression.
        Each backup looks one decision further ahead, so `iters` backups only see ~`iters` decisions; with
        tol, back up until the targets change by less than tol (relative mean absolute change), at most
        `iters` backups. Returns the number of backups."""
        y_old = None
        for k in range(iters):
            y = (R + gamma ** D * self.qs(X2).max(1)) / self.Q_SCALE
            if tol is not None and y_old is not None and np.mean(np.abs(y - y_old)) < tol * np.mean(np.abs(y)):
                return k
            y_old = y
            for _ in range(epochs):
                idx = self.rng.permutation(len(X))
                for i in range(0, len(X), batch):
                    j = idx[i:i + batch]
                    self._step(X[j], A[j], y[j], lr)
        return iters

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


class DQNLearner:
    """Deep Q-network (Mnih et al. 2015) with the Double-DQN target (van Hasselt et al. 2016): experience replay,
    a target network copied every TARGET_EVERY transitions (environment steps, as SB3 counts it), Huber loss,
    Adam, gradient-norm clipping; settings
    follow Stable-Baselines3's DQN defaults where they apply (sites/7065/METHODS.md, DQN section). Online: gets
    every transition as it closes (LSTDQPolicy learner hook) and takes a gradient step every TRAIN_EVERY
    transitions once LEARN_START transitions are stored. Semi-MDP target: r + gamma^d q_target(s', argmax q(s'))."""
    HIDDEN = 256
    LR = 1e-4
    BUFFER = 500_000
    BATCH = 64
    LEARN_START = 10_000
    TRAIN_EVERY = 4
    TARGET_EVERY = 10_000              # transitions (= TARGET_EVERY / TRAIN_EVERY gradient steps)
    MAX_GRAD_NORM = 10.0

    def __init__(self, m, n_actions=2, gamma=0.99, reward_scale=0.01, seed=0):
        import torch
        torch.manual_seed(seed)
        torch.set_num_threads(1)
        self.torch, self.gamma, self.rs = torch, gamma, reward_scale
        self.net = self.make(m, n_actions)
        self.target = self.make(m, n_actions)
        self.target.load_state_dict(self.net.state_dict())
        self.opt = torch.optim.Adam(self.net.parameters(), lr=self.LR)
        self.rng = np.random.default_rng(seed)
        self.X = np.zeros((self.BUFFER, m), np.float32)
        self.X2 = np.zeros((self.BUFFER, m), np.float32)
        self.A = np.zeros(self.BUFFER, np.int64)
        self.R = np.zeros(self.BUFFER, np.float32)
        self.Dt = np.zeros(self.BUFFER, np.float32)
        self.n, self.ptr, self.seen, self.steps = 0, 0, 0, 0
        self.losses, self.qmeans = [], []

    @classmethod
    def make(cls, m, n_actions):
        import torch.nn as nn
        return nn.Sequential(nn.Linear(m, cls.HIDDEN), nn.ReLU(), nn.Linear(cls.HIDDEN, cls.HIDDEN), nn.ReLU(),
                             nn.Linear(cls.HIDDEN, n_actions))

    def q(self, x):
        with self.torch.no_grad():
            return self.net(self.torch.as_tensor(x, dtype=self.torch.float32)).numpy()

    def update(self, x, a, r, x2, d):
        i = self.ptr
        self.X[i], self.A[i], self.R[i], self.X2[i], self.Dt[i] = x, a, self.rs * r, x2, d
        self.ptr = (self.ptr + 1) % self.BUFFER
        self.n = min(self.n + 1, self.BUFFER)
        self.seen += 1
        if self.seen >= self.LEARN_START and self.seen % self.TRAIN_EVERY == 0:
            self._learn()

    def _learn(self):
        torch = self.torch
        j = self.rng.integers(0, self.n, self.BATCH)
        x, x2 = torch.from_numpy(self.X[j]), torch.from_numpy(self.X2[j])
        a, r, d = torch.from_numpy(self.A[j]), torch.from_numpy(self.R[j]), torch.from_numpy(self.Dt[j])
        with torch.no_grad():
            a2 = self.net(x2).argmax(1, keepdim=True)
            y = r + self.gamma ** d * self.target(x2).gather(1, a2).squeeze(1)
        qa = self.net(x).gather(1, a[:, None]).squeeze(1)
        loss = torch.nn.functional.smooth_l1_loss(qa, y)
        self.opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.net.parameters(), self.MAX_GRAD_NORM)
        self.opt.step()
        self.steps += 1
        self.losses.append(float(loss))
        self.qmeans.append(float(qa.mean()))
        if self.steps % (self.TARGET_EVERY // self.TRAIN_EVERY) == 0:
            self.target.load_state_dict(self.net.state_dict())

    def save(self, path):
        self.torch.save(self.net.state_dict(), path)

    @classmethod
    def load_qfun(cls, path, m, n_actions=2):
        import torch
        torch.set_num_threads(1)
        net = cls.make(m, n_actions)
        net.load_state_dict(torch.load(path, weights_only=True))
        net.eval()

        def qfun(x):
            with torch.no_grad():
                return net(torch.as_tensor(x, dtype=torch.float32)).numpy()
        return qfun
