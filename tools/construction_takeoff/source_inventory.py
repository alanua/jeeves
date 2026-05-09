"""Source inventory builder for private Construction Takeoff pilots."""

from __future__ import annotations

import csv
from pathlib import Path

from .schemas import SourceRecord


SOURCE_TYPE_BY_SUFFIX = {
    ".pdf": "pdf",
    ".dxf": "dxf",
    ".dwg": "dwg",
    ".pln": "pln",
    ".jpg": "scan",
    ".jpeg": "scan",
    ".png": "scan",
    ".webp": "scan",
}


def classify_source(path: Path) -> str:
    if path.is_dir():
        return "folder"
    return SOURCE_TYPE_BY_SUFFIX.get(path.suffix.lower(), "other")


def infer_floor_or_scope(name: str, default_scope: str) -> str:
    lowered = name.lower()
    floor_markers = {
        "kellergeschoss": "kellergeschoss",
        "erdgeschoss": "erdgeschoss",
        "obergeschoss 1": "obergeschoss_1",
        "obergeschoss 2": "obergeschoss_2",
        "obergeschoss 3": "obergeschoss_3",
        "dachgeschoss": "dachgeschoss",
    }
    for marker, value in floor_markers.items():
        if marker in lowered:
            return value
    return default_scope


def source_role_for(source_type: str, name: str) -> str:
    lowered = name.lower()
    if "legende" in lowered:
        return "legend_dictionary"
    if source_type == "pdf":
        return "current_visual_version_or_control"
    if source_type in {"dxf", "dwg"}:
        return "vector_measurement_candidate"
    if source_type == "pln":
        return "upstream_archicad_source_metadata_only"
    if source_type == "scan":
        return "field_or_visual_check"
    if source_type == "folder":
        return "supporting_source_folder"
    return "context_or_unclassified"


def priority_for(source_type: str, name: str, source_priority: str) -> str:
    lowered = name.lower()
    if "legende" in lowered:
        return "mandatory_interpretation_layer"
    if source_priority == "pdf_current_vector_measurement":
        if source_type == "pdf":
            return "pdf_current_variant_selector"
        if source_type in {"dxf", "dwg"}:
            return "vector_measurement_after_pdf_match"
    return "standard_priority"


def build_source_inventory(source_dir: Path, scope: str, source_priority: str) -> list[SourceRecord]:
    if not source_dir.exists():
        raise FileNotFoundError(f"source directory does not exist: {source_dir}")
    if not source_dir.is_dir():
        raise NotADirectoryError(f"source path is not a directory: {source_dir}")

    records: list[SourceRecord] = []
    for index, path in enumerate(sorted(source_dir.iterdir(), key=lambda item: item.name.lower()), start=1):
        source_type = classify_source(path)
        parse_status = "pending" if source_type in {"pdf", "dxf", "dwg"} else "metadata_only"
        records.append(
            SourceRecord(
                source_id=f"SRC-{index:04d}",
                private_source_ref=path.name,
                source_type=source_type,  # type: ignore[arg-type]
                file_format=path.suffix.lower().lstrip(".") if path.suffix else "folder",
                floor_or_scope=infer_floor_or_scope(path.name, scope),
                source_role=source_role_for(source_type, path.name),
                priority_for_this_object=priority_for(source_type, path.name, source_priority),
                parse_status=parse_status,  # type: ignore[arg-type]
                notes="",
            )
        )
    return records


def write_source_inventory(records: list[SourceRecord], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(SourceRecord.__dataclass_fields__.keys())
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(record.to_row())
