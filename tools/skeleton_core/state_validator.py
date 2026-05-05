"""Read-only validation for Skeleton boot and current-state files."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict

REQUIRED_STATE_FILES = (
    "BOOTLOADER.md",
    "knowledge_base/START_HERE_FOR_CHATGPT.md",
    "knowledge_base/MEMORY_POLICY.md",
    "knowledge_base/WORKING_PROTOCOL.md",
    "knowledge_base/CHATGPT_BRANCH_CONTINUITY_BOOT.md",
    "knowledge_base/assistant_diary.md",
    "knowledge_base/chatgpt_exoskeleton/START_HERE.md",
    "knowledge_base/chatgpt_exoskeleton/CURRENT_STATE.md",
    "knowledge_base/CHATGPT_EXOSKELETON.md",
    "knowledge_base/CHATGPT_EXOSKELETON_RUNBOOK.md",
)

REQUIRED_ANCHORS = {
    "knowledge_base/chatgpt_exoskeleton/CURRENT_STATE.md": (
        "СК / ChatGPT Exoskeleton",
        "Externalizer",
    ),
    "knowledge_base/CHATGPT_EXOSKELETON.md": (
        "CHATGPT_EXOSKELETON_RUNBOOK.md",
    ),
    "knowledge_base/CHATGPT_BRANCH_CONTINUITY_BOOT.md": (
        "CHATGPT_EXOSKELETON_RUNBOOK.md",
    ),
    "knowledge_base/WORKING_PROTOCOL.md": ("+",),
}


class MissingAnchor(BaseModel):
    """A required text anchor missing from a file."""

    model_config = ConfigDict(extra="forbid")

    path: str
    anchor: str


class StateValidationResult(BaseModel):
    """Result for a read-only Skeleton state validation."""

    model_config = ConfigDict(extra="forbid")

    ok: bool
    missing_files: list[str]
    missing_anchors: list[MissingAnchor]
    checked_files: list[str]


def validate_state(root: Path) -> StateValidationResult:
    """Validate required Skeleton state files and anchors under root."""
    root = root.resolve()
    missing_files: list[str] = []
    missing_anchors: list[MissingAnchor] = []
    checked_files: list[str] = []

    for relative_path in REQUIRED_STATE_FILES:
        path = root / relative_path
        if not path.is_file():
            missing_files.append(relative_path)
            continue
        checked_files.append(relative_path)

    for relative_path, anchors in REQUIRED_ANCHORS.items():
        path = root / relative_path
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        for anchor in anchors:
            if anchor not in content:
                missing_anchors.append(MissingAnchor(path=relative_path, anchor=anchor))

    return StateValidationResult(
        ok=not missing_files and not missing_anchors,
        missing_files=missing_files,
        missing_anchors=missing_anchors,
        checked_files=checked_files,
    )
