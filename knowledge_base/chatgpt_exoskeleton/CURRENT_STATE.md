# ChatGPT Exoskeleton Current State

Status: CONFIRMED_CANON
Scope: short public-safe handoff for the next ChatGPT branch working on СК / Skeleton
Last updated: 2026-05-07

## Active project

```text
СК / ChatGPT Exoskeleton
```

Current work is the ChatGPT-side external control/support layer, not Jeeves runtime/code.

## Current state

Skeleton Stage 1 is complete enough for active use.
Skeleton Stage 2+ is active as practical productivity growth.

Externalizer v1 now has usable local/offline commands for:

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
```

Project-state layer exists as the public-safe mechanism for applying Skeleton to BauClock and other projects without mixing project context with СК/Jeeves canon.

Current rule:

```text
Grow the Skeleton for maximum practical productivity, but only where it reduces repeated work or validation friction.
Do not add abstract policy or runtime behavior by default.
```

Mandatory activation rule:

```text
A ready Skeleton skill must be used when it is relevant to the next action.
If a ready skill is skipped, the next action is blocked until the gate is satisfied or a human explicitly overrides it.
Skeleton must not be a paper checklist; built skills must become active workflow gates.
```

Immediate enforcement rule for ChatGPT/GitHub API work:

```text
Before Python file updates:
1. fetch the current file
2. apply real local Black formatting to the outgoing content
3. update_file only with formatted content
4. verify PR/head SHA changed
5. verify CI for the new head

format-preflight is a check/report gate, not a formatter. Local Black formatting must happen before update_file.
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
```

Format-preflight result:

```text
Given a public-safe fixture or explicit check-only path input, Skeleton can now detect format_ready, needs_black_format, blocked_missing_black, or unknown_needs_review before CI/PR review.
The CLI is local/offline by default. Live mode is Black check-only, does not modify files, reads no .env, prints no secrets, and grants no merge/deploy authority.
Important limitation: it checks formatting; it does not apply formatting. ChatGPT-side GitHub edits must run real local Black before update_file.
```

Runner-env-check result:

```text
Given a public-safe fixture or explicit live preflight input, Skeleton can now detect whether a runner is ready for read-only validation work or blocked by missing Python, missing git, unwritable workdir, DNS/network failure, clone failure, missing pytest, or unsafe credential-like input.
Fixture mode is offline. Live network/clone checks require explicit --allow-network-check. The CLI runs no project tests by default, reads no .env, prints no secrets, and grants no merge/deploy authority.
```

Project-skeleton-profile result:

```text
Given a public-safe project profile JSON, Skeleton can now emit a deterministic development-flow packet and reviewable missing-capability signals.
Projects can adapt branch flow to available Skeleton capabilities, and Skeleton skill growth can adapt to recurring project needs without auto-creating code, PRs, issues, merge, deploy, or runtime changes.
The CLI remains local/offline and grants no merge/deploy authority.
```

Branch-recovery result:

```text
Given a public-safe interrupted branch export, Skeleton can now normalize completed, needs_fix, wait_for_ci_or_fetch_status, create_pr_if_branch_ready, or unknown_needs_review into a compact recovery packet.
The CLI remains local/offline and grants no merge/deploy authority.
```

Pr-review-gate result:

```text
Given a public-safe PR review export, Skeleton can now decide ready_for_chatgpt_review, blocked_disallowed_files, blocked_failed_ci, blocked_scope_mismatch, blocked_runtime_change, blocked_unsafe_text, or unknown_needs_review.
The CLI remains local/offline and grants no merge/deploy authority.
```

Runner-report-ingest result:

```text
Given public-safe runner report/comment text, Skeleton can now normalize green_report, blocked_report, failed_validation, needs_review, unknown_needs_review, and unsafe_or_policy_violation into structured status packets.
The CLI remains local/offline and grants no merge/deploy authority.
```

Queue-state result:

```text
Given a public-safe controller queue export, Skeleton can now classify items as runnable, blocked_by_dependency, completed_or_reported, needs_review, or unsafe_or_unknown, then select the next safe runnable issue.
The CLI remains local/offline and grants no merge/deploy authority.
```

Issue-dispatch result:

```text
Given a public-safe GitHub issue export, Skeleton can normalize risk, route, review flag, allowed files, commands, and dependencies, and optionally pass the packet through issue-runner-bridge.
The CLI remains local/offline and grants no merge/deploy authority.
```

Runner-command-pack result:

```text
Given a public-safe GREEN/YELLOW task packet, Skeleton can emit a compact КОД-style runner/Codex/Antigravity instruction.
Blocked, RED, unsafe, missing-field, merge/deploy, secrets, network, and live-mode packets do not get runnable commands.
```

Validation for #86/#87:

```text
Skeleton Core CI run 25460114727 -> success.
Tests, ruff, black --check, and validate-state passed.
```

## Active GitHub queue

Main planning issue:

```text
#40 [skeleton] Stage 2 practical exoskeleton growth
```

Active / highest priority:

```text
#92 workflow-gate — enforce that ready Skeleton skills are actually used before GitHub write/review/runner/queue actions
#88/#91 github-actions-runner-control — open PR, CI success on latest head, pending review/merge
#90 capability-request-broker — project blocker/manual step -> Skeleton skill request packet
#89 secrets-preflight — prevent secrets, .env, tokens, keys, and private URLs from entering diffs/outputs
```

Open practical Skeleton Core candidates:

```text
migration-preflight — require migration review when DB/model files change
test-scope-preflight — choose minimal relevant validation commands for a change
ci-log-diagnoser — summarize failed CI as cause/file/action
```

Recommended next core slice:

```text
workflow-gate
```

Reason:

```text
Existing skills are useful only if the workflow blocks when they are skipped.
The next priority is making Skeleton operational, not paper-only.
```

## Safety boundaries

```text
No Jeeves runtime/app changes unless Oleksii explicitly switches to ДЖ/runtime.
No BauClock runtime/app changes unless Oleksii explicitly switches to BauClock implementation work.
No private infrastructure details in public GitHub.
No external service calls unless explicitly authorized.
No deploy/server changes unless explicitly requested.
No secrets, tokens, passwords, API keys, .env values, bank data, private documents, or raw private content in public GitHub.
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
START_HERE_FOR_CHATGPT.md
MEMORY_POLICY.md
WORKING_PROTOCOL.md
CHATGPT_BRANCH_CONTINUITY_BOOT.md
assistant_diary.md
chatgpt_exoskeleton/START_HERE.md
chatgpt_exoskeleton/CURRENT_STATE.md
CHATGPT_EXOSKELETON.md
CHATGPT_EXOSKELETON_RUNBOOK.md
```

Then use Skeleton/Externalizer on the current real task without asking Oleksii to repeat context.
