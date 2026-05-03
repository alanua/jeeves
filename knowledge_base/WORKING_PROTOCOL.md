# WORKING PROTOCOL

Status: CONFIRMED_CANON
Scope: compact mnemonic command aliases for collaboration with ChatGPT, ChatGPT exoskeleton, runner, executors, and future Jeeves design work.
Last consolidated: 2026-05-03

## Purpose

Use short meaningful command aliases in chat to reduce typing and keep work structured.

Main rule: prefer Ukrainian mnemonic aliases because they are easier to remember. Latin aliases remain supported as secondary aliases.

## Core command aliases

| Preferred alias | Meaning in Ukrainian | English alias | English meaning | Action |
|---|---|---|---|---|
| `СТ` | старт | `ST` | STARTUP | Load external memory first: GitHub KB, ChatGPT exoskeleton/runbook, and, if needed, Google Drive private memory. Reconstruct context before answering. |
| `СК` | скелетон / екзоскелет | `SK` | SKELETON | Use or audit the ChatGPT exoskeleton model and runbook: boot, diary, memory tools, dev-team workflow, runner, guardrails, recovery. |
| `СТАН` | стан / передача стану | `HO` | HANDOFF | Update short handoff for the next session: what changed, what was fixed, what remains open, next action. |
| `РІШ` | рішення | `DC` | DECISION | Treat this as a candidate decision. Classify, check against canon, and save if durable. |
| `ВІДН` | відновлення | `RC` | RECOVERY | Process a branch/export/dump as historical source. Use the Recovery / Historical Source Layer and the runbook recovery checklist. |
| `КОД` | задача для коду | `TC` | TASK_FOR_EXECUTOR | Create or update a runner-readable structured task file. Runner passes it to Codex/executor; the user does not manually copy tasks to Codex. |
| `ПРИВ` | приватне | `PN` | PRIVATE_NOTE | Treat as private. Do not write raw content to public GitHub. Use Drive/private layer if storage is needed. |
| `АУД` | аудит | `AU` | AUDIT | Check memory/project/exoskeleton state for noise, conflicts, outdated items, privacy risks, or missing handoff. Use the runbook audit checklist. |
| `БЗ` | база знань | `KB` | KNOWLEDGE_BASE_UPDATE | Write cleaned durable knowledge to the correct KB layer. Use read-before-write and post-write verification from the runbook. |
| `ДР` | Драйв | `GV` | GOOGLE_DRIVE_PRIVATE | Use Google Drive private memory layer for private working context. |
| `ГХ` | GitHub | `GH` | GITHUB_CANON | Use public-safe GitHub KB as canonical memory/documentation. |

## Project/context aliases

| Preferred alias | Meaning | Latin alias |
|---|---|---|
| `СК` | ChatGPT exoskeleton / Skeleton | `SK` |
| `ДЖ` | Jeeves / OpenClaw-style agent system | `JV` |
| `БК` | BauClock | `BC` |
| `ГЕВ` | Gewerbe/accounting/admin in Germany | `GW` |
| `ЛАВ` | Lavalamp / WLED / ESP32 | `LV` |
| `ХЛ` | Homelab / Proxmox / Home Assistant | `HL` |
| `АТВ` | Android TV / device experiments | `ATV` |
| `ВЕН` | Van/camper modernization | `VAN` |
| `ВСЕ` | all projects / global context | `ALL` |

## Status/classification aliases

| Preferred alias | Meaning in Ukrainian | Latin alias | Full classification |
|---|---|---|---|
| `КАН` | канон | `CC` | CONFIRMED_CANON |
| `ПЕР` | перевірити | `NR` | NEEDS_REVIEW / LIKELY_NEEDS_REVIEW |
| `БЕК` | беклог | `BL` | BACKLOG / IDEA_BACKLOG |
| `ВІДК` | відкинуто | `RJ` | REJECTED / OUTDATED_REJECTED |
| `ПРВ` | приватне | `PR` | PRIVATE_DO_NOT_STORE_RAW |
| `ТИМ` | тимчасове | `TMP` | TEMPORARY_DO_NOT_CANONIZE |

## Boot levels

Use boot levels from `CHATGPT_EXOSKELETON_RUNBOOK.md`.

```text
L0 quick: current chat only
L1 normal: starter + diary + exoskeleton + runbook
L2 project: starter + diary + exoskeleton + runbook + project docs
L3 private: L2 + Drive private hub
L4 audit/recovery: full scan + structured facts + logs
```

Default for serious project work: L2.
Default for private/admin/infrastructure work: L3.
Default for audit/recovery: L4.

## English command translations

| English command | Ukrainian translation | Preferred Ukrainian alias |
|---|---|---|
| STARTUP | старт / підтягнути стартову пам’ять | `СТ` |
| SKELETON | скелетон / екзоскелет | `СК` |
| HANDOFF | передача стану / стан для наступної сесії | `СТАН` |
| DECISION | рішення | `РІШ` |
| RECOVERY | відновлення / обробка історичного джерела | `ВІДН` |
| TASK_FOR_EXECUTOR | задача для runner/Codex/executor | `КОД` |
| PRIVATE_NOTE | приватна нотатка | `ПРИВ` |
| AUDIT | аудит / перевірка | `АУД` |
| KNOWLEDGE_BASE_UPDATE | оновлення бази знань | `БЗ` |
| GOOGLE_DRIVE_PRIVATE | приватний Google Drive | `ДР` |
| GITHUB_CANON | GitHub-канон | `ГХ` |

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

Task files must be written for runner consumption:
- clear goal
- context
- allowed changes
- forbidden changes
- checks/commands
- expected output
- handoff requirements
- safety/privacy boundaries

## ChatGPT exoskeleton rule

`СК` / `SK` refers to both:

```text
knowledge_base/CHATGPT_EXOSKELETON.md
knowledge_base/CHATGPT_EXOSKELETON_RUNBOOK.md
```

The model defines what Skeleton is.
The runbook defines how to use it in real work.

When the user says `СК`, `Skeleton`, `екзоскелет`, or asks to strengthen ChatGPT through the exoskeleton, use both files.

## Examples

```text
СТ ДЖ
```
Load Jeeves startup context from GitHub/Drive before answering.

```text
СТ СК
```
Load ChatGPT exoskeleton and runbook context.

```text
АУД СК
```
Audit the ChatGPT exoskeleton and runbook state.

```text
БЗ СК
```
Update Skeleton knowledge base using read-before-write and post-write verification.

```text
КОД ЛАВ
```
Create/update a runner-readable executor task for Lavalamp. Do not tell the user to copy it to Codex manually.

## Legacy keyboard-layout aliases

Old mechanical Ukrainian-keyboard equivalents are deprecated because they are not mnemonic.

If the user uses them accidentally, still interpret them, but do not teach them as the preferred protocol.

## Operating rule

When the user writes an alias, infer the full protocol without asking for expansion.

If multiple aliases appear together, combine them.

Preferred style:

```text
КОМАНДА ПРОЄКТ КЛАСИФІКАЦІЯ
```

Examples:

```text
СТ ДЖ
СТ СК
РІШ БК КАН
ПРИВ ГЕВ
ВІДН ДЖ
КОД ЛАВ
СТАН БК
АУД ВСЕ
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
