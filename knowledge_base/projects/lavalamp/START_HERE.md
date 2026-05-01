# Lavalamp / WLED / ESP32 — START HERE

Status: CONFIRMED_CANON
Project alias: `ЛАВ` / `LV`
Scope: public-safe startup file for the cylinder lava lamp / WLED / ESP32 project.
Last consolidated: 2026-05-01

## Purpose

Read this file when work is about the cylinder lava lamp project, WLED effects, ESP32 performance, cylindrical mapping, animation kernels, PlatformIO builds, or executor tasking for this project.

Global startup files:
- `knowledge_base/START_HERE_FOR_CHATGPT.md`
- `knowledge_base/MEMORY_POLICY.md`
- `knowledge_base/WORKING_PROTOCOL.md`

## Canonical working model

Use the same operator/architect/runner/executor model as other projects:
- User = operator / final controller
- ChatGPT = architect / reviewer / task framer
- Runner = execution bridge that reads structured task files and passes them to Codex/executors
- Codex = implementation executor
- Runtime = ESP32/WLED

## Executor workflow

For `КОД ЛАВ`:

```text
ChatGPT creates or updates runner-readable task file
-> runner reads task file
-> runner gives task to Codex/executor
-> runner returns result/logs/handoff
-> ChatGPT reviews and updates KB/handoff
```

Do not tell the user to manually copy tasks into Codex when runner workflow is available.

## Architecture base

Core separation:

```text
geometry -> physics -> render -> WLED integration
```

Do not mix physics, coordinate mapping, and rendering.

Important layers/names:
- cylinder geometry
- lava engine
- cylinder pipeline
- lava scene
- WLED integration

## Startup command

```text
СТ ЛАВ
```

Use `КОД ЛАВ` for runner-readable executor tasks.

## Standard files

- `current_state.md`
- `decisions.md`
- `open_questions.md`
- `tasks.md`
- `handoff.md`
- optional `executor_tasks/` or equivalent for runner-readable task files
