from tools.skeleton_core.branch_recovery import BranchRecoveryInput, build_branch_recovery


def test_branch_recovery_completed_for_merged_pr() -> None:
    result = build_branch_recovery(
        BranchRecoveryInput(
            branch_name="skeleton/example-merged",
            issue_number=68,
            pr_number=70,
            pr_state="closed",
            merged=True,
            merged_sha="abc123def456",
            changed_files=["tools/skeleton_core/example.py"],
            ci_status="success",
        )
    )

    assert result.status == "completed"
    assert result.merged_sha == "abc123def456"
    assert result.blockers == []
    assert result.merge_allowed is False
    assert result.deploy_allowed is False
    assert result.next_safe_action == "checkpoint state and continue next task"


def test_branch_recovery_needs_fix_for_open_failed_ci() -> None:
    result = build_branch_recovery(
        BranchRecoveryInput(
            branch_name="skeleton/example-failed",
            issue_number=68,
            pr_number=69,
            pr_state="open",
            merged=False,
            changed_files=["tools/skeleton_core/example.py"],
            ci_status="failed",
            ci_blockers=["black"],
        )
    )

    assert result.status == "needs_fix"
    assert result.ci_status == "failed"
    assert result.blockers == ["black"]
    assert result.next_safe_action == "read job log summary, fix blocker, rerun CI"


def test_branch_recovery_waits_for_missing_ci() -> None:
    result = build_branch_recovery(
        BranchRecoveryInput(
            branch_name="skeleton/example-missing-ci",
            issue_number=68,
            pr_number=71,
            pr_state="open",
            changed_files=["tools/skeleton_core/example.py"],
            ci_status="missing",
        )
    )

    assert result.status == "wait_for_ci_or_fetch_status"
    assert result.next_safe_action == "wait for CI or fetch public-safe PR status export"


def test_branch_recovery_suggests_create_pr_when_branch_has_changes() -> None:
    result = build_branch_recovery(
        BranchRecoveryInput(
            branch_name="skeleton/example-no-pr",
            issue_number=68,
            changed_files=["tools/skeleton_core/example.py"],
            ci_status="unknown",
        )
    )

    assert result.status == "create_pr_if_branch_ready"
    assert result.pr_number is None
    assert (
        result.next_safe_action
        == "create draft PR if branch diff is still needed and public-safe"
    )


def test_branch_recovery_unknown_for_merged_without_sha() -> None:
    result = build_branch_recovery(
        BranchRecoveryInput(
            branch_name="skeleton/example-bad-merge",
            issue_number=68,
            pr_number=70,
            pr_state="closed",
            merged=True,
            merged_sha="",
            changed_files=["tools/skeleton_core/example.py"],
            ci_status="success",
        )
    )

    assert result.status == "unknown_needs_review"
    assert "Merged PR has no merged_sha in export" in result.blockers
