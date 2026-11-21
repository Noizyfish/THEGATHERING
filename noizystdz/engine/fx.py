"""Real-time character voice FX, block-based, numpy only.

A *character* is a preset: pitch shift (semitones), formant tilt, drive, a tiny room, gate, gain.
Applied per block on the live track and sent to the return device so the actor hears the
character while speaking (that's the interactive part). Deliberately simple and latency-safe
(≈ block_size / sample_rate). Presets live in ../presets/*.json and character sheets attach one.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np


@dataclass
class Preset:
    name: str
    pitch_semitones: float = 0.0
    formant_tilt_db: float = 0.0     # +: brighter/smaller, -: darker/bigger
    drive: float = 0.0               # 0..1 soft saturation
    room: float = 0.0                # 0..1 tiny feedback-delay room
    gate_db: float = -60.0
    gain_db: float = 0.0
    description: str = ""
    tags: list[str] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> "Preset":
        return cls(**json.loads(path.read_text()))

    @classmethod
    def clean(cls) -> "Preset":
        return cls(name="clean")


def _pitch_shift_block(x: np.ndarray, ratio: float, state: dict) -> np.ndarray:
    """Overlap-free resampling pitch shift with a phase accumulator (robotic-ish but real-time).
    ratio > 1 raises pitch. Keeps a one-block history for continuity."""
    hist = state.get("hist")
    buf = x if hist is None else np.concatenate([hist, x])
    n = len(x)
    start = state.get("phase", float(len(buf) - n))
    idx = start + np.arange(n) * ratio
    idx = np.clip(idx, 0, len(buf) - 1.001)
    i0 = idx.astype(np.int64)
    frac = (idx - i0).astype(np.float32)
    y = buf[i0] * (1 - frac) + buf[i0 + 1] * frac
    # pull the phase back toward the live edge so latency never grows
    end = idx[-1] + ratio
    drift = end - (len(buf) - 1)
    state["phase"] = float(len(buf) - n + (drift * 0.5 if abs(drift) < n else 0.0)) - n
    state["phase"] = max(0.0, min(state["phase"], float(len(buf) - n)))
    state["hist"] = buf[-n:].copy()
    return y.astype(np.float32)


def _tilt(x: np.ndarray, db: float, sr: int, state: dict) -> np.ndarray:
    """One-pole shelf tilt around ~1 kHz."""
    if abs(db) < 1e-3:
        return x
    a = np.exp(-2 * np.pi * 1000.0 / sr)
    z = state.get("tilt_z", 0.0)
    low = np.empty_like(x)
    for i, v in enumerate(x):
        z = a * z + (1 - a) * v
        low[i] = z
    state["tilt_z"] = float(z)
    high = x - low
    g = 10 ** (db / 20)
    return (low / g + high * g).astype(np.float32) if db > 0 else (low * (1 / g) ** -1 + high * g).astype(np.float32)


def _room(x: np.ndarray, amount: float, sr: int, state: dict) -> np.ndarray:
    if amount <= 0:
        return x
    d = int(0.023 * sr)
    buf = state.setdefault("room_buf", np.zeros(d, dtype=np.float32))
    pos = state.get("room_pos", 0)
    y = np.empty_like(x)
    fb = 0.35 * amount
    for i, v in enumerate(x):
        r = buf[pos]
        out = v + r * amount
        buf[pos] = v + r * fb
        pos = (pos + 1) % d
        y[i] = out
    state["room_pos"] = pos
    return y


class CharacterFX:
    def __init__(self, preset: Preset, sample_rate: int):
        self.preset = preset
        self.sr = sample_rate
        self.state: dict = {}

    def set_preset(self, preset: Preset) -> None:
        self.preset, self.state = preset, {}

    def process(self, x: np.ndarray) -> np.ndarray:
        p = self.preset
        y = x.astype(np.float32, copy=True)
        if 20 * np.log10(np.sqrt(np.mean(y * y)) + 1e-9) < p.gate_db:
            y *= 0.0
        if abs(p.pitch_semitones) > 1e-3:
            y = _pitch_shift_block(y, 2 ** (p.pitch_semitones / 12), self.state)
        y = _tilt(y, p.formant_tilt_db, self.sr, self.state)
        if p.drive > 0:
            k = 1 + p.drive * 20
            y = np.tanh(y * k) / np.tanh(k) if k > 0 else y
        y = _room(y, p.room, self.sr, self.state)
        y *= 10 ** (p.gain_db / 20)
        return np.clip(y, -1.0, 1.0).astype(np.float32)
