from __future__ import annotations

from pathlib import Path

import pytest

from tools.skeleton_core.atomic_writer import AtomicWritePanic
from tools.skeleton_core.cli_create_pr import (
    CreatePrPanic,
    parse_target_files,
    validate_target_file,
    validate_target_files,
)


def test_parse_target_files_rejects_shortcuts() -> None:
    with pytest.raises(CreatePrPanic):
        parse_target_files(".")

    with pytest.raises(CreatePrPanic):
        parse_target_files("-A")


def test_validate_target_file_allows_green_zone_report(tmp_path: Path) -> None:
    target = tmp_path / "knowledge_base" / "reports" / "report.json"
    target.parent.mkdir(parents=True)
    target.write_text("{}", encoding="utf-8")

    assert (
        validate_target_file("knowledge_base/reports/report.json", repo_root=tmp_path)
        == "knowledge_base/reports/report.json"
    )


def test_validate_target_file_allows_skeleton_diary(tmp_path: Path) -> None:
    target = tmp_path / "knowledge_base" / "skeleton_diary.md"
    target.parent.mkdir(parents=True)
    target.write_text("# diary\n", encoding="utf-8")

    assert (
        validate_target_file("knowledge_base/skeleton_diary.md", repo_root=tmp_path)
        == "knowledge_base/skeleton_diary.md"
    )


@pytest.mark.parametrize(
    "bad_path",
    [
        "src/bad.py",
        "tests/bad.py",
        "canon/bad.md",
        "README.md",
    ],
)
def test_validate_target_file_blocks_bad_paths(tmp_path: Path, bad_path: str) -> None:
    target = tmp_path / bad_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("bad", encoding="utf-8")

    with pytest.raises((CreatePrPanic, AtomicWritePanic)):
        validate_target_file(bad_path, repo_root=tmp_path)


def test_validate_target_files_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(CreatePrPanic):
        validate_target_files(["knowledge_base/reports/missing.json"], repo_root=tmp_path)
