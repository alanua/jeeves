from __future__ import annotations

import json
import subprocess
import sys


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "tools.skeleton_core.cli", *args],
        check=False,
        capture_output=True,
        text=True,
    )


def test_module_registry_cli_json_lists_entries() -> None:
    result = _run_cli("module-registry", "--format", "json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    names = {entry["name"] for entry in payload}
    assert "runner-status-check" in names


def test_module_registry_cli_defaults_to_json() -> None:
    result = _run_cli("module-registry")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert isinstance(payload, list)


def test_module_registry_cli_markdown_outputs_table() -> None:
    result = _run_cli("module-registry", "--format", "markdown")

    assert result.returncode == 0
    assert "| Module | Status | Risk | Side effects | Purpose |" in result.stdout
    assert "`runner-status-check`" in result.stdout


def test_module_registry_cli_command_filters_one_entry() -> None:
    result = _run_cli("module-registry", "--command", "runner-status-check")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["name"] == "runner-status-check"
    assert payload["execution_authority"] is False
    assert payload["side_effects"] is False


def test_module_registry_cli_unknown_command_returns_public_safe_error() -> None:
    result = _run_cli("module-registry", "--command", "missing-module")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload == {"error": "module_not_found", "command": "missing-module"}
    assert result.stderr == ""
