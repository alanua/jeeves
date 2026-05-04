# ChatGPT Exoskeleton Current State

Status: CONFIRMED_CANON
Scope: short public-safe handoff for the next ChatGPT branch working on СК / Skeleton
Last updated: 2026-05-04

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
```

## Active GitHub queue

```text
#22 [agent-task] Audit ChatGPT Exoskeleton canon and queue separation
#23 [skeleton] Stage 1 working exoskeleton stabilization
```

Use #23 as the main practical working thread for Skeleton Stage 1.
Use #22 as audit/check reference.

## Current operating rule

```text
Бюрократія на безпечному мінімумі.
Більше практичної роботи.
Не створювати окремий issue/doc для кожного дрібного кроку.
Користуватися короткими коментарями, чеклістами і прямими діями.
Нові policy docs — тільки за прямою командою.
```

## Safety boundaries

Do not do these under Skeleton work unless Oleksii explicitly asks:

```text
Jeeves runtime/app code work
merge or close PRs/issues
deployments
external model API integration
secret/private configuration work
broad rewrites
new policy docs
```

## Last validation

Manual boot-path self-test:

```text
Input scenario: прокинься + СК
Read: BOOTLOADER.md -> chatgpt_exoskeleton/START_HERE.md -> chatgpt_exoskeleton/CURRENT_STATE.md
Not read: jeeves_runtime/START_HERE.md, assistant_startup_prompt.md
Result: PASS
```

Conclusion:

```text
A future Skeleton branch can reconstruct the current СК state from namespace files without entering Jeeves runtime docs.
```

## Next practical step

Recommended next step:

```text
Use the Skeleton runner-task template on a real bounded Skeleton maintenance task.
```

Good first candidate:

```text
Create one runner-readable Skeleton task to audit whether any remaining public KB files still use old wording that implies Skeleton work is Jeeves runtime work.
```

Keep it narrow:

```text
read-only audit first
no runtime/code work
no PR/merge/close
short report in #23
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
