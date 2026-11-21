from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Track:
    id: str
    label: str
    kind: str
    ch: tuple[int, ...]        # 0-based channel indexes
    stt: bool
    record: bool
    fx: str | None
    consent_required: bool

    @property
    def stereo(self) -> bool:
        return len(self.ch) == 2


@dataclass(frozen=True)
class Config:
    device: str
    sample_rate: int
    block_size: int
    return_device: str
    tracks: tuple[Track, ...]
    stt: dict
    hub: dict
    dataset: dict

    def track(self, track_id: str) -> Track:
        for t in self.tracks:
            if t.id == track_id:
                return t
        raise KeyError(track_id)

    @property
    def n_channels(self) -> int:
        return max(c for t in self.tracks for c in t.ch) + 1


def load(path: Path | None = None) -> Config:
    raw = json.loads((path or ROOT / "channels.json").read_text())
    tracks = tuple(
        Track(
            id=t["id"], label=t["label"], kind=t["kind"], ch=tuple(c - 1 for c in t["ch"]),
            stt=bool(t.get("stt")), record=bool(t.get("record")), fx=t.get("fx"),
            consent_required=bool(t.get("consentRequired")),
        )
        for t in raw["tracks"]
    )
    return Config(
        device=raw["device"], sample_rate=int(raw["sampleRate"]), block_size=int(raw.get("blockSize", 1024)),
        return_device=raw.get("returnDevice", "BlackHole 2ch"), tracks=tracks,
        stt=raw.get("stt", {}), hub=raw.get("hub", {}), dataset=raw.get("dataset", {}),
    )
