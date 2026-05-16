# MEMORY POLICY

Status: CONFIRMED_CANON
Scope: global memory storage and routing policy for the current ChatGPT-facing Skeleton prototype and related project work
Last consolidated: 2026-05-17

## Purpose

This policy defines where different kinds of memory should live and how the active startup route should recover them.

The goal is to keep ChatGPT memory compact, GitHub KB public-safe, private data out of public repositories, and the active boot surface aligned with the merged boot/protocol/lane cleanup.

This policy supports the current ChatGPT-facing Skeleton prototype. It is not Jeeves runtime memory policy.

## Ontology gate

```text
ChatGPT Exoskeleton = historical/current ChatGPT-facing prototype of Skeleton.
Unified Skeleton Core = target model-neutral external operating layer for LLM-assisted work.
ChatGPT = current host/interface for the prototype.
Codex = coding executor.
Gemini = auditor / second-brain role.
OpenHands = bounded executor role.
Jeeves = separate future independent assistant/product.
```

Critical rule:

```text
Jeeves is not a Skeleton adapter.
Jeeves is not runtime under Skeleton.
Skeleton is the precursor, proving ground, practical toolchain, and construction scaffold used to build Jeeves more safely.
```

## Active startup route

For serious work, recover context through the current active route:

```text
BOOTLOADER.md
-> knowledge_base/START_HERE_FOR_CHATGPT.md
-> knowledge_base/MEMORY_POLICY.md
-> knowledge_base/WORKING_PROTOCOL.md
-> knowledge_base/chatgpt_exoskeleton/START_HERE.md
-> project-specific route as needed
```

Supporting history is on-demand only.

Do not reintroduce a default boot chain that automatically pulls in diary, recovery, branch-continuity, or history files. Read those only when the task is recovery, audit, continuity investigation, or another topic that specifically needs them.

## Storage layers

### 1. ChatGPT internal memory

Use only as compact working memory / weak cache.

Store only:
- pointer to the active GitHub startup route
- pointer to private Drive when private context is needed
- critical global behavior rules
- minimal project anchors

Do not store noisy long histories here.
Do not treat internal ChatGPT memory as canon.

### 2. Public GitHub KB

Use for cleaned, non-sensitive, durable canon and public-safe project documentation.

Allowed:
- architecture decisions
- behavior rules
- project workflows
- runner/executor task templates
- public-safe recovery or audit outputs
- startup entrypoints and protocol docs
- Skeleton lane/gate rules
- generic code, schemas, templates, and synthetic examples
- public-safe reports
- security policies without secrets
- rejected/outdated idea summaries
- public-safe diary or continuity notes when they are worth preserving

Not allowed:
- raw private finances
- bank data
- health insurance details
- email bodies
- personal documents
- API keys/secrets
- production credentials
- private client data
- raw project-object materials that belong in private storage
- screenshots with personal data

### 3. Private Google Drive / local runner project memory

Use private Drive or local runner-accessible storage for sensitive or semi-sensitive project materials that should not live in public GitHub.

Allowed:
- private project notes
- redacted invoices and accounting context
- administrative documents
- private handoff notes
- source exports for later recovery
- documents that should not be public on GitHub
- private structured facts and indexes
- real Construction Takeoff source folders
- drawings, source inventories, extracted tables, assumptions, review items, and quantity workups

Rules:
- keep sharing restricted by default
- avoid `Anyone with the link`
- use least-privilege access
- separate folders/sections by project when possible
- do not store raw secrets/API keys unless explicitly encrypted outside the doc
- prefer redaction for bank/account/health/personal identifiers
- keep a public-safe index in GitHub that points only to categories, not sensitive contents
- keep raw project-object data in private Drive or local runner storage, not public GitHub

Public GitHub should keep only generic workflows, schemas, templates, code, synthetic examples, and public-safe reports for Construction Takeoff or similar project lanes.

### 4. Local/encrypted storage

Use for highest-sensitivity material.

Examples:
- API keys
- production secrets
- banking credentials
- identity documents
- unredacted tax/health/insurance documents
- database dumps with personal data

These should not be stored in public GitHub or plain Google Docs.

## Google Drive safety interpretation

