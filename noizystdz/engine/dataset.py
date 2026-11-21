"""NOIZYVOX dataset builder — consented clips only.

    python -m engine.dataset --session 2026-11-22-voices [--corpus NOIZYVOX-LINA]

For every transcript segment on a human track with a *verified, active* consent that includes
`train`, cut the clip from the per-track WAV, resample to the corpus rate, loudness-normalise,
and write  <corpus>/<speaker>/<voice>/<clip>.wav + metadata.csv (LJSpeech style: id|text|voice).
Clips with no consent, expired consent, or missing `train` scope are counted and skipped — never written.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

from . import config as cfg
from .consent import load_all
from .stt import _resample
from .transcript import Transcript


def lufs_gain(x: np.ndarray, target: float) -> float:
    rms = float(np.sqrt(np.mean(x * x))) + 1e-9
    return 10 ** ((target - (20 * np.log10(rms) + 3.0)) / 20)      # crude RMS→LUFS approximation; swap for pyloudnorm if installed


def build(conf: cfg.Config, session_dir: Path, out_root: Path, only_corpus: str | None = None) -> dict:
    tr = Transcript(session_dir)
    consents = load_all(session_dir / "consent")
    ds = conf.dataset
    target_sr = int(ds.get("targetSampleRate", 24000))
    min_s, max_s = float(ds.get("minSec", 1.0)), float(ds.get("maxSec", 15.0))
    raw = json.loads((cfg.ROOT / "channels.json").read_text())
    corpus_of = {t["id"]: t.get("corpus") for t in raw["tracks"]}
    stats = {"written": 0, "no_consent": 0, "no_train_scope": 0, "too_short": 0, "too_long": 0, "not_human": 0, "corpora": {}}
    rows: dict[str, list[list[str]]] = {}
    for seg in tr.segments():
        t = conf.track(seg.track)
        corpus = corpus_of.get(t.id)
        if t.kind != "human" or not corpus:
            stats["not_human"] += 1
            continue
        if only_corpus and corpus != only_corpus:
            continue
        c = consents.get(t.id)
        if not c or not c.active() or c.consent_id != seg.consent_id:
            stats["no_consent"] += 1
            continue
        if not c.allows("train"):
            stats["no_train_scope"] += 1
            continue
        dur = seg.t1 - seg.t0
        if dur < min_s:
            stats["too_short"] += 1
            continue
        if dur > max_s:
            stats["too_long"] += 1
            continue
        with sf.SoundFile(str(session_dir / seg.file)) as f:
            f.seek(int(seg.t0 * f.samplerate))
            a = f.read(int(dur * f.samplerate), dtype="float32", always_2d=True).mean(axis=1)
            sr = f.samplerate
        a = _resample(a, sr, target_sr)
        a = np.clip(a * lufs_gain(a, float(ds.get("loudnessLUFS", -23))), -1, 1)
        voice = seg.character or "natural"
        cid = hashlib.sha1(f"{session_dir.name}|{seg.track}|{seg.t0:.3f}".encode()).hexdigest()[:12]
        d = out_root / corpus / t.id / voice
        d.mkdir(parents=True, exist_ok=True)
        sf.write(str(d / f"{cid}.wav"), a, target_sr, subtype="PCM_16")
        rows.setdefault(corpus, []).append([f"{t.id}/{voice}/{cid}", seg.text, voice, c.consent_id, session_dir.name])
        stats["written"] += 1
        stats["corpora"][corpus] = stats["corpora"].get(corpus, 0) + 1
    for corpus, rs in rows.items():
        meta = out_root / corpus / "metadata.csv"
        exists = meta.exists()
        with meta.open("a", newline="") as f:
            w = csv.writer(f, delimiter="|")
            if not exists:
                w.writerow(["id", "text", "voice", "consent_id", "session"])
            w.writerows(rs)
    return stats


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="noizystdz dataset")
    ap.add_argument("--session", required=True)
    ap.add_argument("--root", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--corpus")
    ap.add_argument("--config", type=Path)
    a = ap.parse_args(argv)
    conf = cfg.load(a.config)
    root = a.root or cfg.ROOT / "sessions"
    stats = build(conf, root / a.session, a.out or cfg.ROOT / "corpus", a.corpus)
    print(json.dumps(stats, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
