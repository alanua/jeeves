# Skeleton Canon-Audit Request Standard

Status: proposed documentation standard
Scope: СК / ChatGPT Exoskeleton / Gemini canon-audit route
Created: 2026-05-12

## Purpose

Canon-audit requests must follow a fixed two-step standard. They must not be created ad hoc from chat wording, guessed labels, or improvised GitHub comments.

This document exists because `agent:canon-audit` is a task-type label, not a complete execution state. A canon-audit request is only ready for the specialized route after the base YELLOW Gemini audit gate has accepted the issue.

## Mental model

```text
base YELLOW audit gate
-> agent:audited
-> specialized canon-audit CLI route
-> agent:audit-complete
```

Do not treat `agent:queued` + `agent:canon-audit` as enough to run the specialized canon-audit route.

## Step 1: create the audit request issue

The request issue must clearly state:

```text
Active project
Target under audit
Goal
Audit questions
Required canon/context to compare against
Expected output format
Forbidden actions
Safety boundary
Done condition
```

The issue body must be public-safe. It must not contain secrets, `.env` values, private paths, tokens, credentials, private Drive URLs, raw private data, or production data.

## Step 2: queue the base YELLOW audit gate

Initial labels for the base YELLOW gate:

```text
agent:task
agent:queued
risk:yellow
runner:hetzner OR runner:any
agent:canon-audit
```

Expected result of the base gate:

```text
agent:queued removed
agent:auditing removed, if present
agent:audited added if Gemini accepts
```

If the base gate returns `agent:needs-revision`, `agent:blocked`, or `agent:audit-error`, do not run the specialized canon-audit route. Fix the request or report the blocker first.

## Step 3: run the specialized canon-audit route

Only after the issue has `agent:audited`, run:

```bash
python -m tools.skeleton_core.cli canon-audit --repo alanua/jeeves --issue <issue-number>
```

Required precondition labels for the specialized route:

```text
agent:task
risk:yellow
agent:audited
agent:canon-audit
runner:hetzner OR runner:any
```

Do not add `agent:queued` again for this step. The issue has already passed the base YELLOW audit gate.

## Expected specialized route result

The specialized canon-audit route must:

```text
read allowlisted canon/core files only
scan issue body and canon bundle for secret-like patterns
ask Gemini to audit against Skeleton canon
post a Skeleton Canon Audit Route Report as a GitHub comment
add agent:audit-complete
remove agent:audited
write no files
create no PR
perform no merge/deploy
print no secrets
```

## Terminal labels

```text
agent:audited
```

Means: the issue passed the base YELLOW Gemini audit gate.

```text
agent:audit-complete
```

Means: the specialized canon-audit route completed and posted the canon audit report.

These are not interchangeable.

## Forbidden shortcuts

Do not:

```text
manually summarize a canon audit when the skill/route exists
assume agent:canon-audit automatically runs the specialized route
expect yellow_runnerd.py to perform the specialized route automatically
re-add agent:queued after the base gate has produced agent:audited
write canon, code, or PRs from the audit issue
merge or deploy based on a positive Gemini audit
store secrets/private paths in the issue, prompt, comment, or fixture
```

## Pre-implementation architecture audit

Use this standard before implementing a new Skeleton module when the module changes or touches:

```text
runner behavior
control flow
audit/gate behavior
security boundaries
memory/canon routing
external model integration
queue state
execution authority
```

The audit issue should ask whether the proposed module is necessary, whether it duplicates existing modules, whether the responsibilities are correctly separated, and whether the smallest safe v0 is defined.

Implementation tasks should normally wait until the canon-audit route has posted its report, or until Oleksii explicitly overrides this gate.

## Correct handling when the first audit output is incomplete

If the base Gemini gate only validates that the request is safe, but does not answer the target audit questions, treat it as an incomplete preliminary result.

Correct next action:

```text
verify the issue has agent:audited
run the specialized canon-audit CLI route
wait for Skeleton Canon Audit Route Report
only then synthesize edits or implementation tasks
```

## Implementation boundary

The canon-audit report is evidence only.

It must not automatically:

```text
approve implementation
modify canon
create a branch
open a PR
merge
deploy
advance unrelated queues
```

Human review remains required after the report.
