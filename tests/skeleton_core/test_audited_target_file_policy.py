from __future__ import annotations

from copy import deepcopy

from tools.skeleton_core.audited_target_file_policy import (
    POLICY_NAME,
    validate_audited_target_file_policy,
)


def valid_input() -> dict:
    return {
        "source_issue": 170,
        "source_repo": "alanua/jeeves",
        "labels": [
            "agent:task",
            "agent:audited",
            "agent:plan-ready",
            "risk:yellow",
            "runner:any",
        ],
        "audit_status": "accepted",
        "audit_blocked_reasons": [],
        "security_flags": [],
        "merge_allowed": False,
        "deploy_allowed": False,
        "human_review_required": True,
        "packet": {
            "id": 170,
            "type": "pr_creation",
            "command": "python -m tools.skeleton_core.cli create-pr",
            "safety_level": "green",
            "pr_creation_allowed": True,
            "target_files": [
                "tools/skeleton_core/project_audit_route.py",
                "tools/skeleton_core/cli.py",
                "tests/skeleton_core/test_project_audit_route.py",
            ],
            "pr_title": "Add generic project audit route",
            "pr_body": "Review required.",
        },
        "requested_files": [
            "tools/skeleton_core/project_audit_route.py",
            "tools/skeleton_core/cli.py",
            "tests/skeleton_core/test_project_audit_route.py",
        ],
        "validation_commands": [
            "python -m pytest tests/skeleton_core/test_project_audit_route.py",
        ],
    }


def test_issue_170_style_packet_is_valid() -> None:
    result = validate_audited_target_file_policy(valid_input())

    assert result.policy == POLICY_NAME
    assert result.status == "valid_plan_packet"
    assert result.blocked_reasons == []


def test_missing_audited_label_blocks() -> None:
    data = valid_input()
    data["labels"].remove("agent:audited")

    result = validate_audited_target_file_policy(data)

    assert result.status == "blocked"
    assert "missing_agent_audited" in result.blocked_reasons


def test_missing_plan_ready_label_blocks() -> None:
    data = valid_input()
    data["labels"].remove("agent:plan-ready")

    result = validate_audited_target_file_policy(data)

    assert result.status == "blocked"
    assert "missing_agent_plan_ready" in result.blocked_reasons


def test_missing_runner_label_blocks() -> None:
    data = valid_input()
    data["labels"].remove("runner:any")

    result = validate_audited_target_file_policy(data)

    assert result.status == "blocked"
    assert "missing_runner_label" in result.blocked_reasons


def test_packet_issue_mismatch_blocks() -> None:
    data = valid_input()
    data["packet"]["id"] = 171

    result = validate_audited_target_file_policy(data)

    assert result.status == "blocked"
    assert "packet_issue_mismatch" in result.blocked_reasons


def test_duplicate_target_files_block() -> None:
    data = valid_input()
    first = data["packet"]["target_files"][0]
    data["packet"]["target_files"].append(first)

    result = validate_audited_target_file_policy(data)

    assert result.status == "blocked"
    assert "duplicate_target_files" in result.blocked_reasons


def test_wildcard_target_blocks() -> None:
    data = valid_input()
    data["packet"]["target_files"] = ["tools/skeleton_core/*.py"]
    data["requested_files"] = ["tools/skeleton_core/*.py"]

    result = validate_audited_target_file_policy(data)

    assert result.status == "blocked"
    assert "wildcard_target_file" in result.blocked_reasons


def test_dot_target_blocks() -> None:
    data = valid_input()
    data["packet"]["target_files"] = ["."]
    data["requested_files"] = ["."]

    result = validate_audited_target_file_policy(data)

    assert result.status == "blocked"
    assert "dot_or_root_target_file" in result.blocked_reasons


def test_directory_shortcut_target_blocks() -> None:
    data = valid_input()
    data["packet"]["target_files"] = ["tests/"]
    data["requested_files"] = ["tests/"]

    result = validate_audited_target_file_policy(data)

    assert result.status == "blocked"
    assert "directory_shortcut_target_file" in result.blocked_reasons


def test_unlisted_requested_file_blocks() -> None:
    data = valid_input()
    data["requested_files"] = ["tools/skeleton_core/not_listed.py"]

    result = validate_audited_target_file_policy(data)

    assert result.status == "blocked"
    assert "requested_file_not_in_target_files" in result.blocked_reasons


def test_unsafe_validation_command_blocks() -> None:
    data = valid_input()
    data["validation_commands"] = [
        "python -m pytest tests/skeleton_core/test_project_audit_route.py && git status",
    ]

    result = validate_audited_target_file_policy(data)

    assert result.status == "blocked"
    assert "unsafe_validation_command" in result.blocked_reasons


def test_merge_allowed_true_blocks() -> None:
    data = valid_input()
    data["merge_allowed"] = True

    result = validate_audited_target_file_policy(data)

    assert result.status == "blocked"
    assert "merge_allowed_true" in result.blocked_reasons


def test_deploy_allowed_true_blocks() -> None:
    data = valid_input()
    data["deploy_allowed"] = True

    result = validate_audited_target_file_policy(data)

    assert result.status == "blocked"
    assert "deploy_allowed_true" in result.blocked_reasons


def test_original_fixture_not_mutated_by_copies() -> None:
    data = valid_input()
    copied = deepcopy(data)
    copied["labels"].remove("agent:audited")

    assert "agent:audited" in data["labels"]
