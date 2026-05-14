from __future__ import annotations

from tools.skeleton_core.adapter_contract import (
    ADAPTER_CONTRACT_VERSION,
    AdapterExecutionResult,
    AdapterTaskPacket,
    FuelPolicy,
    validate_adapter_result,
    validate_task_packet,
)


def valid_packet() -> AdapterTaskPacket:
    return AdapterTaskPacket(
        task_id="adapter-core-v0",
        repo="alanua/jeeves",
        allowed_files=["tools/skeleton_core/adapter_contract.py"],
        forbidden_paths=[".env", ".ssh", "secrets"],
        authority_level="level_2_local_diff",
        risk_level="yellow",
        expected_artifact="diff",
        task_instructions="Create a bounded adapter contract patch.",
        fuel_policy=FuelPolicy(provider="none"),
    )


def valid_result() -> AdapterExecutionResult:
    return AdapterExecutionResult(
        status="success",
        executor="unit-test-adapter",
        changed_files=["tools/skeleton_core/adapter_contract.py"],
        artifact_paths=["artifacts/adapter-core-v0.diff"],
        validation_status="passed",
        risk_flags=[],
    )


def test_valid_task_packet_passes() -> None:
    result = validate_task_packet(valid_packet())

    assert result.contract_version == ADAPTER_CONTRACT_VERSION
    assert result.status == "valid_task_packet"
    assert result.blocked_reasons == []


def test_missing_allowed_files_blocks() -> None:
    packet = valid_packet().model_copy(update={"allowed_files": []})

    result = validate_task_packet(packet)

    assert result.status == "blocked"
    assert "missing_allowed_files" in result.blocked_reasons


def test_missing_task_instructions_blocks() -> None:
    packet = valid_packet().model_copy(update={"task_instructions": ""})

    result = validate_task_packet(packet)

    assert result.status == "blocked"
    assert "missing_task_instructions" in result.blocked_reasons


def test_env_allowed_file_blocks() -> None:
    packet = valid_packet().model_copy(update={"allowed_files": [".env"]})

    result = validate_task_packet(packet)

    assert result.status == "blocked"
    assert "allowed_file_contains_secret_or_control_path" in result.blocked_reasons


def test_directory_shortcut_allowed_file_blocks() -> None:
    packet = valid_packet().model_copy(update={"allowed_files": ["tools/"]})

    result = validate_task_packet(packet)

    assert result.status == "blocked"
    assert "allowed_file_is_directory_shortcut" in result.blocked_reasons


def test_wildcard_allowed_file_blocks() -> None:
    packet = valid_packet().model_copy(update={"allowed_files": ["tools/skeleton_core/*.py"]})

    result = validate_task_packet(packet)

    assert result.status == "blocked"
    assert "allowed_file_contains_wildcard" in result.blocked_reasons


def test_forbidden_path_overlap_blocks() -> None:
    packet = valid_packet().model_copy(
        update={"forbidden_paths": ["tools/skeleton_core/adapter_contract.py"]}
    )

    result = validate_task_packet(packet)

    assert result.status == "blocked"
    assert "allowed_file_overlaps_forbidden_path" in result.blocked_reasons


def test_openrouter_fuel_without_max_usd_blocks() -> None:
    packet = valid_packet().model_copy(
        update={
            "fuel_policy": FuelPolicy(
                provider="openrouter",
                model="deepseek/deepseek-v4-flash:free",
                max_usd=None,
            )
        }
    )

    result = validate_task_packet(packet)

    assert result.status == "blocked"
    assert "fuel_max_usd_missing" in result.blocked_reasons


def test_valid_adapter_result_passes() -> None:
    result = validate_adapter_result(valid_packet(), valid_result())

    assert result.status == "valid_adapter_result"
    assert result.blocked_reasons == []


def test_changed_file_outside_allowed_scope_blocks() -> None:
    adapter_result = valid_result().model_copy(
        update={"changed_files": ["tools/skeleton_core/other.py"]}
    )

    result = validate_adapter_result(valid_packet(), adapter_result)

    assert result.status == "blocked"
    assert "changed_file_outside_allowed_scope" in result.blocked_reasons


def test_success_without_artifact_blocks() -> None:
    adapter_result = valid_result().model_copy(update={"artifact_paths": []})

    result = validate_adapter_result(valid_packet(), adapter_result)

    assert result.status == "blocked"
    assert "success_without_artifact" in result.blocked_reasons


def test_blocking_risk_flag_blocks() -> None:
    adapter_result = valid_result().model_copy(update={"risk_flags": ["secret"]})

    result = validate_adapter_result(valid_packet(), adapter_result)

    assert result.status == "blocked"
    assert "blocking_risk_flag_present" in result.blocked_reasons


def test_level_5_forbidden_blocks() -> None:
    packet = valid_packet().model_copy(update={"authority_level": "level_5_forbidden"})

    result = validate_task_packet(packet)

    assert result.status == "blocked"
    assert "authority_level_forbidden" in result.blocked_reasons
