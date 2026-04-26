# 11 - Continuation Guide and Next Steps

Last updated: 2026-04-26

## Purpose

This file is the practical continuation guide for any future AI platform, developer, or agent asked to continue Jeeves.

If the user says "continue the project", start here, then verify the code and tags before trusting older stage language.

## Current state to preserve

Verified current behavior to preserve:
- `/ask` uses deterministic single-agent routing.
- `complex` tasks select `planner`.
- `research` tasks select `research`.
- other task classes select `executor`.
- Planner and research agents call the LLM router directly with distinct system prompts.
- Session history, messages, and request traces are persisted.
- Boundary/API/trace shapes are covered by tests and should not change casually.
- Policy scaffolding exists for tools, providers, and self-modification.
- Shell tool execution is disabled by default and covered by structured-denial tests.
- No live action execution exists.

Do not currently assume these older documented states are implemented:
- plain hybrid `research -> planner` coordination
- execution-aware `research -> planner -> executor` coordination
- dry-run advisory executor inside a hybrid flow
- planner as final answer source after a multi-agent chain
- canonical `ActionProposal` / `ActionApproval` artifacts
- action approval handling or an action runner

## Tags and commits

Actual tag present in this checkout:
- `stage2-runtime-a27beb3` - concrete PlannerAgent and ResearchAgent routing

Older notes mention these accepted tags, but they are not present in this checkout:
- `stage1-closed`
- `stage1-http-locked`
- `stage2-dry-run-executor-stable`

Older notes also mention these commits, but they are not resolvable in this checkout:
- `0591122` - Stage-1 foundation routing/provider canonicalization
- `fe81bd2` - canonical runtime execution flow
- `36c3dfe` - Stage-1 runtime boundary serialization hardening
- `6a455f7` - execution-aware hybrid provenance and trace hardening

A future contributor should verify current repo state rather than relying only on these notes.

## Test status

Tests were inspected during the 2026-04-26 reconciliation. They cover:
- agent registry
- planner and research route selection
- `/ask` smoke behavior
- provider fallback
- authorization checks
- session history continuity
- policy decisions
- shell tool denial
- trace persistence for selected routes and shell denial

Tests were not executable in this environment because neither `pytest` nor `python3 -m pytest` had pytest installed. Use `pip install -e ".[dev]"` or the project environment, then run:

```bash
pytest -q
```

## Current recommended next coding slice

The safest next implementation direction is to pick one of these explicitly and test it in isolation before changing `/ask` semantics:

1. Proposal-only action artifacts:
   - add canonical proposal/approval data contracts
   - add focused unit tests
   - do not execute actions
   - do not change DB schema or `/ask` response shape yet

2. Multi-agent coordination:
   - add an isolated coordinator for `research -> planner`
   - define and test provenance/trace semantics
   - keep planner/research direct routes working
   - do not add executor or action behavior in the same pass

Do not start from the assumption that execution-aware hybrid is already live.

## Suggested prompt for the next AI engineer

Use this as the opening prompt on any AI coding platform:

```text
You are continuing the Jeeves project. First inspect the repository state, tests, and git tags, then read `knowledge-base/README.md` and the files it links.

Treat the GitHub knowledge base as project-continuation documentation, not runtime memory.

Preserve the current verified state:
- `/ask` uses deterministic single-agent routing.
- `complex` selects PlannerAgent.
- `research` selects ResearchAgent.
- other task types select ExecutorAgent.
- Tool, provider, and self-modification policy scaffolding exists.
- Shell tool execution is disabled by default.
- Real action execution is not live.

Do not assume these are implemented unless you find code/tests/tags proving them:
- hybrid `research -> planner` coordination
- execution-aware `research -> planner -> executor` coordination
- canonical ActionProposal or ActionApproval artifacts
- action approval handling or real side effects

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
5. commit only if explicitly asked
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
- execution-aware hybrid claims without first adding code and tests

## Recommended subsystem order

Current recommended order:
1. choose and design either proposal-only action artifacts or basic multi-agent coordination
2. implement the chosen slice behind focused tests
3. preserve current `/ask` shape unless explicitly changing it
4. add typed session handoff / wake-up context
5. add project-scoped memory and session diary
6. add operation permission matrix
7. later semantic retrieval
8. later browser-use/computer-use
9. later real approval-gated action runner

## Rule for important decisions

All important accepted decisions must be recorded in GitHub KB under `knowledge-base/`.

This is the project continuity layer and must remain portable across AI platforms.
