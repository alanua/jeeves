# Skeleton Dual-Brain Externalizer v0.1 — Architectural Anchor

Status: **v0.1 + Sprint 4 autonomous daemon verified**

This document anchors the practical state of the Skeleton Dual-Brain Externalizer after the successful live hands-off systemd test.

## 1. Current Implementation Status

Skeleton has moved from manual bridge tests to a working autonomous 24/7 pre-execution audit gate.

Implemented and verified:

- Foundation v0.1: typed Pydantic contracts and Gemini adapter.
- Dual-Brain issue bridge: GitHub Issue JSON -> DualBrainTaskPacket -> GeminiAuditorInput -> GeminiAdapterPacket.
- Autonomous once-route: `yellow_gemini_audit_route.py`.
- Continuous daemon: `yellow_runnerd.py`.
- Systemd service: `jeeves-runner.service` installed, enabled, and running on Hetzner.
- Live Gemini audit path: verified.
- Hands-off systemd processing: verified on Issue #126.

## 2. Core Components

### `tools/skeleton_core/dual_brain_task_packet.py`

Defines the typed contracts for bounded dual-brain work:

- `DualBrainTaskPacket`
- `DualBrainReviewPacket`
- `DualBrainTracePacket`
- `DualBrainSource`
- `DualBrainQuestionSet`
- `DualBrainExpectedOutput`
- `DualBrainForbiddenAction`

This file is the contract layer. It does not call Gemini, GitHub, or Runner.

### `tools/skeleton_core/gemini_auditor_adapter.py`

Provides the mock/live Gemini bridge.

Live REST path:

POST `https://generativelanguage.googleapis.com/v1beta/models/<model>:generateContent`

Live mode requires:

- `GEMINI_API_LIVE_MODE=true`
- `GEMINI_API_KEY` or `GOOGLE_API_KEY`

Verified model:

- `gemini-2.5-flash`

Hard output rules:

- `canon_claim` must be false.
- `commands` must be empty.
- `live_access_references` must be empty.
- merge/deploy are always false.
- Gemini output is evidence only.

### `tools/skeleton_core/issue_to_gemini_audit.py`

Translates GitHub issue JSON into strict Pydantic models.

Flow:

GitHub Issue JSON -> `GitHubIssueExport` -> `DualBrainTaskPacket` -> `GeminiAuditorInput` -> `gemini_auditor_adapter` -> `GeminiAdapterPacket`

The bridge does not execute issue tasks. It only prepares and routes them for audit.

### `tools/skeleton_core/yellow_gemini_audit_route.py`

Autonomous once-route for queued YELLOW issues.

Flow:

Queued GitHub issue -> label verification -> local secret/PII/poison scan -> sanitized Gemini audit -> GitHub comment -> label transition -> remove from active queue

This is the verified pre-execution audit route.

### `tools/skeleton_core/yellow_runnerd.py`

Continuous daemon for the Hetzner runner.

Responsibilities:

- Poll GitHub every 60 seconds.
- Find open issues with `agent:task`, `agent:queued`, `risk:yellow`, and `runner:hetzner` or `runner:any`.
- Call `yellow_gemini_audit_route.py`.
- Use Gemini audit as the pre-execution gate.
- Handle SIGINT/SIGTERM gracefully.
- Use a lock file to avoid duplicate daemon instances.
- Apply basic error backoff.
- Validate live Gemini environment before consuming the queue.

### `jeeves-runner.service`

Systemd service installed on Hetzner.

Role:

- Keeps `yellow_runnerd.py` running 24/7.
- Starts automatically after server reboot.
- Loads secrets from `/home/agent/agent-dev/.runner.env`.
- Writes logs to journald.

Current service state after verification:

- installed
- enabled
- active/running
- live mode
- model `gemini-2.5-flash`
- polling interval 60 seconds

## 3. GitHub Label State Machine

Candidate input labels:

- `agent:task`
- `agent:queued`
- `risk:yellow`
- `runner:hetzner` or `runner:any`

Temporary processing label:

