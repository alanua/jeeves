from tools.skeleton_core.runner_env_check import RunnerEnvCheckInput, build_runner_env_check


def _base_packet(**overrides) -> RunnerEnvCheckInput:
    data = {
        "repository": "alanua/bauclock",
        "repo_url_checked": "https://github.com/alanua/bauclock.git",
        "checks": {
            "python": "ok",
            "git": "ok",
            "workdir": "ok",
            "dns_github": "not_checked",
            "clone": "not_checked",
            "pytest": "ok",
        },
        "commands_run": ["python --version", "git --version"],
        "blocked_reason": "",
        "policy_violation": False,
    }
    data.update(overrides)
    return RunnerEnvCheckInput(**data)


def test_runner_env_check_ready() -> None:
    result = build_runner_env_check(_base_packet())

    assert result.status == "ready_for_read_only_validation"
    assert result.repository == "alanua/bauclock"
    assert result.safe_for_runner is True
    assert result.merge_allowed is False
    assert result.deploy_allowed is False
    assert result.next_safe_step == "Continue to runner-command-pack for read-only validation work."


def test_runner_env_check_blocks_dns_failure() -> None:
    result = build_runner_env_check(
        _base_packet(
            checks={
                "python": "ok",
                "git": "ok",
                "workdir": "ok",
                "dns_github": "failed",
                "clone": "not_run_or_failed",
                "pytest": "not_checked",
            },
            blocked_reason="Could not resolve host: github.com",
        )
    )

    assert result.status == "blocked_dns_or_network"
    assert result.safe_for_runner is False
    assert result.blocked_reason == "Could not resolve host: github.com"


def test_runner_env_check_blocks_no_git() -> None:
    result = build_runner_env_check(
        _base_packet(checks={"python": "ok", "git": "missing", "workdir": "ok"})
    )

    assert result.status == "blocked_no_git"
    assert result.safe_for_runner is False
    assert result.blocked_reason == "Git is not available in the runner."


def test_runner_env_check_blocks_clone_failed() -> None:
    result = build_runner_env_check(
        _base_packet(
            checks={
                "python": "ok",
                "git": "ok",
                "workdir": "ok",
                "dns_github": "ok",
                "clone": "failed",
                "pytest": "ok",
            }
        )
    )

    assert result.status == "blocked_clone_failed"
    assert result.safe_for_runner is False


def test_runner_env_check_blocks_pytest_missing() -> None:
    result = build_runner_env_check(
        _base_packet(checks={"python": "ok", "git": "ok", "workdir": "ok", "pytest": "missing"})
    )

    assert result.status == "blocked_pytest_unavailable"
    assert result.safe_for_runner is False


def test_runner_env_check_redacts_credential_url() -> None:
    result = build_runner_env_check(
        _base_packet(
            repo_url_checked="https://token@example.com/alanua/bauclock.git",
            policy_violation=True,
            blocked_reason="Repository URL contains credentials and was redacted.",
        )
    )

    assert result.status == "unsafe_or_policy_violation"
    assert result.repo_url_checked == "<redacted-repo-url>"
    assert "token" not in result.model_dump_json()
    assert result.safe_for_runner is False
