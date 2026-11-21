# ALL Apple Kits × NOIZYSTDZ / ENGR / LUCY / GABRIEL / LINA

Every Apple framework that can touch the studio, what it does for us, which device, and where the code lives. ✅ = implemented in `Sources/NoizyKit`, 📐 = designed/spec'd here, ⏳ = later. Anthropic stays the brain; Apple kits are the senses, hands and the room.

| Kit | Device | Job in the empire | Status |
|---|---|---|---|
| **AVFoundation / AVAudioEngine** | iPhone, Mac | LUCY mic capture + playback; Mac side opens *BlackHole 16ch* as `AVAudioEngine` input for a Swift engine twin; `AVAudioSession` `.playAndRecord` + `.voiceChat` on iPhone | ✅ `StudioAudio.swift` |
| **CoreAudio / AudioToolbox** | Mac | Enumerate BlackHole/Loopback devices, set 48 kHz, aggregate check (`engr doctor` parity) | ✅ `StudioAudio.swift` |
| **CoreMIDI** | Mac, iPhone | 14-bit CC + pitch-bend to the `ENGR MCU` IAC bus; virtual source "NOIZYSTDZ" so LUCY's iPhone is a control surface over network MIDI | ✅ `Midi14.swift` |
| **ARKit (face tracking)** | iPhone 15 Pro Max | 52 ARKit blendshapes → UDP 11111 → Blender live-link for the LUCY/GABRIEL/LINA avatars; also drives the Blender lip-sync when RSP/LINA record | ✅ `FaceStream.swift` (maps to `demo/avatars/blender/arkit_blendshapes.json`) |
| **Speech** | iPhone, Mac | On-device `SFSpeechRecognizer` (`requiresOnDeviceRecognition = true`) as LUCY's live caption + fallback STT when whisper is busy; never leaves the device | ✅ `LiveCaptions.swift` |
| **SoundAnalysis** | iPhone, Mac | `SNClassifySoundRequest` — detects *speech / music / door / cough / dog* on the booth mic → `/home/event {noise}`; auto-flags takes | ✅ `RoomEars.swift` |
| **App Intents / Siri** | all | "Roll NOIZY", "Mark that", "Set voice to Captain Brassbuckle", "LINA time" → hub/ENGR; App Shortcuts appear on Watch, CarPlay, HomePod, Vision Pro | ✅ `StudioIntents.swift` (extends `EmpireIntents.swift`) |
| **HomeKit** | iPhone, iPad, Watch, tvOS (not Mac) | LUCY app owns the *Studio* home: scenes standby/session/record/playback/sleep/wrap/friday, ON AIR, door, HomePods; Mac uses Shortcuts bridge (`engr home`) | ✅ `StudioHome.swift` |
| **WidgetKit / Live Activities / ActivityKit** | iPhone, Watch, Dynamic Island | Live Activity: current voice, take #, elapsed, ON AIR; Lock-Screen controls REC/STOP/MARK | 📐 `StudioActivity.swift` |
| **WatchKit / watchOS** | Apple Watch | Wrist REC/MARK/next voice; haptic on take end; LINA records sleep pieces lights-off with her wrist | 📐 |
| **Core Haptics** | iPhone | Count-in haptic (3-2-1-roll) so no click bleeds into the mic | ✅ in `StudioIntents.swift` |
| **Core ML / Create ML** | Mac, iPhone | Train the 50-voice classifier from NOIZYVOX clips (`MLSoundClassifier`) → SoundAnalysis custom model: the room *knows which character RSP is doing* and labels takes automatically | 📐 `scripts/train_voice_classifier.swift` |
| **Vision** | iPhone, Mac | Read the printed cue sheet / script page on camera → jump to that voice; QR on the booth wall → hub | ⏳ |
| **Natural Language** | all | `NLTagger` on transcripts for speaker-turn sentiment & keyword markers → chapter markers in Logic/FCP XML | ⏳ |
| **AVSpeechSynthesizer + Personal Voice** | iPhone, Mac | **Personal Voice** (iOS 17+): RSP and LINA each create an Apple Personal Voice from 150 phrases — an on-device, Apple-sandboxed twin that LUCY can speak with via `AVSpeechSynthesisVoice(identifier:)` while NOIZYVOX trains. Requires the user to grant *Personal Voice* access per app. | ✅ `PersonalVoiceBridge.swift` |
| **ShazamKit** | iPhone | Catalog NOIZYVOX reel signatures (`SHCustomCatalog`) → any phone in the room identifies which voice is playing; tamper/leak detection for the corpus | 📐 |
| **MusicKit** | all | Reference tracks for narration pacing; Friday walk-in playlist | ⏳ |
| **CallKit / PushKit** | iPhone | LUCY answers as a voice "call" (CallKit UI) so the session feels like a call; remote guests join via CallKit → audio to Loopback via Continuity | 📐 |
| **Continuity Camera / Continuity** | iPhone↔Mac | iPhone mic/camera as Mac devices → Loopback 11-12 for LUCY, no app needed | documented in `noizystdz/ROUTING.md` |
| **Multipeer Connectivity / Network.framework (Bonjour)** | iPhone↔Mac | LUCY finds GOD (`_noizystdz._tcp`) without typing IPs; face-stream and OSC bridge advertised | ✅ `Discovery.swift` |
| **CloudKit** | all | Session metadata + consent receipts (never audio) synced across devices, private DB; consent revocations propagate everywhere | 📐 |
| **CryptoKit** | all | Ed25519 consent signing on the *speaker's own device* (matches `engine/consent.py` format): LINA signs on her phone, Mac verifies | ✅ `Consent.swift` |
| **LocalAuthentication** | iPhone, Mac | Face ID before a consent is signed or a corpus is exported | ✅ in `Consent.swift` |
| **PassKit / Wallet** | iPhone | Friday pass + LIFELUV passes; Qatom receipts as Wallet passes | ⏳ |
| **StoreKit** | iPhone | LUCY paid features — IAP compliance for digital goods alongside Qatom (legal check noted in `empire/accounts/todaq/README.md`) | ⏳ |
| **WeatherKit** | all | Pressure/humidity logged per session (voice changes with weather — real for a C3 voice actor); sleep scene picks rain vs snow ambience | 📐 |
| **HealthKit** | iPhone, Watch | Respiratory rate/HRV around sessions (RSP's call: opt-in, on-device only, never in the corpus) | ⏳ opt-in |
| **MapKit / CoreLocation** | iPhone | Arrive-at-studio automation → `scene standby`; Ottawa demo venue geofence | 📐 |
| **ScreenCaptureKit** | Mac | Record the Logic/hub screen with system audio for the Friday making-of | 📐 `engr capture-screen` |
| **Metal / RealityKit / SceneKit** | iPhone, Vision Pro | Render the LUCY avatar live from ARKit blendshapes on-device (no Blender round trip) → Vision Pro presence | 📐 `AvatarView.swift` |
| **AVKit / AirPlay** | Mac→Apple TV/HomePods | `engr home appletv on` + AirPlay the reel from GOD to the studio HomePods for Friday | documented in `engr/HOMEKIT.md` |
| **Accessibility (AX) / Voice Control / Switch Control** | all | The studio must be fully usable one-handed and by voice: every control has an AX label and a Voice Control name; Switch Control scanning order set | ✅ labels in all views |
| **BackgroundTasks** | iPhone | Nightly: sync consent receipts, prefetch tomorrow's scripts | ⏳ |
| **UserNotifications** | all | "Take 12 saved · 38/50" after each voice; LINA's 20:00 sleep-session reminder | ✅ in `StudioIntents.swift` |
| **Xcode Cloud / TestFlight** | — | LUCY + GABRIEL builds to the family's devices; LINA gets TestFlight | ⏳ |
| **Swift Package: MIDIKit (orchetect)** | Mac/iOS | 14-bit CC & MCU helpers if you prefer a library over `Midi14.swift` | optional dep |

## Package layout
```
engr/applekit/
  Package.swift                  SwiftPM: NoizyKit (iOS 17 / macOS 14 / watchOS 10 / visionOS 1)
  Sources/NoizyKit/
    StudioAudio.swift            AVAudioEngine capture → UDP/HTTP to hub; BlackHole device discovery (macOS)
    Midi14.swift                 CoreMIDI 14-bit CC pair + pitch bend + MCU notes; virtual source
    FaceStream.swift             ARKit 52 blendshapes → UDP 11111 (Blender) at 60 Hz
    LiveCaptions.swift           on-device SFSpeechRecognizer → hub /segment
    RoomEars.swift               SoundAnalysis built-in classifier → hub /home/event
    StudioIntents.swift          App Intents: Roll/Stop/Mark/SetVoice/Scene/Consent + App Shortcuts phrases
    StudioHome.swift             HomeKit scenes + ON AIR characteristic writes (iOS/tvOS/watchOS)
    Consent.swift                CryptoKit Ed25519 consent, same JSON as engine/consent.py; Face ID gate
    Discovery.swift              Bonjour advertise/browse _noizystdz._tcp
    PersonalVoiceBridge.swift    AVSpeechSynthesizer with Personal Voice as LUCY/LINA interim voice
    HubClient.swift              tiny HTTP+SSE client for :9790
```
Build: `cd engr/applekit && swift build` (macOS); add the package to the GABRIEL/LUCY Xcode projects. Nothing here needs a server beyond the hub.
