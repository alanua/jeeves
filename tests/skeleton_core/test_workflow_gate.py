from tools.skeleton_core.workflow_gate import WorkflowGateInput, build_workflow_gate


def test_python_update_ready() -> None:
    result = build_workflow_gate(
        WorkflowGateInput(
            action="github_update_file",
            python_files_changed=True,
            preflights={
                "local_black_applied": "ok",
                "format_preflight": "format_ready",
                "head_sha_verified": "ok",
            },
            requested_next_action="update_file",
        )
    )

    assert result.status == "action_ready"
    assert result.allowed_to_continue is True
    assert result.merge_allowed is False
    assert result.deploy_allowed is False


def test_python_update_missing_format_blocks() -> None:
    result = build_workflow_gate(
        WorkflowGateInput(
            action="github_update_file",
            python_files_changed=True,
            preflights={
                "local_black_applied": "missing",
                "format_preflight": "unknown",
                "head_sha_verified": "ok",
            },
            requested_next_action="update_file",
        )
    )

    assert result.status == "blocked_missing_required_skill"
    assert result.allowed_to_continue is False
    assert "local_black_applied" in result.missing_or_failed_skills
    assert "format_preflight" in result.missing_or_failed_skills


def test_pr_ready_missing_review_gate_blocks() -> None:
    result = build_workflow_gate(
        WorkflowGateInput(
            action="ready_for_review",
            preflights={"ci_status": "success"},
            requested_next_action="ready_for_review",
        )
    )

    assert result.status == "blocked_missing_required_skill"
    assert result.allowed_to_continue is False
    assert result.required_skills == ["ci_status", "pr_review_gate"]
    assert result.missing_or_failed_skills == ["pr_review_gate"]


def test_runner_dispatch_missing_env_check_blocks() -> None:
    result = build_workflow_gate(
        WorkflowGateInput(
            action="runner_dispatch",
            preflights={"runner_command_pack": "ready"},
            requested_next_action="runner_dispatch",
        )
    )

    assert result.status == "blocked_missing_required_skill"
    assert "runner_env_check" in result.missing_or_failed_skills


def test_queue_advance_missing_previous_report_blocks() -> None:
    result = build_workflow_gate(
        WorkflowGateInput(
            action="queue_advance",
            queue_next_runnable_issue=90,
            preflights={"queue_state": "has_next_runnable_issue"},
            requested_next_action="start_next_issue",
        )
    )

    assert result.status == "blocked_missing_required_skill"
    assert result.allowed_to_continue is False
    assert "runner_report_ingest" in result.missing_or_failed_skills


def test_actions_report_unsafe_blocks() -> None:
    result = build_workflow_gate(
        WorkflowGateInput(
            action="actions_report",
            preflights={"github_actions_runner_control": "unsafe_or_policy_violation"},
            requested_next_action="use_actions_report",
        )
    )

    assert result.status == "blocked_failed_required_skill"
    assert result.allowed_to_continue is False
    assert result.missing_or_failed_skills == [
        "github_actions_runner_control=unsafe_or_policy_violation"
    ]


def test_unknown_without_matching_gate_needs_review() -> None:
    result = build_workflow_gate(WorkflowGateInput(action="unknown"))

    assert result.status == "unknown_needs_review"
    assert result.allowed_to_continue is False
