# ChatGPT Exoskeleton Current State

Status: CONFIRMED_CANON
Scope: short public-safe handoff for the next ChatGPT branch working on СК / Skeleton
Last updated: 2026-05-05

## Active project

```text
СК / ChatGPT Exoskeleton
```

Current work is the ChatGPT-side external control/support layer, not Jeeves runtime/code.

## Current state

Skeleton Stage 1 is complete enough for active use.
Skeleton Stage 2 is active as practical exoskeleton growth.
Externalizer v1 now includes local offline `work-packet`, `validate-state`, `checkpoint`, and `classify-queue` commands.

Current rule:

```text
Grow the Skeleton only where real workflow friction appears.
Do not add abstract policy or runtime behavior by default.
```

## Completed foundation

```text
1. Skeleton and Jeeves runtime namespace split.
2. Skeleton namespace entrypoint created.
3. Jeeves runtime namespace marker created.
4. Bootloader and startup files synced with the namespace split.
5. GitHub queue separated Skeleton work from Jeeves runtime/historical runner noise.
6. Minimal Skeleton runner-task template created.
7. Boot consistency synced after namespace split.
8. Manual `прокинься + СК` boot-path self-test passed without entering Jeeves runtime docs.
9. assistant_startup_prompt.md compact boot memory synced with current global boot and namespace split.
10. `+` command meaning recorded in WORKING_PROTOCOL.md.
11. Response compression rule recorded in WORKING_PROTOCOL.md.
12. Active Skeleton operating loop added to chatgpt_exoskeleton/START_HERE.md.
13. Runner contour audit completed and closed.
14. Queue hygiene inventory completed and closed.
15. Canon/queue separation audit completed and closed.
16. Skeleton Stage 1 stabilization thread completed and closed.
```

## Externalizer merged code

```text
#26/#29 decision gate CLI -> merged, SHA b5772bc20b102ff2847050ca083068c84e8a3f8d
#27/#31 offline GitHub queue adapter -> merged, SHA 3828a1e68864876d817861c9526a86e51aee884d
#32 queue-summary CLI -> merged, SHA d6b9eec3591738ef388ae51a0b0bd5f08d4c7163
#33/#34 trace-packet CLI -> merged, SHA 2b96be29ad5e4b75155e8ecdac7ed371153f9189
#35/#36 task-from-text CLI -> merged, SHA 620a3d19958bd281ba28db2c0f13085f44e59b1b
#37/#38 runner-report-from-trace CLI -> merged, SHA a50248c16e7ba3e448542962f68b46a5e6e40197
#41/#42 work-packet CLI -> merged, SHA cc31a1fcef4a470cd0247bbed86236f3d0cb0150
#43/#44 validate-state CLI -> merged, SHA d8a7442a26410966547d4837e4d3fabf752fc56f
#45/#46 checkpoint CLI -> merged, SHA df2a0c087ebc361d61eb36e488daed6703fe0d1a
#47/#48 classify-queue CLI -> merged, SHA a775775278268746493d3c31a6f3952816718bd1
```

## Active GitHub queue

```text
#40 [skeleton] Stage 2 practical exoskeleton growth
```

Closed/completed Skeleton references:

```text
#22 canon and queue separation audit
#23 Stage 1 working exoskeleton stabilization
#24 queue hygiene inventory
#25 runner contour audit
#39 queue hygiene inventory report
#41 work-packet CLI task
#42 work-packet CLI PR
#43 validate-state CLI task
#44 validate-state CLI PR
#45 checkpoint CLI task
#46 checkpoint CLI PR
#47 classify-queue CLI task
#48 classify-queue CLI PR
```

## Core active files

```text
BOOTLOADER.md
knowledge_base/START_HERE_FOR_CHATGPT.md
knowledge_base/MEMORY_POLICY.md
knowledge_base/WORKING_PROTOCOL.md
knowledge_base/CHATGPT_BRANCH_CONTINUITY_BOOT.md
knowledge_base/assistant_diary.md
knowledge_base/chatgpt_exoskeleton/START_HERE.md
knowledge_base/chatgpt_exoskeleton/CURRENT_STATE.md
knowledge_base/chatgpt_exoskeleton/SKELETON_RUNNER_TASK_TEMPLATE.md
knowledge_base/CHATGPT_EXOSKELETON.md
knowledge_base/CHATGPT_EXOSKELETON_RUNBOOK.md
knowledge_base/jeeves_runtime/START_HERE.md
knowledge_base/assistant_startup_prompt.md
tools/skeleton_core/
```

For active Skeleton work, do not load Jeeves runtime docs unless Oleksii explicitly switches to Jeeves runtime work.

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

