# 12 — Deployment and Family Runtime Target

Last updated: 2026-04-24

## Accepted product direction

When the agent system is mature enough, it should be deployable to a remote server through clear commands and scripts.

The user wants to run Jeeves not only as a development experiment, but eventually as a hosted assistant system for personal and family use.

## Universal adaptive system model

Jeeves is intended to be a **universal adaptive agent system**.

This means the system is not hardcoded for one person, one family, one workflow, or one fixed assistant personality. The same core runtime should be able to adapt to each user through:
- user-scoped context
- user-scoped memory
- user preferences
- user roles and permissions
- user-specific skills and integrations
- user-specific safety limits
- user-specific communication style where appropriate

The universal system provides the common runtime, contracts, policy, deployment, and orchestration framework.

Each user gets a personalized agent instance/profile on top of that shared foundation.

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

Accepted model: **one personal adaptive agent per family member**.

This is not one shared family agent with one shared context. It is a multi-user family runtime with separate personal assistants under one controlled deployment.

Each family member's agent should have:
- separate user identity
- separate personal context
- separate runtime memory scope
- separate preferences
- separate permissions
- separate conversation/session history
- clear boundaries around user-specific information

A shared family space may exist later, but only as an explicit shared area with clear access rules.

This introduces requirements beyond a single-user development agent:
- user identity
- role/access separation
- per-user context boundaries
- user-scoped memory and handoff
- explicitly designed shared family context
- safe permissions
- auditability of actions
- no accidental cross-user memory leakage
- no silent side effects

## Family-agent model

Accepted conceptual model:

```text
Remote Jeeves deployment
  ├─ operator/admin account
  │   └─ admin/supervisor agent
  ├─ family member A
  │   └─ personal adaptive agent A
  ├─ family member B
  │   └─ personal adaptive agent B
  └─ optional shared family space
      └─ shared tasks / calendar / household knowledge / approved integrations
```

Important rules:
- personal agents do not read each other's memory by default
- shared family resources must be explicitly marked as shared
- action permissions may differ by user
- family-wide actions require clear ownership and approval rules
- adaptation must not override privacy, policy, or permission boundaries

## Safety requirements for family deployment

Before family use, the system must have at least:
- authentication
- explicit user/session separation
- per-user memory/context isolation
- clear shared-space rules
- operation permission matrix
- safe default denial for side-effectful operations
- approval-gated action execution
- logging and audit trail
- backup and recovery plan
- secrets kept outside Git

## What must not happen prematurely

Do not deploy a family-facing action-capable system before:
- runtime memory boundaries are clear
- per-user context boundaries are implemented
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
- trusted family use with one personal adaptive agent per family member

Minimum requirements:
- multiple users
- one personal adaptive agent per user
- user-scoped memory/context
- explicit shared family space if needed
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
- per-user and shared-action approval rules
- audit trail for executed actions
- rollback/recovery strategy where possible

## Relationship to current architecture

This deployment goal depends on existing and future subsystems:
- API/runtime foundation from Stage 1
- coordination from Stage 2
- dry-run executor from Stage 2.5
- future action proposal and approval layer
- future runtime memory / handoff subsystem
- future project/user-scoped memory boundaries
- future permission matrix
- future deployment scripts and ops documentation

## Current status

This is an accepted future product and ops goal.

It is not yet implemented.

Near-term development should continue to prioritize correctness and safety of runtime contracts before exposing Jeeves as a family-facing hosted assistant.
