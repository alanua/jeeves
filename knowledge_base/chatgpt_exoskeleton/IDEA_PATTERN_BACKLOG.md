# Skeleton Idea and Pattern Backlog

Status: LIKELY_NEEDS_REVIEW
Scope: public-safe review queue for ChatGPT Exoskeleton / Skeleton ideas, external patterns, candidate skills, and future Jeeves design inputs
Created: 2026-05-13
Source issue: #181

## Purpose

This file tracks useful ideas and patterns before canonization or implementation.

It is a review queue, not accepted canon and not implementation approval.

Backlog entries may come from user ideas, external transcripts, audits, project failures, repeated manual work, or architecture discussions.

## Intake rule

All incoming architecture ideas, external patterns, tool patterns, candidate skills, and future-plan suggestions should pass through this backlog before they become canon, issues, or implementation tasks.

Default route:

```text
incoming idea
-> record or map to backlog entry
-> compare with current canon
-> classify
-> deep audit if useful or risky
-> rank priority
-> queue next action
-> promote only through a separate reviewed issue/PR
```

If an idea duplicates an existing backlog entry, update or reference the existing entry instead of creating a parallel one.

## Core rule

```text
idea -> compare with canon -> classify -> audit if needed -> prioritize -> queue -> implement only through a separate reviewed task
```

No item in this backlog grants authority to write code, change runner behavior, merge, deploy, access production, read secrets, or update canon automatically.

## Classification

```text
ACCEPT_FOR_DOCS
-> safe to propose as docs-only canon candidate through a reviewed PR

LIKELY_NEEDS_REVIEW
-> promising and probably aligned, but needs audit, constraints, or a narrow task before adoption

IDEA_BACKLOG
-> useful idea to preserve; not actionable yet

BLOCKED_OR_PREMATURE
-> do not implement now; revisit only after prerequisites or a smaller version proves useful

PARKED_ARCHIVE
-> not in the active queue, but intentionally preserved for periodic review because it may become useful later

OUTDATED_REJECTED
-> recorded for traceability but not pursued because it is unsafe, contradicted, superseded, or no longer relevant
```

Premature is not the same as rejected.

Only unsafe, contradictory, superseded, or clearly obsolete ideas should become `OUTDATED_REJECTED`.

Potentially useful ideas that are not currently actionable should move to `PARKED_ARCHIVE` instead of being deleted.

## Priority levels

```text
P0
-> current blocker or near-term control-plane safety/stability need

P1
-> important next capability after P0 blockers are handled

P2
-> useful later improvement or pilot candidate

P3
-> future Jeeves/runtime direction, broad architecture, or high-complexity idea

ARCHIVE
-> parked outside the active queue until a review trigger occurs
```

## Audit workflow

For each idea:

```text
1. Record the idea in this backlog.
2. Identify the problem it solves.
3. Identify benefit and risk.
4. Classify it.
5. Decide whether Gemini/canon audit is needed.
6. Create a separate issue only when the next action is clear.
7. Implement only after a reviewed task exists.
```

Gemini or any external model may provide evidence, but its output is not canon.

Human review remains required before canon promotion, runner behavior changes, implementation, merge, or deployment.

## Deep audit gate

Use deep audit when an idea would affect any of these:

```text
runner behavior
workflow gates
GitHub label semantics
PR creation/review/merge boundaries
Gemini or external-model routing
Telegram or other human-approval surfaces
memory/canon loading
secret/privacy handling
automation authority
future Jeeves runtime architecture
```

Deep audit must compare the idea against current canon, existing issues/PRs, existing files, known risks, and safer smaller alternatives.

A shallow safety-envelope accept is not enough for backlog promotion when the idea changes authority, routing, memory, or execution behavior.

## Idea archive / parking lot

Old, premature, or temporarily inactive ideas should not be deleted by default.

Use `PARKED_ARCHIVE` when an idea is potentially useful but should not remain in the active queue.

