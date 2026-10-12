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

Check for AgentCM: `.construction/project.yaml` at the project root.

**AgentCM mode** (`.construction/project.yaml` exists):
- Follow `${CLAUDE_PLUGIN_ROOT}/reference/agentcm-mode.md`: which source wins, what a missing file or an empty search means, sheet ids, and how to record a correction of AgentCM's data (a missed tag goes through the ingest in Step 8)
- Read `.construction/CLAUDE.md` for project context and where things are,
  except its database section: never run `query.sh` or `query.ps1`, whatever
  the guide offers
- Read `.construction/database.yaml` for `project_id` and `api_url`, nothing else in it
- Every `{sheet_id}` below (the endpoints) is
  the `id` of the entry in `.construction/index/sheet_index.yaml` whose
  `sheet_number` is that sheet. Never guess it from the number. If that file is
  missing, or its entries have no `id` (an older sheet-splitter wrote a `pages:`
  list with `filename` and `page_index`), say so and stop.
- Look at a sheet through AgentCM's crop script, a box at a time:
  `sh .construction/crop.sh <sheet> <x> <y> <w> <h>` (or
  `powershell -File .construction/crop.ps1 <sheet> <x> <y> <w> <h>`) renders
  that box of the sheet's PDF page as a PNG and prints its path. `<sheet>` is
  the sheet's number as `.construction/INDEX.md` names it; the box is 0 to 1
  from the top left of the sheet. Never rasterize whole sheets, and never ask
  for `rasters/` or `graph/export`: they are not part of AgentCM's contract.
- A sheet's text, each line with its box: `.construction/sheets/<sheet>.tsv` (Steps 3-4)
- Write results back via API: `POST {api_url}/projects/{project_id}/tag-detections/ingest`, sent from the outbox (Step 8)

**Flat File mode** (no `.construction/project.yaml`):
- Discover sheet images from CLAUDE.md or user-provided paths; rasterize sheet
  PDFs with `"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/pdf/rasterize_page.py" "<pdf>" <page> --dpi 200 --output "<png>"`
- Vision-only pipeline (Steps 2-3 skipped)
- Write marked-up PNGs and the Excel workbook to the project directory; the QTO
  JSON goes to `.construction/skills/tag-audit-and-takeoff/qto/` (Step 8)

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

1. Query `GET {api_url}/projects/{project_id}/group-review/available-types` to see
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
Do not skip this step.

Before scanning sheets, read what's already tagged per sheet:

