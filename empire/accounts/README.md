# Accounts — complete sign-up for the empire's external rails

Four providers, one command each. `empire signup` reads [`providers.json`](providers.json) (the single source of truth), opens the right pages, **speaks the steps** (macOS `say`, Daniel), collects keys with silent input, writes them to `empire/stack/.env` (mode 600) **and** the macOS Keychain (`ai.noizy.empire.<KEY>`), then verifies them live.

```bash
scripts/empire signup                 # status table — which providers are configured + verified
scripts/empire signup cloudflare      # guided flow (opens dash + token page, prompts, verifies)
scripts/empire signup proton
scripts/empire signup infomaniak
scripts/empire signup todaq --auto    # creates the Qatom account via API — no browser
scripts/empire signup --all           # all four in order
scripts/empire signup verify          # re-verify everything stored
scripts/empire signup show todaq      # read the plan without doing anything
```

| Provider | What it is for us | Credential(s) | Verified by |
|---|---|---|---|
| **Cloudflare** | The backbone already (20 `wrangler.toml` in GABRIEL: Workers, D1, KV, R2, Workers AI, Pages). Token unlocks the nightly **ALL CLOUDFLARE** inventory + deploys from one identity. | `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID` | `GET /user/tokens/verify` → `active` |
| **Proton** | Encrypted identity: Mail on `noizy.ai`, Drive (off-site encrypted copy), **Pass** (where every key below also lives), Calendar, VPN. | Bridge user/password (IMAP 1143 / SMTP 1025) | Bridge port open on GOD |
| **Infomaniak** | Swiss sovereign hosting with a real API: kDrive (AQUARIUM mirror), kSuite mail, Public Cloud, **AI Tools** (OpenAI-compatible Swiss LLMs — Gabriel's fallback when Anthropic is unreachable). | `INFOMANIAK_TOKEN`, Drive ID, AI product ID, WebDAV app-password | `GET /1/profile` → `success` |
| **TODAQ Micro (Qatom)** | Micropayments, 0% take rate, sub-second settlement, every payment a TODA file with proof of provenance. Pay-per-line voice assets, LIFELUV passes, agent paywalls. | client id/secret, public secret, twin id/key, DQ — **minted by the API** | token + twin readable (`qatom.mjs whoami`) |

## Order of operations (one sitting, ~45 min)

1. **Proton first** — create the account, install **Proton Pass**, make vault *NOIZY Empire*. Everything else gets pasted there as you go.
2. **Cloudflare** — you already have it; make the token, run `empire signup cloudflare`, then `empire run --only cloudflare` → `empire/cloudflare-inventory.json` with every zone/Worker/D1/KV/R2/Pages/Access/tunnel **and** drift (declared in a `wrangler.toml` but not deployed, or deployed but in no repo).
3. **Proton domain** — add `noizy.ai` in Proton, create the DNS records in Cloudflare, verify, Bridge on GOD, `empire signup proton`.
4. **Infomaniak** — account → kSuite/kDrive → API token → AI Tools → `empire signup infomaniak`.
5. **TODAQ** — `empire signup todaq --auto` (staging). Fund the wallet at `load.m.todaq.net`, pay your own 0.25 test item, watch `qatom.mjs revenue`. Then `TODAQ_ENV=production empire signup todaq --auto`.

Then `empire doctor` should be all green, and `empire run` picks up the new stages automatically.

## How each one plugs into the stack

```
Cloudflare ──► cloudflare-inventory.json ──► EMPIRE.md timeline + groups + drift; n8n/Gabriel deploys via wrangler
Proton     ──► n8n IMAP/SMTP (Bridge) · rclone proton: (docs backup) · Pass (secrets)
Infomaniak ──► rclone kdrive: (AQUARIUM mirror) · OpenAI-compatible fallback for Gabriel brain · Public Cloud for Forgejo/n8n off-GOD
TODAQ      ──► empire/accounts/todaq/qatom.mjs (v4 client) · payment-js on the PWA · WKWebView in LUCY · n8n ledger → Forgejo
```

## Security

- `.env` is gitignored and `chmod 600`; secrets are also stored in Keychain (`security find-generic-password -s ai.noizy.empire.CLOUDFLARE_API_TOKEN -w`).
- Qatom returns `client_secret` and `twin.key` **once**. `empire signup todaq --auto` stores them immediately; copy them into Proton Pass the same minute.
- Never ship `TODAQ_CLIENT_SECRET`, `TODAQ_TWIN_KEY` or any access token to a browser or the iPhone. Only `TODAQ_PUBLIC_SECRET` and commodity hashes go client-side.
- Cloudflare token: scoped permissions listed in `providers.json` — no Global API Key.

Details for TODAQ (API shapes, payment element, redeem flow, what the SDKs really are): [`todaq/README.md`](todaq/README.md).
