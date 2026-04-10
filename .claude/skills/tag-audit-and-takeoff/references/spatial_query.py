#!/usr/bin/env python3
"""
spatial_query.py — Anchor search and neighborhood query for tag detection.

Usage:
  # Find anchor items by text
  python spatial_query.py anchor --sheet-id P1.01 --search-text "FREEZER" --db-url postgresql://...

  # Get neighborhood around an anchor bbox
  python spatial_query.py neighborhood --sheet-id P1.01 \
    --anchor-x 412 --anchor-y 308 --anchor-w 72 --anchor-h 14 \
    --pad 80 --db-url postgresql://...

  # Batch mode: anchors + neighborhoods for multiple tags from a JSON file
  python spatial_query.py batch --input tags.json --db-url postgresql://... --output candidates.json

Output: JSON array of extracted items with id, text, bbox coordinates.
"""

import argparse
import json
import sys
from typing import Optional

# DB connection is injected at runtime — this script defines the queries
# and can be executed by Claude Code with the project's DB credentials.


def build_anchor_query(sheet_id: str, search_text: str) -> dict:
    """Build SQL query to find anchor items by text content."""
    # Use the most distinctive word — caller should pre-select this
    return {
        "sql": """
            SELECT id, text, bbox_x, bbox_y, bbox_w, bbox_h
            FROM extracted_items
            WHERE sheet_id = %(sheet_id)s
            AND LOWER(text) LIKE LOWER(%(pattern)s)
            ORDER BY bbox_y, bbox_x
        """,
        "params": {
            "sheet_id": sheet_id,
            "pattern": f"%{search_text}%"
        }
    }


def build_neighborhood_query(
    sheet_id: str,
    anchor_x: float, anchor_y: float,
    anchor_w: float, anchor_h: float,
    pad: float
) -> dict:
    """Build SQL query to get items in spatial neighborhood of anchor."""
    return {
        "sql": """
            SELECT id, text, bbox_x, bbox_y, bbox_w, bbox_h
            FROM extracted_items
            WHERE sheet_id = %(sheet_id)s
            AND bbox_x >= %(min_x)s AND bbox_x <= %(max_x)s
            AND bbox_y >= %(min_y)s AND bbox_y <= %(max_y)s
            ORDER BY bbox_y, bbox_x
        """,
        "params": {
            "sheet_id": sheet_id,
            "min_x": anchor_x - pad,
            "max_x": anchor_x + anchor_w + pad,
            "min_y": anchor_y - pad,
            "max_y": anchor_y + anchor_h + pad,
        }
    }


def build_dedup_query(
    sheet_id: str, tag_type: str,
    bbox_x: float, bbox_y: float,
    bbox_w: float, bbox_h: float,
    overlap_threshold: float = 0.7
) -> dict:
    """Build SQL query to check for existing detections that overlap."""
    return {
        "sql": """
            SELECT id, tag_text, composite_bbox, status
            FROM detections
            WHERE sheet_id = %(sheet_id)s
            AND tag_type = %(tag_type)s
            AND status IN ('approved', 'pending_review')
            AND spatial_overlap(
                composite_bbox,
                jsonb_build_object(
                    'x', %(bbox_x)s, 'y', %(bbox_y)s,
                    'w', %(bbox_w)s, 'h', %(bbox_h)s
                )
            ) > %(threshold)s
        """,
        "params": {
            "sheet_id": sheet_id,
            "tag_type": tag_type,
            "bbox_x": bbox_x,
            "bbox_y": bbox_y,
            "bbox_w": bbox_w,
            "bbox_h": bbox_h,
            "threshold": overlap_threshold,
        }
    }


def cluster_anchors(items: list, cluster_distance: float = 200) -> list:
    """
    Group anchor items into spatial clusters.
    Items within cluster_distance of each other belong to the same tag.
    Returns list of clusters, each cluster is a list of items.
    """
    if not items:
        return []

    # Sort by position
    sorted_items = sorted(items, key=lambda i: (i["bbox_y"], i["bbox_x"]))
    clusters = [[sorted_items[0]]]

    for item in sorted_items[1:]:
        merged = False
        for cluster in clusters:
            for member in cluster:
                dx = abs(item["bbox_x"] - member["bbox_x"])
                dy = abs(item["bbox_y"] - member["bbox_y"])
                if dx < cluster_distance and dy < cluster_distance:
                    cluster.append(item)
                    merged = True
                    break
            if merged:
                break
        if not merged:
            clusters.append([item])

    return clusters


def compute_cluster_bbox(cluster: list, pad: float) -> dict:
    """Compute padded bounding box for a cluster of items."""
    min_x = min(i["bbox_x"] for i in cluster)
    min_y = min(i["bbox_y"] for i in cluster)
    max_x = max(i["bbox_x"] + i["bbox_w"] for i in cluster)
    max_y = max(i["bbox_y"] + i["bbox_h"] for i in cluster)

    return {
        "min_x": min_x - pad,
        "min_y": min_y - pad,
        "max_x": max_x + pad,
        "max_y": max_y + pad,
    }


def build_batch_queries(tags_input: list, sheet_id: str, default_pad: float = 80) -> list:
    """
    Build anchor + neighborhood query pairs for a batch of tags.

    tags_input: list of {"tag_text": str, "search_word": str, "pad": float (optional)}
    Returns: list of {"tag_text": str, "anchor_query": dict, "pad": float}
    """
    results = []
    for tag in tags_input:
        search_word = tag.get("search_word", tag["tag_text"].split()[-1])
        pad = tag.get("pad", default_pad)
        results.append({
            "tag_text": tag["tag_text"],
            "anchor_query": build_anchor_query(sheet_id, search_word),
            "pad": pad,
        })
    return results


def main():
    parser = argparse.ArgumentParser(description="Spatial query helper for tag detection")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Anchor subcommand
    anchor_parser = subparsers.add_parser("anchor", help="Find anchor items by text")
    anchor_parser.add_argument("--sheet-id", required=True)
    anchor_parser.add_argument("--search-text", required=True)

    # Neighborhood subcommand
    nbr_parser = subparsers.add_parser("neighborhood", help="Get spatial neighborhood")
    nbr_parser.add_argument("--sheet-id", required=True)
    nbr_parser.add_argument("--anchor-x", type=float, required=True)
    nbr_parser.add_argument("--anchor-y", type=float, required=True)
    nbr_parser.add_argument("--anchor-w", type=float, required=True)
    nbr_parser.add_argument("--anchor-h", type=float, required=True)
    nbr_parser.add_argument("--pad", type=float, default=80)

    # Batch subcommand
    batch_parser = subparsers.add_parser("batch", help="Batch anchor + neighborhood queries")
    batch_parser.add_argument("--input", required=True, help="JSON file with tag list")
    batch_parser.add_argument("--sheet-id", required=True)
    batch_parser.add_argument("--output", default="-", help="Output file (- for stdout)")

    args = parser.parse_args()

    if args.command == "anchor":
        query = build_anchor_query(args.sheet_id, args.search_text)
        print(json.dumps(query, indent=2))

    elif args.command == "neighborhood":
        query = build_neighborhood_query(
            args.sheet_id,
            args.anchor_x, args.anchor_y,
            args.anchor_w, args.anchor_h,
            args.pad
        )
        print(json.dumps(query, indent=2))

    elif args.command == "batch":
        with open(args.input) as f:
            tags = json.load(f)
        queries = build_batch_queries(tags, args.sheet_id)
        output = json.dumps(queries, indent=2)
        if args.output == "-":
            print(output)
        else:
            with open(args.output, "w") as f:
                f.write(output)


if __name__ == "__main__":
    main()
