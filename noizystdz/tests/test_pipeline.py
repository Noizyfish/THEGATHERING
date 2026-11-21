"""End-to-end without hardware: synth 16ch WAV → capture --from-file → dataset (consent gate) → reel."""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from engine import config as cfg  # noqa: E402
from engine.consent import Consent, load_key, save, sign, verify, load_all  # noqa: E402
from engine.fx import CharacterFX, Preset  # noqa: E402
from engine.vad import EnergyVAD  # noqa: E402


def tone_bursts(sr, total, bursts, f=180.0):
    x = np.zeros(int(total * sr), dtype=np.float32)
    for s, e in bursts:
        n = np.arange(int((e - s) * sr))
        x[int(s * sr): int(s * sr) + len(n)] = 0.3 * np.sin(2 * np.pi * f * n / sr) * (0.6 + 0.4 * np.sin(2 * np.pi * 3 * n / sr))
    return x


def test_vad_segments():
    sr = 48000
    v = EnergyVAD(sr, -42, 350, 0.6, 20)
    x = tone_bursts(sr, 6, [(0.5, 2.0), (3.0, 4.5)])
    segs = []
    for i in range(0, len(x), 1024):
        segs += v.feed(x[i:i + 1024])
    segs += v.flush()
    assert len(segs) == 2
    assert abs(segs[0][0] / sr - 0.5) < 0.1 and abs(segs[1][0] / sr - 3.0) < 0.1


def test_consent_roundtrip(tmp_path):
    key = load_key(tmp_path / "k")
    c = sign(Consent("RSP", "Rob", ["record", "train"], "s1"), key)
    assert verify(c)
    c.scopes.append("commercial")
    assert not verify(c)              # tamper breaks signature
    sign(c, key); save(c, tmp_path / "consent")
    assert load_all(tmp_path / "consent")["RSP"].allows("record", "train", "commercial")


def test_fx_runs_and_bounded():
    sr = 48000
    fx = CharacterFX(Preset.load(HERE / "presets" / "villain.json"), sr)
    x = tone_bursts(sr, 1, [(0, 1)])
    y = np.concatenate([fx.process(x[i:i + 1024]) for i in range(0, len(x), 1024)])
    assert y.shape == x.shape and np.max(np.abs(y)) <= 1.0 and np.max(np.abs(y)) > 0.05


def test_end_to_end(tmp_path):
    conf = cfg.load()
    sr = conf.sample_rate
    root = tmp_path / "sessions"
    sess = "test-sess"
    sd = root / sess
    # consent: RSP full, LINA_SRC record-only (no train), GUEST_B none
    for spk, scopes in (("RSP", ["record", "transcribe", "train"]), ("LINA_SRC", ["record", "transcribe"])):
        save(sign(Consent(spk, spk, scopes, sess), load_key(sd / "keys" / f"{spk}.ed25519")), sd / "consent")
    # 16ch file: RSP speaks 0.5–2.5 & 4–6, LINA 7–9, GUEST_B 1–3 (no consent → must not be recorded)
    x = np.zeros((int(10 * sr), 16), dtype=np.float32)
    rsp = tone_bursts(sr, 10, [(0.5, 2.5), (4.0, 6.0)], 150); x[:, 0] = x[:, 1] = rsp
    lina = tone_bursts(sr, 10, [(7.0, 9.0)], 260); x[:, 2] = x[:, 3] = lina
    gb = tone_bursts(sr, 10, [(1.0, 3.0)], 200); x[:, 4] = x[:, 5] = gb
    wav = tmp_path / "in16.wav"; sf.write(str(wav), x, sr)
    r = subprocess.run([sys.executable, "-m", "engine.capture", "--session", sess, "--root", str(root), "--from-file", str(wav), "--no-stt", "--voice", "anim-01", "--fx", "RSP=villain"], cwd=HERE, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert (sd / "tracks" / "RSP.wav").exists() and (sd / "tracks" / "LINA_SRC.wav").exists()
    assert not (sd / "tracks" / "GUEST_B.wav").exists() or sf.info(str(sd / "tracks" / "GUEST_B.wav")).frames == 0
    segs = [json.loads(l) for l in (sd / "transcript.jsonl").read_text().splitlines()]
    assert {s["track"] for s in segs} == {"RSP", "LINA_SRC"}
    assert sum(s["track"] == "RSP" for s in segs) == 2 and all(s["character"] == "anim-01" for s in segs if s["track"] == "RSP")
    assert (sd / "transcript.md").exists()
    # dataset: only RSP has train scope
    r = subprocess.run([sys.executable, "-m", "engine.dataset", "--session", sess, "--root", str(root), "--out", str(tmp_path / "corpus")], cwd=HERE, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    st = json.loads(r.stdout)
    assert st["written"] == 2 and st["no_train_scope"] == 1 and st["corpora"] == {"NOIZYVOX-RSP": 2}
    meta = (tmp_path / "corpus" / "NOIZYVOX-RSP" / "metadata.csv").read_text().splitlines()
    assert len(meta) == 3 and meta[1].split("|")[2] == "anim-01"
    clip = sf.info(str(tmp_path / "corpus" / "NOIZYVOX-RSP" / "RSP" / "anim-01" / (meta[1].split("|")[0].split("/")[-1] + ".wav")))
    assert clip.samplerate == 24000
    # reel: 1/50 voices has a take
    r = subprocess.run([sys.executable, "-m", "engine.reel", "--root", str(root), "--out", str(tmp_path / "reel")], cwd=HERE, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    cue = (tmp_path / "reel" / "cue-sheet.md").read_text()
    assert "**1/50 voices have a take.**" in cue and (tmp_path / "reel" / "animation.wav").exists() and "NO TAKE YET" in cue
