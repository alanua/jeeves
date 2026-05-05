from tools.skeleton_core.job_log_summary import summarize_job_log


def test_detects_black_formatting_failure() -> None:
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


def test_detects_pytest_failure() -> None:
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


def test_no_failure_detected_for_clean_log() -> None:
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


def test_unknown_failure_when_pattern_is_not_known() -> None:
    summary = summarize_job_log("""
        Run custom step
        something unexpected happened
        ##[error]Process completed with exit code 1.
        """)

    assert summary.status == "unknown_needs_review"
    assert summary.detected_failure_type == "unknown"
    assert summary.evidence_lines == ["##[error]Process completed with exit code 1."]
