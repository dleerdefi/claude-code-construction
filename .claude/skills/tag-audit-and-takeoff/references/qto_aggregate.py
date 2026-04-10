#!/usr/bin/env python3
"""
qto_aggregate.py — Aggregate approved detection records into a QTO summary.

Usage:
  python qto_aggregate.py \
    --detections detections.json \
    --project-name "Holabird Academy" \
    --tag-type plumbing_fixtures \
    --csi-division 22 \
    --schedule-count 70 \
    --output qto_summary.json

Input: JSON array of detection records (schema: detection-record.schema.json)
       Only records with status="approved" are counted.

Output: QTO summary JSON (format defined in references/qto-output-format.md)
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone


def aggregate(
    detections: list,
    project_name: str,
    tag_type: str,
    csi_division: str,
    schedule_count: int = None,
) -> dict:
    """Aggregate approved detection records into QTO summary."""

    approved = [d for d in detections if d.get("status") == "approved"]

    # Separate by record type
    instances = [d for d in approved if d["record_type"] == "element_instance"]
    type_defs = [d for d in approved if d["record_type"] == "element_type_def"]
    derived = [d for d in approved if d["record_type"] == "derived_instance"]

    # Deduplicated derived instances don't count
    derived_active = [d for d in derived if not d.get("deduplicated", False)]
    derived_deduped = [d for d in derived if d.get("deduplicated", False)]

    # Collect all sheets
    all_sheets = set()
    sheets_with_detections = set()
    for d in approved:
        all_sheets.add(d["sheet_id"])
        if d["record_type"] in ("element_instance", "element_type_def"):
            sheets_with_detections.add(d["sheet_id"])

    # Group by element designation for line items
    line_items = defaultdict(lambda: {
        "sheet_instances": [],
        "derived_instances": [],
        "deduplicated_count": 0,
    })

    for inst in instances:
        key = inst["tag_text"]
        line_items[key]["sheet_instances"].append({
            "type": "element_instance",
            "detection_id": inst["id"],
            "sheet": inst["sheet_id"],
            "room": inst.get("associated_items", {}).get("room_number", {}).get("text", ""),
            "status": inst["status"],
            "approved_at": inst.get("approved_at"),
        })

    for d in derived:
        key = d["tag_text"]
        detail = {
            "type": "derived_instance",
            "derived_id": d["id"],
            "type_def_id": d.get("type_def_id"),
            "source_detail": d.get("source_detail", ""),
            "source_label": d.get("parent_view_label", ""),
            "target_room": d.get("target_room", ""),
            "target_sheet": d["sheet_id"],
            "derivation_method": d.get("derivation_method", ""),
            "deduplicated": d.get("deduplicated", False),
            "status": d["status"],
        }
        line_items[key]["derived_instances"].append(detail)
        if d.get("deduplicated", False):
            line_items[key]["deduplicated_count"] += 1

    # Build line item summaries
    line_item_list = []
    total_sheet = 0
    total_derived = 0
    total_dedup = 0

    for element, data in sorted(line_items.items()):
        sheet_count = len(data["sheet_instances"])
        derived_count = len([d for d in data["derived_instances"] if not d["deduplicated"]])
        dedup_count = data["deduplicated_count"]
        building_qty = sheet_count + derived_count

        total_sheet += sheet_count
        total_derived += derived_count
        total_dedup += dedup_count

        line_item_list.append({
            "element": element,
            "designation": element,
            "sheet_instances": sheet_count,
            "derived_instances": derived_count,
            "deduplicated": dedup_count,
            "building_qty": building_qty,
            "instance_details": data["sheet_instances"],
            "derived_details": data["derived_instances"],
        })

    total_building = total_sheet + total_derived

    # Build type definitions applied
    type_def_summaries = []
    for td in type_defs:
        elements_in = td.get("elements_in_type", [])
        applied_rooms = [
            d.get("target_room", "")
            for d in derived
            if d.get("type_def_id") == td["id"] and not d.get("deduplicated", False)
        ]
        type_def_summaries.append({
            "type_def_id": td["id"],
            "source_detail": td.get("source_detail", ""),
            "parent_view_label": td.get("parent_view_label", ""),
            "elements_defined": elements_in,
            "applied_to_rooms": sorted(set(applied_rooms)),
            "applied_count": len(set(applied_rooms)),
            "derivation_method": "room_type_match",
        })

    # Completeness
    completeness = {}
    if schedule_count is not None:
        coverage = (total_building / schedule_count * 100) if schedule_count > 0 else 0
        gap_sheets = sorted(all_sheets - sheets_with_detections)
        completeness = {
            "schedule_reference": "User-provided schedule count",
            "expected_count": schedule_count,
            "detected_count": total_building,
            "coverage_pct": round(coverage, 1),
            "gap_sheets": gap_sheets,
            "gap_notes": (
                f"{schedule_count - total_building} items expected per schedule not detected"
                if total_building < schedule_count else "All expected items detected"
            ),
        }

    # Issues
    issues = []
    if schedule_count and total_building < schedule_count:
        issues.append({
            "severity": "warning",
            "message": (
                f"Detected {total_building} of {schedule_count} expected "
                f"{tag_type}. {schedule_count - total_building} items not found."
            ),
            "suggested_action": "Review gap sheets for untagged items",
        })

    sheets_zero = sorted(all_sheets - sheets_with_detections)
    for s in sheets_zero:
        issues.append({
            "severity": "info",
            "message": f"Sheet {s} scanned but zero {tag_type} detected",
            "suggested_action": f"Verify {s} contains {tag_type} scope",
        })

    return {
        "project": {
            "name": project_name,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": "tag-audit-and-takeoff skill",
        },
        "scope": {
            "tag_type": tag_type,
            "csi_division": csi_division,
            "sheets_scanned": sorted(all_sheets),
            "sheets_with_detections": sorted(sheets_with_detections),
            "sheets_with_zero": sheets_zero,
        },
        "totals": {
            "sheet_instances": total_sheet,
            "derived_instances": total_derived,
            "deduplicated": total_dedup,
            "building_quantity": total_building,
        },
        "completeness": completeness if completeness else None,
        "line_items": line_item_list,
        "type_definitions_applied": type_def_summaries,
        "issues": issues,
    }


def format_table(summary: dict) -> str:
    """Format QTO summary as human-readable table."""
    lines = []
    lines.append("TAG AUDIT & QTO SUMMARY")
    lines.append(f"Project: {summary['project']['name']}")
    lines.append(f"Scope: {summary['scope']['tag_type']} (CSI {summary['scope']['csi_division']})")
    lines.append(
        f"Sheets: {len(summary['scope']['sheets_scanned'])} scanned, "
        f"{len(summary['scope']['sheets_with_detections'])} with detections"
    )
    lines.append("")

    # Header
    lines.append(f"{'ELEMENT':<30} | {'SHEET':>5} | {'DERIVED':>7} | {'DEDUP':>5} | {'TOTAL':>5}")
    lines.append("-" * 30 + "-+-" + "-" * 5 + "-+-" + "-" * 7 + "-+-" + "-" * 5 + "-+-" + "-" * 5)

    for item in summary["line_items"]:
        lines.append(
            f"{item['element']:<30} | {item['sheet_instances']:>5} | "
            f"{item['derived_instances']:>7} | {item['deduplicated']:>5} | "
            f"{item['building_qty']:>5}"
        )

    lines.append("")
    t = summary["totals"]
    lines.append(
        f"{'TOTALS':<30} | {t['sheet_instances']:>5} | "
        f"{t['derived_instances']:>7} | {t['deduplicated']:>5} | "
        f"{t['building_quantity']:>5}"
    )

    if summary.get("completeness"):
        c = summary["completeness"]
        lines.append("")
        lines.append(f"COMPLETENESS: {c['detected_count']}/{c['expected_count']} ({c['coverage_pct']}%)")
        if c.get("gap_sheets"):
            lines.append(f"GAPS: {', '.join(c['gap_sheets'])}")
        lines.append(f"NOTE: {c['gap_notes']}")

    if summary.get("type_definitions_applied"):
        lines.append("")
        lines.append("TYPE DEFINITIONS APPLIED:")
        for td in summary["type_definitions_applied"]:
            lines.append(
                f"  {td['source_detail']} \"{td['parent_view_label']}\" "
                f"→ {td['applied_count']} rooms"
            )

    if summary.get("issues"):
        lines.append("")
        lines.append("ISSUES:")
        for issue in summary["issues"]:
            lines.append(f"  [{issue['severity'].upper()}] {issue['message']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Aggregate detections into QTO summary")
    parser.add_argument("--detections", required=True, help="JSON file with detection records")
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--tag-type", required=True)
    parser.add_argument("--csi-division", required=True)
    parser.add_argument("--schedule-count", type=int, default=None,
                        help="Expected count from fixture/door schedule")
    parser.add_argument("--output", default="-", help="Output JSON file (- for stdout)")
    parser.add_argument("--table", action="store_true", help="Also print human-readable table")

    args = parser.parse_args()

    with open(args.detections) as f:
        detections = json.load(f)

    summary = aggregate(
        detections,
        args.project_name,
        args.tag_type,
        args.csi_division,
        args.schedule_count,
    )

    output_json = json.dumps(summary, indent=2)
    if args.output == "-":
        print(output_json)
    else:
        with open(args.output, "w") as f:
            f.write(output_json)
        print(f"QTO summary written to {args.output}", file=sys.stderr)

    if args.table:
        print("\n" + format_table(summary), file=sys.stderr)


if __name__ == "__main__":
    main()
