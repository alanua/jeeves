import csv
import json
from pathlib import Path

from tools.construction_takeoff.cli import main


def test_pilot_cli_writes_expected_artifacts(tmp_path: Path) -> None:
    source_dir = tmp_path / "sources"
    output_dir = tmp_path / "out"
    source_dir.mkdir()
    (source_dir / "Synthetic Floor Plan.pdf").write_text("not a real pdf", encoding="utf-8")
    (source_dir / "Synthetic Floor Plan.dxf").write_text("not a real dxf", encoding="utf-8")
    (source_dir / "Synthetic Legend.pdf").write_text("legend", encoding="utf-8")

    exit_code = main(
        [
            "pilot",
            "--source-dir",
            str(source_dir),
            "--output-dir",
            str(output_dir),
            "--scope",
            "erdgeschoss",
            "--targets",
            "rooms,walls_by_room",
            "--gemini-packet-only",
            "--notebooklm-handoff",
        ]
    )

    assert exit_code == 0
    expected = [
        "source_inventory.csv",
        "pdf_text_blocks.csv",
        "dxf_layers.csv",
        "dxf_entities_summary.csv",
        "rooms_prelim.csv",
        "walls_prelim.csv",
        "crosscheck_matrix.csv",
        "assumptions.csv",
        "review_items.csv",
        "workbook_manifest.csv",
        "gemini_intake_packet.json",
        "notebooklm_handoff.md",
        "runner_log.md",
    ]
    for filename in expected:
        assert (output_dir / filename).exists()

    with (output_dir / "source_inventory.csv").open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 3
    with (output_dir / "rooms_prelim.csv").open(encoding="utf-8") as handle:
        room_rows = list(csv.DictReader(handle))
    assert room_rows
    assert room_rows[0]["review_required"] == "yes"
    assert room_rows[0]["version_match_status"] == "not_performed"
    with (output_dir / "walls_prelim.csv").open(encoding="utf-8") as handle:
        wall_rows = list(csv.DictReader(handle))
    assert wall_rows[0]["status"] == "placeholder_review_required"
    with (output_dir / "crosscheck_matrix.csv").open(encoding="utf-8") as handle:
        crosscheck_rows = list(csv.DictReader(handle))
    assert {row["check_name"] for row in crosscheck_rows} >= {
        "pdf_current_state_evidence",
        "pdf_vector_version_match",
    }
    with (output_dir / "assumptions.csv").open(encoding="utf-8") as handle:
        assumption_rows = list(csv.DictReader(handle))
    assert assumption_rows[0]["review_required"] == "yes"

    packet = json.loads((output_dir / "gemini_intake_packet.json").read_text(encoding="utf-8"))
    assert packet["schema_version"] == "gemini_adapter.input.v1"
    assert packet["mode"] == "mock"
    assert "NotebookLM" in packet["confirmed_canon"]

    handoff = (output_dir / "notebooklm_handoff.md").read_text(encoding="utf-8")
    assert "NotebookLM is not the parser" in handoff
