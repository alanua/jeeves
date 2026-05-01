# Lavalamp / WLED / ESP32 — Handoff

Status: ACTIVE_HANDOFF
Last updated: 2026-05-01

## What changed

Project-specific KB structure for Lavalamp/WLED/ESP32 was created.

## Current rule

Use:

```text
СТ ЛАВ
```

for startup context.

Use:

```text
КОД ЛАВ
```

for exact Codex/executor tasks.

## Current focus

Keep architecture separated:

```text
geometry -> physics -> render -> WLED integration
```

## Next action

Before implementation, inspect current repo/files and define a small safe task.
