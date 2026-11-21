#!/usr/bin/env python3
"""ENGR — the engineer in the room. Named for R.K. Plowman, civil engineer: precise, methodical, no ambiguity.

    engr logic play|stop|record|arm 1|mute 2|marker|save|bounce|new-audio-track|import <file>
    engr logic import-session <noizystdz-session-dir>     → FCPXML → Logic Pro
    engr fcp import-session <session-dir>                 → same XML into Final Cut Pro
    engr app <App> activate|quit|open <file>
    engr hijack start|stop <Session>                      → Audio Hijack
    engr shortcut <Name> [input]
    engr do "<natural language>"                          → router (Claude if ANTHROPIC_API_KEY, else rules)
    engr home scene <name> | home <accessory> <state> | home install | home triggers   → ALL HomeKit via Shortcuts
    engr talon                                            → write ~/.talon/user/engr/engr.talon (every action spoken)
    engr doctor
Add --dry-run anywhere to print what would run.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from drivers import applescript, homekit, keycmd, mcu, shortcuts  # noqa: E402
from logic import fcpxml  # noqa: E402

APPS = json.loads((HERE / "apps.json").read_text())
KEYS = json.loads((HERE / "logic" / "keycmds.json").read_text())
BUS = APPS.get("iacBus", "ENGR MCU")

# Logic actions: prefer MCU (focus-free), fall back to key commands.
LOGIC_MCU = {"play": "play", "stop": "stop", "record": "record", "rewind": "rewind", "ffwd": "ffwd", "cycle": "cycle", "click": "click", "marker": "marker", "save": "save", "undo": "undo"}
LOGIC_KEYS = {"go-to-start": "go_to_start", "new-audio-track": "new_audio_track", "bounce": "bounce", "save-as": "save_as", "new-project": "new_project", "strip-silence": "strip_silence", "mixer": "mixer", "capture": "capture_recording", "zoom-fit": "zoom_fit", "import-audio": "import_audio", "metronome": "metronome"}


def logic(action: str, args: list[str], dry: bool) -> str:
    if action in LOGIC_MCU:
        try:
            return mcu.press(LOGIC_MCU[action], BUS, dry)
        except RuntimeError as e:
            if action in ("play", "stop", "record", "cycle", "metronome") and action in ("play", "stop", "record", "cycle"):
                key = {"play": "play_stop", "stop": "stop", "record": "record", "cycle": "cycle"}[action]
                return f"(mcu unavailable: {e}) → " + keycmd.keystroke("Logic Pro", KEYS[key], dry)
            raise
    if action in ("arm", "mute", "solo", "select"):
        return mcu.press(f"{action} {args[0]}", BUS, dry)
    if action in LOGIC_KEYS:
        return keycmd.keystroke("Logic Pro", KEYS[LOGIC_KEYS[action]], dry)
    if action == "import":
        return applescript.open_file("Logic Pro", str(Path(args[0]).resolve()), dry)
    if action == "import-session":
        xml = fcpxml.build(Path(args[0]))
        res = applescript.activate("Logic Pro", dry)
        res += "\n" + keycmd.keystroke("Logic Pro", KEYS["import_fcpxml"], dry)
        return f"{xml}\n{res}\n→ in the import dialog choose {xml.name} (Logic has no API to pass the path). Tracks: one per WAV, markers per line."
    raise SystemExit(f"unknown logic action {action!r}. Known: {sorted(LOGIC_MCU | LOGIC_KEYS | {'arm':0,'mute':0,'solo':0,'select':0,'import':0,'import-session':0})}")


def fcp(action: str, args: list[str], dry: bool) -> str:
    if action == "import-session":
        xml = fcpxml.build(Path(args[0]))
        return f"{xml}\n" + applescript.open_file("Final Cut Pro", str(xml), dry)
    raise SystemExit("fcp: import-session <session-dir>")


def app(name: str, action: str, args: list[str], dry: bool) -> str:
    if name not in APPS["apps"]:
        print(f"note: {name!r} not in apps.json — using generic drivers", file=sys.stderr)
    if action == "activate":
        return applescript.activate(name, dry)
    if action == "quit":
        return applescript.quit_app(name, dry)
    if action == "open":
        return applescript.open_file(name, str(Path(args[0]).resolve()), dry)
    if action == "menu":
        return keycmd.menu(name, args, dry)
    if action == "key":
        spec = {"key": args[0], "mods": args[1:]}
        return keycmd.keystroke(name, spec, dry)
    raise SystemExit("app <App> activate|quit|open <file>|menu <Menu> <Item>…|key <k> [mods…]")


def hijack(action: str, session: str, dry: bool) -> str:
    verb = {"start": "start", "stop": "stop"}[action]
    return applescript.run(f'tell application "Audio Hijack" to {verb} session named "{session}"', dry)


RULES = [
    (("record", "roll", "rolling"), ["logic", "record"]),
    (("stop",), ["logic", "stop"]),
    (("play", "playback"), ["logic", "play"]),
    (("marker", "mark that", "flag"), ["logic", "marker"]),
    (("save",), ["logic", "save"]),
    (("bounce", "export mix"), ["logic", "bounce"]),
    (("new track", "new audio track", "add a track"), ["logic", "new-audio-track"]),
    (("safety", "start safety"), ["hijack", "start", "Safety"]),
    (("stop safety",), ["hijack", "stop", "Safety"]),
    (("on air",), ["home", "onair", "red"]),
    (("off air",), ["home", "onair", "off"]),
    (("lock the door", "lock up"), ["home", "door", "lock"]),
    (("wrap", "we're done", "that's a wrap"), ["home", "scene", "wrap"]),
    (("sleep scene", "lina time"), ["home", "scene", "sleep"]),
]


def route(text: str) -> list[str] | None:
    t = text.lower().strip()
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            import anthropic  # type: ignore
            client = anthropic.Anthropic()
            msg = client.messages.create(model="claude-sonnet-4-5", max_tokens=100, system="You are ENGR, a studio engineer. Map the request to exactly one ENGR CLI command from: logic play|stop|record|marker|save|bounce|new-audio-track|arm N|mute N|solo N|select N|import-session DIR; hijack start|stop NAME; app NAME activate|quit; shortcut NAME. Reply with the command only, no prose. If impossible reply NONE.", messages=[{"role": "user", "content": text}])
            out = msg.content[0].text.strip()
            return None if out == "NONE" else out.split()
        except Exception as e:  # fall through to rules
            print(f"(claude unavailable: {e}) → rules", file=sys.stderr)
    # longest matching phrase wins ("stop safety" beats "safety" beats "stop")
    best = None
    for keys, cmd in RULES:
        for k in keys:
            if k in t and (best is None or len(k) > len(best[0])):
                best = (k, cmd)
    if best:
        return best[1]
    for n in APPS["apps"]:
        if n.lower() in t:
            return ["app", n, "quit" if "quit" in t or "close" in t else "activate"]
    return None


TALON = """# ENGR — spoken studio control (generated by `engr talon`). Requires Talon.
os: mac
-
engr roll: user.system_command("{engr} logic record")
engr stop: user.system_command("{engr} logic stop")
engr play: user.system_command("{engr} logic play")
engr mark: user.system_command("{engr} logic marker")
engr save: user.system_command("{engr} logic save")
engr bounce: user.system_command("{engr} logic bounce")
engr new track: user.system_command("{engr} logic new-audio-track")
engr arm <number_small>: user.system_command("{engr} logic arm {{number_small}}")
engr mute <number_small>: user.system_command("{engr} logic mute {{number_small}}")
engr solo <number_small>: user.system_command("{engr} logic solo {{number_small}}")
engr safety on: user.system_command("{engr} hijack start Safety")
engr safety off: user.system_command("{engr} hijack stop Safety")
engr studio: user.system_command("open http://127.0.0.1:9790")
engr on air: user.system_command("{engr} home onair red")
engr off air: user.system_command("{engr} home onair off")
engr scene <user.text>: user.system_command("{engr} home scene {{text}}")
engr lock up: user.system_command("{engr} home door lock")
engr <user.text>: user.system_command("{engr} do '{{text}}'")
"""


def home(rest: list[str], dry: bool) -> str:
    sub = rest[0] if rest else "install"
    if sub == "install":
        return homekit.install_plan()
    if sub == "triggers":
        return "\n".join(f"• {t['when']} → {t['effect']}" for t in homekit.HOME["triggers"])
    if sub == "scene":
        return homekit.scene(rest[1], dry)
    if sub == "hap":
        return (HERE / "logic" / "hap_accessory.py").read_text()
    return homekit.accessory(sub, " ".join(rest[1:]), dry)


def talon(dry: bool) -> str:
    dest = Path.home() / ".talon" / "user" / "engr" / "engr.talon"
    body = TALON.format(engr=str(HERE / "engr"))
    if dry:
        return body
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(body)
    return f"wrote {dest}"


def doctor() -> int:
    ok = True
    def line(good, label, hint=""):
        nonlocal ok
        ok &= bool(good)
        print(f"{'✅' if good else '❌'} {label}{'  → ' + hint if (hint and not good) else ''}")
    mac = sys.platform == "darwin"
    line(mac, "macOS", "ENGR drives macOS apps; on other OSes everything is --dry-run")
    line(shutil.which("osascript"), "osascript", "macOS only")
    try:
        import rtmidi  # type: ignore
        ports = rtmidi.MidiOut().get_ports()
        line(any(BUS in p for p in ports), f"IAC bus {BUS!r}", f"Audio MIDI Setup → IAC Driver → add bus {BUS!r}; ports seen: {ports}")
    except ImportError:
        line(shutil.which("sendmidi"), "MIDI backend (python-rtmidi or sendmidi)", "pip install python-rtmidi")
    for a in ("Logic Pro", "Final Cut Pro", "Audio Hijack", "Loopback", "Blender", "Talon"):
        line((Path("/Applications") / f"{a}.app").exists() if mac else None, a, "not installed (ok if unused)")
    line(shutil.which("shortcuts"), "shortcuts CLI", "macOS 12+")
    line(os.environ.get("ANTHROPIC_API_KEY"), "ANTHROPIC_API_KEY (natural-language routing)", "rules-only routing without it")
    print("\nLogic Pro one-time: Control Surfaces ▸ Setup ▸ Install ▸ Mackie Designs ▸ Mackie Control ▸ Add; set input+output port to the IAC bus. Grant Accessibility to Terminal for key commands.")
    return 0 if ok else 1


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    dry = "--dry-run" in argv
    argv = [a for a in argv if a != "--dry-run"]
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(__doc__); return 0
    cmd, rest = argv[0], argv[1:]
    try:
        if cmd == "logic":
            out = logic(rest[0], rest[1:], dry)
        elif cmd == "fcp":
            out = fcp(rest[0], rest[1:], dry)
        elif cmd == "app":
            out = app(rest[0], rest[1], rest[2:], dry)
        elif cmd == "hijack":
            out = hijack(rest[0], rest[1], dry)
        elif cmd == "shortcut":
            out = shortcuts.run(rest[0], rest[1] if len(rest) > 1 else None, dry)
        elif cmd == "do":
            r = route(" ".join(rest))
            if not r:
                print("ENGR: no mapping for that. Try `engr help`.", file=sys.stderr); return 2
            print(f"→ engr {' '.join(r)}", file=sys.stderr)
            return main(r + (["--dry-run"] if dry else []))
        elif cmd == "home":
            out = home(rest, dry)
        elif cmd == "talon":
            out = talon(dry)
        elif cmd == "doctor":
            return doctor()
        else:
            print(f"unknown command {cmd!r}\n{__doc__}", file=sys.stderr); return 2
    except (IndexError, KeyError):
        print(__doc__, file=sys.stderr); return 2
    if out:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
