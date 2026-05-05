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
14. #26 was refined into the first Externalizer v0 decision-gate task: EvidencePolicy, RED tripwire semantics, blocked_reason, and structured runner report shape.
15. #27 was aligned with #26: queue items preserve evidence_policy/blocked_reason and classify Gemini/NotebookLM/Antigravity/manual auditor references as EVIDENCE_ONLY unless converted into reviewed Skeleton implementation tasks.
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
```

For active Skeleton work, do not load Jeeves runtime docs unless Oleksii explicitly switches to Jeeves runtime work.

## Active GitHub queue

```text
#22 [agent-task] Audit ChatGPT Exoskeleton canon and queue separation
#23 [skeleton] Stage 1 working exoskeleton stabilization
#25 [agent-task-green] Skeleton runner contour audit
#26 [agent-task-yellow] Implement minimal Skeleton core CLI
#27 [agent-task-yellow] Implement Skeleton github_queue offline adapter
```

Use #23 as the main practical working thread for Skeleton Stage 1.
Use #22 as audit/check reference.
Use #25 as the runner-contour reference.
Use #26 as the first Externalizer v0 code task.
Use #27 after #26 for offline queue classification.

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

## Last validation

Manual boot-path self-test:

```text
Input scenario: прокинься + СК
Read: BOOTLOADER.md -> chatgpt_exoskeleton/START_HERE.md -> chatgpt_exoskeleton/CURRENT_STATE.md
Not read: jeeves_runtime/START_HERE.md, assistant_startup_prompt.md
Result: PASS
```

Follow-up wording audit:

```text
Found: stale compact startup text in assistant_startup_prompt.md
Fixed: assistant_startup_prompt.md now includes current global boot, Skeleton namespace/model/runbook, and separate Jeeves runtime namespace
Result: PASS after post-write verification
```

Plus command verification:

```text
WORKING_PROTOCOL.md now records `+` as accepted + permission for the next safe practical step within the active task.
Result: PASS after post-write verification
```

Response style verification:

```text
WORKING_PROTOCOL.md now records one-short-human-sentence progress reports as the default.
Result: PASS after post-write verification
```

Externalizer queue refinement:

```text
#26 now defines the first Skeleton decision gate.
#27 now classifies evidence-only and blocked queue items consistently with #26.
Result: ready to start #26 through the runner contour.
```

Conclusion:

```text
A future Skeleton branch can reconstruct the current СК state from namespace files without entering Jeeves runtime docs.
Jeeves runtime docs are aligned for explicit runtime work.
Fast `+` continuation and compact reporting are now part of the working protocol.
Externalizer v0 should start from #26, not from a new duplicate task.
```

## Next practical step

Recommended next step:

```text
Start #26 through the runner contour as the first Externalizer v0 code task.
```

Keep it narrow:

```text
no Jeeves runtime/app changes
no private infrastructure details in public GitHub
no external API calls
no Gemini/NotebookLM/Antigravity calls
no deploy or server changes
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
