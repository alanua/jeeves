from pathlib import Path

from tools.construction_takeoff.source_inventory import build_source_inventory


def test_build_source_inventory_classifies_common_sources(tmp_path: Path) -> None:
    (tmp_path / "Consum Quartier Erdgeschoss.pdf").write_text("pdf", encoding="utf-8")
    (tmp_path / "Consum Quartier Erdgeschoss.dxf").write_text("dxf", encoding="utf-8")
    (tmp_path / "Consum Quartier LEGENDE.pdf").write_text("legend", encoding="utf-8")
    (tmp_path / "Scans").mkdir()

    records = build_source_inventory(tmp_path, "erdgeschoss", "pdf_current_vector_measurement")

    by_name = {record.private_source_ref: record for record in records}
    assert by_name["Consum Quartier Erdgeschoss.pdf"].source_type == "pdf"
    assert by_name["Consum Quartier Erdgeschoss.pdf"].priority_for_this_object == (
        "pdf_current_variant_selector"
    )
    assert by_name["Consum Quartier Erdgeschoss.dxf"].source_type == "dxf"
    assert by_name["Consum Quartier Erdgeschoss.dxf"].priority_for_this_object == (
        "vector_measurement_after_pdf_match"
    )
    assert by_name["Consum Quartier LEGENDE.pdf"].source_role == "legend_dictionary"
    assert by_name["Scans"].source_type == "folder"
