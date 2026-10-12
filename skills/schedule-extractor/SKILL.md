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
- [ ] Step 6: Ingest to AgentCM (AgentCM mode)
- [ ] Step 7: Write a finding
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

#### Source B — AgentCM's tables (AgentCM mode)

In AgentCM mode (`.construction/project.yaml` exists; follow `${CLAUDE_PLUGIN_ROOT}/reference/agentcm-mode.md`), `.construction/INDEX.md`'s Schedules and legends table lists every table AgentCM found, each in its own `.construction/schedules/<sheet>-<n>.tsv`. The file's comment line gives the table's box on the sheet (x y w h, 0 to 1 from the top left) and, for a schedule already ingested, its `schedule_id` (`none` for a table read from the sheet's text alone). For embedded schedules on non-schedule sheets, that box is where to look: `sh .construction/crop.sh <sheet> <x> <y> <w> <h>`.

**Note**: A table read from the text is AgentCM's reading, and its box an estimate: treat both as leads, not definitive boundaries. Always verify with vision.

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
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/pdf/rasterize_page.py" "{pdf_path}" {page} --dpi 150 --output full_sheet.png
```

Use vision on the full sheet image: "Identify any tabular schedules on this drawing sheet. Report the approximate bounding box (top-left x,y and bottom-right x,y) as fractions of the image width and height between 0 and 1, the schedule type, and the column headers visible."

### Step 2: Isolate the Schedule Region

**For dedicated schedule sheets** (entire page is a schedule): Skip cropping — use the full page.

**For embedded schedules** (schedule is one element on a larger sheet):

Crop the identified region with padding. The box is the 0–1 fractions from
Step 1, so `--normalized` is required; without it the script reads the values
as pixels and returns an empty crop:
```bash
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/pdf/crop_region.py" full_sheet.png \
  --box {x1},{y1},{x2},{y2} --normalized \
  --padding 20 \
  --output schedule_crop.png
```

Re-rasterize at higher DPI (300) for the cropped region to improve text clarity.
`rasterize_page.py --crop` takes percentages, so multiply each fraction by 100
(`0.62,0.08,0.98,0.45` becomes `62,8,98,45`):
```bash
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/pdf/rasterize_page.py" "{pdf_path}" {page} \
  --dpi 300 \
  --crop {x1_pct},{y1_pct},{x2_pct},{y2_pct} \
  --output schedule_hires.png
```

### Step 3: Extract Structured Data

Use a **try → validate → fallback** approach:

#### Method A — pdfplumber table extraction (try first)

Extract the page's tables with the shared script (its JSON holds `text` and `tables`; add `--bbox x1,y1,x2,y2` in PDF points to limit it to the schedule region):
```bash
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/pdf/extract_text_region.py" "{pdf_path}" {page} --output tables.json
```
If multiple tables are found, select the largest one (most rows with the most columns — schedules are wide). The first row of the selected table contains headers; subsequent rows are data. If no tables are found or results look garbled, fall back to vision (Method B). Do not write pdfplumber code of your own.

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
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/pdf/rasterize_page.py" "{pdf_path}" {page} --dpi 150 --output full_sheet.png
```

2. **Use vision** on the full sheet image to read the schedule directly:

"This is a construction drawing sheet containing a schedule (tabular data). Extract ALL rows from the schedule as a JSON array of objects. The first row of the table contains column headers — use those as object keys. Each subsequent row is one entry. Preserve exact values including dimensions, abbreviations, and codes. If a cell is empty, use null."

3. For dense schedules with small text, **re-rasterize at 300 DPI** and crop to just the schedule region:
```bash
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/pdf/rasterize_page.py" "{pdf_path}" {page} --dpi 300 --output schedule_hires.png
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
- **Cross-reference with AgentCM's identifiers**: In AgentCM mode, check each room number and door mark against `.construction/tags.tsv` (`kind` room or door; the lines starting with the number and a tab). Not finding one there proves nothing (INDEX.md says when its room list is incomplete): report it as "not in AgentCM's index" and check the plan sheets' `.construction/sheets/<sheet>.tsv`.

### Step 5: Output to Excel

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_SKILL_DIR}/scripts/schedule_to_xlsx.py" \
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

### Step 6: Ingest to AgentCM (AgentCM mode)

After Excel output, send the extracted data to AgentCM's schedule ingest, which stores it and links its rows to rooms. Write the payload (below) to `.construction/skills/schedule-extractor/outbox/schedules-ingest-<sheet>-<YYYYMMDD-HHMMSS>.json` and send it as `${CLAUDE_PLUGIN_ROOT}/reference/agentcm-mode.md` says under Writing back; if AgentCM is closed, the payload waits there and the PE is told:

```bash
# api_url and project_id from .construction/database.yaml
curl -sS -X POST "{api_url}/projects/{project_id}/schedules/ingest" \
  -H "Content-Type: application/json" \
  -d @".construction/skills/schedule-extractor/outbox/schedules-ingest-<sheet>-<YYYYMMDD-HHMMSS>.json" \
  -w "\nHTTP %{http_code}\n"
