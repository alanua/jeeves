"""Gemini auditor packet builder for Construction Takeoff pilots."""

from __future__ import annotations

import json
from pathlib import Path

from .schemas import PilotConfig, SourceRecord


def build_gemini_packet(config: PilotConfig, records: list[SourceRecord]) -> dict[str, object]:
    return {
        "schema_version": "gemini_adapter.input.v1",
        "packet_id": f"construction-takeoff-{config.scope}",
        "objective": "Review preliminary Construction Takeoff source inventory and identify risks before extraction.",
        "mode": "mock",
        "privacy_level": "STRICT_REDACTION",
        "confirmed_canon": (
            "Runner/Antigravity/Codex parse private files locally. Gemini is a stateless "
            "second-brain auditor only. NotebookLM is private evidence memory/result-reading "
            "layer only. PDF selects current visual state; vector files provide measurements "
            "only after matching to the current PDF variant."
        ),
        "evidence": {
            "scope": config.scope,
            "targets": list(config.targets),
            "source_priority": config.source_priority,
            "source_counts": _source_counts(records),
            "records": [record.to_row() for record in records],
        },
        "draft_artifact": "source_inventory.csv and initial review_items.csv placeholders",
        "exact_questions": [
            "Are source roles and priorities internally consistent?",
            "Which source types are missing for the requested targets?",
            "Which files should be reviewed before room and wall area extraction?",
            "Which risks should be represented in REVIEW_ITEMS before proceeding?",
        ],
        "forbidden_actions": [
            "Do not execute commands.",
            "Do not claim final quantities.",
            "Do not request secrets or credentials.",
            "Do not treat Gemini as geometry source of record.",
            "Do not publish private drawing data.",
        ],
    }


def write_gemini_packet(packet: dict[str, object], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _source_counts(records: list[SourceRecord]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        counts[record.source_type] = counts.get(record.source_type, 0) + 1
    return counts
