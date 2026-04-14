---
name: tag-audit-and-takeoff
description: >
  Count-based quantity takeoff and tag completeness auditing for construction
  drawings. Vision + OCR reconciliation, sheet markup, Excel QTO output.
  Triggers: 'tag audit', 'quantity takeoff', 'QTO', 'count fixtures'.
disable-model-invocation: true
---

# Tag Audit & Quantity Takeoff

## Purpose

Count-based QTO for tagged construction elements — fixtures, devices,
doors, equipment, and any element identified by a tag/symbol on drawings.
Does NOT do area (sqft) or linear (lf) takeoffs — only discrete counts.

The QTO is a byproduct of the audit. The real value: the completeness
engine that finds what's tagged, what's missing, and produces a defensible
count with full provenance for every number.

Does NOT: do area/linear takeoffs, create outbound documents autonomously,
override user-approved groupings, or assume quantities without provenance.

---

## Step 0: Detect Operating Mode

Check for `.construction/` directory at the project root.

**AgentCM mode** (`.construction/` exists):
- Read `.construction/CLAUDE.md` for project context
- Read `.construction/database.yaml` for `query_command` and `project_id`
- Sheet images at `.construction/rasters/{sheet_number}.png`

**Verify raster images exist:** Check `.construction/rasters/` for PNG files.
If empty, tell the user: "Raster images not found. Open this project in
AgentCM to trigger the export, or run:
`curl -s -X POST '{api_url}/projects/{project_id}/graph/export' -H 'Content-Type: application/json' -d '{\"rootPath\": \"'$(pwd)'\"}'`"
You can also rasterize individual sheets on demand using the rasterize_page.py script.
- OCR data queryable via `extracted_items` table in PostgreSQL
- Write results back via API: `POST /api/projects/{id}/tag-detections/ingest`

**Flat File mode** (no `.construction/`):
- Discover sheet images from CLAUDE.md or user-provided paths
- Vision-only pipeline (Steps 2-3 skipped)
- Write marked-up PNGs and QTO JSON to project directory

## Step 1: User Scopes the Task

User provides: (1) tag type — e.g., "plumbing fixtures", "doors",
"light fixtures" (see `references/tag-types.md` for full list), and
(2) sheet scope — specific sheets, a discipline, or "all sheets".
Confirm scope before proceeding.

**Custom tag types:** If the user requests a tag type not in
`references/tag-types.md` (e.g., "keynote legends", "fire dampers",
"seismic bracing"), treat it as a custom type. Use it in the `tag_type`
field at ingest — the server auto-registers unknown types in the
`tag_types` table with default styling. The normalized name will be
`qto_{type}` (e.g., `qto_keynote_legend`). Custom types appear in the
Group Review gallery and support the full accept/reject/promote workflow.

**REQUIRED: Tag type resolution.** Before using any `tag_type` value,
you MUST resolve it against existing types:

1. Query `GET /api/projects/{id}/group-review/available-types` to see
   all active tag types for this project
2. Check if the user's requested type matches ANY existing type name
3. Apply alias resolution — these names are synonyms of existing types:
   - `detail_callout`, `section_callout`, `interior_elevation`,
     `callout_single_ref`, `single_ref_callout` → `simple_callout`
   - `multi_callout`, `callout_multi_ref`, `multi_ref_callout`
     → `multi_detail_callout`
4. If the resolved type exists in available-types, USE THAT NAME
5. Report to user: "Resolved type: '{resolved_name}' (matched from
   '{user_input}')" — get confirmation before proceeding
6. **If there is ANY ambiguity** about whether a requested tag type
   maps to an existing type, **ASK THE USER** before proceeding.
   Do not guess or invent a new type name.
7. Only auto-register a truly new type if no existing type or alias
   matches after checking both the available-types list and the alias
   map above

NEVER invent a new type name for concepts that already have canonical
types. When in doubt, ask.

## Step 1.5: Check Existing Coverage [REQUIRED GATE] (AgentCM mode only)

**HARD GATE — you MUST complete this step before proceeding to Step 2.**
Do not skip this step. If the API is unreachable, stop and tell the user.

Before scanning sheets, query what's already tagged per sheet:

```bash
curl -s "http://localhost:3001/api/projects/{project_id}/sheets/{sheet_id}/claimed-elements"
```

Response:
```json
{
  "claimed_element_ids": ["el_001", "el_002", ...],
  "suggestion_count": 12,
  "by_type": { "qto_room_tag": 8, "room_tag": 4 },
  "existing_tags": [
    { "id": "...", "proposedType": "qto_room_tag", "proposedText": "KITCHEN",
      "status": "accepted", "constituentIds": [...], "combinedBbox": {...}, "confidence": 0.92 }
  ]
}
```

Report to user: "Sheet A-1.4: 12 tags already detected (8 accepted, 4 pending)."

