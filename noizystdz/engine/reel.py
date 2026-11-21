"""Build the Friday showreel: for each roster voice, pick the best take (longest consented clip labelled with
that voice), add a spoken slate (macOS `say`, or silence elsewhere), concatenate per category, write
reel/<category>.wav + reel/NOIZYVOX-50.wav + reel/cue-sheet.md. Honest: lists voices with no take yet."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

from . import config as cfg
from .transcript import Transcript


def slate(text: str, sr: int) -> np.ndarray:
    if shutil.which("say"):
        with tempfile.TemporaryDirectory() as d:
            aiff = Path(d) / "s.aiff"
            subprocess.run(["say", "-v", "Daniel", "-o", str(aiff), text], check=False)
            if aiff.exists():
                a, s = sf.read(str(aiff), dtype="float32", always_2d=True)
                a = a.mean(axis=1)
                if s != sr:
                    a = np.interp(np.linspace(0, len(a) - 1, int(len(a) * sr / s)), np.arange(len(a)), a).astype(np.float32)
                return a * 0.6
    return np.zeros(int(0.8 * sr), dtype=np.float32)


def best_take(sessions: list[Path], voice_id: str, voice_name: str):
    best = None
    for sd in sessions:
        for seg in Transcript(sd).segments():
            if seg.character in (voice_id, voice_name) and seg.consent_id:
                dur = seg.t1 - seg.t0
                if best is None or dur > best[0]:
                    best = (dur, sd, seg)
    return best


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="noizystdz reel")
    ap.add_argument("--root", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--gap", type=float, default=1.2)
    a = ap.parse_args(argv)
    conf = cfg.load()
    root = a.root or cfg.ROOT / "sessions"
    out = a.out or cfg.ROOT / "reel"
    out.mkdir(parents=True, exist_ok=True)
    roster = json.loads((cfg.ROOT / "characters" / "roster.json").read_text())
    sessions = sorted(p for p in root.iterdir() if (p / "transcript.jsonl").exists()) if root.exists() else []
    sr = conf.sample_rate
    gap = np.zeros(int(a.gap * sr), dtype=np.float32)
    full: list[np.ndarray] = []
    cue = ["# NOIZYVOX — 50 voices for Nicholas AC Mumford", "", "| # | voice | category | performer | take | length |", "|---|---|---|---|---|---|"]
    missing = []
    per_cat: dict[str, list[np.ndarray]] = {}
    t = 0.0
    for i, v in enumerate(roster["voices"], 1):
        take = best_take(sessions, v["id"], v["name"])
        if not take:
            missing.append(v)
            cue.append(f"| {i} | {v['name']} | {v['category']} | {v['performer']} | — | **NO TAKE YET** |")
            continue
        dur, sd, seg = take
        with sf.SoundFile(str(sd / seg.file)) as f:
            f.seek(int(seg.t0 * f.samplerate))
            clip = f.read(int(dur * f.samplerate), dtype="float32", always_2d=True).mean(axis=1)
        clip = clip / (np.max(np.abs(clip)) + 1e-9) * 0.8
        s = slate(f"{i}. {v['name']}", sr)
        chunk = np.concatenate([s, gap[: len(gap) // 3], clip, gap])
        per_cat.setdefault(v["category"], []).append(chunk)
        full.append(chunk)
        mm, ss = divmod(int(t), 60)
        cue.append(f"| {i} | {v['name']} | {v['category']} | {v['performer']} | {sd.name} @ {seg.t0:.1f}s | {dur:.1f}s (reel {mm:02d}:{ss:02d}) |")
        t += len(chunk) / sr
    for c, chunks in per_cat.items():
        sf.write(str(out / f"{c}.wav"), np.concatenate(chunks), sr, subtype="PCM_24")
    if full:
        sf.write(str(out / "NOIZYVOX-50.wav"), np.concatenate(full), sr, subtype="PCM_24")
    cue += ["", f"**{50 - len(missing)}/50 voices have a take.** Reel length {int(t // 60)}:{int(t % 60):02d}."]
    if missing:
        cue += ["", "## Still to record", ""] + [f"- {v['id']} — {v['name']} ({v['performer']}): _{v['script'][:60]}…_" for v in missing]
    (out / "cue-sheet.md").write_text("\n".join(cue) + "\n")
    print(f"{50 - len(missing)}/50 takes → {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
