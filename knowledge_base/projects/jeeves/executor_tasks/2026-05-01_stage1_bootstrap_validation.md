# Runner Task — Validate Jeeves Stage 1 Bootstrap

Status: READY_FOR_RUNNER
Project: Jeeves
Alias: `КОД ДЖ`
Date: 2026-05-01

## Runner handoff

This file is for the runner.

The user does not manually copy this task into Codex.

Correct flow:

```text
runner reads this file
-> runner passes the task to Codex/executor
-> executor runs validation/fixes within allowed scope
-> runner returns result/logs/handoff
-> ChatGPT reviews and updates KB/handoff
```

## Goal

Validate the current Jeeves Stage-1 bootstrap exactly as it exists before adding Stage-2 features.

Do not redesign architecture in this task.
Do not add multi-agent complexity.
Do not implement long-term memory yet.

## Context

Stage-1 should include:
- FastAPI app
- health/readiness/metrics endpoints
- ask endpoint
- orchestrator
- policy layer
- task classifier
- DB-backed session/message/trace persistence
- executor/planner/research agents
- LLM router with provider abstraction
- Alembic migration
- tests using in-memory SQLite

## Required validation

1. Inspect repository structure.
2. Install dependencies in a clean environment.
3. Run full tests.
4. Run lint/format checks.
5. Start Docker Compose.
6. Apply Alembic migration.
7. Verify health/readiness/metrics endpoints.
8. Verify ask endpoint in deterministic mock-provider mode where possible.
9. Verify DB persistence for sessions, messages, and traces.
10. Verify default safety gates stay closed.

## Expected output

Create a concise validation report:

```text
Summary:
What works:
What fails:
Commands run:
Errors/logs:
Files changed:
Recommended next task:
```

## Allowed changes

Allowed:
- small fixes required to make documented Stage-1 run
- clear test fixes if code drift caused failures
- missing docs for exact run commands
- simple validation script if useful

Not allowed:
- no Stage-2 memory in this task
- no browser or computer-use
- no enabling dangerous tools by default
- no secrets
- no new architecture rewrite

## Safety/privacy boundaries

Do not commit secrets, tokens, private account data, local private paths, or private logs.

If logs contain sensitive data, redact before returning them.

## Final handoff

After validation, propose public-safe updates for:
- `knowledge_base/projects/jeeves/handoff.md`
- `knowledge_base/projects/jeeves/current_state.md`
- `knowledge_base/projects/jeeves/tasks.md`