Each parked idea should record:

```text
why parked
what must change before reconsidering
review trigger
last reviewed date, if known
```

Suggested review triggers:

```text
after Worktree Protocol implementation
after runner route/mapping stabilization
after secrets-preflight is active
after PR reviewer meta-skill exists
after Telegram notification-only pilot
when a parked idea becomes relevant to a real blocker
periodic backlog review after major Skeleton milestones
```

Parking an idea does not approve it. It only preserves it for possible future reconsideration.

## Forbidden shortcuts

```text
Do not treat this backlog as canon.
Do not implement a backlog idea directly from this file.
Do not merge multiple unrelated ideas into one implementation task.
Do not bypass GitHub issue/PR audit trail.
Do not give Telegram, Gemini, Codex, OpenHands, or runner hidden authority.
Do not store secrets, .env values, tokens, private infrastructure data, or private user data here.
Do not rewrite existing canon from external trend evidence without audit and review.
```

## Current queue order

```text
P0. Review/finish #166 Worktree Protocol docs.
P0. Fix #157 unknown YELLOW task mapping.
P0. Review #162 runner status live collector.

P1. Create Secrets Preflight audit/design issue.
P1. Create skeleton_pr_reviewer audit/design issue.
P1. Create OpenHands executor adapter audit/pilot issue.
P1. Finish #163 Gemini audit for controlled agentic engineering principles.

P2. Telegram notification-only pilot via @Jeeveshelp_bot.
P2. Canon Graph Index v0 audit.
P2. Directory-specific override rules audit.

P3. LLM Router / provider fallback.
P3. Full graph memory / Infinite Brain only after smaller index proves useful.
```

## Backlog entries

| ID | Idea / Pattern | Classification | Priority | Main benefit | Main risk | Audit status | Next action | Links |
|---|---|---|---|---|---|---|---|---|
| IPB-001 | Git Worktree Protocol | ACCEPT_FOR_DOCS | P0 | Enables parallel agent work while keeping the main control checkout clean. | Worktree isolation can be mistaken for runtime isolation. | Docs PR open. | Review #166; merge only after human review and optional validation. | #165, #166 |
| IPB-002 | Unknown YELLOW task mapping fix | LIKELY_NEEDS_REVIEW | P0 | Prevents live runner tasks from staying falsely claimed/running when no route exists. | Incorrect generic fallback could expand runner authority. | Existing issue. | Fix fail-closed behavior before adding broader runner routes. | #157 |
| IPB-003 | Runner status / stale task diagnostics | LIKELY_NEEDS_REVIEW | P0 | Makes stuck/running/failed runner tasks visible without guessing. | Live diagnostics can leak secrets or mutate state if not bounded. | PR open. | Review #162 and preserve read-only boundaries. | #161, #162 |
| IPB-004 | Secrets preflight | LIKELY_NEEDS_REVIEW | P1 | Prevents `.env`, tokens, keys, credentials, private URLs, and secret-like data from entering diffs or outputs. | Over-broad detection can create false positives; under-broad detection can leak secrets. | Needs audit/design issue. | Create a narrow audit/design issue before implementation. | #89 |
| IPB-005 | skeleton_pr_reviewer meta-skill | LIKELY_NEEDS_REVIEW | P1 | Adds a safety review report over PR diffs before human review. | Automated reviewer may be mistaken for final approval authority. | Needs audit/design issue. | Define report-only scope; no approve, merge, or final authority. | pr-review-gate related |
| IPB-006 | Controlled agentic engineering principles | LIKELY_NEEDS_REVIEW | P1 | Frames Skeleton as controlled agentic engineering, not vibe coding. | External trend evidence may be over-canonized or overgeneralized. | Audit issue open. | Finish #163 and promote only concise reviewed principles if accepted. | #163 |
| IPB-007 | Telegram notification-only gateway via @Jeeveshelp_bot | IDEA_BACKLOG | P2 | Gives Oleksii faster visibility into PRs, audits, stale tasks, and approval requests. | Telegram could bypass GitHub audit trail if granted authority too early. | Needs future audit. | Start only as notification/read-only mirror over GitHub state. | future issue |
| IPB-008 | Canon Graph Index v0 | IDEA_BACKLOG | P2 | Reduces context noise by mapping intents to required canon sections. | Graph/index errors may hide mandatory safety rules. | Needs concept audit. | Audit a read-only index over existing Markdown canon; do not replace canon. | future issue |
| IPB-009 | Directory-specific overrides | IDEA_BACKLOG | P2 | Allows local conventions for docs, tests, mocks, or project folders. | Local overrides can create canon drift or conflict with global safety rules. | Needs audit. | Define priority order: global canon > project profile > local override > task packet. | future issue |
| IPB-010 | LLM Router / provider fallback | IDEA_BACKLOG | P3 | Reduces dependency on one model/provider and may handle quota/rate-limit failures. | Adds complexity, inconsistent behavior, cost risk, and authority confusion. | Future Jeeves/runtime audit needed. | Postpone until control plane, secrets, PR review, and runner routes are stable. | future issue |
| IPB-011 | Full Infinite Brain / graph-memory rewrite | BLOCKED_OR_PREMATURE | P3 | Could eventually support richer machine-readable memory. | Full rewrite would fragment human-readable canon and increase drift. | Not approved. | Do not implement; first test smaller Canon Graph Index v0. Move to PARKED_ARCHIVE after v0 decision if still premature. | future issue |
| IPB-012 | OpenHands executor adapter | LIKELY_NEEDS_REVIEW | P1 | May accelerate controlled code-writing and test tasks as a bounded software-agent executor inside worktrees. | Could become a second control plane, receive excessive permissions, conflict with runner, or expose secrets if integrated too broadly. | Needs deep audit and tiny pilot issue. | Audit OpenHands only as a bounded executor: no secrets, no merge, no deploy, no production access, worktree-only, PR/diff output only. | future issue |

