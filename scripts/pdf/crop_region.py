#!/usr/bin/env python3
"""Crop a region from an image. Supports anchor-based and absolute box cropping."""

import argparse
import sys

def crop(image_path, output="cropped.png", anchor=None, width=None, height=None,
         box=None, padding=0):
    try:
        from PIL import Image
    except ImportError:
        print("ERROR: Pillow not installed. Run: pip install Pillow")
        sys.exit(1)

    img = Image.open(image_path)
    img_w, img_h = img.size

    if box:
        # Absolute box: x1,y1,x2,y2 in pixels
        coords = [int(v) for v in box.split(",")]
        x1, y1, x2, y2 = coords
        # Apply padding
        x1 = max(0, x1 - padding)
        y1 = max(0, y1 - padding)
        x2 = min(img_w, x2 + padding)
        y2 = min(img_h, y2 + padding)
    elif anchor and width and height:
        # Anchor-based: crop from a corner
        anchors = {
            "bottom-right": (img_w - width, img_h - height, img_w, img_h),
            "bottom-left": (0, img_h - height, width, img_h),
            "top-right": (img_w - width, 0, img_w, height),
            "top-left": (0, 0, width, height),
            "center": ((img_w - width) // 2, (img_h - height) // 2,
                       (img_w + width) // 2, (img_h + height) // 2),
        }
        if anchor not in anchors:
            print(f"ERROR: Invalid anchor '{anchor}'. Use: {list(anchors.keys())}")
            sys.exit(1)
        x1, y1, x2, y2 = anchors[anchor]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(img_w, x2), min(img_h, y2)
    else:
        print("ERROR: Provide either --box or --anchor with --width and --height")
        sys.exit(1)

    cropped = img.crop((x1, y1, x2, y2))
    cropped.save(output)
    print(f"OK: {output} ({cropped.width}x{cropped.height}px)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crop a region from an image")
    parser.add_argument("image", help="Path to input image")
    parser.add_argument("--output", "-o", default="cropped.png")
    parser.add_argument("--anchor", choices=["bottom-right","bottom-left","top-right","top-left","center"])
    parser.add_argument("--width", type=int, help="Crop width in pixels")
    parser.add_argument("--height", type=int, help="Crop height in pixels")
    parser.add_argument("--box", help="Crop box as x1,y1,x2,y2 in pixels")
    parser.add_argument("--padding", type=int, default=0, help="Padding around box in pixels")
    args = parser.parse_args()
    crop(args.image, args.output, args.anchor, args.width, args.height, args.box, args.padding)
