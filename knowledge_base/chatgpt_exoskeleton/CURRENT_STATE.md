# ChatGPT Exoskeleton Current State

Status: CONFIRMED_CANON
Scope: short public-safe handoff for the next ChatGPT branch working on СК / Skeleton
Last updated: 2026-05-08

## Active project

```text
СК / ChatGPT Exoskeleton
```

Current work is the ChatGPT-side external control/support layer, not Jeeves runtime/code.

## Current state

Skeleton Stage 1 is complete enough for active use.
Skeleton Stage 2+ is active as practical productivity growth.

## Active local/offline Externalizer commands

```text
decide
task-from-text
work-packet
validate-state
checkpoint
trace-packet
runner-report-from-trace
queue-summary
classify-queue
handoff-pack
pr-status
job-log-summary
issue-runner-bridge
task-lifecycle
runner-command-pack
issue-dispatch
queue-state
runner-report-ingest
pr-review-gate
branch-recovery
project-skeleton-profile
runner-env-check
format-preflight
github-actions-runner-control
capability-request-broker
workflow-gate
```

## Active practical Skeleton skills/templates

```text
construction_takeoff_from_drawings
construction_takeoff_runner_task_template
gemini_auditor_node
gemini_auditor_adapter
```

Gemini Auditor Node status:

```text
Priority: HIGH
Status: LIKELY_NEEDS_REVIEW
Public GitHub: protocol + mock-first adapter only
Private/live route: only through Runner environment with GEMINI_API_KEY and GEMINI_API_LIVE_MODE=true
```

Construction Takeoff / Aufmaß status:

```text
Priority: HIGH
Status: LIKELY_NEEDS_REVIEW
Public GitHub: generic skill docs/templates only
Private pilot: real objects/files/outputs stay in Drive/local runner only
```

## Mandatory activation rule

```text
A ready Skeleton skill must be used when it is relevant to the next action.
If a ready skill is skipped, the next action is blocked until the gate is satisfied or a human explicitly overrides it.
Skeleton must not be a paper checklist; built skills must become active workflow gates.
```

## GitHub/API enforcement rule

```text
Before Python file updates:
1. fetch the current file
2. apply real local Black formatting using repo pyproject config
3. update_file only with formatted content
4. verify PR/head SHA changed
5. verify CI for the new head

format-preflight is a check/report gate, not a formatter.
workflow-gate is mandatory before relevant GitHub write/review/runner/queue actions.
```

## Recently completed

```text
#63/#76 task-lifecycle wrapper -> merged, SHA 2938279952b072a81b0625b729fed6f3873153cc
#65 issue-runner-bridge negation-aware safety clauses -> merged, SHA 689b75e05df4e80a0be9fc21c6a06f06601a2885
#75/#76 runner-command-pack CLI -> merged, SHA 12c9b5e8daba570617cfc7c08e36819b7abe02bb
#62/#77 issue-dispatch CLI -> merged, SHA 80a1c984aa65ac46f1b16eba6b5eb41f64e48ce4
#71/#78 queue-state CLI -> merged, SHA a69d564845cc2121fa9718df42ebe7f3dfef85b1
#72/#79 runner-report-ingest CLI -> merged, SHA b7a0fb0b9f4a798e28046486c41380d13897cd9f
#74/#80 pr-review-gate CLI -> merged, SHA 88a1b7c98583e433846746a3c39fa2a856c4b4f4
#68/#81 branch-recovery CLI -> merged, SHA e558bc569031b8844b507bd040ea5a5c7802c09b
#82/#84 project-skeleton-profile CLI -> merged, SHA 03e5aa4f399b2a22b4d634bac16c125320ed69f8
#83/#85 runner-env-check CLI -> merged, SHA 02c69555b39427972df7d040bae91fc544e9abf5
#86/#87 format-preflight CLI -> merged, SHA a7b23564b9ddf4733912e7dbb81ab5ae386d3ab7
#88/#91 github-actions-runner-control CLI -> merged, SHA abc2bd9c0623a2ac46191cd5d724c970dd2c0939
#90/#94 capability-request-broker CLI -> merged, SHA 99d59a0e2951857584f9d7f53b4b84c93e1e8aac
#92/#96 workflow-gate CLI -> merged, SHA 52fb67a38e963b742b2fb83854fd87f343827577
construction-takeoff-from-drawings/#98 docs+template -> merged, SHA 0b71d67f97bcad41bbae7aeacba92d1edec4ffc0
#99 Gemini Auditor Node bridge protocol -> merged, SHA f2833a19ed658fc1e071ceb3a8a47fb1b2f174ab
#100 mock-first Gemini auditor adapter -> merged, SHA aca2e71c1543c50b8b1f44474c8d9a3a77500c69
```

