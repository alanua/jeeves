"""Mock-first Gemini auditor adapter for Skeleton runner workflows.

Direct REST bridge:
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent

Default behavior:
- mock mode by default
- live mode only with GEMINI_API_LIVE_MODE=true
- API key from GEMINI_API_KEY or GOOGLE_API_KEY
- no .env reads
- no command execution
- no canon writes
"""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

InputMode = Literal["mock", "live"]
PrivacyLevel = Literal["PUBLIC_SAFE", "STRICT_REDACTION", "INTERNAL_BHK"]
Decision = Literal["accept", "block", "revise"]

AdapterStatus = Literal[
    "mock_accept",
    "mock_revise",
    "mock_block",
    "live_accept",
    "live_revise",
    "live_block",
    "blocked_schema_validation",
    "blocked_secret_or_pii",
    "blocked_live_mode_disabled",
    "blocked_live_mode_missing_key",
    "blocked_output_validation",
    "blocked_live_transport_error",
    "unknown_needs_review",
]

OUTPUT_SCHEMA_VERSION = "gemini-auditor-mock-output-v0.1"
DEFAULT_MODEL = "gemini-2.5-flash"
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"

SECRET_PATTERNS = {
    "gemini_api_key": r"AIza[0-9A-Za-z_\-]{20,}",
    "generic_api_key": (
        r"(?i)\b(api[_-]?key|secret|token|password)\b" r"\s*[:=]\s*['\"]?[^ \n\r\t,'\"]{8,}"
    ),
    "private_key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
}

PII_PATTERNS = {
    "email_address": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
}

POISON_PATTERNS = {
    "poisoned_instruction": (
        r"(?i)poisoned_instruction|ignore previous|bypass.+control|disable.+gate"
    ),
    "structural_code_injection": (
        r"(?i)__proto__|constructor\s*:|import\s+os|subprocess|eval\(|exec\("
    ),
}


