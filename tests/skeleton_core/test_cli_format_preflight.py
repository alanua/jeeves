import json

from tools.skeleton_core.cli import main


def _run_fixture(path: str, capsys) -> dict:
    exit_code = main(["format-preflight", "--input", path])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    return payload


def test_cli_format_preflight_clean_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/format_preflight_clean.json", capsys)

    assert payload["status"] == "format_ready"
    assert payload["safe_to_continue_ci"] is True
    assert payload["merge_allowed"] is False
    assert payload["deploy_allowed"] is False


def test_cli_format_preflight_needs_black_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/format_preflight_needs_black.json", capsys)

    assert payload["status"] == "needs_black_format"
    assert payload["safe_to_continue_ci"] is False
    assert payload["files_needing_format"] == ["tools/skeleton_core/cli.py"]


def test_cli_format_preflight_missing_black_fixture(capsys) -> None:
    payload = _run_fixture("tests/fixtures/format_preflight_missing_black.json", capsys)

    assert payload["status"] == "blocked_missing_black"
    assert payload["safe_to_continue_ci"] is False


def test_cli_format_preflight_missing_args(capsys) -> None:
    exit_code = main(["format-preflight"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["status"] == "unknown_needs_review"
    assert payload["safe_to_continue_ci"] is False
