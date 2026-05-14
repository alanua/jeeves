# Skeleton Runner Task Template

Status: CONFIRMED_CANON
Scope: minimal reusable task shape for ChatGPT Exoskeleton / Skeleton runner-mediated work
Created: 2026-05-04

## Purpose

Use this template when ChatGPT needs to create a bounded task for a runner/executor during Skeleton work.

This is not a Jeeves runtime task template.

## Minimal task shape

```markdown
# [skeleton-task] <short action title>

## Active project

СК / ChatGPT Exoskeleton

## Goal

<one concrete outcome>

## Scope

Allowed:
- <specific files / issues / labels / checks allowed>

Forbidden:
- Jeeves runtime/app code changes
- production/deploy/infrastructure changes
- external model API calls
- private configuration or secrets
- broad rewrites
- merge/close/delete unless Oleksii explicitly asked

## Sources to read first

- BOOTLOADER.md
- knowledge_base/START_HERE_FOR_CHATGPT.md
- knowledge_base/chatgpt_exoskeleton/START_HERE.md
- knowledge_base/CHATGPT_EXOSKELETON.md
- knowledge_base/CHATGPT_EXOSKELETON_RUNBOOK.md
- knowledge_base/chatgpt_exoskeleton/AGENT_WORKTREE_PROTOCOL.md, if the task is test-only, code-changing, parallel, or long-running
- <target file / issue if relevant>

## Worktree requirement

For test-only or code-changing tasks, use one issue = one branch = one worktree = one reviewable PR/diff.

Read-only audits do not require a worktree when they only read GitHub/files and post a report.

## Work to perform

1. <small step>
2. <small step>
3. <verification step>

## Required output

Report briefly:

```text
What changed:
What was verified:
What was not changed:
Remaining risk/noise:
Next safe step:
```

## Done condition

<clear observable completion condition>
```

## Operating notes

Prefer one small task that can be verified over a large ambiguous task.

Use GitHub Issues/PRs as task queue and audit trail, but keep bureaucracy at the safe minimum.

Do not create a separate issue for every tiny step unless it improves safety, auditability, or delegation.

For parallel agent work, follow `knowledge_base/chatgpt_exoskeleton/AGENT_WORKTREE_PROTOCOL.md`. A worktree isolates Git working directories and branch state only; it does not isolate runtime resources, secrets, databases, ports, processes, caches, or virtual environments.
