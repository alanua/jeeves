# 06 — Memory and Handoff

## Position of this subsystem

The project treats future memory / handoff continuity as a dedicated subsystem, separate from:
- live orchestration
- external API shapes
- future research wiki / knowledge base

## Why it matters

The project is being built as a long-running engineering and assistant system. Continuity between sessions is therefore a first-class need.

Key continuity goals:
- preserve state across sessions
- preserve accepted decisions
- preserve active phase and next-step context
- reduce dependence on chat history alone
- make engineer-to-engineer and agent-to-agent continuation deterministic

## Accepted reference signal: MemPalace

MemPalace is treated as a useful reference for future memory subsystem v1.

Patterns worth borrowing conceptually:
- verbatim memory ingestion
- wake-up / startup context
- session diary / handoff continuity

Patterns explicitly not accepted for direct adoption:
- AAAK / compression layer as the system base
- shell-hook implementations copied directly
- treating MemPalace as the architecture base for Jeeves as a whole

## Accepted design stance

Memory subsystem v1 should:
- preserve continuity
- remain separate from the knowledge-base subsystem
- be compatible with typed runtime contracts
- support wake-up context and handoff continuity
- avoid hidden magical prompt memory as the only source of continuity

## Future likely contents

Future memory / handoff artifacts are expected to include things like:
- active plan / active phase
- completed work summary
- changed files
- known risks
- blockers
- next recommended step
- stable wake-up context for the next engineering or assistant session

## Important boundary

Memory is not the same as the future research knowledge base.

Memory should hold continuity-relevant project and session state.

Knowledge base should hold broader raw evidence, compiled wiki content, external research, and derived outputs.

## Safe next direction

The project has already accepted that a typed session handoff layer would be valuable. That remains a safe future subsystem pass when the core runtime work allows it.
