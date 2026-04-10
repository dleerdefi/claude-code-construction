---
name: schedule-extractor
description: >
  Extract tabular schedule data from construction drawings — door, window,
  finish, fixture, panel schedules — and output to Excel. Triggers: 'door
  schedule', 'extract schedule', 'schedule to Excel', 'panel schedule'.
argument-hint: "<sheet_number> [schedule_type]"
disable-model-invocation: true
---

# Schedule Extractor

Extracts tabular schedule data embedded in drawing sheets or spec pages and outputs structured Excel files. Schedules are typically one element among many on a sheet — or the entire sheet may be a schedule.

## Workflow

```
Extraction Progress:
- [ ] Step 1: Discover schedule locations
- [ ] Step 2: Isolate (crop) the schedule region
- [ ] Step 3: Extract structured data (pdfplumber + vision)
- [ ] Step 4: Validate and clean data
- [ ] Step 5: Output to Excel
- [ ] Step 6: Write graph entry
```

### Step 1: Discover Schedule Locations

Use a multi-source discovery approach, checking all available sources:

#### Source A — Sheet titles in sheet index (primary, most reliable)

Search `.construction/index/sheet_index.yaml` (or the sheet index you've built) for sheets with "SCHEDULE" in the title. Many important schedules occupy an **entire sheet** — the sheet title tells you exactly what it is:
- "DOOR SCHEDULE" → entire sheet is a door schedule
- "FINISH SCHEDULE" or "ROOM FINISH SCHEDULE" → entire sheet is finishes
- "WINDOW SCHEDULE" → entire sheet is windows
- "PANEL SCHEDULE" → electrical panel schedule
- "FIXTURE SCHEDULE" → plumbing fixtures

For dedicated schedule sheets, the entire page is the extraction target — no need to crop.

#### Source B — AgentCM database query (supplementary)

If `.construction/database.yaml` exists, read `query_command` from it, then query known schedules:
```bash
# Read query_command and project_id from .construction/database.yaml
{query_command} -c "SELECT id, schedule_type, title, sheet_id, bounding_region FROM schedules WHERE project_id = '{PROJECT_ID}'"
```
This returns all schedules already detected (including stubs from Group Review with bounding regions). For embedded schedules on non-schedule sheets, check the `bounding_region` column.

**Note**: Schedule bounding region detection is still being refined — treat these as hints, not definitive boundaries. Always verify with vision.

#### Source C — Discipline-based heuristics

Schedules appear on specific sheet types:
- **Door schedule** → typically on A-0.XX or A-8.XX sheets, or a dedicated sheet
- **Window schedule** → same sheets as door schedule, or separate
- **Room finish schedule** → A-0.XX or interior sheets
- **Panel schedule** → E-X.XX electrical sheets
- **Fixture schedule** → P-X.XX plumbing sheets
- **Equipment schedule** → M-X.XX mechanical sheets

#### Source D — Vision scan (fallback)

If no index or graph is available:
```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/../../scripts/pdf/rasterize_page.py {pdf_path} {page} --dpi 150 --output full_sheet.png
```

Use vision on the full sheet image: "Identify any tabular schedules on this drawing sheet. Report the approximate bounding box coordinates (top-left x,y and bottom-right x,y) as percentages of the image dimensions, the schedule type, and the column headers visible."

### Step 2: Isolate the Schedule Region

**For dedicated schedule sheets** (entire page is a schedule): Skip cropping — use the full page.

**For embedded schedules** (schedule is one element on a larger sheet):

Crop the identified region with padding:
```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/../../scripts/pdf/crop_region.py full_sheet.png \
  --box {x1},{y1},{x2},{y2} \
  --padding 20 \
  --output schedule_crop.png
```

Re-rasterize at higher DPI (300) for the cropped region to improve text clarity:
```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/../../scripts/pdf/rasterize_page.py {pdf_path} {page} \
  --dpi 300 \
  --crop {x1},{y1},{x2},{y2} \
  --output schedule_hires.png
```

### Step 3: Extract Structured Data

Use a **try → validate → fallback** approach:

#### Method A — pdfplumber table extraction (try first)

Use pdfplumber's `extract_tables()` method on the target page. If multiple tables are found, select the largest one (most rows with the most columns — schedules are wide). The first row of the selected table contains headers; subsequent rows are data. If no tables are found or results look garbled, fall back to vision (Method B).

#### Evaluate Method A — Quality Gate

**Check these criteria before proceeding:**

1. **Row count**: Did pdfplumber extract at least 10 data rows? Most schedules have 20-200+ entries.
2. **Column consistency**: Do ≥80% of rows have the same number of columns? Inconsistent columns = parsing error.
3. **Non-empty cells**: Are >50% of cells non-empty? Mostly-empty extraction = parsing failed.
4. **First column validity**: Does the first column contain recognizable IDs (door numbers, room numbers, equipment tags)?

**Decision:**
- All 4 checks pass → **Method A succeeded**, proceed to Step 4
- Any check fails → **Method A failed**, use Method B below

```
QUALITY GATE:
  extracted_rows >= 10?          YES → check next  |  NO → use Method B
  column_consistency >= 80%?     YES → check next  |  NO → use Method B
  non_empty_cells >= 50%?        YES → check next  |  NO → use Method B
  first_col_has_valid_ids?       YES → use Method A |  NO → use Method B
```

#### Method B — Vision extraction (fallback)

When pdfplumber fails (common with complex layouts, merged cells, non-standard table lines):

1. **Rasterize** the sheet at 150 DPI for overview:
```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/../../scripts/pdf/rasterize_page.py {pdf_path} {page} --dpi 150 --output full_sheet.png
```

2. **Use vision** on the full sheet image to read the schedule directly:

"This is a construction drawing sheet containing a schedule (tabular data). Extract ALL rows from the schedule as a JSON array of objects. The first row of the table contains column headers — use those as object keys. Each subsequent row is one entry. Preserve exact values including dimensions, abbreviations, and codes. If a cell is empty, use null."

3. For dense schedules with small text, **re-rasterize at 300 DPI** and crop to just the schedule region:
```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/../../scripts/pdf/rasterize_page.py {pdf_path} {page} --dpi 300 --output schedule_hires.png
```

#### Method C — Hybrid (for maximum accuracy)

Run both methods and cross-validate:
- pdfplumber gives exact text positioning and catches every character
- Vision catches content pdfplumber misses (stamps, handwritten marks, non-standard table layouts)
- Compare row counts: if they differ by >10%, investigate the discrepancy
- Use vision results for rows that pdfplumber returned empty or garbled

### Step 4: Validate and Clean

After extraction (by either method):

- **Row count check**: Compare extracted count against what's visually present. If off by >10%, re-extract using the other method.
- **Column structure**: Verify headers match expected schedule type (door schedule has MARK/SIZE/TYPE/FRAME/HARDWARE; finish schedule has RM.NO/NAME/FLOOR/BASE/WALLS/CLG)
- **Merged cell cleanup**: Expand merged header cells (e.g., "WALLS" spanning A/B/C/D sub-columns)
- **Normalize dimensions**: `3' - 0"` → `3'-0"` (remove spaces around dashes)
- **Flag revisions**: Note any cells within revision clouds or delta markers
- **Cross-reference with database**: If `.construction/database.yaml` exists, read `query_command` from it, then verify room numbers via `{query_command} -c "SELECT number FROM rooms WHERE project_id = '{PROJECT_ID}' AND number = '{room_number}'"` and door numbers via `{query_command} -c "SELECT tag_number FROM graph_elements WHERE element_type = 'door' AND tag_number = '{door_mark}'"`

### Step 5: Output to Excel

```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/scripts/schedule_to_xlsx.py \
  --data schedule_data.json \
  --type door_schedule \
  --project "Project Name" \
  --sheet "A-0.01" \
  --output "Door_Schedule_A-0.01.xlsx"
```

The script creates a formatted Excel workbook with:
- Header row with project info and source sheet
- Auto-sized columns
- Conditional formatting for empty/flagged cells
- Source metadata in a separate tab

### Step 6: Ingest to Database

After Excel output, POST extracted data to the AgentCM schedule ingest API so it's stored in PostgreSQL, linked to rooms, and queryable by agents:

```bash
# Read api_url and project_id from .construction/database.yaml
curl -X POST "{api_url}/projects/{project_id}/schedules/ingest" \
  -H "Content-Type: application/json" \
  -d @schedule_ingest_payload.json
```

The ingest payload JSON follows this structure:

```json
{
  "sheetId": "<uuid of the source sheet>",
  "scheduleType": "door",
  "title": "DOOR SCHEDULE",
  "rowEntityType": "door",
  "columns": [
    {"key": "MARK", "header": "MARK"},
    {"key": "WIDTH", "header": "WIDTH"},
    {"key": "HEIGHT", "header": "HEIGHT"},
    {"key": "TYPE", "header": "TYPE"},
    {"key": "FRAME", "header": "FRAME"},
    {"key": "HARDWARE_SET", "header": "HARDWARE SET"},
    {"key": "FIRE_RATING", "header": "FIRE RATING"}
  ],
  "rows": [
    {
      "entityIdentifier": "2.101A",
      "cells": {"MARK": "2.101A", "WIDTH": "3'-0\"", "HEIGHT": "7'-0\"", "TYPE": "A", "FRAME": "HM", "HARDWARE_SET": "HW-3", "FIRE_RATING": "1 HR"}
    }
  ],
  "sourceMethod": "pdfplumber",
  "confidence": 0.95
}
```

**Schedule types and their `rowEntityType`:**
- Door schedule → `"door"` (room derived from door number: "2.101A" → Room 2.101)
- Window schedule → `"window"` (room derived from window mark)
- Finish schedule → `"room"` (entity identifier IS the room number)
- Panel schedule → `"equipment"`
- Fixture schedule → `"fixture"` (room linked spatially from plan tags)

The ingest endpoint automatically:
1. Creates/updates the schedule record
2. Inserts all rows with GIN-indexed jsonb cells
3. Links rows to rooms (exact match, fuzzy match, or creates rooms from schedule data)
4. Extracts finish/hardware codes into the code legends table
5. Creates pending links for fixtures/equipment that need spatial resolution

**Also write the graph finding entry** (for backwards compatibility with existing skills):

```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/../../scripts/graph/write_finding.py \
  --type "schedule_extracted" \
  --title "Door schedule extracted from A-0.01" \
  --source_sheet "A-0.01" \
  --output_file "Door_Schedule_A-0.01.xlsx" \
  --data '{"schedule_type": "door", "row_count": 45, "columns": ["MARK","SIZE","TYPE","FRAME","HARDWARE SET"]}'
```

## Schedule Reconciliation (Excel → DB Round-Trip)

When a PE edits an exported Excel schedule and wants changes applied back to the database:

### Reconciliation Workflow

```
Reconciliation Progress:
- [ ] Step R1: Read metadata from edited Excel
- [ ] Step R2: Compute changeset (diff vs DB)
- [ ] Step R3: POST changeset to reconcile endpoint
- [ ] Step R4: Report summary to user
```

### Step R1: Read Metadata from Edited Excel

Exported Excel files contain reconciliation anchors:
- Hidden `_agentcm_meta` sheet with `schedule_id`, `schedule_type`, `sheet_id`
- Hidden `_row_key` column A with entity identifiers (door numbers, room numbers, etc.)

If the Excel lacks `_agentcm_meta`, it was not exported by AgentCM — treat as a fresh import (re-run the extraction workflow above).

### Step R2: Compute Changeset

Run the diff engine to compare the edited Excel against current DB state:

```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/scripts/xlsx_to_changeset.py \
  --excel "edited_schedule.xlsx" \
  --query-command "$(cat .construction/database.yaml | grep query_command | cut -d'"' -f2)" \
  --output changeset.json
```

The script:
1. Reads `_agentcm_meta` → extracts `schedule_id`
2. Reads data sheet → extracts `_row_key` column + all data columns
3. Queries DB for current schedule rows/cells via psql
4. Computes diff: cell changes, new rows, deleted rows, new columns, hidden columns
5. Outputs a structured JSON changeset

### Step R3: POST Changeset to Reconcile Endpoint

```bash
# Read api_url and project_id from .construction/database.yaml
curl -X POST "{api_url}/projects/{project_id}/schedules/reconcile" \
  -H "Content-Type: application/json" \
  -d @changeset.json
```

The reconcile endpoint applies changes with:
- **Override protection**: All user edits set `isUserOverride=TRUE` — future re-extractions will not overwrite them
- **Audit trail**: Every cell edit, row add/delete, and column change is logged to `schedule_change_log`
- **Conflict detection**: If a re-extraction later disagrees with a user override, a conflict is created (not silently overwritten)

### Step R4: Report Summary

The endpoint returns an `ExcelReconcileResult`:
```json
{
  "rowsUpdated": 3,
  "rowsAdded": 1,
  "rowsSoftDeleted": 0,
  "cellsChanged": 7,
  "conflictsCreated": 0,
  "columnsAdded": 0,
  "columnsHidden": 0,
  "errors": []
}
```

Report the summary to the user. If `errors` is non-empty, surface those for review.

### Anchored Excel Export

When exporting schedules for PE review, always include reconciliation anchors:

```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/scripts/schedule_to_xlsx.py \
  --data schedule_data.json \
  --type door_schedule \
  --project "Project Name" \
  --sheet "A-0.01" \
  --schedule-id "{schedule_uuid}" \
  --sheet-id "{sheet_uuid}" \
  --output "Door_Schedule_A-0.01.xlsx"
```

The `--schedule-id` and `--sheet-id` flags embed metadata in the hidden `_agentcm_meta` sheet, enabling the round-trip reconciliation workflow.

## Schedule Type Reference

| Type | Common columns | Notes |
|---|---|---|
| Door | Mark, Width, Height, Type, Frame, Hardware Set, Fire Rating | Cross-ref hardware sets with spec 08 71 00 |
| Window | Mark, Width, Height, Type, Glazing, Frame Material | Check for energy code compliance |
| Room Finish | Room #, Name, Floor, Base, North/South/East/West Walls, Ceiling | Finish codes defined in legend |
| Panel | Circuit #, Description, Load (VA), Breaker Size, Phase | Verify total load vs panel capacity |
| Fixture (Plumbing) | Mark, Description, Manufacturer, Model, Connection | Cross-ref with spec Division 22 |
| Equipment (HVAC) | Tag, Description, CFM/BTU, Voltage, Weight | Cross-ref with spec Division 23 |

## File Safety
Never overwrite an existing schedule extraction. The export script uses `safe_output_path()` which appends `_v2`, `_v3`, etc. automatically.

---

## Allowed Scripts

**Allowed scripts — exhaustive list.** Only execute these scripts during this skill:
- `../../scripts/pdf/rasterize_page.py` — rasterize PDF pages for vision extraction
- `../../scripts/pdf/crop_region.py` — crop schedule region from full sheet image
- `scripts/schedule_to_xlsx.py` — Excel export with reconciliation anchors
- `scripts/xlsx_to_changeset.py` — diff edited Excel against DB for reconciliation
- `../../scripts/graph/write_finding.py` — graph entry (Step 6)
