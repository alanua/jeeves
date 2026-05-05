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

Skeleton Stage 1 is now in practical stabilization.

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
14. #26 was refined into the first Externalizer v0 decision-gate task.
15. #27 was aligned with #26 for queue classification and evidence-only handling.
16. #26 was implemented and merged via #29 as the first Externalizer v0 code slice: `tools/skeleton_core` CLI decision gate.
17. #27 was implemented and merged via #31 as the offline GitHub queue adapter.
18. Queue-summary usability CLI was merged via #32 and verified on the runner.
19. Oleksii confirmed: Externalizer v0 works and is accepted for active use.
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
#22 [agent-task] Audit ChatGPT Exoskeleton canon and queue separation
#23 [skeleton] Stage 1 working exoskeleton stabilization
#25 [agent-task-green] Skeleton runner contour audit
```

Closed/completed:

```text
#26 [agent-task-yellow] Implement minimal Skeleton core CLI -> merged via #29, merge SHA b5772bc20b102ff2847050ca083068c84e8a3f8d
#27 [agent-task-yellow] Implement Skeleton github_queue offline adapter -> merged via #31, merge SHA 3828a1e68864876d817861c9526a86e51aee884d
#32 Externalizer v0 queue-summary CLI -> merged, merge SHA d6b9eec3591738ef388ae51a0b0bd5f08d4c7163
```

Use #23 as the main practical working thread for Skeleton Stage 1.
Use #22 as audit/check reference.
Use #25 as the runner-contour reference.

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

Decision gate:

```bash
python -m tools.skeleton_core.cli --title "Write docs" --body "Add markdown note"
python -m tools.skeleton_core.cli decide --title "Write docs" --body "Add markdown note"
```

Queue summary:

```bash
python -m tools.skeleton_core.cli queue-summary --input tests/fixtures/github_queue_sample.json
```

Current validated behavior:

```text
- normal docs task -> YELLOW / RUNNER_YELLOW
- RED trigger task -> BLOCKED_RED with blocked_reason
- queue-summary counts Skeleton/runtime-noise/evidence-only/blocked items
```

## Last validation

Externalizer v0 decision gate:

```text
#26 implemented and merged through #29.
Runner validation before merge: PASS.
```

Externalizer v0 offline queue adapter:

```text
#27 implemented and merged through #31.
Runner validation before merge: PASS.
```

Queue-summary CLI:

```text
#32 merged.
Runner validation before merge: PASS.
Oleksii confirmed: checked, works, use it.
Result: PASS / accepted for active use.
```

Conclusion:

```text
A future Skeleton branch can reconstruct the current СК state from namespace files without entering Jeeves runtime docs.
Jeeves runtime docs are aligned for explicit runtime work.
Fast `+` continuation and compact reporting are now part of the working protocol.
Externalizer v0 has usable merged code on main.
```

## Next practical step

Recommended next step:

```text
Use Externalizer v0 for the next Skeleton task instead of manually deciding route/queue state in chat.
```

Possible next implementation step:

```text
Add a small `trace` or `task-from-text` slice only after first active use shows what is missing.
```

Keep it narrow:

```text
no Jeeves runtime/app changes
no private infrastructure details in public GitHub
no external service calls
no deploy/server changes unless explicitly requested
short report in #23 only if durable
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

Then continue from #23 without asking Oleksii to repeat context.
