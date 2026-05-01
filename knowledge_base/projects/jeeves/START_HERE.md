# Jeeves — START HERE

Status: CONFIRMED_CANON
Project alias: `ДЖ` / `JV`
Scope: project-specific startup file for Jeeves / OpenClaw-style agent system.
Last consolidated: 2026-05-01

## Purpose

Read this file when work is about Jeeves, OpenClaw-style agents, agent memory, orchestration, tools, skills, observability, controlled self-improvement, or the future personal assistant runtime.

Global startup files:
- `knowledge_base/START_HERE_FOR_CHATGPT.md`
- `knowledge_base/MEMORY_POLICY.md`
- `knowledge_base/WORKING_PROTOCOL.md`
- `knowledge_base/assistant_startup_prompt.md`

## Current identity

Jeeves is a local/server-first controlled personal/workspace orchestrator.

It is not a chaotic autonomous corporation. It should behave as a controlled lead/orchestrator that uses memory, tools, agents, policies, logs, and approvals.

Role model:
- User = operator / owner / final controller
- ChatGPT = architect / reviewer / memory organizer / task framer
- Codex/coding agents = implementation executors
- Jeeves = future orchestrator
- GitHub KB + Drive = temporary shared memory until Jeeves memory is mature

## Current implementation baseline

Current runnable baseline is Stage-1 vertical slice:
- FastAPI API
- orchestrator
- policy gate
- task classifier
- bounded session memory
- provider router
- DB persistence/traces

Strategic target architecture must not be forced too early.

## Long-term target direction

Progressive path:
1. single agent
2. reflection/reviewer
3. model router
4. tool layer
5. scheduler/heartbeat
6. observability/evals
7. one specialist agent
8. read-only subagents
9. controlled agent team

Core principles:
- wiki-first memory
- structured facts
- logs/evals
- least-privilege tools
- human approval for dangerous actions
- contract-first spawning for complex dev
- no autonomous self-rewrites

## Important project files

- `current_state.md`
- `decisions.md`
- `open_questions.md`
- `tasks.md`
- `handoff.md`

## Default startup command

```text
СТ ДЖ
```

Equivalent:

```text
ST JV
```
