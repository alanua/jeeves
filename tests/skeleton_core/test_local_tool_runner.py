from __future__ import annotations

import json
import subprocess
import sys

from tools.skeleton_core.local_tool_runner import (
    LocalToolRequest,
    build_local_tool_command,
    main,
    run_local_tool,
    validate_local_tool_request,
)


def test_build_py_compile_command() -> None:
    request = LocalToolRequest(
        tool="py_compile",
        targets=["tools/skeleton_core/local_tool_runner.py"],
    )

    assert build_local_tool_command(request) == [
        sys.executable,
        "-m",
        "py_compile",
        "tools/skeleton_core/local_tool_runner.py",
    ]


def test_build_pytest_command() -> None:
    request = LocalToolRequest(
        tool="pytest",
        targets=["tests/skeleton_core/test_local_tool_runner.py"],
    )

    assert build_local_tool_command(request) == [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "tests/skeleton_core/test_local_tool_runner.py",
    ]


def test_blocks_unsafe_targets() -> None:
    request = LocalToolRequest(
        tool="pytest",
        targets=["../secret.py", ".env", "tests/*.py"],
    )

    reasons = validate_local_tool_request(request)

    assert "path_traversal" in reasons
    assert "secret_or_control_path" in reasons
    assert "wildcard_target" in reasons


def test_run_local_tool_success_with_fake_runner() -> None:
    def fake_runner(*args, **kwargs):
        return subprocess.CompletedProcess(
            args[0],
            0,
            stdout="ok",
            stderr="",
        )

    report = run_local_tool(
        LocalToolRequest(
            tool="ruff_check",
            targets=["tools/skeleton_core/local_tool_runner.py"],
        ),
        runner=fake_runner,
    )

    assert report.status == "success"
    assert report.returncode == 0
    assert report.stdout_tail == "ok"


def test_run_local_tool_failure_with_fake_runner() -> None:
    def fake_runner(*args, **kwargs):
        return subprocess.CompletedProcess(
            args[0],
            1,
            stdout="",
            stderr="failed",
        )

    report = run_local_tool(
        LocalToolRequest(
            tool="black_check",
            targets=["tools/skeleton_core/local_tool_runner.py"],
        ),
        runner=fake_runner,
    )

    assert report.status == "failed"
    assert report.returncode == 1
    assert report.stderr_tail == "failed"


def test_run_local_tool_timeout_with_fake_runner() -> None:
    def fake_runner(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], timeout=3, output="", stderr="slow")

    report = run_local_tool(
        LocalToolRequest(
            tool="pytest",
            targets=["tests/skeleton_core/test_local_tool_runner.py"],
            timeout_seconds=3,
        ),
        runner=fake_runner,
    )

    assert report.status == "failed"
    assert report.returncode == 124
    assert "local_tool_timeout_seconds=3" in report.stderr_tail


def test_main_outputs_json(capsys) -> None:
    code = main(
        [
            "py_compile",
            "tools/skeleton_core/local_tool_runner.py",
            "--pretty",
        ]
    )

    assert code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "success"
    assert output["tool"] == "py_compile"


def test_main_blocks_invalid_target(capsys) -> None:
    code = main(["pytest", "../secret.py"])

    assert code == 2
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "blocked"
    assert "path_traversal" in output["blocked_reasons"]
