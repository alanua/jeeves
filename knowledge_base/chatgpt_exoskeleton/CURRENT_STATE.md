# ChatGPT Exoskeleton Current State

Status: CONFIRMED_CANON
Scope: short public-safe handoff for the next ChatGPT branch working on СК / Skeleton
Last updated: 2026-05-06

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
```

Project-state layer exists as the public-safe mechanism for applying Skeleton to BauClock and other projects without mixing project context with СК/Jeeves canon.

Current rule:

```text
Grow the Skeleton for maximum practical productivity, but only where it reduces repeated work or validation friction.
Do not add abstract policy or runtime behavior by default.
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
```

Project-skeleton-profile result:

```text
Given a public-safe project profile JSON, Skeleton can now emit a deterministic development-flow packet and reviewable missing-capability signals.
Projects can adapt branch flow to available Skeleton capabilities, and Skeleton skill growth can adapt to recurring project needs without auto-creating code, PRs, issues, merge, deploy, or runtime changes.
The BauClock fixture emits runner-env-check as a missing-capability signal/backlog candidate for #83.
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

Validation for #82/#84:

```text
Skeleton Core CI run 25455796004 -> success.
Tests, ruff, black --check, and validate-state passed.
```

## Active GitHub queue

Main planning issue:

```text
#40 [skeleton] Stage 2 practical exoskeleton growth
```

Open practical Skeleton Core candidates:

```text
#83 runner-env-check — preflight runner environment before assigning BauClock/project validation work
```

Recommended next core slice:

```text
#83 runner-env-check
```

Reason:

```text
BauClock #22 exposed a real execution-environment blocker: the runner/container could not resolve github.com. Project-skeleton-profile now emits runner-env-check as a BauClock missing-capability signal, so the next useful Skeleton growth is a runner environment preflight that blocks before assigning work to an unsuitable runner.
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
