# 03 - Implementation State

Last reconciled against code/tests/tags: 2026-04-26

## Verification snapshot

This file describes the current repository state, not only prior project intent.

Verified in this checkout:
- actual git tag present: `stage2-runtime-a27beb3`
- current HEAD: `deaf223` on branch `codex/docs-drift-audit-20260426-233221`
- tests exist for `/ask`, routing, policy, provider fallback, session history, tool denial, and trace persistence
- tests were inspected, but not executed here because `pytest` is not installed in the current environment

Not present in this checkout:
- tags `stage1-closed`, `stage1-http-locked`, or `stage2-dry-run-executor-stable`
- commits `0591122`, `fe81bd2`, `36c3dfe`, or `6a455f7`
- implemented hybrid choreography such as `research -> planner`
- implemented execution-aware choreography such as `research -> planner -> executor`
- canonical `ActionProposal` or `ActionApproval` runtime contracts
- action execution runner or approval workflow

## Current implemented runtime

The live `/ask` path is a deterministic single-agent routing flow:
- messages classified as `complex` select `planner`
- messages classified as `research` select `research`
- all other task classes select `executor`

Each selected agent calls the LLM router directly and returns one answer. The current orchestrator does not compose multiple agents into a single coordinated answer.

Verified current behavior:
- request pre-flight self-modification policy check
- task classification by keyword heuristics
- DB-backed session history hydration
- user and assistant message persistence
- trace persistence with selected agent/provider/model, latency, token counts, success/error state, and optional tool-call summary
- local-first provider routing with optional OpenRouter fallback, as covered by tests
- `/ask` response shape includes `request_id`, `answer`, selected agent/provider/model, fallback flag, `tool_calls`, latency, and warnings
- explicit `tool:shell ...` intent can produce a structured denial when tools are allowed but shell is disabled

## Agent state

Implemented agents:
- `ExecutorAgent`: general-purpose answer generation
- `PlannerAgent`: planning-framed answer generation for `complex` tasks
- `ResearchAgent`: research-framed answer generation for `research` tasks

The planner and research agents have distinct system prompts and warnings. They are not currently chained together.

## Stage documentation status

### Stage 1 - Foundation

Stage 1 is documented as a prior foundation target, and several foundation behaviors are present in code/tests:
- canonical `/ask` request/response schemas
- LLM router and provider fallback behavior
- policy checks for tools/providers/self-modification
- DB session/message/trace persistence
- `/ask` smoke and authorization tests

However, the historical Stage 1 tags named in older notes are not present in this checkout. Treat "Stage 1 closed" as a documented historical claim, not a tag-verified fact in this repository clone.

### Stage 2 - Agent routing

The tag `stage2-runtime-a27beb3` verifies a concrete routing slice: planner and research agents were added and routed directly by task type.

Accepted current scope:
- distinct planner and research agents exist
- planner route is tested through selected agent and warning checks
- research route is tested through selected agent and warning checks
- executor remains the fallback/general route

Not accepted as current implemented behavior:
- "true hybrid coordination"
- deterministic `research -> planner` chaining
- planner as final answer producer after research
- coordinated multi-agent provenance semantics

Those are documented targets or historical notes until code and tests reintroduce them.

### Stage 2.5 - Execution-aware dry-run executor

This slice is not present in the current code/tests/tags. Treat prior claims that execution-aware hybrid uses `research -> planner -> executor` as unverified target documentation.

Not currently implemented:
- optional dry-run executor step after planner
- executor advisory output inside a coordinated hybrid flow
- failure degradation from executor back to planner success
- hardened execution-aware provenance or trace semantics

## Action-layer foundation

The current repo has policy and disabled-tool scaffolding, but no canonical action layer.

Present:
- `PolicyEngine` gates tool access, provider access, and self-modification
- `ToolHandler` recognizes explicit shell intent in one narrow path
- `ShellScaffoldTool` always denies execution by default
- tests cover policy denial and shell tool denial

Not present:
- canonical action proposal contracts
- approval and execution status enums
- live action proposal generation
- action approval handling
- action execution runner
- real side effects
- rich per-action DB ledgers

## Current safe next engineering direction

Conservative next step:
- first decide whether to implement proposal-only action artifacts or multi-agent coordination
- add isolated contracts and tests before changing `/ask` behavior
- keep real action execution out of scope until approval semantics, persistence, and policy are explicit

Do not treat older hybrid or action-layer claims as accepted current runtime behavior unless new code/tests/tags are added.

## Project stability summary

Current verified stability posture:
- single-agent `/ask` routing is present
- planner/research/executor direct routing is present
- provider fallback and policy scaffolding are present
- session/message/trace persistence is present
- shell tool execution remains disabled by default

Current unverified or target-only posture:
- Stage 1 historical tags and commit references
- hybrid coordination
- execution-aware dry-run executor coordination
- canonical action proposal/approval layer
