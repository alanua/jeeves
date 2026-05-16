# ChatGPT Exoskeleton Runbook

Status: CONFIRMED_CANON
Scope: supporting runbook/checklist for applying the active protocol safely
Created: 2026-05-03
Last consolidated: 2026-05-16

## Purpose

`knowledge_base/WORKING_PROTOCOL.md` is the active operating protocol.

This runbook is the supporting checklist for applying that protocol in real work. It keeps boot-level selection, read/write verification flow, evidence interpretation, recovery handling, and common failure defenses.

It does not redefine the full active alias table or reintroduce the long boot chain removed in Phase 2.

## Active references

Use these as the current operating stack:

```text
knowledge_base/START_HERE_FOR_CHATGPT.md
knowledge_base/MEMORY_POLICY.md
knowledge_base/WORKING_PROTOCOL.md
knowledge_base/chatgpt_exoskeleton/START_HERE.md
knowledge_base/CHATGPT_EXOSKELETON.md
knowledge_base/CHATGPT_EXOSKELETON_RUNBOOK.md
```

When instruction, canon, or ontology wording changes are involved, treat `knowledge_base/WORKING_PROTOCOL.md` as the active rules source and recheck its ontology gate before editing.

## Core invariant

```text
identify command/project/privacy
-> choose the lowest safe boot level
-> read required sources
-> classify the next safe action
-> act
-> verify
-> record durable result only if needed
```

No serious work should start from unsupported internal memory when GitHub or Drive memory can be checked.

## Boot levels

Use the lowest level that is safe for the task.

```text
L0 quick: current chat only
L1 normal: active startup route from START_HERE_FOR_CHATGPT.md
L2 project: L1 + relevant namespace/project docs
L3 private: L2 + private memory when needed
L4 audit/recovery: L2/L3 + audit/history/reference sources needed for drift or recovery
```

Defaults:
- casual/simple answer: L0
- serious global/project work: L2
- private/admin/infrastructure work: L3
- audit/recovery/memory repair: L4

## Command application patterns

Use the alias meanings from `knowledge_base/WORKING_PROTOCOL.md`. Then apply the matching pattern below.

### Startup / project switch

```text
1. Identify project alias and privacy need.
2. Choose the lowest safe boot level.
3. Read only the needed startup/project sources.
4. Continue from external state, not from internal guesswork.
```

### Audit

```text
1. Read the relevant canon/reference first.
2. Compare the current source against active rules.
3. Report drift, risk, and next action before patching unless the user explicitly asked to fix.
```

### Knowledge-base update

```text
1. Read the active rules and the target file.
2. Classify the candidate memory.
3. Choose the correct storage route from MEMORY_POLICY.
4. Apply the minimal patch.
5. Verify by rereading the result.
```

### Runner task

```text
1. Load the active project context.
2. Create/update a runner-readable task with goal, context, allowed changes, forbidden changes, checks, expected output, handoff requirements, and safety boundaries.
3. Keep ChatGPT in the framing/review role and the executor in the bounded execution role.
```

### Recovery

```text
1. Treat old material as historical evidence, not automatic canon.
2. Extract only durable items.
3. Classify before writing anything back.
4. Preserve history as archive/reference instead of deleting it blindly.
```

### Canon or instruction change

```text
1. Read the current rule first.
2. Check the ontology gate in WORKING_PROTOCOL.
3. Critique before action: find duplicate/conflict/ambiguity/risk.
4. Patch minimally only after that critique.
```

## Read-before-answer checklist

Before status, architecture, memory, protocol, runner, or canon answers:

```text
[ ] I identified the exact topic and likely canon source.
[ ] I checked the relevant GitHub or Drive source when tools are available.
[ ] I am not relying on weak internal memory for a factual claim.
[ ] I can name the source used, or I can say it was not checked.
```

If any item is false, do not make a confident status or canon claim.

## Read-before-write checklist

Before any KB, Drive, or task-file write:

```text
[ ] I know the command and project.
[ ] I selected the lowest safe boot level.
[ ] I read the relevant active rules.
[ ] I read the target file before editing.
[ ] I know whether the content is public, private, secret, or temporary.
[ ] I classified the item.
[ ] I know the minimal patch.
```

If any item is false, do not write yet.

## Post-write verification checklist

After a write:

```text
[ ] Re-read the changed file or range.
[ ] Confirm the intended content exists.
[ ] Check for broken inserted text, duplicated sections, or stale contradictory text.
[ ] Record diary/audit/structured facts only if the change is durable.
[ ] Report briefly and honestly.
```

## Evidence interpretation checklist

```text
[ ] GitHub issues, PRs, and comments are treated as the public evidence trail.
[ ] Executor self-report is not treated as sufficient evidence.
[ ] Coding-task evidence includes diff, checks/tests, and git status.
[ ] Without explicit Oleksii merge command, stop at review/draft PR state.
[ ] Without explicit approval, do not deploy.
[ ] Do not touch secrets, env, server, or runtime access during normal protocol work.
```

## Common failure modes and defenses

### Failure: answer-before-read

Defense:

```text
For serious status/canon/protocol claims, read the external source first or answer with uncertainty.
```

### Failure: write-before-read

Defense:

```text
No read -> no write.
```

### Failure: canon pollution

Defense:

```text
No classification -> no canon update.
```

### Failure: private leak

Defense:

```text
Use MEMORY_POLICY routing before any public write.
```

### Failure: ontology drift

Defense:

```text
Use the ontology gate from WORKING_PROTOCOL before changing Skeleton, ChatGPT, or Jeeves instruction text.
```

### Failure: merge/deploy drift

Defense:

```text
No merge without explicit Oleksii command.
No deploy without explicit approval.
```

## Canonical principle

```text
Runbook turns protocol from text into behavior.
```
