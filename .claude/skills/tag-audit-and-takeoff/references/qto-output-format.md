# QTO Output Format

> **CRITICAL — RIGID SCHEMA.** The Excel export script (`scripts/qto_to_xlsx.py`)
> parses these exact JSON key names. If you use different keys (e.g., `qto_lines`
> instead of `line_items`, or `summary` instead of `totals`), the workbook will
> contain all zeros. Do NOT improvise field names — use the schema below verbatim.

## Required Top-Level Keys

| Key | Type | Required | Consumed By |
|-----|------|----------|-------------|
| `project` | object | yes | Excel title row |
| `scope` | object | yes | Excel completeness sheet |
| `totals` | object | yes | Excel summary sub-header |
| `line_items` | array | yes | Excel summary + detail sheets |
| `type_definitions_applied` | array | yes | Excel type defs sheet |
| `completeness` | object | yes | Excel completeness sheet |
| `issues` | array | no | Excel completeness warnings |

## Summary Report Structure

The QTO summary is a JSON document that serves as both the machine-
readable output and the source for human-readable reports.

```json
{
  "project": {
    "name": "Project name from CLAUDE.md or user input",
    "generated_at": "ISO 8601 timestamp",
    "generated_by": "tag-audit-and-takeoff skill"
  },
  "scope": {
    "tag_type": "plumbing_fixtures",
    "csi_division": "22",
    "sheets_scanned": ["P1.01", "P1.02", "P1.03", "P2.01"],
    "sheets_with_detections": ["P1.01", "P1.02", "P2.01"],
    "sheets_with_zero": ["P1.03"]
  },
  "totals": {
    "sheet_instances": 43,
    "derived_instances": 28,
    "deduplicated": 5,
    "building_quantity": 66
  },
  "completeness": {
    "schedule_reference": "Plumbing Fixture Schedule on P0.01",
    "expected_count": 70,
    "detected_count": 66,
    "coverage_pct": 94.3,
    "gap_sheets": ["P1.03"],
    "gap_notes": "4 fixtures expected per schedule not detected"
  },
  "line_items": [
    {
      "element": "Water Closet",
      "designation": "WC-1",
      "sheet_instances": 12,
      "derived_instances": 8,
      "deduplicated": 2,
      "building_qty": 18,
      "instance_details": [
        {
          "type": "element_instance",
          "detection_id": "uuid",
          "sheet": "P1.01",
          "room": "101",
          "status": "approved",
          "approved_at": "ISO 8601"
        }
      ],
      "derived_details": [
        {
          "type": "derived_instance",
          "derived_id": "uuid",
          "type_def_id": "uuid",
          "source_detail": "3/P5.02",
          "source_label": "TYPICAL TOILET",
          "target_room": "203",
          "target_sheet": "P1.02",
          "derivation_method": "room_type_match",
          "deduplicated": false,
          "status": "approved"
        }
      ]
    }
  ],
  "type_definitions_applied": [
    {
      "type_def_id": "uuid",
      "source_detail": "3/P5.02",
      "parent_view_label": "TYPICAL TOILET",
      "elements_defined": [
        { "tag_text": "WC-1", "count_per_instance": 1 },
        { "tag_text": "LAV-2", "count_per_instance": 2 },
        { "tag_text": "FD-1", "count_per_instance": 1 }
      ],
      "applied_to_rooms": ["101","103","201","203","301","303"],
      "applied_count": 6,
      "derivation_method": "room_type_match"
    }
  ],
  "issues": [
    {
      "severity": "warning",
      "message": "Sheet P1.03 has 4 toilet rooms but zero plumbing fixture tags detected",
      "suggested_action": "Manual review of P1.03 for untagged fixtures"
    }
  ]
}
```

## Human-Readable Report

When presenting to the user, format the summary as a table:

```
TAG AUDIT & QTO SUMMARY
Project: [name]
Scope: [tag_type] (CSI [division])
Sheets: [count] scanned, [count] with detections

ELEMENT           | SHEET | DERIVED | DEDUP | TOTAL
------------------|-------|---------|-------|------
Water Closet WC-1 |    12 |       8 |     2 |   18
Lavatory LAV-2    |     8 |      12 |     2 |   18
Floor Drain FD-1  |    10 |       6 |     1 |   15
...

COMPLETENESS: 66/70 (94.3%) per fixture schedule
GAPS: P1.03 (4 fixtures expected, 0 detected)

TYPE DEFINITIONS APPLIED:
  Detail 3/P5.02 "TYPICAL TOILET" → 6 rooms
    Each room: 1x WC-1, 2x LAV-2, 1x FD-1

PROVENANCE: Every count traces to detection records
  with sheet, bbox, approval status, and timestamp.
```

## File Output

Save the JSON to:
```
.construction/qto/[tag_type]_[timestamp].json
```

If the user requests an Excel output, produce a workbook with:
- Sheet 1: Summary table (as above)
- Sheet 2: Instance detail (one row per detection)
- Sheet 3: Derived detail (one row per derivation)
- Sheet 4: Type definitions applied
