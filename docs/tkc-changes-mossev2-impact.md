# TKC Changes & Mossev2 Surface Impact Log

**Target Project:** `C:\Users\ptmth\Desktop\main project\tkc` (TKC v2 Core)  
**Consumer Surface:** `C:\Users\ptmth\Desktop\main project\mossev2` (Mosse v2 / Hermes Fork)  
**Governing Directive:** Directive #404, #406 & Strategy Decision #613 (Approach B: Remote Cloud Brain + Thin Local Bridge).

---

## 1. Architectural Touchpoints Map (Approach B)

```
┌────────────────────────────────────────────────────────┐
│                   mossev2 (Hermes Fork)                │
│                                                        │
│  [agent/memory_provider.py] ◄── Stage 3 Integration    │
│  [apps/desktop] (Settings: License Key & Cloud Sync)   │
└───────────────────────────┬────────────────────────────┘
                            │
              Local Loopback / Lightweight Bridge
                            ▼
┌────────────────────────────────────────────────────────┐
│                   TKC Thin Bridge                      │
│  • Local stdio MCP surface for host agents             │
│  • Local filesystem operations (read/diff/write)       │
│  • Outbound credential sanitization / blocklist        │
└───────────────────────────┬────────────────────────────┘
                            │
               HTTPS / SSE (Bearer Token Auth)
                            ▼
┌────────────────────────────────────────────────────────┐
│                 Remote TKC Cloud Engine                │
│                 (Proprietary Closed IP)                │
│  • Compression & content-addressing engines            │
│  • Hybrid retrieval & vector semantic search           │
│  • Global multi-agent board & atomic handoffs          │
│  • Supabase PG backend (aws-0-eu-west-1 pooler)        │
└────────────────────────────────────────────────────────┘
```

---

## 2. Key Surface Contracts & Invariants

1. **IP Protection Invariant:**
   - The core TKC algorithms (compression, symbol indexing, hybrid recall scoring, board mechanics) reside exclusively on the authenticated remote cloud engine.
   - The user machine only runs a thin local bridge (~50–100 lines) to interface with the local filesystem.

2. **Mosse v2 Packaging Impact:**
   - Mosse v2 desktop installers do not bundle proprietary heavy models or the full TKC engine, reducing installer footprint down to ~15MB.
   - Stage 3 (`agent/memory_provider.py`) connects to the Remote Cloud Engine via the thin bridge using the user's license key.

3. **Security Invariant:**
   - Secret blocklists and credential redaction run **locally on the bridge** before any data egress to the cloud engine, preventing credentials from entering remote memory.

---

## 3. Change Register

| Date | Component | Change Summary | Impact on Mossev2 Surface |
|---|---|---|---|
| **2026-10-11** | Strategy | Locked **Approach B** (Thin Local Bridge + Remote Cloud MCP over SSE). | Mosse v2 memory provider changes from heavy local Bun runtime to authenticated remote client. |
| **2026-10-11** | `tkc/src/mcp` | Remote SSE transport (`@modelcontextprotocol/sdk`) planned for cloud deployment. | Mosse v2 can consume TKC as a remote web service using standard Bearer license authentication. |
| **2026-10-11** | `drizzle.config.ts` | Dialect shifted to `postgresql` pointing to Supabase `tkc-cloud` (eu-west-1). | Database tier aligns with cloud hosting backend. |
| **2026-10-11** | `DUAL-MODE.md` | Defined Dual-Mode architecture: SQLite primary + Supabase PG backup. | Re-anchored: Cloud engine handles persistent PG state; local bridge handles fast filesystem access. |
| **2026-10-15** | `mossev2/plugins/memory/tkc/` | **Phase 1: TKC-native memory provider** — Hermes `MemoryProvider` ABC implementation that shells out to the local TKC CLI (bundled by default, overridable via `memory.tkc.tkc_path`). Graceful degradation: mosse boots without TKC, memory features disabled until TKC reachable. | Replaces mosse v1's plugin memory (byterover/retaindb) as the default memory provider. TKC is the shared brain across Hermes, OpenCode, and mosse. Config: `memory.provider: "tkc"`, `memory.tkc.tkc_path`, `memory.tkc.tkc_home`. |
| **2026-10-15** | TKC brain | Recorded context precedence rule: **mosse v2 supersedes mosse** in context (comment ID 1152 on `docs/tkc-changes-mossev2-impact`). mosse v1 planning docs are legacy/obsolete. | Future TKC lookups prefer mossev2 entries; mosse entries are historical only. |
