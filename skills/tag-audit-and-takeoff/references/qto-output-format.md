# QTO Output Format

> **CRITICAL — RIGID SCHEMA.** The Excel export script (`scripts/qto_to_xlsx.py`)
> parses these exact JSON key names. If you use different keys (e.g., `qto_lines`
> instead of `line_items`), the workbook will contain all zeros. Do NOT improvise
> field names — use the schema below verbatim.

## Required Top-Level Keys

| Key | Type | Required | Consumed By |
|-----|------|----------|-------------|
| `project` | object | yes | Excel title row |
| `scope` | object | yes | Excel completeness sheet; `scope.mode` (`agentcm` or `flat_file`) picks the caveat |
| `line_items` | array | yes | Every count, and the summary, detail and to-confirm sheets |
| `type_definitions_applied` | array | yes | Excel type defs sheet |
| `completeness` | object | yes | Excel completeness sheet |
| `issues` | array | no | Excel completeness warnings |

Retired: `pending_review` (the export refuses a file that still has it; a pending tag is a `to_confirm` instance) and the count fields (`totals`, and each line item's `sheet_instances`, `derived_instances`, `deduplicated`, `building_qty`): the export counts from the instances and ignores them.

## What the count holds

Three numbers per line item, which the export computes from the instances and prints, one line per item:

- **Confirmed:** instances with `status` `accepted`, tags accepted in AgentCM's review (older files say `approved`).
- **To confirm:** instances with `status` `to_confirm`, every tag not yet accepted (older files say `new` or `pending`), plus every derived instance not `deduplicated`. Derived instances come from type definitions, not tags, so nothing confirms them.
- **Possible total:** confirmed plus to confirm.

A tag the PE already turned down in AgentCM's review has `status` `rejected`. It is in no number and not on the to-confirm list: the export lists it once, apart (its own sheet, and a line after the total).

Each instance has a `source`:

| `source` | `status` | What it is |
|---|---|---|
| `accepted_in_agentcm` | `accepted` | An accepted tag: claimed-elements' `existing_tags` with status accepted, or a line of the sheet's `.groups.tsv` |
| `pending_in_agentcm` | `to_confirm` | A tag waiting in AgentCM's review: `existing_tags` with status pending, or the sheet's `.tsv` lines of that type marked `pending` |
| `waiting_in_outbox` | `to_confirm` | A tag an earlier run saved in this skill's `outbox/` because AgentCM was closed |
| `found_this_run` | `to_confirm` | A tag this run found that matches none of the above; its `ingest` says `sent` or `outbox` |

**One tag, once.** Two instances are the same tag when they are on the same sheet, their texts match (upper case, spaces collapsed) and one box's center falls inside the other box. Keep one: an existing tag wins over this run's sighting of it and keeps its `detection_id`. The export refuses a file that lists the same tag twice (exit 2, no workbook). Instances without a `bounding_box` (flat-file vision gives rough locations) are not compared.

In flat-file mode there is no review step, so nothing is accepted: every instance is `to_confirm` with `source` `found_this_run`, and `scope.mode` is `flat_file`.

**The caveat**, which the export prints and puts under each sheet's title, and which the report repeats:

- AgentCM mode: "Confirmed: tags accepted in AgentCM's review. To confirm: every tag not yet accepted, found in this run or waiting from an earlier one, and every count derived from a type definition. Possible total: confirmed plus to confirm, what has been seen so far, not a ceiling."
- Flat-file mode: "No review step in this project (no AgentCM): every tag found is to confirm on the drawings, so none is confirmed yet. Possible total: what this run saw, not a ceiling."

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
    "mode": "agentcm",
    "csi_division": "22",
    "sheets_scanned": ["P1.01", "P1.02", "P1.03", "P2.01"],
    "sheets_with_detections": ["P1.01", "P1.02", "P2.01"],
    "sheets_with_zero": ["P1.03"]
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
      "instance_details": [
        {
          "type": "element_instance",
          "detection_id": "uuid of AgentCM's group, or this run's own id",
          "sheet": "P1.01",
          "tag_text": "WC-1",
          "room": "101",
          "view_type": "floor_plan",
          "bounding_box": {"x": 0.412, "y": 0.288, "width": 0.018, "height": 0.011},
          "status": "accepted",
          "source": "accepted_in_agentcm",
          "confidence": 0.92
        },
        {
          "type": "element_instance",
          "detection_id": "run-7",
          "sheet": "P1.01",
          "tag_text": "WC-1",
          "room": "103",
          "view_type": "floor_plan",
          "bounding_box": {"x": 0.655, "y": 0.290, "width": 0.018, "height": 0.011},
          "status": "to_confirm",
          "source": "found_this_run",
          "ingest": "sent",
          "confidence": 0.81
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
          "deduplicated": false
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

When presenting to the user, take the numbers from the export's printed lines, never your own tally, and format them as a table:

```
TAG AUDIT & QTO SUMMARY
Project: [name]
Scope: [tag_type] (CSI [division])
Sheets: [count] scanned, [count] with detections

ELEMENT           | CONFIRMED | TO CONFIRM | POSSIBLE TOTAL
------------------|-----------|------------|---------------
Water Closet WC-1 |        12 |          6 |             18
Lavatory LAV-2    |         8 |         10 |             18
Floor Drain FD-1  |        10 |          5 |             15
...

[the caveat, as the export printed it]

TO CONFIRM IN AGENTCM: [n] tags (pending in its review, waiting in the
  outbox, or found and sent in this run) and [n] derived counts

REJECTED IN AGENTCM (not counted): [n] tags the PE already turned down,
  each listed once, as the export printed them

COMPLETENESS: 66/70 (94.3%) per fixture schedule
GAPS: P1.03 (4 fixtures expected, 0 detected)

TYPE DEFINITIONS APPLIED:
  Detail 3/P5.02 "TYPICAL TOILET" → 6 rooms
    Each room: 1x WC-1, 2x LAV-2, 1x FD-1

PROVENANCE: Every count traces to detection records
  with sheet, bbox, review status, and source.
```

## File Output

Save the JSON to:
```
.construction/skills/tag-audit-and-takeoff/qto/[tag_type]_[timestamp].json
```

The Excel export produces a workbook with:
- Sheet 1: QTO Summary (confirmed, to confirm, possible total, of which derived; the caveat)
- Sheet 2: Instance Detail (one row per detection and per derivation)
- Sheet 3: Type Definitions applied
- Sheet 4: Completeness
- Sheet 5: To Confirm in AgentCM (every instance not yet accepted, and every derived count)
- Sheet 6: Rejected in AgentCM (every instance the PE turned down there; not counted)
