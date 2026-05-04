# Jeeves Runtime START HERE

Status: CONFIRMED_CANON
Scope: namespace marker for future Jeeves runtime and application code
Created: 2026-05-04

## Purpose

This directory is the public-safe namespace marker for the future Jeeves runtime.

The Jeeves runtime is separate from the ChatGPT Exoskeleton / Skeleton.

## Core distinction

```text
Jeeves runtime = future independent assistant runtime, app code, memory subsystem, tools, policies, audit trail, and approval model.
ChatGPT Exoskeleton / Skeleton = current external operating layer around ChatGPT.
```

Do not treat Skeleton docs as runtime implementation docs.

Do not treat runtime code or runtime PRs as Skeleton stabilization work.

## Runtime materials may include

```text
FastAPI app design
LLM provider routing
DB models and migrations
runtime policy engine
runtime action layer
API contracts
executor/runtime integration
Jeeves-specific memory subsystem design
runtime tests and validation
```

## Runtime materials do not include

```text
ChatGPT boot discipline
ChatGPT branch continuity protocol
ChatGPT read-before-answer rule
ChatGPT public/private/canon routing discipline
ChatGPT runner-readable task workflow as an exoskeleton behavior
ChatGPT assistant diary
```

Those belong to:

```text
knowledge_base/chatgpt_exoskeleton/START_HERE.md
```

## Operating rule

When the active project is `СК` / ChatGPT Exoskeleton, avoid Jeeves runtime/code work unless Oleksii explicitly switches the active project to Jeeves runtime.

When the active project is `ДЖ` / Jeeves runtime, load global boot first, then Jeeves-specific runtime docs.
