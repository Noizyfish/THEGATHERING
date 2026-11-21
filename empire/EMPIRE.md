<!-- GENERATED FILE. Edit empire/repos.json then run: node scripts/build-empire.mjs -->

# MC96ECO UNIVERSE — THE NOIZY EMPIRE, ONE MAP

> 35 repositories across **RSPNOIZY** (org) and **Noizyfish** (personal), 2 planned, plus every git repo, loose project and document on the M2 Ultra and the drives. Hub: Noizyfish/THEGATHERING.

**killSwitchHolder:** RSP_001 | **covenant:** 75/25 | **canon:** noizy.ai

## How to pull everything into one workspace

```sh
scripts/gather.sh          # clones/pulls core + tooling into ~/NOIZY
scripts/gather.sh --all    # also personal vaults and upstream forks
scripts/gather.sh --list   # just print what would be cloned
```

## Flow of code

```
experiment  ->  RSPNOIZY/NOIZYLAB  (canonical lab)
                      |  fork
               Noizyfish/THEGATHERING  (this hub: manifest + working branch)
                      |  promote tested modules
               NOIZYVOX/governance/schemas  (planned)
                      |  consumed by
   NOIZYFISH . NOIZYKIDZ . NOIZYWORLD . DREAMCHAMBER . THE-OLD-GUARD . FISHMUSICINC . 2NDACT
```

## The Thru-Line

**Late 2025 → now: the vibe-coding era** — 2025-12 to 2026-11. 25 things born across GitHub. Read top to bottom: this is the story.

_No local inventory yet. Run `scripts/gather-local.sh` on the M2 Ultra with the drives mounted to colour in the local half of the story._

_No Google inventory yet. Import `empire/stack/n8n/google-inventory.json` into n8n (Drive + YouTube + Gmail) or run `scripts/gather-google.sh` with rclone._

