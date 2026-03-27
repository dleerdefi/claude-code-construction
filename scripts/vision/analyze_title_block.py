#!/usr/bin/env python3
"""Rasterize and crop a title block region from a drawing PDF for vision analysis."""

import argparse
import sys

def analyze(pdf_path, page_num=1, output="title_block.png", dpi=200):
    try:
        import fitz
    except ImportError:
        print("ERROR: pymupdf not installed. Run: pip install PyMuPDF")
        sys.exit(1)

    doc = fitz.open(pdf_path)
    if page_num < 1 or page_num > len(doc):
        print(f"ERROR: Page {page_num} out of range (1-{len(doc)})")
        sys.exit(1)

    page = doc[page_num - 1]
    rect = page.rect
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    # Title block is typically in the bottom-right quadrant of the sheet
    # For ARCH D (24x36"): title block is roughly 7" wide × 3" tall in bottom-right
    # Conservative crop: rightmost 30% of width, bottom 15% of height
    tb_rect = fitz.Rect(
        rect.x0 + rect.width * 0.65,
        rect.y0 + rect.height * 0.80,
        rect.x1,
        rect.y1,
    )

    pix = page.get_pixmap(matrix=matrix, clip=tb_rect)
    pix.save(output)
    doc.close()
    print(f"OK: Title block → {output} ({pix.width}x{pix.height}px)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract title block region from drawing")
    parser.add_argument("pdf", help="Path to PDF")
    parser.add_argument("--page", type=int, default=1, help="Page number (1-based)")
    parser.add_argument("--output", "-o", default="title_block.png")
    parser.add_argument("--dpi", type=int, default=200)
    args = parser.parse_args()
    analyze(args.pdf, args.page, args.output, args.dpi)
