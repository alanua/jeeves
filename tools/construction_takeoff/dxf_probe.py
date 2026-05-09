"""DXF probe adapter for the Construction Takeoff pilot.

ezdxf is optional. Without it, the adapter records unsupported rows so the
private Runner can install richer dependencies later without breaking public CI.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

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


def write_dxf_layers(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=LAYER_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_dxf_entities_summary(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ENTITY_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
