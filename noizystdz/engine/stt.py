"""Speech-to-text on the M2 Ultra: mlx-whisper first (Apple silicon), faster-whisper fallback, else a stub.
Returns (text, confidence). Nothing leaves the machine — voice sovereignty starts here."""
from __future__ import annotations

import numpy as np


class Transcriber:
    def __init__(self, conf: dict, disabled: bool = False):
        self.conf = conf
        self.backend = None
        self.name = "stub"
        if disabled:
            return
        try:
            import mlx_whisper  # type: ignore
            self.backend = ("mlx", mlx_whisper)
            self.name = f"mlx-whisper:{conf.get('model')}"
        except Exception:
            try:
                from faster_whisper import WhisperModel  # type: ignore
                size = (conf.get("fallback") or "faster-whisper:large-v3-turbo").split(":", 1)[-1]
                self.backend = ("fw", WhisperModel(size, device="auto", compute_type="auto"))
                self.name = f"faster-whisper:{size}"
            except Exception:
                self.backend = None

    def transcribe(self, mono: np.ndarray, sr: int) -> tuple[str, float | None]:
        if self.backend is None:
            dur = len(mono) / sr
            return f"[untranscribed {dur:.1f}s — install mlx-whisper]", None
        kind, b = self.backend
        audio16 = _resample(mono, sr, 16000)
        if kind == "mlx":
            r = b.transcribe(audio16, path_or_hf_repo=self.conf.get("model"), language=self.conf.get("language", "en"))
            return r.get("text", ""), None
        segs, _ = b.transcribe(audio16, language=self.conf.get("language", "en"), vad_filter=False)
        segs = list(segs)
        text = " ".join(s.text.strip() for s in segs)
        conf = float(np.mean([np.exp(s.avg_logprob) for s in segs])) if segs else None
        return text, conf


def _resample(x: np.ndarray, sr: int, target: int) -> np.ndarray:
    if sr == target:
        return x.astype(np.float32)
    n = int(round(len(x) * target / sr))
    idx = np.linspace(0, len(x) - 1, n)
    return np.interp(idx, np.arange(len(x)), x).astype(np.float32)
