from pathlib import Path

from tools.skeleton_core.handoff_pack import current_state_excerpt, render_handoff_pack
from tools.skeleton_core.state_validator import REQUIRED_ANCHORS, REQUIRED_STATE_FILES


def _write_minimal_valid_state(root: Path) -> None:
    for relative_path in REQUIRED_STATE_FILES:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("placeholder\n", encoding="utf-8")

    for relative_path, anchors in REQUIRED_ANCHORS.items():
        path = root / relative_path
        path.write_text("\n".join(anchors) + "\n", encoding="utf-8")


def test_current_state_excerpt_uses_selected_sections_only() -> None:
    content = """# State

## Current state

Current content.

## Externalizer usage

Should not be included.

## Active GitHub queue

Queue content.

## Next practical step

Next content.
"""

    excerpt = current_state_excerpt(content)

    assert "## Current state" in excerpt
    assert "Current content." in excerpt
    assert "## Active GitHub queue" in excerpt
    assert "Queue content." in excerpt
    assert "## Next practical step" in excerpt
    assert "Next content." in excerpt
    assert "Should not be included." not in excerpt


def test_current_state_excerpt_is_capped() -> None:
    content = "## Current state\n\n" + ("x" * 3000)

    excerpt = current_state_excerpt(content, max_chars=100)

    assert len(excerpt) == 100
    assert excerpt.endswith("…")


def test_render_handoff_pack_success(tmp_path: Path) -> None:
    _write_minimal_valid_state(tmp_path)
    current_state_path = tmp_path / "knowledge_base" / "chatgpt_exoskeleton" / "CURRENT_STATE.md"
    current_state_path.write_text(
        """# State

## Current state

СК / ChatGPT Exoskeleton
Externalizer ready.

## Active GitHub queue

#40

## Next practical step

Use current tools.
""",
        encoding="utf-8",
    )

    handoff = render_handoff_pack(tmp_path)

    assert handoff.startswith("skeleton_handoff_pack\nstate_validation")
    assert "ok: true" in handoff
    assert "missing_files\n- none" in handoff
    assert "missing_anchors\n- none" in handoff
    assert "current_state_excerpt\n## Current state" in handoff
    assert "available_commands\n- validate-state" in handoff
    assert "- handoff-pack" not in handoff
    assert "next_recommended_step" in handoff


def test_render_handoff_pack_reports_missing_state(tmp_path: Path) -> None:
    handoff = render_handoff_pack(tmp_path)

    assert "ok: false" in handoff
    assert "missing_files\n- BOOTLOADER.md" in handoff
    assert "CURRENT_STATE excerpt unavailable" in handoff