## Key results

Workflow-gate:

```text
Blocks relevant actions when required ready skills were skipped or failed.
Covers Python update, PR review, runner dispatch, queue advance, and GitHub Actions report gates.
Prevents ready Skeleton skills from staying paper-only.
```

Gemini Auditor Node:

```text
Universal Runner-mediated Gemini bridge now exists.
ChatGPT does not connect to Gemini directly.
Gemini is stateless auditor/reviewer, not manager, executor, canon writer, merger, or deployer.
Adapter is mock-first and fail-closed.
Live mode is blocked unless GEMINI_API_LIVE_MODE=true and GEMINI_API_KEY or GOOGLE_API_KEY exists in the Runner environment.
Secrets must not be posted in chat, Drive docs, public GitHub, or hardcoded code.
```

Capability-request-broker:

```text
Converts public-safe project blocker/manual-step exports into Skeleton skill request packets and reviewable issue title/body.
```

Construction Takeoff / Aufmaß:

```text
Public-safe skill document and generic runner task template now exist in main.
Defines source priority, public/private routing, table schemas, statuses, validation gates, DXF/DWG parser expectations, and runner handoff.
No private drawings, real project data, extracted quantities, Drive URLs, parser code, live API calls, or final billable quantity claims were added to public GitHub.
Remains LIKELY_NEEDS_REVIEW until one real private floor/object pilot is processed end-to-end and reviewed by Oleksii.
```

## Validation records

```text
#100 Skeleton Core CI run 25565705312 -> success.
#98 Skeleton Core CI run 25539774958 -> success.
#92/#96 Skeleton Core CI run 25526615544 -> success.
#90/#94 Skeleton Core CI run 25499030865 -> success.
#88/#91 Skeleton Core CI run 25478609111 -> success.
#86/#87 Skeleton Core CI run 25460114727 -> success.
```

## Active queue

```text
1. private Gemini live ping — only from Runner/local environment, using public-safe packet and GEMINI_API_LIVE_MODE=true
2. private construction-takeoff pilot prep — use the public skill on a private Drive/local dataset, without public object data
3. #89 secrets-preflight — prevent secrets, .env, tokens, keys, and private URLs from entering diffs/outputs
4. #95 runner-status-check — runner heartbeat/status -> queue pacing so tasks do not advance while runner is still running/blocked/stale
```

## Safety boundaries

```text
No Jeeves runtime/app changes unless Oleksii explicitly switches to ДЖ/runtime.
No BauClock runtime/app changes unless Oleksii explicitly switches to BauClock implementation work.
No private infrastructure details in public GitHub.
No external service calls unless explicitly authorized.
No deploy/server changes unless explicitly requested.
No secrets, tokens, passwords, API keys, .env values, bank data, private documents, or raw private content in public GitHub.
No Gemini API key in chat, Google Drive files, public GitHub, committed .env files, or hardcoded code.
No real construction-object drawings, addresses, client data, extracted real quantities, or Drive URLs in public GitHub.
```

## Current operating rules

```text
Бюрократія на безпечному мінімумі.
Більше практичної роботи.
Не створювати окремий issue/doc для кожного дрібного кроку.
Користуватися короткими коментарями, чеклістами і прямими діями.
Нові policy docs — тільки за прямою командою.
Built Skeleton skills must be activated as gates, not just listed as capabilities.
```

`+` means:

```text
accepted + continue with the next safe practical step inside the current active task.
It allows bounded GitHub/KB maintenance inside that task.
High-risk or destructive actions still require an explicit named instruction from Oleksii.
```

## Short boot instruction for the next branch

When Oleksii says `прокинься` and the active project is `СК`, load:

```text
BOOTLOADER.md
knowledge_base/START_HERE_FOR_CHATGPT.md
knowledge_base/MEMORY_POLICY.md
knowledge_base/WORKING_PROTOCOL.md
knowledge_base/CHATGPT_BRANCH_CONTINUITY_BOOT.md
knowledge_base/assistant_diary.md
knowledge_base/chatgpt_exoskeleton/START_HERE.md
knowledge_base/chatgpt_exoskeleton/CURRENT_STATE.md
knowledge_base/CHATGPT_EXOSKELETON.md
knowledge_base/CHATGPT_EXOSKELETON_RUNBOOK.md
```

Then use Skeleton/Externalizer on the current real task without asking Oleksii to repeat context.
