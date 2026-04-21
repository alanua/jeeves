# 03 — Implementation State

## Stage overview

### Stage 1 — Foundation
Stage 1 is **closed**.

Accepted outcomes:
- canonical contracts and enums became the runtime source of truth
- canonical runtime execution flow was established
- runtime evidence and validation were populated
- runtime-to-boundary serialization was hardened
- `/ask` HTTP behavior was locked with tests

Known project tags from accepted work:
- `stage1-closed`
- `stage1-http-locked`

### Stage 2 — Hybrid coordination
Stage 2 is **live**.

Accepted outcomes:
- true hybrid coordination exists in the live runtime
- plain hybrid uses a deterministic `research -> planner` path
- planner remains the final user-facing answer producer
- coordinated provenance, validation, trace semantics, and tool attribution were hardened

### Stage 2.5 — Execution-aware hybrid with dry-run executor
This slice is **live and stable**.

Accepted outcomes:
- execution-aware hybrid uses `research -> planner -> executor`
- executor is optional, dry-run only, and advisory
- executor is not action-producing
- planner remains the final visible agent and final answer source
- optional executor failure degrades in place without erasing planner success
- execution-aware hybrid provenance and trace semantics are hardened

Known project tag from accepted work:
- `stage2-dry-run-executor-stable`

## Action-layer foundation
The action layer is **foundationally present but not live**.

Already added:
- canonical action contracts
- approval and execution status enums
- policy scaffolding for future proposal assessment and execution authorization

Not yet live:
- action proposal generation in the live runtime
- action approval handling in live flows
- action execution runner
- real side effects

## Current behavior summary

What live runtime can do now:
- route requests
- execute single-agent flows
- execute coordinated hybrid flows
- execute execution-aware hybrid flows with a dry-run advisory executor step
- produce canonical evidence / validation / aggregate results
- preserve stable `/ask` behavior

What live runtime cannot do yet:
- execute approved real-world actions
- expose action state through `/ask`
- persist rich per-action ledgers in DB schema
- act as a mature browser-use / computer-use runtime

## Current safe next engineering direction

The most recently accepted next-step posture is:
- implement **proposal-only generation in isolation** for execution-aware hybrid
- keep live behavior unchanged until proposal semantics are stable
- defer real action execution until the approval-gated action layer is deliberately wired

## Project stability summary

Current stability posture:
- Stage 1 is stable
- plain hybrid coordination is stable
- execution-aware dry-run executor coordination is stable
- boundary/API compatibility is stable
- action foundation exists but is not yet behaviorally active