```bash
curl -sS "{api_url}/projects/{project_id}/sheets/{sheet_id}/claimed-elements" -w "\nHTTP %{http_code}\n"
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

Keep the `existing_tags` of the resolved tag type (`proposedType`), each with
its `status` (accepted or pending) and its box (`combinedBbox`).

**If curl cannot connect (exit 7), AgentCM is closed.** Read the existing tags
from its files instead and go on:
- accepted: the lines of `.construction/sheets/<sheet>.groups.tsv` whose
  `type` is the resolved type (box `x y w h`, `text`)
- pending: the lines of `.construction/sheets/<sheet>.tsv` with that type in
  `tag` and `pending` in `how`, grouped into tags as Step 5 groups

Tell the PE the existing tags came from AgentCM's files, and that this run's
new tags will wait in the outbox (Step 8). In both cases, the payloads in
`.construction/skills/tag-audit-and-takeoff/outbox/` (an earlier run's, saved
while AgentCM was closed) hold existing tags too: not yet in AgentCM.

Report to user: "Sheet A-1.4: 12 tags already detected (8 accepted, 4 pending)."

**Reconciliation rules (the count, `references/qto-output-format.md`):**
- **Confirmed** is the accepted existing tags, and only those.
- **To confirm** is every tag not yet accepted: the pending existing tags,
  the tags waiting in the outbox, and the tags this run finds that match none
  of them.
- **One tag, once.** A tag found in this run is an existing tag when it is on
  the same sheet, its text matches (upper case, spaces collapsed) and one
  box's center falls inside the other box. Keep the existing tag, with its
  `detection_id`, and drop this run's sighting of it.
- **Send only the new ones:** the tags found in this run that match no
  existing tag, and nothing else, go to ingest (Step 8). Nothing new, no POST.
- **EXCLUDE** from the neighborhood search (Steps 3-4) the lines an existing
  tag already holds: a line whose box's center falls inside an existing tag's
  box
- The server also deduplicates at ingest: detections with element IDs
  overlapping existing suggestions are skipped (safety net)

**Run it twice, get the same numbers.** A second run finds the first run's new
tags pending in AgentCM (or waiting in the outbox), matches its own sightings
to them, sends nothing again, and reports the same confirmed, to confirm and
possible total. Reconciliation avoids redundant detection *work*, not
redundant *output*.

**Before proceeding to Step 2, report coverage and get confirmation:**
"Existing coverage: {N} sheets have {M} accepted, {P} pending detections
for this tag type. {Q} sheets have zero coverage.
Proceed with the vision scan of the {S} sheets in scope?"
Every sheet in scope is looked at, covered or not: existing tags are matched,
never skipped (one tag, once), and coverage only narrows the neighborhood
search within a sheet (the EXCLUDE rule above), never which sheets are scanned.
Wait for explicit user confirmation before continuing.

## Step 2: Vision Tag Identification

**CRITICAL — Vision is MANDATORY for this step.**
- You MUST read each sheet's image via vision to identify tags
- You may NOT substitute text pattern matching (regex, searches of the
  sheet files) for visual identification — a text search finds text, not tags
- The sheet's text is used ONLY in Steps 3-4 to spatially anchor
  vision-identified tags, not to replace the visual identification step
- If you cannot get an image of a sheet, FLAG it as
  "skipped — image unavailable" and move to the next sheet
- Do NOT report OCR text matches as "detected tags"

Examine each sheet image. Identify all visible tags of the requested
type. Return tag texts and view type classification — no coordinates.

**In AgentCM mode** a sheet is read in boxes through `crop.sh` (Step 0): one
box per view, from the `## view` headings in `.construction/sheets/<sheet>.txt`
(each heading gives the view's area as x, y, w, h), or quadrants
(`0 0 0.5 0.5`, `0.5 0 0.5 0.5`, `0 0.5 0.5 0.5`, `0.5 0.5 0.5 0.5`) for a
sheet without views. If `crop.sh` refuses a box as too large to read (exit 2),
split it in four and crop those. Keep each PNG with its box: a point at pixel
(px, py) in a crop of box (x, y, w, h) sized W × H pixels is at sheet position
(x + px / W × w, y + py / H × h).

Vision must classify each tag's view: FLOOR PLAN, ENLARGED PLAN,
DETAIL, SECTION, or ELEVATION. This determines record type in Step 5.
Classification signals are in `references/tag-types.md`.

**In Flat File mode:** This is the primary (and only) identification step.
Provide rough locations ("upper-left quadrant") for markup purposes.

## Step 3: Text-Anchor Search (AgentCM mode only)

For each vision-identified tag, find its spatial anchor in the sheet's
`.construction/sheets/<sheet>.tsv` (one line of text per row: `x y w h
source tag how label para view zone text`, the text last) using the **most
distinctive word** in the tag text. "WALK-IN FREEZER" → search "FREEZER".
"WOMEN'S RESTROOM" → search "WOMEN".

```bash
grep -i "FREEZER" ".construction/sheets/<sheet>.tsv"
```

Multiple hits expected — each is a potential tag location. Zero hits
→ try alternate words. Still zero → flag "vision-only, no OCR anchor".

## Step 4: Spatial Neighborhood Query (AgentCM mode only)

For each anchor, pull the sheet's nearby lines: those whose `x` and `y` fall
within the padding of the anchor's. Padding values by tag type in
`references/spatial-params.md`. Target: 8-25 candidates per tag.

```bash
awk -F'\t' 'NR > 1 && $1 >= {anchor_x - pad} && $1 <= {anchor_x + pad} && $2 >= {anchor_y - pad} && $2 <= {anchor_y + pad}' ".construction/sheets/<sheet>.tsv"
```

Adaptive: double padding if < 3 items returned, reduce 30% if > 40.

## Step 5: Grouping

Give Claude the vision tag text and the small candidate set (~15-20
items). Group constituent items following `references/grouping-rules.md`
— text reconstruction, spatial coherence, include/exclude criteria,
confidence scoring.

**Batching**: Process ALL tags per sheet in one call. 12 tags × ~200
tokens each = ~2400 tokens. Never load the sheet's whole `.tsv`.

**Flat File mode**: Skip grouping. Tags come from vision only. Mark
all detections as `confidence: "vision_only"` in output.

**Validation checkpoint (after first 3 sheets):**
After grouping tags on the first 3 sheets, STOP and present 5 sample
grouped detections to the user. Show for each:
- Vision-identified text
- OCR-reconstructed text (from constituents)
- Confidence score
- Number of constituent lines
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
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" \
  "${CLAUDE_SKILL_DIR}/scripts/markup_tags.py" \
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

**In AgentCM mode** the base images are the `crop.sh` PNGs from Step 2, one
marked-up image per box: give `--base` the crop's path and the items' pixel
positions within that crop (sheet position minus the box's x and y, divided by
its w and h, times the image's width and height). The crops live in AgentCM's
`.construction/crops/`; write the marked-up PNGs to the project directory.

**If PDF is available**, also create native PDF annotations:
```bash
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" \
  "${CLAUDE_PLUGIN_ROOT}/scripts/pdf/annotate_pdf.py" \
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
- Total new detections to ingest: {N} (found in this run, matching no existing tag)
- Total existing: {M} accepted, {P} pending, {W} waiting in the outbox
- Resolved tag type: {type_name}
- 3-5 sample detections (tag_text, confidence, element_ids count)
- Any flagged items (low confidence, no OCR anchor, skipped sheets)

"Ready to ingest {N} new detections as '{type_name}'? (Y/N)"

Do NOT POST to the ingest endpoint until the user explicitly confirms.
Ingesting without confirmation is a blocking violation of this skill.
The server enforces a maximum of 100 detections per request — batch
your ingest calls per sheet.

**AgentCM mode:** write each sheet's payload, `{"sheet_id": "{sheet_id}", "detections": [...]}`,
to `.construction/skills/tag-audit-and-takeoff/outbox/tag-detections-ingest-<sheet>-<YYYYMMDD-HHMMSS>.json`
and send it as `${CLAUDE_PLUGIN_ROOT}/reference/agentcm-mode.md` says under
Writing back; if AgentCM is closed, the payload waits there and the PE is told:
```bash
curl -sS -X POST "{api_url}/projects/{project_id}/tag-detections/ingest" \
  -H "Content-Type: application/json" \
  -d @".construction/skills/tag-audit-and-takeoff/outbox/tag-detections-ingest-<sheet>-<YYYYMMDD-HHMMSS>.json" \
  -w "\nHTTP %{http_code}\n"
```

Each detection: `{ tag_text, tag_type, element_ids, bounding_box, confidence, view_type, room_id }`.
`bounding_box` must be `{ x, y, width, height }` in normalized 0-1 coordinates.
Results appear as highlighted overlays in AgentCM's canvas UI.

In both modes, once the QTO JSON is saved (below), record a finding in `.construction/skills/tag-audit-and-takeoff/findings/`:

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/graph/write_finding.py" \
  --skill "tag-audit-and-takeoff" --type "qto_{tag_type}" \
  --title "QTO: {tag_type_display} — {confirmed} confirmed, {possible} possible across {N} sheets" \
  --output-file "{qto_json_path}" \
  --data '{"tag_type": "...", "confirmed": ..., "to_confirm": ..., "possible_total": ..., "sheets": [...], "ingested": ...}'
```

**CRITICAL — use the EXACT schema from `references/qto-output-format.md`.**
The Excel script is rigid and parses specific key names. Required keys:
- `line_items[]` (NOT `qto_lines`) — one entry per unique element/designation
- Each line item has `instance_details[]` with `detection_id`, `sheet`, `tag_text`, `room`, `bounding_box`, `status` (`accepted` or `to_confirm`), `source`, `confidence`
- `scope{}` with `mode` (`agentcm` or `flat_file`), `completeness{}`, `issues[]`

**What the count holds** (Step 1.5): every tag once. `accepted` instances are
the confirmed count; every other tag is `to_confirm`, with its `source`
(`pending_in_agentcm`, `waiting_in_outbox`, or `found_this_run` with `ingest`
`sent` or `outbox`); derived instances are to confirm too. In flat-file mode
nothing is accepted: every tag is `to_confirm`. The export computes the three
numbers per item, prints them, and refuses a file that lists the same tag
twice. Report the export's lines, never your own tally: per item, confirmed,
to confirm and the possible total, and the caveat in its words.

**Both modes:** Save the QTO JSON (working data) to
`.construction/skills/tag-audit-and-takeoff/qto/{tag_type}_{timestamp}.json` and the
marked-up PNGs (deliverables) to the project directory.

**Excel export** (both modes): Pass that QTO JSON as `{qto_json_path}`
and invoke the export script to produce a styled multi-sheet workbook:

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" \
  "${CLAUDE_SKILL_DIR}/scripts/qto_to_xlsx.py" \
  --data "{qto_json_path}" \
  --project "{project_name}" \
  --scope "{tag_type_display}" \
  --output "QTO_{tag_type}_{date}.xlsx"
```

The workbook has 5 sheets: QTO Summary (confirmed, to confirm and possible
total per line item, with the caveat), Instance Detail (every detection with
provenance), Type Definitions (templates applied to rooms), Completeness
(coverage metrics), and To Confirm in AgentCM (every tag not yet accepted).

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
- `${CLAUDE_PLUGIN_ROOT}/scripts/pdf/rasterize_page.py` — rasterize a sheet PDF page to PNG (flat file mode)
- AgentCM's `.construction/crop.sh` / `crop.ps1` (a box of a sheet as a PNG), in AgentCM mode
- `scripts/markup_tags.py` — sheet markup with tag highlights
- `${CLAUDE_PLUGIN_ROOT}/scripts/pdf/annotate_pdf.py` — native PDF annotations
- `scripts/qto_to_xlsx.py` — QTO Excel export (5-sheet workbook; computes and prints confirmed, to confirm and possible total; refuses a tag listed twice)
- `${CLAUDE_PLUGIN_ROOT}/scripts/issue_manager.py` — log schedule/drawing count mismatches to the Issue Registry (command and severity mapping in construction-guide)
- `${CLAUDE_PLUGIN_ROOT}/scripts/graph/write_finding.py` — record the QTO as a finding (Step 8)
- `${CLAUDE_PLUGIN_ROOT}/scripts/corrections_append.py` — AgentCM mode: record a correction of AgentCM's data other than a missed tag (`reference/agentcm-mode.md`)
