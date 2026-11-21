from __future__ import annotations
import shutil
import subprocess


def run(name: str, input_path: str | None = None, dry_run: bool = False) -> str:
    cmd = ["shortcuts", "run", name] + (["--input-path", input_path] if input_path else [])
    if dry_run or not shutil.which("shortcuts"):
        return " ".join(cmd)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr.strip())
    return r.stdout.strip()
