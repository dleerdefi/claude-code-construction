#!/usr/bin/env python3
"""Split a bound drawing set PDF into individual page PDFs.

Each page becomes its own PDF named by page number. Sheet number and title
identification is delegated to Claude Code vision (the SKILL.md instructs
Claude to rasterize title blocks and read them).

Usage:
  python split_drawing_set.py <drawings.pdf> [--output-dir <sheets/>]
  python split_drawing_set.py <drawings.pdf> --dry-run

Output:
  sheets/page_001.pdf
  sheets/page_002.pdf
  ...
  sheets/sheet_index.yaml
"""

import argparse
import sys
from pathlib import Path

import fitz  # PyMuPDF


def split_pages(pdf_path, output_dir, dry_run=False):
    """Split PDF into one file per page."""
    doc = fitz.open(str(pdf_path))
    total_pages = len(doc)
    output_dir = Path(output_dir)

    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    sheets = []

    for page_idx in range(total_pages):
        page = doc[page_idx]
        rect = page.rect
        filename = f"page_{page_idx + 1:03d}.pdf"

        info = {
            "filename": filename,
            "page_index": page_idx,
            "page_size": f"{rect.width:.0f}x{rect.height:.0f}",
            "page_size_inches": f"{rect.width/72:.1f}x{rect.height/72:.1f}",
        }
        sheets.append(info)

        if not dry_run:
            out_path = output_dir / filename
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=page_idx, to_page=page_idx)
            new_doc.save(str(out_path))
            new_doc.close()

        print(f"  {page_idx + 1:3d}/{total_pages}: {filename}")

    doc.close()
    return sheets


def write_index(sheets, output_dir, source_pdf):
    """Write a YAML index of the split sheets."""
    import yaml

    index = {
        "source": str(source_pdf),
        "total_pages": len(sheets),
        "note": "Sheet numbers and titles need to be identified via Claude Code vision. Run /sheet-index-builder after splitting.",
        "pages": [
            {
                "filename": s["filename"],
                "page_index": s["page_index"],
                "page_size": s["page_size"],
                "sheet_number": "needs_identification",
                "title": "needs_identification",
            }
            for s in sheets
        ],
    }

    index_path = Path(output_dir) / "sheet_index.yaml"
    with open(index_path, "w") as f:
        yaml.dump(index, f, default_flow_style=False, sort_keys=False)
    return index_path


def main():
    parser = argparse.ArgumentParser(description="Split a bound drawing set into individual page PDFs")
    parser.add_argument("pdf", help="Path to the bound drawing set PDF")
    parser.add_argument("--output-dir", default=None, help="Output directory (default: sheets/ next to PDF)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be split without writing files")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"ERROR: PDF not found: {pdf_path}")
        sys.exit(1)

    output_dir = args.output_dir or str(pdf_path.parent / "sheets")

    doc = fitz.open(str(pdf_path))
    total = len(doc)
    page_size = f"{doc[0].rect.width/72:.1f}x{doc[0].rect.height/72:.1f} in" if total > 0 else "unknown"
    doc.close()

    print(f"Source: {pdf_path.name}")
    print(f"Pages: {total} ({page_size})")
    print(f"Output: {output_dir}")

    print(f"\n{'='*50}")
    sheets = split_pages(pdf_path, output_dir, dry_run=args.dry_run)

    if not args.dry_run:
        try:
            index_path = write_index(sheets, output_dir, pdf_path)
            print(f"\nIndex: {index_path}")
        except ImportError:
            print("\n(PyYAML not installed - index skipped)")

    print(f"\n{'='*50}")
    print(f"COMPLETE: {len(sheets)} pages split")
    print(f"Next: Run /sheet-index-builder to identify sheet numbers via vision")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
