# 12 — Deployment and Family Runtime Target

Last updated: 2026-04-24

## Accepted product direction

When the agent system is mature enough, it should be deployable to a remote server through clear commands and scripts.

The user wants Jeeves to have a simple install/deploy mechanism similar in spirit to OpenClaw: a straightforward way to prepare a server, deploy the runtime, configure environment variables, and start the agents without manually rebuilding the whole stack each time.

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
- create or register personal agents for users
- start and stop services predictably
- update the system from Git
- inspect logs and health checks
- back up important state
- recover or roll back if needed

## Expected deployment style

The preferred deployment style should be boring, repeatable, and scriptable.

The target is not a manual installation guide only. It should be a command/script-driven installation path.

Likely future shape:

```text
scripts/
  install_remote.sh
  setup_server.sh
  deploy_remote.sh
  update_remote.sh
  create_user_agent.sh
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

This is not one shared family agent, and there is no shared family context by default. The desired model is simple: each family member has their own agent.

Each family member's agent should have:
- separate user identity
- separate personal context
- separate runtime memory scope
- separate preferences
- separate permissions
- separate conversation/session history
- clear boundaries around user-specific information

The current accepted model does **not** require a shared family workspace. Shared resources may be reconsidered later only as an explicit feature, not as part of the baseline family runtime.

This introduces requirements beyond a single-user development agent:
- user identity
- per-user context boundaries
- user-scoped memory and handoff
- safe permissions
- auditability of actions
- no accidental cross-user memory leakage
- no silent side effects

## Family-agent model

Accepted conceptual model:

```text
Remote Jeeves deployment
  ├─ operator/admin account
  │   └─ personal/admin agent
  ├─ family member A
  │   └─ personal adaptive agent A
  └─ family member B
      └─ personal adaptive agent B
```

Important rules:
- each user gets their own agent
- personal agents do not read each other's memory by default
- there is no shared family memory/context by default
- action permissions may differ by user
- adaptation must not override privacy, policy, or permission boundaries

## Safety requirements for family deployment

Before family use, the system must have at least:
- authentication
- explicit user/session separation
- per-user memory/context isolation
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
- role/permission model
- audit log
- action approval gates
- safe fallback behavior

### Stage D3 — Action-capable personal agents
Purpose:
- real actions with safeguards for each user-owned agent

Minimum requirements:
- approved action contracts
- action runner isolation
- per-user action approval rules
- audit trail for executed actions
- rollback/recovery strategy where possible

## Relationship to current architecture

This deployment goal depends on existing and future subsystems:
- API/runtime foundation from Stage 1
- coordination from Stage 2
- dry-run executor from Stage 2.5
- future action proposal and approval layer
- future runtime memory / handoff subsystem
- future user-scoped memory boundaries
- future permission matrix
- future deployment scripts and ops documentation

## Current status

This is an accepted future product and ops goal.

It is not yet implemented.

Near-term development should continue to prioritize correctness and safety of runtime contracts before exposing Jeeves as a hosted multi-user assistant.
