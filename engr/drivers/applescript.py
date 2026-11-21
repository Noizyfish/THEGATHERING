from __future__ import annotations
import shutil
import subprocess


def run(script: str, dry_run: bool = False) -> str:
    if dry_run or not shutil.which("osascript"):
        return f"osascript -e {script!r}"
    r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr.strip() or f"osascript exit {r.returncode}")
    return r.stdout.strip()


def activate(app: str, dry_run: bool = False) -> str:
    return run(f'tell application "{app}" to activate', dry_run)


def quit_app(app: str, dry_run: bool = False) -> str:
    return run(f'tell application "{app}" to quit', dry_run)


def open_file(app: str, path: str, dry_run: bool = False) -> str:
    return run(f'tell application "{app}" to open POSIX file "{path}"', dry_run)


def notify(title: str, text: str, dry_run: bool = False) -> str:
    return run(f'display notification "{text}" with title "{title}"', dry_run)


def say(text: str, voice: str = "Daniel", dry_run: bool = False) -> str:
    if dry_run or not shutil.which("say"):
        return f"say -v {voice} {text!r}"
    subprocess.run(["say", "-v", voice, text], check=False)
    return ""
