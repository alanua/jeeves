# Skeleton Development Lane Gate and Evidence Protocol

Status: CONFIRMED_CANON
Scope: active Development Lane gate for Codex, OpenHands, and other bounded coding work
Issue: #226
Last consolidated: 2026-05-16

## Purpose

The Development Lane exists so bounded executors can do real coding work without turning Skeleton into broad autonomy theater.

The lane is intentionally narrow:

```text
branch
-> bounded change
-> validation
-> draft PR
-> independent review
-> explicit Oleksii merge command
```

That boundary applies to docs-only work, test work, CLI wiring, and narrow production fixes.

## Ontology gate

```text
ChatGPT Exoskeleton = historical/current ChatGPT-facing prototype of Skeleton.
Unified Skeleton Core = target model-neutral external operating layer for LLM-assisted work.
ChatGPT = current host/interface for the prototype.
Codex = coding executor.
OpenHands = bounded executor role.
Gemini = auditor / second-brain role.
Jeeves = separate future independent assistant/product.
```

Critical rule:

```text
Jeeves is not a Skeleton adapter.
Jeeves is not runtime under Skeleton.
Skeleton is the precursor, proving ground, practical toolchain, and construction scaffold used to build Jeeves more safely.
```

## Core evidence rule

```text
Executor self-report is not evidence.
```

A claim like `done`, `fixed`, or `tests passed` is not enough by itself. Evidence must be collected outside the executor answer.

GitHub issues, pull requests, and comments are the public evidence trail for this lane.

## Lane trigger

Use this gate whenever a task asks Codex, OpenHands, or another bounded executor to change repository content.

This includes:

```text
docs-only PRs
test-only PRs
pure module plus tests
CLI wiring
narrow production fixes
```

If the work is broader than one reviewable PR, split it before execution.

## Standard task envelope

Every Development Lane task should define:

```text
Task ID:
Repository:
Branch name:
Goal:
Allowed files:
Forbidden actions:
Stop conditions:
Required validation:
Expected output:
```

Allowed files must be explicit. If the task needs more files than allowed, stop and report instead of expanding scope.

## Default executor boundaries

```text
No merge.
No deploy.
No secrets, private config, env, server, or runtime access.
No production data access.
No hidden expansion of scope.
No broad setup or refactor unless explicitly authorized.
```

For canon or instruction edits inside this lane, critique-before-action still applies: read the current rule first, identify overlap or contradiction, then patch minimally.

## Required evidence collection

Collect evidence after the executor stops and outside the executor answer.

Minimum evidence:

```text
working tree status
diff sanity check
diff summary
diff limited to allowed files
targeted validation relevant to the change
```

Typical commands:

```bash
git status --short
git diff --check
git diff --stat
git diff -- <allowed-files>
```

Typical validation:

```text
docs-only: git diff --check + git status --short
code/test changes: targeted tests + relevant lint/format checks + git evidence
```

Without that evidence, the lane is incomplete even if the edit itself looks correct.

## Review and merge boundary

The Development Lane ends at a reviewable draft PR unless Oleksii explicitly commands more.

Required boundary:

```text
branch
-> local validation
-> draft PR
-> independent review
-> explicit Oleksii merge command
```

Do not collapse review into executor self-approval. Do not treat draft PR creation as merge permission.

## Lane types

### Docs-only PR

Use for public-safe canon, protocol, or template compression.

Done means:

```text
files stayed inside the allowed docs scope
validation result reported
draft PR opened
```

### Test-only PR

Use for regression hardening and bounded validation work.

Done means:

```text
targeted tests changed
no unrelated production edits
draft PR opened
```

### Pure module plus tests

Use for isolated logic with explicit boundaries.

Done means:

```text
targeted tests pass
relevant lint/format pass
draft PR opened
```

### CLI wiring only

Use when a tested core already exists and the task is only integration wiring.

Done means:

```text
CLI behavior validated
existing related tests still pass
draft PR opened
```

### Narrow production fix

Use only after a specific failing behavior is identified.

Done means:

```text
one bug
smallest viable fix
relevant failing test included or referenced
draft PR opened
```

## Stop conditions

Stop and report instead of continuing if:

```text
the task needs files outside the allowed list
the task needs private configuration, secrets, env, server, or runtime access
the task needs deploy or merge
the task becomes broader than one reviewable PR
validation failure requires out-of-scope implementation
```

## Current evidence trail

The Development Lane is no longer hypothetical. As of 2026-05-16, real evidence exists in:

```text
#235 deep-diff-audit-pack CLI wiring
#236 first Skeleton/Jeeves canon audit matrix
#237 boot surface compression
#238 operating protocol compression
```

These PRs show the lane handling bounded implementation, docs-only compression, validation reporting, and reviewable draft-PR flow.

## Canonical principle

```text
Development Lane is how bounded coding work becomes reviewable evidence instead of trust-based claims.
```
