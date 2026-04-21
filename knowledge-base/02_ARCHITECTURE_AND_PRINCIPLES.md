# 02 — Architecture and Principles

## Canonical architecture direction

Jeeves is being built around explicit runtime layers rather than hidden prompt behavior.

Main layers:
- API / ingress
- routing
- orchestration
- specialized agents
- policy / permissions
- memory / handoff continuity
- future knowledge-base subsystem
- future action-contract subsystem
- repo-local skills

## Core accepted principles

### 1. Contracts-first source of truth
Canonical models and enums are the source of truth for runtime behavior.

Implications:
- no parallel result families in the main runtime path
- additive changes are preferred over shadow contract trees
- tests must lock behavior at the contract and boundary level

### 2. Deterministic orchestration
Orchestration belongs in runtime code, not in implicit prompt choreography.

Implications:
- agents do not own fallback policy
- agents do not own approval policy
- step order and degradation rules must be explicit

### 3. Explicit boundary centralization
Internal runtime objects may be richer than external shapes, but flattening must be explicit and centralized.

Implications:
- API and trace shapes may remain flattened for compatibility
- boundary serializers must be the only main serialization path
- ad-hoc dict assembly in routes / persistence paths is architectural debt

### 4. Single top-level aggregate truth
The boundary layer flattens the top-level aggregate result only.

Implications:
- child run details remain internal unless intentionally exposed
- trace and API compatibility are preserved by flattening the aggregate truth
- nested coordination artifacts should not leak directly into user-facing schema by accident

### 5. Fallback and degradation discipline
Required-step failures and optional-step failures are not treated the same.

Implications:
- required-step failure may trigger explicit fallback
- optional-step failure may degrade in place if a valid final answer still exists
- no silent fallback

### 6. No silent side effects
The system must distinguish advisory reasoning from real-world action.

Implications:
- dry-run semantics must remain separate from real execution
- future side effects require typed action contracts and approval
- future execution must be runtime-owned, not prompt-implied

## Architecture preferences

The project prefers:
- local-first when practical
- cloud fallback when needed
- typed evidence and validation
- conservative rollout of risky capabilities
- repo-grounded engineering workflow
- explicit continuity artifacts

## What should not be reintroduced

Anyone continuing the project should avoid reintroducing:
- hidden dual semantics between old and new contract families
- route-only fake orchestration paths
- prompt-only permission logic
- boundary flattening scattered across multiple call sites
- uncontrolled action semantics hidden inside executor text
