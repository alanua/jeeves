# Skeleton Skill Inventory and Activation Snapshot

Status: REFERENCE_SNAPSHOT
Scope: dated status and inventory snapshot for the current ChatGPT-facing Skeleton prototype
Issue: #228
Snapshot date: 2026-05-16

## Purpose

This file is a status snapshot, not core canon.

Use it to see what currently exists, what appears active, and what still looks provisional. Do not use it as the durable source of operating rules.

Active rule sources:

```text
knowledge_base/WORKING_PROTOCOL.md
knowledge_base/CHATGPT_EXOSKELETON_RUNBOOK.md
knowledge_base/chatgpt_exoskeleton/CONTROLLED_GROWTH.md
knowledge_base/chatgpt_exoskeleton/runner_tasks/coding_lane_template_and_evidence_protocol.md
```

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

## How to read this file

Classification legend:

```text
ACTIVE_GATE = active rule or gate that should change behavior
AVAILABLE_CAPABILITY = usable now, but not itself the core rule source
BOUNDED_EXECUTOR = executor role with explicit limits
REFERENCE_ONLY = useful background or template, not active canon
DOMAIN_SPECIFIC = active only inside a specific project/domain workflow
LEGACY_OR_ARCHIVE = preserved history, not active path
```

## Current snapshot

| Item | Class | What it means now | Evidence or status note | Next handling |
|---|---|---|---|---|
| `CONTROLLED_GROWTH.md` | ACTIVE_GATE | Durable anti-bloat and admission policy for lanes/skills/gates | Active canon after Phase 4 cleanup | Keep as core rule |
| `runner_tasks/coding_lane_template_and_evidence_protocol.md` | ACTIVE_GATE | Active Development Lane gate for Codex/OpenHands/bounded coding work | Real evidence from #235, #236, #237, #238 | Keep as core rule |
| `CURRENT_STATE.md` | ACTIVE_GATE | Short Skeleton continuity and handoff source | Active wake/recovery support | Keep active |
| `runner-status-check` | AVAILABLE_CAPABILITY | Runner truth check before trusting labels or stale task claims | Used to avoid status guessing | Keep available |
| `deep-diff-audit-pack` CLI | AVAILABLE_CAPABILITY | Public-safe duplicate/gap/conflict evidence builder | #178 CLI wiring merged through #235; available via `python -m tools.skeleton_core.cli deep-diff-audit-pack --input <json>` | Use when deep-diff audit evidence is needed |
| Gemini auditor node / adapter docs | AVAILABLE_CAPABILITY | Auditor/second-brain reference with adapter boundary | Useful when independent critique is requested | Keep as reference-backed capability |
| OpenHands bounded executor role | BOUNDED_EXECUTOR | Bounded executor path for sandboxed coding tasks | Must stay inside Development Lane gate and external evidence collection | Keep bounded |
| `SKELETON_RUNNER_TASK_TEMPLATE.md` | REFERENCE_ONLY | Task drafting template | Helpful, but not a gate | Keep as reference |
| General exoskeleton docs/runbook | REFERENCE_ONLY | Orientation and operating support | Useful background, not a skill inventory gate | Keep as reference |
| Construction takeoff skill/task docs | DOMAIN_SPECIFIC | Domain workflow for takeoff work | Not core Skeleton canon | Keep scoped to that domain |
| Old host-local shell runner mapping | LEGACY_OR_ARCHIVE | Historical runner route notes | Preserved as old evidence, not active behavior | Keep out of active path |

## Activation map

| Task type | Use this first | Notes |
|---|---|---|
| New lane/skill/gate proposal | `CONTROLLED_GROWTH.md` | Admission and anti-bloat rule |
| Codex coding task | Development Lane gate | Branch -> validation -> draft PR -> independent review -> explicit Oleksii merge command |
| OpenHands coding task | Development Lane gate + bounded OpenHands role | Same evidence and review boundary as Codex |
| Deep duplicate/gap/conflict audit | `deep-diff-audit-pack` CLI when relevant | Capability is available now after #235 |
| Runner/task state claim | runner-status-check or GitHub evidence | Do not trust stale labels or self-report |
| Canon/instruction cleanup | `WORKING_PROTOCOL.md` + runbook + critique-before-action | Read current rules before editing |

## Snapshot cautions

This file will age faster than the active rule docs.

Do not use it to overrule:

```text
WORKING_PROTOCOL for ontology, merge, and safety rules
RUNBOOK for operating checklist and verification flow
CONTROLLED_GROWTH for admission policy
Development Lane protocol for bounded coding work
```

## Canonical principle

```text
An inventory helps orientation.
It should never compete with the active rule surface.
```
