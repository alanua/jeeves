# History source: ChatGPT memory snapshot — 2026-05-01

Status: RECOVERY_SOURCE
Source type: ChatGPT/project working memory dump provided by the user in `JEEVES_BRANCH_RECOVERY_MODE`.
Date captured: 2026-05-01
Scope: Jeeves / OpenClaw-style project only.

## Purpose

This file records that a full ChatGPT working-memory snapshot was used as a historical recovery source for Jeeves.

The source is not treated as automatically canonical. It is an evidence source used to extract durable project knowledge into smaller Knowledge-base notes.

## Recovery rule confirmed by this source

When the user invokes `JEEVES_BRANCH_RECOVERY_MODE`, old/current chat branches, files, exports, screenshots, documents and memory snapshots are treated as recovery sources.

The recovery process must:

1. Extract only durable items:
   - identity
   - architecture
   - memory model
   - security/policy
   - controlled self-improvement
   - agent pipeline / department
   - behavior / UX rules
   - concrete decisions
   - rejected or outdated ideas
   - backlog ideas
2. Classify each item as:
   - `CONFIRMED_CANON`
   - `LIKELY_NEEDS_REVIEW`
   - `IDEA_BACKLOG`
   - `OUTDATED_REJECTED`
3. Never blindly canonize old chat content.
4. Treat ChatGPT/project memory as working memory.
5. Treat GitHub Knowledge-base as the durable project canon after user review or explicit user approval.
6. Prefer small docs-only updates.
7. Report briefly in the format:
   - `Що сталося / Що важливо / Ризик / Що робити тобі`
   - or `Нічого важливого. Дій від тебе не треба.`

## Extracted KB artifacts from this recovery pass

The durable Jeeves items from this memory snapshot were split into these Knowledge-base artifacts:

- `knowledge-base/jeeves/canon/2026-05-01-recovered-canon-snapshot.md`
- `knowledge-base/jeeves/behavior/oleksii-personal-preset-v1.md`
- `knowledge-base/recovery_audit/2026-05-01-memory-overflow-audit.md`

## Explicit non-goals

This recovery pass does not import every memory item into Jeeves canon.

Project-specific memories for BauClock, Gewerbe accounting, Lavalamp/WLED, Android TV, homelab, and other side projects are not copied into the Jeeves canon unless they define reusable Jeeves behavior, orchestration patterns, security rules, or user-preset requirements.

## Current interpretation

The memory snapshot confirms two separate architecture layers:

1. Current runnable bootstrap: `multi-agent-v1-bootstrap-v11` / Stage 1 vertical slice.
2. Strategic target architecture: LangGraph core, MCP tool plane, OpenHands coding sidecar, Langfuse observability, browser worker, own policy/approval layer.

The strategic target map is not the current runnable implementation.
