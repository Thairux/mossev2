---
id: ARCH-REBRAND-MOSSE
title: "Rebranding Hermes Agent Core and Interfaces to Mosse v2 (Facade & Proxy Pattern)"
type: architecture
status: approved
version: 2
schema_version: 1
dependencies: []
scope:
  - pyproject.toml
  - hermes_constants.py
  - cli.py
  - "apps/desktop/**/*"
  - "ui-tui/**/*"
  - "web/**/*"
verification:
  commands:
    - "python scripts/check"
---

# Rebranding Hermes Agent Core and Interfaces to Mosse v2 (Facade & Proxy Pattern)

## Problem Statement & Motivation
Mosse v2 is an evolution from Hermes Agent into a sovereign, local-first workstation agent. A full, deep backend rename (renaming thousands of internal symbols, Python modules, database tables, and test fixtures) would create catastrophic merge conflicts with upstream Nous Research `hermes-agent` releases and risk breaking code health ratchets.

To achieve total brand ownership without sacrificing maintainability, Mosse v2 adopts the **User-Facing Facade & Proxy Rebranding Pattern**:
- 100% of user-facing touchpoints (Desktop UI, Web UI, CLI executable, TUI banner, persona self-identification, installer) present as **Mosse v2**.
- The internal engine, module structure, and low-level protocol names operate cleanly as the robust execution backbone by proxy.

## Architecture & Proxy Boundaries

```
┌────────────────────────────────────────────────────────┐
│                   USER TOUCHPOINTS (100% MOSSE)        │
│  • CLI Executable: `mosse` (`mosse = "cli:main"`)      │
│  • Desktop App: Window Title, Tray, Splash, Installer   │
│  • Web Dashboard: Header, Favicon, Title, About Modal   │
│  • TUI: ASCII Banner, Prompt (`mosse>`), Help Screens   │
│  • Agent Persona: "I am Mosse, your AI assistant"      │
│  • Config Alias: `MOSSE_HOME` / `~/.mosse`             │
└───────────────────────────┬────────────────────────────┘
                            │
              Transparent Facade / Path Resolution
                            ▼
┌────────────────────────────────────────────────────────┐
│               EXECUTION ENGINE BACKBONE (BY PROXY)     │
│  • `hermes_constants.py` handles proxy path routing    │
│  • Preserves internal Python imports & class names     │
│  • Preserves full upstream git rebase/mergeability     │
│  • Zero code health ratchet regressions                │
└────────────────────────────────────────────────────────┘
```

## Invariants & Guardrails
- **Zero Merge Friction:** Internal Python filenames, class definitions (`HermesCLI`, `SessionDB`), and test fixtures remain unchanged unless touching user-facing text strings.
- **Backwards Compatibility:** If `~/.mosse` is absent, automatically check and resolve `~/.hermes` without error. If `MOSSE_HOME` is set, it overrides `HERMES_HOME`.
- **Prompt Caching Invariant:** Rebranding copy changes in system prompts or agent persona must remain strictly static; dynamic strings must never be introduced into prompt prefixes.
- **Dual Command Resolution:** Both `mosse` and `hermes` CLI entrypoints function, with `mosse` documented as primary.

## Scope of Work
1. **Packaging Manifest (`pyproject.toml`):**
   - Add `mosse = "cli:main"` to `[project.scripts]`.
   - Update user-facing project metadata (name, description) to Mosse v2.
2. **Environment & Path Proxy (`hermes_constants.py`):**
   - Add `get_mosse_home()` with precedence: `MOSSE_HOME` -> `HERMES_HOME` -> `~/.mosse` (if exists) -> `~/.hermes`.
   - Update user-facing display paths to show Mosse paths while maintaining transparent filesystem resolution.
3. **CLI & TUI Presentation (`cli.py`, `ui-tui/`):**
   - Update startup banner to Mosse v2 ASCII logo and styling.
   - Set interactive prompt string to `mosse>`.
   - Update `/help`, `/version`, and slash command help descriptions.
4. **Desktop Application (`apps/desktop`):**
   - Rename app bundle in `package.json` to `mosse-desktop`.
   - Update Electron window title, tray tooltip, taskbar app ID, and icon assets to Mosse.
   - Configure Windows installer targets in `electron-builder.yml` to produce `Mosse-Setup-<version>.exe`.
5. **Web Dashboard (`web/`):**
   - Update SPA title, navigation header, brand badges, and theme accents to Mosse.
6. **Agent Persona Default (`agent/prompt_builder.py`):**
   - Default persona self-identifies as Mosse: *"You are Mosse, a sovereign local-first AI workstation agent."*

## Acceptance Criteria
- `python scripts/check` passes with zero lint, formatting, or ratchet regressions.
- Running `mosse --version` outputs `Mosse v2.x.x` (or current development semver).
- Launching the Electron desktop app renders "Mosse" in window title, system tray, and About modal.
- Launching the web dashboard renders "Mosse" in browser tab title and navigation bar.
- Existing `~/.hermes/config.yaml` is discovered transparently if `~/.mosse` is absent.
- Git diff against upstream `main` remains minimal and strictly confined to facade files and UI templates.
