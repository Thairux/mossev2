---
id: FEAT-TKC-NATIVE
title: "Native TKC Integration for Persistent Context and Zero-Amnesia Memory"
type: feature
status: proposed
version: 1
schema_version: 1
dependencies: [ARCH-REBRAND-MOSSE]
scope:
  - agent/memory_provider.py
  - "agent/turn_*.py"
  - agent/prompt_builder.py
  - "plugins/memory/tkc/**/*"
  - tools/tkc_tools.py
verification:
  commands:
    - "python scripts/check"
---

# Native TKC Integration for Persistent Context and Zero-Amnesia Memory

## Problem Statement & Motivation
Currently, memory in Hermes Agent is fragmented across secondary plugins (`byterover`, `retaindb`) and a shell-out phase 1 wrapper in `plugins/memory/tkc/`. This creates inconsistent context persistence, latency overhead, and memory bloat. Mosse v2 mandates Native TKC Core Integration, establishing TKC (conforming to the SGM protocol) as the default shared brain across CLI, TUI, Desktop, and Gateway platforms.

## Invariants & Guardrails
- **Prompt Caching Invariant:** Dynamic board digests and handoffs must NEVER be injected into the static system prompt prefix. They must be injected into the first user turn context or a designated dynamic message block.
- **Content-Addressed Compression:** When context fills up, conversation segments are compressed into TKC slugs with short refs (`tkc:slug@v1`), ensuring zero hallucination or lossy LLM summarization.
- **Graceful Offline Fallback:** If TKC CLI or daemon is temporarily unavailable, Mosse operates in offline stateless mode with clear telemetry rather than crashing.
- **Credential Hygiene:** Credentials, `.env` files, and private tokens must never be written or indexed into TKC memory.

## Requirements
- Bind `tkc` as the default `MemoryProvider` implementation in `agent/memory_provider.py`.
- Auto-run `tkc_fingerprint` and `tkc_board digest` at turn initiation.
- Auto-record atomic status and invoke `tkc_handoff` at session termination or pause.
- Provide first-class tools (`tkc_recall`, `tkc_compress`, `tkc_comment`, `tkc_board`, `tkc_write`, `tkc_rules`, `tkc_decision`) directly in the agent's active toolset.
- Integrate TKC block compression into `agent/turn_compression.py`.

## Acceptance Criteria
- Unit tests verify session bootstrap retrieves fingerprint and board digest without mutating prompt prefix.
- Eviction tests confirm context compression generates valid TKC short refs and restores them cleanly.
- Integration tests confirm prompt caching prefixes remain bit-for-bit identical across turns.
- If TKC is disabled or unreachable, agent logs a warning and proceeds gracefully.
