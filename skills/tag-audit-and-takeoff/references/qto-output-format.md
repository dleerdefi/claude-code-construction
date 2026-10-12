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

Four groups per line item, which the export computes from the instances and prints, one line per item:

- **Confirmed:** instances with `status` `accepted`, tags accepted in AgentCM's review (older files say `approved`).
- **To confirm in AgentCM:** instances with `status` `to_confirm` (older files say `new` or `pending`): a pending card in AgentCM's review (made this run or earlier), a tag waiting in the outbox, or a tag on a sheet `pending.tsv` lists (`reason` "this sheet's file is behind or edited"; such a tag is never confirmed, even if its file says accepted). Plus every derived instance not `deduplicated`: derived instances come from type definitions, not tags, so nothing confirms them.
- **Seen on the drawing, not in AgentCM:** instances with `status` `seen`: the drawing shows the tag, and the sheet's `.tsv` has no text for it, so AgentCM has no card and nobody can accept it there. Each has its `crop` (the export refuses one without) and `corrections` (`appended`, or `reported <date>` when corrections.tsv already had it).
- **Possible total:** all three.

**Groups.** Each line item's `group` is the schedule whose key column holds its code (`schedules/*.tsv`, named as INDEX.md names the table, with its sheet), or `not in any schedule`. It is the report's wording, never a `tag_type`. When line items carry it, the export also prints the numbers per group under "By schedule:", `not in any schedule` last with its codes listed.

A tag the PE already turned down in AgentCM's review has `status` `rejected`. It is in no number and not on the to-confirm list: the export lists it once, apart (its own sheet, and a line after the total).

Each instance has a `source`:

| `source` | `status` | What it is |
|---|---|---|
| `accepted_in_agentcm` | `accepted` | An accepted tag in AgentCM's files: a line of the sheet's `.groups.tsv` of that type, or an accepted line of `tags.tsv` (a point; one inside a `.groups.tsv` box is that group) |
| `pending_in_agentcm` | `to_confirm` | A tag waiting in AgentCM's review: the sheet's `.tsv` lines of that type marked `pending`, grouped into one tag |
| `waiting_in_outbox` | `to_confirm` | A tag an earlier run saved in this skill's `outbox/` because AgentCM was closed |
| `found_this_run` | from AgentCM's answer | A tag this run found that matches none of the above. Its `ingest`: `created` (to confirm, `detection_id` the new card), `already_held` (the holding card's id; `accepted` or `to_confirm` as that card is), `rejected` (`rejected`, the card the PE turned down), `no_free_text` (the box held no text: sent once more with the box redrawn from the sheet's `.tsv` lines there, and the second answer is the outcome; no lines there at all, `seen`), `not_sent` (`seen`: no text in the sheet file to send) or `outbox` (to confirm; AgentCM closed) |

Each `to_confirm` instance may carry a `reason`, shown on the to-confirm sheet: "this sheet's file is behind or edited" for a sheet `pending.tsv` lists.

**One tag, once.** Two instances are the same tag when they are on the same sheet, their texts match (upper case, spaces collapsed) and one box's center falls inside the other box. Keep one: an existing tag wins over this run's sighting of it and keeps its `detection_id`. The export refuses a file that lists the same tag twice (exit 2, no workbook). Instances without a `bounding_box` (flat-file vision gives rough locations) are not compared.

In flat-file mode there is no review step, so nothing is accepted: every instance is `to_confirm` with `source` `found_this_run`, and `scope.mode` is `flat_file`.

**The caveat**, which the export prints and puts under each sheet's title, and which the report repeats:

- AgentCM mode: "Confirmed: tags accepted in AgentCM's review. To confirm: tags waiting in AgentCM's review as pending cards (made this run or earlier) or in the outbox, tags on a sheet whose file is behind or edited, and every count derived from a type definition. Seen on the drawing, not in AgentCM: tags the drawing shows that AgentCM has no text for, so no card; each with its crop. Possible total: all three, what has been seen so far, not a ceiling."
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
      "group": "PLUMBING FIXTURE SCHEDULE (P0.01)",
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
          "detection_id": "the suggestion_id AgentCM answered with",
          "sheet": "P1.01",
          "tag_text": "WC-1",
          "room": "103",
          "view_type": "floor_plan",
          "bounding_box": {"x": 0.655, "y": 0.290, "width": 0.018, "height": 0.011},
          "status": "to_confirm",
          "source": "found_this_run",
          "ingest": "created",
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

ELEMENT           | CONFIRMED | TO CONFIRM | SEEN, NOT IN AGENTCM | POSSIBLE TOTAL
------------------|-----------|------------|----------------------|---------------
Water Closet WC-1 |        12 |          6 |                    0 |             18
Lavatory LAV-2    |         8 |          9 |                    1 |             18
Floor Drain FD-1  |        10 |          5 |                    0 |             15
...

BY SCHEDULE (as the export printed it, when line items name their group):
  PLUMBING FIXTURE SCHEDULE (P0.01): confirmed 30, to confirm 20, seen not in AgentCM 1, possible 51
  not in any schedule: confirmed 0, to confirm 2, seen not in AgentCM 0, possible 2 (XF-9, ZZ-1)

[the caveat, as the export printed it]

TO CONFIRM IN AGENTCM: [n] tags (pending in its review, waiting in the
  outbox, or on a sheet whose file is behind) and [n] derived counts

SEEN ON THE DRAWING, NOT IN AGENTCM: [n] tags AgentCM has no text for,
  each with its crop and whether corrections.tsv already had it; to clear
  one, draw its text on AgentCM's canvas and tag it

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
- Sheet 1: QTO Summary (confirmed, to confirm, seen not in AgentCM, possible total, of which derived; the caveat)
- Sheet 2: Instance Detail (one row per detection and per derivation)
- Sheet 3: Type Definitions applied
- Sheet 4: Completeness
- Sheet 5: To Confirm in AgentCM (every instance not yet accepted, and every derived count, each with its reason)
- Sheet 6: Seen, not in AgentCM (every tag AgentCM has no text for: its box, crop and corrections line, and how to clear it)
- Sheet 7: Rejected in AgentCM (every instance the PE turned down there; not counted)
