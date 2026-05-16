# Skeleton Skill Inventory and Activation Map

Status: LIKELY_NEEDS_REVIEW
Scope: public-safe inventory of existing Skeleton skills/protocols/templates
Issue: #228

## Operating principle

Skeleton is practical usefulness, not a pile of unused templates.

```text
A skill without activation is clutter.
```

No new Skeleton skill should be accepted unless it has:

```text
trigger + gate + evidence of use + owner task type
```

## Classification legend

```text
ACTIVE_GATE — actively used as a workflow gate
READY_NOT_WIRED — useful, but lacks trigger/gate/evidence wiring
REFERENCE_ONLY — background reference, not a skill
DUPLICATE_OR_OVERLAP — should be merged with another item
OBSOLETE_OR_REJECT — should be archived or removed from active lists
IDEA_BACKLOG — not ready to be called a skill
```

## Current inventory

| Item | Current class | Task type | Trigger | Evidence/use today | Next action |
|---|---|---|---|---|---|
| `CURRENT_STATE.md` | ACTIVE_GATE | branch continuity | new branch / wake / status question | used to recover state and avoid chat-memory-only claims | keep active, update after important merges |
| `START_HERE.md` wake source map | ACTIVE_GATE | Skeleton wake/recovery | `прокинься СК`, infrastructure/context recovery | defines files to read before claims | keep active |
| `runner-status-check` | ACTIVE_GATE | runner truth check | user asks task/runner status, labels look stale | used to avoid trusting `agent:running` labels | keep active; prefer before queue advance |
| `deep_diff_audit_pack.py` | READY_NOT_WIRED | deep audit evidence | duplicate/overlap/gap/conflict audit | core builder exists with tests; no full CLI/source workflow yet | wire CLI/source collection in #178 |
| Gemini Auditor Node / adapter docs | READY_NOT_WIRED | external audit | user asks Gemini audit or second opinion | mock-first and safety policy exist; live route not always available | keep but require adapter status/evidence |
| Coding lane evidence protocol | ACTIVE_GATE | agent coding work | OpenHands/Codex/bounded executor coding task | merged after OpenHands pilot; defines evidence requirements | use for every coding task |
| OpenHands bounded adapter | READY_NOT_WIRED | bounded executor | sandbox/doc/test-only executor task | adapter exists; smoke path hardened; still needs wrapper evidence automation | use only for bounded pilots |
| Construction takeoff skill docs | READY_NOT_WIRED | Aufmaß/takeoff | user asks drawing/takeoff/areas | workflow docs exist; private pilot not complete | use only with private source routing and review |
| Semi-automatic construction takeoff + Gemini | READY_NOT_WIRED | takeoff with reviewer | takeoff needs Gemini second-brain review | workflow exists; no completed private pilot yet | keep as pilot workflow |
| Skeleton runner task template | REFERENCE_ONLY | task drafting | creating runner tasks | template supports task creation but is not a gate itself | keep reference |
| General exoskeleton docs/runbook | REFERENCE_ONLY | architecture/boot | branch recovery / orientation | useful background; not a narrow skill | keep reference, do not call it a skill |
| Old host-local shell runner mapping | OBSOLETE_OR_REJECT | legacy execution | none; do not use | failed new tasks with unknown YELLOW task mapping | keep as evidence until inventoried, not active |

## Activation map

| Task type | Required active gate | Stop if missing |
|---|---|---|
| New Skeleton branch / wake | `START_HERE.md` + `CURRENT_STATE.md` | yes |
| Claiming runner/task state | runner-status-check or explicit issue/PR/log evidence | yes |
| Coding with bounded executor | coding lane evidence protocol | yes |
| OpenHands task | coding lane evidence protocol + OpenHands adapter boundaries | yes |
| Deep duplicate/gap/conflict audit | deep-diff evidence packet | not yet mandatory until #178 CLI is wired |
| Gemini audit | Gemini adapter contract + adapter/live/mock status | yes |
| Construction takeoff | construction takeoff skill + private/public source routing | yes |
| Creating a new skill | trigger + gate + evidence + owner task type | yes |

## Deadweight candidates

These are not deleted now, but should not be presented as active skills:

```text
general architecture docs without a trigger
templates that only describe a process but do not block or validate work
legacy runner route notes that no longer match live behavior
old shell runner mappings
```

## Immediate wiring priorities

```text
1. Finish #178 CLI wiring for deep-diff-audit-pack.
2. Use coding lane evidence protocol for the next real coding task.
3. Use BauClock #23 as the first real test-only coding lane pilot.
4. Build wrapper-side evidence collection for OpenHands instead of relying on executor self-report.
5. Inventory/archive old host-local shell runner scripts after reference capture.
```

## Practical rule for future work

If a document cannot answer all four questions, it is not an active Skeleton skill:

```text
When does it trigger?
What does it check or block?
What output does it produce?
What evidence proves it was used?
```

If the answer is unclear, classify it as `REFERENCE_ONLY`, `READY_NOT_WIRED`, or `IDEA_BACKLOG` instead of calling it a skill.
