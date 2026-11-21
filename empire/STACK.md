# THE STACK — Forgejo + n8n + Claude + App Intents

All FOSS, all self-hosted, one manifest. Everything reads `empire/repos.json`.

```
 Siri / Shortcuts / Action Button / CLI
        │  App Intents (Gabriel) · scripts/empire
        ▼
  n8n  ──►  Forgejo  ◄──  GitHub (RSPNOIZY + Noizyfish)        pull-mirrors, auto-synced
   │  ◄──  empire/local-inventory.json   (M2 Ultra + HDDs, nightly launchd, file birth dates)
   │  ◄──  empire/google-inventory.json  (Drive + YouTube + Gmail, n8n Google OAuth2 or rclone)
   └─►  Anthropic Messages API  ──►  chronological thru-line (1996 → now)  ──►  Forgejo issue + Siri reply
```

| Piece | What | Where |
|---|---|---|
| Forgejo | Self-hosted git. Every repo in the manifest becomes a pull-mirror, so the whole 30 months lives on hardware you own. | `empire/stack/docker-compose.yml` |
| n8n | Automation. Daily at 06:00 (or on Siri trigger) refreshes mirrors, asks Claude for the thru-line, files it. | `empire/stack/n8n/empire-thru-line.json` |
| Claude | Anthropic Messages API (`claude-sonnet-4-6` by default; same IDs as Gabriel's `.env.example`). | called from n8n |
| App Intents | *Gather the Empire*, *Ask the Empire*, *Configure Empire Webhook* in the Gabriel iOS app. | `_mc96-common/gabriel/ios/Gabriel/Intents/EmpireIntents.swift` |
| Local inventory | Every git repo, loose project and document on the Mac + `/Volumes/*`, with **file birth dates** (`stat -f %B`), first/last commit, size, remote. Nightly via launchd, committed to the hub. | `scripts/gather-local.sh`, `scripts/nightly-local-inventory.sh`, `empire/stack/launchd/` |
| Google | Drive (every file + `createdTime`), YouTube uploads, Gmail totals → `empire/google-inventory.json`, committed to the hub daily. FOSS path: `rclone lsjson --metadata`. | `empire/stack/n8n/google-inventory.json`, `scripts/gather-google.sh` |
| Claude on GOD | Daily harvest of Claude Code project memory, a session index (first prompt/turns/times — never full transcripts), `~/.claude-worktrees` branches, Gemini `mc96_*` reports and every `CLAUDE.md` → pushed to `Noizyfish/CLAUDE-TODAY` under `days/YYYY-MM-DD/`. Secrets excluded. Runs inside the nightly job. | `scripts/gather-claude.sh` |
| FOSS hitz | Every open-source dependency of the whole empire, licensed and verifiable: `empire/foss/hitz.json` → Brewfile / requirements / `GREATEST_HITZ.md`. `scripts/foss check` is the doctor. | `empire/foss/`, `scripts/foss`, `scripts/build-foss.mjs` |
| Scripts | Same jobs with zero infrastructure: clone everything, or mirror everything. | `scripts/gather.sh`, `scripts/mirror-to-forgejo.sh` |
| CLI | `empire gather / ask / brief / status / open` from any shell or launcher. | `scripts/empire` |

## Bring it up

```sh
cd empire/stack
cp .env.example .env            # fill in tokens; openssl rand -hex 32 for N8N_ENCRYPTION_KEY
docker compose up -d
```

1. **Forgejo** → http://localhost:3000 — finish the installer, create the `noizy` user, then *Settings → Applications → Generate Token* (repo + org scopes). Put it in `.env` as `FORGEJO_TOKEN`, then `docker compose up -d` again so n8n sees it.
2. **n8n** → http://localhost:5678 — create the owner account, *Workflows → Import from file* → `/workflows/empire-thru-line.json` (mounted read-only). Activate it.
3. **First mirror** (optional, instant): `FORGEJO_URL=http://localhost:3000 FORGEJO_TOKEN=… FORGEJO_OWNER=noizy scripts/mirror-to-forgejo.sh --all`
4. **Google** — in n8n create OAuth2 credentials named *Google Drive (NOIZY)*, *YouTube (NOIZY)*, *Gmail (NOIZY)* (one Google Cloud project, enable Drive/YouTube Data/Gmail APIs, redirect URL from n8n). Import `/workflows/google-inventory.json`, activate. `GITHUB_TOKEN` needs `contents:write` on the hub so it can commit `empire/google-inventory.json`.
5. **M2 Ultra nightly** — `sed "s#__REPO__#$PWD#g" empire/stack/launchd/ai.noizy.empire.nightly.plist > ~/Library/LaunchAgents/ai.noizy.empire.nightly.plist && launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.noizy.empire.nightly.plist`. Edit `empire/sources.json` to match your drives.
6. **iPhone** — build the Gabriel app, run the *Configure Empire Webhook* shortcut with `http://<host>:5678/webhook/empire` and your `INTENT_SHARED_SECRET`. Then say **“Bring everything together in Gabriel.”**

## Webhook contract

`POST /webhook/empire` with header `X-Noizy-Key: <INTENT_SHARED_SECRET>`

```json
{ "action": "gather" | "gather-all" | "digest", "question": "optional free text" }
```

Returns `{ ok, date, repoCount, mirrored, digest }`. The same digest is filed as an issue on the `Noizyfish--THEGATHERING` mirror so there's a permanent, searchable history of how the thru-line evolved.

## Daily rhythm

| Time | Who | What |
|---|---|---|
| 05:30 | launchd on M2 Ultra | `gather-local.sh --docs` → `local-inventory.json` + `EMPIRE.md` → push |
| 05:45 | n8n | Google inventory → `google-inventory.json` → commit |
| 06:00 | n8n | mirrors → Claude thru-line (GitHub + local + Google, 1996 → now) → Forgejo issue |
| any time | Siri / CLI | same pipeline on demand, answer spoken or printed |

## Keep the manifest honest

```sh
node scripts/build-empire.mjs          # regenerate empire/EMPIRE.md
node scripts/build-empire.mjs --check  # CI-style: fails if EMPIRE.md is stale or repos.json is invalid
```

New repo? Add one object to `empire/repos.json`, regenerate, commit. Forgejo, n8n, Siri and the docs all pick it up.
