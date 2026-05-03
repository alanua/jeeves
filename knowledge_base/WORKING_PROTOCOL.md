# WORKING PROTOCOL

Status: CONFIRMED_CANON
Scope: compact command aliases for collaboration with ChatGPT, ChatGPT exoskeleton, runner, executors, and future Jeeves design work.
Last consolidated: 2026-05-03

## Main command

Preferred wake command:

```text
прокинься
```

Meaning:
- wake up through the ChatGPT exoskeleton;
- read the global startup files first;
- load the general context across projects;
- do not assume the active project yet;
- wait for Oleksii to name the current project or continue with a global task.

Old aliases remain valid, but `прокинься` is the preferred entrypoint.

## Core command aliases

| Alias | Meaning | Action |
|---|---|---|
| `прокинься` | main wake command | Load global boot, Skeleton, runbook, diary; wait for active project. |
| `СТ` | startup | Old startup alias. |
| `СК` | Skeleton / ChatGPT exoskeleton | Use Skeleton model + runbook. |
| `СТ СК` | start Skeleton | Old alias for Skeleton startup. |
| `АУД СК` | audit Skeleton | Audit Skeleton state. |
| `БЗ СК` | update Skeleton KB | Update Skeleton knowledge base after read-before-write. |
| `ДЖ` | Jeeves project | Jeeves / OpenClaw-style project. |
| `СТ ДЖ` | start Jeeves | Old alias for Jeeves context. |
| `КОД <project>` | code task | Create/update runner-readable task file, not manual Codex prompt. |
| `ПРИВ` | private | Treat as private; do not write raw content to public GitHub. |
| `СТАН` | handoff | Update short handoff for next session. |

## Project switch after wake

After `прокинься`, Oleksii may name the current project:

```text
Jeeves / ДЖ
Skeleton / СК
BauClock / БК
Gewerbe / ГЕВ
Lavalamp / ЛАВ
Homelab / ХЛ
Android TV / АТВ
Van / ВЕН
```

Then load only the relevant project context.

## Boot levels

Use boot levels from `CHATGPT_EXOSKELETON_RUNBOOK.md`.

```text
L0 quick: current chat only
L1 normal: starter + diary + exoskeleton + runbook
L2 project: starter + diary + exoskeleton + runbook + project docs
L3 private: L2 + Drive private hub
L4 audit/recovery: full scan + structured facts + logs
```

Default for `прокинься`: L1 global.
Default after project selection: L2 or L3 if private context is needed.
Default for audit/recovery: L4.

## ChatGPT exoskeleton rule

Skeleton uses both files:

```text
knowledge_base/CHATGPT_EXOSKELETON.md
knowledge_base/CHATGPT_EXOSKELETON_RUNBOOK.md
```

Model = what Skeleton is.
Runbook = how to behave.

## Runner-mediated executor rule

`КОД <project>` never means “tell the user to manually pass this to Codex”.

It means:

```text
ChatGPT creates or updates a structured task file
-> runner reads it
-> runner passes it to Codex/executor
-> runner returns logs/result/handoff
-> ChatGPT reviews and prepares the next task
```

## Default report style

For memory/protocol work, report briefly:

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
