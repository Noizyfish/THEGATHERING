"""Per-track transcript store: JSONL of segments + merged Markdown timeline."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Segment:
    track: str
    t0: float          # seconds from session start
    t1: float
    text: str
    speaker: str
    file: str          # per-track WAV the segment lives in
    consent_id: str | None = None
    confidence: float | None = None
    character: str | None = None


class Transcript:
    def __init__(self, session_dir: Path):
        self.path = session_dir / "transcript.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, seg: Segment) -> None:
        with self.path.open("a") as f:
            f.write(json.dumps(asdict(seg), ensure_ascii=False) + "\n")

    def segments(self) -> list[Segment]:
        if not self.path.exists():
            return []
        return [Segment(**json.loads(l)) for l in self.path.read_text().splitlines() if l.strip()]

    def render_markdown(self, title: str) -> str:
        segs = sorted(self.segments(), key=lambda s: s.t0)
        lines = [f"# {title}", "", "| time | track | speaker | text |", "|---|---|---|---|"]
        for s in segs:
            mm, ss = divmod(int(s.t0), 60)
            who = f"{s.speaker}{f' as **{s.character}**' if s.character else ''}"
            lines.append(f"| {mm:02d}:{ss:02d} | {s.track} | {who} | {s.text.replace('|', '\\|')} |")
        return "\n".join(lines) + "\n"

    def write_markdown(self, title: str) -> Path:
        p = self.path.with_name("transcript.md")
        p.write_text(self.render_markdown(title))
        return p
