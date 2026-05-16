# Skeleton Controlled Growth Policy

Status: CONFIRMED_CANON
Scope: durable anti-bloat and admission policy for Skeleton lanes, skills, and workflow gates
Created: 2026-05-07
Last consolidated: 2026-05-16

## Purpose

Skeleton should grow by turning repeated failure or friction into a smaller, safer, more enforceable operating layer.

This file is the durable policy for admitting or rejecting new Skeleton capabilities. It is not a status board, a roadmap dump, or a place to restate every active workflow.

## Ontology gate

```text
ChatGPT Exoskeleton = historical/current ChatGPT-facing prototype of Skeleton.
Unified Skeleton Core = target model-neutral external operating layer for LLM-assisted work.
ChatGPT = current host/interface for the prototype.
Codex = coding executor.
Gemini = auditor / second-brain role.
OpenHands = bounded executor role.
Jeeves = separate future independent assistant/product.
```

Critical rule:

```text
Jeeves is not a Skeleton adapter.
Jeeves is not runtime under Skeleton.
Skeleton is the precursor, proving ground, practical toolchain, and construction scaffold used to build Jeeves more safely.
```

## Core growth rule

```text
repeated pain or repeated failure
-> narrow proposal
-> bounded implementation or rule
-> explicit safety boundary
-> validation
-> activation as a real gate when relevant
-> evidence of use
-> periodic audit
```

If a proposal does not change behavior, reduce risk, or remove repeated work, it should not enter active Skeleton canon.

## Integrity rule

Skeleton must remain a coherent external operating layer, not a pile of disconnected helpers.

A new lane, skill, or gate is allowed only when it does at least one of these:

```text
strengthens an existing workflow joint
closes a repeated failure point
connects existing parts into a safer operating loop
compresses a noisy process into a smaller enforceable rule
```

If it duplicates an existing gate, creates a side branch, or exists only as explanation without enforcement, it should be merged, demoted to reference, or kept as backlog.

## Admission criteria

Admit a new Skeleton lane, skill, or gate only if all are true:

```text
[ ] It solves a concrete repeated blocker, risk, or validation gap.
[ ] It has narrow inputs, outputs, and stop conditions.
[ ] It has explicit role boundaries.
[ ] It is local/offline/public-safe by default unless a separate task authorizes more.
[ ] It does not create deploy, merge, secret, runtime, or server access by default.
[ ] It has a clear evidence trail.
[ ] It attaches to an existing workflow gate, or the task records why no gate is needed.
[ ] It makes the active operating surface smaller or stronger, not broader or noisier.
```

For canon or instruction changes, critique-before-action is part of admission. Read the current rule first, identify overlap or contradiction, then patch minimally.

## Anti-bloat filter

Block, defer, or demote proposals that are mainly:

```text
duplicate policy
status snapshot pretending to be canon
broad orchestration ambition without a bounded workflow
live executor autonomy by default
merge or deploy path by default
secret/runtime/server access path
unclear input/output
missing validation or evidence
unowned backlog disguised as an active lane
```

The default answer to a vague or oversized proposal is not "add another doc." The default answer is "narrow it, attach it to a real gate, or keep it out of active canon."

## Activation rule

```text
ready gate + relevant task = mandatory use
missing ready gate for required work = stop and report
human override = explicit and recorded
```

Do not keep "ready but optional" active gates around for long. If a gate matters, wire it into behavior. If it does not change behavior, demote it from active status.

## Definition of done

A new Skeleton capability is done only when:

```text
[ ] the boundary and intended trigger are explicit
[ ] the required evidence is explicit
[ ] validation exists
[ ] GitHub issues, PRs, or comments can show real use or justified readiness
[ ] it is connected to an existing operating lane when relevant
[ ] it does not expand the default boot or canon surface unnecessarily
[ ] it is listed in status inventory only after the active rule is real
```

## Active-rule boundary

Use this split to keep the operating surface compressed:

```text
CONTROLLED_GROWTH.md = durable admission and anti-bloat policy
coding_lane_template_and_evidence_protocol.md = active Development Lane gate
skill_inventory_activation_map.md = dated status/inventory snapshot, not core canon
```

## Periodic audit questions

During lane or canon audits, ask:

```text
[ ] Which active items still change behavior?
[ ] Which items are status snapshots and should not act as canon?
[ ] Which gates are merged but not actually used?
[ ] Which duplicated docs can be compressed into one rule?
[ ] Did a recent failure happen because a ready gate was skipped?
[ ] Is any proposal silently widening access or authority?
```

## Canonical principle

```text
Skeleton should gain enforcement, not paperwork.
If a capability does not improve behavior, evidence, or safety, it does not belong in the active layer.
```