- add `agent:auditing`

If Gemini returns `live_accept` or mock returns `mock_accept`:

- add `agent:audited`
- remove `agent:queued`
- remove `agent:auditing`

If Gemini returns `live_revise` or mock returns `mock_revise`:

- add `agent:needs-revision`
- remove `agent:queued`
- remove `agent:auditing`

If adapter returns `blocked_*`, `live_block`, or `mock_block`:

- add `agent:blocked`
- remove `agent:queued`
- remove `agent:auditing`

If route/daemon error occurs:

- add `agent:audit-error`
- remove `agent:queued`
- remove `agent:auditing`

Loop prevention rule:

- every terminal state removes `agent:queued`.

## 4. Verified Evidence

PR #118:

- added typed dual-brain packets
- added issue-to-Gemini bridge
- updated Gemini adapter
- CI passed
- merged to `main`

PR #119:

- added autonomous YELLOW Gemini audit once-route
- added route tests
- CI passed
- merged to `main`

PR #123:

- added `yellow_runnerd.py`
- added daemon tests
- CI passed
- merged to `main`

Issue #121:

- mock once-route test
- result: `mock_accept`
- `agent:queued` removed
- `agent:audited` added
- comment posted

Issue #122:

- live once-route test
- result: `live_accept`
- `agent:queued` removed
- `agent:audited` added
- comment posted
- no secrets leaked

Issue #124:

- daemon end-to-end mock test
- result: `mock_accept`
- daemon processed one queued issue
- comment posted
- label transition succeeded

Issue #125:

- daemon end-to-end live test
- result: `live_accept`
- daemon processed one queued issue
- comment posted
- label transition succeeded

Issue #126:

- full hands-off 24/7 systemd live test
- no manual script execution after issue creation
- systemd daemon picked up the issue automatically
- result: `live_accept`
- `agent:auditing` added during processing
- `agent:queued` removed
- `agent:auditing` removed
- `agent:audited` added
- live Gemini audit comment posted
- no secrets leaked
- merge/deploy remained false

## 5. Security Boundaries

Gemini must not:

- execute commands
- write canon
- merge
- deploy
- access secrets
- act as final authority

Runner must not:

- print secrets
- merge without approval
- deploy without approval
- write canon without approval
- execute arbitrary issue payloads before audit
- keep blocked issues in the active queue loop

Secrets must not be stored in:

- GitHub repo
- Markdown docs
- issue bodies
- comments
- fixtures
- ChatGPT memory
- Google Drive docs
- logs

Secrets belong only in protected runner environment, encrypted local storage, or a secret manager.

## 6. Current Implementation Boundary

The system currently provides a reliable **pre-execution audit gate**.

It does not yet execute the actual task described in the issue.

The system currently does not:

- run arbitrary commands from issue bodies
- change repository files based on issue body
- create PRs from audited issues
- merge
- deploy
- promote canon automatically

## 7. Next Sprint: Sprint 5 Execution Handoff

Goal:

Create a safe mechanism for moving from audit to bounded execution.

Sprint 5 should define and implement:

- `ExecutionPacket`
- post-audit execution dispatcher
- strict command allowlist
- workspace isolation
- trace logging
- execution result comment
- new labels for execution state
- human approval gates for file writes, PR creation, merge, deploy, or canon promotion

Possible next labels:

- `agent:execution-ready`
- `agent:executing`
- `agent:execution-complete`
- `agent:execution-blocked`
- `agent:needs-human-approval`

The execution dispatcher must consume only issues that already passed the audit gate.


## 10. Sprint 5 Phase 1 Verified

Sprint 5 Phase 1 added:

- `tools/skeleton_core/bounded_execution_packet.py`
- `tools/skeleton_core/dry_run_execution_route.py`
- `tests/skeleton_core/test_bounded_execution_packet.py`
- `tests/skeleton_core/test_dry_run_execution_route.py`

Verified on Issue #126:

