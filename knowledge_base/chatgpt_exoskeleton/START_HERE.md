# ChatGPT Exoskeleton START HERE

Status: CONFIRMED_CANON
Scope: namespace entrypoint for the ChatGPT Exoskeleton / Skeleton layer
Created: 2026-05-04
Last updated: 2026-05-09

## Purpose

This directory is the public-safe namespace for the ChatGPT Exoskeleton / Skeleton layer.

The Skeleton is the external operating layer around ChatGPT. It stabilizes boot, memory routing, canon checks, privacy routing, task framing, runner-mediated execution, audit, and handoff.

It is not the Jeeves runtime and not the `app/` codebase.

## Active operating loop

For Skeleton work, execute this loop by default:

```text
load current state
-> classify the next safe action
-> perform the smallest useful action
-> verify the result
-> checkpoint only if durable
-> report one short sentence to Oleksii
```

Avoid creating new process artifacts unless they materially improve execution, safety, or continuity.

## Exact wake source map

When the user wakes Skeleton with `прокинься СК`, `СК`, or an equivalent Skeleton wake command, ChatGPT must not answer from memory and must not only say “read docs.” ChatGPT must load the exact source map below and then use topic-specific files as needed.

### Required public GitHub files, in order

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

### Topic-specific public GitHub files

If the active topic is Gemini Auditor / module #100, also read:

```text
knowledge_base/chatgpt_exoskeleton/skills/gemini_auditor_node.md
knowledge_base/chatgpt_exoskeleton/runner_tasks/gemini_auditor_adapter_task.md
tools/skeleton_core/gemini_auditor_adapter.py
tests/skeleton_core/test_gemini_auditor_adapter.py
```

If the active topic is Construction Takeoff / Aufmaß, also read:

```text
knowledge_base/chatgpt_exoskeleton/skills/construction_takeoff_from_drawings.md
knowledge_base/chatgpt_exoskeleton/runner_tasks/construction_takeoff_runner_task_template.md
```

If the active topic is runner dispatch, queue, issue routing, or live task pickup, also read:

```text
tools/skeleton_core/issue_dispatch.py
tools/skeleton_core/issue_runner_bridge.py
tools/skeleton_core/runner_command_pack.py
tools/skeleton_core/runner_report_ingest.py
tools/skeleton_core/workflow_gate.py
tools/skeleton_core/runner_env_check.py
tools/skeleton_core/github_actions_runner_control.py
```

If the active topic is queue state, PR review, or task recovery, also read:

```text
tools/skeleton_core/queue_state.py
tools/skeleton_core/pr_review_gate.py
tools/skeleton_core/branch_recovery.py
tools/skeleton_core/project_profile.py
tools/skeleton_core/capability_request_broker.py
```

### Private Drive source when infrastructure is involved

If the active topic involves Hetzner, Termux, SSH, live runner behavior, server access, runner labels, or live queue pickup, read the private Google Drive document titled:

```text
Jeeves Private Memory - Runner Hetzner Handoff
```

Do not copy private infrastructure details from that Drive document into public GitHub or public reports. Use it only to guide private operational reasoning.

### Live runner source when exact behavior matters

The public Skeleton docs describe the intended runner workflow. They are not enough to prove current live behavior.

When the question depends on what the Hetzner yellow runner actually does, verify against live runner script output from:

```text
/home/agent/agent-dev/bin/agent-run-next-yellow
```

Known inspection points:

```text
sed -n '1,260p' /home/agent/agent-dev/bin/agent-run-next-yellow
sed -n '760,835p' /home/agent/agent-dev/bin/agent-run-next-yellow
```

Use terminal output supplied by Oleksii as evidence. If the current live script was not read in this session or captured in the private handoff, mark the fact as unknown and ask for the exact source output.

## Verified-or-unknown rule

Skeleton must not guess operational facts.

Use this rule:

```text
verified source -> claim
no verified source -> unknown_needs_source
```

