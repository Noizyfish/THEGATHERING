<!-- Compiled 2026-11-21 by research subagent. Sources: gh CLI (GitHub API, token = Noizyfish integration token), local clones in /root/copilot-worktrees. -->

# SUPERSTACK — AI research & vibe-coding inventory (NOIZY / MC96ECOUNIVERSE)

> Scope searched: GitHub users `Noizyfish`, `RSPNOIZY`, and orgs `NOIZYLAB-io`, `NOIZY-ai` (the two orgs were *discovered*, they are not in the
> manifest `empire/repos.json`). Sizes are GitHub `diskUsage` (KB → MB). Dates are repo `createdAt` / `pushedAt` (UTC).
> Brand spelling: NOIZY (with Z).

## 0. Headline findings (read this first)

1. **There is no artifact literally named "SUPERSTACK" anywhere reachable on GitHub** (repos, code, commits, issues/PRs, gists, local clones). See §1.
2. **Two GitHub organisations exist that the manifest does not list**, and they hold the *earliest* and the *largest* material:
   `NOIZYLAB-io` (created 2025-11-20) and `NOIZY-ai` (created 2025-12-14). Both contain commits authored by `Noizyfish`.
3. **Nothing on GitHub pre-dates Sep 2025.** `Noizyfish` account created 2025-09-10; first repo 2025-11-20. The "Jul 2024 →" part of the story is **not on GitHub**
   (it must live on the M2 Ultra / drives / Google — see §5). The GitHub-visible burst is Nov 2025 → Nov 2026 (~12 months), not 30.
4. **`RSPNOIZY` is a *User* account, not an org** (`gh api users/RSPNOIZY` → `type: User`, created 2026-03-29), although `empire/repos.json`/`EMPIRE.md` call it "(org)".
5. **Planned repos do not exist**: `NOIZYVOX`, `NOIZYANTHROPIC`, `NOIZYSTDZ`, `NOIZYBEAST`, `LIFELUV`, `AEON`, `GET-GIT-GOOD` → 404 under both users
   (GET-GIT-GOOD exists only as a *directory*: `Noizyfish/GABRIEL/products/get-git-good`; LIFELUV only as a commit/module inside `RSPNOIZY/NOIZYLAB`).
6. **Provenance flag:** `Noizyfish/GABRIEL` README and `funding/anthropic-fellows-2026/*` are written for applicant **"Matthew Olson-Roos / NoizyLab.ai"**
   (README: "Matthew Olson-Roos + Claude … Rob/Matthew"), not Robert Stephen Plowman. Treat authorship/identity of that content as **unverified** (§5).

## 1. Exact matches for SUPERSTACK

**None.** Searches performed (all returned 0 hits, valid responses — not errors):

| Search | Scope | Result |
|---|---|---|
| code `superstack`, `"super stack"`, `super-stack`, `SUPER_STACK` | `user:Noizyfish`, `user:RSPNOIZY`, `org:NOIZYLAB-io`, `org:NOIZY-ai` | 0 each (`superstack.ai` also 0 earlier, but that run was rate-limited; the rerun of the 4 base variants is authoritative) |
| code `"vibe coding"` | all 4 scopes | 0 |
| code `vibe` | Noizyfish → 15 hits; RSPNOIZY → 8; both orgs → 0 | all hits are incidental (see below) |
| repos `superstack`, `super stack`, `super-stack`, `vibe` | `--owner Noizyfish` / `RSPNOIZY` | 0 |
| commits `superstack` | `author:Noizyfish`, `author:RSPNOIZY` | 0 / 0 |
| commits `vibe` | `author:Noizyfish`, `author:RSPNOIZY` | 0 / 0 |
| issues + PRs `superstack` | 4 scopes | 0 |
| `git log --all --grep` for `super.?stack`, `vibe` | local clones GABRIEL, THEGATHERING, MC96-Mission-Control | 0 |
| gists | `gh gist list` | **not reachable** — token is an integration token (`Resource not accessible by integration (viewer.gists)`) |

