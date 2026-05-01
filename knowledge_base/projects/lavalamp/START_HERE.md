# Lavalamp / WLED / ESP32 — START HERE

Status: CONFIRMED_CANON
Project alias: `ЛАВ` / `LV`
Scope: public-safe startup file for the cylinder lava lamp / WLED / ESP32 project.
Last consolidated: 2026-05-01

## Purpose

Read this file when work is about the cylinder lava lamp project, WLED effects, ESP32 performance, cylindrical mapping, animation kernels, PlatformIO builds, or Codex tasking for this project.

## Canonical working model

Use the same operator/architect/executor model as BauClock:
- User = operator
- ChatGPT = architect/reviewer/task framer
- Codex = executor
- Runtime = ESP32/WLED

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

Use `КОД ЛАВ` for Codex/executor tasks.

## Standard files

- `current_state.md`
- `decisions.md`
- `open_questions.md`
- `tasks.md`
- `handoff.md`
