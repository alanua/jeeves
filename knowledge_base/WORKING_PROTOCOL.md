# WORKING PROTOCOL

Status: CONFIRMED_CANON
Scope: compact command aliases for collaboration with ChatGPT and future Jeeves.
Last consolidated: 2026-05-01

## Purpose

Use short command aliases in chat to reduce typing and keep work structured.

These aliases apply across projects, unless a project-specific protocol overrides them.

## Core aliases

| Alias | Ukrainian-keyboard equivalent | Full meaning | Action |
|---|---|---|---|
| `ST` | `ІЕ` | STARTUP | Load external memory first: GitHub KB and, if needed, Google Drive private memory. Reconstruct context before answering. |
| `HO` | `РЩ` | HANDOFF | Update short handoff for the next session: what changed, what was fixed, what remains open, next action. |
| `DC` | `ВС` | DECISION | Treat this as a candidate decision. Classify, check against canon, and save if durable. |
| `RC` | `КС` | RECOVERY | Process a branch/export/dump as historical source. Extract durable knowledge, classify, and do not blindly canonize. |
| `TC` | `ЕС` | TASK_FOR_CODEX | Produce a precise implementation task for Codex or another coding executor. |
| `PN` | `ЗТ` | PRIVATE_NOTE | Treat as private. Do not write raw content to public GitHub. Use Drive/private layer if storage is needed. |
| `AU` | `ФГ` | AUDIT | Check memory/project state for noise, conflicts, outdated items, privacy risks, or missing handoff. |
| `KB` | `ЛИ` | KNOWLEDGE_BASE_UPDATE | Write cleaned durable knowledge to the correct KB layer if tools are available. |
| `GV` | `ПМ` | GOOGLE_DRIVE_PRIVATE | Use Google Drive private memory layer for private working context. |
| `GH` | `ПР` | GITHUB_CANON | Use public-safe GitHub KB as canonical memory. |

## Project/context aliases

| Alias | Ukrainian-keyboard equivalent | Meaning |
|---|---|---|
| `JV` | `ОМ` | Jeeves / OpenClaw-style agent system |
| `BC` | `ИС` | BauClock |
| `GW` | `ПЦ` | Gewerbe/accounting/admin in Germany |
| `LV` | `ДМ` | Lavalamp / WLED / ESP32 |
| `HL` | `РД` | Homelab / Proxmox / Home Assistant |
| `ATV` | `ФЕМ` | Android TV / device experiments |
| `VAN` | `МФТ` | Van/camper modernization |

## Status/classification aliases

| Alias | Ukrainian-keyboard equivalent | Full classification |
|---|---|---|
| `CC` | `СС` | CONFIRMED_CANON |
| `NR` | `ТК` | NEEDS_REVIEW / LIKELY_NEEDS_REVIEW |
| `BL` | `ИД` | BACKLOG / IDEA_BACKLOG |
| `RJ` | `КО` | REJECTED / OUTDATED_REJECTED |
| `PR` | `ЗК` | PRIVATE_DO_NOT_STORE_RAW |
| `TMP` | `ЕЬЗ` | TEMPORARY_DO_NOT_CANONIZE |

## Ukrainian keyboard rule

If the user types an alias while the Ukrainian keyboard layout is active, treat the Ukrainian-keyboard equivalent exactly like the Latin alias.

Examples:

```text
ІЕ ОМ
```
Same as `ST JV`: load Jeeves startup context.

```text
ВС ИС
```
Same as `DC BC`: BauClock decision candidate.

```text
ЗТ ПЦ
```
Same as `PN GW`: private Gewerbe/admin note.

```text
КС ОМ
```
Same as `RC JV`: Jeeves recovery source.

```text
ЕС ДМ
```
Same as `TC LV`: Codex/executor task for Lavalamp.

```text
РЩ ИС
```
Same as `HO BC`: BauClock handoff.

```text
ФГ ALL
```
Same as `AU ALL`: global audit.

## Examples

```text
ST JV
```
Load Jeeves startup context from GitHub/Drive before answering.

```text
DC BC
```
This is a BauClock decision candidate. Check, classify, and save if durable.

```text
PN GW
```
This is private Gewerbe/admin context. Do not store raw in public GitHub.

```text
RC JV
```
Process the supplied Jeeves branch/memory dump as historical source.

```text
TC LV
```
Prepare an exact Codex/executor task for Lavalamp.

```text
HO BC
```
Update BauClock handoff after this work session.

```text
AU ALL
```
Audit overall memory structure and report issues briefly.

## Operating rule

When the user writes an alias, infer the full protocol without asking for expansion.

If multiple aliases appear together, combine them. Example:

```text
DC PN GW
```
Means: this is a private Gewerbe decision candidate; analyze/classify it, but do not store raw content in public GitHub.

The same applies to Ukrainian keyboard equivalents:

```text
ВС ЗТ ПЦ
```
Means the same as `DC PN GW`.

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
