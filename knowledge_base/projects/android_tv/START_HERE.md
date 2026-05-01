# Android TV / Device Experiments — START HERE

Status: CONFIRMED_CANON
Project alias: `АТВ` / `ATV`
Scope: public-safe startup file for Android TV, x86 Android, rEFInd, Waydroid/ATV experiments, and device troubleshooting.
Last consolidated: 2026-05-01

## Purpose

Read this file when work is about Android TV installation, x86 Android variants, rEFInd booting, ADB, BIOS/boot recovery, old tablets/TV boxes, or media app experiments.

Global startup files:
- `knowledge_base/START_HERE_FOR_CHATGPT.md`
- `knowledge_base/MEMORY_POLICY.md`
- `knowledge_base/WORKING_PROTOCOL.md`

## Working model

- User = operator / final controller
- ChatGPT = troubleshooting guide / architect / reviewer / task framer
- Runner = execution bridge only when a structured task file is needed
- Runtime = physical device / VM / boot media / Android environment

Work step-by-step. Verify after each risky boot/storage action.

## Safety rule

Device experiments can break boot. Avoid destructive repartition/format/flash commands unless explicitly intended, backed up, and confirmed.

Do not store private device identifiers, account tokens, Wi-Fi credentials, or private service credentials in public GitHub.

## Executor workflow

For `КОД АТВ`, create runner-readable task files only when useful and public-safe.

Correct flow when a task file is appropriate:

```text
ChatGPT creates or updates runner-readable task file
-> runner reads task file
-> runner gives task to executor
-> runner returns result/logs/handoff
-> ChatGPT reviews and updates KB/handoff
```

Do not tell the user to manually copy tasks into Codex/executor when runner workflow is available.

## Startup command

```text
СТ АТВ
```

## Standard files

- `current_state.md`
- `decisions.md`
- `open_questions.md`
- `tasks.md`
- `handoff.md`
- optional `executor_tasks/` for runner-readable task files
