#!/usr/bin/env python3
"""Extract PDF annotations (Bluebeam markups, comments, stamps) via PyMuPDF."""

import argparse
import json
import sys

def extract_annotations(pdf_path, output=None):
    try:
        import fitz
    except ImportError:
        print("ERROR: pymupdf not installed. Run: pip install PyMuPDF")
        sys.exit(1)

    doc = fitz.open(pdf_path)
    all_annotations = []

    for page_num, page in enumerate(doc, 1):
        for annot in page.annots():
            info = annot.info
            a = {
                "page": page_num,
                "type": annot.type[1],  # e.g., 'Text', 'FreeText', 'Square', etc.
                "rect": list(annot.rect),
                "content": info.get("content", ""),
                "subject": info.get("subject", ""),
                "title": info.get("title", ""),  # author
                "creation_date": info.get("creationDate", ""),
                "mod_date": info.get("modDate", ""),
                "color": list(annot.colors.get("stroke", [])) if annot.colors else [],
            }
            # Extract vertices for polyline/polygon annotations
            if annot.vertices:
                a["vertices"] = [list(v) for v in annot.vertices]
            all_annotations.append(a)

    doc.close()

    result = {
        "file": pdf_path,
        "total_annotations": len(all_annotations),
        "by_type": {},
        "annotations": all_annotations,
    }
    for a in all_annotations:
        t = a["type"]
        result["by_type"][t] = result["by_type"].get(t, 0) + 1

    out = json.dumps(result, indent=2)
    if output:
        with open(output, "w") as f:
            f.write(out)
        print(f"OK: {len(all_annotations)} annotations → {output}")
    else:
        print(out)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract PDF annotations")
    parser.add_argument("pdf", help="Path to PDF")
    parser.add_argument("--output", "-o", help="Output JSON file")
    args = parser.parse_args()
    extract_annotations(args.pdf, args.output)
