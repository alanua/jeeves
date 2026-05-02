# Runner Task — Runner Health Cleanup

Status: APPROVED_FOR_RUNNER
Project: Jeeves
Alias: `КОД ДЖ`
Date: 2026-05-02

## Runner handoff

This file is for the runner.

The user does not manually copy this task into Codex.

Correct flow:

```text
runner reads this file
-> runner passes the task to Codex/executor if implementation is needed
-> executor makes only allowed changes
-> runner returns result/logs/handoff
-> ChatGPT reviews and updates KB/handoff
```

## Goal

Clean up the runner health/status workflow after the successful Stage-1 validation report.

Do not build a development-agent team yet.
Do not add Stage-2 agent features yet.
Do not change application architecture.

## Context

Latest status:
- server is reachable
- toolchain is present
- GitHub auth is active
- Jeeves validation passed
- runner appears to be script-based rather than a persistent systemd service
- there are open draft PRs in the knowledge-base repo
- BauClock audit has security/config hardening findings
- a Codex/session rollout warning appeared in the latest status report

Current report file:

```text
knowledge_base/projects/jeeves/runner_reports/20260502-085821-runner-status.md
```

## Required work

1. Inspect current runner scripts under the runner workspace:
   - `bin/agentctl`
   - green runner scripts
   - yellow runner scripts
   - daemon/status scripts
   - queue/status scripts

2. Determine runner operating model:
   - green runner: manual script, loop, daemon, queue-based, or inactive
   - yellow runner: manual script, loop, daemon, queue-based, or inactive
   - whether any lock file is active or stale
   - where logs and run records are written

3. Normalize a concise status command/output.

Expected user-facing categories:

```text
GREEN:
YELLOW:
RED:
OPEN ITEMS:
NEXT SAFE ACTION:
```

4. Investigate the Codex/session rollout warning from the latest report.

Required outcome:
- identify whether it is harmless, transient, stale session metadata, or a real workflow issue
- document the cause if clear
- propose a safe fix if needed

5. Document current runner health in a public-safe report.

Suggested output path:

```text
knowledge_base/projects/jeeves/runner_reports/YYYYMMDD-HHMMSS-runner-health-cleanup.md
```

6. If small docs or status-script fixes are needed, they are allowed.

## Allowed changes

Allowed:
- add concise runner status/report docs
- add or improve a safe read-only status command
- clarify green/yellow runner operating model
- clarify logs/run directories
- document lock-file behavior
- document the Codex/session warning cause
- minor script fixes only if they are read-only/status/reporting related

Not allowed:
- no new agent-team implementation
- no Stage-2 memory implementation
- no browser/computer-use
- no enabling dangerous tools by default
- no production secrets
- no architecture rewrite
- no destructive operations
- no private IPs, tokens, keys, or raw secrets in public GitHub

## Expected output

Return a concise public-safe handoff:

```text
Summary:
GREEN:
YELLOW:
RED:
Open items:
Commands run:
Files changed:
Recommended next task:
```

## Final handoff

After completion, propose public-safe updates for:
- `knowledge_base/projects/jeeves/handoff.md`
- `knowledge_base/projects/jeeves/tasks.md`

If private operational details are needed, store only redacted summaries in public GitHub and keep sensitive details out of commits.
