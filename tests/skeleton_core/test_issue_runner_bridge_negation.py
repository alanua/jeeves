from tools.skeleton_core.issue_runner_bridge import IssueRunnerInput, build_issue_runner_packet


def test_accepts_bauclock_green_safe_forbidden_clauses() -> None:
    result = build_issue_runner_packet(
        IssueRunnerInput(
            issue_number=22,
            title="BauClock docs cleanup",
            body=(
                "Update public-safe docs only.\n\n"
                "Safety note:\n"
                "No merge.\n"
                "No deploy.\n"
                "No production database.\n"
                "No .env reading or printing.\n"
                "No secrets.\n"
                "No tokens.\n"
                "Forbidden: merge/deploy/server/production DB/.env/secrets."
            ),
            labels=["risk:green"],
            project="bauclock",
        )
    )

    assert result.status == "accepted"
    assert result.risk_level == "GREEN"
    assert result.runner_route == "RUNNER_GREEN"
    assert result.merge_allowed is False
    assert result.deploy_allowed is False
    assert result.blockers == []


def test_accepts_bauclock_yellow_safe_negations() -> None:
    result = build_issue_runner_packet(
        IssueRunnerInput(
            issue_number=23,
            title="BauClock role docs note",
            body=(
                "Create a public-safe planning note.\n\n"
                "Hard safety rules:\n"
                "Do not merge.\n"
                "Do not deploy.\n"
                "Do not access production DB.\n"
                "Do not read or print .env.\n"
                "Never show secrets.\n"
                "Never include tokens."
            ),
            labels=["risk:yellow"],
            project="bauclock",
        )
    )

    assert result.status == "accepted"
    assert result.risk_level == "YELLOW"
    assert result.runner_route == "RUNNER_YELLOW"
    assert result.review_required is True
    assert result.merge_allowed is False
    assert result.deploy_allowed is False
    assert result.blockers == []


def test_blocks_positive_deploy_request() -> None:
    result = build_issue_runner_packet(
        IssueRunnerInput(
            issue_number=66,
            title="Deploy BauClock",
            body="Deploy to production, read .env, use API key, and call external network service.",
            labels=["risk:yellow"],
            project="bauclock",
        )
    )

    assert result.status == "blocked"
    assert result.runner_route == "BLOCKED"
    assert result.merge_allowed is False
    assert result.deploy_allowed is False
    assert any("deploy" in blocker for blocker in result.blockers)
    assert any("production" in blocker for blocker in result.blockers)
    assert any("secret" in blocker for blocker in result.blockers)
    assert any("network" in blocker for blocker in result.blockers)
