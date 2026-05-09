"""Workbook manifest exporter.

The v0 pilot writes a CSV manifest instead of requiring openpyxl in public CI.
Runner can later add XLSX export when optional dependencies are installed.
"""

from __future__ import annotations

import csv
from pathlib import Path


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
