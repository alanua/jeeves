# 06 — Memory and Handoff

Last updated: 2026-04-24

## Position of this subsystem

The project treats future memory / handoff continuity as a dedicated **runtime subsystem**, separate from:
- live orchestration
- external API shapes
- GitHub project documentation / continuity insurance
- future research wiki / knowledge-base subsystem

## Critical distinction

The project has three different continuity-related layers, and they must not be confused:

1. **Runtime memory / handoff subsystem**
   - belongs to Jeeves as a running assistant system
   - supports session continuity, wake-up context, project-scoped memory, diary, retrieval, and later audio-to-context ingestion

2. **Knowledge-base / research wiki subsystem**
   - stores external research, raw evidence, compiled markdown wiki pages, reports, and derived outputs
   - supports research and Q&A over accumulated source material

3. **GitHub knowledge base**
   - is not runtime memory
   - is a protective documentation layer / continuity insurance
   - exists so the project can be continued by another developer or agent without depending on a specific AI chat or subscription context

## Why runtime memory matters

The project is being built as a long-running engineering and assistant system. Continuity between sessions is therefore a first-class runtime need.

Key continuity goals:
- preserve state across sessions
- preserve accepted decisions
- preserve active phase and next-step context
- reduce dependence on chat history alone
- make engineer-to-engineer and agent-to-agent continuation deterministic
- support project-specific context without mixing unrelated projects

## Accepted memory options and priority

### 1. Session handoff / wake-up memory

This is the highest-priority first memory layer.

Purpose:
- at the end of a work session, produce a structured handoff
- at the start of a new session, load a compact wake-up context

Expected contents:
- what was done
- current project phase
- accepted decisions
- changed files / commits / tags if available
- open risks
- blockers
- next recommended step
- stability status

Why it is valuable:
- prevents the system from starting from zero each session
- supports deterministic continuation
- fits the current operator / architect / executor workflow

### 2. Project-scoped memory

Memory must be separated by project.

Known project scopes include:
- Jeeves / OpenClaw-style personal agent
- BauClock
- Lavalamp
- Gewerbe / administrative support
- Home Assistant / IoT

Reason:
- rules, decisions, constraints, and runtime context from one project must not pollute another project

### 3. Session diary / project diary

A diary is a chronological development log.

Each meaningful cycle may record:
- date
- task
- decisions
- outcome
- commit / tag if available
- open questions
- next step

This is valuable as project history, but should not be the only runtime memory mechanism.

### 4. Verbatim memory ingest

This pattern is inspired by MemPalace.

Purpose:
- store important conversations, decisions, and session fragments close to their original wording
- avoid losing details through premature summarization
- support later semantic retrieval against primary context

Accepted stance:
- borrow the pattern, not the whole MemPalace architecture
- raw/verbatim memory is useful, but must be layered with handoff summaries and project scoping

### 5. Long-term semantic memory / retrieval

This is a later layer.

Purpose:
- store durable facts, decisions, preferences, project rules, and prior outcomes
- retrieve relevant context through semantic search / RAG-like mechanisms

Possible future inspirations:
- LightRAG-like retrieval
- ChromaDB-like vector retrieval
- MemPalace-style verbatim storage plus search

Priority:
- not first
- should come after typed handoff and project-scoped diary are stable

### 6. Audio-to-context ingestion

This is a future input channel.

Purpose:
- convert voice notes, calls, lectures, or spoken instructions into text
- extract decisions, tasks, and relevant context
- write structured output into memory, handoff, or knowledge-base layers depending on content type

Priority:
- useful later
- not part of first memory v1 implementation

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

## Accepted design stance for memory v1

Memory subsystem v1 should:
- start with typed handoff and wake-up context
- be project-scoped from the beginning
- support a simple session diary
- stay compatible with canonical runtime contracts
- avoid hidden magical prompt memory as the only source of continuity
- not try to solve full RAG or audio ingestion in the first pass

## Priority order for implementation

Accepted priority:
1. Session handoff / wake-up context
2. Project-scoped memory
3. Session diary
4. Verbatim memory ingest
5. Semantic retrieval / LightRAG-like layer
6. Audio-to-context ingestion
7. Knowledge-base subsystem separately
8. GitHub KB as continuity insurance, not runtime memory

## Important boundaries

Runtime memory is not the same as the future research knowledge base.

Runtime memory should hold continuity-relevant project and session state.

The knowledge-base subsystem should hold broader raw evidence, compiled wiki content, external research, and derived outputs.

The GitHub knowledge base is a documentation safety layer for human/agent continuation. It is not the assistant runtime memory.

## Safe next direction

The project has accepted that a typed session handoff layer is the safest first memory pass.

The first memory implementation should not start with a large vector database or a full RAG stack. It should start with typed handoff, wake-up context, project scope, and session diary primitives.
