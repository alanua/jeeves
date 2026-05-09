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
PrelimStatus = Literal[
    "candidate_review_required",
    "placeholder_review_required",
    "unsupported",
    "failed_parse",
    "no_candidates",
]


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
class RoomPrelim:
    room_prelim_id: str
    source_ref: str
    source_entity_id: str
    source_layer: str
    area_raw: str
    area_unit: str
    confidence: str
    status: PrelimStatus
    review_required: str = "yes"
    version_match_status: str = "not_performed"
    notes: str = "Preliminary closed-polyline candidate only; not a final quantity claim."

    def to_row(self) -> dict[str, str]:
        return {key: str(value) for key, value in asdict(self).items()}


@dataclass(frozen=True)
class WallPrelim:
    wall_prelim_id: str
    source_ref: str
    source_entity_id: str
    source_layer: str
    length_raw: str
    height_raw: str
    area_raw: str
    unit: str
    confidence: str
    status: PrelimStatus = "placeholder_review_required"
    review_required: str = "yes"
    version_match_status: str = "not_performed"
    notes: str = "Wall extraction is not implemented in this public-safe v0 scaffold."

    def to_row(self) -> dict[str, str]:
        return {key: str(value) for key, value in asdict(self).items()}


@dataclass(frozen=True)
class CrosscheckRow:
    crosscheck_id: str
    check_name: str
    source_refs: str
    status: str
    review_required: str
    notes: str

    def to_row(self) -> dict[str, str]:
        return {key: str(value) for key, value in asdict(self).items()}


@dataclass(frozen=True)
class AssumptionRow:
    assumption_id: str
    scope: str
    assumption: str
    status: str
    review_required: str
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
    rooms_prelim_csv: Path
    walls_prelim_csv: Path
    crosscheck_matrix_csv: Path
    assumptions_csv: Path
    review_items_csv: Path
    workbook_manifest_csv: Path
    workbook_xlsx: Path
    gemini_intake_packet_json: Path
    notebooklm_handoff_md: Path
    runner_log_md: Path
