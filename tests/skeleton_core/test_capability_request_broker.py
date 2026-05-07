from tools.skeleton_core.capability_request_broker import (
    CapabilityRequestInput,
    build_capability_request,
)


def test_ready_capability_request() -> None:
    result = build_capability_request(
        CapabilityRequestInput(
            project="bauclock",
            repository="alanua/bauclock",
            source_issue=22,
            blocker_or_need="Need to reduce manual GitHub Actions report work.",
            manual_steps_repeated=["Read Actions run", "Write issue report"],
            desired_capability="github-actions-runner-control",
            safety_constraints=["no merge", "no deploy", "no secrets"],
            evidence=["BauClock #22", "BauClock #45"],
        )
    )

    assert result.status == "capability_request_ready"
    assert result.capability_name == "github-actions-runner-control"
    assert result.risk_level == "YELLOW"
    assert result.merge_allowed is False
    assert result.deploy_allowed is False
    assert "github-actions-runner-control" in result.recommended_skeleton_issue_title
    assert "No GitHub writes from CLI in v1" in result.recommended_skeleton_issue_body


def test_existing_capability_request() -> None:
    result = build_capability_request(
        CapabilityRequestInput(
            project="bauclock",
            repository="alanua/bauclock",
            source_issue=22,
            blocker_or_need="Need to use existing runner-env-check.",
            manual_steps_repeated=["Check runner manually"],
            desired_capability="runner-env-check",
            existing_capabilities=["runner-env-check"],
            evidence=["Capability already merged"],
        )
    )

    assert result.status == "capability_already_exists"
    assert result.next_safe_step == "Update the project workflow to use the existing Skeleton capability."
    assert result.merge_allowed is False
    assert result.deploy_allowed is False


def test_unsafe_capability_request_blocks() -> None:
    result = build_capability_request(
        CapabilityRequestInput(
            project="bauclock",
            repository="alanua/bauclock",
            source_issue=22,
            blocker_or_need="Need live executor that can merge deploy and read .env token.",
            manual_steps_repeated=["Manual deploy"],
            desired_capability="live-executor",
            evidence=["unsafe fixture"],
        )
    )

    assert result.status == "blocked_unsafe_capability"
    assert result.risk_level == "RED"
    assert result.allowed_scope == []
    assert result.acceptance_criteria == []
    assert result.recommended_skeleton_issue_body == ""
    assert result.merge_allowed is False
    assert result.deploy_allowed is False
    assert result.blockers


def test_unknown_capability_request_needs_review() -> None:
    result = build_capability_request(
        CapabilityRequestInput(
            project="bauclock",
            blocker_or_need="Need some automation.",
            desired_capability="",
        )
    )

    assert result.status == "unknown_needs_review"
    assert result.risk_level == "UNKNOWN"
    assert result.merge_allowed is False
    assert result.deploy_allowed is False
