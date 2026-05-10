# Skeleton Dual-Brain Externalizer v0.1 — State Anchor

Status: implemented in `main`.

This file anchors the practical state of the Skeleton Dual-Brain Externalizer so ChatGPT, Gemini, Runner, and Oleksii keep the same map.

## 1. Base Camp

Implemented and verified:

- `tools/skeleton_core/gemini_auditor_adapter.py`
- `tools/skeleton_core/dual_brain_task_packet.py`
- `tools/skeleton_core/issue_to_gemini_audit.py`
- `tools/skeleton_core/yellow_gemini_audit_route.py`

Merged:

- PR #118: Dual-Brain issue bridge.
- PR #119: Autonomous YELLOW Gemini audit once-route.

Verified:

- Issue #121: mock route passed with `mock_accept`.
- Issue #122: live route passed with `live_accept`.
- CI passed.
- Local validation passed.

Current boundary:

- The system has an autonomous once-route.
- It is not yet a 24/7 daemon.
- Next step is daemonization, not more architecture.

## 2. Roles

Oleksii is final authority.

ChatGPT / Skeleton is the architect, control plane, synthesis node, and canon gate.

Gemini Auditor Node is a stateless evidence source only.

Gemini is not:

- executor
- manager
- canon writer
- merger
- deployer
- final authority

Hetzner Runner is the deterministic execution and routing environment.

GitHub Issues are the public-safe queue, state machine, and audit trail.

## 3. Core Components

### `dual_brain_task_packet.py`

Defines typed Pydantic contracts:

- `DualBrainTaskPacket`
- `DualBrainReviewPacket`
- `DualBrainTracePacket`
- `DualBrainSource`
- `DualBrainQuestionSet`
- `DualBrainExpectedOutput`
- `DualBrainForbiddenAction`

Important defaults:

- `executor_allowed = False`
- `approval_mode = BEFORE_PERSISTENCE`
- `persistence_target = RUNNER_TRACE_ONLY`
- allowed nodes are ChatGPT/Skeleton, Gemini Auditor, and Runner.

This file is only a contract layer. It does not call Gemini, GitHub, or Runner.

### `gemini_auditor_adapter.py`

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

## 4. Bridge

### `issue_to_gemini_audit.py`

Flow:

GitHub Issue JSON
-> `GitHubIssueExport`
-> `DualBrainTaskPacket`
-> `GeminiAuditorInput`
-> `gemini_auditor_adapter`
-> `GeminiAdapterPacket`

Expected GitHub input:

`gh issue view <number> --repo alanua/jeeves --json number,title,body,labels,url,state`

Default forbidden actions:

- merge
- deploy
- print_secrets
- write_canon

The bridge does not execute issue tasks. It only prepares and routes them for audit.

## 5. Autonomous Once-Route

### `yellow_gemini_audit_route.py`

Flow:

GitHub queued YELLOW issue
-> verify labels
-> local secret/PII/poison scan
-> sanitize issue body if needed
-> run `issue_to_gemini_audit.py`
-> capture `GeminiAdapterPacket`
-> post public-safe GitHub comment
-> transition labels
-> remove issue from active queue

Candidate issue must have:

- `agent:task`
- `agent:queued`
- `risk:yellow`
- `runner:hetzner` or `runner:any`

Skip labels:

- `agent:auditing`
- `agent:audited`
- `agent:blocked`
- `agent:audit-error`
- `agent:needs-revision`

## 6. Label State Machine

Initial queued state:

- `agent:task`
- `agent:queued`
- `risk:yellow`
- `runner:hetzner` or `runner:any`

Processing:

- add `agent:auditing`

If `live_accept` or `mock_accept`:

- add `agent:audited`
- remove `agent:queued`
- remove `agent:auditing`

If `live_revise` or `mock_revise`:

- add `agent:needs-revision`
- remove `agent:queued`
- remove `agent:auditing`

If `blocked_*`, `live_block`, or `mock_block`:

- add `agent:blocked`
- remove `agent:queued`
- remove `agent:auditing`

If route error:

- add `agent:audit-error`
- remove `agent:queued`
- remove `agent:auditing`

Loop prevention:

- every terminal state removes `agent:queued`.

## 7. Verified Evidence

PR #118 added:

- typed dual-brain packets
- issue-to-Gemini bridge
- updated Gemini adapter

PR #119 added:

- autonomous YELLOW Gemini audit once-route
- route tests

Issue #121:

- `mock_accept`
- `agent:queued` removed
- `agent:audited` added
- comment posted

Issue #122:

- `live_accept`
- `agent:queued` removed
- `agent:audited` added
- comment posted
- no secrets leaked
- merge allowed false
- deploy allowed false

## 8. Security Boundaries

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

## 9. Pending Work

Not yet implemented:

- `yellow_runnerd.py`
- continuous daemon loop
- systemd service
- production runner heartbeat
- post-audit execution handoff

## 10. Next Sprint

Sprint 4 should implement:

- `tools/skeleton_core/yellow_runnerd.py`
- `tests/skeleton_core/test_yellow_runnerd.py`
- systemd service for Hetzner runner
- graceful shutdown
- poll interval
- lock file
- basic exponential error backoff
- live env validation

The daemon must call the existing route:

- `yellow_gemini_audit_route.py`

It must not duplicate Gemini adapter logic.

## 11. Minimal Mental Model

`dual_brain_task_packet.py`
= typed contract

`gemini_auditor_adapter.py`
= live/mock Gemini bridge

`issue_to_gemini_audit.py`
= GitHub Issue JSON -> GeminiAuditorInput

`yellow_gemini_audit_route.py`
= queued YELLOW issue -> audit comment + label transition

`yellow_runnerd.py`
= future continuous loop calling the route

## 12. Current State

Skeleton Dual-Brain Externalizer v0.1 is real code in `main`.

Gemini live bridge is verified.

GitHub issue to Gemini audit is verified.

Autonomous YELLOW once-route is verified.

Next step is daemonization, not more architecture.