## Parking lot entries

| ID | Idea / Pattern | Why parked | Reconsider when | Review trigger | Last reviewed | Links |
|---|---|---|---|---|---|---|
| PARK-001 | Full autonomous multi-agent orchestrator | Too much authority and complexity before worktree, runner mapping, secrets, and PR review are stable. | Control plane is stable and worktree execution is implemented safely. | After Worktree Protocol implementation and skeleton_pr_reviewer audit. | 2026-05-13 | IPB-011 |
| PARK-002 | Telegram approval buttons with real actions | Notification-only mode must prove safe first; approval buttons can bypass GitHub trace if implemented too early. | Telegram v1 is only a GitHub-visible mirror and audit trail rules are proven. | After notification-only pilot. | 2026-05-13 | IPB-007 |
| PARK-003 | Full knowledge-base graph rewrite | Full rewrite risks fragmenting human-readable canon and increasing drift. | Canon Graph Index v0 proves useful and safe. | After Canon Graph Index v0 audit and pilot. | 2026-05-13 | IPB-008, IPB-011 |

## Automation level rule candidate

This rule is not canon yet, but should be evaluated in #163:

```text
Verifiability determines automation level.
If an action cannot be objectively checked, it stays audit/report-only.
```

Possible levels:

```text
report-only
-> model or tool can produce findings only

draft-only
-> model or tool can create a draft artifact for review

PR-only
-> executor can open a reviewable PR after validation

human-approved action
-> action occurs only after explicit human approval and GitHub-visible trace
```

## Promotion rule

An idea may be promoted out of this backlog only through a separate reviewed artifact:

```text
backlog entry
-> audit/design issue
-> docs-only canon PR if appropriate
-> implementation issue only after docs/protocol approval
-> tests/validation
-> human review
```

Do not combine backlog promotion, implementation, runner behavior changes, and merge/deploy in one task.
