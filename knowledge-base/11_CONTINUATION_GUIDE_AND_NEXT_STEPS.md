# 11 — Continuation Guide and Next Steps

Last updated: 2026-04-24

## Purpose

This file is the practical continuation guide for any future AI platform, developer, or agent asked to continue Jeeves.

If the user says “continue the project”, start here.

## Current state to preserve

Do not regress these accepted states:
- Stage 1 foundation is closed and HTTP-locked.
- Plain hybrid live coordination uses `research -> planner`.
- Execution-aware hybrid live coordination uses `research -> planner -> executor`.
- Executor is optional, dry-run only, advisory, and non-final.
- Planner remains the visible selected agent and final answer source for coordinated flows.
- Boundary/API/trace shapes are stable.
- Action contracts and policy scaffolding exist, but no live action execution exists.

## Stable tags and commits mentioned in project history

Known accepted tags:
- `stage1-closed`
- `stage1-http-locked`
- `stage2-dry-run-executor-stable`

Known accepted commits from recent project history include:
- `0591122` — Stage-1 foundation routing/provider canonicalization
- `fe81bd2` — canonical runtime execution flow
- `36c3dfe` — Stage-1 runtime boundary serialization hardening
- `6a455f7` — execution-aware hybrid provenance and trace hardening

A future contributor should verify current repo state rather than relying only on these notes.

## Current recommended next coding slice

The next safe implementation direction is:

**isolated proposal-only generation for execution-aware hybrid**

Expected behavior:
- execution-aware hybrid coordinator may produce canonical `ActionProposal` and `ActionApproval` artifacts in isolation
- no live `/ask` behavior change yet
- no real action execution
- no DB schema change
- no boundary/API shape change

This should be done before any real action runner.

## Suggested prompt for the next AI engineer

Use this as the opening prompt on any AI coding platform:

```text
You are continuing the Jeeves project. First read the repository, then read `knowledge-base/README.md` and the files it links.

Treat the GitHub knowledge base as project-continuation documentation, not runtime memory.

Preserve the current accepted state:
- Stage 1 is closed and HTTP-locked.
- Stage 2 hybrid coordination is live and stable.
- Execution-aware hybrid with dry-run executor is stable.
- Action contracts and policy scaffolding exist, but real action execution is not live.

Do not rewrite architecture from scratch.
Do not introduce real side effects.
Do not change `/ask` shape or DB schema unless explicitly asked.

First task:
1. inspect the repo state;
2. verify tests and tags if possible;
3. compare code against `knowledge-base/03_IMPLEMENTATION_STATE.md`;
4. report drift before making changes.
```

## Engineering workflow rule

Use small explicit passes:
1. design lock
2. narrow implementation
3. tests
4. report
5. commit
6. update GitHub KB if an important decision changed

Do not combine unrelated work.

## Definition of done for a pass

A coding pass is not accepted until it reports:
- changed files
- what changed
- what did not change
- test command and result
- remaining risks
- next safe pass

## What not to do next

Do not jump directly to:
- real action execution
- browser-use control
- full RAG/memory system
- DB migration for action ledgers
- API expansion for action state
- dynamic planner-generated choreography
- parallel multi-agent execution

## Recommended subsystem order

Current recommended order:
1. isolated proposal-only action generation
2. proposal-only live wiring after isolated semantics are stable
3. typed session handoff / wake-up context
4. project-scoped memory and session diary
5. operation permission matrix
6. later semantic retrieval
7. later browser-use/computer-use
8. later real approval-gated action runner

## Rule for important decisions

All important accepted decisions must be recorded in GitHub KB under `knowledge-base/`.

This is the project continuity insurance layer and must remain portable across AI platforms.
