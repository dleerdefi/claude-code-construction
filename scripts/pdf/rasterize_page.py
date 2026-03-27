#!/usr/bin/env python3
"""Rasterize a PDF page to PNG. Supports DPI control and optional cropping."""

import argparse
import sys

def rasterize(pdf_path, page_num, dpi=200, output="page.png", crop=None):
    try:
        import fitz  # pymupdf
    except ImportError:
        print("ERROR: pymupdf not installed. Run: pip install PyMuPDF")
        sys.exit(1)

    doc = fitz.open(pdf_path)
    if page_num < 1 or page_num > len(doc):
        print(f"ERROR: Page {page_num} out of range (1-{len(doc)})")
        sys.exit(1)

    page = doc[page_num - 1]
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    if crop:
        # crop format: x1,y1,x2,y2 as percentages (0-100)
        x1, y1, x2, y2 = [float(v) for v in crop.split(",")]
        rect = page.rect
        clip = fitz.Rect(
            rect.x0 + rect.width * x1 / 100,
            rect.y0 + rect.height * y1 / 100,
            rect.x0 + rect.width * x2 / 100,
            rect.y0 + rect.height * y2 / 100,
        )
        pix = page.get_pixmap(matrix=matrix, clip=clip)
    else:
        pix = page.get_pixmap(matrix=matrix)

    pix.save(output)
    doc.close()
    print(f"OK: {output} ({pix.width}x{pix.height}px at {dpi} DPI)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rasterize a PDF page")
    parser.add_argument("pdf", help="Path to PDF file")
    parser.add_argument("page", type=int, help="Page number (1-based)")
    parser.add_argument("--dpi", type=int, default=200, help="DPI (default 200)")
    parser.add_argument("--output", "-o", default="page.png", help="Output filename")
    parser.add_argument("--crop", help="Crop region as x1,y1,x2,y2 percentages")
    args = parser.parse_args()
    rasterize(args.pdf, args.page, args.dpi, args.output, args.crop)
