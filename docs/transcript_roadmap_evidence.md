# Transcript-Derived Roadmap Evidence for Skeleton Trust Layers

Status: LIKELY_NEEDS_REVIEW
Scope: evidence-backed roadmap notes derived from user-provided video transcript extraction.
Created: 2026-05-12
Source: Issue #168 and prior transcript extraction discussion.

This document records roadmap evidence only. It is not an automatic canon promotion and does not grant Skeleton new autonomy.

## Source material

The user provided or summarized transcript material covering:

- Auto Research / Karpathy-style experiment loops
- agentic development workflows
- skills / Markdown knowledge files
- CLI vs MCP tradeoffs
- multi-agent teams
- Git worktrees and parallel agent workflows
- self-improvement risks

The extracted ideas are useful for Skeleton design, but they must remain classified as roadmap evidence until reviewed and promoted through the normal PR/canon flow.

## Core lesson

The useful idea is not uncontrolled self-improvement.

The useful idea is a bounded loop:

```text
task/spec -> bounded action -> independent evaluation -> report/PR -> human decision
```

Skeleton should preserve this loop while maintaining existing authority boundaries:

- no autonomous merge
- no autonomous deploy
- no autonomous canon promotion
- no secrets exposure
- no arbitrary command execution
- no self-modification without review

## Auto-Research mapping

The transcript extraction describes a three-part Auto-Research model:

```text
program.md  -> goal / task / spec
train.py    -> editable work product
prepare.py  -> immutable evaluator / judge
```

Skeleton equivalent:

```text
GitHub Issue / task payload                 -> program
branch / changed files / generated report   -> train
tests / validate-state / canon-audit / gates -> prepare
```

Key rule:

```text
The agent must not modify its own evaluator within the same task.
```

This supports a future Evaluation / Judge Layer.

## Evaluation / Judge Layer evidence

Future Skeleton tasks should distinguish editable work from immutable evaluation.

Candidate objective gates:

- `tests_passed = true`
- `ruff_errors = 0`
- `black_ok = true`
- `validate_state_ok = true`
- `forbidden_files_touched = 0`
- `secrets_detected = 0`
- `ci_green = true`

These are suitable for technical evaluation.

For architecture, canon, safety, or UX decisions, scalar metrics are not enough. Those areas require:

- structured audit reports
- traceable evidence
- human review
- explicit canon promotion if needed

Rule:

```text
Technical gates -> scalar metrics.
Canon / architecture / safety -> structured audit + human decision.
```

## Skills Layer evidence

Markdown skills are useful as controlled context.

Possible future paths:

```text
knowledge_base/skills/github_pr_review.md
knowledge_base/skills/canon_audit.md
knowledge_base/skills/python_patch.md
knowledge_base/skills/security_review.md
knowledge_base/skills/construction_takeoff.md
```

Boundary:

```text
Skill = knowledge / context.
Skill != permission.
```

A skill file must not automatically grant runner authority, file-write rights, PR rights, merge rights, deploy rights, or canon-write rights.

## CLI-first evidence

The transcript extraction supports the existing Skeleton CLI-first direction.

Current Skeleton examples:

```text
python -m tools.skeleton_core.cli validate-state
python -m tools.skeleton_core.cli ai-ping
python -m tools.skeleton_core.cli canon-audit
python -m tools.skeleton_core.cli create-pr
```

CLI remains preferred before MCP because it is:

- easier to test
- easier to allowlist
- easier to log
- lower token overhead
- fewer moving parts
- suitable for the Hetzner runner

MCP may be reconsidered later after CLI layers stabilize.

## Sub-agent sequencing evidence

Potential roles:

- Planner
- Auditor
- Executor
- Reviewer
- QA
- later parallel agents

Do not jump directly to a multi-agent mesh.

Recommended sequence:

```text
1. one planner
2. one auditor
3. one executor
4. one reviewer
5. parallel agents later
```

Current approximate state:

- Auditor exists.
- Executor exists.
- Reviewer partially exists through audit routes.
- Planner is not yet implemented.

## Worktree Isolation Layer evidence

Parallel Git worktrees may be useful later for multi-task execution.

Required prerequisites:

- task isolation
- branch naming rules
- locked target files
- conflict detection
- one PR per task
- clean workspaces
- runner-state locks
- no shared dirty workspace

This should remain a future layer, not an immediate implementation target.

## Safe self-improvement boundary

Reject:

```text
agent modifies itself autonomously without human review
```

Accept only a bounded experiment loop:

```text
agent proposes experiment
human approves
agent runs bounded experiment
evaluator checks
agent creates report/PR
human decides merge
```

This preserves controlled self-improvement without granting unsafe autonomy.

## Proposed roadmap direction

The following roadmap is evidence-backed and proposed, not final autonomous policy:

```text
Sprint 12 — LLM Provider Health / Routing Layer
Sprint 13 — AI Planning Layer
Sprint 14 — Evaluation / Judge Layer
Sprint 15 — Skills Layer
Sprint 16 — Worktree Isolation Layer
```

### Sprint 12 — LLM Provider Health / Routing Layer

Reason:

- Gemini is available.
- OpenAI has shown quota-related failure (`429 insufficient_quota`).
- Skeleton needs explicit provider health state and fallback rules.

Expected boundary:

- read-only/audit/planning calls only
- no new execution powers
- no autonomous fallback that bypasses safety

### Sprint 13 — AI Planning Layer

Goal:

```text
Issue -> structured plan -> risks -> files -> commands -> human review
```

Boundary:

- planning only
- no execution
- no file writes unless separately approved

### Sprint 14 — Evaluation / Judge Layer

Goal:

Create an explicit evaluator model similar to `prepare.py`.

Boundary:

- evaluator rules must be immutable within the task they evaluate
- agent may not modify its own judge as part of the same work item

### Sprint 15 — Skills Layer

Goal:

Create allowlisted Markdown skills for specific task types.

Boundary:

- skills are context only
- skills do not grant permissions

### Sprint 16 — Worktree Isolation Layer

Goal:

Prepare for parallel agent work using Git worktrees.

Boundary:

- only after task isolation, branch rules, conflict detection, and locks are implemented

## Working principle

```text
First: see, read, audit, and plan.
Then: act in bounded ways.
Later: act in parallel.
Never: self-merge, self-deploy, self-promote canon, self-modify without review.
```

## Classification

- Auto-Research mapping: LIKELY_NEEDS_REVIEW
- Evaluation / Judge Layer: LIKELY_NEEDS_REVIEW
- Skills Layer: IDEA_BACKLOG -> LIKELY_NEEDS_REVIEW after design
- CLI-first principle: CONFIRMED_CANON-compatible evidence
- Worktree Isolation Layer: IDEA_BACKLOG
- Safe self-improvement boundary: CONFIRMED_CANON-compatible evidence
- Proposed Sprint 12-16 ordering: LIKELY_NEEDS_REVIEW

## Non-goals

This document does not:

- implement code
- change runner permissions
- create new execution rights
- approve autonomous self-improvement
- promote transcript ideas directly to canon
- replace the existing memory policy or working protocol
