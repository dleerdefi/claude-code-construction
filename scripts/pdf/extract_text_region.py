#!/usr/bin/env python3
"""Extract text from a specific region of a PDF page using pdfplumber."""

import argparse
import json
import sys

def extract(pdf_path, page_num, bbox=None, output=None):
    try:
        import pdfplumber
    except ImportError:
        print("ERROR: pdfplumber not installed. Run: pip install pdfplumber")
        sys.exit(1)

    with pdfplumber.open(pdf_path) as pdf:
        if page_num < 1 or page_num > len(pdf.pages):
            print(f"ERROR: Page {page_num} out of range (1-{len(pdf.pages)})")
            sys.exit(1)

        page = pdf.pages[page_num - 1]

        if bbox:
            coords = [float(v) for v in bbox.split(",")]
            region = page.within_bbox(coords)
        else:
            region = page

        text = region.extract_text() or ""
        tables = region.extract_tables() or []

        result = {
            "page": page_num,
            "bbox": bbox,
            "text": text,
            "tables": tables,
            "word_count": len(text.split()),
        }

        out = json.dumps(result, indent=2)
        if output:
            with open(output, "w") as f:
                f.write(out)
            print(f"OK: Extracted to {output}")
        else:
            print(out)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract text from PDF region")
    parser.add_argument("pdf", help="Path to PDF")
    parser.add_argument("page", type=int, help="Page number (1-based)")
    parser.add_argument("--bbox", help="Bounding box as x1,y1,x2,y2 in PDF points")
    parser.add_argument("--output", "-o", help="Output JSON file")
    args = parser.parse_args()
    extract(args.pdf, args.page, args.bbox, args.output)
