# 10 — Security and Release Hygiene

Last updated: 2026-04-24

## Security posture

Jeeves must treat security and permissions as architecture, not as an afterthought.

Accepted stance:
- permission models must be explicit and deterministic
- prompts must not be the only enforcement layer
- side effects must require policy and approval gates
- release artifacts must be checked before publishing

## Lessons from ecosystem incidents

Recent AI-agent ecosystem incidents reinforce these project rules:
- do not use leaked proprietary agent code or prompts as source material
- use public patterns, not copied leaked implementation
- assume malicious forks and poisoned packages may appear around popular agent leaks
- treat release artifact hygiene as part of product security

## Permission model direction

Future permission layers should distinguish operations such as:
- read
- search
- edit
- command execution
- action proposal
- action approval
- action execution

These permissions must be represented in runtime policy, not only in prompt text.

## Action safety rules

Future real-world actions must obey:
- no silent side effects
- no hidden approval in prompts
- no executor-to-tool direct execution without policy
- proposals are not execution
- executed actions require explicit typed execution records

## Release hygiene checklist direction

Future release checks should include:
- no secrets committed
- no API keys or tokens
- no sourcemaps or debug artifacts when not intended
- no private prompt assets accidentally included
- no unsafe default permissions
- dependency and package audit where practical

## Current safe interpretation

Current Jeeves state is safe because:
- executor is dry-run only
- action contracts exist but are not live
- policy scaffolding exists but does not authorize hidden execution
- boundary/API shapes are stable and conservative

## Future security work

Likely future security passes:
- operation permission matrix
- action approval flow hardening
- release artifact audit tool
- secrets scan integration
- dependency/package audit
- safe command execution policy
- browser-use/computer-use sandbox model
