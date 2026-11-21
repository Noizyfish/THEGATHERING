"""Generate the Open Stage Control session (JSON) for NOIZYSTDZ: 8 MCU faders (14-bit pitch bend) + 14-bit CC macro knobs
for character FX, transport, per-track arm/mute/solo, the 50-voice grid, consent buttons, ON AIR — all from channels.json,
roster.json and apps.json so the surface never drifts from the rig. Output: engr/osc/noizystdz.json → open in O-S-C."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))

MIDI_TARGET = "midi:engr"          # O-S-C midi device alias (see osc/README.md)
ENGINE_TARGET = "127.0.0.1:9792"   # OSC → engine bridge (osc/bridge.py)


def w(type_, id_, **kw):
    d = {"type": type_, "id": id_, "label": kw.pop("label", id_)}
    d.update(kw)
    return d


def fader_mcu(i: int, name: str, x: int):
    """MCU fader i (1-8) = pitch bend on channel i, 14-bit."""
    return w("fader", f"fader_{i}", label=name, left=x, top=60, width=70, height=300, range={"min": 0, "max": 16383}, default=12288,
             address="/pitch", preArgs=[i - 1], target=[MIDI_TARGET], decimals=0, doubleTap=True, design="compact", css=":host{--color-fill:#06d6a0}")


def knob14(id_, label, cc, x, y, color="#ffd166"):
    """14-bit CC knob: O-S-C's /control14 sends MSB on cc, LSB on cc+32 when the midi device is created with 14-bit enabled."""
    return w("knob", id_, label=label, left=x, top=y, width=90, height=110, range={"min": 0, "max": 16383}, default=8192, decimals=0,
             address="/control14", preArgs=[0, cc], target=[MIDI_TARGET], css=f":host{{--color-fill:{color}}}")


def button(id_, label, address, args, x, y, w_=90, h=44, color="#2a2a3a", target=None, mode="push"):
    return w("button", id_, label=label, left=x, top=y, width=w_, height=h, mode=mode, address=address, preArgs=args, target=[target or ENGINE_TARGET], on=1, off=0, css=f":host{{--color-widget:{color}}}")


def note_button(id_, label, note, x, y, color="#2a2a3a", w_=70):
    return w("button", id_, label=label, left=x, top=y, width=w_, height=40, mode="push", address="/note", preArgs=[0, note], target=[MIDI_TARGET], on=127, off=0, css=f":host{{--color-widget:{color}}}")


def build() -> dict:
    ch = json.loads((ROOT / "noizystdz" / "channels.json").read_text())
    roster = json.loads((ROOT / "noizystdz" / "characters" / "roster.json").read_text())
    home = json.loads((HERE.parent / "home.json").read_text())
    tracks = [t for t in ch["tracks"] if t["kind"] in ("human", "synthetic")][:8]

    mixer = []
    for i, t in enumerate(tracks, 1):
        x = 20 + (i - 1) * 110
        mixer.append(fader_mcu(i, t["id"], x))
        mixer.append(note_button(f"arm_{i}", "REC", 0 + i - 1, x, 370, "#e63946"))
        mixer.append(note_button(f"solo_{i}", "SOLO", 8 + i - 1, x, 414, "#ffd166"))
        mixer.append(note_button(f"mute_{i}", "MUTE", 16 + i - 1, x, 458, "#457b9d"))
        mixer.append(note_button(f"sel_{i}", "SEL", 24 + i - 1, x, 502, "#2a2a3a"))
    tx = 20
    for lbl, note, col in (("◀◀", 91, "#2a2a3a"), ("▶▶", 92, "#2a2a3a"), ("■", 93, "#2a2a3a"), ("▶", 94, "#06d6a0"), ("●", 95, "#e63946"), ("CYC", 86, "#2a2a3a"), ("MRK", 84, "#2a2a3a")):
        mixer.append(note_button(f"tr_{note}", lbl, note, tx, 560, col, 84)); tx += 94

    fx = [knob14("fx_pitch", "PITCH ±12", 1, 20, 60), knob14("fx_formant", "FORMANT", 2, 130, 60), knob14("fx_drive", "DRIVE", 3, 240, 60), knob14("fx_room", "ROOM", 4, 350, 60), knob14("fx_gain", "GAIN", 5, 460, 60),
          knob14("fx_gate", "GATE", 6, 20, 190, "#8ecae6"), knob14("fx_mix", "DRY/WET", 7, 130, 190, "#8ecae6")]
    presets = sorted(p.stem for p in (ROOT / "noizystdz" / "presets").glob("*.json"))
    for i, p in enumerate(presets):
        fx.append(button(f"preset_{p}", p.upper(), "/noizystdz/preset", [p], 20 + i * 100, 330, color="#3a3a5a"))

    voices = []
    for i, v in enumerate(roster["voices"]):
        col = {"animation": "#e76f51", "narration": "#457b9d", "sleep": "#6d597a"}[v["category"]]
        voices.append(button(f"voice_{v['id']}", f"{i+1}. {v['name']}", "/noizystdz/voice", [v["id"]], 20 + (i % 5) * 190, 60 + (i // 5) * 56, 180, 48, col))

    room = []
    for i, (n, s) in enumerate(home["scenes"].items()):
        room.append(button(f"scene_{n}", s["homeScene"].replace("Studio ", "").upper(), "/engr/home/scene", [n], 20 + (i % 4) * 150, 60 + (i // 4) * 60, 140, 52, "#264653"))
    room.append(button("onair_red", "ON AIR", "/engr/home", ["onair", "red"], 20, 200, 140, 80, "#e63946"))
    room.append(button("onair_off", "OFF AIR", "/engr/home", ["onair", "off"], 170, 200, 140, 80, "#2a2a3a"))
    room.append(button("door_lock", "LOCK", "/engr/home", ["door", "lock"], 320, 200, 140, 80, "#264653"))
    room.append(button("safety", "SAFETY REC", "/engr/hijack", ["start", "Safety"], 470, 200, 140, 80, "#9d0208"))
    for i, spk in enumerate(("RSP", "LINA_SRC", "GUEST_B", "GUEST_C")):
        room.append(button(f"consent_{spk}", f"CONSENT {spk}", "/noizystdz/consent", [spk], 20 + i * 150, 300, 140, 52, "#06d6a0"))

    return {"version": "1.26.0", "type": "root", "id": "root", "label": "NOIZYSTDZ", "css": "body{background:#0b0b10}", "widgets": [
        {"type": "tab", "id": "mixer", "label": "MIXER (MCU 14-bit)", "widgets": mixer},
        {"type": "tab", "id": "fx", "label": "CHARACTER FX (14-bit CC)", "widgets": fx},
        {"type": "tab", "id": "voices", "label": "50 VOICES", "widgets": voices},
        {"type": "tab", "id": "room", "label": "ROOM · HOMEKIT · CONSENT", "widgets": room},
    ]}


if __name__ == "__main__":
    out = HERE / "noizystdz.json"
    out.write_text(json.dumps(build(), indent=1))
    print(out)
