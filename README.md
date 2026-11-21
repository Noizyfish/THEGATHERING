# NOIZYLAB

> Experimental research lab and shared tooling core for the NOIZY Empire | MC96ECO Universe.

---

## Bring Everything Together

Thirty years of work (1996 → today): two GitHub identities, an M2 Ultra, a shelf of drives, and all of Google (Drive, YouTube, Gmail) — found, dated by **file birth date**, grouped by brand family, and told as **one chronological story** that recolours itself every night.

| | |
|---|---|
| **[empire/EMPIRE.md](empire/EMPIRE.md)** | The map: thru-line by month, 1996+ archive by year, everything grouped by brand family, duplicates and unbacked work flagged. Generated. |
| **[empire/repos.json](empire/repos.json)** | Single source of truth: every repo across RSPNOIZY + Noizyfish, tiers, grouping rules, story anchors. |
| **[empire/sources.json](empire/sources.json)** | Local roots to scan on the Mac + `/Volumes/*`. |
| **[empire/STACK.md](empire/STACK.md)** | Forgejo + n8n + Claude + App Intents. All FOSS, self-hosted, one `docker compose up`. |
| **[empire/foss/GREATEST_HITZ.md](empire/foss/GREATEST_HITZ.md)** | **FOSS GREATEST HITZ** — every open-source piece the empire runs on (license, role, install), the non-FOSS links and their exits. `scripts/foss install` rebuilds GOD from zero. |
| **[noizystdz/](noizystdz/README.md)** | **NOIZYSTDZ** — BlackHole 16ch interactive studio → consent-gated **NOIZYVOX** corpus; 50 voices for Friday; **LINA**. |
| **[engr/](engr/HOMEKIT.md)** | **ENGR** — Logic Pro / all apps / HomeKit control plane; 14-bit MIDI, Open Stage Control surface, NoizyKit (Apple frameworks). |
| **[noizybeast/](noizybeast/README.md)** | **NOIZYBEAST.IDE** — Tauri + RustDesk window onto all of it. |
| **[empire/shortcuts/README.md](empire/shortcuts/README.md)** | Siri / Shortcuts on every device. |

```sh
scripts/gather.sh                    # clone or pull every repo into ~/NOIZY
scripts/gather-local.sh --docs       # on the M2 Ultra: inventory repos, loose projects, docs (by file birth date)
scripts/gather-local.sh --push       # …and push every local git repo into Forgejo
scripts/mirror-to-forgejo.sh --all   # pull-mirror every GitHub repo into Forgejo
scripts/gather-google.sh             # Drive inventory via rclone (or the n8n Google workflow)
scripts/gather-claude.sh             # Claude Code memory/sessions/worktrees on GOD → Noizyfish/CLAUDE-TODAY
node scripts/build-empire.mjs        # regenerate empire/EMPIRE.md
scripts/foss install                 # FOSS GREATEST HITZ: Brewfile + uv + npm → GOD rebuilt from zero; `scripts/foss check` = doctor
scripts/empire ask "what did I build in April 2026?"
```

Say **"Bring everything together in Gabriel"** and the same pipeline runs from your phone.

---

## What Lives Here

NOIZYLAB is the internal research and integration layer of the NOIZY sovereign infrastructure.
It houses shared modules, cross-brand utilities, MC96 common libraries, and agent scaffolding
that power every brand in the empire without belonging to any single one.

| Layer | Contents |
|---|---|
| `_mc96-common/` | Shared MC96 router utilities, Gabriel agent sync modules, Gabriel iOS app + App Intents |
| `empire/` | Empire manifest, generated map, self-hosted stack (Forgejo, n8n, launchd) |
| `scripts/` | gather / mirror / inventory / `empire` CLI |
| Swift / TypeScript | Native iOS scaffolding and cross-platform tooling |
| HTML / JS / CSS | Web panel prototypes and SideWindow integrations |
| Shell | Startup, deploy, and automation scripts |

---

## Role in the Empire

- Supplies shared code consumed by NOIZYVOX, NOIZYANTHROPIC, and RSPNOIZY-THE-GATHERING
- Hosts the MC96 common envelope contracts before promotion to NOIZYVOX governance
- Experimental ground for new schema, API shape, and agent protocol designs
- Feeds tested modules upward into the canonical schema pack at `NOIZYVOX/governance/schemas/`

---

## Part of the NOIZY Empire

| Brand | Role |
|---|---|
| [NOIZY.AI](https://noizy.ai) | Sovereign AI infrastructure |
| [NOIZYFISH](https://noizyfish.com) | Producer ecosystem |
| [NOIZYKIDZ](https://noizykidz.com) | Youth division |
| [NOIZYVOX](https://noizyvox.com) | Voice + schema core _(repo planned)_ |
| [NOIZYLAB](https://noizylab.ca) | Research + shared tooling |
| [DREAMCHAMBER](https://github.com/RSPNOIZY/DREAMCHAMBER) | Creative residency |
| [THE-OLD-GUARD](https://github.com/RSPNOIZY/THE-OLD-GUARD) | Legacy artist catalog |
| [THE-GATHERING](https://github.com/RSPNOIZY/THE-GATHERED) | Community gathering point |
| NOIZYANTHROPIC | AI governance + doctrine _(repo planned; doctrine lives in `_mc96-common/gabriel/doctrine/`)_ |
| [THE-AQUARIUM](https://github.com/Noizyfish/NOIZYFISH_THE_AQAURIUM) | Audio vault -- CLIENT#1 RSP001 |

**killSwitchHolder:** RSP_001 | **covenant:** 75/25 | **canon:** noizy.ai