- **2025-12**
  - `GitHub` [Noizyfish/GABRIEL](https://github.com/Noizyfish/GABRIEL) · GABRIEL · Gabriel agent master code location. _(→ 2026-09-20)_
  - `GitHub` [Noizyfish/NOIZYLAB-GABRIEL](https://github.com/Noizyfish/NOIZYLAB-GABRIEL) · GABRIEL · Gabriel master code location (earlier edition). _(→ 2026-04-04)_
  - `GitHub` [Noizyfish/NOIZYLAB_CONSOLE_v3](https://github.com/Noizyfish/NOIZYLAB_CONSOLE_v3) · NOIZYLAB · Lab console, v3. _(→ 2026-09-23)_
  - `GitHub` [Noizyfish/MC96-Mission-Control](https://github.com/Noizyfish/MC96-Mission-Control) · MC96 · MC96 Zero Latency AI Mission Control.
  - `GitHub` [Noizyfish/CODEMASTER](https://github.com/Noizyfish/CODEMASTER) · NOIZYLAB · Code archive: legacy scripts, backups and archived code.
  - `GitHub` [Noizyfish/NOIZYLAB](https://github.com/Noizyfish/NOIZYLAB) · NOIZYLAB · Shell automation and lab scripts. _(→ 2026-11-06)_
- **2026-02**
  - `GitHub` [Noizyfish/NOIZYFISH_THE_AQAURIUM](https://github.com/Noizyfish/NOIZYFISH_THE_AQAURIUM) · THE-AQUARIUM · Audio vault, 40-year collection. CLIENT#1 RSP001.
  - `GitHub` [Noizyfish/desktop-tutorial](https://github.com/Noizyfish/desktop-tutorial) · personal · GitHub Desktop tutorial repository.
- **2026-03**
  - `GitHub` [Noizyfish/CLAUDE-TODAY](https://github.com/Noizyfish/CLAUDE-TODAY) · NOIZY.AI · Daily Claude / Anthropic workspace. Audited 2026-11-21: repo is EMPTY (0 commits, default branch NOIZY.AI, never pushed since 2026-03-27). Filled nightly by scripts/gather-claude.sh from GOD.
  - `GitHub` [Noizyfish/swift-library](https://github.com/Noizyfish/swift-library) · NOIZYLAB · Swift library scaffolding.
- **2026-04**
  - `GitHub` [RSPNOIZY/NOIZYKIDZ](https://github.com/RSPNOIZY/NOIZYKIDZ) · NOIZYKIDZ · Youth division. Haptic music education. Deaf-first. Autism-calm. Every kid plays. _(→ 2026-05-06)_
  - `GitHub` [RSPNOIZY/DREAMCHAMBER](https://github.com/RSPNOIZY/DREAMCHAMBER) · DREAMCHAMBER · Creative residency. 500-Year Codex Creative Sanctuary for human-AI collaboration. _(→ 2026-10-13)_
  - `GitHub` [RSPNOIZY/RSPNOIZY](https://github.com/RSPNOIZY/RSPNOIZY) · NOIZY.AI · Organisation profile README. _(→ 2026-05-06)_
  - `GitHub` [RSPNOIZY/NOIZYLAB](https://github.com/RSPNOIZY/NOIZYLAB) · NOIZYLAB · Canonical upstream of this hub. Research lab + shared tooling core (MC96 common, Gabriel, voice engine, LIFELUV). _(→ 2026-05-30)_
  - `GitHub` [RSPNOIZY/NOIZYFISH](https://github.com/RSPNOIZY/NOIZYFISH) · NOIZYFISH · Producer ecosystem. THE REVOLUTION WILL SOUND LIKE YESTERDAY. _(→ 2026-05-06)_
  - `GitHub` [Noizyfish/THE-GATHERING](https://github.com/Noizyfish/THE-GATHERING) · THE-GATHERING · Community gathering point (personal edition).
  - `GitHub` [RSPNOIZY/THE-GATHERED](https://github.com/RSPNOIZY/THE-GATHERED) · THE-GATHERING · Community gathering point (org edition). _(→ 2026-05-06)_
- **2026-05**
  - `GitHub` [RSPNOIZY/THE-OLD-GUARD](https://github.com/RSPNOIZY/THE-OLD-GUARD) · THE-OLD-GUARD · Legacy artist catalog + ResurrectionOS: giving older Apple hardware new life. _(→ 2026-05-06)_
  - `GitHub` [RSPNOIZY/FISHMUSICINC](https://github.com/RSPNOIZY/FISHMUSICINC) · FISH MUSIC INC · Music catalog and licensing. Robert Plowman's original label entity. _(→ 2026-05-06)_
  - `GitHub` [RSPNOIZY/NOIZYWORLD](https://github.com/RSPNOIZY/NOIZYWORLD) · NOIZYWORLD · 10-Year Sovereign Commerce System.
  - `GitHub` [RSPNOIZY/2NDACT](https://github.com/RSPNOIZY/2NDACT) · 2NDACT · Universal Bridge App: AIVA + Replit + GOD.local + Cloudflare.
- **2026-09**
  - `GitHub` [Noizyfish/RSPOO1---Robert-Stephen-Plowman](https://github.com/Noizyfish/RSPOO1---Robert-Stephen-Plowman) · RSP001 · Founder repo.
- **2026-10**
  - `GitHub` [Noizyfish/aeon-magick-ai-computer-control](https://github.com/Noizyfish/aeon-magick-ai-computer-control) · NOIZY.AI · Universal AI computer-control KVM (REST API + MCP) with private networking stack. _(→ 2026-09-23)_
  - `GitHub` [Noizyfish/noizy-local-agents](https://github.com/Noizyfish/noizy-local-agents) · NOIZY.AI · Local-first NOIZY.AI agents for TagSpaces, Desktop Commander, DEVONthink and Obsidian.
- **2026-11**
  - `GitHub` [Noizyfish/THEGATHERING](https://github.com/Noizyfish/THEGATHERING) · NOIZYLAB · Working fork of RSPNOIZY/NOIZYLAB and home of this Empire manifest. _(→ 2026-05-30)_

## 1996 → late 2025: the archive (30 years of work on the drives)

_Nothing dated 1996–2025-11 yet. Mount the HDDs and run `scripts/gather-local.sh --docs`; every file's birth date fills this in automatically._

## Everything, grouped

27 things from GitHub clustered into 17 families by name and path (rules: `groups` in repos.json).

### GABRIEL · 2

- `GitHub` [Noizyfish/GABRIEL](https://github.com/Noizyfish/GABRIEL) · repo · born 2025-12-10
- `GitHub` [Noizyfish/NOIZYLAB-GABRIEL](https://github.com/Noizyfish/NOIZYLAB-GABRIEL) · repo · born 2025-12-10

### MC96 · 1

- `GitHub` [Noizyfish/MC96-Mission-Control](https://github.com/Noizyfish/MC96-Mission-Control) · repo · born 2025-12-18

### NOIZYVOX · 1

- `GitHub` [RSPNOIZY/NOIZYVOX](https://github.com/RSPNOIZY/NOIZYVOX) · planned

### NOIZYANTHROPIC · 1

- `GitHub` [RSPNOIZY/NOIZYANTHROPIC](https://github.com/RSPNOIZY/NOIZYANTHROPIC) · planned

### NOIZYLAB · 6

- `GitHub` [Noizyfish/NOIZYLAB_CONSOLE_v3](https://github.com/Noizyfish/NOIZYLAB_CONSOLE_v3) · repo · born 2025-12-17
- `GitHub` [Noizyfish/CODEMASTER](https://github.com/Noizyfish/CODEMASTER) · repo · born 2025-12-23
- `GitHub` [Noizyfish/NOIZYLAB](https://github.com/Noizyfish/NOIZYLAB) · repo · born 2025-12-28
- `GitHub` [Noizyfish/swift-library](https://github.com/Noizyfish/swift-library) · repo · born 2026-03-30
- `GitHub` [RSPNOIZY/NOIZYLAB](https://github.com/RSPNOIZY/NOIZYLAB) · repo · born 2026-04-05
- `GitHub` [Noizyfish/THEGATHERING](https://github.com/Noizyfish/THEGATHERING) · repo · born 2026-11-06

### NOIZYFISH · 1

- `GitHub` [RSPNOIZY/NOIZYFISH](https://github.com/RSPNOIZY/NOIZYFISH) · repo · born 2026-04-09

### NOIZYKIDZ · 1

- `GitHub` [RSPNOIZY/NOIZYKIDZ](https://github.com/RSPNOIZY/NOIZYKIDZ) · repo · born 2026-04-04

### DREAMCHAMBER · 1

- `GitHub` [RSPNOIZY/DREAMCHAMBER](https://github.com/RSPNOIZY/DREAMCHAMBER) · repo · born 2026-04-04

### THE-OLD-GUARD · 1

- `GitHub` [RSPNOIZY/THE-OLD-GUARD](https://github.com/RSPNOIZY/THE-OLD-GUARD) · repo · born 2026-05-05

### FISH MUSIC INC · 1

- `GitHub` [RSPNOIZY/FISHMUSICINC](https://github.com/RSPNOIZY/FISHMUSICINC) · repo · born 2026-05-05

### 2NDACT · 1

- `GitHub` [RSPNOIZY/2NDACT](https://github.com/RSPNOIZY/2NDACT) · repo · born 2026-05-06

### NOIZYWORLD · 1

- `GitHub` [RSPNOIZY/NOIZYWORLD](https://github.com/RSPNOIZY/NOIZYWORLD) · repo · born 2026-05-06

### THE-AQUARIUM · 1

- `GitHub` [Noizyfish/NOIZYFISH_THE_AQAURIUM](https://github.com/Noizyfish/NOIZYFISH_THE_AQAURIUM) · repo · born 2026-02-11

### NOIZY.AI · 4

- `GitHub` [Noizyfish/CLAUDE-TODAY](https://github.com/Noizyfish/CLAUDE-TODAY) · repo · born 2026-03-27
- `GitHub` [RSPNOIZY/RSPNOIZY](https://github.com/RSPNOIZY/RSPNOIZY) · repo · born 2026-04-04
- `GitHub` [Noizyfish/aeon-magick-ai-computer-control](https://github.com/Noizyfish/aeon-magick-ai-computer-control) · repo · born 2026-10-05
- `GitHub` [Noizyfish/noizy-local-agents](https://github.com/Noizyfish/noizy-local-agents) · repo · born 2026-10-29

### RSP001 · 1

- `GitHub` [Noizyfish/RSPOO1---Robert-Stephen-Plowman](https://github.com/Noizyfish/RSPOO1---Robert-Stephen-Plowman) · repo · born 2026-09-15

### THE-GATHERING · 2

- `GitHub` [Noizyfish/THE-GATHERING](https://github.com/Noizyfish/THE-GATHERING) · repo · born 2026-04-10
- `GitHub` [RSPNOIZY/THE-GATHERED](https://github.com/RSPNOIZY/THE-GATHERED) · repo · born 2026-04-29

### UNGROUPED · 1

- `GitHub` [Noizyfish/desktop-tutorial](https://github.com/Noizyfish/desktop-tutorial) · repo · born 2026-02-13

### Same thing, many places

Candidates to merge or delete. A local clone of its own GitHub repo is fine; two unrelated copies are not.

- **noizylab** → `GitHub` [RSPNOIZY/NOIZYLAB](https://github.com/RSPNOIZY/NOIZYLAB) · `GitHub` [Noizyfish/NOIZYLAB](https://github.com/Noizyfish/NOIZYLAB)
- **thegathering** → `GitHub` [Noizyfish/THEGATHERING](https://github.com/Noizyfish/THEGATHERING) · `GitHub` [Noizyfish/THE-GATHERING](https://github.com/Noizyfish/THE-GATHERING)


## Registry by tier

### CORE

> Brand repos that ARE the NOIZY Empire. Cloned by default.

| Repo | Brand | Role | Lang | Vis | Created | Last push |
|---|---|---|---|---|---|---|
| [RSPNOIZY/NOIZYKIDZ](https://github.com/RSPNOIZY/NOIZYKIDZ) | NOIZYKIDZ | Youth division. Haptic music education. Deaf-first. Autism-calm. Every kid plays. — [site](https://noizykidz.com) | HTML | public | 2026-04-04 | 2026-05-06 |
| [RSPNOIZY/DREAMCHAMBER](https://github.com/RSPNOIZY/DREAMCHAMBER) | DREAMCHAMBER | Creative residency. 500-Year Codex Creative Sanctuary for human-AI collaboration. | HTML | public | 2026-04-04 | 2026-10-13 |
| [RSPNOIZY/RSPNOIZY](https://github.com/RSPNOIZY/RSPNOIZY) | NOIZY.AI | Organisation profile README. — [site](https://noizy.ai) | — | public | 2026-04-04 | 2026-05-06 |
| [RSPNOIZY/NOIZYFISH](https://github.com/RSPNOIZY/NOIZYFISH) | NOIZYFISH | Producer ecosystem. THE REVOLUTION WILL SOUND LIKE YESTERDAY. — [site](https://noizyfish.com) | HTML | public | 2026-04-09 | 2026-05-06 |
| [Noizyfish/THE-GATHERING](https://github.com/Noizyfish/THE-GATHERING) | THE-GATHERING | Community gathering point (personal edition). | — | public | 2026-04-10 | 2026-04-10 |
| [RSPNOIZY/THE-GATHERED](https://github.com/RSPNOIZY/THE-GATHERED) | THE-GATHERING | Community gathering point (org edition). | — | public | 2026-04-29 | 2026-05-06 |
| [RSPNOIZY/THE-OLD-GUARD](https://github.com/RSPNOIZY/THE-OLD-GUARD) | THE-OLD-GUARD | Legacy artist catalog + ResurrectionOS: giving older Apple hardware new life. | — | public | 2026-05-05 | 2026-05-06 |
| [RSPNOIZY/FISHMUSICINC](https://github.com/RSPNOIZY/FISHMUSICINC) | FISH MUSIC INC | Music catalog and licensing. Robert Plowman's original label entity. | — | public | 2026-05-05 | 2026-05-06 |
| [RSPNOIZY/NOIZYWORLD](https://github.com/RSPNOIZY/NOIZYWORLD) | NOIZYWORLD | 10-Year Sovereign Commerce System. | — | public | 2026-05-06 | 2026-05-06 |
| [RSPNOIZY/2NDACT](https://github.com/RSPNOIZY/2NDACT) | 2NDACT | Universal Bridge App: AIVA + Replit + GOD.local + Cloudflare. | — | public | 2026-05-06 | 2026-05-06 |

### TOOLING

> Shared code, agents, consoles and archives that power the brands. Cloned by default.

| Repo | Brand | Role | Lang | Vis | Created | Last push |
|---|---|---|---|---|---|---|
| [Noizyfish/GABRIEL](https://github.com/Noizyfish/GABRIEL) | GABRIEL | Gabriel agent master code location. | Python | private | 2025-12-10 | 2026-09-20 |
| [Noizyfish/NOIZYLAB-GABRIEL](https://github.com/Noizyfish/NOIZYLAB-GABRIEL) | GABRIEL | Gabriel master code location (earlier edition). | — | private | 2025-12-10 | 2026-04-04 |
| [Noizyfish/NOIZYLAB_CONSOLE_v3](https://github.com/Noizyfish/NOIZYLAB_CONSOLE_v3) | NOIZYLAB | Lab console, v3. | Python | private | 2025-12-17 | 2026-09-23 |
| [Noizyfish/MC96-Mission-Control](https://github.com/Noizyfish/MC96-Mission-Control) | MC96 | MC96 Zero Latency AI Mission Control. | Python | public | 2025-12-18 | 2025-12-18 |
| [Noizyfish/CODEMASTER](https://github.com/Noizyfish/CODEMASTER) | NOIZYLAB | Code archive: legacy scripts, backups and archived code. | — | public | 2025-12-23 | 2025-12-23 |
| [Noizyfish/NOIZYLAB](https://github.com/Noizyfish/NOIZYLAB) | NOIZYLAB | Shell automation and lab scripts. | Shell | public | 2025-12-28 | 2026-11-06 |
| [Noizyfish/CLAUDE-TODAY](https://github.com/Noizyfish/CLAUDE-TODAY) | NOIZY.AI | Daily Claude / Anthropic workspace. Audited 2026-11-21: repo is EMPTY (0 commits, default branch NOIZY.AI, never pushed since 2026-03-27). Filled nightly by scripts/gather-claude.sh from GOD. | — | private | 2026-03-27 | 2026-03-27 |
| [Noizyfish/swift-library](https://github.com/Noizyfish/swift-library) | NOIZYLAB | Swift library scaffolding. | Swift | private | 2026-03-30 | 2026-03-30 |
| [RSPNOIZY/NOIZYLAB](https://github.com/RSPNOIZY/NOIZYLAB) | NOIZYLAB | Canonical upstream of this hub. Research lab + shared tooling core (MC96 common, Gabriel, voice engine, LIFELUV). — [site](https://noizylab.ca) | TypeScript | public | 2026-04-05 | 2026-05-30 |
| [Noizyfish/aeon-magick-ai-computer-control](https://github.com/Noizyfish/aeon-magick-ai-computer-control) | NOIZY.AI | Universal AI computer-control KVM (REST API + MCP) with private networking stack. | Rust | public | 2026-10-05 | 2026-09-23 |
| [Noizyfish/noizy-local-agents](https://github.com/Noizyfish/noizy-local-agents) | NOIZY.AI | Local-first NOIZY.AI agents for TagSpaces, Desktop Commander, DEVONthink and Obsidian. | — | private | 2026-10-29 | 2026-10-29 |
| [Noizyfish/THEGATHERING](https://github.com/Noizyfish/THEGATHERING) | NOIZYLAB | Working fork of RSPNOIZY/NOIZYLAB and home of this Empire manifest. — fork of `RSPNOIZY/NOIZYLAB` | TypeScript | public | 2026-11-06 | 2026-05-30 |

### PERSONAL

> Private vaults, people repos and scratch space. Cloned only with --all.

| Repo | Brand | Role | Lang | Vis | Created | Last push |
|---|---|---|---|---|---|---|
| [Noizyfish/NOIZYFISH_THE_AQAURIUM](https://github.com/Noizyfish/NOIZYFISH_THE_AQAURIUM) | THE-AQUARIUM | Audio vault, 40-year collection. CLIENT#1 RSP001. | — | private | 2026-02-11 | 2026-02-11 |
| [Noizyfish/desktop-tutorial](https://github.com/Noizyfish/desktop-tutorial) | — | GitHub Desktop tutorial repository. | — | private | 2026-02-13 | 2026-02-13 |
| [Noizyfish/RSPOO1---Robert-Stephen-Plowman](https://github.com/Noizyfish/RSPOO1---Robert-Stephen-Plowman) | RSP001 | Founder repo. | — | private | 2026-09-15 | 2026-09-15 |

### UPSTREAM

> Third-party forks kept for reference or contribution. Cloned only with --all.

| Repo | Brand | Role | Lang | Vis | Created | Last push |
|---|---|---|---|---|---|---|
| [Noizyfish/cloudflare-docs](https://github.com/Noizyfish/cloudflare-docs) | — | Fork: Cloudflare documentation. — fork of `cloudflare/cloudflare-docs` | MDX | public | 2025-11-29 | 2025-12-13 |
| [Noizyfish/refact](https://github.com/Noizyfish/refact) | — | Fork: Refact AI agent. — fork of `smallcloudai/refact` | Rust | public | 2025-12-25 | 2025-12-25 |
| [Noizyfish/brew](https://github.com/Noizyfish/brew) | — | Fork: Homebrew. — fork of `Homebrew/brew` | Ruby | public | 2025-12-26 | 2026-01-11 |
| [Noizyfish/copilot-cli](https://github.com/Noizyfish/copilot-cli) | — | Fork: GitHub Copilot CLI. — fork of `github/copilot-cli` | Shell | public | 2025-12-29 | 2025-12-29 |
| [Noizyfish/awesome-selfhosted](https://github.com/Noizyfish/awesome-selfhosted) | — | Fork: awesome-selfhosted list. — fork of `awesome-selfhosted/awesome-selfhosted` | — | public | 2026-04-25 | 2026-04-18 |
| [RSPNOIZY/cloudflare-docs](https://github.com/RSPNOIZY/cloudflare-docs) | — | Fork: Cloudflare documentation (org copy). — fork of `cloudflare/cloudflare-docs` | MDX | public | 2026-04-26 | 2026-05-13 |
| [Noizyfish/agent-skills](https://github.com/Noizyfish/agent-skills) | — | Fork: Agent Skills for Firebase. — fork of `firebase/agent-skills` | JavaScript | public | 2026-07-29 | 2026-07-28 |
| [Noizyfish/brave-browser](https://github.com/Noizyfish/brave-browser) | — | Fork: Brave browser. — fork of `brave/brave-browser` | — | public | 2026-08-06 | 2026-08-06 |
| [Noizyfish/homebridge-config-ui-x](https://github.com/Noizyfish/homebridge-config-ui-x) | — | Fork: Homebridge UI. — fork of `homebridge/homebridge-config-ui-x` | TypeScript | public | 2026-09-23 | 2026-09-21 |
| [Noizyfish/sonobus](https://github.com/Noizyfish/sonobus) | — | Fork: SonoBus real-time network audio. — fork of `sonosaurus/sonobus` | C++ | public | 2026-09-30 | 2026-09-04 |

### PLANNED

> Referenced in doctrine but no repository exists yet. Never cloned.

| Repo | Brand | Role | Lang | Vis | Created | Last push |
|---|---|---|---|---|---|---|
| [RSPNOIZY/NOIZYVOX](https://github.com/RSPNOIZY/NOIZYVOX) | NOIZYVOX | Voice + schema core. Target home for governance/schemas promoted from NOIZYLAB. — [site](https://noizyvox.com) | — | public | — | — |
| [RSPNOIZY/NOIZYANTHROPIC](https://github.com/RSPNOIZY/NOIZYANTHROPIC) | NOIZYANTHROPIC | AI governance + doctrine. | — | public | — | — |
