"""HomeKit for the studio.

There is no public HomeKit API on macOS, so ENGR uses the two sanctioned bridges, both of which work with *all*
HomeKit accessories (lights, plugs, locks, sensors, thermostats, cameras, speakers, Matter devices):

  1. Shortcuts: a Shortcut per scene/accessory action ("Control Home" action) → `shortcuts run "<name>"`.
     `engr home install` prints the exact list of Shortcuts to create (names are the contract; one tap each in Shortcuts.app).
  2. Home automations → webhooks: Home.app can run a Shortcut when a sensor fires; that Shortcut POSTs to the NOIZYSTDZ hub
     (`/home/event`), so the room drives the studio too (door opens → Safety recording; motion in booth → "someone's in").

Optional backend 3: a Homebridge/HAP-python 'ENGR' accessory exposing Logic transport as switches — see HOMEKIT.md.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import shortcuts

HERE = Path(__file__).resolve().parent.parent
HOME = json.loads((HERE / "home.json").read_text())


def scene(name: str, dry_run: bool = False) -> str:
    s = HOME["scenes"].get(name)
    if not s:
        raise SystemExit(f"unknown scene {name!r}; known: {sorted(HOME['scenes'])}")
    return shortcuts.run(s["shortcut"], dry_run=dry_run)


def accessory(name: str, state: str, dry_run: bool = False) -> str:
    a = HOME["accessories"].get(name)
    if not a:
        raise SystemExit(f"unknown accessory {name!r}; known: {sorted(HOME['accessories'])}")
    if state not in a["states"]:
        raise SystemExit(f"{name}: states are {sorted(a['states'])}")
    return shortcuts.run(f"ENGR {name} {state}", dry_run=dry_run)


def install_plan() -> str:
    lines = ["Create these Shortcuts (Shortcuts.app → + → add a 'Control Home' / 'Set Scene' action). Names are exact:", ""]
    for n, s in HOME["scenes"].items():
        lines.append(f"  • {s['shortcut']:<28} Home ▸ Set Scene '{s['homeScene']}'   — {s['why']}")
    for n, a in HOME["accessories"].items():
        for st in a["states"]:
            lines.append(f"  • ENGR {n} {st:<18} Home ▸ Control '{a['homeName']}' → {st}")
    lines += ["", "Home automations (Home.app ▸ Automation ▸ + ▸ A Sensor Detects Something ▸ Convert to Shortcut):"]
    for t in HOME["triggers"]:
        lines.append(f"  • when {t['when']:<42} → Get Contents of URL POST {t['post']}  body {json.dumps(t['body'])}")
    lines += ["", "Then: engr home scene standby   # should set the room"]
    return "\n".join(lines)