Google Drive is acceptable as a private memory layer for this collaboration, but it is not absolute zero-risk storage.

Use it as:
- safer than public GitHub for private documents
- useful for private KB and raw source archives
- convenient for collaboration and retrieval

Do not use it as:
- a secret manager
- a place for raw credentials
- uncontrolled public link storage
- a replacement for encryption when legal/financial identity data is highly sensitive

## Default routing rule

When new information appears:

```text
public-safe durable canon -> GitHub KB
private useful context -> private Google Drive or local runner project memory
high-sensitivity secrets/credentials -> local encrypted store or secret manager
temporary logs/noise -> do not persist unless needed for audit
```

## Executor task storage rule

Runner-readable task files are public-safe only if they contain no secrets, private client data, bank data, production credentials, or private document contents.

For implementation work:

```text
ChatGPT writes structured task file
-> runner reads task file
-> runner passes to Codex/executor
-> runner returns result/logs/handoff
-> ChatGPT reviews and updates KB/handoff
```

Do not store raw executor logs in public GitHub if they contain private data, tokens, local paths that expose sensitive context, IPs, account IDs, or credentials.

## Startup memory rule

The ChatGPT settings prompt is a bootloader, not the fact database.

If ChatGPT memory is compacted, keep this pointer:

```text
For work with Oleksii, treat the ChatGPT settings prompt as a bootloader, not memory. Use the current wake command from `knowledge_base/WORKING_PROTOCOL.md`. Recover context through `BOOTLOADER.md` -> `knowledge_base/START_HERE_FOR_CHATGPT.md` -> `knowledge_base/MEMORY_POLICY.md` -> `knowledge_base/WORKING_PROTOCOL.md` -> `knowledge_base/chatgpt_exoskeleton/START_HERE.md`, then continue into the project-specific route only when needed. Use private Drive only when private context or raw project-object data is required. GitHub KB is public-safe canon after review; private Drive/local runner storage is for non-public working memory; secrets belong in local encrypted storage. Supporting diary/recovery/history files are on-demand only.
```

## Skeleton memory rule

`knowledge_base/chatgpt_exoskeleton/START_HERE.md` is the namespace entrypoint for Skeleton work.

For serious Skeleton/protocol/memory work, follow the read order from that namespace file instead of reconstructing a separate long startup chain here.

Use the supporting runbook and lane docs when the task needs them, but do not treat every supporting file as part of the default global boot path.

## Jeeves runtime memory rule

`knowledge_base/jeeves_runtime/START_HERE.md` is the namespace marker for future Jeeves runtime/code work.

Do not treat Skeleton files as runtime implementation docs.
Do not treat runtime code or runtime PRs as Skeleton stabilization work.

## Archive/reference rule

Old material should be demoted to archive/reference/on-demand rather than blindly deleted.

This includes public-safe diary, recovery, continuity, and historical files that still have evidence value but should not sit on the default startup route.

## Diary and audit routing

Use these only when the task actually needs continuity or audit evidence:
- `knowledge_base/assistant_diary.md` for public-safe global boot/collaboration diary notes
- public GitHub project KB for cleaned project canon
- `Jeeves Private Memory - Handoff` for private cross-session handoff
- `Jeeves Private Memory - Recovery Audit Log` for private recovery/audit notes
- `Jeeves Private Memory - Structured Facts` for structured private indexes and classified facts

A diary or audit entry must be classified before saving.

## Skeleton diary and canon writes

`knowledge_base/skeleton_diary.md` is an operational traceability log for Skeleton Core.

It records execution evidence such as:
- `[REAL_EXECUTION]`
- `[REAL_WRITE]`
- route completion notes
- issue-processing traces

These append-only operational entries support the rule that every real action must be traceable.

They are not the same as canon-policy patches.

Canon-policy writes include changes to durable rules, architecture, memory policy, working protocol, or governance documents. Those changes still require human review and PR approval before becoming canon.

Therefore:
- automated append-only diary entries are operational logs
- structural changes to the diary format or meaning require review
- changes to canon/policy documents require human-reviewed PR flow
- audit reports are evidence, not canon, until reviewed and explicitly promoted
