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
Externalizer v0 minimal loop is merged and usable on `main`.
Future work should use the current loop on real tasks and add new commands only when actual friction appears.

Completed:

```text
1. Skeleton and Jeeves runtime namespace split.
2. Skeleton namespace entrypoint created.
3. Jeeves runtime namespace marker created.
4. Bootloader and startup files synced with the namespace split.
5. GitHub queue labeled so current Skeleton work is separated from Jeeves runtime/historical runner noise.
6. Minimal Skeleton runner-task template created.
7. Boot consistency synced after namespace split.
8. Manual `прокинься + СК` boot-path self-test passed without entering Jeeves runtime docs.
9. Read-only wording audit found stale compact startup text in assistant_startup_prompt.md.
10. assistant_startup_prompt.md compact boot memory was synced with current global boot and namespace split.
11. `+` command meaning was recorded in WORKING_PROTOCOL.md.
12. Response compression rule was recorded in WORKING_PROTOCOL.md.
13. Active Skeleton operating loop was added to chatgpt_exoskeleton/START_HERE.md.
14. #26 was implemented and merged via #29 as the first Externalizer v0 code slice: `tools/skeleton_core` CLI decision gate.
15. #27 was implemented and merged via #31 as the offline GitHub queue adapter.
16. Queue-summary usability CLI was merged via #32 and verified on the runner.
17. Oleksii confirmed: Externalizer v0 works and is accepted for active use.
18. #33 was implemented and merged via #34 as the trace-packet CLI.
19. #35 was implemented and merged via #36 as the task-from-text CLI.
20. #37 was implemented and merged via #38 as the runner-report-from-trace CLI.
21. #25 runner contour audit was completed as a read-only report comment and closed.
22. #24 queue hygiene inventory was completed as separate report issue #39 and closed.
23. #39 queue hygiene inventory report was closed after completion.
24. #22 ChatGPT Exoskeleton canon and queue separation audit was completed as a read-only report comment and closed.
25. #23 Skeleton Stage 1 working exoskeleton stabilization was completed and closed.
```

Core active files:

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

## Active GitHub queue

```text
No open Skeleton Stage 1 task remains.
Use the existing Skeleton/Externalizer loop on the next real task.
```

Closed/completed Skeleton items:

```text
#22 [agent-task] Audit ChatGPT Exoskeleton canon and queue separation -> completed as read-only report comment and closed
#23 [skeleton] Stage 1 working exoskeleton stabilization -> completed and closed
#24 [agent-task-green] Skeleton queue hygiene inventory -> completed via #39 and closed
#25 [agent-task-green] Skeleton runner contour audit -> completed as report comment and closed
#26 [agent-task-yellow] Implement minimal Skeleton core CLI -> merged via #29, merge SHA b5772bc20b102ff2847050ca083068c84e8a3f8d
#27 [agent-task-yellow] Implement Skeleton github_queue offline adapter -> merged via #31, merge SHA 3828a1e68864876d817861c9526a86e51aee884d
#32 Externalizer v0 queue-summary CLI -> merged, merge SHA d6b9eec3591738ef388ae51a0b0bd5f08d4c7163
#33 [agent-task-yellow] Add Externalizer v0 trace packet CLI -> merged via #34, merge SHA 2b96be29ad5e4b75155e8ecdac7ed371153f9189
#35 [agent-task-yellow] Add Externalizer v0 task-from-text CLI -> merged via #36, merge SHA 620a3d19958bd281ba28db2c0f13085f44e59b1b
#37 [agent-task-yellow] Add Externalizer v0 runner-report-from-trace CLI -> merged via #38, merge SHA a50248c16e7ba3e448542962f68b46a5e6e40197
#39 [agent-report] Skeleton queue hygiene inventory completed -> closed
```

Use #23, #22, #39, and #25 as references only.

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

## Externalizer v0 usage

Task intake / decision:

```bash
python -m tools.skeleton_core.cli task-from-text --text "Write docs note for Skeleton queue usage"
python -m tools.skeleton_core.cli --title "Write docs" --body "Add markdown note"
python -m tools.skeleton_core.cli decide --title "Write docs" --body "Add markdown note"
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
- normal docs task -> YELLOW / RUNNER_YELLOW
- code-like task -> ORANGE / RUNNER_ORANGE
- RED trigger task -> BLOCKED_RED with blocked_reason
- queue-summary counts Skeleton/runtime-noise/evidence-only/blocked items
- trace-packet emits public-safe JSON checkpoint fields
- task-from-text creates deterministic decision packets from free-form text without model calls
- runner-report-from-trace converts TracePacket JSON into the short public-safe runner report shape
```

## Last validation

```text
Decision gate: #26/#29 PASS.
Offline queue adapter: #27/#31 PASS.
Queue-summary CLI: #32 PASS and accepted for active use by Oleksii.
Trace-packet CLI: #33/#34 PASS.
Task-from-text CLI: #35/#36 PASS.
Runner-report-from-trace CLI: #37/#38 PASS; merge SHA a50248c16e7ba3e448542962f68b46a5e6e40197.
Queue/runner audits: #25 PASS; #24 PASS via #39; #22 PASS.
Stage 1: #23 PASS / closed.
```

Conclusion:

```text
A future Skeleton branch can reconstruct the current СК state from namespace files without entering Jeeves runtime docs.
Jeeves runtime docs are aligned for explicit runtime work.
Fast `+` continuation and compact reporting are now part of the working protocol.
Externalizer v0 has usable merged code on main: task-from-text, decision gate, queue-summary, trace-packet, and runner-report-from-trace.
Skeleton Stage 1 is complete and should now be used on real work instead of expanded abstractly.
```

## Next practical step

Recommended next step:

```text
Use the full minimal Externalizer v0 loop for the next real task:
task-from-text -> decision/route -> trace-packet -> runner-report-from-trace.
```

Possible next implementation step:

```text
Only add new Skeleton commands/tools after real workflow friction appears.
```

Keep it narrow:

```text
no Jeeves runtime/app changes unless Oleksii explicitly switches to ДЖ/runtime
no private infrastructure details in public GitHub
no external service calls unless explicitly authorized
no deploy/server changes unless explicitly requested
no issue/PR cleanup unless Oleksii explicitly asks
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

Then use Skeleton/Externalizer v0 on the current real task without asking Oleksii to repeat context.