"vibe" hits are code identifiers, not the concept: `vibe=` parameter in `GABRIEL/CODEMASTER/harvested/github-harvest/turbo_gabriel.py`, `gabriel_genesis.py`
(`run_genesis(project_name, style, vibe)`), `memcell_core.py` (keyword list), `portal.py`/`app.py` ("ANALYZE AUDIO VIBE"); and
`_mc96-common/gabriel/agents/gabriel.morning.md:350` ("Prefer proof over vibe.") + `doctrine/DISCORD_FLEET.md:9` (replicated into RSPNOIZY/{NOIZYLAB,NOIZYFISH,NOIZYKIDZ,DREAMCHAMBER}).
The only "vibe-coding" phrase in any file is the **storyLabel** `"Late 2025 → now: the vibe-coding era"` in
`THEGATHERING/empire/repos.json:7` / `empire/EMPIRE.md:31` (that is the user's own framing, written in this hub).

**Closest conceptual matches to "a super stack"** (names differ, same idea — use as SUPERSTACK anchors):
- `Noizyfish/THEGATHERING:empire/STACK.md` — "Forgejo + n8n + Claude + App Intents. All FOSS, self-hosted, one `docker compose up`."
- `NOIZY-ai/noizy.ai:docs/IDEATION.md` — "NOIZY Ideation Compendium" (the system map: NOIZY.AI, DreamChamber, GABRIEL, HEAVEN, NOIZY PROOF, Consent Gateway, NOIZYVOX, NOIZYFISH, NOIZYLAB, NOIZYKIDZ).
- `NOIZY-ai/noizy.ai:NOIZYLAB/gabriel/packages/prompts/PROMPT_STACK.md` and `.../CODEMASTER/_ORGANIZED/05_TOOLS/gabriel_packages/prompts/PROMPT_STACK.md` — a prompt stack.
- `NOIZYLAB-io/NOIZYLAB:apple-ultimate-stack.md`, `apple-singularity.md`, `apple-god-mode.md` — Apple/M2 Ultra "ultimate stack" notes.
- `NOIZY-ai/noizy.ai:NOIZYLAB/SUPERSONIC_2.1_ARCHITECTURE.md`; `NOIZYLAB-io/NOIZYLAB:supersonic.sh` — "SUPERSONIC" (nearest *name* to SUPERSTACK; likely a different thing, unverified).
- `Noizyfish/GABRIEL:CLAUDE.md` — Claude Code rules file ("Inspired by Boris Cherny's workflow") = the vibe-coding operating manual.

## 2. "AI research" repo inventory

Owner scopes: **U1** = user Noizyfish, **U2** = user RSPNOIZY, **O1** = org NOIZYLAB-io, **O2** = org NOIZY-ai. F = fork of third party.
Size in MB (diskUsage/1024). "Commits" from API `Link: rel=last`.

### 2a. Original work (not forks)

| repo | owner | created | last push | lang | size | what it is | research theme tags |
|---|---|---|---|---|---|---|---|
| [NOIZYLAB-io/NOIZYLAB](https://github.com/NOIZYLAB-io/NOIZYLAB) | O1 | 2025-11-20 | 2026-10-29 | Go* | 412 MB | "United Nations of Code": M2-Ultra + HP-OMEN integration platform; 38 branches, 24 commits by Noizyfish, 13 by RSPNOIZY. Has `AGENTS/`, `.windsurf/`, `.claude/`, gRPC bridge, DREAMCHAMBER, Unity SDK, `mission-run-2025120*` logs, GORUNFREE bootstrap | agents, orchestration, M2-Ultra tuning, voice, Cloudflare Workers |
| [Noizyfish/GABRIEL](https://github.com/Noizyfish/GABRIEL) | U1 | 2025-12-10 | 2026-09-20 | Python | 9.6 MB (4,546 files, 8 commits) | Master code location: `agents/`, `automation/{ai-agents,mcp-server,voice-first,hotrod-turbo}`, `workers/{gabriel-mcp,aeon-god-kernel}`, `portal/`, `products/get-git-good`, `funding/{anthropic-fellows-2026,anthology-fund,google-cloud-startup}`; "MEGA HARVEST: 4,027 code files" (2026-01-05); MCP Worker added by Copilot 2026-05-31 | multi-agent constellation, MCP, voice-first/accessibility, HOTROD cache, Claude Code rules, safety/AI-fellows proposals |
| [Noizyfish/NOIZYLAB_CONSOLE_v3](https://github.com/Noizyfish/NOIZYLAB_CONSOLE_v3) | U1 | 2025-12-17 | 2026-09-23 | Python | 0.2 MB (29 commits) | 2025-12-17 marathon: Console v3.1 → GABRIEL V1 → v12 → HYPERVELOCITY (MLX LLM, Metal FFT, uvloop) → GABRIEL INFINITY "Temporal OS" → GORUNFREE; Gemini 3 Flash, OpenAI Realtime, Runway/Luma/Veo/Chatterbox/RVC | local LLM (MLX), M2-Ultra perf, multi-voice, temporal memory graph, creative-AI arsenal |
| [Noizyfish/MC96-Mission-Control](https://github.com/Noizyfish/MC96-Mission-Control) | U1 | 2025-12-18 | 2025-12-18 | Python | 30 KB (2 commits) | "MC96 Zero Latency AI Mission Control": server, MemCell core, consolidator, global todo executor, portal | orchestration, memory cells |
| [Noizyfish/NOIZYLAB-GABRIEL](https://github.com/Noizyfish/NOIZYLAB-GABRIEL) | U1 | 2025-12-10 | 2026-04-04 | – | 8 KB (2 commits; CLAUDE.md + README) | Earlier GABRIEL edition; defines the agent family (Gabriel, Lucy, Shirley, Pops, Engr Keith, …) "Part of NOIZY.AI Enterprise (NOIZYLAB-io)" | agent personas |
| [RSPNOIZY/DREAMCHAMBER](https://github.com/RSPNOIZY/DREAMCHAMBER) | U2 | 2026-04-04 | 2026-10-13 | HTML | 142 MB (16 commits) | "MC96 AI Family Command Center": one prompt file per agent (CLAUDE, LUCY, SHIRL, POPS, DREAM, ENGR_KEITH, HEAVEN, CB01), CrewAI swarm scaffold, `WALKING_IN_THE_DREAMS/` (OSC/Lemur), `wisdom/`, Claude Code constitutional GitHub Action (2026-10-13) | agent role prompts, CrewAI, consent, human-AI creative collaboration |
| [RSPNOIZY/NOIZYLAB](https://github.com/RSPNOIZY/NOIZYLAB) | U2 | 2026-04-05 | 2026-05-30 | TS | 0.2 MB (7 commits) | "Experimental research lab & shared tooling core"; `_mc96-common` (68-file Gabriel corpus synced from NOIZYANTHROPIC), pure-TypeScript sovereign voice pipeline, LIFELUV | research lab core, voice pipeline, doctrine |
| [Noizyfish/THEGATHERING](https://github.com/Noizyfish/THEGATHERING) | U1 | 2026-11-06 | 2026-11-21 | TS | 0.2 MB (local clone 207 files) | Fork of RSPNOIZY/NOIZYLAB — **this hub**: `empire/{repos.json,EMPIRE.md,STACK.md}`, `scripts/gather*.sh`, `empire` CLI, NOIZYSTDZ→NOIZYVOX studio, GORUNFREE pipeline. Recent commits: MC96ECOUNIVERSE history, CLAUDE-TODAY nightly harvest | empire manifest, self-hosted stack, n8n, Forgejo, Claude |
| [NOIZY-ai/noizy.ai](https://github.com/NOIZY-ai/noizy.ai) | O2 | 2025-12-15 | 2026-11-09 | (Go*) | 180 MB, 23,477 tree entries | **Technically a fork of `cisco/openh264`** (5,410 commits of upstream history) repurposed as the "canonical NOIZY master": `heaven/` agent profiles, `schemas/`, `cloudflare/` workers, `n8n/` (8 workflows), `.claude/commands/*` (build, dreamchamber, escape, gabriel, noizyvox, brutal-polish), `docs/IDEATION.md`. On 2026-11-09 Noizyfish imported `NOIZYLAB`, `ARCHIVE`, `CODE_2026`, `nextjs-with-supabase` into it | consent-native AI, 75/25 covenant, provenance, agent routing, Claude Code slash-commands |
| [NOIZYLAB-io/NOIZY.ai](https://github.com/NOIZYLAB-io/NOIZY.ai) | O1 | 2025-12-12 | 2026-09-26 | JS | 0.9 MB | Contains `heaven/` + README stub | agent routing (stub) |
| [Noizyfish/noizy-local-agents](https://github.com/Noizyfish/noizy-local-agents) | U1 | 2026-10-29 | 2026-10-29 | – | 0 (1 commit, README only) | "Local-first, open-source NOIZY.AI agents for TagSpaces, Desktop Commander, DEVONthink and Obsidian." Default branch `NOIZY.AI` | local agents, MCP tool bridges (idea stage) |
| [RSPNOIZY/2NDACT](https://github.com/RSPNOIZY/2NDACT) | U2 | 2026-05-06 | 2026-05-06 | – | 4 KB | Universal Bridge App: AIVA + Replit SideWindow + GOD.local + Cloudflare (README only) | integration layer, voice agent |
| [RSPNOIZY/THE-OLD-GUARD](https://github.com/RSPNOIZY/THE-OLD-GUARD) | U2 | 2026-05-05 | 2026-05-06 | – | 30 KB (8 commits) | ResurrectionOS blueprint, MC96 DB schema + router contract | hardware revival, schema/contract design |

### 2b. Third-party forks with AI/agent relevance (reference, not original research)

| repo | owner | forked | last push | lang | size | note |
|---|---|---|---|---|---|---|
| [Noizyfish/aeon-magick-ai-computer-control](https://github.com/Noizyfish/aeon-magick-ai-computer-control) | U1 | 2026-10-05 | 2026-09-23 | Rust | 66 MB | Fork of `AEON-7/aeon-magick-ai-computer-control` — AI computer-control KVM (REST + MCP, Tor/I2P). **Relation to user's "AEON" project unverified** (name overlap with `GABRIEL/workers/aeon-*`, `docs/AEON-POWER-README.md`). |
| [Noizyfish/refact](https://github.com/Noizyfish/refact) | U1 | 2025-12-25 | 2025-12-25 | Rust | 134 MB | Fork of `smallcloudai/refact` — AI coding agent. |
| [Noizyfish/copilot-cli](https://github.com/Noizyfish/copilot-cli) | U1 | 2025-12-29 | 2025-12-29 | Shell | 0.1 MB | Fork of `github/copilot-cli`. |
| [Noizyfish/agent-skills](https://github.com/Noizyfish/agent-skills) | U1 | 2026-07-29 | 2026-07-28 | JS | 0.6 MB | Fork of `firebase/agent-skills`. |
| [Noizyfish/NOIZYLAB](https://github.com/Noizyfish/NOIZYLAB) | U1 | 2025-12-28 | 2026-11-06 | Shell | 408 MB | Fork of `NOIZYLAB-io/NOIZYLAB` (his own org); push of 2026-11-06 is the newest. |

### 2c. Not research (kept for completeness)
Forks: `cloudflare-docs` (Noizyfish 2025-11-29, RSPNOIZY 2026-04-26), `brew`, `awesome-selfhosted`, `brave-browser`, `homebridge-config-ui-x`, `sonobus`.

## 3. Vibe-coding timeline ("the crazy months")

Repos created per month, all four owners (U1+U2+O1+O2). `own` = non-fork. Source: `gh repo list <owner> --json createdAt,isFork`.

| Month | total | own | repos created | dominant themes / what happened |
|---|---|---|---|---|
| ≤ 2025-08 | 0 | 0 | – | **No GitHub footprint.** Account `Noizyfish` created 2025-09-10 (`gh api users/Noizyfish`). |
| 2025-09 / 10 | 0 | 0 | – | Account exists, no repos visible. |
| 2025-11 | 2 | 1 | `NOIZYLAB-io/NOIZYLAB` (11-20), fork `cloudflare-docs` (11-29) | Org `NOIZYLAB-io` founded 2025-11-20; Cloudflare-centric stack begins. |
| **2025-12** | **12** | **7** | `NOIZY-ai/noizy.ai`(fork), `NOIZYLAB-io/NOIZY.ai`, `docs.github`, `Noizyfish/{GABRIEL, NOIZYLAB-GABRIEL, NOIZYLAB_CONSOLE_v3, MC96-Mission-Control, CODEMASTER}`, forks `refact`, `brew`, `copilot-cli`, `NOIZYLAB` | **Peak burst #1.** 2025-12-17 alone = ~29 commits in NOIZYLAB_CONSOLE_v3 (GABRIEL v1→v12, MLX, Gemini 3 Flash, GORUNFREE). 12-18 MC96 Mission Control; 12-20 "MC96UNIVERSE AGENTS registry … Windsurf workflows"; "Block ALL audio/video from GitHub"; 12-28 NOIZYVOX Unity SDK v1.0.0. Tools: Claude Code, Copilot SWE agent (PR #1 on CONSOLE_v3, 12-20), Windsurf, Gemini, Claude "claude/deploy-cloudflare-worker" branch. |
| 2026-01 | 0 | 0 | (commits only) | GABRIEL: Slack Bolt v2.0 + CODEMASTER (01-02, Copilot), "OneDrive harvest" + "MEGA HARVEST 4,027 code files" + ORGANIZE (01-05), PROJECT_STATUS "100% organized" (01-07); Anthropic Fellows 2026 application (deadline 2026-01-12); Copilot custom agent on NOIZYLAB-io (01-20). |
| 2026-02 | 2 | 2 | `NOIZYFISH_THE_AQAURIUM` (empty), `desktop-tutorial` (empty) | Quiet; Copilot instructions added to GABRIEL (02-22). Audio-vault placeholder. |
| 2026-03 | 2 | 2 | `CLAUDE-TODAY` (empty), `swift-library` | Claude daily-workspace concept; Swift scaffold. `RSPNOIZY` account created 03-29. |
| **2026-04** | **9** | **7** | `RSPNOIZY/{RSPNOIZY, NOIZYKIDZ, DREAMCHAMBER, NOIZYLAB, NOIZYFISH, THE-GATHERED, cloudflare-docs(fork)}`, `Noizyfish/{THE-GATHERING, awesome-selfhosted(fork)}` | **Burst #2 — brand-split.** 04-04 DREAMCHAMBER: one commit per agent prompt (CLAUDE, LUCY, SHIRL, POPS, DREAM, ENGR_KEITH, HEAVEN, CB01) + CrewAI swarm scaffold. 04-05 NOIZYLAB research lab; 04-20 "sync Gabriel corpus from NOIZYANTHROPIC · 68 files" into every brand repo. |
| **2026-05** | **4** | **4** | `RSPNOIZY/{FISHMUSICINC, THE-OLD-GUARD, NOIZYWORLD, 2NDACT}` | **Burst #3 — empire completion.** 05-05/06 "10-brand canonical table" pushed to all repos; 05-15 voice pipeline in pure TypeScript + LIFELUV; 05-31 GABRIEL MCP Worker (Copilot, #9). |
| 2026-06 | 0 | 0 | – | No new repos or pushes seen. |
| 2026-07 | 1 | 0 | fork `agent-skills` | Reference-gathering (Firebase agent skills). |
| 2026-08 | 1 | 0 | fork `brave-browser` | – |
| 2026-09 | 3 | 1 | `RSPOO1---Robert-Stephen-Plowman` (founder repo), forks `homebridge-config-ui-x`, `sonobus` | GABRIEL push 09-20; CONSOLE_v3 push 09-23; NOIZY.ai (O1) push 09-26. Real-time audio (SonoBus) + HomeKit interest. |
| **2026-10** | **2** | **1** | `noizy-local-agents`, fork `aeon-magick-ai-computer-control` | DREAMCHAMBER gets Claude Code constitutional GitHub Action (10-13); NOIZYLAB-io/NOIZYLAB push 10-29. |
| **2026-11** | **1** | **0** (fork) | `THEGATHERING` (11-06) | **Burst #4 — consolidation.** 11-09 mass import into `NOIZY-ai/noizy.ai` ("NOIZY ideation compendium", ARCHIVE, CODE_2026, NOIZYLAB); 11-21 empire manifest, MC96ECOUNIVERSE history, CLAUDE-TODAY nightly harvest, NOIZYSTDZ studio. |

Totals found: **39 repos** = Noizyfish 24 + RSPNOIZY 11 + NOIZYLAB-io 3 + NOIZY-ai 1 (of which ≈14 are third-party forks).
Pattern: build burst (Dec 2025) → harvest/organise (Jan) → quiet (Feb–Mar) → brand-split + agent prompts (Apr–May) → forks-as-research (Jul–Oct) → consolidate (Nov).
Caveat: commit counts are lower bounds; repo history of `NOIZYLAB-io/NOIZYLAB` was "SLIMMED" (oldest commit 2025-12-05, "Archives on 12TB"), so work before that is not in git history.

## 4. Recommended grouping

### 4a. THE SUPERSTACK (the AI-research stack — what to name SUPERSTACK)
Rationale: these hold the agent architecture, prompts, doctrine, memory/consent design and local-LLM work; everything else depends on them.
1. **`Noizyfish/GABRIEL`** — brain: agents, MCP worker, HOTROD, constellation, CLAUDE.md rules. *(resolve §5 provenance issue first)*
2. **`RSPNOIZY/DREAMCHAMBER`** — agent family prompts (CLAUDE/LUCY/SHIRL/POPS/DREAM/ENGR_KEITH/HEAVEN/CB01), CrewAI swarm.
3. **`NOIZY-ai/noizy.ai`** — canonical master: heaven/, schemas/, consent gateway, n8n, `.claude/commands`, IDEATION.md. (Fork of cisco/openh264 — consider re-creating as a non-fork to detach 5,410 unrelated upstream commits.)
4. **`RSPNOIZY/NOIZYLAB`** (+ working fork `Noizyfish/THEGATHERING`) — research lab core, `_mc96-common`, voice pipeline, empire stack (Forgejo+n8n+Claude).
5. **`NOIZYLAB-io/NOIZYLAB`** — the original unified lab (largest history; M2-Ultra tuning, AGENTS registry).
6. **`Noizyfish/NOIZYLAB_CONSOLE_v3`** — the 2025-12-17 local-LLM/MLX/Temporal-OS experiments (best record of day-by-day vibe coding).
7. **`Noizyfish/noizy-local-agents`** + **`Noizyfish/MC96-Mission-Control`** — small but on-theme (local agents; mission control).

### 4b. Tooling (enable the stack, not the research itself)
`Noizyfish/THEGATHERING` scripts/empire CLI (gather, mirror-to-forgejo, n8n); `NOIZYLAB-io/docs.github`; `Noizyfish/CODEMASTER` (intended code archive — empty on GitHub, content actually lives in `GABRIEL/CODEMASTER/`); `Noizyfish/swift-library`; `RSPNOIZY/2NDACT` (bridge, README-only);
forks used as references: `refact`, `copilot-cli`, `agent-skills`, `aeon-magick-ai-computer-control`, `awesome-selfhosted`, `cloudflare-docs` ×2, `brew`.

### 4c. Products / brands
`RSPNOIZY/{NOIZYFISH, NOIZYKIDZ, NOIZYWORLD, FISHMUSICINC, THE-OLD-GUARD, THE-GATHERED, RSPNOIZY (profile)}`, `Noizyfish/GABRIEL/products/get-git-good` (Get.Git.Good landing + VS Code extension; not a standalone repo), `Noizyfish/{sonobus, homebridge-config-ui-x, brave-browser}` (interest forks, audio/home/browser).

### 4d. Dead / empty / placeholder
- **Empty (0 commits):** `Noizyfish/CODEMASTER`, `Noizyfish/CLAUDE-TODAY` (never pushed; manifest already notes this), `Noizyfish/NOIZYFISH_THE_AQAURIUM` (name typo "AQAURIUM"), `Noizyfish/desktop-tutorial`.
- **README-only stubs:** `Noizyfish/THE-GATHERING`, `Noizyfish/RSPOO1---Robert-Stephen-Plowman`, `Noizyfish/noizy-local-agents`, `NOIZYLAB-io/NOIZY.ai`, `RSPNOIZY/{NOIZYWORLD, THE-GATHERED, 2NDACT, FISHMUSICINC}`.
- **Superseded:** `Noizyfish/NOIZYLAB-GABRIEL` (earlier edition of GABRIEL).
- **Duplicates:** `THE-GATHERING` (U1) vs `THE-GATHERED` (U2) vs `THEGATHERING` (U1 fork); `NOIZYLAB` ×3 (O1 original, U1 fork, U2 lab) + a copy inside `noizy.ai/NOIZYLAB/`; `NOIZYLAB-io/NOIZY.ai` vs `NOIZY-ai/noizy.ai`; `_mc96-common` replicated into 5 repos.
- **Never created:** NOIZYVOX, NOIZYANTHROPIC, NOIZYSTDZ, NOIZYBEAST, LIFELUV, AEON, GET-GIT-GOOD (as repos).

## 5. Gaps / unverified

- **Gists, private repos of RSPNOIZY, other org memberships:** the token is a Noizyfish integration token. `gh gist list` → forbidden; `gh api user/orgs` → `[]`; `user/memberships/orgs` → `[]`.
  Orgs `NOIZYLAB-io` and `NOIZY-ai` were found via public events and commit authorship (Noizyfish pushed to both; Noizyfish profile shows name/company "NOIZYLAB", blog NOIZYLAB.ca), not via membership. `gh api orgs/NOIZYLAB-io/members` returned nothing.
  Only **public** repos of RSPNOIZY / the orgs are visible; private ones (if any) were not listed.
  Other possible orgs (e.g. `NOIZY-AI`, `NOIZYLAB` user, `NOIZYBEAST` user created 2019) exist as names but **ownership by Robert is unverified**; I did not inventory them. `RSPNOIZYLAB-3474` appears as a commit author in `NOIZYLAB-io` (probably a secondary account of his — unverified).
- **Code search limits:** GitHub code search skips forks and files > ~384 KB and only indexes default branches; `NOIZYLAB-io/NOIZYLAB` has 38 branches (e.g. `xenodochial-almeida`) that were not searched. A rate limit (10/min) hit the first search pass; the 0-hit results in §1 are from the clean rerun. The `commits … author:NOIZYLAB` search returns unrelated global results (the name is generic) and was discarded.
- **Content not grep'd** inside the big remote trees (`NOIZYLAB-io/NOIZYLAB` 412 MB, `NOIZY-ai/noizy.ai` 180 MB): only file *paths* were scanned for `super stack|vibe|research|ideation|journal|fellow`. Local clones grep'd fully: GABRIEL, MC96-Mission-Control, THEGATHERING, CLAUDE-TODAY (empty).
- **Pre-GitHub history (Jul 2024 →):** no evidence on GitHub. The only 2024 dates in clones are Cloudflare `compatibility_date` values in `wrangler.toml` files and a file named `workers/hotrod-dec31-2024.py` (suggests Dec 2024 work). The "30 crazy months" are therefore **on the M2 Ultra/drives/Google/Claude-chat history**, which this inventory could not reach. Claude conversation exports, Cursor/Windsurf/Antigravity workspaces, Obsidian/DEVONthink notes, and `CLAUDE-TODAY` nightly harvest (empty on GitHub; filled by `scripts/gather-claude.sh` from GOD) are the likeliest homes of a "SUPERSTACK" write-up.
- **Identity/provenance:** `Noizyfish/GABRIEL` README and `funding/anthropic-fellows-2026/*` name "Matthew Olson-Roos / NoizyLab.ai" (contact `me@matthewolsonroos.com`); `NOIZYLAB-GABRIEL` says GABRIEL is "named after Gabriel Almeida"; `NOIZYLAB-io/NOIZYLAB` README describes "xenodochial-almeida" branch. Repo commits are authored `RSP` / `NOIZYLAB` / `Noizyfish` / `Rob Plowman` / Copilot. I cannot determine whether the applicant name is an alias, a collaborator, or harvested third-party material — **check before publishing GABRIEL as SUPERSTACK**.
- **Counts of "own" vs fork** rely on the GitHub `fork` flag; `Noizyfish/NOIZYLAB` and `NOIZY-ai/noizy.ai` are flagged forks but contain original work.
- Manifest drift to fix in `empire/repos.json`: add orgs `NOIZYLAB-io`, `NOIZY-ai`; `RSPNOIZY` is a user; `Noizyfish/THEGATHERING` row says `pushedAt 2026-05-30` (it is 2026-11-21, and `createdAt` 2026-11-06 is the fork date); `aeon-magick…` row has `pushedAt` earlier than `createdAt` (fork semantics).

### Suggested follow-ups
1. Run `scripts/gather-claude.sh` on GOD and search `~/.claude/projects/**` and Claude.ai export for `superstack`.
2. `grep -ril "super.\?stack"` across `/Volumes/*`, `~/NOIZY`, Obsidian vault, DEVONthink.
3. Clone `NOIZYLAB-io/NOIZYLAB` (all 38 branches) and `NOIZY-ai/noizy.ai` and grep content (≈600 MB).
4. Re-run `gh gist list` with a personal-access token (`gist` + `read:org` scopes) as `Noizyfish` and `RSPNOIZY`.