class GeminiAuditorInput(BaseModel):
    """Strict input packet sent by the runner toward the adapter."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["gemini_adapter.input.v1"]
    packet_id: str
    objective: str
    mode: InputMode = "mock"
    privacy_level: PrivacyLevel = "PUBLIC_SAFE"
    confirmed_canon: str
    evidence: str
    draft_artifact: str
    exact_questions: list[str] = Field(default_factory=list)
    forbidden_actions: list[str] = Field(default_factory=list)


class GeminiAuditorOutput(BaseModel):
    """Output packet returned by Gemini/mock through the adapter.

    Gemini can add extra fields. The adapter ignores extras and then enforces
    authority and safety invariants.
    """

    model_config = ConfigDict(extra="ignore")

    schema_version: Literal["gemini-auditor-mock-output-v0.1"] = OUTPUT_SCHEMA_VERSION
    packet_id: str
    decision: Decision
    security_flags: list[str] = Field(default_factory=list)
    summary: str
    rationale: list[str] = Field(default_factory=list)
    blocked_instruction: str = ""
    exoskeleton_note: str = ""
    canon_claim: bool = False
    commands: list[str] = Field(default_factory=list)
    architecture_suggestions: list[str] = Field(default_factory=list)
    live_access_references: list[str] = Field(default_factory=list)


class GeminiAdapterPacket(BaseModel):
    """Adapter result returned to the runner/ChatGPT side."""

    model_config = ConfigDict(extra="forbid")

    status: AdapterStatus
    packet_id: str = ""
    mode: InputMode = "mock"
    model: str = DEFAULT_MODEL
    output: GeminiAuditorOutput | None = None
    blocked_reasons: list[str] = Field(default_factory=list)
    security_flags: list[str] = Field(default_factory=list)
    merge_allowed: bool = False
    deploy_allowed: bool = False
    next_safe_step: str


def scan_sensitive_text(text: str) -> list[str]:
    """Return matched secret/PII/poison flags for text."""
    flags: list[str] = []
    for name, pattern in {**SECRET_PATTERNS, **PII_PATTERNS, **POISON_PATTERNS}.items():
        if re.search(pattern, text):
            flags.append(name)
    return sorted(set(flags))


def _packet_text(packet: GeminiAuditorInput) -> str:
    return json.dumps(packet.model_dump(mode="json"), ensure_ascii=False, sort_keys=True)


def _blocked(
    status: AdapterStatus,
    *,
    packet_id: str = "",
    mode: InputMode = "mock",
    model: str = DEFAULT_MODEL,
    reasons: list[str] | None = None,
    flags: list[str] | None = None,
) -> GeminiAdapterPacket:
    return GeminiAdapterPacket(
        status=status,
        packet_id=packet_id,
        mode=mode,
        model=model,
        blocked_reasons=reasons or [],
        security_flags=flags or [],
        merge_allowed=False,
        deploy_allowed=False,
        next_safe_step="Stop and fix the Gemini auditor packet before continuing.",
    )


def validate_output(output: GeminiAuditorOutput, *, strict_mode: bool) -> list[str]:
    """Validate fail-closed output invariants."""
    reasons: list[str] = []

    if output.canon_claim:
        reasons.append("canon_claim_must_be_false")
    if output.commands:
        reasons.append("commands_must_be_empty")
    if output.live_access_references:
        reasons.append("live_access_references_must_be_empty")
    if strict_mode and output.architecture_suggestions:
        reasons.append("architecture_suggestions_must_be_empty_in_strict_mode")

    inbound_flags = scan_sensitive_text(output.model_dump_json())
    reasons.extend(f"inbound_{flag}" for flag in inbound_flags)

    return sorted(set(reasons))


def build_mock_output(packet: GeminiAuditorInput) -> GeminiAuditorOutput:
    """Create deterministic mock output without calling Gemini."""
    decision: Decision = "accept"
    if packet.privacy_level != "PUBLIC_SAFE" or not packet.exact_questions:
        decision = "revise"

    return GeminiAuditorOutput(
        schema_version=OUTPUT_SCHEMA_VERSION,
        packet_id=packet.packet_id,
        decision=decision,
        security_flags=[],
        summary="Mock Gemini auditor response generated without live API access.",
        rationale=[
            "Input packet passed strict schema validation.",
            "No outbound secret or PII pattern was detected.",
            "Mock mode preserves fail-closed development without network access.",
        ],
        blocked_instruction="",
        exoskeleton_note="Treat this as adapter validation evidence, not canon.",
        canon_claim=False,
        commands=[],
        architecture_suggestions=[],
        live_access_references=[],
    )


def _api_key_from_env() -> str | None:
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


def _live_mode_enabled() -> bool:
    return os.environ.get("GEMINI_API_LIVE_MODE", "").casefold() == "true"


def _normalize_model_name(model: str) -> str:
    cleaned = model.strip()
    if cleaned.startswith("models/"):
        cleaned = cleaned.removeprefix("models/")
    return cleaned or DEFAULT_MODEL


def _live_system_text() -> str:
    return (
        "You are Gemini Auditor Node inside Skeleton. "
        "You are stateless evidence source only. "
        "You are not manager, executor, canon writer, merger, or deployer. "
        "Return only a JSON object. "
        "Do not wrap the JSON in Markdown. "
        "Do not return commands. "
        "Do not claim canon. "
        "Do not include live access references."
    )


def _live_user_text(packet: GeminiAuditorInput) -> str:
    return (
        "Audit this Skeleton adapter packet.\n\n"
        "Return JSON with this shape:\n"
        "{\n"
        '  "schema_version": "gemini-auditor-mock-output-v0.1",\n'
        '  "packet_id": "string",\n'
        '  "decision": "accept|block|revise",\n'
        '  "security_flags": [],\n'
        '  "summary": "string",\n'
        '  "rationale": ["string"],\n'
        '  "blocked_instruction": "",\n'
        '  "exoskeleton_note": "string",\n'
        '  "canon_claim": false,\n'
        '  "commands": [],\n'
        '  "architecture_suggestions": [],\n'
        '  "live_access_references": []\n'
        "}\n\n"
        f"Input packet:\n{packet.model_dump_json(indent=2)}"
    )


def _build_gemini_request_body(packet: GeminiAuditorInput) -> dict[str, Any]:
    """Build Google-compliant generateContent payload."""
    return {
        "systemInstruction": {
            "parts": [
                {
                    "text": _live_system_text(),
                }
            ]
        },
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": _live_user_text(packet),
                    }
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0,
            "topP": 0.1,
            "topK": 1,
            "responseMimeType": "application/json",
        },
    }


def _strip_json_fence(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```json"):
        stripped = stripped.removeprefix("```json").strip()
    elif stripped.startswith("```"):
        stripped = stripped.removeprefix("```").strip()
    if stripped.endswith("```"):
        stripped = stripped[: -len("```")].strip()
    return stripped.strip()


def _json_object_from_text(text: str) -> dict[str, Any]:
    stripped = _strip_json_fence(text)
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start < 0 or end <= start:
            raise
        parsed = json.loads(stripped[start : end + 1])

    if not isinstance(parsed, dict):
        raise ValueError("gemini_output_must_be_json_object")
    return parsed


def _extract_text_from_gemini_response(raw: dict[str, Any]) -> str:
    candidates = raw.get("candidates") or []
    if not candidates:
        raise ValueError(f"missing_candidates: {json.dumps(raw, ensure_ascii=False)[:1000]}")

    content = candidates[0].get("content") or {}
    parts = content.get("parts") or []
    texts = [part.get("text", "") for part in parts if isinstance(part, dict)]
    text = "".join(texts).strip()

    if not text:
        raise ValueError(f"missing_text: {json.dumps(raw, ensure_ascii=False)[:1000]}")

    return _strip_json_fence(text)


def _coerce_output_mapping(raw_output: dict[str, Any], *, packet_id: str) -> dict[str, Any]:
    """Add safe defaults before Pydantic validation."""
    output = dict(raw_output)
    output.setdefault("schema_version", OUTPUT_SCHEMA_VERSION)
    output.setdefault("packet_id", packet_id)
    output.setdefault("decision", "revise")
    output.setdefault("security_flags", [])
    output.setdefault("summary", "Gemini returned a partial JSON audit packet.")
    output.setdefault("rationale", [])
    output.setdefault("blocked_instruction", "")
    output.setdefault("exoskeleton_note", "Treat this as adapter evidence, not canon.")
    output.setdefault("canon_claim", False)
    output.setdefault("commands", [])
    output.setdefault("architecture_suggestions", [])
    output.setdefault("live_access_references", [])
    return output


def _read_http_error_body(exc: urllib.error.HTTPError) -> str:
    try:
        body = exc.read().decode("utf-8", errors="replace")
    except Exception:
        body = ""
    return body[:2000]


def call_live_gemini(packet: GeminiAuditorInput, *, model: str) -> GeminiAuditorOutput:
    """Call Gemini REST API with stdlib urllib and validate JSON response."""
    api_key = _api_key_from_env()
    if not api_key:
        raise RuntimeError("missing_gemini_api_key")

    model_name = _normalize_model_name(model)
    endpoint = (
        f"{GEMINI_API_BASE}/models/" f"{urllib.parse.quote(model_name, safe='')}:generateContent"
    )

    body = json.dumps(_build_gemini_request_body(packet)).encode("utf-8")

    request = urllib.request.Request(
        endpoint,
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw_response = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        error_body = _read_http_error_body(exc)
        raise RuntimeError(f"http_{exc.code}_from_gemini_generateContent: {error_body}") from exc

    output_text = _extract_text_from_gemini_response(raw_response)
    output_mapping = _coerce_output_mapping(
        _json_object_from_text(output_text),
        packet_id=packet.packet_id,
    )
    return GeminiAuditorOutput.model_validate(output_mapping)


def run_adapter(packet: GeminiAuditorInput, *, model: str = DEFAULT_MODEL) -> GeminiAdapterPacket:
    """Run mock-first Gemini auditor adapter."""
    model_name = _normalize_model_name(model)

    flags = scan_sensitive_text(_packet_text(packet))
    if flags:
        return _blocked(
            "blocked_secret_or_pii",
            packet_id=packet.packet_id,
            mode=packet.mode,
            model=model_name,
            reasons=[f"outbound_{flag}" for flag in flags],
            flags=flags,
        )

    if packet.mode == "live" and not _live_mode_enabled():
        return _blocked(
            "blocked_live_mode_disabled",
            packet_id=packet.packet_id,
            mode=packet.mode,
            model=model_name,
            reasons=["GEMINI_API_LIVE_MODE=true is required for live mode."],
        )

    if packet.mode == "live" and not _api_key_from_env():
        return _blocked(
            "blocked_live_mode_missing_key",
            packet_id=packet.packet_id,
            mode=packet.mode,
            model=model_name,
            reasons=["GEMINI_API_KEY or GOOGLE_API_KEY is required for live mode."],
        )

    try:
        output = (
            build_mock_output(packet)
            if packet.mode == "mock"
            else call_live_gemini(packet, model=model_name)
        )
    except (RuntimeError, urllib.error.URLError, TimeoutError) as exc:
        return _blocked(
            "blocked_live_transport_error",
            packet_id=packet.packet_id,
            mode=packet.mode,
            model=model_name,
            reasons=[str(exc)],
        )
    except (ValidationError, ValueError, json.JSONDecodeError) as exc:
        return _blocked(
            "blocked_output_validation",
            packet_id=packet.packet_id,
            mode=packet.mode,
            model=model_name,
            reasons=[str(exc)],
        )

    strict_mode = packet.privacy_level == "STRICT_REDACTION"
    output_errors = validate_output(output, strict_mode=strict_mode)
    if output_errors:
        return _blocked(
            "blocked_output_validation",
            packet_id=packet.packet_id,
            mode=packet.mode,
            model=model_name,
            reasons=output_errors,
        )

    prefix = "mock" if packet.mode == "mock" else "live"
    status: AdapterStatus = f"{prefix}_{output.decision}"  # type: ignore[assignment]

    return GeminiAdapterPacket(
        status=status,
        packet_id=packet.packet_id,
        mode=packet.mode,
        model=model_name,
        output=output,
        blocked_reasons=[],
        security_flags=output.security_flags,
        merge_allowed=False,
        deploy_allowed=False,
        next_safe_step="Return this packet to ChatGPT/Skeleton for synthesis and review.",
    )


def run_adapter_from_json(raw_json: str, *, model: str = DEFAULT_MODEL) -> GeminiAdapterPacket:
    """Validate JSON input and run the adapter."""
    try:
        packet = GeminiAuditorInput.model_validate_json(raw_json)
    except ValidationError as exc:
        return _blocked("blocked_schema_validation", reasons=[exc.json()])
    return run_adapter(packet, model=model)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Gemini auditor adapter.")
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to input packet JSON",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Gemini model name")
    args = parser.parse_args(argv)

    result = run_adapter_from_json(
        args.input.read_text(encoding="utf-8"),
        model=args.model,
    )
    print(
        json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2),
        flush=True,
    )
    return 0 if not result.status.startswith("blocked_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
