from pathlib import Path

from tools.skeleton_core.state_validator import (
    REQUIRED_ANCHORS,
    REQUIRED_STATE_FILES,
    validate_state,
)


def _write_minimal_valid_state(root: Path) -> None:
    for relative_path in REQUIRED_STATE_FILES:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("placeholder\n", encoding="utf-8")

    for relative_path, anchors in REQUIRED_ANCHORS.items():
        path = root / relative_path
        path.write_text("\n".join(anchors) + "\n", encoding="utf-8")


def test_validate_state_success(tmp_path: Path) -> None:
    _write_minimal_valid_state(tmp_path)

    result = validate_state(tmp_path)

    assert result.ok is True
    assert result.missing_files == []
    assert result.missing_anchors == []
    assert result.checked_files == list(REQUIRED_STATE_FILES)


def test_validate_state_reports_missing_file(tmp_path: Path) -> None:
    _write_minimal_valid_state(tmp_path)
    missing_path = tmp_path / "knowledge_base" / "assistant_diary.md"
    missing_path.unlink()

    result = validate_state(tmp_path)

    assert result.ok is False
    assert result.missing_files == ["knowledge_base/assistant_diary.md"]
    assert result.missing_anchors == []
    assert "knowledge_base/assistant_diary.md" not in result.checked_files


def test_validate_state_reports_missing_anchor(tmp_path: Path) -> None:
    _write_minimal_valid_state(tmp_path)
    current_state_path = tmp_path / "knowledge_base" / "chatgpt_exoskeleton" / "CURRENT_STATE.md"
    current_state_path.write_text("СК / ChatGPT Exoskeleton\n", encoding="utf-8")

    result = validate_state(tmp_path)

    assert result.ok is False
    assert result.missing_files == []
    assert len(result.missing_anchors) == 1
    assert result.missing_anchors[0].path == "knowledge_base/chatgpt_exoskeleton/CURRENT_STATE.md"
    assert result.missing_anchors[0].anchor == "Externalizer"
