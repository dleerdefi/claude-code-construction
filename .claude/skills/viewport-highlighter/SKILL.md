---
name: viewport-highlighter
description: >
  Identify and highlight viewports on construction drawing sheets using
  vision. Detects view boundaries, titles, scales, and view types. Creates
  viewport overlays via AgentCM API. Triggers: 'highlight viewports',
  'find views'.
allowed-tools:
  - Bash(${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/../../scripts/pdf/rasterize_page.py *)
  - Bash(${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/../../scripts/vision/markup_drawing.py *)
---

# Viewport Highlighter

## Purpose

Automate viewport segmentation of construction drawing sheets. Each sheet
typically contains 1-12+ distinct views (floor plans, sections, elevations,
details, schedules). This skill identifies all views, determines their
boundaries, extracts metadata (title, detail number, scale, type), and
creates viewport highlights — producing the same result as a user manually
drawing and labeling each viewport in the UI.

Does NOT: modify existing viewports, delete viewports, or change element
data. Only creates new viewport highlights and populates their metadata.

---

## Step 0: Detect Operating Mode

Check for `.construction/` directory at the project root.

**AgentCM mode** (`.construction/` exists):
- Read `.construction/CLAUDE.md` for project context
- Read `.construction/database.yaml` for `query_command`, `project_id`, `api_url`
- Read `.construction/index/sheet_index.yaml` for sheet inventory
- Sheet images at `.construction/rasters/{sheet_number}.png`
- OCR data queryable via `extracted_items` table in PostgreSQL
- Write viewports via REST API

**Flat File mode** (no `.construction/`):
- Discover sheet images from CLAUDE.md or user-provided paths
- Vision-only pipeline (Steps 3-4 simplified)
- Write viewport definitions as JSON + marked-up PNGs to project directory
- All viewports marked as `confidence: "vision_only"` in output

## Step 1: User Scopes the Task

User provides sheet scope:
- Specific sheets: "A2.01, A2.02, A5.01"
- By discipline: "all architectural sheets"
- All sheets: "every sheet in the set"

Optional: user can specify which view types to look for (e.g., "only floor
plans and sections"). Default: identify ALL views on each sheet.

**Before proceeding:** Confirm the sheet list and any filters with the user.
Show the count of sheets to process.

## Step 2: Vision — Identify View Boundaries

For each sheet in scope, rasterize to PNG (if not already available) and
examine with vision.

```bash
# Rasterize if needed (AgentCM mode has pre-rendered PNGs)
${CLAUDE_SKILL_DIR}/../../bin/construction-python \
  ${CLAUDE_SKILL_DIR}/../../scripts/pdf/rasterize_page.py \
  "{pdf_path}" {page_index} --dpi 200 --output /tmp/{sheet_number}.png
```

**Vision task:** Examine the full sheet image. Identify every distinct view
(drawing area) on the sheet. For each view, extract:

| Field | What to look for | Example |
|-------|-----------------|---------|
| **Title** | View title bar text (usually centered below the view) | "FIRST FLOOR PLAN" |
| **Detail Number** | Number in the detail bubble or title bar | "1", "A2.01", "3/A5" |
| **Scale** | Scale annotation near the title bar | `1/8" = 1'-0"`, `1/4" = 1'-0"`, "NTS" |
| **View Type** | Classification of the drawing content | plan, section, elevation, detail, schedule |
| **Bounding Region** | Approximate rectangle enclosing the entire view (normalized 0-1) | `{x: 0.02, y: 0.05, w: 0.48, h: 0.65}` |

### View boundary detection signals

Use these visual cues to determine where one view ends and another begins:

1. **Heavy border lines** — thick lines separating drawing areas
2. **Title bars** — horizontal bars with view name, scale, detail number
3. **Detail bubbles** — circles or hexagons with detail/sheet reference
4. **Whitespace gaps** — clear separations between drawing content
5. **Grid systems** — column/row grids define the extents of a plan view
6. **Section cut lines** — long dash-dot lines with directional arrows
7. **Match lines** — indicate where a plan continues on another sheet

### View type classification

| View Type | `extractionScope` value | Signals |
|-----------|------------------------|---------|
| Floor plan | `plan` | Grid lines, room names/numbers, dimension strings, north arrow |
| Enlarged plan | `plan` | "ENLARGED" in title, larger scale than base plan, room detail |
| Section | `section` | Section cut reference (e.g., "SECTION A-A"), vertical layers, material hatching |
| Elevation | `elevation` | "ELEVATION" in title, facade view, material callouts, floor lines |
| Detail | `detail` | Detail bubble reference, large scale (3"=1'-0"), construction assembly closeup |
| Schedule | `schedule` | Tabular grid, column headers, row data (door schedule, finish schedule) |
| Diagram | `other` | Riser diagrams, single-line diagrams, flow diagrams |

### Bounding region estimation from vision

When estimating the bounding region as normalized 0-1 coordinates:

- **x** = left edge of view content / sheet width (0.0 = left edge)
- **y** = top edge of view content / sheet height (0.0 = top edge)
- **width** = view content width / sheet width
- **height** = view content height / sheet height (include title bar)

**Include** the title bar and any associated notes/legends within the view.
**Exclude** the sheet title block (typically bottom-right corner).
**Margins:** Add ~1% padding on each side to avoid clipping content.

### Multi-view sheet layout patterns

Common construction sheet layouts to expect:

- **Single view:** One large plan fills most of the sheet
- **2-up vertical:** Two views stacked (e.g., floor plan top, reflected ceiling bottom)
- **2-up horizontal:** Two views side by side (e.g., two elevations)
- **Grid layout:** 4-6 details arranged in a 2x3 or 3x2 grid
- **Mixed:** Large plan on left, 2-3 sections/details stacked on right
- **Schedule + details:** Schedule table in upper portion, details below

## Step 3: OCR Anchor Verification (AgentCM mode only)

For each vision-identified view, verify and refine metadata using OCR data.

### Title verification

Search for the view title text in `extracted_items`:

```bash
{query_command} -c "SELECT id, text, x_min, y_min, x_max, y_max
  FROM extracted_items
  WHERE sheet_id = '{sheet_id}'
    AND text ILIKE '%{distinctive_title_word}%'
  ORDER BY y_max DESC"
```

The title bar is typically near the **bottom** of the view content area.
Use the title's y-coordinate to refine the view's bottom boundary.

### Scale verification

Search for scale text near the title:

```bash
{query_command} -c "SELECT id, text, x_min, y_min, x_max, y_max
  FROM extracted_items
  WHERE sheet_id = '{sheet_id}'
    AND text ILIKE '%SCALE%'
    AND y_min BETWEEN {title_y - 0.02} AND {title_y + 0.02}
    AND x_min BETWEEN {title_x - 0.15} AND {title_x + 0.15}"
```

Common scale text patterns:
- `SCALE: 1/8" = 1'-0"`
- `1/4" = 1'-0"`
- `SCALE: NTS` (not to scale)
- `3" = 1'-0"`

### Detail number verification

Search for detail number in title bar area or detail bubbles:

```bash
{query_command} -c "SELECT id, text, x_min, y_min, x_max, y_max
  FROM extracted_items
  WHERE sheet_id = '{sheet_id}'
    AND y_min BETWEEN {title_y - 0.02} AND {title_y + 0.02}
    AND x_min BETWEEN {title_x - 0.10} AND {title_x + 0.10}
    AND text ~ '^[0-9A-Z]'"
```

Detail number formats: `1`, `2`, `A`, `A2.01`, `3/A5`, `1/A5.01`.

## Step 4: Bounding Region Refinement

Refine vision-estimated boundaries using OCR element positions.

### AgentCM mode refinement

Query all extracted items within and near the estimated viewport area:

```bash
{query_command} -c "SELECT x_min, y_min, x_max, y_max
  FROM extracted_items
  WHERE sheet_id = '{sheet_id}'
    AND (x_min + x_max) / 2 BETWEEN {est_x - 0.02} AND {est_x + est_w + 0.02}
    AND (y_min + y_max) / 2 BETWEEN {est_y - 0.02} AND {est_y + est_h + 0.02}"
```

Use the extremes of contained items + 1% padding to set the final bounds.

### Overlap prevention

After refining all viewports on a sheet, check for overlaps:
- If two viewports overlap, shrink the boundary of the one with fewer
  contained elements at the overlapping edge
- Adjacent viewports should have a gap of 0.5-2% of sheet dimension

### Validation checklist

Before creating each viewport, verify:
- [ ] `x >= 0.0` and `x + width <= 1.0`
- [ ] `y >= 0.0` and `y + height <= 1.0`
- [ ] `width > 0.02` (at least 2% of sheet width)
- [ ] `height > 0.02` (at least 2% of sheet height)
- [ ] Title is non-empty
- [ ] View type is one of: plan, section, elevation, detail, schedule, other
- [ ] No significant overlap with other viewports on same sheet

## Step 5: Submit Viewports for Review

### AgentCM mode — Suggestion ingest

Submit all viewports for a sheet as **pending suggestions** via the
viewport suggestion ingest endpoint. The user reviews and approves them
in the Group Review Gallery before they become live viewports.

```bash
curl -s -X POST "{api_url}/projects/{project_id}/viewport-suggestions/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "sheet_id": "{sheet_id}",
    "viewports": [
      {
        "title": "FIRST FLOOR PLAN",
        "detail_number": "1",
        "scale_text": "1/8\" = 1'"'"'-0\"",
        "extraction_scope": "plan",
        "bounding_region": {"x": 0.02, "y": 0.05, "width": 0.48, "height": 0.65},
        "confidence": 0.85,
        "element_ids": []
      },
      {
        "title": "BUILDING SECTION A-A",
        "detail_number": "A",
        "scale_text": "1/4\" = 1'"'"'-0\"",
        "extraction_scope": "section",
        "bounding_region": {"x": 0.52, "y": 0.05, "width": 0.46, "height": 0.45},
        "confidence": 0.80,
        "element_ids": []
      }
    ]
  }'
```

**Response:** Returns `suggestion_ids` for the created pending cards.

**Processing order:** Submit all viewports for one sheet in a single
POST. The system creates `group_suggestions` rows with `status: pending`
and `proposedType: viewport_highlight`. Crop images are generated when
the user opens the Group Review Gallery.

**Confidence scoring:**
- 0.90+ = title, scale, and detail number all OCR-verified
- 0.70–0.89 = vision-identified with partial OCR verification
- 0.50–0.69 = vision-only, no OCR anchors found

### Review flow

Viewport suggestions appear in the **Group Review Gallery** as cards
with cropped raster previews. The user can:
- Edit title, detail number, scale text, and view type
- Adjust bounding region (future: via canvas interaction)
- Accept → promotes to a live viewport in `graph_views` with containment
  rebuild and crop generation
- Reject → suggestion archived, no viewport created

### Title formatting conventions

When setting viewport titles, follow these conventions:
- Use the exact title text from the drawing (preserve case)
- If the title includes the sheet number reference (e.g., "1/A5.01"),
  put only the detail number portion in `detail_number` and the full
  title in `title`
- Common abbreviations to preserve: "FLR", "CLG", "ELEV", "TYP"

### Flat File mode — JSON output

Write viewport definitions to a JSON file:

```bash
# Output path (never overwrite existing files)
output_path=$(safe_output_path "viewport_findings_{sheet_number}")
```

```json
{
  "sheet_number": "A2.01",
  "sheet_title": "FIRST FLOOR PLAN",
  "generated_at": "2026-04-06T18:30:00Z",
  "generated_by": "viewport-highlighter skill",
  "viewports": [
    {
      "title": "FIRST FLOOR PLAN",
      "detail_number": "1",
      "scale_text": "1/8\" = 1'-0\"",
      "extraction_scope": "plan",
      "bounding_region": {"x": 0.02, "y": 0.05, "width": 0.48, "height": 0.65},
      "confidence": "vision_only",
      "element_count_estimate": null
    }
  ]
}
```

## Step 6: Verification & Markup

### Sheet markup (REQUIRED for all modes)

Mark up each processed sheet with viewport boundary rectangles to show
exactly what was identified.

```bash
# Build items JSON with rectangles for each viewport
# Convert normalized 0-1 coordinates to pixel coordinates using image dims

${CLAUDE_SKILL_DIR}/../../bin/construction-python \
  ${CLAUDE_SKILL_DIR}/../../scripts/vision/markup_drawing.py \
  --base "{sheet_image_path}" \
  --items "{items_json_path}" \
  --output "{output_path}" \
  --color "amber" \
  --label-style "titled"
```

Items JSON format (pixel coordinates):
```json
[
  {
    "x": 100, "y": 200,
    "width": 4000, "height": 3200,
    "shape": "rect",
    "label": "1 - FIRST FLOOR PLAN (plan)"
  },
  {
    "x": 4200, "y": 200,
    "width": 3800, "height": 1500,
    "shape": "rect",
    "label": "A - BUILDING SECTION (section)"
  }
]
```

Use `safe_output_path()` pattern — never overwrite existing markup files.

### Verification report

After processing all sheets, produce a summary:

```
VIEWPORT HIGHLIGHTING SUMMARY
==============================
Sheets processed: 12
Total viewports created: 47

Sheet      | Views | Types
-----------|-------|------------------
A2.01      |     3 | plan, section, section
A2.02      |     2 | plan, plan
A5.01      |     8 | detail (x8)
A5.02      |     6 | detail (x4), section (x2)
...

Element containment:
  A2.01 / FIRST FLOOR PLAN:     342 elements
  A2.01 / BUILDING SECTION A:    87 elements
  ...
```

### Vision verification (recommended)

After creating all viewports on a sheet, re-examine the marked-up image
to verify:
- All views on the sheet are captured (no missing viewports)
- Bounding regions accurately encompass view content
- No significant overlap between viewports
- Title, detail number, and scale text are correct

If issues are found, PATCH the viewport to correct:
```bash
curl -s -X PATCH "{api_url}/projects/{project_id}/viewports/{viewport_id}" \
  -H "Content-Type: application/json" \
  -d '{"title": "CORRECTED TITLE", "boundingRegion": {...}}'
```

---

## Common Pitfalls

1. **Title block is not a viewport.** Every sheet has a title block
   (bottom-right, ~15% of sheet). Do NOT create a viewport for it.

2. **Revision blocks are not viewports.** Revision history areas
   (right edge) should be excluded.

3. **Key plans are not primary viewports.** Small orientation diagrams
   showing which area of the building is depicted — skip these unless
   the user specifically requests them.

4. **Matchline continuation.** When a floor plan spans two sheets
   (A2.01 and A2.02 split at a matchline), each sheet gets its own
   viewport — they are separate views even though they show one plan.

5. **Schedule views.** Tabular schedules (door schedule, finish schedule)
   ARE viewports. Set `extractionScope: "schedule"`.

6. **North arrows and legends.** Include these within the parent view's
   bounding region, not as separate viewports.

7. **Overlapping views.** Some sheets show plans with section cuts and
   enlarged areas overlaid. The base plan is the viewport — don't create
   separate viewports for the section cut lines themselves.

8. **Scale = "AS NOTED" or "NTS".** Some sheets have multiple scales
   or no scale. Set `scaleText` to the literal text found.

---

## API Reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/projects/{id}/viewport-suggestions/ingest` | **Primary** — submit viewport suggestions for review |
| GET | `/api/projects/{id}/sheets/{sheetId}/viewports` | List existing (promoted) viewports |
| POST | `/api/projects/{id}/sheets/{sheetId}/viewports` | Direct create (manual/bypass review) |
| PATCH | `/api/projects/{id}/viewports/{viewportId}` | Update metadata (title, bounds, scale, scope) |
| GET | `/api/projects/{id}/viewports/{viewportId}/elements` | Get contained element IDs + count |
| GET | `/api/projects/{id}/viewports/{viewportId}/crop` | Fetch auto-generated raster crop PNG |
| DELETE | `/api/projects/{id}/viewports/{viewportId}` | Remove viewport (use only if user requests) |

### ViewportSuggestionIngestBody (primary endpoint)

```json
{
  "sheet_id": "uuid",
  "viewports": [
    {
      "title": "string (required)",
      "detail_number": "string (optional)",
      "scale_text": "string (optional)",
      "extraction_scope": "plan|section|elevation|detail|schedule|other (optional)",
      "bounding_region": { "x": 0.0, "y": 0.0, "width": 0.5, "height": 0.5 },
      "confidence": 0.85,
      "element_ids": ["optional array of extracted_item IDs within viewport"]
    }
  ]
}
```

### CreateViewportBody (direct create — bypass review)

```json
{
  "boundingRegion": { "x": 0.0, "y": 0.0, "width": 0.5, "height": 0.5 },
  "title": "string (required)",
  "detailNumber": "string (optional)",
  "extractionScope": "plan|section|elevation|detail|schedule|other (optional)"
}
```

### GraphViewport (response)

```json
{
  "id": "uuid",
  "sheetId": "uuid",
  "title": "FIRST FLOOR PLAN",
  "detailNumber": "1",
  "scaleText": "1/8\" = 1'-0\"",
  "boundingRegion": { "x": 0.02, "y": 0.05, "width": 0.48, "height": 0.65 },
  "centroid": [0.26, 0.375],
  "bboxSource": "user",
  "elementCount": 342,
  "extractionScope": "plan",
  "userCreated": true,
  "rasterStorageKey": "{projectId}/viewports/{viewportId}.png",
  "createdAt": "2026-04-06T18:30:00Z",
  "updatedAt": "2026-04-06T18:30:00Z"
}
```

All coordinates are **normalized 0-1**. Origin is top-left. Multiply by
image pixel dimensions to convert to pixel coordinates for markup.

---

## Idempotency

Before submitting viewport suggestions for a sheet, check for existing
viewports (already promoted/live):

```bash
existing=$(curl -s "{api_url}/projects/{project_id}/sheets/{sheet_id}/viewports")
```

If viewports already exist on the sheet:
1. Report them to the user
2. Ask whether to skip the sheet, replace existing viewports, or add alongside
3. If replacing: DELETE each existing viewport first, then submit new suggestions
4. Never silently duplicate viewports

Pending suggestions (not yet reviewed) can be safely re-submitted — the
ingest endpoint creates new suggestion rows each time. The user resolves
duplicates during review in the Group Review Gallery.