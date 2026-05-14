from __future__ import annotations

from tools.skeleton_core.adapter_contract import AdapterTaskPacket, FuelPolicy
from tools.skeleton_core.openhands_adapter import (
    OPENHANDS_ADAPTER_VERSION,
    OpenHandsAdapterConfig,
    build_openhands_command,
    build_openhands_env,
    build_openhands_result,
    build_openhands_task_text,
    prepare_openhands_task,
)


def valid_packet() -> AdapterTaskPacket:
    return AdapterTaskPacket(
        task_id="openhands-adapter-v0",
        repo="alanua/jeeves",
        allowed_files=["tools/skeleton_core/openhands_adapter.py"],
        forbidden_paths=[".env", ".git", ".ssh", "secrets", "tokens"],
        authority_level="level_2_local_diff",
        risk_level="yellow",
        expected_artifact="diff",
        fuel_policy=FuelPolicy(
            provider="openrouter",
            model="deepseek/deepseek-v4-flash:free",
            max_usd=1.0,
        ),
    )


def test_valid_packet_prepares_task() -> None:
    prepared = prepare_openhands_task(valid_packet(), "/tmp/task.md")

    assert prepared.adapter_version == OPENHANDS_ADAPTER_VERSION
    assert prepared.task_validation.status == "valid_task_packet"
    assert prepared.command[-2:] == ["-f", "/tmp/task.md"]


def test_invalid_packet_returns_blocked_task_validation() -> None:
    packet = valid_packet().model_copy(update={"allowed_files": []})

    prepared = prepare_openhands_task(packet, "/tmp/task.md")

    assert prepared.task_validation.status == "blocked"
    assert "missing_allowed_files" in prepared.task_validation.blocked_reasons


def test_task_text_contains_scope_and_boundaries() -> None:
    text = build_openhands_task_text(valid_packet())

    assert "tools/skeleton_core/openhands_adapter.py" in text
    assert ".env" in text
    assert "Do not read .env, .git, .ssh" in text
    assert "Do not install packages" in text
    assert "Do not push, merge, deploy" in text


def test_command_is_exact_openhands_command() -> None:
    config = OpenHandsAdapterConfig(executable="/bin/openhands")

    command = build_openhands_command("/tmp/task.md", config)

    assert command == ["/bin/openhands", "--override-with-envs", "-f", "/tmp/task.md"]


def test_env_builder_keeps_secret_out_of_prepared_metadata() -> None:
    config = OpenHandsAdapterConfig(model="test/model", base_url="https://example.test/v1")

    env = build_openhands_env("sk-or-secret-value", config)
    prepared = prepare_openhands_task(valid_packet(), "/tmp/task.md", config)

    assert env["LLM_API_KEY"] == "sk-or-secret-value"
    assert env["LLM_MODEL"] == "test/model"
    assert env["LLM_BASE_URL"] == "https://example.test/v1"
    assert "OPENHANDS_SUPPRESS_BANNER" in env
    assert "LLM_API_KEY" in prepared.env_keys
    assert "sk-or-secret-value" not in str(prepared.model_dump())


def test_result_builder_validates_success_result() -> None:
    result = build_openhands_result(
        valid_packet(),
        executor_status="success",
        changed_files=["tools/skeleton_core/openhands_adapter.py"],
        artifact_paths=["artifacts/openhands-adapter-v0.diff"],
        validation_status="passed",
        risk_flags=[],
        stop_reason="done",
    )

    assert result.result.status == "success"
    assert result.result_validation.status == "valid_adapter_result"


def test_result_builder_blocks_changed_file_outside_allowed_scope() -> None:
    result = build_openhands_result(
        valid_packet(),
        executor_status="success",
        changed_files=["tools/skeleton_core/other.py"],
        artifact_paths=["artifacts/openhands-adapter-v0.diff"],
        validation_status="passed",
        risk_flags=[],
        stop_reason="done",
    )

    assert result.result_validation.status == "blocked"
    assert "changed_file_outside_allowed_scope" in result.result_validation.blocked_reasons


def test_result_builder_blocks_secret_risk_flag() -> None:
    result = build_openhands_result(
        valid_packet(),
        executor_status="success",
        changed_files=["tools/skeleton_core/openhands_adapter.py"],
        artifact_paths=["artifacts/openhands-adapter-v0.diff"],
        validation_status="passed",
        risk_flags=["secret"],
        stop_reason="done",
    )

    assert result.result_validation.status == "blocked"
    assert "blocking_risk_flag_present" in result.result_validation.blocked_reasons


def test_result_builder_blocks_success_without_artifact() -> None:
    result = build_openhands_result(
        valid_packet(),
        executor_status="success",
        changed_files=["tools/skeleton_core/openhands_adapter.py"],
        artifact_paths=[],
        validation_status="passed",
        risk_flags=[],
        stop_reason="done",
    )

    assert result.result_validation.status == "blocked"
    assert "success_without_artifact" in result.result_validation.blocked_reasons