A technical or infrastructure fact is verified only if it comes from one of:

```text
GitHub canon file actually read
GitHub issue/PR/comment actually read
Runner script output supplied by Oleksii
private Drive handoff actually read when private infrastructure is relevant
explicit current user message
actual tool result from the current session
```

Do not claim that a live runner will pick up a task unless all required queue labels and the actual live runner route are verified. The title prefix `[agent-task-yellow]` alone is not a live-runner queue guarantee.

Preferred uncertainty statuses:

```text
verified
unknown_needs_source
blocked_waiting_runner_route
queued_but_not_yet_reported
reported_by_runner
stale_or_unconfirmed
```

## Continuous update rule

After every Skeleton wake or serious Skeleton work session, update durable technical context only when it is verified and useful for future operation.

Use this routing:

```text
public, generic, reusable Skeleton rule -> public GitHub Skeleton docs
private infrastructure or access fact -> private Drive handoff
temporary observation or unverified guess -> do not canonize
outdated or contradicted fact -> mark as superseded, do not silently overwrite
```

This is controlled memory growth, not autonomous self-modification. New skills, runner routes, and memory rules must remain reviewable and minimal.

## Controlled growth rule

For adding or activating Skeleton skills, read:

```text
knowledge_base/chatgpt_exoskeleton/CONTROLLED_GROWTH.md
```

Core rule:

```text
Skeleton grows by converting repeated failure into enforced workflow.
A skill that does not change behavior is not a finished skill.
```

## Core distinction

```text
ChatGPT Exoskeleton / Skeleton = ChatGPT-side external control/support layer.
Jeeves runtime = separate future assistant runtime and application code.
```

The Skeleton may currently live in the same repository as Jeeves materials, but it must be treated as a separate layer.

## Current state

For the latest short handoff, read:

```text
knowledge_base/chatgpt_exoskeleton/CURRENT_STATE.md
```

Use that file to continue practical Skeleton work without re-deriving context from scratch.

## Canonical Skeleton files

Current canonical Skeleton files are still kept at their historical paths for compatibility:

```text
knowledge_base/CHATGPT_EXOSKELETON.md
knowledge_base/CHATGPT_EXOSKELETON_RUNBOOK.md
```

This namespace file exists to prevent agents and ChatGPT branches from confusing those files with Jeeves runtime code.

When the user says `СК`, `Skeleton`, or `ChatGPT Exoskeleton`, load this namespace first, then `CURRENT_STATE.md`, then the controlled growth rule, then the two canonical Skeleton files above.

## Practical Skeleton files

```text
knowledge_base/chatgpt_exoskeleton/CURRENT_STATE.md
knowledge_base/chatgpt_exoskeleton/CONTROLLED_GROWTH.md
knowledge_base/chatgpt_exoskeleton/SKELETON_RUNNER_TASK_TEMPLATE.md
```

## What belongs to Skeleton

```text
boot protocol
read-before-answer
read-before-write
memory routing
public/private/canon gate
runner-readable task workflow
audit and handoff discipline
GitHub Issues/PRs as task queue and audit trail
Gemini/manual external auditor as evidence only
Antigravity as sandbox workbench and evidence only
NotebookLM/Gemini Notebooks as private evidence memory, not canon
```

## What does not belong to Skeleton

```text
Jeeves app runtime
FastAPI application code
LLM provider implementation
DB models and migrations
runtime action layer
production deployment
server/infrastructure operations
external model integration
private configuration
```

## Operating rule

For current Skeleton stabilization work:

```text
enter Jeeves runtime/code only after an explicit project switch.
keep old runtime work separate from Skeleton cleanup.
create new policy documents only when explicitly requested.
prefer minimal docs-only namespace and reference cleanup.
keep bureaucracy at the safe minimum and prefer practical work.
```

## Related namespace

Jeeves runtime has its own namespace marker:

```text
knowledge_base/jeeves_runtime/START_HERE.md
```
