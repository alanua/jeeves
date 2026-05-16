# Skeleton Coding Lane Template and Forced Evidence Protocol

Status: LIKELY_NEEDS_REVIEW
Scope: public-safe operating template for bounded coding executors
Issue: #226

## Purpose

Skeleton coding lanes exist to let bounded executors help with real code while keeping the control plane evidence-driven.

The goal is not broad autonomy. The goal is small, repeatable, reviewable coding work through branches and draft pull requests.

## Core rule

```text
Executor self-report is not evidence.
```

A message like `done`, `fixed`, or `successfully updated` is only a claim. The runner, wrapper, or human operator must collect independent evidence after the executor stops.

## Standard task envelope

Every coding task should define:

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

The goal must be narrow enough for one reviewable pull request. The allowed files list must be explicit. If the task needs more files than allowed, the executor must stop and report instead of expanding scope.

## Default executor boundaries

```text
No private configuration access.
No remote environment access.
No production data access.
No deployment or service mutation.
No merge.
No broad setup actions unless explicitly allowed.
No hidden expansion of scope.
```

A coding lane may allow extra actions only when the task envelope names them explicitly.

## Forced evidence protocol

After the executor finishes, evidence must be collected outside the executor's own answer.

Required evidence:

```text
working tree status
diff sanity check
diff summary
diff for allowed files only
targeted tests
format and lint checks when relevant
```

Equivalent local commands may include:

```bash
git status --short
git diff --check
git diff --stat
git diff -- <allowed-files>
```

For Python code, typical validation is:

```bash
python -m pytest -q <targeted-tests>
python -m ruff check <changed-python-files-and-tests>
python -m black --check <changed-python-files-and-tests>
```

For documentation-only changes, at minimum:

```bash
git diff --check
git status --short
```

## Lane types

### Sandbox edit

Use for first executor pilots and safe file-bound edits.

Done means:

```text
only allowed file changed
diff/status evidence collected outside the executor
```

### Docs-only PR

Use for protocols, templates, task specs, and public-safe handoffs.

Done means:

```text
draft PR opened
files changed are documentation-only
validation result reported
```

### Pure module plus tests

Use for isolated logic with no external calls.

Done means:

```text
targeted tests pass
format/lint pass
draft PR opened
```

### CLI wiring only

Use after a tested core module exists.

Done means:

```text
CLI test passes
existing module tests still pass
format/lint pass
draft PR opened
```

### Test-only PR

Use for access-control, privacy, business-logic, and regression hardening.

Done means:

```text
test files only by default
no production code changes
if a real bug is exposed, stop and report
```

### Narrow production fix after failing test

Use only after a test or audit identifies a specific failing behavior.

Done means:

```text
one bug
smallest viable fix
failing test included or referenced
no architecture rewrite
no unrelated cleanup
```

## Promotion rule

Executors earn broader responsibility only by repeated clean runs.

Promotion evidence should include:

```text
scope stayed inside allowed files
no forbidden actions attempted
wrapper evidence was complete
tests and checks were run
PR stayed small and reviewable
```

Suggested progression:

```text
sandbox edit
-> docs-only PR
-> pure module plus tests
-> CLI wiring only
-> test-only PR
-> narrow production fix after failing test
```

## OpenHands pilot lesson

The first OpenHands sandbox pilot was useful but not sufficient as a trust signal.

Observed:

```text
OpenHands completed the allowed sandbox edit.
OpenHands stayed inside the allowed file boundary.
OpenHands did not provide the required post-edit diff evidence.
```

Conclusion:

```text
A bounded executor can perform the edit and still miss the evidence protocol.
The wrapper must force evidence collection independently.
```

## Minimal PR report template

```text
Summary:
Files changed:
Lane type:
Validation run:
Evidence collected:
Scope confirmation:
Known limitations:
Next safe step:
```

## Stop conditions

Stop and report instead of continuing if:

```text
the task needs files outside the allowed list
the task needs remote environment access
the task needs private configuration or production data
the task becomes broader than one reviewable change
tests fail in a way that requires implementation outside the task scope
```

## Current status

This protocol is a draft operating rail. It should be tested on small tasks before being treated as a mandatory gate.

Recommended first real pilot:

```text
BauClock #23 test-only access-control hardening
```
