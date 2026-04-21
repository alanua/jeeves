# 05 — Action Layer

## Current state

The project has accepted a future action direction and already added foundational contracts, but the action layer is **not live**.

Current live truth:
- no real side effects
- no action runner
- no live proposal generation
- no approval flow exposed in runtime behavior
- no `/ask` or DB schema changes for action handling

## Why this layer exists

The project must eventually distinguish between:
- dry-run advisory executor output
- typed future action intent
- approval-gated action plans
- approved action execution
- post-action validation

This separation is required to avoid silent or ambiguous side effects.

## Canonical action-layer foundation already added

### Enums
- `ApprovalState`
  - `not_required`
  - `required`
  - `approved`
  - `denied`
  - `expired`

- `ActionExecutionStatus`
  - `not_started`
  - `running`
  - `succeeded`
  - `failed`
  - `blocked`
  - `skipped`

### Models
- `ActionProposal`
- `ActionApproval`
- `ActionExecutionRecord`

### ExecutionResult extensions
Additive default-empty fields exist for:
- `proposed_actions`
- `action_approvals`
- `action_executions`

## Policy scaffolding already added

The policy engine now has future-facing scaffolding for:
- `assess_action_proposal(proposal)`
- `authorize_action_execution(proposal, approval=None)`

Accepted conservative defaults:
- side-effectful actions require approval by default
- no implicit authorization exists
- no live execution path is enabled by these methods yet

## Accepted future action architecture

The accepted long-term direction is:
- keep orchestration and approval ownership in the orchestrator/runtime layer
- keep agent coordination separate from real action execution
- use typed action contracts rather than burying approval or execution semantics in prompts
- eventually execute approved actions through a dedicated non-LLM action runner

## First accepted future slice

The smallest accepted future action slice is:
- **proposal-only generation** for execution-aware hybrid
- no real execution
- no boundary changes
- no DB changes

That future slice would allow the system to produce typed proposed action intent while keeping planner output and live behavior compatible.

## What must not be done prematurely

Do not prematurely introduce:
- direct executor-to-tool execution
- hidden approval logic in prompts
- claims of successful action without a real `ActionExecutionRecord`
- API schema expansion before action semantics stabilize
- DB schema changes before the runtime action model is proven
