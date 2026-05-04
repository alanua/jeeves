# ChatGPT Exoskeleton START HERE

Status: CONFIRMED_CANON
Scope: namespace entrypoint for the ChatGPT Exoskeleton / Skeleton layer
Created: 2026-05-04

## Purpose

This directory is the public-safe namespace for the ChatGPT Exoskeleton / Skeleton layer.

The Skeleton is the external operating layer around ChatGPT. It stabilizes boot, memory routing, canon checks, privacy routing, task framing, runner-mediated execution, audit, and handoff.

It is not the Jeeves runtime and not the `app/` codebase.

## Core distinction

```text
ChatGPT Exoskeleton / Skeleton = ChatGPT-side external control/support layer.
Jeeves runtime = separate future assistant runtime and application code.
```

The Skeleton may currently live in the same repository as Jeeves materials, but it must be treated as a separate layer.

## Canonical Skeleton files

Current canonical Skeleton files are still kept at their historical paths for compatibility:

```text
knowledge_base/CHATGPT_EXOSKELETON.md
knowledge_base/CHATGPT_EXOSKELETON_RUNBOOK.md
```

This namespace file exists to prevent agents and ChatGPT branches from confusing those files with Jeeves runtime code.

When the user says `СК`, `Skeleton`, or `ChatGPT Exoskeleton`, load this namespace first, then the two canonical Skeleton files above.

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
Gemini API integration
secrets or private configuration
```

## Operating rule

For current Skeleton stabilization work:

```text
do not enter Jeeves runtime/code unless Oleksii explicitly switches to Jeeves runtime work.
do not merge or close old runtime PRs as part of Skeleton cleanup.
do not create new policy documents unless explicitly requested.
prefer minimal docs-only namespace and reference cleanup.
```

## Related namespace

Jeeves runtime has its own namespace marker:

```text
knowledge_base/jeeves_runtime/START_HERE.md
```
