"""Mackie Control Universal over an IAC bus — drives Logic Pro / MainStage transport & channel buttons without window focus.

Standard MCU note map (channel 1, velocity 127 = press, 0 = release):
  rec-arm 0-7 · solo 8-15 · mute 16-23 · select 24-31 · rewind 91 · ffwd 92 · stop 93 · play 94 · record 95 · cycle 86 · click 89 · marker 84
Backends: python-rtmidi (preferred) → `sendmidi` CLI (brew install gbevin/tools/sendmidi) → dry run.
"""
from __future__ import annotations
import shutil
import subprocess
import time

NOTES = {"rewind": 91, "ffwd": 92, "stop": 93, "play": 94, "record": 95, "cycle": 86, "click": 89, "marker": 84,
         "zoom": 100, "scrub": 101, "save": 80, "undo": 81}
BANKS = {"arm": 0, "solo": 8, "mute": 16, "select": 24}


def note_for(action: str) -> int:
    """'play' → 94; 'arm 3' → 2; 'mute 1' → 16."""
    parts = action.split()
    if parts[0] in NOTES and len(parts) == 1:
        return NOTES[parts[0]]
    if parts[0] in BANKS and len(parts) == 2:
        ch = int(parts[1])
        if not 1 <= ch <= 8:
            raise ValueError("MCU channel strips are 1-8 (bank with ffwd/rewind + option for more)")
        return BANKS[parts[0]] + ch - 1
    raise ValueError(f"unknown MCU action {action!r}")


def press(action: str, bus: str = "ENGR MCU", dry_run: bool = False, hold_ms: int = 60) -> str:
    n = note_for(action)
    msgs = [[0x90, n, 127], [0x90, n, 0]]
    if dry_run:
        return f"midi[{bus}] note {n} on/off"
    try:
        import rtmidi  # type: ignore
        out = rtmidi.MidiOut()
        ports = out.get_ports()
        idx = next((i for i, p in enumerate(ports) if bus in p), None)
        if idx is None:
            raise RuntimeError(f"IAC bus {bus!r} not found; ports: {ports}. Create it in Audio MIDI Setup → IAC Driver.")
        out.open_port(idx)
        out.send_message(msgs[0]); time.sleep(hold_ms / 1000); out.send_message(msgs[1])
        out.close_port()
        return f"rtmidi → {bus}: note {n}"
    except ImportError:
        pass
    if shutil.which("sendmidi"):
        subprocess.run(["sendmidi", "dev", bus, "on", str(n), "127"], check=True)
        time.sleep(hold_ms / 1000)
        subprocess.run(["sendmidi", "dev", bus, "off", str(n), "0"], check=True)
        return f"sendmidi → {bus}: note {n}"
    raise RuntimeError("no MIDI backend: pip install python-rtmidi  or  brew install gbevin/tools/sendmidi")
