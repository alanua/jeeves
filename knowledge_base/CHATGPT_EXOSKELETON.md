# ChatGPT Exoskeleton

Status: CONFIRMED_CANON
Scope: ChatGPT-side operating layer: boot, memory tools, development-team workflow, guardrails, audit, and runner-mediated execution. Design input for future Jeeves only after review.
Created: 2026-05-03

## Purpose

This document defines the working model of the external exoskeleton built around ChatGPT.

The exoskeleton is not a replacement for ChatGPT's internal runtime and not Jeeves runtime memory. It is a controlled external operating layer that compensates for ChatGPT's known weak points and amplifies its strong points.

Future Jeeves may reuse selected exoskeleton parts only after they are tested, cleaned, reviewed, adapted, and approved.

## Priority

Priority: build and stabilize the ChatGPT exoskeleton.

The development-team workflow is part of the exoskeleton.

The memory tools are parts of the exoskeleton.

This means:
- ChatGPT first learns to work reliably through the exoskeleton.
- The exoskeleton protects weak points and amplifies strong points.
- Some exoskeleton parts may later become Jeeves modules or design patterns.
- Raw ChatGPT memory/diary must not be blindly copied into Jeeves.

## Core distinction

```text
Memory tools = boot, diary, handoff, audit, structured facts, runner workflow, read-before-write.
Memories = facts, decisions, project history, examples, context, traces, source material.
Development team = runner-mediated executor workflow, Codex/executor tasks, review loops, logs, handoff.
```

Memory tools and the development-team workflow are currently optimized for ChatGPT and its limits.

Memories may be partially migrated into Jeeves over time, but only as classified, reviewed, cleaned source material.

## Why the exoskeleton exists

ChatGPT has strong capabilities:
- reasoning
- synthesis
- language
- review
- planning
- structuring
- task framing
- architecture critique

ChatGPT also has platform/runtime limits that cannot be fully removed from inside chat:
- unreliable branch-local context
- weak internal memory
- no stable self-managed long-term diary
- limited control over tool persistence
- risk of writing before reading
- risk of mixing brainstorming with canon
- risk of leaking private context into public notes
- limited direct execution continuity

The exoskeleton compensates for these limits externally.

## Working model

```text
WAKE
-> BOOT
-> LOAD CONTEXT
-> CLASSIFY TASK
-> PLAN
-> ACT / DELEGATE
-> TRACE
-> REVIEW
-> SAVE ONLY DURABLE MEMORY
-> HANDOFF
```

## Exoskeleton layers

### 0. Wake / Trigger Layer

Recognize explicit commands and task type.

Important triggers:
- `СТ`
- `СТ ВСЕ`
- `СТ ДЖ`
- `АУД ВСЕ`
- `РІШ`
- `КОД`
- `ПРИВ`
- `ВІДН`

Rule:

```text
User command
-> detect project/scope/privacy
-> choose boot depth
-> only then answer/work
```

### 1. Boot Layer

Protects against branch amnesia.

Minimal boot:

```text
START_HERE_FOR_CHATGPT.md
MEMORY_POLICY.md
WORKING_PROTOCOL.md
CHATGPT_BRANCH_CONTINUITY_BOOT.md
assistant_diary.md
CHATGPT_EXOSKELETON.md
```

For Jeeves/OpenClaw-style work:

```text
+ assistant_startup_prompt.md
```

For private context:

```text
+ Drive START HERE
+ Drive Handoff
+ Drive Structured Facts
+ Drive Recovery Audit Log
+ project-specific private handoff if needed
```

Rule:

```text
No boot -> no trust in the answer.
```

### 2. Context Loader

Loads enough relevant context, not all context.

Classify the task first:
- global
- Jeeves
- BauClock
- Gewerbe/private
- runner/Hetzner
- coding task
- recovery/audit
- side project

Rule:

```text
enough context, not all context
```

### 3. Memory Router

Routes information to the right layer.

```text
public-safe durable rule -> GitHub KB
private durable context -> Drive private memory
raw private source -> Drive Inbox / private document
secret -> not GitHub/Drive plain text
temporary log -> do not persist unless needed
project fact -> project-specific section
```

### 4. Read-Before-Write Gate

Prevents memory chaos.

