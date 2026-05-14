from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def valid_payload() -> dict:
    return {
        "issue_number": 198,
        "repo": "alanua/jeeves",
        "title": "Add OpenHands dispatch CLI hook v0",
        "body": "bounded CLI hook test payload",
        "labels": [
            "agent:task",
            "agent:audited",
            "agent:plan-ready",
            "runner:openhands",
            "risk:yellow",
        ],
        "allowed_files": ["tools/skeleton_core/cli.py"],
        "expected_artifact": "diff",
        "authority_level": "level_2_local_diff",
        "risk_level": "yellow",
        "fuel_provider": "openrouter",
        "fuel_model": "deepseek/deepseek-v4-flash:free",
        "fuel_max_usd": 1.0,
    }


def write_payload(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "payload.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def run_cli(payload_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.skeleton_core.cli",
            "openhands-dispatch",
            "--input",
            str(payload_path),
        ],
        text=True,
        capture_output=True,
        check=False,
    )


def test_main_cli_openhands_dispatch_valid_payload(tmp_path: Path) -> None:
    payload_path = write_payload(tmp_path, valid_payload())

    completed = run_cli(payload_path)

    assert completed.returncode == 0
    output = json.loads(completed.stdout)
    assert output["cli_version"] == "openhands_dispatch_cli.v0"
    assert output["status"] == "dispatched"
    assert output["packet"]["task_id"] == "issue-198-openhands"


def test_main_cli_openhands_dispatch_blocked_payload(tmp_path: Path) -> None:
    payload = valid_payload()
    payload["labels"].remove("agent:audited")
    payload_path = write_payload(tmp_path, payload)

    completed = run_cli(payload_path)

    assert completed.returncode == 1
    output = json.loads(completed.stdout)
    assert output["status"] == "blocked"
    assert "missing_label:agent:audited" in output["blocked_reasons"]
