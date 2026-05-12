from __future__ import annotations

from pathlib import Path

import pytest

from tools.skeleton_core.canon_reader import (
    ALLOWED_CANON_PATHS,
    CanonReaderPanic,
    build_canon_bundle,
    read_canon_file,
    scan_sensitive_text,
    validate_canon_path,
)


def _make_allowed_files(root: Path) -> None:
    for rel in ALLOWED_CANON_PATHS:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"content for {rel}\n", encoding="utf-8")


def test_validate_canon_path_allows_allowlisted_file(tmp_path: Path) -> None:
    _make_allowed_files(tmp_path)

    resolved = validate_canon_path("BOOTLOADER.md", root=tmp_path)

    assert resolved == tmp_path / "BOOTLOADER.md"


def test_validate_canon_path_blocks_non_allowlisted_file(tmp_path: Path) -> None:
    path = tmp_path / "README.md"
    path.write_text("not allowed", encoding="utf-8")

    with pytest.raises(CanonReaderPanic):
        validate_canon_path("README.md", root=tmp_path)


def test_read_canon_file_fails_closed_on_secret_pattern(tmp_path: Path) -> None:
    path = tmp_path / "BOOTLOADER.md"
    path.write_text("OPENAI_API_KEY=secret", encoding="utf-8")

    with pytest.raises(CanonReaderPanic):
        read_canon_file("BOOTLOADER.md", root=tmp_path)


def test_build_canon_bundle_reads_allowlist(tmp_path: Path) -> None:
    _make_allowed_files(tmp_path)

    bundle = build_canon_bundle(paths=["BOOTLOADER.md"], root=tmp_path)

    assert "--- FILE: BOOTLOADER.md ---" in bundle
    assert "content for BOOTLOADER.md" in bundle


def test_scan_sensitive_text_detects_key_names() -> None:
    hits = scan_sensitive_text("GEMINI_API_KEY=value")

    assert hits
