# BauClock — START HERE

Status: CONFIRMED_CANON
Project alias: `БК` / `BC`
Scope: public-safe project-specific startup file for BauClock.
Last consolidated: 2026-05-01

## Purpose

Read this file when work is about BauClock, construction time tracking, Telegram bot workflows, dashboards, company/site/worker model, payroll-support, payments support, DATEV/export boundaries, roles, onboarding, or UI/UX.

Global startup files:
- `knowledge_base/START_HERE_FOR_CHATGPT.md`
- `knowledge_base/MEMORY_POLICY.md`
- `knowledge_base/WORKING_PROTOCOL.md`

## Product identity

BauClock is a Telegram-first / dashboard-supported B2B SaaS concept for construction time tracking, site presence, worker/company roles, overtime/payment support, subcontractor coordination, and export/reporting support.

The product should no longer be named around SEK as the system identity. SEK may remain as first client/tenant/legacy example only.

## Working model

- User = operator / owner / final controller
- ChatGPT = architect / reviewer / task framer / memory organizer
- Runner = execution bridge that reads structured task files and passes them to Codex/Lovable/executors
- Codex = implementation executor
- Lovable = dashboard/UI/web executor when appropriate

## Executor workflow

For `КОД БК`:

```text
ChatGPT creates or updates runner-readable task file
-> runner reads task file
-> runner gives task to Codex/Lovable/executor
-> runner returns result/logs/handoff
-> ChatGPT reviews and updates KB/handoff
```

Do not tell the user to manually copy tasks into Codex/Lovable when runner workflow is available.

## Core model

Canonical business/data spine:

```text
company -> site -> person/worker -> time events -> summaries/payments/export
```

Important target direction:
- target identity model is `person + company_membership`
- implementation may transition gradually through current `worker` layer
- one physical site should move toward a master-site/master-QR model for multi-company work

## Role model

Main roles:
- platform_superadmin
- company_owner
- objektmanager
- accountant
- worker
- subcontractor / partner company context

Role access must be privacy-by-business-logic: each role sees only its legitimate minimum data.

## Legal/security direction

For Germany, do not rebuild the model blindly; perform legal-hardening:
- access control
- audit logging
- manual correction traceability
- ArbZG policy checks
- retention/privacy layer
- export boundaries for DATEV
- avoid turning v1 into full payroll engine too early

## UI direction

Mobile-first, clean, high-contrast interface.

Current style direction:
- warm sand background
- white rounded cards
- strong black text
- orange/red accents
- black round action buttons
- pill chips
- minimal shadows
- collapsible information blocks
- Material-style icons instead of letter badges

## Important project files

- `current_state.md`
- `decisions.md`
- `open_questions.md`
- `tasks.md`
- `handoff.md`
- optional `executor_tasks/` or equivalent for runner-readable task files

## Default startup command

```text
СТ БК
```

Equivalent:

```text
ST BC
```
