# Jeeves — Handoff

Status: ACTIVE_HANDOFF
Last updated: 2026-05-02

## Current working rule

For Jeeves context, start with:

```text
СТ ДЖ
```

Then load:
- `knowledge_base/START_HERE_FOR_CHATGPT.md`
- `knowledge_base/MEMORY_POLICY.md`
- `knowledge_base/WORKING_PROTOCOL.md`
- `knowledge_base/assistant_startup_prompt.md`
- `knowledge_base/projects/jeeves/START_HERE.md`
- this handoff

## Runner handoff rule

GitHub reports are the primary runner handoff channel.

Preferred flow:

```text
runner executes task
-> runner writes concise public-safe report/log summary into GitHub
-> ChatGPT reads repo/report directly
-> user does not paste long terminal output or screenshots unless something is stuck
```

Screenshots from Termux are fallback only.

Runner reports should go under:

```text
knowledge_base/projects/jeeves/runner_reports/
```

Runner task files should go under:

```text
knowledge_base/projects/jeeves/executor_tasks/
```

## Latest runner status report

Report file:

```text
knowledge_base/projects/jeeves/runner_reports/20260502-085821-runner-status.md
```

Summary:
- Runner server is reachable from Termux via `ssh jeeves`.
- Server: `hetzner-agent-runner-1`, Ubuntu 24.04.3 LTS, IPv4 `49.12.76.236`.
- Resource status is healthy: low load, low disk usage, low memory usage.
- Agent toolchain exists: `agentctl`, Codex CLI, GitHub CLI, Node, Python, bubblewrap.
- GitHub auth is active for account `alanua`.
- Jeeves validation passed: 56 tests passed and `JEEVES_VALIDATE_OK`.
- BauClock validation/audit ran and produced useful findings; visible output indicates request tests and full suite passed, but security/config hardening items remain.
- Two draft PRs are open in the knowledge-base repo.
- One Codex/session rollout warning appeared: `thread ... not found`; treat as workflow issue to investigate, not as Stage-1 Jeeves validation failure.

## Current status

Green:
- server reachable
- toolchain present
- GitHub auth active
- Jeeves validation passed

Yellow:
- runner appears script-based, not a persistent systemd service
- knowledge-base draft PRs remain open
- BauClock security/config hardening findings remain
- Codex/session rollout warning needs follow-up
- yellow runner did not yet produce a visible GitHub report for `2026-05-02_runner_health_cleanup.md`

Red:
- no confirmed blocking failure from the latest report

## Current decision

Continue according to the staged plan.

Do not jump directly to a development-agent team before Stage-1 validation is reviewed and runner workflow health is cleaned up.

## Active task

Current approved runner-readable task:

```text
knowledge_base/projects/jeeves/executor_tasks/2026-05-02_runner_health_cleanup.md
```

Goal:
- normalize runner status output into a concise green/yellow/red report
- investigate the Codex/session rollout warning
- document whether green/yellow runners are daemon, manual script, or queue-based
- ensure the result is committed as a GitHub report
- do not change architecture or add new agent-team features yet

## Planned next phase after cleanup

If runner workflow is clean, prepare Stage-2 runner task for:
- `agent_runtime/` artifact layout
- `contract_chain` schema
- task locking / race-condition prevention
- reviewer/monitor role skeleton
- no uncontrolled multi-agent team yet

## User action

No manual Codex task copying.

No long terminal output/screenshots by default.

User only triggers/allows runner workflow when needed, or provides a short screenshot if remote command execution is stuck.
