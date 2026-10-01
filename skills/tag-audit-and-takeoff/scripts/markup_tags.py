#!/usr/bin/env python3
"""Overlay tag detection marks on a construction drawing sheet.

Per-skill script for tag-audit-and-takeoff. Draws circles at detected tag
locations with numbered labels and a persistent legend. Supports multi-color
layered markup: green=accepted, blue=newly detected, orange=pending.
"""

import argparse
import json
import sys
from pathlib import Path

# Ensure sibling shared.py is importable regardless of working directory
sys.path.insert(0, str(Path(__file__).parent))
from shared import safe_output_path


def markup_tags(base_path, items_json, output, color="blue", label_style="numbered"):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("ERROR: Pillow not installed. Run: pip install Pillow")
        sys.exit(1)

    with open(items_json) as f:
        items = json.load(f)

    img = Image.open(base_path).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    colors = {
        "red": (255, 0, 0, 180),
        "blue": (0, 0, 255, 180),
        "green": (0, 180, 0, 180),
        "yellow": (255, 255, 0, 180),
        "orange": (255, 140, 0, 180),
    }
    c = colors.get(color, colors["blue"])

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except (IOError, OSError):
        font = ImageFont.load_default()
        font_sm = font

    for i, item in enumerate(items, 1):
        x, y = int(item["x"]), int(item["y"])
        shape = item.get("shape", "circle")
        label = item.get("label", str(i)) if label_style != "numbered" else str(i)
        radius = item.get("radius", 20)

        if shape == "circle":
            draw.ellipse([x - radius, y - radius, x + radius, y + radius],
                         outline=c, width=3)
        elif shape in ("box", "rect"):
            w = int(item.get("width", 40))
            h = int(item.get("height", 40))
            draw.rectangle([x, y, x + w, y + h], outline=c, width=3)

        # Label offset from shape edge
        draw.text((x + radius + 4, y - 10), label, fill=c, font=font_sm)

    # Legend in top-left corner
    legend_y = 10
    draw.rectangle([5, 5, 300, 10 + len(items) * 22 + 10], fill=(255, 255, 255, 200))
    for i, item in enumerate(items, 1):
        lbl = item.get("label", f"Item {i}")
        text = f"{i}. {lbl}" if label_style == "numbered" else lbl
        draw.text((10, legend_y), text, fill=(0, 0, 0, 255), font=font_sm)
        legend_y += 22

    result = Image.alpha_composite(img, overlay)
    out_path = safe_output_path(output)
    result.convert("RGB").save(str(out_path))
    print(f"OK: {out_path} ({len(items)} items marked)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Markup tag detections on a drawing sheet")
    parser.add_argument("--base", required=True, help="Base drawing image path")
    parser.add_argument("--items", required=True, help="JSON file with items to mark")
    parser.add_argument("--output", "-o", default="marked.png", help="Output image path")
    parser.add_argument("--color", default="blue",
                        choices=["red", "blue", "green", "yellow", "orange"])
    parser.add_argument("--label-style", default="numbered", choices=["numbered", "custom"])
    args = parser.parse_args()
    markup_tags(args.base, args.items, args.output, args.color, args.label_style)
