from tools.skeleton_core.issue_runner_bridge import IssueRunnerInput, build_issue_runner_packet


def test_issue_runner_bridge_accepts_green() -> None:
    result = build_issue_runner_packet(
        IssueRunnerInput(
            issue_number=61,
            title="Docs cleanup",
            body="Update public-safe wording in docs only.",
            labels=["risk:green"],
        )
    )

    assert result.status == "accepted"
    assert result.risk_level == "GREEN"
    assert result.runner_route == "RUNNER_GREEN"
    assert result.review_required is False
    assert result.merge_allowed is False
    assert result.deploy_allowed is False
    assert result.blockers == []


def test_issue_runner_bridge_accepts_yellow_with_review() -> None:
    result = build_issue_runner_packet(
        IssueRunnerInput(
            issue_number=62,
            title="Add docs note",
            body="Create a public-safe docs note.",
            labels=["risk:yellow"],
        )
    )

    assert result.status == "accepted"
    assert result.risk_level == "YELLOW"
    assert result.runner_route == "RUNNER_YELLOW"
    assert result.review_required is True
    assert result.merge_allowed is False
    assert result.deploy_allowed is False


def test_issue_runner_bridge_blocks_merge_and_deploy_even_when_yellow() -> None:
    result = build_issue_runner_packet(
        IssueRunnerInput(
            issue_number=63,
            title="Merge and deploy runner bridge",
            body="Merge the PR and deploy to production using tokens.",
            labels=["risk:yellow"],
        )
    )

    assert result.status == "blocked"
    assert result.runner_route == "BLOCKED"
    assert result.review_required is True
    assert result.merge_allowed is False
    assert result.deploy_allowed is False
    assert any("merge" in blocker for blocker in result.blockers)
    assert any("deploy" in blocker for blocker in result.blockers)
    assert any("secret" in blocker for blocker in result.blockers)


def test_issue_runner_bridge_blocks_orange() -> None:
    result = build_issue_runner_packet(
        IssueRunnerInput(
            issue_number=64,
            title="Implement runtime feature",
            body="Change runtime behavior.",
            labels=["risk:orange"],
        )
    )

    assert result.status == "blocked"
    assert result.risk_level == "ORANGE"
    assert result.runner_route == "BLOCKED"
    assert result.merge_allowed is False
    assert result.deploy_allowed is False


def test_issue_runner_bridge_unknown_without_risk() -> None:
    result = build_issue_runner_packet(
        IssueRunnerInput(
            issue_number=65,
            title="Ambiguous task",
            body="Do something.",
            labels=[],
        )
    )

    assert result.status == "unknown_needs_review"
    assert result.risk_level == "UNKNOWN"
    assert result.runner_route == "BLOCKED"
    assert result.merge_allowed is False
    assert result.deploy_allowed is False
