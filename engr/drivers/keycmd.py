"""System Events keystrokes / menu clicks against a frontmost app. Needs Accessibility permission for the caller (Terminal/launchd)."""
from __future__ import annotations
from . import applescript

KEYCODES = {"space": 49, "return": 36, "escape": 53, "tab": 48, "delete": 51, "left": 123, "right": 124, "down": 125, "up": 126, "0kp": 82}


def _mods(mods: list[str] | None) -> str:
    m = [f"{x} down" for x in (mods or [])]
    return f" using {{{', '.join(m)}}}" if m else ""


def keystroke(app: str, spec: dict, dry_run: bool = False) -> str:
    """spec: {key, mods?, keypad?} or {menu:[...]}."""
    if "menu" in spec:
        return menu(app, spec["menu"], dry_run)
    key = spec["key"]
    if spec.get("keypad") and key == "0":
        body = f"key code {KEYCODES['0kp']}{_mods(spec.get('mods'))}"
    elif key in KEYCODES:
        body = f"key code {KEYCODES[key]}{_mods(spec.get('mods'))}"
    else:
        body = f'keystroke "{key}"{_mods(spec.get("mods"))}'
    script = f'tell application "{app}" to activate\ndelay 0.15\ntell application "System Events" to tell process "{app}" to {body}'
    return applescript.run(script, dry_run)


def menu(app: str, path: list[str], dry_run: bool = False) -> str:
    if len(path) < 2:
        raise ValueError("menu path needs at least [Menu, Item]")
    target = f'menu item "{path[-1]}" of '
    for item in reversed(path[1:-1]):
        target += f'menu 1 of menu item "{item}" of '
    target += f'menu 1 of menu bar item "{path[0]}" of menu bar 1'
    script = f'tell application "{app}" to activate\ndelay 0.15\ntell application "System Events" to tell process "{app}" to click {target}'
    return applescript.run(script, dry_run)
