#!/usr/bin/env python3
"""Overlay viewport boundary rectangles on a construction drawing sheet.

Per-skill script for viewport-highlighter. Draws rectangles with titled
or numbered labels. Supports amber color for viewport boundaries.
"""

import argparse
import json
import sys
from pathlib import Path

# Ensure sibling shared.py is importable regardless of working directory
sys.path.insert(0, str(Path(__file__).parent))
from shared import safe_output_path


def markup_viewports(base_path, items_json, output, color="amber", label_style="titled"):
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
        "amber": (255, 191, 0, 200),
        "red": (255, 0, 0, 200),
        "blue": (0, 0, 255, 200),
        "green": (0, 180, 0, 200),
        "yellow": (255, 230, 0, 200),
        "orange": (255, 140, 0, 200),
    }
    c = colors.get(color, colors["amber"])
    c_solid = (*c[:3], 255)
    c_bg = (*c[:3], 180)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except (IOError, OSError):
        font = ImageFont.load_default()
        font_sm = font

    for i, item in enumerate(items, 1):
        x = int(item["x"])
        y = int(item["y"])
        w = int(item.get("width", 100))
        h = int(item.get("height", 100))
        label = item.get("label", f"Viewport {i}")

        # Viewport rectangle
        draw.rectangle([x, y, x + w, y + h], outline=c_solid, width=3)

        if label_style == "titled":
            # Label bar inside top edge of the rectangle
            label_text = label
            char_w = 8  # approximate char width at font_sm size
            bar_w = min(len(label_text) * char_w + 12, w)
            draw.rectangle([x, y, x + bar_w, y + 22], fill=c_bg)
            draw.text((x + 4, y + 3), label_text, fill=(0, 0, 0, 255), font=font_sm)
        else:
            # Numbered: circle badge at top-left corner
            r = 14
            draw.ellipse([x - r, y - r, x + r, y + r], fill=c_solid)
            num_text = str(i)
            draw.text((x - 5, y - 10), num_text, fill=(255, 255, 255, 255), font=font)

    # Legend for numbered style
    if label_style == "numbered":
        legend_h = len(items) * 22 + 20
        draw.rectangle([5, 5, 310, legend_h + 10], fill=(255, 255, 255, 210))
        for i, item in enumerate(items, 1):
            label = item.get("label", f"Viewport {i}")
            draw.text((10, 12 + i * 22), f"{i}. {label}", fill=(0, 0, 0, 255), font=font_sm)

    result = Image.alpha_composite(img, overlay)
    out_path = safe_output_path(output)
    result.convert("RGB").save(str(out_path))
    print(f"OK: {out_path} ({len(items)} viewports marked)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Markup viewport boundaries on a drawing sheet")
    parser.add_argument("--base", required=True, help="Base drawing image path")
    parser.add_argument("--items", required=True, help="JSON file with viewport rectangles")
    parser.add_argument("--output", "-o", default="marked.png", help="Output image path")
    parser.add_argument("--color", default="amber",
                        choices=["amber", "red", "blue", "green", "yellow", "orange"])
    parser.add_argument("--label-style", default="titled", choices=["titled", "numbered"])
    args = parser.parse_args()
    markup_viewports(args.base, args.items, args.output, args.color, args.label_style)
