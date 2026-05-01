# WORKING PROTOCOL

Status: CONFIRMED_CANON
Scope: compact command aliases for collaboration with ChatGPT and future Jeeves.
Last consolidated: 2026-05-01

## Purpose

Use short command aliases in chat to reduce typing and keep work structured.

These aliases apply across projects, unless a project-specific protocol overrides them.

## Core aliases

| Alias | Full meaning | Action |
|---|---|---|
| `ST` | STARTUP | Load external memory first: GitHub KB and, if needed, Google Drive private memory. Reconstruct context before answering. |
| `HO` | HANDOFF | Update short handoff for the next session: what changed, what was fixed, what remains open, next action. |
| `DC` | DECISION | Treat this as a candidate decision. Classify, check against canon, and save if durable. |
| `RC` | RECOVERY | Process a branch/export/dump as historical source. Extract durable knowledge, classify, and do not blindly canonize. |
| `TC` | TASK_FOR_CODEX | Produce a precise implementation task for Codex or another coding executor. |
| `PN` | PRIVATE_NOTE | Treat as private. Do not write raw content to public GitHub. Use Drive/private layer if storage is needed. |
| `AU` | AUDIT | Check memory/project state for noise, conflicts, outdated items, privacy risks, or missing handoff. |
| `KB` | KNOWLEDGE_BASE_UPDATE | Write cleaned durable knowledge to the correct KB layer if tools are available. |
| `GV` | GOOGLE_DRIVE_PRIVATE | Use Google Drive private memory layer for private working context. |
| `GH` | GITHUB_CANON | Use public-safe GitHub KB as canonical memory. |

## Project/context aliases

| Alias | Meaning |
|---|---|
| `JV` | Jeeves / OpenClaw-style agent system |
| `BC` | BauClock |
| `GW` | Gewerbe/accounting/admin in Germany |
| `LV` | Lavalamp / WLED / ESP32 |
| `HL` | Homelab / Proxmox / Home Assistant |
| `ATV` | Android TV / device experiments |
| `VAN` | Van/camper modernization |

## Status/classification aliases

| Alias | Full classification |
|---|---|
| `CC` | CONFIRMED_CANON |
| `NR` | NEEDS_REVIEW / LIKELY_NEEDS_REVIEW |
| `BL` | BACKLOG / IDEA_BACKLOG |
| `RJ` | REJECTED / OUTDATED_REJECTED |
| `PR` | PRIVATE_DO_NOT_STORE_RAW |
| `TMP` | TEMPORARY_DO_NOT_CANONIZE |

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