- consumed an issue that had already passed audit with `agent:audited`
- verified accepted audit evidence
- built `ExecutionPacket`
- posted bounded execution dry-run report
- transitioned `agent:audited` to `agent:executed`
- removed `agent:executing`
- executed zero shell commands
- changed zero files
- created no PR
- performed no merge
- performed no deploy
- performed no canon write

Current execution boundary:

- `executor_allowed = false`
- `file_writes_allowed = false`
- `pr_creation_allowed = false`
- `merge_allowed = false`
- `deploy_allowed = false`
- `canon_write_allowed = false`

## 8. Minimal Mental Model

`dual_brain_task_packet.py`
= typed contract

`gemini_auditor_adapter.py`
= live/mock Gemini bridge

`issue_to_gemini_audit.py`
= GitHub Issue JSON -> GeminiAuditorInput

`yellow_gemini_audit_route.py`
= queued YELLOW issue -> audit comment + label transition

`yellow_runnerd.py`
= continuous daemon calling the audit route

`jeeves-runner.service`
= 24/7 systemd wrapper around `yellow_runnerd.py`

## 9. Current State

Skeleton Dual-Brain Externalizer v0.1 is real code in `main`.

The live Gemini bridge is verified.

GitHub issue to Gemini audit is verified.

Autonomous YELLOW once-route is verified.

Yellow runner daemon is verified.

Systemd 24/7 hands-off live processing is verified.

Sprint 5 Phase 1 bounded execution dry-run handoff is verified. Next step is designing a real executor only behind stricter approval gates.

## 11. Sprint 7 Phase 1 Plan Mode Verified

Sprint 7 Phase 1 added:

- `tools/skeleton_core/active_executor.py`
- active executor plan/real mode separation
- command allowlist
- destructive command blocking
- force-push blocking
- `[REAL_EXECUTION]` diary logging path for future real execution
- failure snapshot path via `knowledge_base/current_state.json`

Verified on Issue #130:

- issue was first processed by the live systemd audit daemon
- Gemini returned `live_accept`
- issue entered `agent:audited`
- `active_executor` was run in `plan` mode only
- `ExecutionPacket` was built from accepted audit evidence
- GitHub Active Executor Report was posted
- `agent:audited` was removed
- `agent:executed` was added
- no shell commands were executed
- no files were changed
- no PR was created
- no merge was performed
- no deploy was performed
- no canon write was performed

Current Sprint 7 boundary:

- `plan` mode is verified
- `real` mode is implemented but not verified
- `real` mode must not run automatically
- `real` mode requires a separate controlled test issue and explicit human approval


## Sprint 11B Canon Audit Route State Clarification

Status: verified after Issue #143 and PR #142.

The Canon Audit Layer is now implemented and has passed a first real route test.

Verified route:

- `python -m tools.skeleton_core.cli canon-audit`
- reads only predefined allowlisted canon/core files
- scans issue body and canon bundle for secret patterns
- calls Gemini as an auditor/evidence source only
- posts the audit report back to the GitHub Issue
- performs no local file writes
- creates no PR during route execution
- performs no merge or deploy
- does not promote audit findings to canon automatically

### Label state clarification

The label model separates task type from task state.

Task-type label:

- `agent:canon-audit` means the issue is intended for the specialized canon-audit route.

State labels:

- `agent:queued` means the issue is waiting for the base yellow audit daemon.
- `agent:audited` means the issue passed the base YELLOW Gemini audit gate.
- `agent:audit-complete` means the specialized canon-audit route completed and posted its audit report.

Important distinction:

- `agent:audited` is not the same as `agent:audit-complete`.
- `agent:audited` is the precondition produced by the base audit gate.
- `agent:audit-complete` is the terminal state for the canon-audit route.

### Real-mode verification status

The following bounded real-mode actions have been verified:

- `validate-state`
- `create-report`
- `create-pr`
- `canon-audit`

This does not grant general autonomous execution rights.

The runner still must not:

- execute arbitrary shell commands
- merge PRs
- deploy
- promote canon automatically
- write secrets
- modify policy/canon documents without human-reviewed PR flow