Response style:

```text
For normal progress reports, answer with one short human sentence: what changed, what matters, or the next step.
Do not expose internal reasoning, long status blocks, or repeated safety explanations unless Oleksii asks.
```

Active operating loop:

```text
load current state
-> classify the next safe action
-> perform the smallest useful action
-> verify the result
-> checkpoint only if durable
-> report one short sentence to Oleksii
```

## Externalizer usage

State validation:

```bash
python -m tools.skeleton_core.cli validate-state
```

Task intake / decision:

```bash
python -m tools.skeleton_core.cli task-from-text --text "Write docs note for Skeleton queue usage"
python -m tools.skeleton_core.cli --title "Write docs" --body "Add markdown note"
python -m tools.skeleton_core.cli decide --title "Write docs" --body "Add markdown note"
```

Work packet:

```bash
python -m tools.skeleton_core.cli work-packet --text "Add a local state validator for Skeleton boot files"
```

Checkpoint bundle:

```bash
python -m tools.skeleton_core.cli checkpoint --task-id manual-001 --project skeleton --risk-level YELLOW --route-target RUNNER_YELLOW --result completed --next-safe-step review
```

Queue classification:

```bash
python -m tools.skeleton_core.cli classify-queue --input tests/fixtures/github_queue_sample.json
```

Queue summary:

```bash
python -m tools.skeleton_core.cli queue-summary --input tests/fixtures/github_queue_sample.json
```

Trace packet:

```bash
python -m tools.skeleton_core.cli trace-packet --task-id "manual-001" --project skeleton --risk-level YELLOW --route-target RUNNER_YELLOW --result completed --next-safe-step review
```

Runner report from trace:

```bash
python -m tools.skeleton_core.cli runner-report-from-trace --input tests/fixtures/trace_packet_sample.json
```

Current validated behavior:

```text
- validate-state checks required Skeleton boot/current-state files and anchors
- normal docs task -> YELLOW / RUNNER_YELLOW
- code-like task -> ORANGE / RUNNER_ORANGE
- RED trigger task -> BLOCKED_RED with blocked_reason
- task-from-text creates deterministic decision packets from free-form text without model calls
- work-packet converts free-form text into a public-safe task/issue packet
- checkpoint emits TracePacket JSON and public-safe runner report text in one output
- classify-queue emits per-item queue classification and summary counts
- queue-summary counts Skeleton/runtime-noise/evidence-only/blocked items
- trace-packet emits public-safe JSON checkpoint fields
- runner-report-from-trace converts TracePacket JSON into short public-safe runner report shape
```

## Last validation

```text
Decision gate: #26/#29 PASS.
Offline queue adapter: #27/#31 PASS.
Queue-summary CLI: #32 PASS and accepted for active use by Oleksii.
Trace-packet CLI: #33/#34 PASS.
Task-from-text CLI: #35/#36 PASS.
Runner-report-from-trace CLI: #37/#38 PASS.
Work-packet CLI: #41/#42 PASS; validation: 105 tests passed, ruff passed, black passed, git clean.
Validate-state CLI: #43/#44 PASS; validation: 109 tests passed, ruff passed, black passed, validate-state ok=true, git clean.
Checkpoint CLI: #45/#46 PASS; validation: 111 tests passed, ruff passed, black passed, validate-state ok=true, git clean.
Classify-queue CLI: #47/#48 PASS; validation: 114 tests passed, ruff passed, black passed, validate-state ok=true, git clean.
Queue/runner audits: #25 PASS; #24 PASS via #39; #22 PASS.
Stage 1: #23 PASS / closed.
```

Conclusion:

```text
A future Skeleton branch can reconstruct and validate the current СК state from namespace files without entering Jeeves runtime docs.
Jeeves runtime docs are aligned for explicit runtime work.
Fast `+` continuation and compact reporting are part of the working protocol.
Externalizer has usable merged code on main: validate-state, task-from-text, decision gate, work-packet, checkpoint, classify-queue, queue-summary, trace-packet, and runner-report-from-trace.
Skeleton Stage 2 is now active through #40 and should grow around real work only.
```

## Next practical step

Recommended next Stage 2 step:

```text
Use `validate-state`, `work-packet`, `checkpoint`, and `classify-queue` on the next real Skeleton task and observe friction before adding another command.
```

Candidate Stage 2 work should now be selected only from observed friction, not from abstract backlog.

Keep it narrow:

```text
no Jeeves runtime/app changes unless Oleksii explicitly switches to ДЖ/runtime
no private infrastructure details in public GitHub
no external service calls unless explicitly authorized
no deploy/server changes unless explicitly requested
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
