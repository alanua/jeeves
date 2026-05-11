"""Construction Takeoff fact-extraction pipeline scaffold.

This module models the Aufmass workflow as source corpus -> structured facts ->
crosschecks/review packets. It deliberately does not produce final billable
quantities. Every extracted candidate remains source-linked and review-aware.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .dxf_probe import extract_closed_polyline_room_candidates, probe_dxf
from .pdf_extract import extract_pdf_text_blocks
from .source_inventory import classify_source
from .workbook_export import write_workbook_manifest, write_workbook_xlsx

WORKBOOK_VERSION = "v4"

FACT_STATUSES = [
    "AUTO_EXTRACTED",
    "CHECKED",
    "FIELD_MEASURED_CURRENT_STATE",
    "FIELD_MEASURED_FROM_METERRISS",
    "ASSUMED_FROM_TYPICAL",
    "NEEDS_FFB_OFFSET",
    "NEEDS_DATUM_CHECK",
    "NEEDS_SCALE_CHECK",
    "NEEDS_SECTION_MAPPING",
    "NEEDS_GEOMETRY_REVIEW",
    "NEEDS_VISUAL_REVIEW",
    "CONFLICT",
    "CONFLICT_HEIGHT",
    "CONFLICT_AREA",
    "LOW_PRIORITY_CONTEXT",
    "METADATA_ONLY",
    "CONTEXT_ONLY",
    "NOT_AVAILABLE",
    "FAILED_PARSE",
]

PRIVACY_LEVELS = [
    "PRIVATE_RAW",
    "PRIVATE_DERIVED",
    "INTERNAL_RUNNER_ONLY",
    "REDACTED_REVIEW",
    "PUBLIC_SAFE",
]

TABLE_ORDER = [
    "Dashboard",
    "INPUT_SOURCES",
    "GLOBAL_COORD_MAP",
    "AXES_INDEX",
    "SECTION_CUTS_INDEX",
    "SCALE_ANCHORS",
    "LEGEND_DICTIONARY",
    "ROOMS_PRELIM",
    "ROOM_LABELS_RAW",
    "ROOM_CONTOUR_CANDIDATES",
    "HEIGHT_MEASUREMENTS_PRELIM",
    "MEASUREMENT_DATUM_REVIEW",
    "OPENINGS_PRELIM",
    "WINDOW_SCHEDULE_PRELIM",
    "DOOR_SCHEDULE_PRELIM",
    "WALLS_PRELIM",
    "FACADES_PRELIM",
    "FACADE_OPENINGS",
    "SECTIONS_INDEX",
    "SECTION_HEIGHTS",
    "ANNOTATIONS_PRELIM",
    "CROSSCHECK_MATRIX",
    "SOURCE_RELATION_MAP",
    "REVIEW_ITEMS",
    "ASSUMPTIONS",
    "DXF_PARSE_LOG",
    "PDF_PARSE_LOG",
    "SCAN_INVENTORY",
    "ARCHICAD_EXPORT_REQUESTS",
    "DWG_CONVERSION_QUEUE",
    "RENDERED_PREVIEW_INDEX",
    "QUANTITY_FORMULAS",
    "TOLERANCE_RULES",
    "QUESTIONS_FOR_OLEKSII",
]

SOURCE_FIELDS = [
    "source_id",
    "file_name",
    "file_type",
    "folder",
    "source_role",
    "building_part",
    "floor",
    "drawing_date",
    "revision_index",
    "source_priority_by_revision",
    "duplicate_group",
    "outdated_source_status",
    "source_snapshot_date",
    "parse_status",
    "notes",
]

FACT_FIELDS = [
    "fact_id",
    "entity_id",
    "entity_type",
    "attribute",
    "value",
    "unit",
    "source_file",
    "source_type",
    "source_layer",
    "source_entity_id",
    "extraction_method",
    "confidence",
    "status",
    "notes",
]

TABLE_FIELDS: dict[str, list[str]] = {
    "Dashboard": ["key", "value", "status", "notes"],
    "INPUT_SOURCES": SOURCE_FIELDS,
    "GLOBAL_COORD_MAP": FACT_FIELDS,
    "AXES_INDEX": FACT_FIELDS,
    "SECTION_CUTS_INDEX": FACT_FIELDS,
    "SCALE_ANCHORS": FACT_FIELDS,
    "LEGEND_DICTIONARY": FACT_FIELDS,
    "ROOMS_PRELIM": [
        "room_id",
        "building_part",
        "floor",
        "unit_id",
        "room_name",
        "printed_area_m2",
        "calculated_area_m2",
        "perimeter_m",
        "height_m",
        "source_file",
        "source_type",
        "source_entity_id",
        "source_layer",
        "extraction_method",
        "confidence",
        "status",
        "notes",
    ],
    "ROOM_LABELS_RAW": FACT_FIELDS,
    "ROOM_CONTOUR_CANDIDATES": FACT_FIELDS,
    "HEIGHT_MEASUREMENTS_PRELIM": FACT_FIELDS,
    "MEASUREMENT_DATUM_REVIEW": FACT_FIELDS,
    "OPENINGS_PRELIM": FACT_FIELDS,
    "WINDOW_SCHEDULE_PRELIM": FACT_FIELDS,
    "DOOR_SCHEDULE_PRELIM": FACT_FIELDS,
    "WALLS_PRELIM": FACT_FIELDS,
    "FACADES_PRELIM": FACT_FIELDS,
    "FACADE_OPENINGS": FACT_FIELDS,
    "SECTIONS_INDEX": FACT_FIELDS,
    "SECTION_HEIGHTS": FACT_FIELDS,
    "ANNOTATIONS_PRELIM": FACT_FIELDS,
    "CROSSCHECK_MATRIX": [
        "check_id",
        "check_name",
        "left_source",
        "right_source",
        "conflict_type",
        "status",
        "confidence",
        "notes",
    ],
    "SOURCE_RELATION_MAP": [
        "relation_id",
        "left_source",
        "right_source",
        "relation_type",
        "status",
        "confidence",
        "notes",
    ],
    "REVIEW_ITEMS": [
        "review_item_id",
        "severity",
        "entity_type",
        "entity_id",
        "issue",
        "recommended_action",
        "status",
        "notes",
    ],
    "ASSUMPTIONS": [
        "assumption_id",
        "scope",
        "assumption",
        "status",
        "review_required",
        "notes",
    ],
    "DXF_PARSE_LOG": [
        "source_file",
        "parse_status",
        "layer_count",
        "entity_summary_count",
        "room_candidate_count",
        "notes",
    ],
    "PDF_PARSE_LOG": ["source_file", "parse_status", "text_block_count", "notes"],
    "SCAN_INVENTORY": SOURCE_FIELDS,
    "ARCHICAD_EXPORT_REQUESTS": [
        "export_id",
        "export_name",
        "required",
        "purpose",
        "status",
        "notes",
    ],
    "DWG_CONVERSION_QUEUE": [
        "conversion_id",
        "source_file",
        "preferred_tool",
        "fallback_tools",
        "output_expected",
        "status",
        "notes",
    ],
    "RENDERED_PREVIEW_INDEX": [
        "preview_id",
        "source_file",
        "preview_type",
        "output_path",
        "status",
        "notes",
    ],
    "QUANTITY_FORMULAS": [
        "formula_id",
        "quantity_name",
        "formula",
        "allowed_when",
        "status",
        "notes",
    ],
    "TOLERANCE_RULES": [
        "tolerance_id",
        "check_name",
        "value",
        "unit",
        "status",
        "notes",
    ],
    "QUESTIONS_FOR_OLEKSII": [
        "question_id",
        "category",
        "entity_ref",
        "question",
        "priority",
        "status",
        "notes",
    ],
}


@dataclass(frozen=True)
class FactExtractionConfig:
    source_dir: Path
    output_dir: Path
    object_id: str
    scope: str
    run_id: str
    source_snapshot_date: str
    workbook_name: str
    allow_overwrite: bool = False


@dataclass(frozen=True)
class FactExtractionResult:
    output_dir: Path
    csv_dir: Path
    log_dir: Path
    workbook_xlsx: Path
    workbook_manifest_csv: Path
    gemini_intake_packet_json: Path
    notebooklm_handoff_md: Path
    gemini_audit_report_md: Path
    questions_for_oleksii_md: Path
    run_report_txt: Path


def default_run_id() -> str:
    return datetime.now(timezone.utc).strftime("run_%Y%m%d_%H%M%S")


def run_fact_extraction_pipeline(config: FactExtractionConfig) -> FactExtractionResult:
    _prepare_output_dir(config.output_dir, config.allow_overwrite)

    csv_dir = config.output_dir / "csv"
    log_dir = config.output_dir / "logs"
    preview_dir = config.output_dir / "rendered_previews"
    csv_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    preview_dir.mkdir(parents=True, exist_ok=True)

    result = FactExtractionResult(
        output_dir=config.output_dir,
        csv_dir=csv_dir,
        log_dir=log_dir,
        workbook_xlsx=config.output_dir / config.workbook_name,
        workbook_manifest_csv=config.output_dir / "workbook_manifest.csv",
        gemini_intake_packet_json=config.output_dir / "gemini_intake_packet.json",
        notebooklm_handoff_md=config.output_dir / "notebooklm_handoff.md",
        gemini_audit_report_md=config.output_dir / "gemini_audit_report.md",
        questions_for_oleksii_md=config.output_dir / "questions_for_oleksii.md",
        run_report_txt=log_dir / "run_report.txt",
    )

    source_rows = build_input_sources(config.source_dir, config.source_snapshot_date)
    rows_by_table = _initial_empty_tables()

    rows_by_table["Dashboard"] = _dashboard_rows(config, source_rows)
    rows_by_table["INPUT_SOURCES"] = source_rows
    rows_by_table["SCAN_INVENTORY"] = [
        row for row in source_rows if row["source_role"] == "SCAN_FIELD_MEASUREMENT"
    ]
    rows_by_table["ARCHICAD_EXPORT_REQUESTS"] = _archicad_export_requests()
    rows_by_table["DWG_CONVERSION_QUEUE"] = _dwg_conversion_queue(source_rows)
    rows_by_table["RENDERED_PREVIEW_INDEX"] = _rendered_preview_index(
        source_rows, preview_dir
    )
    rows_by_table["QUANTITY_FORMULAS"] = _quantity_formula_rows()
    rows_by_table["TOLERANCE_RULES"] = _tolerance_rule_rows()
    rows_by_table["ASSUMPTIONS"] = _assumption_rows(config)
    rows_by_table["CROSSCHECK_MATRIX"] = _crosscheck_seed_rows()
    rows_by_table["SOURCE_RELATION_MAP"] = _source_relation_rows(source_rows)
    rows_by_table["REVIEW_ITEMS"] = _review_seed_rows(source_rows)
    rows_by_table["QUESTIONS_FOR_OLEKSII"] = _questions_seed_rows()
    rows_by_table["GLOBAL_COORD_MAP"] = _global_coord_rows(source_rows)
    rows_by_table["SCALE_ANCHORS"] = _scale_anchor_seed_rows(source_rows)
    rows_by_table["SECTION_CUTS_INDEX"] = _section_cut_seed_rows(source_rows)

    _extract_pdf_facts(config.source_dir, source_rows, rows_by_table)
    _extract_dxf_facts(config.source_dir, source_rows, rows_by_table)

    csv_paths = []
    for table_name in TABLE_ORDER:
        csv_path = csv_dir / f"{_table_file_name(table_name)}.csv"
        _write_rows(csv_path, TABLE_FIELDS[table_name], rows_by_table[table_name])
        csv_paths.append(csv_path)

    workbook_created = write_workbook_xlsx(csv_paths, result.workbook_xlsx)
    write_workbook_manifest(
        [
            *csv_paths,
            result.workbook_xlsx,
            result.gemini_intake_packet_json,
            result.notebooklm_handoff_md,
            result.gemini_audit_report_md,
            result.questions_for_oleksii_md,
            result.run_report_txt,
        ],
        result.workbook_manifest_csv,
    )

    _write_gemini_intake_packet(config, result, rows_by_table)
    _write_notebooklm_handoff(config, result)
    _write_gemini_audit_placeholder(config, result)
    _write_questions_for_oleksii(result, rows_by_table["QUESTIONS_FOR_OLEKSII"])
    _write_run_report(config, result, rows_by_table, workbook_created)

    return result


def build_input_sources(source_dir: Path, source_snapshot_date: str) -> list[dict[str, str]]:
    if not source_dir.exists():
        raise FileNotFoundError(f"source directory does not exist: {source_dir}")
    if not source_dir.is_dir():
        raise NotADirectoryError(f"source path is not a directory: {source_dir}")

    paths = _iter_source_paths(source_dir)
    duplicate_groups = _duplicate_groups(paths)
    rows = []
    for index, path in enumerate(paths, start=1):
        relative = path.relative_to(source_dir).as_posix()
        source_type = classify_source(path)
        drawing_date = _extract_drawing_date(path.name)
        duplicate_group = duplicate_groups.get(_duplicate_key(path), "")
        outdated_status = _outdated_status(path, paths, duplicate_group)
        source_role = _source_role(path, source_type)
        rows.append(
            {
                "source_id": f"SRC-{index:04d}",
                "file_name": relative,
                "file_type": source_type,
                "folder": path.parent.relative_to(source_dir).as_posix()
                if path.parent != source_dir
                else ".",
                "source_role": source_role,
                "building_part": _building_part(path.name),
                "floor": _floor(path.name),
                "drawing_date": drawing_date,
                "revision_index": _revision_index(path.name),
                "source_priority_by_revision": _source_priority_by_revision(
                    source_type, source_role, outdated_status
                ),
                "duplicate_group": duplicate_group,
                "outdated_source_status": outdated_status,
                "source_snapshot_date": source_snapshot_date,
                "parse_status": "pending"
                if source_type in {"pdf", "dxf", "dwg"}
                else "metadata_only",
                "notes": _source_notes(path, source_type, source_role),
            }
        )
    return rows


def _prepare_output_dir(output_dir: Path, allow_overwrite: bool) -> None:
    if output_dir.exists() and any(output_dir.iterdir()) and not allow_overwrite:
        raise FileExistsError(
            f"output directory is not empty: {output_dir}. "
            "Use a new run_id/output path or pass --allow-overwrite."
        )
    output_dir.mkdir(parents=True, exist_ok=True)


def _initial_empty_tables() -> dict[str, list[dict[str, str]]]:
    return {table_name: [] for table_name in TABLE_ORDER}


def _dashboard_rows(
    config: FactExtractionConfig, source_rows: list[dict[str, str]]
) -> list[dict[str, str]]:
    counts: dict[str, int] = {}
    for row in source_rows:
        counts[row["file_type"]] = counts.get(row["file_type"], 0) + 1
    return [
        {
            "key": "process_name",
            "value": "construction_takeoff_fact_extraction",
            "status": "CHECKED",
            "notes": "Pipeline models raw drawing corpus as structured Aufmass facts.",
        },
        {
            "key": "object_id",
            "value": config.object_id,
            "status": "PRIVATE_DERIVED",
            "notes": "",
        },
        {"key": "scope", "value": config.scope, "status": "CHECKED", "notes": ""},
        {"key": "run_id", "value": config.run_id, "status": "CHECKED", "notes": ""},
        {
            "key": "source_snapshot_date",
            "value": config.source_snapshot_date,
            "status": "CHECKED",
            "notes": "",
        },
        {
            "key": "workbook_version",
            "value": WORKBOOK_VERSION,
            "status": "CHECKED",
            "notes": "",
        },
        {
            "key": "source_counts",
            "value": json.dumps(counts, sort_keys=True),
            "status": "AUTO_EXTRACTED",
            "notes": "Counts are metadata only; not a quantity claim.",
        },
        {
            "key": "final_quantities_allowed",
            "value": "false",
            "status": "CHECKED",
            "notes": "This run produces preliminary facts and review items only.",
        },
    ]


def _extract_pdf_facts(
    source_dir: Path,
    source_rows: list[dict[str, str]],
    rows_by_table: dict[str, list[dict[str, str]]],
) -> None:
    for source in source_rows:
        if source["file_type"] != "pdf":
            continue
        path = source_dir / source["file_name"]
        rows = extract_pdf_text_blocks(path)
        parsed_count = sum(row.get("status") == "parsed" for row in rows)
        rows_by_table["PDF_PARSE_LOG"].append(
            {
                "source_file": source["file_name"],
                "parse_status": "parsed"
                if parsed_count
                else rows[0].get("status", "FAILED_PARSE"),
                "text_block_count": str(parsed_count),
                "notes": rows[0].get("notes", "") if rows else "",
            }
        )
        for row in rows:
            text = row.get("text", "")
            if not text:
                continue
            category = _annotation_category(text)
            fact = _fact_row(
                fact_id=f"TXT-{len(rows_by_table['ANNOTATIONS_PRELIM']) + 1:04d}",
                entity_id=f"{source['source_id']}:p{row.get('page')}:b{row.get('block_index')}",
                entity_type="pdf_text",
                attribute=category,
                value=text,
                unit="text",
                source_file=source["file_name"],
                source_type="pdf",
                source_layer="",
                source_entity_id="",
                extraction_method="pymupdf_text_probe",
                confidence="0.35",
                status="AUTO_EXTRACTED",
                notes="PDF text is evidence for labels/annotations only; visual review still required.",
            )
            rows_by_table["ANNOTATIONS_PRELIM"].append(fact)
            if _looks_like_room_label(text):
                label = dict(fact)
                label["fact_id"] = (
                    f"ROOM-LABEL-{len(rows_by_table['ROOM_LABELS_RAW']) + 1:04d}"
                )
                label["entity_type"] = "room_label_candidate"
                rows_by_table["ROOM_LABELS_RAW"].append(label)


def _extract_dxf_facts(
    source_dir: Path,
    source_rows: list[dict[str, str]],
    rows_by_table: dict[str, list[dict[str, str]]],
) -> None:
    for source in source_rows:
        if source["file_type"] != "dxf":
            continue
        path = source_dir / source["file_name"]
        try:
            layer_rows, entity_rows = probe_dxf(path)
            layer_count = sum(row.get("status") == "parsed" for row in layer_rows)
            entity_count = sum(row.get("status") == "parsed" for row in entity_rows)
            parse_status = (
                "parsed"
                if layer_count or entity_count
                else layer_rows[0].get("status", "FAILED_PARSE")
            )
            parse_notes = layer_rows[0].get("notes", "") if layer_rows else ""
        except Exception as exc:  # pragma: no cover - parser internals/environment
            layer_count = 0
            entity_count = 0
            parse_status = "failed_parse"
            parse_notes = f"{type(exc).__name__}: {exc}"

        candidates = extract_closed_polyline_room_candidates(path)
        candidate_count = sum(row.status == "candidate_review_required" for row in candidates)
        rows_by_table["DXF_PARSE_LOG"].append(
            {
                "source_file": source["file_name"],
                "parse_status": parse_status,
                "layer_count": str(layer_count),
                "entity_summary_count": str(entity_count),
                "room_candidate_count": str(candidate_count),
                "notes": parse_notes,
            }
        )

        for candidate in candidates:
            rows_by_table["ROOM_CONTOUR_CANDIDATES"].append(
                _fact_row(
                    fact_id=f"ROOM-CONTOUR-{len(rows_by_table['ROOM_CONTOUR_CANDIDATES']) + 1:04d}",
                    entity_id=candidate.room_prelim_id,
                    entity_type="room_contour_candidate",
                    attribute="area_candidate",
                    value=candidate.area_raw,
                    unit=candidate.area_unit,
                    source_file=source["file_name"],
                    source_type="dxf",
                    source_layer=candidate.source_layer,
                    source_entity_id=candidate.source_entity_id,
                    extraction_method="ezdxf_closed_polyline_shoelace_area",
                    confidence=candidate.confidence,
                    status=_map_prelim_status(candidate.status),
                    notes=(
                        "Raw closed-polyline geometry candidate only. "
                        "Not merged into ROOMS_PRELIM until label/area/geometry review."
                    ),
                )
            )


def _fact_row(
    *,
    fact_id: str,
    entity_id: str,
    entity_type: str,
    attribute: str,
    value: str,
    unit: str,
    source_file: str,
    source_type: str,
    source_layer: str,
    source_entity_id: str,
    extraction_method: str,
    confidence: str,
    status: str,
    notes: str,
) -> dict[str, str]:
    return {
        "fact_id": fact_id,
        "entity_id": entity_id,
        "entity_type": entity_type,
        "attribute": attribute,
        "value": value,
        "unit": unit,
        "source_file": source_file,
        "source_type": source_type,
        "source_layer": source_layer,
        "source_entity_id": source_entity_id,
        "extraction_method": extraction_method,
        "confidence": confidence,
        "status": status,
        "notes": notes,
    }


def _placeholder_fact(table_name: str, fact_id: str, notes: str) -> dict[str, str]:
    return _fact_row(
        fact_id=fact_id,
        entity_id="",
        entity_type=table_name.lower(),
        attribute="not_available",
        value="",
        unit="",
        source_file="",
        source_type="",
        source_layer="",
        source_entity_id="",
        extraction_method="not_implemented_in_v0",
        confidence="0.00",
        status="NOT_AVAILABLE",
        notes=notes,
    )


def _global_coord_rows(source_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for source in source_rows:
        if source["source_role"] == "GLOBAL_AXIS_MAP":
            rows.append(
                _fact_row(
                    fact_id=f"GLOBAL-MAP-{len(rows) + 1:04d}",
                    entity_id=source["source_id"],
                    entity_type="global_axis_coordination_map",
                    attribute="source_file",
                    value=source["file_name"],
                    unit="file_ref",
                    source_file=source["file_name"],
                    source_type=source["file_type"],
                    source_layer="",
                    source_entity_id="",
                    extraction_method="filename_role_classifier",
                    confidence="0.60",
                    status="NEEDS_GEOMETRY_REVIEW",
                    notes=(
                        "Treat as whole-object coordination candidate, not only as one floor. "
                        "Axes, section cuts, scale anchors, facades, and floor alignment need extraction."
                    ),
                )
            )
    return rows or [
        _placeholder_fact(
            "GLOBAL_COORD_MAP",
            "GLOBAL-MAP-0001",
            "No global coordination file was auto-identified.",
        )
    ]


def _scale_anchor_seed_rows(source_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    vector_sources = [row for row in source_rows if row["file_type"] in {"dxf", "dwg", "pdf"}]
    if not vector_sources:
        return [
            _placeholder_fact(
                "SCALE_ANCHORS",
                "SCALE-0001",
                "No vector/PDF sources available for scale anchors.",
            )
        ]
    return [
        _fact_row(
            fact_id="SCALE-0001",
            entity_id="source_set",
            entity_type="scale_anchor",
            attribute="scale_anchor_status",
            value="not_found",
            unit="status",
            source_file=", ".join(row["file_name"] for row in vector_sources[:5]),
            source_type="mixed",
            source_layer="",
            source_entity_id="",
            extraction_method="v0_seed_gate",
            confidence="0.00",
            status="NEEDS_SCALE_CHECK",
            notes="Scale anchors must be extracted or confirmed before final measurement use.",
        )
    ]


def _section_cut_seed_rows(source_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    section_sources = [row for row in source_rows if row["source_role"] == "SECTION"]
    if not section_sources:
        return [
            _placeholder_fact(
                "SECTION_CUTS_INDEX",
                "SECTION-CUT-0001",
                "No section source was auto-identified.",
            )
        ]
    return [
        _fact_row(
            fact_id=f"SECTION-CUT-{index:04d}",
            entity_id=row["source_id"],
            entity_type="section_source",
            attribute="section_mapping_status",
            value=row["file_name"],
            unit="file_ref",
            source_file=row["file_name"],
            source_type=row["file_type"],
            source_layer="",
            source_entity_id="",
            extraction_method="filename_role_classifier",
            confidence="0.45",
            status="NEEDS_SECTION_MAPPING",
            notes="Section cut position must be mapped to the global coordination map.",
        )
        for index, row in enumerate(section_sources, start=1)
    ]


def _source_relation_rows(source_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    relations = []
    by_floor: dict[str, list[dict[str, str]]] = {}
    for row in source_rows:
        by_floor.setdefault(row["floor"], []).append(row)
    for floor, rows in sorted(by_floor.items()):
        pdfs = [row for row in rows if row["file_type"] == "pdf"]
        vectors = [row for row in rows if row["file_type"] in {"dxf", "dwg"}]
        for pdf in pdfs:
            for vector in vectors:
                relations.append(
                    {
                        "relation_id": f"REL-{len(relations) + 1:04d}",
                        "left_source": pdf["file_name"],
                        "right_source": vector["file_name"],
                        "relation_type": f"same_floor_candidate:{floor}",
                        "status": "NEEDS_VISUAL_REVIEW",
                        "confidence": "0.35",
                        "notes": "Filename/floor pairing only; revision and geometry match are not confirmed.",
                    }
                )
    return relations or [
        {
            "relation_id": "REL-0001",
            "left_source": "",
            "right_source": "",
            "relation_type": "not_available",
            "status": "NOT_AVAILABLE",
            "confidence": "0.00",
            "notes": "No source relations were auto-created.",
        }
    ]


def _crosscheck_seed_rows() -> list[dict[str, str]]:
    checks = [
        ("PDF_area_vs_DXF_area", "CONFLICT_AREA"),
        ("DXF_dimension_vs_scale_anchor", "CONFLICT_SCALE"),
        ("floor_plan_vs_section_cut", "NEEDS_SECTION_MAPPING"),
        ("section_height_vs_scan_height", "CONFLICT_HEIGHT"),
        ("facade_window_vs_plan_opening", "CONFLICT_OPENING"),
        ("scan_No_Np_vs_window_schedule", "NEEDS_DATUM_CHECK"),
        ("room_height_vs_floor_build_up", "NEEDS_DATUM_CHECK"),
        ("DG_plan_vs_roof_section", "NEEDS_VISUAL_REVIEW"),
    ]
    return [
        {
            "check_id": f"CHECK-{index:04d}",
            "check_name": check_name,
            "left_source": "",
            "right_source": "",
            "conflict_type": conflict_type,
            "status": "NOT_AVAILABLE",
            "confidence": "0.00",
            "notes": "Crosscheck registered but not performed in v0 scaffold.",
        }
        for index, (check_name, conflict_type) in enumerate(checks, start=1)
    ]


def _review_seed_rows(source_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = [
        {
            "review_item_id": "RI-0001",
            "severity": "warning",
            "entity_type": "pipeline",
            "entity_id": "all",
            "issue": "Final billable quantities are intentionally disabled.",
            "recommended_action": "Use this workbook as a precheck and review queue only.",
            "status": "open",
            "notes": "Facts require source/status/confidence and human review before final use.",
        }
    ]
    if any(row["file_type"] == "pln" for row in source_rows):
        rows.append(
            {
                "review_item_id": f"RI-{len(rows) + 1:04d}",
                "severity": "info",
                "entity_type": "archicad",
                "entity_id": "pln",
                "issue": "PLN sources are metadata-only in this pipeline.",
                "recommended_action": "Request IFC, DXF floor plans, DXF sections/facades, PDFs, and schedules from Archicad.",
                "status": "open",
                "notes": "Direct PLN parsing is intentionally out of scope.",
            }
        )
    if any(row["file_type"] == "dwg" for row in source_rows):
        rows.append(
            {
                "review_item_id": f"RI-{len(rows) + 1:04d}",
                "severity": "warning",
                "entity_type": "dwg_conversion",
                "entity_id": "dwg",
                "issue": "DWG sources require controlled conversion before vector extraction.",
                "recommended_action": "Use ODA File Converter or CAD fallback and capture conversion_log.",
                "status": "open",
                "notes": "Converted DXF must be linked back to the original DWG source.",
            }
        )
    if not any(row["source_role"] == "GLOBAL_AXIS_MAP" for row in source_rows):
        rows.append(
            {
                "review_item_id": f"RI-{len(rows) + 1:04d}",
                "severity": "warning",
                "entity_type": "global_coordination",
                "entity_id": "GLOBAL_COORD_MAP",
                "issue": "No whole-object global axis coordination map was identified.",
                "recommended_action": "Select or name the global axis map source before cross-floor alignment.",
                "status": "open",
                "notes": "",
            }
        )
    return rows


def _assumption_rows(config: FactExtractionConfig) -> list[dict[str, str]]:
    return [
        {
            "assumption_id": "ASSUMP-0001",
            "scope": config.scope,
            "assumption": "DXF/DWG-derived geometry is primary geometry evidence after revision and scale checks.",
            "status": "open",
            "review_required": "yes",
            "notes": "PDF remains a control/visual source; scans remain current-state field evidence.",
        },
        {
            "assumption_id": "ASSUMP-0002",
            "scope": "Dachgeschoss",
            "assumption": "DG ceilings may be sloped and must not default to horizontal ceiling area.",
            "status": "open",
            "review_required": "yes",
            "notes": "Requires section/roof geometry review.",
        },
    ]


def _questions_seed_rows() -> list[dict[str, str]]:
    return [
        {
            "question_id": "Q-0001",
            "category": "source_revision",
            "entity_ref": "INPUT_SOURCES",
            "question": "Which PDF/DXF revision is the current contractual measurement basis?",
            "priority": "high",
            "status": "open",
            "notes": "",
        },
        {
            "question_id": "Q-0002",
            "category": "height_datum",
            "entity_ref": "HEIGHT_MEASUREMENTS_PRELIM",
            "question": "Which field heights are measured from Meterriss and which need OK FFB offset?",
            "priority": "high",
            "status": "open",
            "notes": "",
        },
        {
            "question_id": "Q-0003",
            "category": "dg_ceiling",
            "entity_ref": "DG_SLOPED_CEILING_REVIEW",
            "question": "Which Dachgeschoss rooms require sloped ceiling review before ceiling area calculation?",
            "priority": "high",
            "status": "open",
            "notes": "",
        },
    ]


def _archicad_export_requests() -> list[dict[str, str]]:
    exports = [
        ("IFC", "rooms, walls, doors, windows, slabs, heights, properties"),
        ("DXF floor plans", "floor geometry, room boundaries, wall/opening candidates"),
        ("DXF sections", "levels, heights, roof slopes, stair/elevator geometry"),
        ("DXF facades", "facade geometry and opening candidates"),
        ("PDF issued drawings", "visual control, title blocks, printed areas, notes"),
        ("Room schedule XLSX/CSV", "room identity, names, printed areas"),
        ("Window/door schedule XLSX/CSV", "opening dimensions and identifiers"),
    ]
    return [
        {
            "export_id": f"ARCHICAD-EXPORT-{index:04d}",
            "export_name": name,
            "required": "yes",
            "purpose": purpose,
            "status": "requested_if_available",
            "notes": "PLN is not parsed directly; use controlled exports only.",
        }
        for index, (name, purpose) in enumerate(exports, start=1)
    ]


def _dwg_conversion_queue(source_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for source in source_rows:
        if source["file_type"] != "dwg":
            continue
        rows.append(
            {
                "conversion_id": f"DWG-CONVERT-{len(rows) + 1:04d}",
                "source_file": source["file_name"],
                "preferred_tool": "ODA File Converter",
                "fallback_tools": "AutoCAD/BricsCAD/LibreCAD/Archicad export",
                "output_expected": "converted_DXF + conversion_log",
                "status": "NEEDS_CONVERSION",
                "notes": "Do not use DWG directly for extraction until converted and logged.",
            }
        )
    return rows or [
        {
            "conversion_id": "DWG-CONVERT-0001",
            "source_file": "",
            "preferred_tool": "ODA File Converter",
            "fallback_tools": "AutoCAD/BricsCAD/LibreCAD/Archicad export",
            "output_expected": "converted_DXF + conversion_log",
            "status": "NOT_AVAILABLE",
            "notes": "No DWG sources detected.",
        }
    ]


def _rendered_preview_index(
    source_rows: list[dict[str, str]], preview_dir: Path
) -> list[dict[str, str]]:
    preview_sources = [
        row
        for row in source_rows
        if row["file_type"] in {"pdf", "dxf", "dwg", "scan"}
        or row["source_role"] in {"FACADE", "SECTION"}
    ]
    if not preview_sources:
        return [
            {
                "preview_id": "PREVIEW-0001",
                "source_file": "",
                "preview_type": "not_available",
                "output_path": preview_dir.as_posix(),
                "status": "NOT_AVAILABLE",
                "notes": "No previewable sources detected.",
            }
        ]
    return [
        {
            "preview_id": f"PREVIEW-{index:04d}",
            "source_file": row["file_name"],
            "preview_type": _preview_type(row),
            "output_path": (preview_dir / f"{index:04d}.png").as_posix(),
            "status": "NEEDS_VISUAL_REVIEW",
            "notes": "Preview rendering is indexed here; actual renderer is a later private runner step.",
        }
        for index, row in enumerate(preview_sources, start=1)
    ]


def _quantity_formula_rows() -> list[dict[str, str]]:
    formulas = [
        ("floor_area", "room_area", "room identity and area checked"),
        ("ceiling_area", "room_area unless sloped/section_override", "DG/section review complete"),
        ("wall_gross_area", "perimeter * height", "perimeter and height checked"),
        ("wall_net_area", "wall_gross_area - openings", "openings checked"),
        ("volume", "floor_area * height", "floor area and height checked"),
        ("facade_net_area", "facade_gross_area - facade_openings", "facade/opening geometry checked"),
    ]
    return [
        {
            "formula_id": f"FORMULA-{index:04d}",
            "quantity_name": name,
            "formula": formula,
            "allowed_when": allowed_when,
            "status": "CONTEXT_ONLY",
            "notes": "Formula layer only; v0 does not create final billable quantities.",
        }
        for index, (name, formula, allowed_when) in enumerate(formulas, start=1)
    ]


def _tolerance_rule_rows() -> list[dict[str, str]]:
    rules = [
        ("area_tolerance_m2", "0.10", "m2", "Tune per object before acceptance."),
        ("area_tolerance_percent", "1.00", "percent", "Tune per object before acceptance."),
        ("height_tolerance_cm", "1.00", "cm", "Needs datum/FFB context."),
        ("dimension_tolerance_cm", "1.00", "cm", "Needs scale anchor check."),
        ("scale_tolerance_percent", "0.20", "percent", "Preliminary default only."),
    ]
    return [
        {
            "tolerance_id": f"TOL-{index:04d}",
            "check_name": name,
            "value": value,
            "unit": unit,
            "status": "ASSUMED_FROM_TYPICAL",
            "notes": notes,
        }
        for index, (name, value, unit, notes) in enumerate(rules, start=1)
    ]


def _iter_source_paths(source_dir: Path) -> list[Path]:
    paths = []
    for path in source_dir.rglob("*"):
        if any(part.startswith(".") for part in path.relative_to(source_dir).parts):
            continue
        if path.is_file() or path.is_dir():
            paths.append(path)
    return sorted(paths, key=lambda item: item.relative_to(source_dir).as_posix().lower())


def _duplicate_groups(paths: list[Path]) -> dict[str, str]:
    keys: dict[str, list[Path]] = {}
    for path in paths:
        if path.is_dir():
            continue
        keys.setdefault(_duplicate_key(path), []).append(path)
    result = {}
    group_index = 1
    for key, grouped in sorted(keys.items()):
        if len(grouped) < 2:
            continue
        group_id = f"DUP-{group_index:04d}"
        group_index += 1
        result[key] = group_id
    return result


def _duplicate_key(path: Path) -> str:
    stem = path.stem.lower()
    stem = re.sub(r"\b\d{1,2}[._-]\d{1,2}[._-]\d{2,4}\b", "", stem)
    stem = re.sub(r"\brev(?:ision)?[_ -]?[a-z0-9]+\b", "", stem)
    stem = re.sub(r"\s+", " ", stem).strip()
    return f"{stem}:{path.suffix.lower()}"


def _outdated_status(path: Path, paths: list[Path], duplicate_group: str) -> str:
    if not duplicate_group:
        return "current_unknown"
    same = [candidate for candidate in paths if _duplicate_key(candidate) == _duplicate_key(path)]
    dated = [(candidate, _extract_drawing_date(candidate.name)) for candidate in same]
    dated = [(candidate, date) for candidate, date in dated if date]
    if not dated:
        return "duplicate_needs_review"
    latest = max(date for _, date in dated)
    return "current_candidate" if _extract_drawing_date(path.name) == latest else "outdated_source_candidate"


def _source_role(path: Path, source_type: str) -> str:
    name = path.name.lower()
    if path.is_dir():
        if "scan" in name or "foto" in name or "photo" in name:
            return "SCAN_FIELD_MEASUREMENT"
        return "LOW_PRIORITY_CONTEXT"
    if "1. bauabschnitt-eg" in name or ("bauabschnitt" in name and "eg" in name):
        return "GLOBAL_AXIS_MAP"
    if "legende" in name or "legend" in name:
        return "LEGEND"
    if "schnitt" in name or "section" in name:
        return "SECTION"
    if "fassade" in name or "facade" in name or "farbkonzept" in name:
        return "FACADE"
    if "wandansicht" in name or "wall elevation" in name:
        return "WALL_ELEVATION"
    if "detail" in name:
        return "DETAIL_PLAN"
    if source_type == "pln":
        return "MASTER_PLN"
    if source_type == "scan":
        return "SCAN_FIELD_MEASUREMENT"
    if source_type in {"pdf", "dxf", "dwg"}:
        return "FLOOR_PLAN"
    return "LOW_PRIORITY_CONTEXT"


def _building_part(name: str) -> str:
    upper = name.upper()
    for marker in ["VH", "SF", "HH", "NB", "TG"]:
        if re.search(rf"(^|[^A-Z0-9]){marker}([^A-Z0-9]|$)", upper):
            return marker
    return ""


def _floor(name: str) -> str:
    lowered = name.lower()
    mappings = [
        (["kellergeschoss", "kg"], "KG"),
        (["erdgeschoss", "eg"], "EG"),
        (["obergeschoss 1", "og1", "og 1", "1. og"], "OG1"),
        (["obergeschoss 2", "og2", "og 2", "2. og"], "OG2"),
        (["obergeschoss 3", "og3", "og 3", "3. og"], "OG3"),
        (["dachgeschoss", "dg"], "DG"),
    ]
    for markers, floor in mappings:
        if any(marker in lowered for marker in markers):
            return floor
    return ""


def _extract_drawing_date(name: str) -> str:
    match = re.search(r"(\d{1,2})[._-](\d{1,2})[._-](\d{2,4})", name)
    if not match:
        return ""
    day, month, year = match.groups()
    if len(year) == 2:
        year = f"20{year}"
    return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"


def _revision_index(name: str) -> str:
    match = re.search(r"\brev(?:ision)?[_ -]?([a-z0-9]+)\b", name, flags=re.IGNORECASE)
    return match.group(1).upper() if match else ""


def _source_priority_by_revision(
    source_type: str, source_role: str, outdated_status: str
) -> str:
    if outdated_status == "outdated_source_candidate":
        return "low_outdated_candidate"
    if source_role == "GLOBAL_AXIS_MAP":
        return "global_coordination_priority"
    if source_type in {"dxf", "dwg"}:
        return "primary_geometry_after_revision_check"
    if source_type == "pdf":
        return "control_source_after_revision_check"
    if source_type == "pln":
        return "metadata_only_request_exports"
    if source_type == "scan":
        return "field_measurement_current_state"
    return "context"


def _source_notes(path: Path, source_type: str, source_role: str) -> str:
    if source_role == "GLOBAL_AXIS_MAP":
        return "Use as whole-object axis/section/facade coordination candidate, not only floor-specific evidence."
    if source_type == "pln":
        return "Direct PLN parsing disabled; request IFC/DXF/PDF/schedule exports."
    if source_type == "dwg":
        return "Requires controlled conversion to DXF and conversion_log before vector extraction."
    if source_type == "scan":
        return "Current-state field evidence only; requires datum/OK FFB review."
    return ""


def _annotation_category(text: str) -> str:
    lowered = text.lower()
    keyword_map = {
        "FINISHING": ["wdvs", "putz", "sockel", "bossen", "fliesen"],
        "REMODELING": ["abriss", "neubau", "bestand"],
        "HEIGHT_INFO": ["ok ffb", "meterriss", "brüstung", "bruestung", "höhe", "hoehe"],
        "OPENING_INFO": ["tür", "tuer", "fenster", "door", "window"],
        "FIRE_SAFETY": ["brandschutz", "f90", "f30"],
        "QA_WARNING": ["am bau prüfen", "klaerungsbedarf", "klärungsbedarf"],
    }
    for category, keywords in keyword_map.items():
        if any(keyword in lowered for keyword in keywords):
            return category
    return "METADATA_ONLY"


def _looks_like_room_label(text: str) -> bool:
    lowered = text.lower()
    return bool(
        re.search(r"\b(raum|zimmer|küche|kueche|bad|flur|wc|büro|buero)\b", lowered)
        or re.search(r"\b\d+[,.]\d+\s*m[²2]\b", lowered)
    )


def _map_prelim_status(status: str) -> str:
    mapping = {
        "candidate_review_required": "NEEDS_VISUAL_REVIEW",
        "placeholder_review_required": "NEEDS_VISUAL_REVIEW",
        "unsupported": "NOT_AVAILABLE",
        "failed_parse": "FAILED_PARSE",
        "no_candidates": "NOT_AVAILABLE",
    }
    return mapping.get(status, "NEEDS_VISUAL_REVIEW")


def _preview_type(row: dict[str, str]) -> str:
    if row["source_role"] == "SECTION":
        return "marked_section_cut_preview"
    if row["source_role"] == "FACADE":
        return "facade_preview"
    if row["file_type"] == "scan":
        return "scan_preview"
    return "per_file_preview_png"


def _table_file_name(table_name: str) -> str:
    return table_name.lower()


def _write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: str(row.get(field, "")) for field in fieldnames})


def _write_gemini_intake_packet(
    config: FactExtractionConfig,
    result: FactExtractionResult,
    rows_by_table: dict[str, list[dict[str, str]]],
) -> None:
    packet = {
        "schema_version": "construction_takeoff.gemini_intake.v1",
        "packet_id": f"{config.run_id}-gemini-audit",
        "objective": (
            "Audit preliminary Aufmass fact tables for conflicts, missing facts, "
            "unsafe assumptions, and manual review needs."
        ),
        "privacy_level": "INTERNAL_RUNNER_ONLY",
        "summary": {
            "process_name": "construction_takeoff_fact_extraction",
            "object_id": config.object_id,
            "scope": config.scope,
            "run_id": config.run_id,
            "workbook_version": WORKBOOK_VERSION,
        },
        "source_inventory": "csv/input_sources.csv",
        "selected_tables": {
            table_name: {
                "path": f"csv/{_table_file_name(table_name)}.csv",
                "row_count": len(rows),
            }
            for table_name, rows in rows_by_table.items()
        },
        "selected_rendered_previews": "rendered_previews/",
        "review_items": "csv/review_items.csv",
        "assumptions": "csv/assumptions.csv",
        "explicit_questions": [
            "Which source pairings and revisions need manual confirmation?",
            "Which room contour candidates are likely noise rather than rooms?",
            "Which height facts require datum or OK FFB review?",
            "Which facade/opening checks are missing before net area calculations?",
            "Which facts should be blocked from final quantity use?",
        ],
        "forbidden_actions": [
            "Do not approve final billable quantities.",
            "Do not invent missing dimensions.",
            "Do not treat Gemini output as source of truth.",
            "Do not request secrets, live access, or repo writes.",
        ],
    }
    result.gemini_intake_packet_json.write_text(
        json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _write_notebooklm_handoff(
    config: FactExtractionConfig, result: FactExtractionResult
) -> None:
    result.notebooklm_handoff_md.write_text(
        "\n".join(
            [
                "# NotebookLM Handoff",
                "",
                f"Run ID: `{config.run_id}`",
                f"Scope: `{config.scope}`",
                "",
                "NotebookLM/Gemini Notebooks role: source-grounded textual review.",
                "",
                "Use for:",
                "- PDF notes, legends, title blocks, annotations, and issue text.",
                "- Finding missed warnings such as OK FFB, Meterriss, WDVS, Putz, Sockel, Bossen, Brandschutz, am Bau prüfen.",
                "",
                "Do not use for:",
                "- Final CAD geometry.",
                "- DXF vector measurement.",
                "- Final billable Aufmaß quantities.",
                "",
                "Primary evidence files:",
                "- csv/input_sources.csv",
                "- csv/annotations_prelim.csv",
                "- csv/review_items.csv",
                "- csv/assumptions.csv",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _write_gemini_audit_placeholder(
    config: FactExtractionConfig, result: FactExtractionResult
) -> None:
    result.gemini_audit_report_md.write_text(
        "\n".join(
            [
                "# Gemini Audit Report",
                "",
                f"Run ID: `{config.run_id}`",
                "",
                "Status: GEMINI_AUDIT_SKIPPED",
                "",
                "Reason: This file is a placeholder until the Gemini auditor adapter is explicitly invoked by the private Runner.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _write_questions_for_oleksii(
    result: FactExtractionResult, question_rows: list[dict[str, str]]
) -> None:
    lines = ["# Questions for Oleksii", ""]
    for row in question_rows:
        lines.extend(
            [
                f"## {row['question_id']} — {row['category']}",
                "",
                f"Priority: {row['priority']}",
                "",
                row["question"],
                "",
            ]
        )
    result.questions_for_oleksii_md.write_text("\n".join(lines), encoding="utf-8")


def _write_run_report(
    config: FactExtractionConfig,
    result: FactExtractionResult,
    rows_by_table: dict[str, list[dict[str, str]]],
    workbook_created: bool,
) -> None:
    lines = [
        "Construction Takeoff Fact Extraction Run Report",
        "",
        "process_name: construction_takeoff_fact_extraction",
        f"object_id: {config.object_id}",
        f"scope: {config.scope}",
        f"run_id: {config.run_id}",
        f"source_snapshot_date: {config.source_snapshot_date}",
        f"workbook_version: {WORKBOOK_VERSION}",
        f"workbook_created: {str(workbook_created).lower()}",
        "",
        "table_counts:",
    ]
    for table_name in TABLE_ORDER:
        lines.append(f"  {table_name}: {len(rows_by_table[table_name])}")
    lines.extend(
        [
            "",
            "status: PARTIAL_OUTPUT",
            "notes: Preliminary fact tables only. No final billable quantities are approved by this run.",
            "",
        ]
    )
    result.run_report_txt.write_text("\n".join(lines), encoding="utf-8")
