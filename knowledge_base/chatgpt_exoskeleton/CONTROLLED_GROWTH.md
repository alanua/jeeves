# Skeleton Controlled Growth Process

Status: CONFIRMED_CANON
Scope: rule for adding, activating, auditing, and stopping Skeleton skills
Created: 2026-05-07

## Purpose

Skeleton must grow as a real operating layer, not as a paper checklist.

A new skill is allowed only when it removes repeated work, prevents repeated failure, improves validation, reduces privacy/safety risk, or unlocks a concrete project workflow.

## Integrity rule

Skeleton must remain a coherent exoskeleton, not a pile of disconnected helpers.

Every new skill must either strengthen an existing workflow joint, close a repeated failure point, or connect two existing parts into a more reliable process.

If a proposed skill grows sideways, duplicates another skill, weakens enforcement, or creates unmanaged process branches, it must be blocked, merged into an existing skill, or kept as backlog.

The target shape is:

```text
few strong connected gates
not many loose paper capabilities
```

## Growth rule

```text
pain / repeated blocker
-> narrow skill request
-> local/offline public-safe v1
-> tests and fixtures
-> workflow-gate integration or explicit reason why no gate is needed
-> green CI
-> documented activation rule
-> use in real workflow
-> audit after use
```

## Admission criteria for a new skill

A proposed Skeleton skill is allowed only if all are true:

```text
[ ] It solves a concrete repeated blocker or validation friction.
[ ] It has a narrow input and output.
[ ] It has deterministic statuses such as ready/blocked/unknown.
[ ] It is local/offline/public-safe by default.
[ ] It does not perform live GitHub writes, runner execution, merge, deploy, server access, or secret handling unless explicitly authorized by a separate task.
[ ] It has tests and fixtures.
[ ] It is connected to workflow-gate, or the task records why workflow-gate is not relevant.
[ ] It strengthens the existing Skeleton flow instead of creating a disconnected side branch.
```

If these are not true, keep the idea as backlog instead of building it.

## Definition of done

A skill is not done when the file exists.

A skill is done only when:

```text
[ ] CLI command exists.
[ ] Unit tests exist.
[ ] CLI tests or fixtures exist.
[ ] CI is green.
[ ] Safety boundaries are explicit.
[ ] It is listed in CURRENT_STATE only after merge.
[ ] It is activated as a workflow gate when relevant.
[ ] A real workflow uses it at least once, or a follow-up issue records the integration gap.
[ ] It is connected to the existing Skeleton workflow map and does not remain a loose helper.
```

## Activation rule

```text
ready skill + relevant next action = mandatory gate
missing ready skill = blocked action
human override = explicit and recorded
```

The default response to a skipped ready skill is not “continue manually”. The default response is:

```text
stop
-> run the relevant skill
-> inspect the packet/report
-> continue only if action_ready or explicitly approved
```

## Anti-bloat rule

Do not add skills just because they sound useful.

Block or defer skill work if it is:

```text
abstract policy only
broad orchestrator work
large automation rewrite
live executor by default
auto-merge or deploy path
unclear input/output
missing tests
not connected to a real workflow
disconnected from existing Skeleton gates
```

## Current enforcement priority

```text
workflow-gate first
then capability-request-broker
then secrets-preflight
then only skills backed by observed project need
```

## Periodic audit questions

During `АУД СК`, check:

```text
[ ] Which skills are merged but not used?
[ ] Which skills are used only manually and need workflow-gate enforcement?
[ ] Which open issues are abstract or too broad?
[ ] Which skills should be retired, merged, or kept as backlog?
[ ] Did any recent failure happen because a ready skill was skipped?
[ ] Which skills are disconnected helpers rather than parts of one coherent workflow?
[ ] Which skills should be merged to keep the Skeleton compact and strong?
```

## Canonical principle

```text
Skeleton grows by converting repeated failure into enforced workflow.
A skill that does not change behavior is not a finished skill.
A disconnected skill is armor clutter, not strength.
```