**Reconciliation rules:**
- **EXCLUDE** claimed element IDs from spatial queries (Steps 3-4) —
  add `AND id NOT IN ('{id1}', '{id2}', ...)` to SQL WHERE clauses
- **INCLUDE** `existing_tags` in the final QTO output — the QTO captures
  ALL items (existing + newly detected), not just new ones
- During vision (Step 2), note tags that match existing `proposedText`
  values — these are "confirmed" not "new"
- New detections that survive dedup → POST to ingest as usual
- The server also deduplicates at ingest: detections with element IDs
  overlapping existing suggestions are skipped (safety net)
- Final QTO JSON must merge: `existing_tags` (from this endpoint) +
  newly detected (from ingest response)

**The QTO is always a complete count.** Reconciliation avoids redundant
detection *work*, not redundant *output*.

**Before proceeding to Step 2, report coverage and get confirmation:**
"Existing coverage: {N} sheets have {M} accepted, {P} pending detections
for this tag type. {Q} sheets have zero coverage.
Proceed with vision scan on {Q} uncovered sheets?"
Wait for explicit user confirmation before continuing.

## Step 2: Vision Tag Identification

**CRITICAL — Vision is MANDATORY for this step.**
- You MUST read each sheet's raster image via vision to identify tags
- You may NOT substitute OCR text pattern matching (regex, ILIKE queries)
  for visual identification — OCR regex finds text, not tags
- OCR data is used ONLY in Steps 3-4 to spatially anchor
  vision-identified tags, not to replace the visual identification step
- If you cannot read a raster image for a sheet, FLAG it as
  "skipped — raster unavailable" and move to the next sheet
- Do NOT report OCR text matches as "detected tags"

Examine each sheet image. Identify all visible tags of the requested
type. Return tag texts and view type classification — no coordinates.

Vision must classify each tag's view: FLOOR PLAN, ENLARGED PLAN,
DETAIL, SECTION, or ELEVATION. This determines record type in Step 5.
Classification signals are in `references/tag-types.md`.

**In Flat File mode:** This is the primary (and only) identification step.
Provide rough locations ("upper-left quadrant") for markup purposes.

## Step 3: Text-Anchor Search (AgentCM mode only)

For each vision-identified tag, find its spatial anchor in the DB
using the **most distinctive word** in the tag text. "WALK-IN FREEZER"
→ search "FREEZER". "WOMEN'S RESTROOM" → search "WOMEN".

```bash
{query_command} -c "SELECT id, text, x_min, y_min, x_max, y_max FROM extracted_items WHERE sheet_id = '{sheet_id}' AND text ILIKE '%FREEZER%'"
```

Multiple hits expected — each is a potential tag location. Zero hits
→ try alternate words. Still zero → flag "vision-only, no OCR anchor".

## Step 4: Spatial Neighborhood Query (AgentCM mode only)

For each anchor, pull nearby extracted items. Padding values by tag type
in `references/spatial-params.md`. Target: 8-25 candidates per tag.

```bash
{query_command} -c "SELECT id, text, x_min, y_min, x_max, y_max FROM extracted_items WHERE sheet_id = '{sheet_id}' AND x_min BETWEEN {anchor_x - pad} AND {anchor_x + pad} AND y_min BETWEEN {anchor_y - pad} AND {anchor_y + pad}"
```

Adaptive: double padding if < 3 items returned, reduce 30% if > 40.

## Step 5: Grouping

Give Claude the vision tag text and the small candidate set (~15-20
items). Group constituent items following `references/grouping-rules.md`
— text reconstruction, spatial coherence, include/exclude criteria,
confidence scoring.

**Batching**: Process ALL tags per sheet in one call. 12 tags × ~200
tokens each = ~2400 tokens. Never load the full extracted items set.

**Flat File mode**: Skip grouping. Tags come from vision only. Mark
all detections as `confidence: "vision_only"` in output.

**Validation checkpoint (after first 3 sheets):**
After grouping tags on the first 3 sheets, STOP and present 5 sample
grouped detections to the user. Show for each:
- Vision-identified text
- OCR-reconstructed text (from constituents)
- Confidence score
- Number of constituent element IDs
- Approximate sheet location (combined bounding box)

Get explicit user confirmation: "Grouping quality acceptable? Proceed
with remaining {N} sheets?" Do not continue until confirmed.

## Step 6: Sheet Markup

**REQUIRED for all modes.** Mark up each sheet with visual highlights
so the user can see exactly what was identified.

**QTO markup must show ALL tagged items per sheet** — not just newly detected.
Pull existing items from the Step 1.5 claimed-elements response (`existing_tags`)
and include them in the markup alongside new detections. Use color to distinguish:
- `--color "green"` for accepted items (from previous detection/review)
- `--color "blue"` for newly detected items (this session)
- `--color "orange"` for pending review items

Run the markup script once per color group per sheet, layering onto the same
output image (use the previous output as `--base` for the next pass).

