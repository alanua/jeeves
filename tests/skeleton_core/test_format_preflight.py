from tools.skeleton_core.format_preflight import FormatPreflightInput, build_format_preflight


def test_format_preflight_clean_ready() -> None:
    result = build_format_preflight(
        FormatPreflightInput(
            checked_paths=["tools/skeleton_core", "tests/skeleton_core"],
            files_needing_format=[],
            black_available="ok",
        )
    )

    assert result.status == "format_ready"
    assert result.safe_to_continue_ci is True
    assert result.merge_allowed is False
    assert result.deploy_allowed is False


def test_format_preflight_needs_black() -> None:
    result = build_format_preflight(
        FormatPreflightInput(
            checked_paths=["tools/skeleton_core/cli.py"],
            files_needing_format=["tools/skeleton_core/cli.py"],
            black_available="ok",
        )
    )

    assert result.status == "needs_black_format"
    assert result.safe_to_continue_ci is False
    assert result.files_needing_format == ["tools/skeleton_core/cli.py"]
    assert "python -m black tools/skeleton_core/cli.py" in result.commands_recommended


def test_format_preflight_missing_black() -> None:
    result = build_format_preflight(
        FormatPreflightInput(
            checked_paths=["tools/skeleton_core"],
            black_available="missing",
        )
    )

    assert result.status == "blocked_missing_black"
    assert result.safe_to_continue_ci is False
    assert result.next_safe_step == "Install dev dependencies with Black before formatting checks."


def test_format_preflight_unknown_without_paths() -> None:
    result = build_format_preflight(FormatPreflightInput())

    assert result.status == "unknown_needs_review"
    assert result.safe_to_continue_ci is False
