from tools.skeleton_core.job_log_summary import summarize_job_log
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


def test_job_log_summary_detects_black_formatting_failure() -> None:
    summary = summarize_job_log("""
        Run Black check
        would reformat /repo/tests/skeleton_core/test_pr_status.py
        Oh no! 1 file would be reformatted, 30 files would be left unchanged.
        ##[error]Process completed with exit code 1.
        """)

    assert summary.status == "needs_fix"
    assert summary.detected_failure_type == "black_formatting"
    assert summary.failed_step == "Run Black check"
    assert summary.affected_files == ["/repo/tests/skeleton_core/test_pr_status.py"]
    assert any("would reformat" in line for line in summary.evidence_lines)


def test_job_log_summary_detects_pytest_failure() -> None:
    summary = summarize_job_log("""
        Run tests
        =================================== FAILURES ===================================
        FAILED tests/skeleton_core/test_job_log_summary.py::test_detects_pytest_failure
        assert 'actual' == 'expected'
        =========================== short test summary info ===========================
        """)

    assert summary.status == "needs_fix"
    assert summary.detected_failure_type == "tests_failed"
    assert summary.failed_step == "Run tests"
    assert "tests/skeleton_core/test_job_log_summary.py" in summary.affected_files


def test_job_log_summary_no_failure_detected_for_clean_log() -> None:
    summary = summarize_job_log("""
        Run tests
        126 passed in 0.71s
        Run Ruff
        All checks passed!
        Run Black check
        All done!
        """)

    assert summary.status == "no_failure_detected"
    assert summary.detected_failure_type == "unknown"
    assert summary.evidence_lines == []


def test_job_log_summary_unknown_failure_when_pattern_is_not_known() -> None:
    summary = summarize_job_log("""
        Run custom step
        something unexpected happened
        ##[error]Process completed with exit code 1.
        """)

    assert summary.status == "unknown_needs_review"
    assert summary.detected_failure_type == "unknown"
    assert summary.evidence_lines == ["##[error]Process completed with exit code 1."]
