from pathlib import Path

from tools.skeleton_core.gemini_auditor_adapter import (
    GeminiAuditorInput,
    GeminiAuditorOutput,
    run_adapter,
    run_adapter_from_json,
    validate_output,
)


def _read_fixture(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _packet(mode: str = "mock") -> GeminiAuditorInput:
    return GeminiAuditorInput(
        schema_version="gemini_adapter.input.v1",
        packet_id=f"test-{mode}",
        objective="Review synthetic packet.",
        mode=mode,
        privacy_level="PUBLIC_SAFE",
        confirmed_canon="Gemini cannot execute commands or update canon.",
        evidence="Synthetic public-safe evidence.",
        draft_artifact="Synthetic draft.",
        exact_questions=["Is this safe?"],
        forbidden_actions=["do not execute commands"],
    )


def test_mock_public_safe_accepts() -> None:
    result = run_adapter(_packet())

    assert result.status == "mock_accept"
    assert result.output is not None
    assert result.output.canon_claim is False
    assert result.output.commands == []
    assert result.merge_allowed is False
    assert result.deploy_allowed is False


def test_live_disabled_blocks_before_key_check(monkeypatch) -> None:
    monkeypatch.delenv("GEMINI_API_LIVE_MODE", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    result = run_adapter(_packet("live"))

    assert result.status == "blocked_live_mode_disabled"
    assert result.output is None


def test_live_missing_key_blocks_when_live_flag_enabled(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_API_LIVE_MODE", "true")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    result = run_adapter(_packet("live"))

    assert result.status == "blocked_live_mode_missing_key"
    assert result.output is None


def test_secret_blocks() -> None:
    raw_json = """
    {
      "schema_version": "gemini_adapter.input.v1",
      "packet_id": "test-secret",
      "objective": "Review leaked secret.",
      "mode": "mock",
      "privacy_level": "PUBLIC_SAFE",
      "confirmed_canon": "No secrets.",
      "evidence": "api_key=SHOULD_NOT_PASS",
      "draft_artifact": "Synthetic draft.",
      "exact_questions": ["Should this block?"],
      "forbidden_actions": ["do not execute commands"]
    }
    """

    result = run_adapter_from_json(raw_json)

    assert result.status == "blocked_secret_or_pii"
    assert "generic_api_key" in result.security_flags


def test_schema_validation_blocks_extra_field() -> None:
    raw_json = """
    {
      "schema_version": "gemini_adapter.input.v1",
      "packet_id": "test-extra",
      "objective": "Review synthetic packet.",
      "mode": "mock",
      "privacy_level": "PUBLIC_SAFE",
      "confirmed_canon": "No commands.",
      "evidence": "Synthetic evidence.",
      "draft_artifact": "Synthetic draft.",
      "exact_questions": ["Is this safe?"],
      "forbidden_actions": ["do not execute commands"],
      "unexpected": "blocked"
    }
    """

    result = run_adapter_from_json(raw_json)

    assert result.status == "blocked_schema_validation"


def test_output_validation_blocks_forbidden_fields() -> None:
    output = GeminiAuditorOutput(
        schema_version="gemini-auditor-mock-output-v0.1",
        packet_id="test-output",
        decision="accept",
        security_flags=[],
        summary="Unsafe output.",
        rationale=["bad"],
        blocked_instruction="",
        exoskeleton_note="",
        canon_claim=True,
        commands=["run something"],
        architecture_suggestions=["suggestion"],
        live_access_references=["live ref"],
    )

    errors = validate_output(output, strict_mode=True)

    assert "canon_claim_must_be_false" in errors
    assert "commands_must_be_empty" in errors
    assert "live_access_references_must_be_empty" in errors
    assert "architecture_suggestions_must_be_empty_in_strict_mode" in errors


def test_fixture_public_safe_accepts() -> None:
    result = run_adapter_from_json(
        _read_fixture("tests/fixtures/gemini_auditor_input_public_safe.json")
    )

    assert result.status == "mock_accept"


def test_fixture_live_disabled_blocks(monkeypatch) -> None:
    monkeypatch.delenv("GEMINI_API_LIVE_MODE", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    result = run_adapter_from_json(
        _read_fixture("tests/fixtures/gemini_auditor_input_live_missing_key.json")
    )

    assert result.status == "blocked_live_mode_disabled"


def test_fixture_live_missing_key_blocks_when_live_flag_enabled(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_API_LIVE_MODE", "true")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    result = run_adapter_from_json(
        _read_fixture("tests/fixtures/gemini_auditor_input_live_missing_key.json")
    )

    assert result.status == "blocked_live_mode_missing_key"


def test_fixture_secret_blocks() -> None:
    result = run_adapter_from_json(
        _read_fixture("tests/fixtures/gemini_auditor_input_secret_blocked.json")
    )

    assert result.status == "blocked_secret_or_pii"
