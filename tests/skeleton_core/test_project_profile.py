from tools.skeleton_core.project_profile import (
    ProjectSkeletonProfileInput,
    build_project_skeleton_profile,
)


def test_bauclock_profile_ready_with_missing_skill_signals() -> None:
    result = build_project_skeleton_profile(
        ProjectSkeletonProfileInput(
            project="BauClock",
            type="application",
            default_risk="YELLOW",
            allowed_skeleton_capabilities=[
                "issue-dispatch",
                "runner-command-pack",
                "runner-report-ingest",
                "queue-state",
                "pr-review-gate",
                "branch-recovery",
            ],
            project_needs=["runner-env-check", "migration-risk-gate"],
            forbidden_by_default=["deploy", "server ssh", "production db", "secrets", ".env"],
            runtime_change_requires_explicit_approval=True,
        )
    )

    assert result.profile_status == "ready"
    assert result.project == "BauClock"
    assert result.risk_level == "YELLOW"
    assert result.development_flow == [
        "issue-dispatch",
        "runner-command-pack",
        "runner-report-ingest",
        "pr-review-gate",
        "branch-recovery",
    ]
    assert result.recommended_next_gate == "pr-review-gate"
    assert "runner-env-check" in result.missing_capability_signals
    assert "migration-risk-gate" in result.missing_capability_signals
    assert any("runner-env-check" in item for item in result.recommended_skeleton_skill_backlog)
    assert result.blockers == []
    assert result.merge_allowed is False
    assert result.deploy_allowed is False


def test_skeleton_core_profile_ready_flow() -> None:
    result = build_project_skeleton_profile(
        ProjectSkeletonProfileInput(
            project="Skeleton Core",
            type="skeleton-core",
            default_risk="YELLOW",
            allowed_skeleton_capabilities=[
                "issue-dispatch",
                "runner-command-pack",
                "runner-report-ingest",
                "pr-review-gate",
                "branch-recovery",
                "queue-state",
                "validate-state",
                "handoff-pack",
            ],
            forbidden_by_default=["deploy", "server ssh", "production db", "secrets", ".env"],
        )
    )

    assert result.profile_status == "ready"
    assert result.development_flow == [
        "issue-dispatch",
        "runner-command-pack",
        "runner-report-ingest",
        "pr-review-gate",
        "branch-recovery",
        "queue-state",
        "validate-state",
        "handoff-pack",
    ]
    assert result.missing_capability_signals == []
    assert result.merge_allowed is False
    assert result.deploy_allowed is False


def test_unknown_capability_blocks_profile() -> None:
    result = build_project_skeleton_profile(
        ProjectSkeletonProfileInput(
            project="Unsafe Example",
            type="application",
            default_risk="YELLOW",
            allowed_skeleton_capabilities=["issue-dispatch", "autonomous-deploy"],
            forbidden_by_default=["deploy", "secrets", ".env"],
        )
    )

    assert result.profile_status == "blocked_unknown_capability"
    assert result.development_flow == []
    assert any("autonomous-deploy" in blocker for blocker in result.blockers)
    assert result.merge_allowed is False
    assert result.deploy_allowed is False


def test_unsafe_default_blocks_profile() -> None:
    result = build_project_skeleton_profile(
        ProjectSkeletonProfileInput(
            project="Unsafe Example",
            type="application",
            default_risk="YELLOW",
            allowed_skeleton_capabilities=["issue-dispatch"],
            forbidden_by_default=["deploy without approval", "secrets", ".env"],
        )
    )

    assert result.profile_status == "blocked_unsafe_default"
    assert result.development_flow == []
    assert any("deploy without approval" in blocker for blocker in result.blockers)
    assert result.merge_allowed is False
    assert result.deploy_allowed is False


def test_missing_profile_fields_needs_review() -> None:
    result = build_project_skeleton_profile(ProjectSkeletonProfileInput())

    assert result.profile_status == "unknown_needs_review"
    assert result.development_flow == []
    assert any("project" in blocker for blocker in result.blockers)
    assert any("type" in blocker for blocker in result.blockers)
    assert any("default_risk" in blocker for blocker in result.blockers)
    assert any("allowed_skeleton_capabilities" in blocker for blocker in result.blockers)
