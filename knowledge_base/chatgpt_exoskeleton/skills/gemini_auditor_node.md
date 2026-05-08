# Gemini Auditor Node Bridge

Status: LIKELY_NEEDS_REVIEW
Priority: HIGH
Scope: reusable public-safe Skeleton integration protocol

## Purpose

Define a universal Gemini Auditor Node bridge for any Skeleton skill or project workflow.

This bridge is not specific to Construction Takeoff / Aufmaß. Construction Takeoff is only one future consumer.

## Role assignment

```text
ChatGPT/Skeleton = primary architect, control plane, and canon gate.
Oleksii = final authority.
Gemini = stateless deep-context auditor, multimodal analyst, and private-memory triage assistant.
Runner = deterministic Python/Docker execution and transport layer.
Adapter = strict stateless validation/redaction/API bridge between Runner and Gemini API.
```

## Rules of engagement

```text
No direct ChatGPT -> Gemini connection.
ChatGPT generates a JSON Intake Packet.
Runner parses the packet, handles redaction, calls the adapter, and returns the result.
Gemini is a reviewer, not a manager.
Gemini does not execute code, merge PRs, deploy, update canon, or approve final facts.
Gemini is stateless: every request must include all needed confirmed_canon and evidence.
ChatGPT/Skeleton synthesizes Gemini feedback and makes the final recommendation to Oleksii.
```

## Adapter operating model

```text
Adapter role: stateless deterministic transport and validation layer.
Live mode: disabled by default.
Mock-first architecture is mandatory.
Fail-closed parser is mandatory.
Secrets must exist only in isolated Runner/server environment variables.
Outbound and inbound payloads must be scanned for secrets/PII.
Malformed JSON, missing required fields, forbidden populated arrays, or poisoned instructions must block.
```

## Input packet schema

From Runner to Gemini:

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

## Output packet schema

From Gemini to Runner:

```json
{
  "schema_version": "gemini-auditor-mock-output-v0.1",
  "packet_id": "string",
  "decision": "SELECT_ONE: [accept, block, revise]",
  "security_flags": [
    "string (e.g., 'secret_detected', 'parser_validation_failure')"
  ],
  "summary": "string",
  "rationale": [
    "string"
  ],
  "blocked_instruction": "string",
  "exoskeleton_note": "string",
  "canon_claim": "boolean (Must be false)",
  "commands": [
    "string (Must be empty)"
  ],
  "architecture_suggestions": [
    "string (Must be empty in strict mode)"
  ],
  "live_access_references": [
    "string (Must be empty)"
  ]
}
```

## Immediate block conditions

```text
1. API key environment variable is missing or malformed while live mode is requested.
2. Input packet fails strict JSON schema validation before send.
3. Adapter regex scanner detects leaked secret or PII in outbound packet or inbound response.
4. Executable code is injected into JSON structural keys.
5. poisoned_instruction or equivalent bypass attempt is detected.
6. Gemini output sets canon_claim=true.
7. Gemini output returns non-empty commands.
8. Gemini output returns non-empty live_access_references.
9. Strict mode receives non-empty architecture_suggestions.
```

## Privacy levels

```text
PUBLIC_SAFE = redacted/public-safe material only.
STRICT_REDACTION = private-derived material after deterministic redaction.
INTERNAL_BHK = private/internal working material allowed only inside approved Runner/server environment.
```

No raw private material may be copied from INTERNAL_BHK packets into public GitHub.

## Universal usage pattern

```text
Skeleton skill or project task
-> ChatGPT builds Intake Packet
-> workflow-gate / privacy gate confirms safe route
-> Runner validates packet
-> Adapter scans/redacts and uses mock mode by default
-> Adapter may call Gemini only when live mode is explicitly enabled in Runner environment
-> Adapter validates Gemini output fail-closed
-> Runner returns structured output packet to ChatGPT
-> ChatGPT synthesizes recommendation
-> Oleksii approves if needed
```

## Tool relationship

Gemini may support Antigravity, NotebookLM, and Google services indirectly through the Runner-mediated workflow.

```text
Antigravity = private implementation/code workbench.
NotebookLM = private evidence notebook over uploaded sources and generated summaries.
Google Drive/Sheets/Docs = private source and review artifact surfaces.
Gemini = stateless auditor/analyst over packets prepared by Runner.
```

Gemini must not become a hidden executor or canon writer.

## Canon rule

```text
Gemini output is evidence, not canon.
NotebookLM output is evidence, not canon.
Antigravity output is implementation evidence, not canon.
Only ChatGPT/Skeleton + Oleksii approval can promote reviewed results to canon/workflow status.
```

## Construction Takeoff consumer example

For Construction Takeoff / Aufmaß, the bridge may be used as:

```text
DXF/PDF/IFC/scans
-> local parser / private DB
-> workbook + review tables
-> Gemini Intake Packet with confirmed_canon, evidence, draft_artifact, exact_questions
-> Gemini anomaly/consistency review
-> Runner output packet
-> ChatGPT/Skeleton synthesis
-> Oleksii review
```

Gemini may review parser strategy, anomalies, cross-check conflicts, and table consistency. It must not be treated as the geometry source of record or final quantity authority.

## Definition of done

This bridge remains LIKELY_NEEDS_REVIEW until:

```text
- public bridge protocol exists;
- adapter runner task exists;
- strict schemas are implemented in mock mode;
- fail-closed validation is tested;
- secret/PII scanner is tested;
- one private pilot skill uses the bridge safely;
- no private data leaks to public GitHub;
- Oleksii reviews the pilot result.
```
