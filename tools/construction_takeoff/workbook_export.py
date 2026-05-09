"""Workbook manifest and optional XLSX exporter.

The v0 pilot never requires openpyxl in public CI. When it is available in a
private Runner environment, the same preliminary CSV artifacts are copied into
an XLSX workbook for manual review.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


def write_workbook_manifest(artifact_paths: list[Path], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["artifact", "exists", "notes"])
        writer.writeheader()
        for path in artifact_paths:
            writer.writerow(
                {
                    "artifact": path.name,
                    "exists": "yes" if path.exists() else "no",
                    "notes": "v0 manifest; XLSX export is a later Runner adapter",
                }
            )


def write_workbook_xlsx(csv_paths: list[Path], output_path: Path) -> bool:
    try:
        from openpyxl import Workbook  # type: ignore[import-not-found]
    except ModuleNotFoundError:
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    workbook: Any = Workbook()
    default_sheet = workbook.active
    workbook.remove(default_sheet)

    for csv_path in csv_paths:
        worksheet = workbook.create_sheet(title=_safe_sheet_title(csv_path.stem))
        if not csv_path.exists():
            worksheet.append(["artifact", "exists", "notes"])
            worksheet.append(
                [csv_path.name, "no", "Artifact was not created before workbook export."]
            )
            continue
        with csv_path.open(newline="", encoding="utf-8") as handle:
            for row in csv.reader(handle):
                worksheet.append(row)

    workbook.save(output_path)
    return True


def _safe_sheet_title(title: str) -> str:
    safe = "".join(char if char not in "[]:*?/\\\\" else "_" for char in title)
    return safe[:31] or "sheet"
