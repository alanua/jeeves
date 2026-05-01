# Van / Camper Modernization — START HERE

Status: CONFIRMED_CANON
Project alias: `ВЕН` / `VAN`
Scope: public-safe startup file for van/camper modernization planning.
Last consolidated: 2026-05-01

## Purpose

Read this file when work is about converting or modernizing a van/Bulli into a camper, including layout, electrics, technical systems, materials, project examples, and planning.

Global startup files:
- `knowledge_base/START_HERE_FOR_CHATGPT.md`
- `knowledge_base/MEMORY_POLICY.md`
- `knowledge_base/WORKING_PROTOCOL.md`

## Working model

- User = operator / final controller
- ChatGPT = architect / planner / reviewer / task framer
- Runner = execution bridge only when a structured task file is needed
- External executors/tools may be used only through safe, explicit workflows

The preferred build direction is a middle/practical variant with minimal purchased modules and more self-build where reasonable.

## Safety rule

Electrical, gas, heating, structural, and vehicle-registration topics require careful verification and may need professional inspection. Do not treat rough planning as final legal/technical approval.

Do not store private documents/photos/raw vehicle papers in public GitHub. Use Drive private memory where needed.

## Executor workflow

For `КОД ВЕН`, create runner-readable task files only when useful and public-safe.

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
СТ ВЕН
```

## Standard files

- `current_state.md`
- `decisions.md`
- `open_questions.md`
- `tasks.md`
- `handoff.md`
- optional `executor_tasks/` for runner-readable task files
