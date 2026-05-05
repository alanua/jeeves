# Project State Template

Status: TEMPLATE
Scope: public-safe per-project state for using the ChatGPT Skeleton / Externalizer with a target project

## Project identity

```text
project_name:
project_type:
runtime_scope:
support_layer: ChatGPT Skeleton / Externalizer
```

## Separation rule

```text
The target project is separate from the Skeleton and from Jeeves runtime.
The Skeleton is only the external development support layer: task intake, PR/CI review, log diagnosis, handoff, and checkpoints.
Do not mix target project runtime decisions into Skeleton canon except as short pointers.
```

## Current goal

```text
current_goal:
active_repo:
active_branch_or_pr:
```

## Current state

```text
current_state:
last_completed_step:
last_validation:
```

## Next safe step

```text
next_safe_step:
blocked_by:
```

## Active constraints

```text
forbidden_context_mix:
- do not mix this project state with Jeeves runtime canon
- do not mix this project state with ChatGPT Skeleton implementation state
- do not add private infrastructure, secrets, credentials, client data, or financial/accounting details
- do not change runtime/app code unless the user explicitly switches to implementation work
```

## Skeleton tools usable for this project

```text
work-packet
task-from-text
pr-status
job-log-summary
checkpoint
handoff-pack
```

## Handoff notes

```text
handoff_notes:
```