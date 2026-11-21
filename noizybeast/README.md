# NOIZYBEAST.IDE

**One window for the whole beast.** Tauri 2 (Rust) desktop shell on GOD, with RustDesk baked in so the same window is reachable from any device. Everything built this week lands here directly:

| panel | what's inside | backed by |
|---|---|---|
| **Studio** | ROLL / STOP / MARK, voice picker (the 50), consent, live per-speaker transcript, 50-for-Friday progress grid | NOIZYSTDZ hub `:9790` (SSE) + `engr logic …` + HomeKit scenes |
| **ENGR** | console: `engr …` or plain words → Logic Pro, Audio Hijack, apps, Talon, HomeKit | `engr/engr` sidecar (MCU/IAC MIDI, key commands, FCPXML import) |
| **Surface** | Open Stage Control (14-bit faders/knobs, 50-voice grid, room) in an iframe | O-S-C at `:8080` → IAC bus + `osc/bridge.py :9792` |
| **Room** | scenes standby/session/record/playback/sleep/wrap/friday, ON AIR, door, HomePods | `engr home …` (Shortcuts → HomeKit) or NoizyKit `StudioHome` on iOS |
| **Remote** | RustDesk ID + connect, self-hosted relay | `rustdesk --get-id`, `rustdesk://connect/…`, `remote/docker-compose.rustdesk.yml` |
| **Thru-line** | `empire run` → regenerate the chronological EMPIRE.md from everything | `scripts/empire` |

Rust `core.rs` carries 14-bit MIDI / OSC / RustDesk URL logic and is **byte-identical** to `engr/osc/midi14.py` and `NoizyKit/Midi14.swift` (all three test `cc14(1,7,0.75) == [[176,7,95],[176,39,127]]`).

## Build on GOD
```bash
brew install --cask rustdesk open-stage-control          # OSC surface + remote
cd noizybeast && npm install && npm run tauri dev          # first run compiles Tauri (~3 min on M2 Ultra)
npm run tauri build                                        # → src-tauri/target/release/bundle/dmg/NOIZYBEAST.IDE_0.1.0_aarch64.dmg
```
Env: `NOIZY_GATHERING=/Users/m2ultra/THEGATHERING` if the repo isn't at `~/THEGATHERING`. Hub URL is `localStorage.hub` (default `http://127.0.0.1:9790`).

Accessibility is first-class (RSP is one-handed, voice-first): every control has an `aria-label`, Voice Control names match the labels, and everything in the UI is also an ENGR verb (`engr …`) so Talon / Siri / Stream Deck can do it without the window.

## Layout
```
src-tauri/   Cargo.toml · tauri.conf.json · capabilities/default.json (sidecar allow-list) · entitlements.plist · src/{core,lib,main}.rs
src/         main.ts · beast.css      index.html
remote/      RustDesk relay compose + README
```
Tests: `cargo test` in `src-tauri` (core), `npm run typecheck`.
