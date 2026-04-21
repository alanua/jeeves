# PROJECT KNOWLEDGE BASE

_Last updated: 2026-04-21_

This file is a project-level knowledge base snapshot for **Jeeves**, intended to preserve architecture, current implementation state, strategic decisions, ecosystem signals, and future subsystem direction in one durable GitHub-native place.

## 1. Project identity

**Project name:** Jeeves

**Working concept:** personal local-first multi-agent system with an OpenClaw-style core, but without blind copying of OpenClaw.

**Primary product thesis:** the durable value is not only the model itself, but the runtime shell around the model:
- context
- memory
- tools
- permissions
- integrations
- deterministic orchestration
- handoff continuity

**Target role of the system:** a top-level assistant (“Jeeves”) that can coordinate specialized subagents, retain continuity, accumulate skills, and later operate across real workflows under policy and approval gates.

## 2. High-level architecture direction

The project is being built around these layers:
- **API / ingress layer**
- **routing layer**
- **orchestration layer**
- **specialized agents**
- **policy / permissions layer**
- **memory / handoff continuity layer**
- **future knowledge-base layer**
- **future action-contract / approval-gated execution layer**
- **repo-local skills layer**

Architectural preferences:
- local-first where practical
- cloud fallback where necessary
- contracts-first foundation
- deterministic orchestration in runtime code, not prompt magic
- explicit boundary serializers between canonical runtime objects and external API/trace shapes
- no hidden dual contract families
- policy and approval separated from prompt behavior

## 3. Current implementation snapshot

### Stage 1 — foundation
Stage 1 is considered **closed**.

Closed work includes:
- canonical contracts and enums as the source of truth
- canonical runtime execution flow
- populated runtime evidence and validation
- hardened runtime-to-boundary serialization
- `/ask` HTTP behavioral contract locked by tests

Stage 1 design properties:
- single-agent runtime baseline
- explicit boundary flattening for API/trace
- no hidden route-only bridge
- no ambiguous contract duplication in the main runtime path

### Stage 2 — coordination
Stage 2 is active and already partially implemented.

Current accepted state:
- live hybrid coordination exists
- plain hybrid uses a deterministic **research -> planner** coordinated path
- planner remains the final user-facing answer producer
- boundary-visible `selected_agent` remains planner
- coordinated evidence, validation, provenance, and trace semantics have been hardened
- coordinated tool attribution and flattened trace ordering have been hardened

### Stage 2.5 — dry-run executor
Execution-aware hybrid is already live in a constrained form.

Current accepted state:
- execution-aware hybrid uses **research -> planner -> executor**
- executor is **optional**, **dry-run only**, and **advisory**, not action-producing
- planner remains the final-output producer and visible selected agent
- executor failure degrades in place without erasing a valid planner answer
- execution-aware hybrid provenance and trace semantics are hardened and stable
- repository tagged as `stage2-dry-run-executor-stable`

## 4. Agent roles

Current agent set:
- **planner** — planning and final answer shaping for coordinated hybrid flows
- **research** — research/input gathering for hybrid flows
- **executor** — currently a generic LLM worker with dry-run advisory semantics only; not a real action runtime

Important constraint:
- `executor` currently does **not** represent real side-effect execution
- any future real action execution must be owned by a separate action-contract / approval-gated layer, not by prompt implication

## 5. Core architectural decisions already accepted

1. **Contracts-first source of truth**
   - canonical models and enums must drive runtime behavior
   - no parallel result families

2. **Deterministic orchestration**
   - orchestration logic lives in runtime code
   - agents do not own fallback policy or approval policy

3. **Explicit boundary centralization**
   - external API and trace shapes may remain flattened for compatibility
   - flattening must be centralized and regression-tested

4. **Single top-level aggregate result**
   - boundary serialization flattens the top-level aggregate truth only
   - child run details stay in runtime structures unless explicitly flattened by compatibility rules

5. **Hybrid fallback discipline**
   - required-step failure can trigger explicit fallback
   - optional-step failure degrades in place when safe

6. **No silent side effects**
   - future action execution must be approval-gated
   - dry-run semantics must stay distinct from real action execution

## 6. Memory subsystem direction

A future **memory subsystem v1** is considered valuable and separate from the main runtime.

MemPalace is treated as a useful reference, specifically for:
- verbatim memory ingestion
- wake-up / startup context
- session diary / handoff continuity

