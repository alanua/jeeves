from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

from tools.construction_takeoff.dxf_probe import extract_closed_polyline_room_candidates


class FakeLWPolyline:
    closed = True

    dxf = SimpleNamespace(layer="ROOM_BOUNDARY", handle="ABC1")

    def dxftype(self) -> str:
        return "LWPOLYLINE"

    def get_points(self) -> list[tuple[int, int]]:
        return [(0, 0), (4, 0), (4, 3), (0, 3)]


class FakeLine:
    dxf = SimpleNamespace(layer="LINES", handle="ABC2")

    def dxftype(self) -> str:
        return "LINE"


class FakeDocument:
    header = {"$INSUNITS": 6}

    def modelspace(self) -> list[object]:
        return [FakeLWPolyline(), FakeLine()]


def test_extract_closed_polyline_room_candidates_from_synthetic_dxf(
    monkeypatch, tmp_path: Path
) -> None:
    dxf_path = tmp_path / "synthetic_room_boundaries.dxf"
    dxf_path.write_text("synthetic placeholder", encoding="utf-8")
    monkeypatch.setitem(
        sys.modules, "ezdxf", SimpleNamespace(readfile=lambda _path: FakeDocument())
    )

    rows = extract_closed_polyline_room_candidates(dxf_path)

    assert len(rows) == 1
    assert rows[0].source_ref == "synthetic_room_boundaries.dxf"
    assert rows[0].source_entity_id == "ABC1"
    assert rows[0].source_layer == "ROOM_BOUNDARY"
    assert rows[0].area_raw == "12.000000"
    assert rows[0].area_unit == "meters_squared"
    assert rows[0].status == "candidate_review_required"
    assert rows[0].review_required == "yes"
    assert rows[0].version_match_status == "not_performed"
