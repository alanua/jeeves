# ChatGPT Exoskeleton START HERE

Status: CONFIRMED_CANON
Scope: namespace entrypoint for the ChatGPT Exoskeleton / Skeleton layer
Created: 2026-05-04
Last updated: 2026-05-05

## Purpose

This directory is the public-safe namespace for the ChatGPT Exoskeleton / Skeleton layer.

The Skeleton is the external operating layer around ChatGPT. It stabilizes boot, memory routing, canon checks, privacy routing, task framing, runner-mediated execution, audit, and handoff.

It is not the Jeeves runtime and not the `app/` codebase.

## Active operating loop

For Skeleton work, execute this loop by default:

```text
load current state
-> classify the next safe action
-> perform the smallest useful action
-> verify the result
-> checkpoint only if durable
-> report one short sentence to Oleksii
```

Avoid creating new process artifacts unless they materially improve execution, safety, or continuity.

## Core distinction

```text
ChatGPT Exoskeleton / Skeleton = ChatGPT-side external control/support layer.
Jeeves runtime = separate future assistant runtime and application code.
```

The Skeleton may currently live in the same repository as Jeeves materials, but it must be treated as a separate layer.

## Current state

For the latest short handoff, read:

```text
knowledge_base/chatgpt_exoskeleton/CURRENT_STATE.md
```

Use that file to continue practical Skeleton Stage 1 work without re-deriving context from scratch.

## Canonical Skeleton files

Current canonical Skeleton files are still kept at their historical paths for compatibility:

```text
knowledge_base/CHATGPT_EXOSKELETON.md
knowledge_base/CHATGPT_EXOSKELETON_RUNBOOK.md
```

This namespace file exists to prevent agents and ChatGPT branches from confusing those files with Jeeves runtime code.

When the user says `СК`, `Skeleton`, or `ChatGPT Exoskeleton`, load this namespace first, then `CURRENT_STATE.md`, then the two canonical Skeleton files above.

## Practical Skeleton files

```text
knowledge_base/chatgpt_exoskeleton/CURRENT_STATE.md
knowledge_base/chatgpt_exoskeleton/SKELETON_RUNNER_TASK_TEMPLATE.md
```

## What belongs to Skeleton

```text
boot protocol
read-before-answer
read-before-write
memory routing
public/private/canon gate
runner-readable task workflow
audit and handoff discipline
GitHub Issues/PRs as task queue and audit trail
Gemini/manual external auditor as evidence only
Antigravity as sandbox workbench and evidence only
NotebookLM/Gemini Notebooks as private evidence memory, not canon
```

## What does not belong to Skeleton

```text
Jeeves app runtime
FastAPI application code
LLM provider implementation
DB models and migrations
runtime action layer
production deployment
server/infrastructure operations
external model integration
private configuration
```

## Operating rule

For current Skeleton stabilization work:

```text
enter Jeeves runtime/code only after an explicit project switch.
keep old runtime work separate from Skeleton cleanup.
create new policy documents only when explicitly requested.
prefer minimal docs-only namespace and reference cleanup.
keep bureaucracy at the safe minimum and prefer practical work.
```

## Related namespace

Jeeves runtime has its own namespace marker:

```text
knowledge_base/jeeves_runtime/START_HERE.md
```
