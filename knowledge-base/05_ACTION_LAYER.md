# 05 — Action Layer

## Current state

The project has accepted a future action direction and added proposal-only
contracts, but the action layer is **not live**.

Current live truth:
- no real side effects
- no action runner
- no live proposal generation
- no approval flow exposed in runtime behavior
- no action execution result produced by runtime behavior
- no `/ask` or DB schema changes for action handling

## Why this layer exists

The project must eventually distinguish between:
- dry-run advisory executor output
- typed future action intent
- approval-gated action plans
- approved action execution
- post-action validation

This separation is required to avoid silent or ambiguous side effects.

## Canonical proposal-only action contracts already added

### Enums
- `ActionRisk`
  - `low`
  - `medium`
  - `high`
  - `critical`

- `ActionStatus`
  - `proposed`
  - `approved`
  - `rejected`
  - `completed`
  - `failed`

### Models
- `ActionProposal`
- `ActionApproval`
- `ActionResult`

These are typed data contracts only. They are not wired into `/ask`,
orchestration, persistence, policy authorization, or tool execution.

Current contract constraints:
- action contracts reject unknown fields
- proposal IDs and required proposal text fields must be non-empty strings
- proposals must remain in `proposed` status
- approvals normalize omitted status from the `approved` flag
- approval status must match the `approved` flag
- results normalize omitted status from the `success` flag
- result status must match the `success` flag

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
- claims of successful action without a real execution path and `ActionResult`
- API schema expansion before action semantics stabilize
- DB schema changes before the runtime action model is proven