```bash
# Build items JSON with one entry per detected tag
# Then call the shared markup script:
${CLAUDE_SKILL_DIR}/../../bin/construction-python \
  ${CLAUDE_SKILL_DIR}/scripts/markup_tags.py \
  --base "{sheet_image_path}" \
  --items "{items_json_path}" \
  --output "{output_path}" \
  --color "blue" \
  --label-style "numbered"
```

Items JSON format (pixel coordinates):
```json
[
  {"x": 2500, "y": 1800, "shape": "circle", "radius": 20, "label": "WALK-IN FREEZER"},
  {"x": 3100, "y": 2200, "shape": "circle", "radius": 20, "label": "DRY STORAGE"}
]
```

Convert normalized 0-1 coordinates to pixels using sheet image dimensions.

**If PDF is available**, also create native PDF annotations:
```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python \
  ${CLAUDE_SKILL_DIR}/../../scripts/pdf/annotate_pdf.py \
  --pdf "{pdf_path}" --items "{items_json}" --output "{output_pdf}" \
  --author "Claude Code QTO"
```

## Step 7: Record Classification

Record type depends on view type. Full data model in
`references/quantity-model.md`.

**Floor plan tags → Element Instance.** One tag = one installed item.
**Detail/section/elevation tags → Element Type Definition.** Template.

## Step 8: Write Results

**Pre-ingest confirmation (REQUIRED before POSTing):**
Before making ANY ingest API calls, present this summary to the user:
- Total new detections to ingest: {N}
- Total existing from claimed-elements: {M}
- Resolved tag type: {type_name}
- 3-5 sample detections (tag_text, confidence, element_ids count)
- Any flagged items (low confidence, no OCR anchor, skipped sheets)

"Ready to ingest {N} new detections as '{type_name}'? (Y/N)"

Do NOT POST to the ingest endpoint until the user explicitly confirms.
Ingesting without confirmation is a blocking violation of this skill.
The server enforces a maximum of 100 detections per request — batch
your ingest calls per sheet.

**AgentCM mode:** POST detection results to the API:
```bash
curl -X POST "http://localhost:3001/api/projects/{project_id}/tag-detections/ingest" \
  -H "Content-Type: application/json" \
  -d '{"sheet_id": "{sheet_id}", "detections": [...]}'
```

Each detection: `{ tag_text, tag_type, element_ids, bounding_box, confidence, view_type, room_id }`.
`bounding_box` must be `{ x, y, width, height }` in normalized 0-1 coordinates.
Results appear as highlighted overlays in AgentCM's canvas UI.

Also write JSON to `.construction/agent_findings/qto_{tag_type}_{timestamp}.json`.

**CRITICAL — use the EXACT schema from `references/qto-output-format.md`.**
The Excel script is rigid and parses specific key names. Required keys:
- `line_items[]` (NOT `qto_lines`) — one entry per unique element/designation
- `totals{}` with `sheet_instances`, `derived_instances`, `deduplicated`, `building_quantity`
- Each line item has `instance_details[]` with `detection_id`, `sheet`, `room`, `status`, `confidence`
- `scope{}`, `completeness{}`, `issues[]`

**Include ALL items** — existing pipeline detections + newly detected this session.
The QTO is a complete count. Query the claimed-elements endpoint (Step 1.5) for
existing items and merge them into `line_items[].instance_details[]`.

**Flat File mode:** Write QTO JSON + marked-up PNGs to project directory.

**Excel export** (both modes): Write the QTO data JSON to a temp file,
then invoke the export script to produce a styled multi-sheet workbook:

```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python \
  ${CLAUDE_SKILL_DIR}/scripts/qto_to_xlsx.py \
  --data "{qto_json_path}" \
  --project "{project_name}" \
  --scope "{tag_type_display}" \
  --output "QTO_{tag_type}_{date}.xlsx"
```

The workbook has 4 sheets: QTO Summary (line items with counts),
Instance Detail (every detection with provenance), Type Definitions
(templates applied to rooms), and Completeness (coverage metrics).

---

## Reference Resolution (Type Defs → Derived Instances)

After type definitions are identified from details/sections/enlarged
plans, resolve where they apply. Full logic: `references/quantity-model.md`.

Three methods (in order of reliability):
1. **Callout reference** — detail bubble on floor plan references source
2. **Room type match** — room tags match the type def's parent view label
3. **Schedule cross-ref** — finish/room schedule references the detail

Deduplication: direct instances always take precedence over derived.

---

## Completeness Metrics

Compare detected counts against schedules (door, fixture, equipment)
when available. Report: "[tag type]: X detected, Y expected, Z%
coverage. Gaps on sheets: [list]." No schedule → report raw counts.

---

## Allowed Scripts

**Allowed scripts — exhaustive list.** Only execute these scripts during this skill:
- `scripts/markup_tags.py` — sheet markup with tag highlights
- `../../scripts/pdf/annotate_pdf.py` — native PDF annotations
- `scripts/qto_to_xlsx.py` — QTO Excel export (4-sheet workbook)
