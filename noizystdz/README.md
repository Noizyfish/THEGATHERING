# NOIZYSTDZ — the NOIZY studio (→ NOIZYVOX)

**Interactive, multi-person character-creation studio on the M2 Ultra.** Everyone in the room (and on the call) performs on their own track; the engine captures 16 channels through BlackHole, records every track clean, cuts speech with VAD, transcribes each speaker locally with whisper, applies a live character voice the performer hears in their cans, and — only where a signed consent says so — feeds clips into **NOIZYVOX**: a human-created, human-owned voice corpus. Voice sovereignty is enforced in code, not in a policy PDF.

```
BlackHole 16ch ──► engine/capture.py ──► sessions/<id>/tracks/*.wav   (per track, 48k/24-bit, clean)
                        │  VAD                 └ transcript.jsonl / .md  (per speaker, time-coded, voice-labelled)
                        │  FX ──► BlackHole 2ch ──► cans (the character, live)
                        └──► hub :9790 (SSE) ──► every phone in the room
engine/dataset.py ──► corpus/NOIZYVOX-RSP | NOIZYVOX-LINA   (consent-gated, 24 kHz, LJSpeech metadata)
engine/reel.py    ──► reel/NOIZYVOX-50.wav + cue-sheet.md   (Friday)
```

## Models that come out of this
| model | voice source | corpus | host |
|---|---|---|---|
| **GABRIEL** | RSP | NOIZYVOX-RSP | M2 Ultra |
| **LUCY** | RSP | NOIZYVOX-RSP | iPhone 15 Pro Max |
| **LINA** *(new)* | RSP's wife — her consent, her key, her corpus | NOIZYVOX-LINA | M2 Ultra |

LINA is the sleep/soothing voice of the reel and the first NOIZYVOX model built from someone other than RSP — which is the whole point: the pipeline proves consent and provenance for a second human before it ever scales to a third.

## Friday: 50 voices for Nicholas AC Mumford (2026-11-28)
[`characters/roster.json`](characters/roster.json) — 20 animation · 15 narration · 15 sleep (37 RSP, 13 LINA), each with a 20–40 s script and the live FX preset. `./noizystdz roster sleep` is the teleprompter.

| day | do |
|---|---|
| Sat 22 | `./noizystdz setup`; build Loopback/Audio Hijack per [ROUTING.md](ROUTING.md); 10-minute test session; `./noizystdz test` on GOD |
| Sun 23 | **Animation day** — RSP, 20 voices, 2 takes each (`session day2 --voice anim-01` …) |
| Mon 24 | **Narration day** — 15 voices; LINA consent + mic check; her first 3 sleep pieces |
| Tue 25 | **LINA sleep day** — 10 pieces, quiet room, late evening |
| Wed 26 | Pickups; `dataset` both corpora; first `reel`; listen end-to-end in the car |
| Thu 27 | Fix the 5 weakest; final `reel`; burn to USB + Proton Drive + kDrive; cue sheet printed |
| Fri 28 | Play it. `reel/NOIZYVOX-50.wav`, 50 slates, ~30 min. |

## Commands
```bash
./noizystdz setup                                  # deps + device check (GOD)
./noizystdz session 2026-11-23-anim --voice anim-01 --fx RSP=villain
./noizystdz dataset 2026-11-23-anim                # → corpus/NOIZYVOX-RSP
./noizystdz dataset 2026-11-25-lina --corpus NOIZYVOX-LINA
./noizystdz reel                                   # → reel/
./noizystdz test                                   # no hardware needed
```
Hardware-free: `python -m engine.capture --session x --from-file some16ch.wav --no-stt` runs the identical pipeline from disk.

## Human Voice Sovereignty (HVS) — how it's enforced
- `engine/consent.py`: Ed25519-signed JSON per speaker per session, scopes `record · transcribe · train · synthesize · commercial · share`, optional expiry, revocable. Legal names are stored only as a salted hash.
- **No consent → the track isn't written to disk**, not even for the session (`capture.py`). Guests on a call are recorded only after they tap *consent* on the hub page.
- `dataset.py` writes a clip only if the segment's `consent_id` matches a verified, active consent that includes `train`. Everything refused is counted in the stats, never silently dropped.
- Every corpus row carries `consent_id` + `session` → every future synthesized line can be traced to a signed grant. TODAQ receipts (see `empire/accounts/todaq`) sit on top of this for payment provenance.
- STT runs on-device (mlx-whisper). Nothing is uploaded.

## Layout
```
channels.json     16-channel map, STT/hub/dataset config, model registry (GABRIEL/LUCY/LINA)
engine/           config · capture · vad · stt · fx · consent · transcript · dataset · reel · hub
presets/          clean · gabriel · lucy · lina · villain · sprite
characters/       roster.json (the 50)
tests/            hardware-free end-to-end
sessions/ corpus/ reel/   outputs (gitignored)
```
