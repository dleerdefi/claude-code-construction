---
name: sheet-splitter
description: Split a bound drawing set PDF into individual sheet PDFs. Creates one PDF per page from a combined/stapled drawing set, extracts sheet numbers from title blocks, and renames files accordingly. Use when drawings are in a single multi-page PDF instead of individual sheet files. Triggers on "split drawings", "break up the drawing set", "separate sheets", or when a bound drawing set is detected by another skill.
argument-hint: "<drawing_set.pdf> [--output-dir <path>]"
---

!`mkdir -p ~/.construction-skills/analytics 2>/dev/null; echo "{\"skill\":\"sheet-splitter\",\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"repo\":\"$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")\"}" >> ~/.construction-skills/analytics/skill-usage.jsonl 2>/dev/null || true`



# Sheet Splitter

Splits a bound drawing set PDF into individual page PDFs. Mirrors what spec-splitter does for specifications.

This is valuable for:
- **Project teams**: Navigate drawings by sheet number instead of scrolling a multi-page PDF
- **Other skills**: `sheet-index-builder`, `drawing-reader`, and all drawing analysis skills work better with individual sheet files
- **AgentCM**: Split files become the basis for per-sheet structured data

## Workflow

```
Sheet Split Progress:
- [ ] Step 1: Check if drawings are already split
- [ ] Step 2: Locate the bound drawing set
- [ ] Step 3: Split into individual page PDFs
- [ ] Step 4: Extract sheet numbers from title blocks
- [ ] Step 5: Rename files with sheet number + title
- [ ] Step 6: Write sheet index
```

### Step 1: Check if Drawings Are Already Split

Look for individual sheet PDFs. Drawings are already split if:
- Multiple PDFs exist with sheet number patterns in filenames (e.g., `A-1.1 - FLOOR PLAN.pdf`)
- A `sheet_index.yaml` exists

If already split, report the count and skip.

### Step 2: Find ALL Drawing PDFs

Search the project directory for ALL PDFs that are drawings. Many projects have multiple drawing PDFs:
- **Multi-part sets**: Part1.pdf, Part2.pdf, Part3.pdf (split by file size)
- **Discipline sets**: Architectural.pdf, Civil.pdf, Electrical.pdf, Mechanical.pdf
- **Single combined**: one large PDF with all sheets

Search in:
- Folders named `drawings/`, `plans/`, `01 - Drawings/`, or similar (case-insensitive)
- The project root (some projects have no folder structure)
- Look for PDFs > 2MB with keywords: "plan", "drawing", "bid set", "dwg", discipline names

Process EACH PDF found. All split pages go to the same `sheets/` output directory.

If the user specifies a single file (`/sheet-splitter path/to/specific.pdf`), process only that file.

### Step 3: Split Pages

Run the split script on each drawing PDF found:

```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/../../scripts/pdf/split_drawing_set.py \
  "{drawing_set.pdf}" \
  --output-dir "{drawings_directory}/sheets"
```

The script splits each page into its own PDF: `page_001.pdf`, `page_002.pdf`, etc. It does NOT attempt to read sheet numbers — that's unreliable across different title block formats.

### Step 4: Identify Sheets via Vision

After splitting, read each page to identify sheet numbers and titles:

1. Rasterize the title block region of each page:
```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/../../scripts/pdf/rasterize_page.py page_NNN.pdf 1 --dpi 200 --output tb.png
```

2. Use vision on the rasterized title block: "Read the title block on this construction drawing. What is the sheet number and sheet title?"

3. Rename the file: `page_001.pdf` → `A-1.1 - FLOOR PLAN.pdf`

4. Update `sheet_index.yaml` with the identified sheet number, title, and discipline.

**Title blocks vary significantly across firms** — they can be on the east side, south side, or bottom-center. Some use VA standard forms, some use firm-specific formats. Vision handles all these variations.

### Step 5: Write Sheet Index

After identifying all sheets, write `.construction/index/sheet_index.yaml`.

### Output

```
sheets/
  A-1.1 - FLOOR PLAN.pdf         ← renamed by Claude via vision
  A-2.1 - ELEVATIONS.pdf
  S-1.1 - FOUNDATION PLAN.pdf
  page_006.pdf                    ← could not read title block
  ...
  sheet_index.yaml
```

### Updating Project Context

After splitting and identifying, update `.construction/project_context.yaml` with:
- `documents.drawing_count`: number of sheets
- `documents.disciplines`: list of unique discipline prefixes found

Report to user: number of pages split, how many identified via vision, output location.
