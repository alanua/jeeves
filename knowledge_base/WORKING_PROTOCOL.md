# WORKING PROTOCOL

Status: CONFIRMED_CANON
Scope: compact mnemonic command aliases for collaboration with ChatGPT and future Jeeves.
Last consolidated: 2026-05-01

## Purpose

Use short meaningful command aliases in chat to reduce typing and keep work structured.

Main rule: prefer Ukrainian mnemonic aliases because they are easier to remember. Latin aliases remain supported as secondary aliases.

## Core command aliases

| Preferred alias | Meaning in Ukrainian | English alias | English meaning | Action |
|---|---|---|---|---|
| `СТ` | старт | `ST` | STARTUP | Load external memory first: GitHub KB and, if needed, Google Drive private memory. Reconstruct context before answering. |
| `СТАН` | стан / передача стану | `HO` | HANDOFF | Update short handoff for the next session: what changed, what was fixed, what remains open, next action. |
| `РІШ` | рішення | `DC` | DECISION | Treat this as a candidate decision. Classify, check against canon, and save if durable. |
| `ВІДН` | відновлення | `RC` | RECOVERY | Process a branch/export/dump as historical source. Extract durable knowledge, classify, and do not blindly canonize. |
| `КОД` | код / задача для коду | `TC` | TASK_FOR_CODEX | Produce a precise implementation task for Codex or another coding executor. |
| `ПРИВ` | приватне | `PN` | PRIVATE_NOTE | Treat as private. Do not write raw content to public GitHub. Use Drive/private layer if storage is needed. |
| `АУД` | аудит | `AU` | AUDIT | Check memory/project state for noise, conflicts, outdated items, privacy risks, or missing handoff. |
| `БЗ` | база знань | `KB` | KNOWLEDGE_BASE_UPDATE | Write cleaned durable knowledge to the correct KB layer if tools are available. |
| `ДР` | Драйв | `GV` | GOOGLE_DRIVE_PRIVATE | Use Google Drive private memory layer for private working context. |
| `ГХ` | GitHub | `GH` | GITHUB_CANON | Use public-safe GitHub KB as canonical memory. |

## Project/context aliases

| Preferred alias | Meaning | Latin alias |
|---|---|---|
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

## English command translations

| English command | Ukrainian translation | Preferred Ukrainian alias |
|---|---|---|
| STARTUP | старт / підтягнути стартову пам’ять | `СТ` |
| HANDOFF | передача стану / стан для наступної сесії | `СТАН` |
| DECISION | рішення | `РІШ` |
| RECOVERY | відновлення / обробка історичного джерела | `ВІДН` |
| TASK_FOR_CODEX | задача для Codex / задача для коду | `КОД` |
| PRIVATE_NOTE | приватна нотатка | `ПРИВ` |
| AUDIT | аудит / перевірка | `АУД` |
| KNOWLEDGE_BASE_UPDATE | оновлення бази знань | `БЗ` |
| GOOGLE_DRIVE_PRIVATE | приватний Google Drive | `ДР` |
| GITHUB_CANON | GitHub-канон | `ГХ` |

## Examples

```text
СТ ДЖ
```
Same as `ST JV`: load Jeeves startup context from GitHub/Drive before answering.

```text
РІШ БК
```
Same as `DC BC`: BauClock decision candidate. Check, classify, and save if durable.

```text
ПРИВ ГЕВ
```
Same as `PN GW`: private Gewerbe/admin context. Do not store raw in public GitHub.

```text
ВІДН ДЖ
```
Same as `RC JV`: process a Jeeves branch/memory dump as historical source.

```text
КОД ЛАВ
```
Same as `TC LV`: prepare an exact Codex/executor task for Lavalamp.

```text
СТАН БК
```
Same as `HO BC`: update BauClock handoff after this work session.

```text
АУД ВСЕ
```
Same as `AU ALL`: audit overall memory structure and report issues briefly.

```text
РІШ ПРИВ ГЕВ
```
Same as `DC PN GW`: this is a private Gewerbe decision candidate; analyze/classify it, but do not store raw content in public GitHub.

## Legacy keyboard-layout aliases

Old mechanical Ukrainian-keyboard equivalents like `ІЕ`, `РЩ`, `ВС`, `КС`, `ЕС`, `ЗТ`, `ФГ`, `ЛИ`, `ПМ`, `ПР` are deprecated because they are not mnemonic.

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
