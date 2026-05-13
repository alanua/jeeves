# ChatGPT Exoskeleton Current State

Status: CONFIRMED_CANON
Scope: short public-safe handoff for the next ChatGPT branch working on СК / Skeleton
Last updated: 2026-05-09

## Active project

```text
СК / ChatGPT Exoskeleton
```

Current work is the ChatGPT-side external control/support layer, not Jeeves runtime/code.

## Current state

Skeleton Stage 1 is complete enough for active use.
Skeleton Stage 2+ is active as practical productivity growth.

The most important recent correction is:

```text
Skeleton must not guess operational infrastructure facts.
After `прокинься СК`, use the exact wake source map in START_HERE.md.
For live runner behavior, public docs are not enough; verify live script evidence or private handoff.
```

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
semi_automatic_construction_takeoff_with_gemini
semi_automatic_construction_takeoff_gemini_task_template
gemini_auditor_node
gemini_auditor_adapter
```

Gemini Auditor Node status:

```text
Priority: HIGH
Status: LIKELY_NEEDS_REVIEW
Public GitHub: protocol + mock-first adapter only
Private/live route: only through Runner environment with GEMINI_API_KEY and GEMINI_API_LIVE_MODE=true
Live bridge: still needs verified Runner report from #101 or equivalent
```

Construction Takeoff / Aufmaß status:

```text
Priority: HIGH
Status: LIKELY_NEEDS_REVIEW
Public GitHub: generic skill docs/templates only
Gemini second-brain review pass: documented in main via #105
Semi-automatic takeoff + Gemini workflow: documented in main via #109
Private pilot: real objects/files/outputs stay in Drive/local runner only
```

Semi-automatic Construction Takeoff + Gemini status:

```text
Priority: HIGH
Status: LIKELY_NEEDS_REVIEW
Public GitHub: skill/protocol + runner task template merged via #109
Purpose: coordinate Oleksii + ChatGPT/Skeleton + Runner + Gemini for semi-automatic takeoff without pretending full autonomy
Activation: use when the user asks for semi-automatic Aufmaß / drawing analysis / room areas / wall areas / Gemini review
Real extraction: stopped in the prior chat and should continue only in a separate work branch/chat
Private source folder and object-specific source priority are recorded only in the private Drive pilot handoff
```

## Exact wake source map

`knowledge_base/chatgpt_exoskeleton/START_HERE.md` now contains an exact source map for `прокинься СК` / `СК`.

The wake flow is:

```text
read exact required files
-> read topic-specific files
-> read private Drive handoff if infrastructure is involved
-> verify live runner facts from live script output or private handoff
-> claim only verified facts
```

Core rule:

```text
verified source -> claim
no verified source -> unknown_needs_source
```

Do not say that a live runner will pick up a task unless the queue labels and actual route in the live runner script are verified.

## Live Hetzner yellow runner contract

Confirmed from Oleksii terminal output and private Drive handoff:

```text
[agent-task-yellow] alone is not enough for live pickup.
```

The live Hetzner yellow runner searches these repos:

```text
alanua/bauclock
alanua/jeeves
alanua/Knowledge-base
```

Required labels for pickup:

```text
agent:task
agent:queued
risk:yellow
runner:hetzner OR runner:any
```

The issue must also be open.

Verified route status:

```text
The live yellow runner is not a fully generic executor for every `[agent-task-yellow]` issue.
It uses hard-coded run_* route functions and a case "$REPO|$TITLE" dispatch table.
The only observed generic fallback is scoped to alanua/Knowledge-base with lane:docs.
There is no verified generic route for arbitrary alanua/jeeves Skeleton tasks.
```

Track this in:

```text
#104 Inventory and source-control live Hetzner runner scripts
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
#103 exact Skeleton wake source map -> merged, merge commit 7f92a657f9036f6b1c7f5c36ec9f771b1903d614
#105 Construction Takeoff Gemini second-brain review pass -> merged, merge commit 72872e1a1513886a1009fcd6beb83a1d294e8c89
#106 current state update after wake map and takeoff merges -> merged, merge commit df2a399da1e3ee590d0348fb8e16ceeaf8ff2206
#109 semi-automatic takeoff Gemini workflow -> merged, merge commit 743832965cb667ff26df96b78be400284c319ad9
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
Public-safe skill document and generic runner task template exist in main.
Defines source priority, public/private routing, table schemas, statuses, validation gates, DXF/DWG parser expectations, and runner handoff.
Now includes optional Gemini second-brain review pass: Gemini reviews consistency/anomalies only, not final quantities or geometry source of record.
Semi-automatic takeoff + Gemini workflow exists to coordinate human checkpoints, Runner extraction, Gemini review, stop/resume, and source-priority handling.
No private drawings, real project data, extracted quantities, Drive URLs, parser code, live API calls, or final billable quantity claims were added to public GitHub.
Remains LIKELY_NEEDS_REVIEW until one real private floor/object pilot is processed end-to-end and reviewed by Oleksii.
```

## Validation records

```text
#109 Skeleton Core CI run 25603296492 -> success.
#105 Skeleton Core CI run 25602313369 -> success.
#103 Skeleton Core CI run 25602241998 -> success.
#100 Skeleton Core CI run 25565705312 -> success.
#98 Skeleton Core CI run 25539774958 -> success.
#92/#96 Skeleton Core CI run 25526615544 -> success.
#90/#94 Skeleton Core CI run 25499030865 -> success.
#88/#91 Skeleton Core CI run 25478609111 -> success.
#86/#87 Skeleton Core CI run 25460114727 -> success.
```

## Active queue

```text
1. private construction-takeoff pilot — continue in a separate branch/chat using semi_automatic_construction_takeoff_with_gemini; real source folder and object-specific source priority are in private Drive handoff
2. #101 private Gemini live ping — blocked until Runner route/pickup is verified or a matching live route/manual Runner call is used
3. #104 live Hetzner runner script inventory/source-control — route contract now verified as hard-coded; next step is source-control/redacted runner-host scripts or add reviewed Skeleton route
4. #89 secrets-preflight — prevent secrets, .env, tokens, keys, and private URLs from entering diffs/outputs
5. #95 runner-status-check — runner heartbeat/status -> queue pacing so tasks do not advance while runner is still running/blocked/stale
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
Technical/infrastructure claims must be verified-or-unknown; no guessing.
```

`+` means:

```text
accepted + continue with the next safe practical step inside the current active task.
It allows bounded GitHub/KB maintenance inside that task.
High-risk or destructive actions still require an explicit named instruction from Oleksii.
```

## Short boot instruction for the next branch

When Oleksii says `прокинься СК`, load:

```text
BOOTLOADER.md
knowledge_base/START_HERE_FOR_CHATGPT.md
knowledge_base/MEMORY_POLICY.md
knowledge_base/WORKING_PROTOCOL.md
knowledge_base/CHATGPT_BRANCH_CONTINUITY_BOOT.md
knowledge_base/assistant_diary.md
knowledge_base/chatgpt_exoskeleton/START_HERE.md
knowledge_base/chatgpt_exoskeleton/CURRENT_STATE.md
knowledge_base/chatgpt_exoskeleton/CONTROLLED_GROWTH.md
knowledge_base/chatgpt_exoskeleton/SKELETON_RUNNER_TASK_TEMPLATE.md
knowledge_base/CHATGPT_EXOSKELETON.md
knowledge_base/CHATGPT_EXOSKELETON_RUNBOOK.md
```

Then load topic-specific files from the exact wake source map in `START_HERE.md`. If the topic involves Hetzner/Termux/live runner behavior, also read the private Drive handoff and require live runner script evidence when exact behavior matters.

For Construction Takeoff / Aufmaß, also load:

```text
knowledge_base/chatgpt_exoskeleton/skills/construction_takeoff_from_drawings.md
knowledge_base/chatgpt_exoskeleton/runner_tasks/construction_takeoff_runner_task_template.md
knowledge_base/chatgpt_exoskeleton/skills/semi_automatic_construction_takeoff_with_gemini.md
knowledge_base/chatgpt_exoskeleton/runner_tasks/semi_automatic_construction_takeoff_gemini_task_template.md
```

If the active takeoff topic is the private Consum Quartier pilot, also read the private Drive document:

```text
СК Private Construction Takeoff Gemini Pilot Handoff
```

## 2026-05-13 continuity checkpoint

```text
Chat memory is not a reliable source of truth.
Future branches must recover Skeleton state from GitHub, repo files, KB/runbooks, and explicit runner diagnostics.
Status labels are not truth by themselves; they require evidence.
```

Recent Skeleton runner/status milestones:

```text id="px2oxg"
runner-status-check core module completed
runner-status-check CLI completed
static module registry completed
bounded live runner status collector completed
```

Current runner state:

```text id="3yvq3d"
Python/Gemini audit runner remains active.
Old host-local shell execution loop has been disabled.
The old shell dispatcher failed newer Skeleton tasks with unknown YELLOW task mapping.
Do not rely on the old host-local shell mapping path for new Skeleton execution tasks.
Do not delete old host-local runner scripts yet; keep them as evidence until source-controlled reference copies are reviewed.
```

Current task state:

```text id="j0cuxv"
#175 — continuity/current-state guardrail: active, should update this file.
#178 — deep-diff evidence packet builder: valid, but old shell runner failed it with unknown YELLOW task mapping.
#179 — false-confidence/shallow-gates audit: valid, currently blocked by Gemini quota/transport, not semantic rejection.
#180 — blocked subtype semantics: valid, currently blocked by Gemini quota/transport, not semantic rejection.
```

Guardrail:

```text id="zvkp4j"
agent:running does not prove a task is actually running.
agent:blocked does not prove semantic rejection.
agent:audited may mean safety-envelope accepted, not deep substance validated.
For exact state, inspect issue comments, adapter_status, runner-status-check output, PR state, and repo state.
```

Next safe order:

```text id="qkehog"
1. Finish #175 as a controlled docs-only PR.
2. Continue #178 through a controlled path, not the old shell runner.
3. Return to #179/#180 after quota reset or by manual controlled PR.
4. Normalize dispatcher/source-controlled runner path only after evidence/reference work is reviewed.
```
