"""14-bit MIDI helpers (16 384 steps). Pure functions; tested.

Two ways to carry 14-bit on MIDI 1.0, both used here:
  • CC pair   — CC n (MSB, 0-31) + CC n+32 (LSB). Order: MSB first, LSB second (MIDI spec; Logic 'Learn' sees both).
  • Pitch bend — 14-bit natively (LSB, MSB), per channel. Mackie Control uses this for its 9 faders (ch 1-8 + master on 9).
Open Stage Control sends 14-bit CC itself when a widget's MIDI target is '/control14' (address `/control14`), or we build the
pairs here when bridging OSC floats → MIDI.
"""
from __future__ import annotations

MAX14 = 16383


def clamp01(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else float(x)


def to14(x: float) -> int:
    """0.0..1.0 → 0..16383"""
    return int(round(clamp01(x) * MAX14))


def from14(v: int) -> float:
    return max(0, min(MAX14, int(v))) / MAX14


def split14(v: int) -> tuple[int, int]:
    """→ (msb, lsb), each 0..127"""
    v = max(0, min(MAX14, int(v)))
    return (v >> 7) & 0x7F, v & 0x7F


def join14(msb: int, lsb: int) -> int:
    return ((msb & 0x7F) << 7) | (lsb & 0x7F)


def cc14(channel: int, cc: int, x: float) -> list[list[int]]:
    """14-bit CC pair for value x∈[0,1]. channel 1-16, cc 0-31. Returns [[status, cc, msb], [status, cc+32, lsb]]."""
    if not 0 <= cc <= 31:
        raise ValueError("14-bit CC MSB number must be 0-31 (LSB is cc+32)")
    st = 0xB0 | ((channel - 1) & 0x0F)
    msb, lsb = split14(to14(x))
    return [[st, cc, msb], [st, cc + 32, lsb]]


def pitchbend14(channel: int, x: float) -> list[int]:
    """Mackie fader position as pitch bend: [status, lsb, msb]."""
    st = 0xE0 | ((channel - 1) & 0x0F)
    msb, lsb = split14(to14(x))
    return [st, lsb, msb]


def db_to_fader(db: float) -> float:
    """Logic/MCU fader taper approximation: +6 dB = 1.0, 0 dB ≈ 0.75, -∞ = 0."""
    if db <= -90:
        return 0.0
    if db >= 6:
        return 1.0
    if db >= -10:
        return 0.75 + (db / 6.0) * 0.25 if db >= 0 else 0.75 + db * 0.025
    # -10 → 0.5 ; -30 → 0.25 ; -60 → 0.1 ; linear between
    pts = [(-10, 0.5), (-30, 0.25), (-60, 0.1), (-90, 0.0)]
    for (d1, f1), (d2, f2) in zip(pts, pts[1:]):
        if d2 <= db <= d1:
            return f2 + (f1 - f2) * (db - d2) / (d1 - d2)
    return 0.0
