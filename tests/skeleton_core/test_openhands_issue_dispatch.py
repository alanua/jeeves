from __future__ import annotations

import subprocess
from pathlib import Path

from tools.skeleton_core.adapter_contract import AdapterTaskPacket
from tools.skeleton_core.openhands_issue_dispatch import (
    OPENHANDS_ISSUE_DISPATCH_VERSION,
    build_packet_from_issue,
    dispatch_openhands_issue,
    validate_issue_payload,
)
from tools.skeleton_core.openhands_runner_route import (
    OpenHandsRunnerRouteConfig,
    run_openhands_route,
)


def valid_payload(tmp_path: Path) -> dict:
    return {
        "issue_number": 196,
        "repo": "alanua/jeeves",
        "title": "Add OpenHands issue dispatch v0",
        "body": "bounded test payload",
        "labels": [
            "agent:task",
            "agent:audited",
            "agent:plan-ready",
            "runner:openhands",
            "risk:yellow",
        ],
        "allowed_files": ["tools/skeleton_core/openhands_issue_dispatch.py"],
        "expected_artifact": "diff",
        "authority_level": "level_2_local_diff",
        "risk_level": "yellow",
        "fuel_provider": "openrouter",
        "fuel_model": "deepseek/deepseek-v4-flash:free",
        "fuel_max_usd": 1.0,
    }


def test_valid_issue_payload_passes(tmp_path: Path) -> None:
    assert validate_issue_payload(valid_payload(tmp_path)) == []


def test_missing_required_label_blocks(tmp_path: Path) -> None:
    payload = valid_payload(tmp_path)
    payload["labels"].remove("agent:audited")

    blocked = validate_issue_payload(payload)

    assert "missing_label:agent:audited" in blocked


def test_forbidden_running_label_blocks(tmp_path: Path) -> None:
    payload = valid_payload(tmp_path)
    payload["labels"].append("agent:running")

    blocked = validate_issue_payload(payload)

    assert "forbidden_label:agent:running" in blocked


def test_build_packet_from_issue_maps_scope_and_fuel(tmp_path: Path) -> None:
    packet = build_packet_from_issue(valid_payload(tmp_path))

    assert packet.task_id == "issue-196-openhands"
    assert packet.repo == "alanua/jeeves"
    assert packet.allowed_files == ["tools/skeleton_core/openhands_issue_dispatch.py"]
    assert ".env" in packet.forbidden_paths
    assert packet.fuel_policy.provider == "openrouter"
    assert packet.fuel_policy.max_usd == 1.0


def test_dispatch_blocks_invalid_issue_before_route(tmp_path: Path) -> None:
    payload = valid_payload(tmp_path)
    payload["allowed_files"] = []
    route_called = False

    def route(packet: AdapterTaskPacket):
        nonlocal route_called
        route_called = True
        raise AssertionError("route must not be called")

    report = dispatch_openhands_issue(payload, route=route)

    assert report.status == "blocked"
    assert "missing_allowed_files" in report.blocked_reasons
    assert route_called is False
    assert report.route_report is None


def test_dispatch_calls_injected_route_for_valid_issue(tmp_path: Path) -> None:
    secret_file = tmp_path / "openrouter.env"
    task_file = tmp_path / "task.md"
    secret_file.write_text("OPENROUTER_API_KEY='sk-or-test-value'\n", encoding="utf-8")

    def fake_runner(
        command: list[str], env: dict[str, str], timeout_seconds: int
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    def route(packet: AdapterTaskPacket):
        return run_openhands_route(
            packet,
            config=OpenHandsRunnerRouteConfig(task_file=task_file, secret_file=secret_file),
            runner=fake_runner,
            changed_files=["tools/skeleton_core/openhands_issue_dispatch.py"],
            artifact_paths=["artifacts/openhands-issue-dispatch-v0.diff"],
        )

    report = dispatch_openhands_issue(valid_payload(tmp_path), route=route)

    assert report.dispatch_version == OPENHANDS_ISSUE_DISPATCH_VERSION
    assert report.status == "dispatched"
    assert report.packet is not None
    assert report.route_report is not None
    assert report.route_report.result.result_validation.status == "valid_adapter_result"
    assert "sk-or-test-value" not in report.model_dump_json()
