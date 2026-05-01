# Project Index

Status: CONFIRMED_CANON
Last consolidated: 2026-05-01

## Purpose

Global index of active collaboration/project memory areas.

Use this file to select the correct project memory before answering.

## Required global startup files

At serious project startup, use:

```text
knowledge_base/START_HERE_FOR_CHATGPT.md
knowledge_base/MEMORY_POLICY.md
knowledge_base/WORKING_PROTOCOL.md
```

For Jeeves-specific work also use:

```text
knowledge_base/assistant_startup_prompt.md
```

## Projects

| Alias | Project | Folder | Storage note |
|---|---|---|---|
| `ДЖ` | Jeeves / OpenClaw-style agent system | `knowledge_base/projects/jeeves/` | Public-safe canon; private raw sources in Drive |
| `БК` | BauClock | `knowledge_base/projects/bauclock/` | Public-safe product canon; private client/accounting details go to Drive |
| `ГЕВ` | Gewerbe/accounting/admin in Germany | `knowledge_base/projects/gewerbe/` | Public-safe workflow only; private details go to Drive |
| `ЛАВ` | Lavalamp / WLED / ESP32 | `knowledge_base/projects/lavalamp/` | Technical canon; local/private build details only if safe |
| `ХЛ` | Homelab / Proxmox / Home Assistant | `knowledge_base/projects/homelab/` | Technical canon; secrets/IPs/tokens excluded |
| `АТВ` | Android TV / device experiments | `knowledge_base/projects/android_tv/` | Technical/troubleshooting canon |
| `ВЕН` | Van/camper modernization | `knowledge_base/projects/van/` | Project planning canon; private docs/photos in Drive if needed |

## Standard files per project

- `START_HERE.md`
- `current_state.md`
- `decisions.md`
- `open_questions.md`
- `tasks.md`
- `handoff.md`
- optional `executor_tasks/` or project-specific legacy `codex_tasks/` for runner-readable task files

## Global commands

```text
СТ <alias>     = load project startup context
СТАН <alias>   = update project handoff
РІШ <alias>    = decision candidate / confirmed decision when accepted
КОД <alias>    = create/update runner-readable task file
АУД <alias>    = audit project memory/state
ПРИВ <alias>   = private context; do not store raw in public GitHub
```

## Executor handoff rule

`КОД <alias>` means:

```text
ChatGPT writes structured task file
-> runner reads it
-> runner passes it to Codex/executor
-> runner returns result/logs/handoff
-> ChatGPT reviews and updates KB/handoff
```

Do not tell the user to manually copy tasks to Codex when runner workflow is available.
