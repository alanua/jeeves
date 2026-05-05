from tools.skeleton_core.pr_status import PRStatusInput, build_pr_status


def test_pr_status_ready_to_merge() -> None:
    result = build_pr_status(
        PRStatusInput(
            pr_number=52,
            title="Ready PR",
            state="open",
            mergeable=True,
            draft=False,
            workflow_runs=[
                {"name": "Skeleton Core", "status": "completed", "conclusion": "success"}
            ],
            jobs=[
                {
                    "name": "Validate Skeleton core",
                    "status": "completed",
                    "conclusion": "success",
                }
            ],
        )
    )

    assert result.status == "ready_to_merge"
    assert result.ci_state == "success"
    assert result.blockers == []


def test_pr_status_draft_blocks() -> None:
    result = build_pr_status(
        PRStatusInput(
            pr_number=53,
            title="Draft PR",
            state="open",
            mergeable=True,
            draft=True,
        )
    )

    assert result.status == "blocked"
    assert result.blockers == ["PR is draft"]


def test_pr_status_waiting_for_ci() -> None:
    result = build_pr_status(
        PRStatusInput(
            pr_number=54,
            title="Pending PR",
            state="open",
            mergeable=True,
            draft=False,
            workflow_runs=[{"name": "Skeleton Core", "status": "in_progress", "conclusion": None}],
        )
    )

    assert result.status == "waiting_for_ci"
    assert result.ci_state == "pending"


def test_pr_status_black_failure_from_log_excerpt() -> None:
    result = build_pr_status(
        PRStatusInput(
            pr_number=55,
            title="Black failed PR",
            state="open",
            mergeable=True,
            draft=False,
            workflow_runs=[
                {"name": "Skeleton Core", "status": "completed", "conclusion": "failure"}
            ],
            jobs=[
                {
                    "name": "Validate Skeleton core",
                    "status": "completed",
                    "conclusion": "failure",
                    "failed_step": "Run Black check",
                }
            ],
            log_excerpt=(
                "would reformat /repo/tests/skeleton_core/test_handoff_pack.py\n"
                "would reformat /repo/tools/skeleton_core/handoff_pack.py"
            ),
        )
    )

    assert result.status == "needs_fix"
    assert result.ci_state == "failure"
    assert "Job failed: Validate Skeleton core / Run Black check" in result.blockers
    assert any("Black formatting check failed" in blocker for blocker in result.blockers)
    assert any("test_handoff_pack.py" in blocker for blocker in result.blockers)


def test_pr_status_unknown_without_ci_data() -> None:
    result = build_pr_status(
        PRStatusInput(
            pr_number=56,
            title="Ambiguous PR",
            state="open",
            mergeable=True,
            draft=False,
        )
    )

    assert result.status == "unknown_needs_review"
    assert result.ci_state == "unknown"
