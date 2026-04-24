# 12 — Deployment and Family Runtime Target

Last updated: 2026-04-24

## Accepted product direction

When the agent system is mature enough, it should be deployable to a remote server through clear commands and scripts.

The user wants to run Jeeves not only as a development experiment, but eventually as a hosted assistant system for personal and family use.

## Target deployment outcome

The future deployment flow should allow the operator to:
- provision or prepare a remote server
- deploy the Jeeves backend/runtime
- configure providers, secrets, and environment variables safely
- start and stop services predictably
- update the system from Git
- inspect logs and health checks
- back up important state
- recover or roll back if needed

## Expected deployment style

The preferred deployment style should be boring, repeatable, and scriptable.

Likely future shape:

```text
scripts/
  deploy_remote.sh
  setup_server.sh
  update_remote.sh
  backup_state.sh
  restore_state.sh
  healthcheck.sh

deploy/
  docker-compose.yml
  .env.example
  nginx/
  systemd/
  README.md
```

The exact implementation can change later, but the deployment process must be documented and executable by commands, not only manual steps.

## Remote server assumptions

The target may be a VPS such as Hetzner or a similar Linux server.

The deployment should be designed so that it can later support:
- Docker Compose or equivalent containerized runtime
- reverse proxy / HTTPS
- persistent storage
- logs
- backups
- environment-based secret configuration

## Family runtime goal

The future system should support trusted family usage.

This introduces requirements beyond a single-user development agent:
- user identity
- role/access separation
- per-user context boundaries
- safe permissions
- auditability of actions
- no accidental cross-user memory leakage
- no silent side effects

## Safety requirements for family deployment

Before family use, the system must have at least:
- authentication
- explicit user/session separation
- operation permission matrix
- safe default denial for side-effectful operations
- approval-gated action execution
- logging and audit trail
- backup and recovery plan
- secrets kept outside Git

## What must not happen prematurely

Do not deploy a family-facing action-capable system before:
- runtime memory boundaries are clear
- action approvals are implemented
- side-effect execution is gated
- secrets and provider keys are protected
- basic monitoring/logging exists
- rollback path exists

## Deployment readiness stages

### Stage D0 — Developer deployment
Purpose:
- run Jeeves remotely for controlled personal testing

Minimum requirements:
- Docker or equivalent runtime
- `.env.example`
- start/stop/update commands
- health checks
- basic logs

### Stage D1 — Private personal runtime
Purpose:
- single-user stable remote assistant

Minimum requirements:
- authentication
- persistent state
- backups
- provider secret management
- basic monitoring

### Stage D2 — Family runtime
Purpose:
- trusted family use

Minimum requirements:
- multiple users
- user-scoped memory/context
- role/permission model
- audit log
- action approval gates
- safe fallback behavior

### Stage D3 — Action-capable family assistant
Purpose:
- real actions with safeguards

Minimum requirements:
- approved action contracts
- action runner isolation
- audit trail for executed actions
- rollback/recovery strategy where possible

## Relationship to current architecture

This deployment goal depends on existing and future subsystems:
- API/runtime foundation from Stage 1
- coordination from Stage 2
- dry-run executor from Stage 2.5
- future action proposal and approval layer
- future runtime memory / handoff subsystem
- future permission matrix
- future deployment scripts and ops documentation

## Current status

This is an accepted future product and ops goal.

It is not yet implemented.

Near-term development should continue to prioritize correctness and safety of runtime contracts before exposing Jeeves as a family-facing hosted assistant.
