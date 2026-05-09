"""PDF text extraction probe for the Construction Takeoff pilot.

PyMuPDF is optional. When it is absent, the adapter records an unsupported row
instead of failing the whole pilot.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

PDF_FIELDS = ["source_ref", "page", "block_index", "text", "status", "notes"]


def extract_pdf_text_blocks(pdf_path: Path) -> list[dict[str, str]]:
    try:
        import fitz  # type: ignore[import-not-found]
    except ModuleNotFoundError:
        return [
            {
                "source_ref": pdf_path.name,
                "page": "",
                "block_index": "",
                "text": "",
                "status": "unsupported",
                "notes": "PyMuPDF is not installed in this environment.",
            }
        ]

    rows: list[dict[str, str]] = []
    try:
        document: Any = fitz.open(pdf_path)
        for page_index, page in enumerate(document, start=1):
            text = page.get_text("text") or ""
            for block_index, block_text in enumerate(_split_blocks(text), start=1):
                rows.append(
                    {
                        "source_ref": pdf_path.name,
                        "page": str(page_index),
                        "block_index": str(block_index),
                        "text": block_text,
                        "status": "parsed",
                        "notes": "",
                    }
                )
    except Exception as exc:  # pragma: no cover - depends on parser internals
        return [
            {
                "source_ref": pdf_path.name,
                "page": "",
                "block_index": "",
                "text": "",
                "status": "failed_parse",
                "notes": f"{type(exc).__name__}: {exc}",
            }
        ]
    return rows or [
        {
            "source_ref": pdf_path.name,
            "page": "",
            "block_index": "",
            "text": "",
            "status": "parsed",
            "notes": "No text blocks extracted.",
        }
    ]


def write_pdf_text_blocks(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=PDF_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _split_blocks(text: str) -> list[str]:
    blocks = [line.strip() for line in text.splitlines() if line.strip()]
    return blocks[:500]
