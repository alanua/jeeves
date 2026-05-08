# [skeleton-task] gemini-auditor-adapter

Priority: HIGH
Status target after task: LIKELY_NEEDS_REVIEW
Scope: reusable Skeleton bridge adapter, mock-first

## Goal

Implement a deterministic Runner/API adapter for the Gemini Auditor Node protocol.

The adapter must be generic and reusable by any Skeleton skill. It must not be specific to Construction Takeoff / Aufmaß.

## Canon source

Read first:

```text
knowledge_base/chatgpt_exoskeleton/skills/gemini_auditor_node.md
knowledge_base/WORKING_PROTOCOL.md
knowledge_base/CHATGPT_EXOSKELETON_RUNBOOK.md
```

## Architecture

```text
ChatGPT/Skeleton
-> JSON Intake Packet
-> Runner
-> Gemini adapter validation/redaction
-> mock Gemini response by default
-> optional live Gemini API only if explicitly enabled
-> fail-closed output validation
-> structured output packet
-> ChatGPT/Skeleton synthesis
```

## Required implementation properties

```text
stateless
mock-first
live mode disabled by default
fail-closed
strict JSON schema validation
secret/PII scanner before send and after receive
no direct ChatGPT -> Gemini connection
no Gemini commands execution
no canon updates from Gemini
no merge/deploy authority
```

## Input schema

```json
{
  "schema_version": "gemini_adapter.input.v1",
  "packet_id": "string",
  "objective": "string",
  "mode": "SELECT_ONE: [mock, live]",
  "privacy_level": "SELECT_ONE: [PUBLIC_SAFE, STRICT_REDACTION, INTERNAL_BHK]",
  "confirmed_canon": "string",
  "evidence": "string",
  "draft_artifact": "string",
  "exact_questions": [
    "string"
  ],
  "forbidden_actions": [
    "string"
  ]
}
```

## Output schema

```json
{
  "schema_version": "gemini-auditor-mock-output-v0.1",
  "packet_id": "string",
  "decision": "SELECT_ONE: [accept, block, revise]",
  "security_flags": [
    "string"
  ],
  "summary": "string",
  "rationale": [
    "string"
  ],
  "blocked_instruction": "string",
  "exoskeleton_note": "string",
  "canon_claim": "boolean",
  "commands": [
    "string"
  ],
  "architecture_suggestions": [
    "string"
  ],
  "live_access_references": [
    "string"
  ]
}
```

## Fail-closed block conditions

```text
missing/malformed API key when live mode is requested
input packet fails schema validation
secret or PII detected outbound
secret or PII detected inbound
executable code injected into JSON structural keys
poisoned_instruction or bypass attempt
Gemini output canon_claim=true
Gemini output commands is non-empty
Gemini output live_access_references is non-empty
strict mode output architecture_suggestions is non-empty
malformed JSON response
missing required output fields
unknown decision value
```

## Suggested files

Prefer a small implementation:

```text
tools/skeleton_core/gemini_auditor_adapter.py
tests/skeleton_core/test_gemini_auditor_adapter.py
tests/fixtures/gemini_auditor_input_public_safe.json
tests/fixtures/gemini_auditor_input_live_missing_key.json
tests/fixtures/gemini_auditor_input_secret_blocked.json
tests/fixtures/gemini_auditor_output_malformed_blocked.json
```

Optional CLI command:

```bash
python -m tools.skeleton_core.cli gemini-auditor-adapter --input tests/fixtures/gemini_auditor_input_public_safe.json
```

## CLI output statuses

```text
mock_accept
mock_revise
mock_block
blocked_schema_validation
blocked_secret_or_pii
blocked_live_mode_missing_key
blocked_output_validation
unknown_needs_review
```

## Forbidden

```text
no live Gemini API by default
no hardcoded API keys
no reading .env from repo
no printing secrets
no commands from Gemini
no merge/deploy/server changes
no private Drive links in public fixtures
no Construction Takeoff-specific assumptions in the generic adapter
```

## Validation required

```bash
python -m pytest -q
python -m ruff check tools/skeleton_core tests/skeleton_core
python -m black --check tools/skeleton_core tests/skeleton_core
python -m tools.skeleton_core.cli validate-state
```

If CLI is implemented:

```bash
python -m tools.skeleton_core.cli gemini-auditor-adapter --input tests/fixtures/gemini_auditor_input_public_safe.json
python -m tools.skeleton_core.cli gemini-auditor-adapter --input tests/fixtures/gemini_auditor_input_live_missing_key.json
python -m tools.skeleton_core.cli gemini-auditor-adapter --input tests/fixtures/gemini_auditor_input_secret_blocked.json
```

## Required report

```text
What changed:
What was verified:
What was not changed:
Blocked conditions tested:
Remaining risk/noise:
Next safe step:
```
