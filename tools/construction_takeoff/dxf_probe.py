"""DXF probe adapter for the Construction Takeoff pilot.

ezdxf is optional. Without it, the adapter records unsupported rows so the
private Runner can install richer dependencies later without breaking public CI.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from .schemas import RoomPrelim

LAYER_FIELDS = ["source_ref", "layer", "status", "notes"]
ENTITY_FIELDS = ["source_ref", "entity_type", "layer", "count", "status", "notes"]


def probe_dxf(dxf_path: Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    try:
        import ezdxf  # type: ignore[import-not-found]
    except ModuleNotFoundError:
        return (
            [
                {
                    "source_ref": dxf_path.name,
                    "layer": "",
                    "status": "unsupported",
                    "notes": "ezdxf is not installed in this environment.",
                }
            ],
            [
                {
                    "source_ref": dxf_path.name,
                    "entity_type": "",
                    "layer": "",
                    "count": "0",
                    "status": "unsupported",
                    "notes": "ezdxf is not installed in this environment.",
                }
            ],
        )

    try:
        document: Any = ezdxf.readfile(dxf_path)
        layer_rows = [
            {"source_ref": dxf_path.name, "layer": layer.dxf.name, "status": "parsed", "notes": ""}
            for layer in document.layers
        ]
        counts: dict[tuple[str, str], int] = {}
        for entity in document.modelspace():
            entity_type = entity.dxftype()
            layer = getattr(entity.dxf, "layer", "")
            key = (entity_type, layer)
            counts[key] = counts.get(key, 0) + 1
        entity_rows = [
            {
                "source_ref": dxf_path.name,
                "entity_type": entity_type,
                "layer": layer,
                "count": str(count),
                "status": "parsed",
                "notes": "",
            }
            for (entity_type, layer), count in sorted(counts.items())
        ]
    except Exception as exc:  # pragma: no cover - depends on parser internals
        return (
            [
                {
                    "source_ref": dxf_path.name,
                    "layer": "",
                    "status": "failed_parse",
                    "notes": f"{type(exc).__name__}: {exc}",
                }
            ],
            [
                {
                    "source_ref": dxf_path.name,
                    "entity_type": "",
                    "layer": "",
                    "count": "0",
                    "status": "failed_parse",
                    "notes": f"{type(exc).__name__}: {exc}",
                }
            ],
        )
    return layer_rows, entity_rows


def extract_closed_polyline_room_candidates(dxf_path: Path) -> list[RoomPrelim]:
    try:
        import ezdxf  # type: ignore[import-not-found]
    except ModuleNotFoundError:
        return [
            RoomPrelim(
                room_prelim_id="ROOM-PRELIM-0001",
                source_ref=dxf_path.name,
                source_entity_id="",
                source_layer="",
                area_raw="",
                area_unit="",
                confidence="0.00",
                status="unsupported",
                notes="ezdxf is not installed; room candidate extraction was skipped.",
            )
        ]

    try:
        document: Any = ezdxf.readfile(dxf_path)
        unit = _drawing_area_unit(document)
        candidates: list[RoomPrelim] = []
        for index, entity in enumerate(document.modelspace(), start=1):
            if entity.dxftype() not in {"LWPOLYLINE", "POLYLINE"} or not _is_closed_polyline(
                entity
            ):
                continue
            points = _polyline_points(entity)
            area = abs(_shoelace_area(points))
            if len(points) < 3 or area <= 0:
                continue
            candidates.append(
                RoomPrelim(
                    room_prelim_id=f"ROOM-PRELIM-{len(candidates) + 1:04d}",
                    source_ref=dxf_path.name,
                    source_entity_id=_entity_id(entity, index),
                    source_layer=str(getattr(entity.dxf, "layer", "")),
                    area_raw=f"{area:.6f}",
                    area_unit=unit,
                    confidence="0.45",
                    status="candidate_review_required",
                    notes=(
                        "Closed DXF polyline candidate; PDF/current-state matching and room label "
                        "association are not performed."
                    ),
                )
            )
    except Exception as exc:  # pragma: no cover - depends on parser internals
        return [
            RoomPrelim(
                room_prelim_id="ROOM-PRELIM-0001",
                source_ref=dxf_path.name,
                source_entity_id="",
                source_layer="",
                area_raw="",
                area_unit="",
                confidence="0.00",
                status="failed_parse",
                notes=f"{type(exc).__name__}: {exc}",
            )
        ]

    return candidates or [
        RoomPrelim(
            room_prelim_id="ROOM-PRELIM-0001",
            source_ref=dxf_path.name,
            source_entity_id="",
            source_layer="",
            area_raw="",
            area_unit=unit,
            confidence="0.00",
            status="no_candidates",
            notes="No simple closed DXF polylines found for room candidates.",
        )
    ]


def write_dxf_layers(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=LAYER_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _is_closed_polyline(entity: Any) -> bool:
    closed = getattr(entity, "closed", None)
    if isinstance(closed, bool):
        return closed
    is_closed = getattr(entity, "is_closed", None)
    if callable(is_closed):
        return bool(is_closed())
    if isinstance(is_closed, bool):
        return is_closed
    return bool(getattr(entity, "is_closed", False))


def _polyline_points(entity: Any) -> list[tuple[float, float]]:
    if entity.dxftype() == "LWPOLYLINE":
        if hasattr(entity, "get_points"):
            return [(float(point[0]), float(point[1])) for point in entity.get_points()]
        return [(float(point[0]), float(point[1])) for point in entity]

    points = []
    vertices = entity.vertices() if callable(getattr(entity, "vertices", None)) else entity.vertices
    for vertex in vertices:
        location = vertex.dxf.location
        points.append((float(location.x), float(location.y)))
    return points


def _shoelace_area(points: list[tuple[float, float]]) -> float:
    if len(points) < 3:
        return 0.0
    pairs = zip(points, [*points[1:], points[0]], strict=True)
    return sum((x1 * y2) - (x2 * y1) for (x1, y1), (x2, y2) in pairs) / 2


def _drawing_area_unit(document: Any) -> str:
    try:
        unit_code = int(document.header.get("$INSUNITS", 0))
    except Exception:
        unit_code = 0
    unit_names = {
        0: "drawing_units_squared",
        1: "inches_squared",
        2: "feet_squared",
        4: "millimeters_squared",
        5: "centimeters_squared",
        6: "meters_squared",
    }
    return unit_names.get(unit_code, f"insunits_{unit_code}_squared")


def _entity_id(entity: Any, fallback_index: int) -> str:
    handle = getattr(getattr(entity, "dxf", object()), "handle", "")
    return str(handle or f"modelspace_index_{fallback_index}")


def write_dxf_entities_summary(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ENTITY_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