```

**The sheet's id.** `sheetId` is the `id` of the entry in `.construction/index/sheet_index.yaml` whose `sheet_number` is the schedule's sheet. Never guess it from the number. If that file is missing, or its entries have no `id` (an older sheet-splitter wrote a `pages:` list with `filename` and `page_index`), say so and stop: do not ingest. The Excel workbook from Step 5 stands either way.

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

### Step 7: Write a Finding

In both modes, record the extraction in `.construction/skills/schedule-extractor/findings/`:

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/graph/write_finding.py" \
  --skill "schedule-extractor" --type "schedule_extracted" \
  --title "Door schedule extracted from A-0.01" \
  --source-sheet "A-0.01" \
  --output-file "Door_Schedule_A-0.01.xlsx" \
  --data '{"schedule_type": "door", "row_count": 45, "columns": ["MARK","SIZE","TYPE","FRAME","HARDWARE SET"]}'
```

## Schedule Reconciliation (Excel → DB Round-Trip)

When a PE edits an exported Excel schedule and wants changes applied back to AgentCM:

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

Run the diff engine to compare the edited Excel against the rows AgentCM holds:

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_SKILL_DIR}/scripts/xlsx_to_changeset.py" \
  --excel "edited_schedule.xlsx" \
  --output ".construction/skills/schedule-extractor/outbox/schedules-reconcile-<sheet>-<YYYYMMDD-HHMMSS>.json"
```

The script:
1. Reads `_agentcm_meta` → extracts `schedule_id`. A table never ingested (`schedule_id=none`) has nothing to reconcile and is refused: ingest it first (Step 6)
2. Reads data sheet → extracts `_row_key` column + all data columns
3. Reads the schedule's stored rows from AgentCM, `GET {api_url}/projects/{project_id}/schedules/{schedule_id}/rows`, with `project_id` and `api_url` from `.construction/database.yaml` (nothing else in it)
4. Computes diff: cell changes, new rows, deleted rows, new columns, hidden columns
5. Outputs a structured JSON changeset, with `sourceFile` the edited Excel's name

It needs AgentCM running. If AgentCM does not answer, the script exits 3 and computes nothing: tell the PE to start AgentCM and rerun this step (the edited Excel is all it needs).

### Step R3: POST Changeset to Reconcile Endpoint

Send the changeset R2 wrote to the outbox, as `${CLAUDE_PLUGIN_ROOT}/reference/agentcm-mode.md` says under Writing back:

```bash
# api_url and project_id from .construction/database.yaml
curl -sS -X POST "{api_url}/projects/{project_id}/schedules/reconcile" \
  -H "Content-Type: application/json" \
  -d @".construction/skills/schedule-extractor/outbox/schedules-reconcile-<sheet>-<YYYYMMDD-HHMMSS>.json" \
  -w "\nHTTP %{http_code}\n"
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
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_SKILL_DIR}/scripts/schedule_to_xlsx.py" \
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
- `${CLAUDE_PLUGIN_ROOT}/scripts/pdf/extract_text_region.py` — Method A table extraction (pdfplumber)
- `${CLAUDE_PLUGIN_ROOT}/scripts/pdf/rasterize_page.py` — rasterize PDF pages for vision extraction
- `${CLAUDE_PLUGIN_ROOT}/scripts/pdf/crop_region.py` — crop schedule region from full sheet image
- `scripts/schedule_to_xlsx.py` — Excel export with reconciliation anchors
- `scripts/xlsx_to_changeset.py` — diff the edited Excel against AgentCM's stored rows (its rows endpoint) for reconciliation
- `${CLAUDE_PLUGIN_ROOT}/scripts/graph/write_finding.py` — record the extraction as a finding (Step 7)
- `${CLAUDE_PLUGIN_ROOT}/scripts/corrections_append.py` — AgentCM mode: record a correction of AgentCM's data (`reference/agentcm-mode.md`)
