"""Data schemas for the Construction Takeoff parser pilot.

The pilot keeps all real source paths private. Public reports should contain only
artifact names, statuses, and review categories.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

SourceType = Literal["pdf", "dxf", "dwg", "pln", "scan", "folder", "other"]
ParseStatus = Literal["pending", "parsed", "unsupported", "failed_parse", "metadata_only"]


@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    private_source_ref: str
    source_type: SourceType
    file_format: str
    floor_or_scope: str
    source_role: str
    priority_for_this_object: str
    parse_status: ParseStatus
    notes: str = ""

    def to_row(self) -> dict[str, str]:
        return {key: str(value) for key, value in asdict(self).items()}


@dataclass(frozen=True)
class ReviewItem:
    review_item_id: str
    severity: Literal["info", "warning", "blocker"]
    entity_type: str
    entity_id: str
    issue: str
    recommended_action: str
    status: str = "open"
    notes: str = ""

    def to_row(self) -> dict[str, str]:
        return {key: str(value) for key, value in asdict(self).items()}


@dataclass(frozen=True)
class PilotConfig:
    source_dir: Path
    output_dir: Path
    scope: str
    targets: tuple[str, ...]
    source_priority: str
    gemini_packet_only: bool
    notebooklm_handoff: bool


@dataclass(frozen=True)
class ArtifactSet:
    source_inventory_csv: Path
    pdf_text_blocks_csv: Path
    dxf_layers_csv: Path
    dxf_entities_summary_csv: Path
    review_items_csv: Path
    workbook_manifest_csv: Path
    gemini_intake_packet_json: Path
    notebooklm_handoff_md: Path
    runner_log_md: Path
