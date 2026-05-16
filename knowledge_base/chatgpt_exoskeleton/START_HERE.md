# ChatGPT Exoskeleton START HERE

Status: CONFIRMED_CANON
Scope: historical namespace entrypoint for the current ChatGPT-facing Skeleton prototype
Created: 2026-05-04
Last updated: 2026-05-16

This is the active entrypoint at the historical `chatgpt_exoskeleton/` path. The global wake path should arrive here after `knowledge_base/START_HERE_FOR_CHATGPT.md`, `knowledge_base/MEMORY_POLICY.md`, and `knowledge_base/WORKING_PROTOCOL.md`.

## Purpose

This path describes the current ChatGPT-facing prototype of Skeleton and points toward the target Unified Skeleton Core.

ChatGPT Exoskeleton is the historical/current ChatGPT-facing prototype of Skeleton. Unified Skeleton Core is the target model-neutral external exoskeleton/control layer for LLM-assisted work.

ChatGPT is the current host/interface for using the prototype. Codex is the coding executor. Gemini is the auditor / second-brain role. OpenHands is the bounded executor role.

Skeleton stabilizes boot, memory routing, read-before-write discipline, runner-mediated execution, audit, and handoff.

Jeeves is a separate future independent assistant/product. It is not a Skeleton adapter, and it is not runtime under Skeleton.

Skeleton is the precursor, proving ground, practical toolchain, and construction scaffold used to build Jeeves more safely.

This path is not the Jeeves runtime and not the `app/` codebase.

## Default Skeleton read order

For normal Skeleton work, read these in order:

```text
knowledge_base/chatgpt_exoskeleton/START_HERE.md
knowledge_base/chatgpt_exoskeleton/CURRENT_STATE.md
knowledge_base/CHATGPT_EXOSKELETON.md
knowledge_base/CHATGPT_EXOSKELETON_RUNBOOK.md
knowledge_base/chatgpt_exoskeleton/CONTROLLED_GROWTH.md
knowledge_base/chatgpt_exoskeleton/runner_tasks/coding_lane_template_and_evidence_protocol.md
```

What each file answers:
- `CURRENT_STATE.md` = current short handoff
- `CHATGPT_EXOSKELETON.md` = what Skeleton is
- `CHATGPT_EXOSKELETON_RUNBOOK.md` = operating protocol and boot levels
- `CONTROLLED_GROWTH.md` = how Skeleton skills and lanes grow
- `coding_lane_template_and_evidence_protocol.md` = active coding lane and evidence discipline

## When to read more

Read these only when the task needs them:
- `docs/audits/2026-05-16-skeleton-jeeves-canon-audit-matrix.md` when doing boot/canon cleanup or docs compression
- `knowledge_base/CHATGPT_BRANCH_CONTINUITY_BOOT.md` when the task is about branch continuity or recovery behavior
- `knowledge_base/assistant_diary.md` when recent public-safe continuity notes matter
- topic-specific skill, task, or template docs under `knowledge_base/chatgpt_exoskeleton/` only for the active topic

Do not pull historical, diary, recovery, or task-artifact files into the default boot path.

## Active operating loop

Use this loop for Skeleton work by default:

```text
load current state
-> classify the next safe action
-> perform the smallest useful action
-> verify the result
-> checkpoint only if durable
-> report one short sentence to Oleksii
```

Avoid creating new process artifacts unless they materially improve execution, safety, or continuity.

## Namespace rule

```text
Historical name/path: ChatGPT Exoskeleton.
Current implementation: ChatGPT-facing Skeleton prototype.
Target: Unified Skeleton Core.
Future product: Jeeves, independent from Skeleton runtime.
```

Enter Jeeves runtime/code only after an explicit project switch.