Before changing GitHub KB or Drive memory:

```text
read starter
-> read diary
-> read relevant project docs / private handoff if needed
-> read current target file
-> compare against current canon
-> identify exact conflict or missing rule
-> write minimal classified patch only
-> verify after write
-> record diary/audit if durable
```

Forbidden:
- write first, think later
- broad rewrite when a small patch is enough
- blind canonization
- raw private data in public GitHub

### 5. Work Planner

Converts conversation into controlled work.

Simple question:

```text
answer directly
```

Architecture/problem solving:

```text
read -> compare -> model -> risks -> next action
```

Coding task:

```text
КОД <project>
-> create/update runner-readable task
-> runner executes
-> logs/result return
-> review
-> next task
```

Recovery/audit:

```text
source dump
-> extract durable items
-> classify
-> update KB/Drive if needed
-> short report
```

### 6. Tool / Runner Layer

Provides controlled hands.

Current tool categories:
- GitHub = public canon/docs/tasks
- Google Drive = private memory/docs/sheets
- Structured Facts = indexed memory
- Runner = bridge to Codex/executors
- Web = current public information
- Calendar/Gmail = only when explicitly relevant/private and permitted

Rule:

```text
minimal toolset for the task
no write/delete without explicit reason
no unsafe private data routing
```

### 7. Development Team Layer

The development team is part of the exoskeleton.

```text
ChatGPT = architect / reviewer / task framer
Runner = dispatcher / executor bridge
Codex/executor = implementation worker
Logs = evidence
Review loop = quality control
User = owner / final controller
```

Workflow:

```text
architect creates task
executor implements
tests run
logs return
architect reviews
fix task created
handoff updated
```

Do not spawn many agents without concrete task, workspace, tests, logs, cost boundaries, approval points, and shutdown path.

### 8. Observability / Diary / Audit

Provides traceability.

Minimum trace fields:
- task id
- project
- input summary
- files read
- files changed
- tools used
- decision/classification
- result
- errors
- next action

Current ChatGPT-side trace tools:
- `assistant_diary.md`
- Drive Handoff
- Recovery Audit Log
- Structured Facts
- runner logs

### 9. Guardrails / Privacy / Safety

Protects against unsafe action and leakage.

Guardrail types:
- input guardrail: is the task allowed?
- memory guardrail: where may this be stored?
- tool guardrail: is this tool/action allowed?
- write guardrail: was read-before-write done?
- privacy guardrail: is there raw private/secrets data?
- output guardrail: do not claim actions that were not done

Core rule:

```text
No read -> no write.
No classification -> no memory update.
No private review -> no public GitHub.
```

### 10. Compression / Promotion / Migration Layer

Prevents memory rot.

Periodic cleanup:

```text
raw notes -> reviewed facts
long chat -> short decision
temporary logs -> delete/archive
private source -> redacted summary
repeated rule -> single canon rule
old contradiction -> superseded/rejected
```

Migration to Jeeves:

```text
ChatGPT exoskeleton tool
-> observed in use
-> works / fails
-> cleaned design
-> adapted to Jeeves runtime
-> tested
-> approved
-> implemented
```

Never migrate:
- raw ChatGPT diary
- Drive chaos
- temporary patches
- branch-specific workarounds
- private data
- unreviewed memories

## Boot levels

Use boot levels to avoid both amnesia and excessive context loading.

```text
L0 quick: current chat only
L1 normal: starter + diary + exoskeleton
L2 project: starter + diary + exoskeleton + project docs
L3 private: L2 + Drive private hub
L4 audit/recovery: full scan + structured facts + logs
```

Default for serious project work: L2.
Default for private/admin/infrastructure work: L3.
Default for audit/recovery: L4.

## Strong operating formula

```text
Boot protects against amnesia.
Diary protects against drift.
Structured facts protect against chaos.
Runner protects against manual copy/paste work.
Audit protects against self-confident errors.
Guardrails protect against unsafe tools and private leaks.
Compression protects against memory rot.
```

## Canonical principle

```text
ChatGPT wears the exoskeleton now.
The development team workflow is part of the exoskeleton.
The memory tools are parts of the exoskeleton.
Jeeves may inherit selected tested tools later.
Jeeves must not inherit ChatGPT's memory chaos.
```
