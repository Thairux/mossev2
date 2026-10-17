---
id: FEAT-KANBAN-EXPLORER
title: "Unified Kanban Multi-Agent Delegation and Visual TKC Database Explorer"
type: feature
status: proposed
version: 1
schema_version: 1
dependencies: [ARCH-REBRAND-MOSSE, FEAT-TKC-NATIVE, FEAT-SDD-INTEGRATION]
scope:
  - tools/kanban_tools.py
  - hermes_cli/kanban.py
  - "apps/desktop/src/**/*"
  - "web/**/*"
verification:
  commands:
    - "python scripts/check"
---

# Unified Kanban Multi-Agent Delegation and Visual TKC Database Explorer

## Problem Statement & Motivation
In complex engineering workflows, human developers and autonomous agents need clear task visibility, asynchronous handoffs, and an intuitive way to explore the persistent knowledge graph accumulated in TKC. While Hermes has a kanban worker swarm and TKC has an atomic board, they currently operate in separate data models. Mosse v2 bridges them: agents leave and claim tasks in a shared Kanban board, and developers can inspect the full TKC context database (symbols, slugs, decisions, comments, revisions) through a high-fidelity visual explorer.

## Invariants & Guardrails
- **Bi-Directional Card Sync:** Kanban task card status transitions (Backlog -> In Progress -> Blocked -> In Review -> Done) must emit atomic TKC board updates so CLI/TUI and Desktop stay in sync.
- **Context Provenance:** Every delegated task card must attach relevant TKC short refs and SDD spec/task IDs.
- **Responsive Electron/Web UI:** Database explorer queries must be paginated or streamed via WebSockets to prevent UI stutter when browsing large symbol indexes.

## Requirements
- Extend Kanban card schema to include `tkc_refs` (array of string refs), `sdd_task_id`, and `assigned_agent`.
- Implement agent-to-agent delegation tools allowing worker agents to spawn subtasks onto the Kanban board and wait for completion signals.
- Build the **TKC Database Explorer** component in `apps/desktop` and `web/`:
  - Visual Knowledge Graph displaying relationships between files, decisions, rules, and symbols.
  - Live atomic activity timeline streaming board posts, handoffs, and questions.
  - Visual diff and revision inspector for checking file version history stored in TKC.
- Provide drag-and-drop task movement, tag filtering, and search across Kanban cards and TKC records.

## Acceptance Criteria
- Creating or moving a Kanban card automatically generates a corresponding atomic entry in the TKC board.
- The TKC visual explorer correctly queries and renders local TKC symbols, decisions, and comments without freezing the Electron main process.
- Subagent task delegations propagate card status and return results to the parent session upon completion.
