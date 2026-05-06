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
```

Runner-command-pack result:

```text
Given a public-safe GREEN/YELLOW task packet, Skeleton can now emit a compact КОД-style runner/Codex/Antigravity instruction.
Blocked, RED, unsafe, missing-field, merge/deploy, secrets, network, and live-mode packets do not get runnable commands.
```

Validation for #75/#76:

```text
Skeleton Core CI run 25449037370 -> success.
Tests, ruff, black --check, and validate-state passed.
```

## Active GitHub queue

Main planning issue:

```text
#40 [skeleton] Stage 2 practical exoskeleton growth
```

Open practical Skeleton Core candidates:

```text
#62 issue-dispatch — normalize public-safe GitHub issue exports and optionally run issue-runner-bridge
#71 queue-state — determine next safe runnable item from a controller queue export
#72 runner-report-ingest — normalize public-safe runner reports into status packets
#74 pr-review-gate — decide whether a PR is ready for ChatGPT review or blocked
#68 branch-recovery — recover interrupted Skeleton branches from public-safe export
```

Recommended next core slice:

```text
#62 issue-dispatch
```

Reason:

```text
It reduces the remaining manual step between a raw public-safe GitHub issue export and the existing issue-runner-bridge / task-lifecycle / runner-command-pack chain.
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
