from tools.skeleton_core.issue_runner_bridge import IssueRunnerInput
from tools.skeleton_core.task_lifecycle import build_task_lifecycle_packet


def test_task_lifecycle_accepts_green() -> None:
    result = build_task_lifecycle_packet(
        IssueRunnerInput(
            issue_number=61,
            title="Docs cleanup",
            body="Update public-safe wording in docs only.",
            labels=["risk:green"],
            project="skeleton",
        )
    )

    assert result.status == "accepted"
    assert result.risk_level == "GREEN"
    assert result.runner_route == "RUNNER_GREEN"
    assert result.review_required is False
    assert result.merge_allowed is False
    assert result.deploy_allowed is False
    assert result.work_summary == "Issue #61: Docs cleanup"
    assert result.initial_checkpoint.task_id == "issue-61"
    assert result.initial_checkpoint.project == "skeleton"
    assert result.initial_checkpoint.result == "queued"
    assert result.blockers == []


def test_task_lifecycle_accepts_yellow_with_review() -> None:
    result = build_task_lifecycle_packet(
        IssueRunnerInput(
            issue_number=62,
            title="Add project-state docs note",
            body="Create a public-safe docs note.",
            labels=["risk:yellow"],
            project="skeleton",
        )
    )

    assert result.status == "accepted"
    assert result.risk_level == "YELLOW"
    assert result.runner_route == "RUNNER_YELLOW"
    assert result.review_required is True
    assert result.merge_allowed is False
    assert result.deploy_allowed is False
    assert result.initial_checkpoint.result == "queued"


def test_task_lifecycle_blocks_unsafe_scope() -> None:
    result = build_task_lifecycle_packet(
        IssueRunnerInput(
            issue_number=63,
            title="Merge and deploy runner bridge",
            body="Merge the PR and deploy to production using tokens.",
            labels=["risk:yellow"],
            project="skeleton",
        )
    )

    assert result.status == "blocked"
    assert result.runner_route == "BLOCKED"
    assert result.merge_allowed is False
    assert result.deploy_allowed is False
    assert result.initial_checkpoint.result == "blocked"
    assert any("merge" in blocker for blocker in result.blockers)
    assert any("deploy" in blocker for blocker in result.blockers)
    assert any("secret" in blocker for blocker in result.blockers)


def test_task_lifecycle_unknown_without_risk() -> None:
    result = build_task_lifecycle_packet(
        IssueRunnerInput(
            issue_number=64,
            title="Ambiguous task",
            body="Do something.",
            labels=[],
            project="skeleton",
        )
    )

    assert result.status == "unknown_needs_review"
    assert result.risk_level == "UNKNOWN"
    assert result.runner_route == "BLOCKED"
    assert result.merge_allowed is False
    assert result.deploy_allowed is False
    assert result.initial_checkpoint.result == "unknown_needs_review"
