"""NotebookLM handoff builder for private Construction Takeoff review."""

from __future__ import annotations

from pathlib import Path

from .schemas import PilotConfig, SourceRecord


def build_notebooklm_handoff(config: PilotConfig, records: list[SourceRecord]) -> str:
    lines = [
        "# Construction Takeoff NotebookLM Handoff",
        "",
        "Status: INITIAL_SOURCE_INVENTORY",
        "Privacy: PRIVATE_REVIEW_CONTEXT",
        "",
        "## Purpose",
        "",
        "Load this handoff into NotebookLM together with selected private source PDFs/reports/results ",
        "so it can act as a private evidence memory and result-reading/Q&A layer.",
        "",
        "NotebookLM is not the parser, not the executor, and not the final quantity authority.",
        "",
        "## Pilot scope",
        "",
        f"- Scope: `{config.scope}`",
        f"- Targets: `{', '.join(config.targets)}`",
        f"- Source priority: `{config.source_priority}`",
        "",
        "## Source priority rule",
        "",
        "PDF selects the current visual/version state. DWG/DXF provide precise vector measurements ",
        "only after the relevant candidate geometry has been matched to the PDF current variant.",
        "",
        "## Source inventory summary",
        "",
    ]

    for record in records:
        lines.append(
            "- "
            f"{record.source_id}: {record.private_source_ref} | "
            f"type={record.source_type} | scope={record.floor_or_scope} | "
            f"role={record.source_role} | priority={record.priority_for_this_object} | "
            f"status={record.parse_status}"
        )

    lines.extend(
        [
            "",
            "## Questions for NotebookLM review",
            "",
            "1. Which documents look essential for the requested quantity target?",
            "2. Which sources appear to be current visual state versus measurement candidates?",
            "3. Which source conflicts should be checked before producing room/wall quantities?",
            "4. Which assumptions must remain open for Oleksii review?",
            "",
            "## Forbidden interpretations",
            "",
            "- Do not treat this handoff as final quantity output.",
            "- Do not treat NotebookLM answers as final authority.",
            "- Do not publish private source names or results outside the private review context.",
            "",
        ]
    )
    return "\n".join(lines)


def write_notebooklm_handoff(content: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
