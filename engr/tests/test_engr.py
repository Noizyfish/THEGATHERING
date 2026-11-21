import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE / "osc"))
import engr  # noqa: E402
from drivers import mcu, keycmd  # noqa: E402
from logic import fcpxml  # noqa: E402
from midi14 import cc14, pitchbend14, split14, join14, to14, db_to_fader  # noqa: E402
from bridge import decode, handle  # noqa: E402


def test_mcu_note_map():
    assert mcu.note_for("play") == 94 and mcu.note_for("record") == 95
    assert mcu.note_for("arm 1") == 0 and mcu.note_for("mute 8") == 23 and mcu.note_for("select 3") == 26
    for bad in ("arm 9", "dance"):
        try:
            mcu.note_for(bad); assert False
        except ValueError:
            pass


def test_midi14():
    for v in (0, 1, 127, 128, 8192, 16383):
        assert join14(*split14(v)) == v
    assert to14(1.0) == 16383 and to14(0.5) == 8192
    assert cc14(1, 7, 0.75) == [[176, 7, 95], [176, 39, 127]]
    assert pitchbend14(9, 1.0) == [0xE8, 127, 127]
    assert db_to_fader(0) == 0.75 and db_to_fader(-90) == 0.0 and 0.49 < db_to_fader(-10) < 0.51


def test_keycmd_dry_run():
    s = keycmd.keystroke("Logic Pro", {"key": "b", "mods": ["command"]}, dry_run=True)
    assert 'keystroke "b" using {command down}' in s and 'process "Logic Pro"' in s
    m = keycmd.menu("Logic Pro", ["File", "Import", "Final Cut Pro XML…"], dry_run=True)
    assert 'menu item "Final Cut Pro XML…" of menu 1 of menu item "Import" of menu 1 of menu bar item "File"' in m


def test_router_rules(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert engr.route("ok roll it") == ["logic", "record"]
    assert engr.route("stop safety") == ["hijack", "stop", "Safety"]
    assert engr.route("we're on air") == ["home", "onair", "red"]
    assert engr.route("open blender") == ["app", "Blender", "activate"]
    assert engr.route("make me a sandwich") is None


def test_osc_decode_and_bridge():
    pkt = b"/noizystdz/voice\0\0\0\0,s\0\0anim-01\0"
    assert decode(pkt) == ("/noizystdz/voice", ["anim-01"])
    assert handle("/noizystdz/voice", ["anim-01"], dry=True) == "POST /voice anim-01"
    assert handle("/engr/home/scene", ["record", 1], dry=True).endswith("engr home scene record")
    assert handle("/fx/pitch", [16383], dry=True) == "POST /fx {'pitch': 1.0}"


def test_fcpxml_from_session(tmp_path):
    sd = tmp_path / "s1"; (sd / "tracks").mkdir(parents=True)
    sr = 48000
    (sd / "session.json").write_text(json.dumps({"session": "s1", "sampleRate": sr}))
    for name, secs in (("RSP", 3.0), ("LINA_SRC", 2.0), ("GUEST_B", 0.0)):
        sf.write(str(sd / "tracks" / f"{name}.wav"), np.zeros((int(secs * sr), 2), dtype=np.float32), sr)
    (sd / "transcript.jsonl").write_text(json.dumps({"track": "RSP", "speaker": "RSP", "t0": 0.5, "t1": 1.5, "text": "Hoist the colours", "character": "anim-01", "file": "tracks/RSP.wav"}) + "\n")
    out = fcpxml.build(sd)
    x = out.read_text()
    assert x.startswith('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE fcpxml>') and 'version="1.9"' in x
    assert x.count("<asset ") == 2 and "GUEST_B" not in x            # empty track skipped
    assert 'lane="1"' in x and 'name="LINA_SRC"' in x
    assert f'start="{int(0.5*sr)}/{sr}s"' in x and "RSP as anim-01: Hoist the colours" in x
    assert 'duration="144000/48000s"' in x


def test_osc_session_builder():
    r = subprocess.run([sys.executable, str(HERE / "osc" / "build_session.py")], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    d = json.loads((HERE / "osc" / "noizystdz.json").read_text())
    tabs = {t["label"]: t["widgets"] for t in d["widgets"]}
    faders = [w for w in tabs["MIXER (MCU 14-bit)"] if w["type"] == "fader"]
    assert len(faders) == 6 and all(w["range"]["max"] == 16383 and w["address"] == "/pitch" for w in faders)
    knobs = [w for w in tabs["CHARACTER FX (14-bit CC)"] if w["type"] == "knob"]
    assert all(w["address"] == "/control14" and w["range"]["max"] == 16383 for w in knobs)
    assert len([w for w in tabs["50 VOICES"]]) == 50
