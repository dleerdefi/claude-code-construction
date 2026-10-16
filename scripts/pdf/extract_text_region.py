#!/usr/bin/env python3
"""Extract text from a specific region of a PDF page using pdfplumber.

Prints JSON: the region's text and tables, the page's size in PDF points and, with --words, every
word with its box, in PDF points (x0, top, x1, bottom) and as fractions of the page from the top left
(x, y, w, h). The fractions are the box `crop_region.py --normalized` takes (as x, y, x+w, y+h) and,
times 100, the percentages `rasterize_page.py --crop` takes: find a row or a column header here, then
look at it.

    extract_text_region.py sheet.pdf 1 [--bbox x1,y1,x2,y2] [--words [--match REGEX]] [--output out.json]
"""

import argparse
import json
import re
import sys


def word_boxes(region, width, height, match=None):
    pattern = re.compile(match, re.IGNORECASE) if match else None
    out = []
    for w in region.extract_words():
        if pattern and not pattern.search(w["text"]):
            continue
        out.append({
            "text": w["text"],
            "x0": round(w["x0"], 1), "top": round(w["top"], 1), "x1": round(w["x1"], 1), "bottom": round(w["bottom"], 1),
            "x": round(w["x0"] / width, 4), "y": round(w["top"] / height, 4),
            "w": round((w["x1"] - w["x0"]) / width, 4), "h": round((w["bottom"] - w["top"]) / height, 4),
        })
    return out


def extract(pdf_path, page_num, bbox=None, output=None, words=False, match=None):
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
            "page_size": {"width": round(page.width, 1), "height": round(page.height, 1)},
            "text": text,
            "tables": tables,
            "word_count": len(text.split()),
        }
        if words:
            result["words"] = word_boxes(region, page.width, page.height, match)

        out = json.dumps(result, indent=2)
        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(out)
            print(f"OK: Extracted to {output}")
        else:
            print(out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract text from PDF region")
    parser.add_argument("pdf", help="Path to PDF")
    parser.add_argument("page", type=int, help="Page number (1-based)")
    parser.add_argument("--bbox", help="Bounding box as x1,y1,x2,y2 in PDF points")
    parser.add_argument("--words", action="store_true",
                        help="Also list every word with its box (PDF points, and fractions of the page)")
    parser.add_argument("--match", help="With --words: only the words matching this regular expression")
    parser.add_argument("--output", "-o", help="Output JSON file")
    args = parser.parse_args()
    if args.match and not args.words:
        parser.error("--match needs --words")
    extract(args.pdf, args.page, args.bbox, args.output, args.words, args.match)
