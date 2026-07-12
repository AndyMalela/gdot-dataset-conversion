"""Dependency-free progress display + interrupt-safe checkpointing.

No tqdm/pip on this box, so this is a small hand-rolled progress line plus
a pickle checkpoint written atomically (write-to-tmp + os.replace) so a
Ctrl-C or crash mid-write can never leave a corrupt checkpoint. Used by
train_random.py; kept generic so train.py could use it too.
"""

from __future__ import annotations

import os
import pickle
import sys
import time

import numpy as np


def _hms(seconds: float) -> str:
    seconds = int(max(0, seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:d}:{s:02d}"


class Progress:
    """Live one-line progress with an ASCII bar, within-episode sim-time
    fill, per-episode summary, running best, and ETA. Falls back to plain
    per-episode prints when stdout isn't a TTY (e.g. redirected to a file),
    so logs stay readable instead of filling with carriage returns."""

    def __init__(self, total: int, width: int = 26):
        self.total = total
        self.width = width
        self.start = time.time()
        self.done = 0
        self.best = None
        self.tty = sys.stdout.isatty()
        self.ep = 0
        self.day = ""
        self.scale = 0.0
        self.ep_start = time.time()

    def _bar(self, frac: float) -> str:
        frac = min(1.0, max(0.0, frac))
        n = int(frac * self.width)
        return "#" * n + "-" * (self.width - n)

    def start_episode(self, ep: int, day: str, scale: float):
        self.ep, self.day, self.scale = ep, day, scale
        self.ep_start = time.time()
        if not self.tty:
            print(f"[ep {ep}/{self.total}] start day={day} x{scale:.2f}",
                  flush=True)

    def step(self, frac: float, sim_time: float):
        if not self.tty:
            return
        el = time.time() - self.ep_start
        sys.stdout.write(
            f"\r[ep {self.ep}/{self.total}] |{self._bar(frac)}| {frac*100:3.0f}% "
            f"day={self.day} x{self.scale:.2f} sim={_hms(sim_time)} {el:4.0f}s   ")
        sys.stdout.flush()

    def end_episode(self, reward: float, decisions: int, switches: int):
        self.done += 1
        wall = time.time() - self.ep_start
        self.best = reward if self.best is None else max(self.best, reward)
        avg = (time.time() - self.start) / self.done
        eta = avg * (self.total - self.done)
        msg = (f"[ep {self.ep}/{self.total}] |{self._bar(1.0)}| done  "
               f"reward={reward:>12.0f} best={self.best:>12.0f} "
               f"dec={decisions:>6d} sw={switches:>5d} {wall:5.0f}s  "
               f"ETA={_hms(eta)}")
        if self.tty:
            sys.stdout.write("\r" + msg + " " * 6 + "\n")
            sys.stdout.flush()
        else:
            print(msg, flush=True)


def save_checkpoint(path: str, ep: int, w: np.ndarray, experience: list,
                    rng: np.random.Generator, best) -> None:
    """Atomic checkpoint. experience (list of (s,a,r,s2,dur)) is stacked into
    compact float32 arrays; rng bit-generator state is saved so the demand /
    exploration stream resumes identically."""
    if experience:
        S = np.asarray([t[0] for t in experience], dtype=np.float32)
        A = np.asarray([t[1] for t in experience], dtype=np.int16)
        R = np.asarray([t[2] for t in experience], dtype=np.float32)
        S2 = np.asarray([t[3] for t in experience], dtype=np.float32)
        D = np.asarray([t[4] for t in experience], dtype=np.float32)
    else:
        S = A = R = S2 = D = None
    blob = {"ep": ep, "w": np.asarray(w), "S": S, "A": A, "R": R, "S2": S2,
            "D": D, "rng": rng.bit_generator.state, "best": best}
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        pickle.dump(blob, f, protocol=4)
    os.replace(tmp, path)   # atomic on POSIX -> never a half-written checkpoint


def load_checkpoint(path: str):
    """Returns (ep, w, experience, rng_state, best)."""
    with open(path, "rb") as f:
        d = pickle.load(f)
    if d["S"] is None:
        experience = []
    else:
        experience = list(zip(d["S"], d["A"], d["R"], d["S2"], d["D"]))
    return d["ep"], d["w"], experience, d["rng"], d["best"]
