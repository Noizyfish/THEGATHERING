"""Energy VAD with hangover — dependency-free, good enough to cut speech into STT segments.
Swap for silero-vad when you want it (same interface: feed blocks, get (start, end) sample ranges)."""
from __future__ import annotations

import numpy as np


def rms_db(x: np.ndarray) -> float:
    r = float(np.sqrt(np.mean(np.square(x), dtype=np.float64))) if x.size else 0.0
    return 20 * np.log10(r + 1e-9)


class EnergyVAD:
    def __init__(self, sample_rate: int, threshold_db: float = -42.0, hangover_ms: int = 350, min_sec: float = 0.6, max_sec: float = 20.0):
        self.sr = sample_rate
        self.threshold = threshold_db
        self.hang_blocks = None
        self.hangover_ms = hangover_ms
        self.min_samples = int(min_sec * sample_rate)
        self.max_samples = int(max_sec * sample_rate)
        self.active = False
        self.start = 0
        self.pos = 0
        self.quiet = 0

    def feed(self, block: np.ndarray) -> list[tuple[int, int]]:
        """block: mono float32. Returns finished (start, end) sample ranges."""
        if self.hang_blocks is None:
            self.hang_blocks = max(1, int(self.hangover_ms / 1000 * self.sr / max(1, len(block))))
        out: list[tuple[int, int]] = []
        loud = rms_db(block) > self.threshold
        if loud:
            if not self.active:
                self.active, self.start = True, self.pos
            self.quiet = 0
        elif self.active:
            self.quiet += 1
            if self.quiet >= self.hang_blocks:
                end = self.pos + len(block)
                if end - self.start >= self.min_samples:
                    out.append((self.start, end))
                self.active = False
        if self.active and self.pos + len(block) - self.start >= self.max_samples:
            out.append((self.start, self.pos + len(block)))
            self.start = self.pos + len(block)
        self.pos += len(block)
        return out

    def flush(self) -> list[tuple[int, int]]:
        if self.active and self.pos - self.start >= self.min_samples:
            self.active = False
            return [(self.start, self.pos)]
        self.active = False
        return []
