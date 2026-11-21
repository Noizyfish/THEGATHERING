"""NOIZYSTDZ session → FCPXML 1.9 that Logic Pro (File ▸ Import ▸ Final Cut Pro XML) and Final Cut Pro both open
as a multitrack timeline: one lane per track WAV, markers at every transcript segment (speaker · voice · text).
Pure stdlib. Frame-exact at the session sample rate (times written as rational seconds, e.g. 48000/48000s)."""
from __future__ import annotations

import json
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

import soundfile as sf


def _t(seconds: float, sr: int) -> str:
    return f"{int(round(seconds * sr))}/{sr}s"


def build(session_dir: Path, out: Path | None = None, project_name: str | None = None, include_markers: bool = True) -> Path:
    meta = json.loads((session_dir / "session.json").read_text())
    sr = int(meta["sampleRate"])
    tracks_dir = session_dir / "tracks"
    wavs = sorted(p for p in tracks_dir.glob("*.wav") if sf.info(str(p)).frames > 0)
    if not wavs:
        raise FileNotFoundError(f"no non-empty tracks in {tracks_dir}")
    segs = []
    tj = session_dir / "transcript.jsonl"
    if include_markers and tj.exists():
        segs = [json.loads(l) for l in tj.read_text().splitlines() if l.strip()]
    name = project_name or f"NOIZYSTDZ {meta['session']}"
    total = max(sf.info(str(p)).frames for p in wavs) / sr

    fcpxml = ET.Element("fcpxml", version="1.9")
    res = ET.SubElement(fcpxml, "resources")
    ET.SubElement(res, "format", id="r1", name="FFVideoFormat1080p30", frameDuration="100/3000s", width="1920", height="1080")
    assets: dict[str, str] = {}
    for i, p in enumerate(wavs, 2):
        info = sf.info(str(p))
        rid = f"r{i}"
        assets[p.stem] = rid
        a = ET.SubElement(res, "asset", id=rid, name=p.stem, start="0s", duration=_t(info.frames / sr, sr), hasVideo="0", hasAudio="1", audioSources="1", audioChannels=str(info.channels), audioRate=str(sr))
        ET.SubElement(a, "media-rep", kind="original-media", src=p.resolve().as_uri())

    lib = ET.SubElement(fcpxml, "library")
    ev = ET.SubElement(lib, "event", name="NOIZYSTDZ")
    proj = ET.SubElement(ev, "project", name=name)
    seq = ET.SubElement(proj, "sequence", format="r1", duration=_t(total, sr), tcStart="0s", tcFormat="NDF", audioLayout="stereo", audioRate=("48k" if sr == 48000 else "44.1k"))
    spine = ET.SubElement(seq, "spine")
    # first track is the primary storyline; the rest are connected lanes so Logic creates one track each
    primary = None
    for lane, p in enumerate(wavs):
        info = sf.info(str(p))
        attrs = dict(name=p.stem, ref=assets[p.stem], offset="0s", start="0s", duration=_t(info.frames / sr, sr), role=f"dialogue.{p.stem}")
        if lane == 0:
            primary = ET.SubElement(spine, "asset-clip", **attrs)
        else:
            ET.SubElement(primary, "asset-clip", lane=str(lane), **attrs)
    for s in segs:
        who = s.get("speaker", s.get("track"))
        label = f"{who}{' as ' + s['character'] if s.get('character') else ''}: {s.get('text', '')}"[:200]
        ET.SubElement(primary, "marker", start=_t(float(s["t0"]), sr), duration=_t(max(0.04, float(s["t1"]) - float(s["t0"])), sr), value=escape(label))

    out = out or session_dir / f"{meta['session']}.fcpxml"
    ET.indent(fcpxml)
    out.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE fcpxml>\n' + ET.tostring(fcpxml, encoding="unicode"))
    return out
