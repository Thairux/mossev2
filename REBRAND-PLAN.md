# Mosse v2 — Stage 2 Rebrand Plan (Identity)

**Source:** `Desktop/main project/mossev2` (Hermes Agent `ce966fef71`, MIT)
**Goal:** Rebrand to Mosse without breaking function or violating MIT attribution.
**Governing rule (directive #404):** audit before edits, smallest diffs, keep custom
code in well-defined modules, tests before claims.

---

## The core problem: two kinds of "Hermes"

A blind find-replace of "Hermes" → "Mosse" across 655 files would **break the app**.
The string splits into two categories that must be handled differently:

| Category | What it is | Count | Action |
|---|---|---|---|
| **Functional** | `.hermes` paths, `HERMES_HOME` env var, config dirs, auth paths | 332 files reference `.hermes` | **Do NOT rename blindly** — see the seam below |
| **Cosmetic** | UI brand text, i18n strings, product name, marketing | ~141 i18n files + UI | **Safe to rebrand** |

### Why functional is safer than it looks

The `.hermes` path is **already indirected** through `HERMES_HOME` / `get_hermes_home()`.
The code resolves the home dir from the env var, not a hardcoded literal, in most places.
That is the seam: **Mosse can keep `.hermes` as its data dir name** (zero migration risk)
and only change what users *see*. Renaming the on-disk dir is a separate, optional,
risky step — defer it.

**Decision: keep `~/.hermes` (or `HERMES_HOME`) as the data directory.** Rebrand the
product identity only. This is the smallest-diff, lowest-risk path and honors the
"smallest diffs" rule. If you later want the folder renamed, that's a one-line change in
`get_hermes_home()` plus a migration script — a deliberate, testable step, not part of
the initial rebrand.

---

## Rebrand surface (cosmetic only)

### 1. Product identity
- `apps/desktop/package.json`: `"name": "hermes"` → `"mosse"`, `"productName": "Hermes"` → `"Mosse"`
- Root `package.json`: `"name": "hermes-agent"` → `"mosse"` (or keep internal, your call)
- `apps/desktop/electron-builder.config.cjs`: installer/appId/productName
- App icons + branding assets in `apps/desktop/assets/`

### 2. UI strings (the bulk)
- `apps/desktop/src/i18n/*.ts` — 141 locale files, the word "Hermes" in user-facing text
- `apps/desktop/electron/main.ts` — 280 occurrences, mostly UI/window titles (the
  `HermesPath`/`HermesHome` identifiers are functional variable names — rename the
  *displayed* string, keep or rename the identifier consistently)

### 3. Attribution to PRESERVE (MIT requirement)
MIT requires the copyright notice and permission notice survive in copies. Keep:
- Root `LICENSE` (MIT, © Nous Research) — do not delete
- `contributors/` directory
- Any `NOTICE`/attribution blocks in source headers
- Add a `NOTICE` or README section: *"Mosse is a fork of Hermes Agent by Nous Research (MIT)."*

This is non-negotiable for legal compliance and it's also honest.

---

## Execution approach

**Scripted, reviewed, not blind.** For each category:

1. **Identity files** — hand-edit `package.json`, `electron-builder.config.cjs`, icons. Small, high-visibility, easy to verify.
2. **i18n + UI display strings** — scripted replace of the *displayed* word "Hermes" → "Mosse" in `apps/desktop/src/i18n/` and UI text, then `git diff` review before commit.
3. **Variable/identifier names** (`HermesPath`, `HermesHome`, …) — optional cosmetic rename; lowest priority, highest churn. **Recommend deferring** — they're internal, invisible to users, and renaming them touches the most code for the least visible gain.
4. **Functional `.hermes` paths / `HERMES_HOME`** — **leave as-is** (the seam). Document the decision.

**Verification (tests before claims):**
- `tsc --noEmit` on the desktop app
- `bun test` / the app's test suite
- Launch the desktop app, confirm it boots, shows "Mosse", and reads existing config
- `git diff --stat` to confirm the change set matches the plan (no stray functional edits)

---

## Sequencing

This is **Stage 2 of 8**. After rebrand:
- Stage 3: TKC memory integration (the `agent/memory_provider.py` seam)
- Stage 4-7: creative caps, media editing, video/audio gen, comic editing
- Stage 8: commercial readiness (re-run the licensing audit; the video-editor RED flag must be resolved here)

**Not started until you approve this plan.** Nothing in `mossev2` has been edited — it's a
clean clone. Say go and I'll start with the identity files (step 1), verify, then move to
the i18n pass.
