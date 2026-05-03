# ChatGPT Exoskeleton Runbook

Status: CONFIRMED_CANON
Scope: operational runbook for using the ChatGPT exoskeleton in real chat work.
Created: 2026-05-03

## Purpose

This file is the practical execution checklist for `knowledge_base/CHATGPT_EXOSKELETON.md`.

`CHATGPT_EXOSKELETON.md` defines the model.
This runbook defines what ChatGPT must do step by step when commands such as `СТ`, `СК`, `АУД`, `БЗ`, `КОД`, `ВІДН`, `РІШ`, `ПРИВ`, or `СТАН` appear.

This is ChatGPT-side operating discipline. It is not future Jeeves runtime memory.

## Core invariant

```text
Wake -> identify command/project/privacy -> choose boot level -> read required sources -> classify -> act -> verify -> record durable result only if needed.
```

No serious work should start from unsupported internal memory when GitHub/Drive memory can be checked.

## Boot levels

Use the lowest level that is safe for the task.

```text
L0 quick: current chat only
L1 normal: starter + diary + exoskeleton
L2 project: starter + diary + exoskeleton + project docs
L3 private: L2 + Drive private hub
L4 audit/recovery: full scan + structured facts + logs
```

Defaults:
- casual/simple answer: L0
- serious global/project work: L2
- private/admin/infrastructure work: L3
- audit/recovery/memory repair: L4

## Required GitHub files for L1+

```text
knowledge_base/START_HERE_FOR_CHATGPT.md
knowledge_base/MEMORY_POLICY.md
knowledge_base/WORKING_PROTOCOL.md
knowledge_base/CHATGPT_BRANCH_CONTINUITY_BOOT.md
knowledge_base/assistant_diary.md
knowledge_base/CHATGPT_EXOSKELETON.md
```

For Jeeves/OpenClaw-style work, also read:

```text
knowledge_base/assistant_startup_prompt.md
```

For private context, also read Drive hub files:

```text
Jeeves Private Memory - START HERE
Jeeves Private Memory - Handoff
Jeeves Private Memory - Inbox Sources
Jeeves Private Memory - Recovery Audit Log
Jeeves Private Memory - Structured Facts
```

Project-specific private handoff is read only when the task needs that project.

## Command handling

### `СТ` / startup

Goal: reconstruct context before answering.

Procedure:

```text
1. Identify project alias: СК, ДЖ, БК, ГЕВ, ЛАВ, ХЛ, АТВ, ВЕН, ВСЕ.
2. Identify privacy need.
3. Select boot level.
4. Read required files for that level.
5. Continue from remembered external state, not from internal guesswork.
6. Answer shortly.
```

### `СК` / Skeleton

Goal: use or audit the ChatGPT exoskeleton.

Procedure:

```text
1. Read CHATGPT_EXOSKELETON.md.
2. Read this runbook if the task is operational.
3. Read Working Protocol if command aliases are involved.
4. For audit, check GitHub startup files + Drive hub + Structured Facts.
5. Report only gaps, risks, and next action.
```

### `АУД` / audit

Goal: find drift, contradictions, stale instructions, privacy risk, broken docs, or missing handoff.

Procedure:

```text
1. Read relevant startup/project/private docs.
2. Compare against current canon.
3. Identify exact issue and affected file.
4. Do not patch during read phase unless user explicitly asked to fix.
5. Report: what is OK, what is broken, risk, next action.
```

For `АУД СК`, check:

```text
START_HERE_FOR_CHATGPT.md
MEMORY_POLICY.md
WORKING_PROTOCOL.md
CHATGPT_BRANCH_CONTINUITY_BOOT.md
assistant_diary.md
CHATGPT_EXOSKELETON.md
CHATGPT_EXOSKELETON_RUNBOOK.md
Drive START HERE
Drive Handoff
Drive Recovery Audit Log
Structured Facts
```

### `БЗ` / knowledge-base update

Goal: write cleaned durable knowledge to the correct layer.

Procedure:

```text
1. Read starter/diary/exoskeleton.
2. Read target file before editing.
3. Classify candidate memory.
4. Decide storage route: GitHub / Drive / secret store / do not store.
5. Apply minimal patch.
6. Verify by reading changed file.
7. Record diary/audit/structured fact only if durable.
```

Forbidden:

```text
write before read
rewrite broad file when a small patch is enough
store raw private data in GitHub
claim a write succeeded before verification
```

For Google Docs, prefer replacing whole damaged sections rather than fragile index inserts inside old text.

### `КОД` / runner task

Goal: create or update runner-readable executor task.

Procedure:

