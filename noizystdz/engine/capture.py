"""16-channel capture → per-track WAVs + VAD segments + STT queue + live FX return.

    python -m engine.capture --session 2026-11-22-voices --fx RSP=villain

Needs `sounddevice` + the BlackHole 16ch device on the M2 Ultra. Without them (CI, sandbox) use
`--from-file some16ch.wav` which feeds the same pipeline from disk — identical outputs, no hardware.
"""
from __future__ import annotations

import argparse
import json
import queue
import sys
import threading
import time
from pathlib import Path

import numpy as np
import soundfile as sf

from . import config as cfg
from .consent import load_all
from .fx import CharacterFX, Preset
from .stt import Transcriber
from .transcript import Segment, Transcript
from .vad import EnergyVAD


class TrackWriter:
    def __init__(self, path: Path, sr: int, channels: int):
        self.f = sf.SoundFile(str(path), mode="w", samplerate=sr, channels=channels, subtype="PCM_24")
        self.path = path

    def write(self, x: np.ndarray) -> None:
        self.f.write(x)

    def close(self) -> None:
        self.f.close()


class Session:
    def __init__(self, conf: cfg.Config, session_id: str, fx_map: dict[str, str], root: Path | None = None, voice: str | None = None):
        self.conf = conf
        self.id = session_id
        self.dir = (root or cfg.ROOT / "sessions") / session_id
        (self.dir / "tracks").mkdir(parents=True, exist_ok=True)
        self.transcript = Transcript(self.dir)
        self.consents = load_all(self.dir / "consent")
        self.voice = voice                     # current character/voice label for RSP takes
        self.writers: dict[str, TrackWriter] = {}
        self.vads: dict[str, EnergyVAD] = {}
        self.fx: dict[str, CharacterFX] = {}
        self.stt_q: queue.Queue = queue.Queue()
        self.pos = 0
        s = conf.stt
        for t in conf.tracks:
            if t.record:
                self.writers[t.id] = TrackWriter(self.dir / "tracks" / f"{t.id}.wav", conf.sample_rate, len(t.ch))
            if t.stt:
                self.vads[t.id] = EnergyVAD(conf.sample_rate, s.get("vadThresholdDb", -42), s.get("hangoverMs", 350), s.get("minSegmentSec", 0.6), s.get("maxSegmentSec", 20))
            name = fx_map.get(t.id) or t.fx
            if name and name != "clean":
                self.fx[t.id] = CharacterFX(Preset.load(cfg.ROOT / "presets" / f"{name}.json"), conf.sample_rate)
        self.meta = {"session": session_id, "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "device": conf.device, "sampleRate": conf.sample_rate, "fx": fx_map, "tracks": [t.id for t in conf.tracks]}
        (self.dir / "session.json").write_text(json.dumps(self.meta, indent=2))

    def consent_for(self, track: cfg.Track):
        c = self.consents.get(track.id)
        if track.consent_required and not (c and c.allows("record")):
            return None
        return c

    def process_block(self, block: np.ndarray) -> np.ndarray:
        """block: (frames, 16) float32. Returns stereo return mix (frames, 2) for the FX return device."""
        ret = np.zeros((len(block), 2), dtype=np.float32)
        for t in self.conf.tracks:
            x = block[:, list(t.ch)]
            c = self.consent_for(t)
            if t.consent_required and c is None:
                continue                      # no consent → the track is not even written to disk
            if t.id in self.writers:
                self.writers[t.id].write(x)
            mono = x.mean(axis=1).astype(np.float32)
            if t.id in self.vads:
                for s0, s1 in self.vads[t.id].feed(mono):
                    self.stt_q.put((t.id, s0, s1, c.consent_id if c else None, self.voice))
            if t.id in self.fx:
                y = self.fx[t.id].process(mono)
                ret[:, 0] += y
                ret[:, 1] += y
        self.pos += len(block)
        return np.clip(ret, -1, 1)

    def flush(self) -> None:
        for tid, v in self.vads.items():
            t = self.conf.track(tid)
            c = self.consent_for(t)
            for s0, s1 in v.flush():
                self.stt_q.put((tid, s0, s1, c.consent_id if c else None, self.voice))

    def close(self) -> None:
        self.flush()
        for w in self.writers.values():
            w.close()
        self.meta["ended"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.meta["frames"] = self.pos
        (self.dir / "session.json").write_text(json.dumps(self.meta, indent=2))


def stt_worker(session: Session, transcriber: Transcriber, stop: threading.Event) -> None:
    sr = session.conf.sample_rate
    while not (stop.is_set() and session.stt_q.empty()):
        try:
            tid, s0, s1, consent_id, voice = session.stt_q.get(timeout=0.2)
        except queue.Empty:
            continue
        wav = session.dir / "tracks" / f"{tid}.wav"
        if not wav.exists():
            continue
        with sf.SoundFile(str(wav)) as f:
            f.seek(s0)
            audio = f.read(s1 - s0, dtype="float32")
        mono = audio.mean(axis=1) if audio.ndim == 2 else audio
        text, conf_ = transcriber.transcribe(mono, sr)
        if text.strip():
            session.transcript.append(Segment(track=tid, t0=s0 / sr, t1=s1 / sr, text=text.strip(), speaker=tid, file=str(wav.relative_to(session.dir)), consent_id=consent_id, confidence=conf_, character=voice if tid == "RSP" else None))
            print(f"[{tid}] {s0/sr:7.2f}s  {text.strip()}", file=sys.stderr)


def run_from_file(session: Session, path: Path) -> None:
    with sf.SoundFile(str(path)) as f:
        assert f.samplerate == session.conf.sample_rate, f"{path} is {f.samplerate} Hz, session is {session.conf.sample_rate}"
        while True:
            block = f.read(session.conf.block_size, dtype="float32", always_2d=True)
            if not len(block):
                break
            if block.shape[1] < session.conf.n_channels:
                block = np.pad(block, ((0, 0), (0, session.conf.n_channels - block.shape[1])))
            session.process_block(block)


def run_live(session: Session) -> None:
    import sounddevice as sd  # macOS only path

    conf = session.conf
    out_stream = sd.OutputStream(device=conf.return_device, samplerate=conf.sample_rate, channels=2, blocksize=conf.block_size, dtype="float32")
    out_stream.start()

    def cb(indata, frames, t, status):
        if status:
            print(status, file=sys.stderr)
        out_stream.write(session.process_block(indata.copy()))

    with sd.InputStream(device=conf.device, samplerate=conf.sample_rate, channels=conf.n_channels, blocksize=conf.block_size, dtype="float32", callback=cb):
        print(f"NOIZYSTDZ live on {conf.device} → {conf.return_device}. Ctrl-C to stop.", file=sys.stderr)
        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
    out_stream.stop()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="noizystdz capture")
    ap.add_argument("--session", required=True)
    ap.add_argument("--fx", action="append", default=[], help="TRACK=preset, e.g. RSP=villain")
    ap.add_argument("--voice", help="label RSP takes with this character/voice id")
    ap.add_argument("--from-file", type=Path)
    ap.add_argument("--config", type=Path)
    ap.add_argument("--root", type=Path)
    ap.add_argument("--no-stt", action="store_true")
    a = ap.parse_args(argv)

    conf = cfg.load(a.config)
    fx_map = dict(kv.split("=", 1) for kv in a.fx)
    session = Session(conf, a.session, fx_map, a.root, a.voice)
    transcriber = Transcriber(conf.stt, disabled=a.no_stt)
    stop = threading.Event()
    th = threading.Thread(target=stt_worker, args=(session, transcriber, stop), daemon=True)
    th.start()
    try:
        if a.from_file:
            run_from_file(session, a.from_file)
        else:
            run_live(session)
    finally:
        session.close()
        stop.set()
        th.join(timeout=120)
        md = session.transcript.write_markdown(f"NOIZYSTDZ — {a.session}")
        print(f"session → {session.dir}\ntranscript → {md}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
