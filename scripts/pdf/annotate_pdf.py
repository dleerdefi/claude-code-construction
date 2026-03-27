#!/usr/bin/env python3
"""Write real PDF annotations (viewable in Bluebeam, Adobe, any PDF reader).
Creates actual annotation objects in the PDF annotation layer, not raster overlays.
Annotations are non-destructive, togglable, and round-trip through AgentCM."""

import argparse
import json
import sys
from datetime import datetime

def annotate(pdf_path, items_json, output=None, author="Claude Code"):
    try:
        import fitz  # pymupdf
    except ImportError:
        print("ERROR: pymupdf not installed. Run: pip install PyMuPDF")
        sys.exit(1)

    with open(items_json) as f:
        items = json.load(f)

    if output is None:
        # Default: write to _annotated copy
        base = pdf_path.rsplit(".", 1)[0]
        output = f"{base}_annotated.pdf"

    doc = fitz.open(pdf_path)
    timestamp = datetime.now().strftime("D:%Y%m%d%H%M%S")

    colors = {
        "red": (1, 0, 0),
        "blue": (0, 0, 1),
        "green": (0, 0.7, 0),
        "yellow": (1, 1, 0),
        "orange": (1, 0.55, 0),
        "purple": (0.6, 0, 0.8),
    }

    for item in items:
        page_num = item.get("page", 1) - 1  # convert to 0-based
        if page_num < 0 or page_num >= len(doc):
            print(f"WARNING: Page {item.get('page')} out of range, skipping")
            continue

        page = doc[page_num]
        shape = item.get("shape", "circle")
        color = colors.get(item.get("color", "red"), (1, 0, 0))
        label = item.get("label", "")
        content = item.get("content", label)
        opacity = item.get("opacity", 0.7)

        # Coordinates in PDF points (72 DPI space)
        # Items can provide either pixel coords (with dpi) or PDF points directly
        if "rect" in item:
            # Direct PDF rect: [x1, y1, x2, y2]
            rect = fitz.Rect(item["rect"])
        elif "x" in item and "y" in item:
            # Point-based: create rect around point
            x, y = float(item["x"]), float(item["y"])
            r = float(item.get("radius", 15))
            dpi = float(item.get("dpi", 72))
            scale = 72.0 / dpi  # convert pixel coords to PDF points
            x, y, r = x * scale, y * scale, r * scale
            rect = fitz.Rect(x - r, y - r, x + r, y + r)
        else:
            print(f"WARNING: Item missing coordinates, skipping: {item}")
            continue

        annot = None

        if shape == "circle":
            annot = page.add_circle_annot(rect)
            annot.set_colors(stroke=color)
            annot.set_border(width=2)
            annot.set_opacity(opacity)

        elif shape == "rect" or shape == "box":
            annot = page.add_rect_annot(rect)
            annot.set_colors(stroke=color)
            annot.set_border(width=2)
            annot.set_opacity(opacity)

        elif shape == "cloud":
            # Cloud markup — use polygon with dashes to approximate
            # Real cloud annotations require custom appearance streams
            # Use a thick dashed rectangle as a visible marker
            annot = page.add_rect_annot(rect)
            annot.set_colors(stroke=color)
            annot.set_border(width=3, dashes=[4, 2])
            annot.set_opacity(opacity)

        elif shape == "highlight":
            # Yellow highlight over a region
            annot = page.add_highlight_annot(rect)

        elif shape == "text" or shape == "label":
            # FreeText annotation — visible text directly on drawing
            fontsize = item.get("fontsize", 10)
            annot = page.add_freetext_annot(
                rect,
                label,
                fontsize=fontsize,
                fontname="helv",
                text_color=color,
                fill_color=(1, 1, 1),  # white background
                border_color=color,
            )
            annot.set_opacity(opacity)

        elif shape == "stamp":
            # Stamp annotation
            stamp_text = item.get("stamp_text", "REVIEWED")
            annot = page.add_stamp_annot(rect, stamp=0)  # 0 = Approved
            # Custom stamp text via content
            content = stamp_text

        elif shape == "line":
            # Line from start to end
            start = fitz.Point(item.get("x1", rect.x0), item.get("y1", rect.y0))
            end = fitz.Point(item.get("x2", rect.x1), item.get("y2", rect.y1))
            annot = page.add_line_annot(start, end)
            annot.set_colors(stroke=color)
            annot.set_border(width=2)
            annot.set_opacity(opacity)

        elif shape == "polygon":
            # Polygon from vertices list
            vertices = item.get("vertices", [])
            if len(vertices) >= 3:
                points = [fitz.Point(v[0], v[1]) for v in vertices]
                annot = page.add_polygon_annot(points)
                annot.set_colors(stroke=color)
                annot.set_border(width=2)
                annot.set_opacity(opacity)

        if annot is not None:
            # Set metadata
            annot.set_info(
                content=content,
                title=author,
                subject=item.get("subject", f"Agent markup: {shape}"),
                creationDate=timestamp,
                modDate=timestamp,
            )
            annot.update()

    doc.save(output)
    doc.close()
    print(f"OK: {output} ({len(items)} annotations written)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Write PDF annotations (viewable in Bluebeam/Adobe)"
    )
    parser.add_argument("--pdf", required=True, help="Source PDF")
    parser.add_argument("--items", required=True, help="JSON file with annotation items")
    parser.add_argument("--output", "-o", help="Output PDF (default: {name}_annotated.pdf)")
    parser.add_argument("--author", default="Claude Code", help="Annotation author name")
    args = parser.parse_args()
    annotate(args.pdf, args.items, args.output, args.author)