```text
1. Identify project and task target.
2. Load project context and current handoff.
3. Create/update structured task file for runner consumption.
4. Include goal, context, allowed changes, forbidden changes, checks, expected output, handoff requirements, safety/privacy boundaries.
5. Do not tell user to manually copy the task to Codex when runner workflow is available.
```

### `ВІДН` / recovery

Goal: process old/current branch, export, screenshot, file, doc, or memory dump as historical source.

Procedure:

```text
1. Treat source as historical evidence, not automatic canon.
2. Extract durable items only.
3. Classify each item.
4. Cross-check existing KB/Drive when tools are available.
5. Write only one of: history source index, behavior rule, recovery audit note, approved canonical doc.
6. Never overwrite canon from old chat without approval.
7. Report shortly.
```

Recovery classifications:

```text
CONFIRMED_CANON
LIKELY_NEEDS_REVIEW
IDEA_BACKLOG
OUTDATED_REJECTED
PRIVATE_DO_NOT_STORE_RAW
TEMPORARY_DO_NOT_CANONIZE
```

### `РІШ` / decision

Goal: process a candidate decision.

Procedure:

```text
1. Determine whether the user is deciding, brainstorming, or asking.
2. Check existing canon.
3. Classify as canon/review/backlog/rejected/private/temporary.
4. If durable and approved, write minimal update.
5. If not durable, answer without storing.
```

### `ПРИВ` / private

Goal: keep private material out of public GitHub.

Procedure:

```text
1. Treat content as private by default.
2. Do not write raw content to public GitHub.
3. If storage is needed, use Drive private memory or project-specific private handoff.
4. Secrets/credentials must not be stored in plain Drive or GitHub.
5. Public notes may contain only redacted summaries.
```

### `СТАН` / handoff

Goal: prepare next-session continuity.

Procedure:

```text
1. Summarize what changed.
2. Record active state.
3. Record open risks/debt.
4. Record next action.
5. Store public-safe handoff in GitHub when appropriate, private handoff in Drive when sensitive.
6. Keep it short.
```

## Read-before-write checklist

Before any KB/Drive write, all must be true:

```text
[ ] I know the command and project.
[ ] I selected a boot level.
[ ] I read the relevant starter/diary/exoskeleton docs.
[ ] I read the target file before editing.
[ ] I know whether the content is public/private/secret/temporary.
[ ] I classified the memory item.
[ ] I know the minimal patch.
[ ] I can verify after write.
```

If any item is false, do not write yet.

## Post-write verification checklist

After a write:

```text
[ ] Re-read changed file or range.
[ ] Confirm the intended content exists.
[ ] Check for broken inserted text, duplicated sections, or stale contradictory text.
[ ] Record diary/audit/structured facts only if the change is durable.
[ ] Report briefly and honestly.
```

## Default report format

Use for memory/protocol/Skeleton work:

```text
Що сталося:
Що важливо:
Ризик:
Що робити тобі:
```

If no user action is needed:

```text
Нічого важливого. Дій від тебе не треба.
```

## Common failure modes and defenses

### Failure: write-before-read

Defense:

```text
No read -> no write.
```

### Failure: canon pollution

Defense:

```text
No classification -> no memory update.
```

### Failure: private leak

Defense:

```text
No private review -> no public GitHub.
```

### Failure: Drive text corruption from index edits

Defense:

```text
Prefer full-section replacement when editing Google Docs.
Always re-read after write.
```

### Failure: treating recovery as whole operating model

Defense:

```text
Recovery is one Skeleton layer, not the whole Skeleton.
```

### Failure: confusing ChatGPT exoskeleton with Jeeves runtime memory

Defense:

```text
Skeleton is ChatGPT-side.
Jeeves may inherit selected tested parts later.
Jeeves must not inherit ChatGPT memory chaos.
```

## Stage 1 implementation rule

Skeleton Stage 1 is behavioral and procedural.

Do not start with a large automation rewrite.

Start by enforcing:

```text
boot level selection
read-before-write
post-write verification
classification before storage
private/public routing
runner-readable tasks
short handoffs
periodic audits
```

## Completion criteria for Stage 1

Stage 1 is working when:

```text
[ ] New serious project chats start with the correct boot level.
[ ] ChatGPT does not ask the user to repeat context when memory tools are available.
[ ] KB/Drive writes happen only after reading target files.
[ ] Durable changes leave diary/audit/structured facts traces.
[ ] Private material is not copied raw into public GitHub.
[ ] Runner tasks are structured for execution, not manual copy/paste.
[ ] `АУД СК` can detect and report drift.
```

## Canonical principle

```text
Runbook turns Skeleton from document into behavior.
```
