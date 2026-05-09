"""Command line entrypoint for the Construction Takeoff parser pilot."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from .dxf_probe import (
    extract_closed_polyline_room_candidates,
    probe_dxf,
    write_dxf_entities_summary,
    write_dxf_layers,
)
from .gemini_packet import build_gemini_packet, write_gemini_packet
from .notebooklm_handoff import build_notebooklm_handoff, write_notebooklm_handoff
from .pdf_extract import extract_pdf_text_blocks, write_pdf_text_blocks
from .schemas import (
    ArtifactSet,
    AssumptionRow,
    CrosscheckRow,
    PilotConfig,
    ReviewItem,
    RoomPrelim,
    WallPrelim,
)
from .source_inventory import build_source_inventory, write_source_inventory
from .workbook_export import write_workbook_manifest, write_workbook_xlsx


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Construction Takeoff parser pilot")
    subparsers = parser.add_subparsers(dest="command", required=True)

    pilot = subparsers.add_parser("pilot", help="Run the initial private/local pilot scaffold")
    pilot.add_argument("--source-dir", required=True, type=Path)
    pilot.add_argument("--output-dir", required=True, type=Path)
    pilot.add_argument("--scope", required=True)
    pilot.add_argument("--targets", default="rooms,walls_by_room")
    pilot.add_argument("--source-priority", default="pdf_current_vector_measurement")
    pilot.add_argument("--gemini-packet-only", action="store_true")
    pilot.add_argument("--notebooklm-handoff", action="store_true")
    return parser


def run_pilot(config: PilotConfig) -> ArtifactSet:
    config.output_dir.mkdir(parents=True, exist_ok=True)

    artifacts = ArtifactSet(
        source_inventory_csv=config.output_dir / "source_inventory.csv",
        pdf_text_blocks_csv=config.output_dir / "pdf_text_blocks.csv",
        dxf_layers_csv=config.output_dir / "dxf_layers.csv",
        dxf_entities_summary_csv=config.output_dir / "dxf_entities_summary.csv",
        rooms_prelim_csv=config.output_dir / "rooms_prelim.csv",
        walls_prelim_csv=config.output_dir / "walls_prelim.csv",
        crosscheck_matrix_csv=config.output_dir / "crosscheck_matrix.csv",
        assumptions_csv=config.output_dir / "assumptions.csv",
        review_items_csv=config.output_dir / "review_items.csv",
        workbook_manifest_csv=config.output_dir / "workbook_manifest.csv",
        workbook_xlsx=config.output_dir / "workbook.xlsx",
        gemini_intake_packet_json=config.output_dir / "gemini_intake_packet.json",
        notebooklm_handoff_md=config.output_dir / "notebooklm_handoff.md",
        runner_log_md=config.output_dir / "runner_log.md",
    )

    records = build_source_inventory(config.source_dir, config.scope, config.source_priority)
    write_source_inventory(records, artifacts.source_inventory_csv)

    pdf_rows = []
    dxf_layer_rows = []
    dxf_entity_rows = []
    room_rows: list[RoomPrelim] = []
    for record in records:
        source_path = config.source_dir / record.private_source_ref
        if record.source_type == "pdf" and source_path.is_file():
            pdf_rows.extend(extract_pdf_text_blocks(source_path))
        if record.source_type == "dxf" and source_path.is_file():
            layer_rows, entity_rows = probe_dxf(source_path)
            dxf_layer_rows.extend(layer_rows)
            dxf_entity_rows.extend(entity_rows)
            room_rows.extend(extract_closed_polyline_room_candidates(source_path))

    write_pdf_text_blocks(pdf_rows, artifacts.pdf_text_blocks_csv)
    write_dxf_layers(dxf_layer_rows, artifacts.dxf_layers_csv)
    write_dxf_entities_summary(dxf_entity_rows, artifacts.dxf_entities_summary_csv)

    wall_rows = _placeholder_wall_rows(records)
    crosscheck_rows = _build_crosscheck_rows(records, room_rows)
    assumption_rows = _build_assumption_rows(config)
    _write_dataclass_rows(room_rows, RoomPrelim, artifacts.rooms_prelim_csv)
    _write_dataclass_rows(wall_rows, WallPrelim, artifacts.walls_prelim_csv)
    _write_dataclass_rows(crosscheck_rows, CrosscheckRow, artifacts.crosscheck_matrix_csv)
    _write_dataclass_rows(assumption_rows, AssumptionRow, artifacts.assumptions_csv)

    review_items = _initial_review_items(records, room_rows)
    _write_review_items(review_items, artifacts.review_items_csv)

    packet = build_gemini_packet(config, records)
    write_gemini_packet(packet, artifacts.gemini_intake_packet_json)

    handoff = build_notebooklm_handoff(config, records)
    write_notebooklm_handoff(handoff, artifacts.notebooklm_handoff_md)

    workbook_created = write_workbook_xlsx(
        [
            artifacts.source_inventory_csv,
            artifacts.pdf_text_blocks_csv,
            artifacts.dxf_layers_csv,
            artifacts.dxf_entities_summary_csv,
            artifacts.rooms_prelim_csv,
            artifacts.walls_prelim_csv,
            artifacts.crosscheck_matrix_csv,
            artifacts.assumptions_csv,
            artifacts.review_items_csv,
        ],
        artifacts.workbook_xlsx,
    )
    if not workbook_created:
        review_items.append(
            ReviewItem(
                review_item_id=_next_review_id(review_items),
                severity="info",
                entity_type="parser_dependency",
                entity_id="openpyxl",
                issue="XLSX workbook export skipped because openpyxl is not installed.",
                recommended_action="Install the takeoff optional dependency group in the private Runner.",
            )
        )
        _write_review_items(review_items, artifacts.review_items_csv)

    _write_runner_log(config, artifacts, len(records), len(review_items), workbook_created)
    write_workbook_manifest(
        [
            artifacts.source_inventory_csv,
            artifacts.pdf_text_blocks_csv,
            artifacts.dxf_layers_csv,
            artifacts.dxf_entities_summary_csv,
            artifacts.rooms_prelim_csv,
            artifacts.walls_prelim_csv,
            artifacts.crosscheck_matrix_csv,
            artifacts.assumptions_csv,
            artifacts.review_items_csv,
            artifacts.workbook_xlsx,
            artifacts.gemini_intake_packet_json,
            artifacts.notebooklm_handoff_md,
            artifacts.runner_log_md,
        ],
        artifacts.workbook_manifest_csv,
    )
    return artifacts


def _initial_review_items(records: list, room_rows: list[RoomPrelim]) -> list[ReviewItem]:
    items: list[ReviewItem] = []
    has_pdf = any(record.source_type == "pdf" for record in records)
    has_vector = any(record.source_type in {"dxf", "dwg"} for record in records)
    has_legend = any("legende" in record.private_source_ref.lower() for record in records)

    if not has_pdf:
        items.append(
            ReviewItem(
                review_item_id=_next_review_id(items),
                severity="blocker",
                entity_type="source_set",
                entity_id="all",
                issue="No PDF source found for current visual/version selection.",
                recommended_action="Add or select the current PDF drawing before extraction.",
            )
        )
    if not has_vector:
        items.append(
            ReviewItem(
                review_item_id=_next_review_id(items),
                severity="warning",
                entity_type="source_set",
                entity_id="all",
                issue="No DXF/DWG vector source found for precise measurement.",
                recommended_action="Use PDF printed values only as preliminary or add vector sources.",
            )
        )
    if not has_legend:
        items.append(
            ReviewItem(
                review_item_id=_next_review_id(items),
                severity="warning",
                entity_type="source_set",
                entity_id="all",
                issue="No legend source detected.",
                recommended_action="Confirm legend/symbol interpretation before room and wall extraction.",
            )
        )
    if any(row.status == "unsupported" for row in room_rows):
        items.append(
            ReviewItem(
                review_item_id=_next_review_id(items),
                severity="warning",
                entity_type="parser_dependency",
                entity_id="ezdxf",
                issue="DXF room candidate extraction skipped because the parser dependency is missing.",
                recommended_action="Install the takeoff optional dependency group in the private Runner.",
            )
        )
    if any(row.status == "failed_parse" for row in room_rows):
        items.append(
            ReviewItem(
                review_item_id=_next_review_id(items),
                severity="warning",
                entity_type="dxf_parse",
                entity_id="rooms_prelim",
                issue="DXF parser failed before producing room candidates.",
                recommended_action="Inspect the private DXF locally and retry after parser validation.",
            )
        )
    if has_vector and room_rows and all(row.status == "no_candidates" for row in room_rows):
        items.append(
            ReviewItem(
                review_item_id=_next_review_id(items),
                severity="warning",
                entity_type="room_candidates",
                entity_id="rooms_prelim",
                issue="No simple closed polyline room candidates were detected.",
                recommended_action="Review DXF layers and confirm whether room boundaries use another entity type.",
            )
        )
    if has_vector:
        items.append(
            ReviewItem(
                review_item_id=_next_review_id(items),
                severity="warning",
                entity_type="version_match",
                entity_id="dxf_pdf",
                issue="PDF/DXF current-state version matching has not been performed.",
                recommended_action="Manually match vector candidates to the current PDF before using quantities.",
            )
        )
    return items


def _placeholder_wall_rows(records: list) -> list[WallPrelim]:
    source_refs = ", ".join(
        record.private_source_ref
        for record in records
        if record.source_type in {"dxf", "dwg", "pdf"}
    )
    return [
        WallPrelim(
            wall_prelim_id="WALL-PRELIM-0001",
            source_ref=source_refs,
            source_entity_id="",
            source_layer="",
            length_raw="",
            height_raw="",
            area_raw="",
            unit="",
            confidence="0.00",
        )
    ]


def _build_crosscheck_rows(records: list, room_rows: list[RoomPrelim]) -> list[CrosscheckRow]:
    has_pdf = any(record.source_type == "pdf" for record in records)
    room_candidate_count = sum(row.status == "candidate_review_required" for row in room_rows)
    return [
        CrosscheckRow(
            crosscheck_id="CHECK-0001",
            check_name="pdf_current_state_evidence",
            source_refs=_refs_for(records, {"pdf"}),
            status="present_review_required" if has_pdf else "missing_review_required",
            review_required="yes",
            notes="PDF source presence is only an evidence gate; current-state matching is manual.",
        ),
        CrosscheckRow(
            crosscheck_id="CHECK-0002",
            check_name="vector_room_candidate_extraction",
            source_refs=_refs_for(records, {"dxf", "dwg"}),
            status="candidate_rows_present" if room_candidate_count else "no_candidate_rows",
            review_required="yes",
            notes=f"Closed-polyline room candidate rows detected: {room_candidate_count}.",
        ),
        CrosscheckRow(
            crosscheck_id="CHECK-0003",
            check_name="pdf_vector_version_match",
            source_refs=_refs_for(records, {"pdf", "dxf", "dwg"}),
            status="not_performed",
            review_required="yes",
            notes="Version matching is outside the public-safe v0 parser scaffold.",
        ),
    ]


def _build_assumption_rows(config: PilotConfig) -> list[AssumptionRow]:
    return [
        AssumptionRow(
            assumption_id="ASSUMP-0001",
            scope=config.scope,
            assumption="Closed DXF polylines may represent room boundary candidates.",
            status="open",
            review_required="yes",
            notes="Room labels, wall buildup, scale calibration, and PDF current-state matching remain manual.",
        )
    ]


def _refs_for(records: list, source_types: set[str]) -> str:
    return ", ".join(
        record.private_source_ref for record in records if record.source_type in source_types
    )


def _write_dataclass_rows(rows: list, row_type: type, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(row_type.__dataclass_fields__.keys())
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.to_row())


def _next_review_id(items: list[ReviewItem]) -> str:
    return f"RI-{len(items) + 1:04d}"


def _write_review_items(items: list[ReviewItem], output_path: Path) -> None:
    fieldnames = list(ReviewItem.__dataclass_fields__.keys())
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for item in items:
            writer.writerow(item.to_row())


def _write_runner_log(
    config: PilotConfig,
    artifacts: ArtifactSet,
    source_count: int,
    review_item_count: int,
    workbook_created: bool,
) -> None:
    artifacts.runner_log_md.write_text(
        "\n".join(
            [
                "# Construction Takeoff Runner Log",
                "",
                f"Scope: {config.scope}",
                f"Targets: {', '.join(config.targets)}",
                f"Source priority: {config.source_priority}",
                f"Source count: {source_count}",
                f"Initial review items: {review_item_count}",
                f"Workbook XLSX: {'created' if workbook_created else 'skipped_openpyxl_not_available'}",
                "",
                "Status: PRELIMINARY_PARSER_SCAFFOLD_COMPLETE_REVIEW_REQUIRED",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "pilot":
        config = PilotConfig(
            source_dir=args.source_dir,
            output_dir=args.output_dir,
            scope=args.scope,
            targets=tuple(part.strip() for part in args.targets.split(",") if part.strip()),
            source_priority=args.source_priority,
            gemini_packet_only=args.gemini_packet_only,
            notebooklm_handoff=args.notebooklm_handoff,
        )
        artifacts = run_pilot(config)
        print(f"source_inventory={artifacts.source_inventory_csv}")
        print(f"pdf_text_blocks={artifacts.pdf_text_blocks_csv}")
        print(f"dxf_layers={artifacts.dxf_layers_csv}")
        print(f"dxf_entities_summary={artifacts.dxf_entities_summary_csv}")
        print(f"rooms_prelim={artifacts.rooms_prelim_csv}")
        print(f"walls_prelim={artifacts.walls_prelim_csv}")
        print(f"crosscheck_matrix={artifacts.crosscheck_matrix_csv}")
        print(f"assumptions={artifacts.assumptions_csv}")
        print(f"review_items={artifacts.review_items_csv}")
        print(f"workbook_manifest={artifacts.workbook_manifest_csv}")
        print(f"workbook_xlsx={artifacts.workbook_xlsx}")
        print(f"gemini_packet={artifacts.gemini_intake_packet_json}")
        print(f"notebooklm_handoff={artifacts.notebooklm_handoff_md}")
        print(f"runner_log={artifacts.runner_log_md}")
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
