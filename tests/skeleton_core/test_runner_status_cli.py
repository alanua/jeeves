from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def _run_cli(*args: str) -> dict:
    result = subprocess.run(
        [sys.executable, "-m", "tools.skeleton_core.cli", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_runner_status_check_cli_fixture_mode_returns_running() -> None:
    payload = _run_cli(
        "runner-status-check",
        "--input",
        str(FIXTURES / "runner_status_check_running.json"),
    )

    assert payload["status"] == "running"
    assert payload["repository"] == "alanua/bauclock"
    assert payload["issue_number"] == 48
    assert payload["merge_allowed"] is False
    assert payload["deploy_allowed"] is False


def test_runner_status_check_cli_no_input_fails_closed() -> None:
    payload = _run_cli(
        "runner-status-check",
        "--repo",
        "alanua/bauclock",
        "--issue",
        "48",
    )

    assert payload["status"] == "needs_manual_review"
    assert payload["repository"] == "alanua/bauclock"
    assert payload["issue_number"] == 48
    assert payload["recommended_queue_action"] == "needs_manual_review"
    assert payload["merge_allowed"] is False
    assert payload["deploy_allowed"] is False


def test_runner_status_check_cli_live_with_temp_run_dir(tmp_path) -> None:
    run_id = "20260512-091344-yellow-alanua-bauclock-48"
    run_dir = tmp_path / "agent-runs" / run_id
    run_dir.mkdir(parents=True)
    (run_dir / "log.txt").write_text(
        "=== YELLOW AGENT RUN START ===\n" "Run ID: 20260512-091344-yellow-alanua-bauclock-48\n",
        encoding="utf-8",
    )

    payload = _run_cli(
        "runner-status-check",
        "--repo",
        "alanua/bauclock",
        "--issue",
        "48",
        "--run-id",
        run_id,
        "--live",
        "--lock-file",
        str(tmp_path / "missing.lock"),
        "--agent-runs-dir",
        str(tmp_path / "agent-runs"),
        "--logs-dir",
        str(tmp_path / "logs"),
    )

    assert payload["repository"] == "alanua/bauclock"
    assert payload["issue_number"] == 48
    assert payload["latest_run_id"] == run_id
    assert payload["merge_allowed"] is False
    assert payload["deploy_allowed"] is False
