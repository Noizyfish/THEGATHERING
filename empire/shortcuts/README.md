# Siri + Shortcuts on every device

The Gabriel app ships **App Shortcuts** (`EmpireIntents.swift`), so these phrases work with zero setup the moment the app is installed — on iPhone, iPad, Apple Watch (via the paired iPhone), Mac (Designed-for-iPad build or Mac Catalyst), Vision Pro, HomePod and CarPlay (Siri hand-off to the phone):

| Say | Intent | What happens |
|---|---|---|
| “**Bring everything together** in Gabriel” | `GatherEmpireIntent` | Mirrors every repo into Forgejo, Claude writes today's chronological thru-line, Siri reads the headline |
| “**Ask the Empire** in Gabriel” → your question | `AskEmpireIntent` | Claude answers over GitHub + M2 Ultra + drives |
| “**Brief me on** NOIZYKIDZ in Gabriel” | `RepoBriefIntent` | One-repo brief; the repo name is resolved from `repos.json` (fuzzy on name or brand) |
| “**Open** DREAMCHAMBER in Gabriel” | `OpenRepoIntent` | Opens the repo on GitHub |
| “**Empire status** in Gabriel” | `EmpireStatusIntent` | Manifest size, webhook, Heaven API health |

One-time: run the **Configure Empire Webhook** action in Shortcuts with `https://<your-n8n>/webhook/empire` and the `INTENT_SHARED_SECRET`. It's stored in the `group.ai.noizy.gabriel` app group so widgets/extensions share it (add the App Group capability to the target).

## Devices without the app (Mac, Linux, Windows, HomePod-only rooms)

Shortcuts' **Get Contents of URL** does exactly what the intents do:

- URL: `https://<your-n8n>/webhook/empire` · Method **POST** · Headers `X-Noizy-Key: <secret>`, `Content-Type: application/json`
- Body (JSON): `{"action":"gather"}` or `{"action":"digest","question":"what did I build in 2026-04?"}`
- Then **Get Dictionary Value** → `digest` → **Speak Text** / **Show Result** / **Append to Note**.

Name it “Bring everything together” and it syncs to every device via iCloud, runs from the Action Button, a HomePod, Apple Watch complication, Focus filter, or a Mac menu-bar Shortcut.

From any shell: `scripts/empire gather`, `scripts/empire ask "…"`, `scripts/empire brief RSPNOIZY/NOIZYKIDZ` — same webhook, same results. Wire it into Raycast, Alfred, Keyboard Maestro, Stream Deck, or `cron`.

## Suggested automations (Shortcuts → Automation tab)

- **Time of Day 06:30 daily** → Run *Gather the Empire* → *Speak Text* (dialog). Pairs with n8n's own 06:00 run; the M2 Ultra launchd job refreshes local inventory at 05:30.
- **When I arrive at the studio** → *Empire status*.
- **Action Button** → *Ask the Empire*.
- **CarPlay / Driving Focus** → *Ask the Empire* with voice-only output.

## Apple Intelligence

When the target moves to iOS 18+, decorate the same intents with `@AssistantIntent` schemas so Siri can chain them with on-device reasoning; no backend change required.
