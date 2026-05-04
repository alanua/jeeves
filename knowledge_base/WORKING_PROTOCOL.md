# WORKING PROTOCOL

Status: CONFIRMED_CANON
Scope: compact command aliases for collaboration with ChatGPT, ChatGPT exoskeleton, runner, executors, and future Jeeves design work.
Last consolidated: 2026-05-04

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
| `прокинься` | main wake command | Load global boot, Skeleton namespace, runbook, diary; wait for active project. |
| `+` | accepted + permission | Continue the current active task with the next safe practical step. This is permission for bounded safe GitHub/KB actions within the active task. It is not permission for merge/close/delete/secrets/deploy/runtime work unless Oleksii explicitly names that action. |
| `СТ` | startup | Old startup alias. |
| `СК` | Skeleton / ChatGPT exoskeleton | Use Skeleton namespace + model + runbook. |
| `СТ СК` | start Skeleton | Old alias for Skeleton startup. |
| `АУД СК` | audit Skeleton | Audit Skeleton state. |
| `БЗ СК` | update Skeleton KB | Update Skeleton knowledge base after read-before-write. |
| `ДЖ` | Jeeves runtime | Future Jeeves runtime/code project; not Skeleton. |
| `СТ ДЖ` | start Jeeves runtime | Old alias for Jeeves runtime context. |
| `КОД <project>` | code task | Create/update runner-readable task file, not manual Codex prompt. |
| `ПРИВ` | private | Treat as private; do not write raw content to public GitHub. |
| `СТАН` | handoff | Update short handoff for next session. |

## Project switch after wake

After `прокинься`, Oleksii may name the current project:

```text
Jeeves runtime / ДЖ
Skeleton / СК
BauClock / БК
Gewerbe / ГЕВ
Lavalamp / ЛАВ
Homelab / ХЛ
Android TV / АТВ
Van / ВЕН
```

Then load only the relevant project context.

## Namespace rule

The repository name `alanua/jeeves` is historical and can confuse project scope.

```text
СК / Skeleton = ChatGPT-side external control/support layer.
ДЖ / Jeeves runtime = separate future assistant runtime/code layer.
```

Do not treat Skeleton work as Jeeves runtime work just because both currently live in the same repository.

## Boot levels

Use boot levels from `CHATGPT_EXOSKELETON_RUNBOOK.md`.

```text
L0 quick: current chat only
L1 normal: starter + diary + Skeleton namespace + exoskeleton + runbook
L2 project: starter + diary + Skeleton namespace + exoskeleton + runbook + project docs
L3 private: L2 + Drive private hub
L4 audit/recovery: full scan + structured facts + logs
```

Default for `прокинься`: L1 global.
Default after project selection: L2 or L3 if private context is needed.
Default for audit/recovery: L4.

## ChatGPT exoskeleton rule

Skeleton uses these files:

```text
knowledge_base/chatgpt_exoskeleton/START_HERE.md
knowledge_base/CHATGPT_EXOSKELETON.md
knowledge_base/CHATGPT_EXOSKELETON_RUNBOOK.md
```

Namespace = where Skeleton begins.
Model = what Skeleton is.
Runbook = how to behave.

## Jeeves runtime rule

Jeeves runtime starts from:

```text
knowledge_base/jeeves_runtime/START_HERE.md
knowledge_base/assistant_startup_prompt.md
```

Only enter this layer when Oleksii explicitly switches to Jeeves runtime work.

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

For Skeleton tasks, prefer:

```text
knowledge_base/chatgpt_exoskeleton/SKELETON_RUNNER_TASK_TEMPLATE.md
```

## Response compression rule

For direct chat with Oleksii, use one short human Ukrainian sentence by default: what changed, what matters, or the next step.

For documentation, use concise technical English, repository conventions, and standard technical writing patterns. Do not use personal voice, chat style, or assistant-specific wording.

Do not expose internal reasoning, long status blocks, or repeated safety explanations unless Oleksii asks.

## Default report style

For memory/protocol work, use the compact format only when a structured report is actually useful:

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
