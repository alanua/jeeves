# 04 — Coordination and Agents

## Current agent set

### Planner
Role:
- planning
- final answer shaping for coordinated hybrid flows
- final-output producer in current coordinated runtime

### Research
Role:
- research / information gathering step in hybrid coordination
- upstream input supplier for planner

### Executor
Current role:
- generic LLM worker
- dry-run advisory execution-readiness participant in execution-aware hybrid

Important limitation:
- executor is **not** a real action runtime
- executor text must not be interpreted as proof that an external action happened

## Current coordination semantics

### Plain hybrid
Live path:
- `research -> planner`

Semantics:
- both are coordinated worker steps
- planner remains final-output producer
- planner is the boundary-visible selected agent

### Execution-aware hybrid
Live path:
- `research -> planner -> executor`

Semantics:
- research is required
- planner is required and remains the final-output producer
- executor is optional, advisory, and dry-run only
- executor may enrich warnings, evidence, and validation
- executor does not replace planner as the answer source

## Coordination ownership

The coordinator is a deterministic runtime component, not an LLM persona.

Accepted ownership rules:
- orchestrator owns fallback policy
- orchestrator owns approval policy for future action work
- coordinator owns step sequencing and aggregation
- worker agents do not decide fallback semantics
- worker agents do not decide approval semantics

## Current failure and degradation rules

### Required-step failure
If required coordinated work fails or the coordinated aggregate is unusable, explicit fallback may occur.

### Optional-step failure
If the optional executor step fails after planner succeeded:
- the coordinated run remains valid
- the run becomes degraded
- the planner answer is preserved
- no Stage-1 fallback is triggered if planner output is still usable

## Aggregate truth rules

Top-level aggregate result must remain authoritative for:
- final answer
- warnings / errors exposed to boundary
- evidence and validation flattened to trace and API
- top-level success / degraded status

Child run details are retained in runtime structures, but boundary flattening continues to use only the aggregate truth.

## What should not be changed casually

Anyone continuing the project should avoid:
- making executor the visible final agent without a deliberate boundary decision
- letting planner-generated free-form choreography replace deterministic runtime sequencing
- adding parallel coordination in the current stage
- mixing optional-step degradation with required-step fallback semantics
