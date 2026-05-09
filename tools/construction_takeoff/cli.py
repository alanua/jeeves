"""Command line entrypoint for the Construction Takeoff parser pilot."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from .gemini_packet import build_gemini_packet, write_gemini_packet
from .notebooklm_handoff import build_notebooklm_handoff, write_notebooklm_handoff
from .schemas import ArtifactSet, PilotConfig, ReviewItem
from .source_inventory import build_source_inventory, write_source_inventory


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
        review_items_csv=config.output_dir / "review_items.csv",
        gemini_intake_packet_json=config.output_dir / "gemini_intake_packet.json",
        notebooklm_handoff_md=config.output_dir / "notebooklm_handoff.md",
        runner_log_md=config.output_dir / "runner_log.md",
    )

    records = build_source_inventory(config.source_dir, config.scope, config.source_priority)
    write_source_inventory(records, artifacts.source_inventory_csv)

    review_items = _initial_review_items(records)
    _write_review_items(review_items, artifacts.review_items_csv)

    packet = build_gemini_packet(config, records)
    write_gemini_packet(packet, artifacts.gemini_intake_packet_json)

    handoff = build_notebooklm_handoff(config, records)
    write_notebooklm_handoff(handoff, artifacts.notebooklm_handoff_md)

    _write_runner_log(config, artifacts, len(records), len(review_items))
    return artifacts


def _initial_review_items(records: list) -> list[ReviewItem]:
    items: list[ReviewItem] = []
    has_pdf = any(record.source_type == "pdf" for record in records)
    has_vector = any(record.source_type in {"dxf", "dwg"} for record in records)
    has_legend = any("legende" in record.private_source_ref.lower() for record in records)

    if not has_pdf:
        items.append(
            ReviewItem(
                review_item_id="RI-0001",
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
                review_item_id="RI-0002",
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
                review_item_id="RI-0003",
                severity="warning",
                entity_type="source_set",
                entity_id="all",
                issue="No legend source detected.",
                recommended_action="Confirm legend/symbol interpretation before room and wall extraction.",
            )
        )
    return items


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
                "",
                "Status: INITIAL_SCAFFOLD_COMPLETE",
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
        print(f"review_items={artifacts.review_items_csv}")
        print(f"gemini_packet={artifacts.gemini_intake_packet_json}")
        print(f"notebooklm_handoff={artifacts.notebooklm_handoff_md}")
        print(f"runner_log={artifacts.runner_log_md}")
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
