# NOIZYSTDZ routing — BlackHole 16ch · Loopback · Audio Hijack · M2 Ultra

One rule: **every source lands on its own BlackHole 16ch stereo pair**, the engine captures all 16 at once, nothing is mixed before capture. Mixing is for the guests' ears (PROGRAM 15-16) and the engine's return (FX_RETURN 13-14) only.

```
 RSP mic (interface in 1-2) ─────────────┐
 LINA mic (interface in 3-4) ────────────┤                                ┌─► RSP.wav       (clean, trains NOIZYVOX-RSP)
 Guest B — kMeet/FaceTime/Discord app ───┤  Loopback                      ├─► LINA_SRC.wav  (clean, trains NOIZYVOX-LINA)
 Guest C — second call app ──────────────┼──► "NOIZYSTDZ IN" (16ch) ──────┼─► GUEST_*.wav   (session only, needs consent)
 GABRIEL voice-service :9799 (python) ───┤   = BlackHole 16ch             ├─► GABRIEL.wav / LUCY.wav
 LUCY (iPhone via Continuity / AirPlay) ─┤                                ├─► VAD → mlx-whisper → transcript.jsonl → hub SSE
 Engine FX return (BlackHole 2ch) ───────┤                                └─► FX_RETURN.wav
 Program mix (Audio Hijack mixer) ───────┘
                                      engine → BlackHole 2ch ─► Audio Hijack "Cans" → RSP's headphones (hears the character live, ~21 ms)
```

## 1. Devices (Audio MIDI Setup)
- `brew install blackhole-16ch blackhole-2ch` → reboot or restart coreaudiod.
- Set **BlackHole 16ch** and your interface both to **48 kHz**. Do not create an aggregate device for capture — Loopback does the routing with proper clocking.

## 2. Loopback — virtual device `NOIZYSTDZ IN`
Create one Loopback device, 16 output channels, and wire **sources → channels**:

| Source (Loopback "Sources") | → Loopback channels | Track |
|---|---|---|
| Audio interface, inputs 1-2 | 1-2 | RSP |
| Audio interface, inputs 3-4 | 3-4 | LINA_SRC |
| App: kMeet / FaceTime / Discord (call #1) | 5-6 | GUEST_B |
| App: second call | 7-8 | GUEST_C |
| App: Python (voice-service) — or Terminal | 9-10 | GABRIEL |
| iPhone (Continuity Camera mic / AirPlay receiver app) | 11-12 | LUCY |
| Device: BlackHole 2ch (engine return) | 13-14 | FX_RETURN |
| Audio Hijack "Program" block (see below) | 15-16 | PROGRAM |

Then in Loopback set the device's **Monitors** to nothing (the engine is the only listener). Set `NOIZYSTDZ IN` as the capture device name in `channels.json` if you named it differently from `BlackHole 16ch`.

> Why Loopback and not only Audio Hijack: Loopback is the only tool here that creates a **single 16-channel device** with per-channel source mapping that `sounddevice` can open as one stream — sample-accurate across all tracks.

## 3. Audio Hijack — three sessions
1. **Cans** — Input: *BlackHole 2ch* (engine FX return) + Input: *Loopback NOIZYSTDZ IN ch 5-12* (guests, GABRIEL, LUCY) → Volume → Output: interface headphones. RSP hears himself **as the character** plus everyone else. (Direct-monitor his dry mic on the interface at −∞ to avoid comb filtering; the engine return is his monitor.)
2. **Program** — the mix the remote guests hear: RSP processed (BlackHole 2ch) + LINA + GABRIEL + LUCY → Output: *Loopback NOIZYSTDZ IN 15-16* **and** → the call app's input (Loopback's own "pass-thru" device for kMeet). Never include the guests' own return in this (echo).
3. **Safety** — Input: *NOIZYSTDZ IN* all 16 → Recorder block, 48 kHz 24-bit WAV, split every 30 min. Belt-and-braces copy of the raw multitrack in case the engine dies mid-take.

## 4. Engine
```bash
cd noizystdz && ./noizystdz setup
./noizystdz session 2026-11-22-day1 --voice anim-01 --fx RSP=villain
```
Open `http://<GOD-ip>:9790` on every phone in the room: tap a voice to switch RSP's character (FX + label), tap *consent* to sign in, watch the transcript appear per speaker as it's spoken.

## 5. Latency budget
| stage | ms |
|---|---|
| interface in → CoreAudio | ~3 |
| Loopback | ~5 (1 buffer) |
| engine block 1024 @ 48 kHz | 21.3 |
| BlackHole 2ch → Audio Hijack → cans | ~6 |
| **total** | **~35 ms** — fine for speech; drop `blockSize` to 512 for ~25 ms if the M2 Ultra is bored (it will be). |

## 6. LUCY on the iPhone 15 Pro Max
Simplest reliable path: LUCY app plays TTS → **Continuity** (iPhone as Mac mic, Settings → General → AirPlay & Continuity) or an AirPlay receiver on GOD; Loopback maps that device to 11-12. Her transcript then comes from the same whisper as everyone else — one pipeline, no special casing.
