# BauClock Project State

Status: STARTER_PUBLIC_SAFE
Scope: public-safe per-project state for using the ChatGPT Skeleton / Externalizer with BauClock

## Project identity

```text
project_name: BauClock
project_type: product / time tracking and cash-settlement support system
runtime_scope: BauClock application, bot, dashboard, roles, audit trail, reporting, and related product logic
support_layer: ChatGPT Skeleton / Externalizer only
```

## Separation rule

```text
BauClock is a separate product/runtime.
Skeleton is an external development support layer used to structure tasks, PR review, CI diagnosis, checkpoints, and handoff.
This file must not be used as Jeeves runtime canon or Skeleton implementation canon.
```

## Current public-safe product concept

```text
BauClock is a Telegram-first time tracking and cash-settlement support system for small construction firms.
Core idea: simple, dispute-resistant work-time capture, role-based review, and clear settlement state.
```

## Current goal

```text
current_goal: prepare BauClock for Skeleton-assisted development without mixing context with СК/Jeeves
active_repo: not recorded here
active_branch_or_pr: not recorded here
```

## Current state

```text
current_state: project-state starter created
last_completed_step: Skeleton tools confirmed usable for BauClock as an external development layer
last_validation: pending PR/CI validation for project-state docs
```

## Next safe step

```text
next_safe_step: use Skeleton work-packet for the next explicit BauClock implementation request
blocked_by: none for planning; implementation requires explicit switch to BauClock work
```

## Active constraints

```text
forbidden_context_mix:
- do not modify BauClock runtime/app code from Skeleton state-maintenance tasks
- do not add private client data, server details, domains, credentials, tokens, banking/accounting data, or personal financial data
- do not treat BauClock project state as Jeeves runtime canon
- do not treat BauClock project state as ChatGPT Skeleton implementation state
- do not merge or deploy BauClock changes without explicit instruction
```

## Skeleton tools usable for BauClock

```text
work-packet: convert "КОД BauClock: ..." into a bounded task
task-from-text: create deterministic task packets from free-form requests
pr-status: review public-safe PR/CI status exports
job-log-summary: diagnose public-safe CI log excerpts
checkpoint: record completed public-safe steps and next action
handoff-pack: hand off Skeleton state between branches/chats
```

## Handoff notes

```text
When Oleksii switches to BauClock work, use this file as the public-safe project-state starter.
Keep BauClock runtime decisions in BauClock-specific work, not in СК/Jeeves canon.
```