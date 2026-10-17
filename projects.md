# Project Specification: Mosse v2 — Autonomous Local-First Workstation Agent

## 1. Executive Summary & Vision

**Mosse v2** is a sovereign, local-first personal AI workstation agent built upon an industrial-grade agent runtime (forked from Nous Research's `hermes-agent`). It unites permanent deterministic memory (**TKC / SGM**), verifiable spec-driven development (**SDD**), autonomous multi-agent task swarms (**Kanban Worker Lanes**), and a sustainable commercial model featuring an ad-supported community tier and secure, encrypted cloud sync for paying license holders.

Mosse v2 eliminates the two biggest failures of modern AI tools:
1. **The Amnesia Tax:** Context loss between sessions and disconnected silos across tools.
2. **The Rental Trap:** Prohibitive $20/month SaaS subscriptions for shallow web wrappers.

---

## 2. Product Architecture & Pillars

```
┌────────────────────────────────────────────────────────────────────────┐
│                        MOSSE v2 CLIENT INTERFACES                      │
│   • Electron Desktop App (React / Vite / Tailwind / Lucide)            │
│   • Web Dashboard SPA (:8000 Web UI)                                   │
│   • Multi-Platform Gateway (Telegram, Discord, Slack, WhatsApp)        │
│   • High-Performance Ink Terminal TUI & CLI (`mosse`)                  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        MOSSE v2 AGENT RUNTIME                          │
│   • Turn Loop Execution & Tool Orchestration (`agent/turn_*.py`)      │
│   • Prompt Caching Invariants & Narrow Waist Core                      │
│   • Subagent Swarm Dispatch & Kanban Worker Lanes                      │
│   • Spec-Driven Development (SDD) Server Verification Gates            │
└─────────────┬────────────────────────────────────────────┬─────────────┘
              │                                            │
              ▼                                            ▼
┌───────────────────────────────┐            ┌───────────────────────────┐
│     NATIVE TKC CORE ENGINE    │            │  SDD VERIFICATION ENGINE  │
│  • Content-addressed short refs│            │  • Strict spec hierarchy  │
│  • MemoryProvider ABC         │            │  • Real server execution  │
│  • Lifecycle: Fingerprint,    │            │  • Diff-derived mappings  │
│    Board Digest, Auto-Handoff │            │  • Two-option write gates │
│  • Token-free context compress│            └───────────────────────────┘
└─────────────┬─────────────────┘
              │
              ▼
┌────────────────────────────────────────────────────────────────────────┐
│                  MONETIZATION & INFRASTRUCTURE TIER                    │
│  • Free Tier: Local SQLite + Non-intrusive Dev Partner Sponsorships    │
│  • Pro/Paid Tier: Gated Zero-Knowledge Encrypted Cloud Backup & Sync   │
│    (Supabase PG Pooler, Multi-device continuity, Team Brain sharing)   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Core Feature Specifications

### Feature Spec 1: Complete Rebranding (Hermes -> Mosse)
- **Scope:** CLI executable, configuration roots (`~/.mosse`), environment naming, desktop assets, logos, copy, documentation, and error messages.
- **Invariants:** Backward-compatible migration from existing `~/.hermes` configs; zero disruption to core prompt caching invariants.
- **Components:** `pyproject.toml`, `cli.py`, `hermes_constants.py` -> `mosse_constants.py`, `apps/desktop/`, `ui-tui/`, `web/`.

### Feature Spec 2: Native TKC Memory & Turn Lifecycle Integration
- **Scope:** Elevate TKC from a plugin shellout to Mosse's native default memory and context engine.
- **Lifecycle Injections:**
  - *Session Startup:* Automatically inject user fingerprint (`tkc_fingerprint`), active project board digest (`tkc_board digest`), and latest handoff (`tkc_handoff latest`).
  - *Context Compression:* Replace lossy LLM summarization with deterministic TKC block compression; compress evicted conversation turns into short refs (`tkc:slug@v1`) that the agent can selectively expand.
  - *Model Toolset:* Expose first-class TKC model tools (`tkc_recall`, `tkc_compress`, `tkc_comment`, `tkc_board`, `tkc_write`, `tkc_rules`, `tkc_decision`).
  - *Session Teardown:* Automatically log atomic state and post session handoffs.

### Feature Spec 3: Spec-Driven Development (SDD) Engine Integration
- **Scope:** Native integration of SDD workflow for structured, verifiable software engineering.
- **Capabilities:**
  - `project.md` -> strict markdown specs under `specs/`.
  - Task state machine (planned -> in_progress -> verified | failed).
  - Server-executed verification evidence: Agent claims of passing tests are rejected unless backed by executed command logs.
  - Two-option write enforcement: Proactive blocking of file edits within pending change impact radiuses.

### Feature Spec 4: Kanban Board Mod with TKC Database Explorer
- **Scope:** Unified multi-agent visual management and context exploration.
- **Kanban Agent Collaboration:**
  - Agents post, assign, and claim task cards with attached TKC references and SDD task IDs.
  - Real-time lane transitions (Backlog -> In Progress -> Blocked -> In Review -> Verified/Done).
- **TKC Database Visual Viewer (Desktop & Web App):**
  - Interactive knowledge graph visualizing symbols, compressed slugs, decisions, comments, rules, and revisions.
  - Live atomic activity stream: Real-time board entries, blocker alerts, and question threads.
  - Side-by-side file revision diffs and provenance tracking.

### Feature Spec 5: 100% Free Community Model — BYO-Supabase Cloud Sync & Dev Utility Ads
- **100% Free of Charge & Sovereign:**
  - Full local-first workstation autonomy with zero paywalls, seat fees, or subscription taxes.
  - Supports local models (Ollama/vLLM) and BYO API keys.
- **BYO-Supabase Cloud Sync (Bring Your Own Database):**
  - Seamless multi-device continuity without creator hosting liability: users connect their own free Supabase PostgreSQL database URL (`SUPABASE_DB_URL`).
  - Automated initial schema migration provisions tables (`tkc_slugs`, `tkc_symbols`, `tkc_decisions`, `tkc_board`, `tkc_comments`) directly on the user's Supabase instance.
  - Client-side zero-knowledge AES-256-GCM encryption before sync: user data is encrypted on the workstation so the cloud vault holds only ciphertext.
- **Sustainable Monetization via Developer Utility Ads:**
  - Non-intrusive, curated developer partner cards (GPU compute credits on RunPod/Together AI, developer hosting perks, developer tool credits) rendered exclusively in peripheral UI surfaces (desktop status bar/footer, CLI startup banner).
  - Strict privacy & invariant: Zero tracking, zero telemetry, and zero injection into model reasoning or prompts.

### Feature Spec 6: Competitor-Inspired Quality of Life (QoL) Enhancements
- **Architect/Editor Dual-Model Flow (Aider pattern):** High-reasoning model creates plans and specs; cost-effective fast model executes code changes.
- **Checkpoint & Sub-Turn Rollbacks (Claude Code / Aider pattern):** Instant git snapshot before each destructive tool turn with 1-click `/undo` rollback.
- **Token & Cache Efficiency Live Meter (Claude Code pattern):** Real-time display of cached vs. uncached prompt tokens and monetary cost per turn.
- **Browser Automation with Visual Verification (Odysseus / Playwright pattern):** Built-in headless browser with visual diffing (`compare_visual`) for UI testing.

---

## 4. Milestone Roadmap

| Milestone | Deliverables | Verification Gate |
|---|---|---|
| **M1: Rebranding & Baseline SDD** | Rename surface to Mosse v2, initialize SDD, establish `specs/` directory and validation rules. | `python scripts/check` clean, SDD `validate_specs` clean. |
| **M2: Native TKC Unification** | Wire TKC into core turn lifecycle (fingerprint, board digest, handoff, context compression). | Turn test verifying automatic context injection and short-ref expansion. |
| **M3: Kanban & TKC Visual Explorer** | Extend desktop app and web SPA with interactive Kanban lanes and TKC database graph viewer. | Electron E2E test verifying card transitions and symbol tree rendering. |
| **M4: Monetization & Gated Cloud Sync** | Implement sponsor card UI in free mode; build gated encrypted sync client for license holders. | License key activation gate test and encrypted sync round-trip test. |
| **M5: QoL Polish & Distribution** | Architect/Editor mode, git checkpoint rollback, token cache dashboard, signed Windows installer. | Clean packaging build via `electron-builder` and full test suite pass. |

---

## 5. Risk Assessment & Mitigations

1. **Prompt Caching Disruption:**  
   *Risk:* Injecting dynamic TKC board digests into system prompts could invalidate model cache prefixes.  
   *Mitigation:* Keep the system prompt strictly static; inject dynamic TKC context into the first user turn or via a dedicated ephemeral context block as per Hermes prompt caching invariants.
2. **Local Privacy in Cloud Sync:**  
   *Risk:* Accidental leak of confidential codebase snippets to remote cloud backup.  
   *Mitigation:* Local bridge enforces strict regex secret blocklists and client-side AES-GCM encryption before payload leaves the machine.
3. **Ad Fatigue:**  
   *Risk:* Developer backlash against advertising in developer tools.  
   *Mitigation:* Strictly non-intrusive, developer-relevant utility sponsorships (e.g., "$50 free GPU compute credits on RunPod"). Never banner ads, popups, or injected model completions.
