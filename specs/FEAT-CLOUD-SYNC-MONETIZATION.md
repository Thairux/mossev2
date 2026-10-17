---
id: FEAT-CLOUD-SYNC-MONETIZATION
title: "Bring-Your-Own-Supabase Cloud Sync and Ad-Supported Developer Sponsorships"
type: feature
status: approved
version: 2
schema_version: 1
dependencies: [ARCH-REBRAND-MOSSE, FEAT-TKC-NATIVE]
scope:
  - "apps/desktop/src/**/*"
  - "plugins/memory/tkc/**/*"
  - hermes_cli/config.py
  - "web/**/*"
verification:
  commands:
    - "python scripts/check"
---

# Bring-Your-Own-Supabase Cloud Sync and Ad-Supported Developer Sponsorships

## Problem Statement & Motivation
Sustaining an autonomous local AI workstation agent requires a viable commercial engine without compromising the local-first, anti-subscription ethos. Rather than locking cloud sync behind a proprietary paid paywall or recurring SaaS subscription, Mosse v2 is **100% free of charge for all users**.

Cloud backup and multi-device continuity operate via a **Bring-Your-Own-Supabase (BYO-Supabase)** architecture: users connect their own free Supabase PostgreSQL instance (`SUPABASE_DB_URL`). Continuous development is funded by non-intrusive, curated developer partner sponsorships and utility ads in peripheral UI surfaces.

## Invariants & Guardrails
- **Prompt Isolation Invariant:** Developer sponsor messages must NEVER be injected into LLM context, system prompts, reasoning loops, or token streams. They reside exclusively in peripheral UI surfaces (desktop status bar, new session header, CLI startup banner).
- **Zero-Knowledge Encryption:** Before any TKC memory block or board record egresses to the user's Supabase database, it undergoes local client-side AES-256-GCM encryption using a passphrase-derived key known only to the user.
- **Local Sovereignty:** Cloud backup is strictly an optional sync enhancement. The local SQLite TKC database remains fully functional offline indefinitely without an internet connection or Supabase configuration.
- **Zero Creator Hosting Liability:** The creator incurs zero database hosting or bandwidth charges, preventing server bankruptcy as adoption scales.

## Requirements
- **BYO-Supabase Configuration:**
  - Input field in Desktop Settings and CLI command (`mosse config set supabase_db_url <url>`).
  - Automated initial schema migration deploying tables (`tkc_slugs`, `tkc_symbols`, `tkc_decisions`, `tkc_board`, `tkc_comments`) to the user's database.
- **Client-Side Encrypted Sync Daemon:**
  - Background replication engine syncing local changes to the user's Supabase instance over HTTPS/SSE with vector clock conflict resolution.
- **Developer Utility Sponsorships & Ads:**
  - Tasteful, non-intrusive developer partner cards (curated GPU compute discounts, AI hosting perks, developer tool credits) rendered in desktop status bar/footer and CLI startup banner.
  - Strict privacy: Zero personal tracking or codebase telemetry.

## Acceptance Criteria
- Free mode allows all users to input their own Supabase connection string without fees or license gates.
- When configured, automated migration runs and sets up tables in the user's Supabase PostgreSQL database.
- Encrypted sync round-trip test verifies that uploaded data is ciphertext-only and decrypts cleanly on a secondary workstation instance.
- Developer sponsor banners render exclusively in peripheral UI components with zero LLM prompt contamination.
- Complete offline capability is preserved when no Supabase URL is configured.
