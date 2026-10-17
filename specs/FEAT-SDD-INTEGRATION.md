---
id: FEAT-SDD-INTEGRATION
title: "Native Spec-Driven Development Workflow and Verification Engine"
type: feature
status: proposed
version: 1
schema_version: 1
dependencies: [ARCH-REBRAND-MOSSE]
scope:
  - ".sdd/**/*"
  - "specs/**/*"
  - "agent/turn_*.py"
  - tools/sdd_tools.py
verification:
  commands:
    - "python scripts/check"
---

# Native Spec-Driven Development Workflow and Verification Engine

## Problem Statement & Motivation
Autonomous AI coding agents frequently hallucinate successful task completions, fabricate test outputs, and introduce regressions across interrelated codebase files without warning. Mosse v2 incorporates SDD (Spec-Driven Development) directly into its core execution loop to ensure every non-trivial change stems from a strictly validated specification and is verified by server-executed evidence rather than unverified agent claims.

## Invariants & Guardrails
- **Execution Truth:** Task verification commands (`run_verification`) must be executed directly by the server in an isolated subshell with scrubbed environment and captured exit codes; model output claims are untrusted.
- **Two-Option Write Fork:** Direct file writes within the blast radius of a pending spec change must be blocked until the user or agent selects RECONCILE (updating the spec) or explicitly waives with an audit trail.
- **Spec Authoring Authority:** The agent writes markdown body content; the SDD server enforces schema, front matter shapes, dependency graphs, and versioning.

## Requirements
- Provide native Mosse tools or MCP bridge for SDD surface (`init_project`, `get_status`, `list_specs`, `write_spec`, `create_task`, `complete_task`, `run_verification`).
- Integrate SDD task checkpoints before and after git modifications.
- Derive file-to-spec impact mappings dynamically from Git diffs upon task completion.
- Support visual verification (`compare_visual`) for frontend components via deterministic browser snapshots.

## Acceptance Criteria
- `complete_task("verified")` throws an error if no passing server execution record exists.
- Modifying a file declared in an active spec's scope triggers impact detection.
- All specs under `specs/` pass SDD `validate_specs` with zero structural errors.
