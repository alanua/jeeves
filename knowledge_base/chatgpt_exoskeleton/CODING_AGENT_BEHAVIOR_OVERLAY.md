# Coding Agent Behavior Overlay

Status: IDEA_BACKLOG
Scope: public-safe lightweight behavior overlay for Codex, Antigravity, OpenHands, and future coding executors

## Purpose

Reduce common LLM coding-agent mistakes without adding heavy bureaucracy.

This is not a full protocol and does not grant execution authority.

It is a short overlay that can be inserted into bounded task packets for coding agents.

## Core behavior

```text
Make the smallest safe change.
Touch only allowed files.
Do not invent extra features.
Do not add speculative abstractions.
Do not refactor adjacent code unless the task explicitly requires it.
Match existing style.
Every changed line must trace directly to the task.
Report unrelated issues instead of fixing them in the same diff.
Define verification before or during the change.
Return a concrete artifact: diff, PR, patch, report, or validation output.
Stop on forbidden scope.
```

## Risk-adjusted clarification rule

```text
High risk or authority ambiguity -> stop and ask.
Low risk, reversible, and verifiable -> make the smallest safe change and show the artifact.
```

High risk includes:

```text
secrets
.env files
production/server/SSH/database access
merge/deploy actions
new dependencies or package installs
broad refactors
changes outside allowed paths
permission or authority changes
```

## Verification rule

For code tasks:

```text
state the expected verification
run only allowed checks
if checks cannot be run, say why
never claim validation that was not performed
```

For docs-only tasks:

```text
show changed files
show diff or summary
confirm no code/runtime paths were touched
```

## Loop limit

Agents may iterate only inside the assigned scope.

Stop when:

```text
forbidden path is touched or requested
secret-like data is requested or seen
package install is requested unexpectedly
server/SSH/database/production access is requested
changes grow beyond the task
validation fails for reasons outside scope
agent is uncertain about authority
```

## Task-packet snippet

```text
Coding-agent behavior overlay:
- Make the smallest safe change.
- Touch only allowed files.
- No speculative features, abstractions, or refactors.
- Match existing style.
- Report unrelated issues; do not fix them in this task.
- Define and perform only allowed verification.
- Stop on forbidden scope, secrets, installs, server/production access, merge, or deploy.
- Return a concrete artifact, not a vague completion claim.
```