Explicit non-goals for direct adoption:
- do **not** treat MemPalace as the full architecture base
- do **not** directly adopt its AAAK/compression layer
- do **not** directly adopt shell-hook implementations

## 7. Knowledge-base subsystem direction

A future **knowledge-base subsystem v1** is considered a distinct layer, separate from memory.

Preferred model:
- raw evidence / docs / repos / images
- LLM-compiled markdown wiki
- agent Q&A and linting over the wiki
- derived outputs such as reports, slide decks, and visuals
- optional viewing in Obsidian / Marp

Important separation:
- this knowledge base is **not** a replacement for canonical project docs
- this knowledge base is **not** a replacement for the memory / handoff subsystem

## 8. Future action-contract layer

The project has already accepted a future direction for action handling, but it is **not live** yet.

Current accepted direction:
- separate advisory executor output from real action intent
- use typed canonical action contracts
- approval must gate future side-effect execution
- keep orchestrator as owner of fallback, approval, and future action execution policy

Action-layer foundation already added:
- `ApprovalState`
- `ActionExecutionStatus`
- `ActionProposal`
- `ActionApproval`
- `ActionExecutionRecord`
- additive `ExecutionResult` fields:
  - `proposed_actions`
  - `action_approvals`
  - `action_executions`

Current policy scaffolding exists for future use:
- `assess_action_proposal(...)`
- `authorize_action_execution(...)`

Current live status:
- no live proposal generation yet
- no real action runner
- no real side effects
- no `/ask` changes
- no DB schema changes for the action layer

## 9. Ecosystem and evaluation stance

The project treats ecosystem claims conservatively.

Principles:
- prefer practical architectural fit over hype
- require official confirmation for major acquisition or platform claims
- avoid adopting leaked or legally ambiguous code/prompt assets
- prefer reusable patterns over copying implementation details

### Provider shortlist for future cloud benchmarking
Future benchmark candidates for coding / agent tasks:
- GPT-5.4
- GLM-5.1
- MiniMax M2.7

These are candidates for evaluation, not automatic replacements for the current stack.

## 10. Telegram / ecosystem watchlist

### Tier 1
- BohomolovLab
- ak_devs
- imatrofAI

### Tier 2
- vladyslav_ai
- veryironman
- IvanM_AI
- Intellectory (practical UX/use-case signal source)

### Tier 3 / background
- serge_ai
- neurohub
- BootUse UA
- OGoMono

### Access-limited / unrated
- AI бля (invite link only)

### Signals worth monitoring
- computer-use / browser-use
- MCP and browser integration
- coding-agent security and OpenClaw risks
- practical multi-agent DevOps / MCP / N8N / Supabase patterns
- wrapper-around-the-model product thesis
- project-scoped contexts / workspaces
- audio-to-context ingestion
- low-code Telegram / Make-style workflow automation

## 11. Skills layer direction

Public skill repositories are treated as **pattern sources**, not direct plug-and-play dependencies.

Sources worth curating from:
- Anthropic skills
- Vercel agent skills
- UI/UX skill repositories

Accepted approach:
- curate repo-local skills from good patterns
- do not mass-import third-party skill packs blindly

## 12. Security and release hygiene lessons

Recent ecosystem incidents reinforce these project-level rules:
- never treat leaked agent internals as a code source
- treat release artifact hygiene as part of system architecture
- separate permission models from prompts
- keep operation permissions explicit and deterministic
- centralize approval and side-effect policy in runtime code

## 13. Recommended near-term subsystem priorities

Most valuable future subsystem directions for Jeeves:
1. memory + handoff continuity
2. knowledge base / research wiki
3. computer-use / browser-use capability layer
4. action-contract / approval-gated execution
5. repo-local skills layer

## 14. Current next-step posture

The project has reached a stable point in the current coordination layer.

Current posture:
- Stage 1 is closed and HTTP-locked
- Stage 2 hybrid coordination is live and stable
- execution-aware hybrid with dry-run executor is stable
- future action-layer foundations exist but are not yet wired into live behavior

Recommended next engineering direction:
- isolated proposal-only generation for execution-aware hybrid
- keep live behavior unchanged until proposal semantics are stable
- defer real action execution until approval-gated action contracts and a dedicated action runner are properly designed and implemented

## 15. Notes on this file

This file is intended as a durable GitHub knowledge artifact for project continuity.

It should be updated when one of the following changes materially:
- accepted architecture
- implementation stage status
- subsystem direction
- ecosystem watchlist priorities
- action / memory / knowledge-base strategy
- model/provider evaluation shortlist
