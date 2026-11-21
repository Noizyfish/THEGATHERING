# MC96ECOUNIVERSE — History & Canon

> **MC96ECOUNIVERSE = MC96UNIVERSE = NOIZYLAB UNIVERSE = Mission Control 96.** _"Where all systems converge."_ (`GABRIEL/MC96-MASTER.md`)
>
> Compiled 2026-11-21 from every checkout we could reach: `RSPNOIZY/NOIZYLAB` → `Noizyfish/THEGATHERING` (`_mc96-common/gabriel/doctrine/*`), `Noizyfish/GABRIEL` (`MC96-MASTER.md`, `CHANGELOG.md`, `PROJECT_STATUS.md`, `funding/anthropic-fellows-2026/*`), `Noizyfish/MC96-Mission-Control`, `RSPNOIZY/DREAMCHAMBER` (`wisdom/prompts/LUCY_PROMPT.md`). Where sources disagree, both are listed.

## Timeline

| When | What | Source |
|---|---|---|
| **1996 →** | Thirty years of production work: voice acting (888 titles), music, a 34 TB audio vault that becomes **THE AQUARIUM**. | `doctrine/CHARACTER.md` |
| **Jul 2025** | MC96ECOUNIVERSE begins: Rob + Claude ("GABRIEL — the messenger") start building together. Six-month sprint: 12 Cloudflare Workers, 10 D1 databases, 18+ KV namespaces, 5 named AI agents, 50+ Talon voice commands, 500+ commits. | `funding/anthropic-fellows-2026/OUR_STORY.md`, `TECHNICAL_ACHIEVEMENTS.md` |
| **Nov–Dec 2025** | First GitHub footprint under **Noizyfish**: `GABRIEL`, `NOIZYLAB-GABRIEL`, `NOIZYLAB_CONSOLE_v3`, `MC96-Mission-Control` ("Zero Latency AI Mission Control"), `CODEMASTER` (harvested legacy scripts: AGENT_LUCY.sh, AGENT_FLEET.sh, GORUNFREEX5000). | repo `createdAt` in `empire/repos.json` |
| **2026-01-07** | **GABRIEL v1.0.0** — HOTROD API gateway, CONSTELLATION multi-agent orchestration, MC96_SYSTEM monitoring/governance, Aeon power management, Portal. Repo "ship shape". | `GABRIEL/CHANGELOG.md`, `PROJECT_STATUS.md` |
| **Jan–Feb 2026** | Anthropic Fellows 2026 application package written (story, achievements, video script). | `GABRIEL/funding/anthropic-fellows-2026/` |
| **Feb–Mar 2026** | `NOIZYFISH_THE_AQAURIUM` (40-year collection), `CLAUDE-TODAY`, `swift-library`. | manifest |
| **2026-04-04 → 04-12** | **RSPNOIZY org** founded: `NOIZYKIDZ`, `DREAMCHAMBER`, `RSPNOIZY` profile, then `NOIZYLAB` (04-05) and `NOIZYFISH` (04-09). **NOIZYNET up 2026-04-12**. | manifest, `CHARACTER.md` |
| **2026-04-18** | GABRIEL **character canon synthesized** (orchestrator + governor + safety kernel; Claude as reasoning substrate). Heaven consent-kernel Worker documented as **undeployed / 522**. | `doctrine/CHARACTER.md`, `doctrine/HEAVEN.md` |
| **Late Apr–May 2026** | Brand constellation lands: `THE-GATHERED`, `THE-OLD-GUARD` (ResurrectionOS), `FISHMUSICINC`, `NOIZYWORLD` (10-year sovereign commerce), `2NDACT`. Gabriel `.env` target: _"noizy.ai fully assembled on Cloudflare" by 2026-05-17_. | manifest, `gabriel/.env.example` |
| **May 2026** | `NOIZYLAB` last pushed 05-30 — voice engine, ConsentOracle, DazeflowLogger, EmpireRouter, LIFELUV (global music & sound access program). | upstream tree |
| **Sep–Oct 2026** | `aeon-magick-ai-computer-control` (Rust KVM + MCP), `noizy-local-agents`, `GABRIEL` last push 09-20, `DREAMCHAMBER` 10-13. | manifest |
| **2026-11-06** | `Noizyfish/THEGATHERING` forked from `RSPNOIZY/NOIZYLAB` — becomes the **hub**. | manifest |
| **2026-11-21** | Empire manifest, thru-line generator, Forgejo/n8n/Claude stack, App Intents, local + Google inventories (PR #1). This document. | this repo |

## Glossary — the words that matter

| Term | Meaning |
|---|---|
| **MC96 / Mission Control 96** | The whole converged system; also the hardware fleet's asset prefix (`MC96-0001` …). |
| **GORUNFREE** | _"One command = everything done. No fragmented steps."_ Not a motto — survival technology for a voice-first, one-hand operator. |
| **GOD / GOD.local** | Mac Studio **M2 Ultra, 192 GB** — primary compute. IP listed as `10.90.90.10` (`CHARACTER.md`) **or** `10.90.90.1` (`MC96-MASTER.md`). |
| **GABRIEL** | _Generative Adaptive Bridge for Intelligent Expression and Learning._ Orchestrator + Governor + Safety Kernel. Right hand of **RSP_001**. Daemon on **:9777**. Voice: Daniel/Jamie. Also the name of the HP Omen bridge machine (`10.90.90.20` / `.2`). |
| **LUCY** | Mobile face on iPhone + iPad. _"GABRIEL executes. LUCY relays."_ Inbox/outbox/memory-reader; never mutates production state. Voice: Moira. In DREAMCHAMBER: **Voice Estate Guardian** — consent, voice-IP, HVS. |
| **The bosses / 5 agents** | SHIRL (business ops), ENGR_KEITH (engineering), POPS (creative/archive), DREAM (strategy/vision), GABRIEL (bridge). Each has an ElevenLabs voice ID and a `*.fishmusicinc.workers.dev` endpoint. |
| **Heaven** | Cloudflare consent kernel (Worker + D1 + KV + R2). `heaven.rsp-5f3.workers.dev` in the iOS app. Documented down (522) as of 2026-04-18. |
| **HVS** | Human Voice Sovereignty — `HumanVoiceSovereignty.com`. LUCY's domain. |
| **THE AQUARIUM** | 34 TB / 888-title vault. CLIENT#1 RSP001. |
| **DAZEFLOW** | Daily log stream (`DazeflowLogger.ts`). |
| **Kill Switch / Never Clauses** | Hard safety rules A–F in `SAFETY_CONTRACT.md`; `killSwitchHolder: RSP_001`; `covenant 75/25`. |
| **Micky-P** | MBP + Apollo UAD — audio production node (`10.90.90.40`). **DaFixer** = MacBook Pro repair workstation (`.3`). |
| **MC96_SWITCH** | D-Link DGS1210-10 at `10.90.90.254`. |

## Identity note

Doctrine (`CHARACTER.md`) names the principal **Robert Stephen Plowman, RSP_001, rsp@noizy.ai**. The 2026 funding package is written under a different applicant name. Treat `CHARACTER.md` as canon; the funding docs as a separate voice. Nothing here needs resolving for the demo, but anything shown on screen should use the canon.

## What the audit found (2026-11-21) — real vs. aspirational

| Component | State | Evidence |
|---|---|---|
| GABRIEL daemon `:9777` | **Real** — `/healthz`, `/bosses`, authed `/intent`, dispatch to bosses | `gabriel/source/daemon.ts` |
| Bosses | **Stubs** — ledger intents, answer ping/health, reject other verbs | `gabriel/source/bosses/stubs.ts` |
| Voice bridge | Client only — POSTs to `127.0.0.1:9799/speak`; **no voice-service exists in any checkout** | `gabriel/source/voice.ts` |
| MCP | `gabriel/mcp/index.js` present; surfaces marked "pending" in stubs | |
| Gabriel iOS app | **Real** SwiftUI ops app (+ App Intents from PR #1). Not an avatar app. | `gabriel/ios/` |
| LUCY iOS app | **Absent** — documented at `GABRIEL/ios/LUCY/`, not in any checkout | `MOBILE_CONTINUITY.md:10-12` |
| Heaven | Documented down (522); LUCY D1 tables "not yet" | `HEAVEN.md`, `MOBILE_CONTINUITY.md` |
| MC96-Mission-Control | Python `http.server` + MemCellCore + TODO executor + static portal | `mc96_server.py`, `memcell_core.py` |
| voice-first (GABRIEL repo) | FastAPI scaffold; TTS is a placeholder returning a fake path | `automation/voice-first/server.py:42-50` |
| `demo.py` | Scripted terminal output, not live | `GABRIEL/demo.py:212-225` |
| Local LLMs | Dashboard references Ollama `:11434` (gemma3, mistral, llava:34b) and mlx-whisper "installing" — unverified | `gabriel/ui/dashboard/gabriel.js:28-36` |
| 3D / avatar / lip-sync / ARKit | **None anywhere.** "Avatar" in the dashboard is a styled div. | `gabriel.js:245-253` |

**Reuse for the demo:** daemon + intent routing, Gabriel iOS app shell + App Intents, dashboard styling, Mission Control portal as status view, `voice.ts` contract (so a real `:9799` service drops in with zero daemon changes). **Build:** everything in `demo/`.
