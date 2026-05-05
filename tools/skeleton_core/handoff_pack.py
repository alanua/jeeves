"""Compact public-safe handoff pack rendering for Skeleton branches."""

from __future__ import annotations

from pathlib import Path

from tools.skeleton_core.state_validator import StateValidationResult, validate_state

AVAILABLE_COMMANDS = (
    "validate-state",
    "task-from-text",
    "decide",
    "work-packet",
    "checkpoint",
    "classify-queue",
    "queue-summary",
    "trace-packet",
    "runner-report-from-trace",
)

CURRENT_STATE_PATH = Path("knowledge_base/chatgpt_exoskeleton/CURRENT_STATE.md")
EXCERPT_HEADINGS = (
    "## Current state",
    "## Active GitHub queue",
    "## Next practical step",
)


def _format_list(values: list[str]) -> str:
    if not values:
        return "- none"
    return "\n".join(f"- {value}" for value in values)


def _format_missing_anchors(result: StateValidationResult) -> str:
    if not result.missing_anchors:
        return "- none"
    return "\n".join(f"- {missing.path}: {missing.anchor}" for missing in result.missing_anchors)


def _extract_heading_section(content: str, heading: str) -> str:
    marker = f"\n{heading}\n"
    start = content.find(marker)
    if start == -1:
        if content.startswith(f"{heading}\n"):
            start = 0
        else:
            return ""
    else:
        start += 1

    next_heading = content.find("\n## ", start + len(heading))
    if next_heading == -1:
        return content[start:].strip()
    return content[start:next_heading].strip()


def current_state_excerpt(content: str, max_chars: int = 2400) -> str:
    """Extract a compact excerpt from CURRENT_STATE content."""
    sections = [
        section
        for heading in EXCERPT_HEADINGS
        if (section := _extract_heading_section(content, heading))
    ]
    excerpt = "\n\n".join(sections).strip()
    if not excerpt:
        excerpt = "CURRENT_STATE excerpt unavailable"
    if len(excerpt) > max_chars:
        return excerpt[: max_chars - 1].rstrip() + "…"
    return excerpt


def render_handoff_pack(root: Path) -> str:
    """Render a compact public-safe handoff pack for the next branch."""
    root = root.resolve()
    validation = validate_state(root)
    current_state_path = root / CURRENT_STATE_PATH
    if current_state_path.is_file():
        excerpt = current_state_excerpt(current_state_path.read_text(encoding="utf-8"))
    else:
        excerpt = "CURRENT_STATE excerpt unavailable"

    return "\n".join(
        [
            "skeleton_handoff_pack",
            "state_validation",
            f"ok: {str(validation.ok).lower()}",
            "missing_files",
            _format_list(validation.missing_files),
            "missing_anchors",
            _format_missing_anchors(validation),
            "current_state_excerpt",
            excerpt,
            "available_commands",
            _format_list(list(AVAILABLE_COMMANDS)),
            "next_recommended_step",
            (
                "Run validate-state, create a work-packet for the real task, "
                "then checkpoint durable results. Use classify-queue when queue hygiene "
                "is needed and CI as the default validation source."
            ),
        ]
    )
