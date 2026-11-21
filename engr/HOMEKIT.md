# HomeKit × NOIZYSTDZ × ENGR

The room is part of the studio. ENGR drives **every** HomeKit accessory (and anything on Matter) through two sanctioned paths — no private APIs, works on every Apple device in the house.

```
engr home scene record ──► shortcuts run "ENGR Scene Record" ──► Home ▸ Studio Record (ON AIR red, fans off, HomePods pause)
Home.app automation  ──► Shortcut: POST http://GOD.local:9790/home/event {"event":"door_open"} ──► hub marker + ENGR Logic marker
```

## Commands
```bash
engr home install                 # prints every Shortcut + Home automation to create (names are the contract)
engr home scene standby|session|record|playback|sleep|wrap|friday
engr home onair red | engr home door lock | engr home homepods pause | engr home thermostat "fan off"
engr home triggers                # list room → studio triggers
```
Everything also speaks: **"engr record"** (Talon) → Logic rolls **and** the ON AIR light goes red, because `hubToHome.on_record_start = scene record`.

## Why Shortcuts and not a HomeKit framework
HomeKit's framework is iOS/iPadOS/tvOS/watchOS-only — there is no `HomeKit.framework` on macOS. Shortcuts' *Control Home* / *Set Scene* actions are the Apple-supported way for a Mac (and `shortcuts run` is a first-party CLI). Latency ≈ 300–800 ms; fine for lights, locks, fans.

## Studio accessories (buy list, all HomeKit/Matter, ≈ CAD 600)
| job | accessory | why |
|---|---|---|
| ON AIR | Nanoleaf Essentials Matter bulb in a vintage ON AIR box (or Philips Hue + Bridge) | red/amber/off states, instant |
| key light | Elgato Key Light Air **is not HomeKit** → put it on a Meross HomeKit plug, or use Hue Play | one scene sets performer light |
| booth fan / fridge | Meross or Eve Energy smart plugs | fans are the #1 noise floor killer; off during record |
| door | Level Lock+ or Aqara U100 (HomeKit) | LINA's own code → `lina_arrived` trigger; locked during takes |
| booth sensor | Aqara/Eve Motion + Eve Room (noise/air) | motion → standby; noise → flag the take |
| monitors | HomePod stereo pair (AirPlay from GOD) | playback scene; Friday demo speakers |
| screen | Apple TV 4K | Friday: plays the reel + Keynote; `engr home appletv on` |
| thermostat | ecobee/Nest (HomeKit/Matter) | fan off during record, back on between |

## Advanced: ENGR as a HomeKit accessory (optional, 1 evening)
Run **HAP-python** on GOD exposing switches *Logic Record*, *Logic Play*, *Safety Rec*, *Studio Session*. Then Siri on *any* device — HomePod in the kitchen, Watch, CarPlay — can say "turn on Logic Record" and HomeKit calls `engr logic record`. Pair once with the Home app; it also shows up as buttons in Control Center. Scaffold: `engr home hap` prints the accessory file.

## Safety & privacy
- Scenes never touch cameras; `door_open` only logs a transcript marker, not video.
- Triggers POST to the hub on the LAN only (`GOD.local`); the hub accepts `/home/event` from RFC1918 addresses only.
- The Friday scene unlocks nothing.
