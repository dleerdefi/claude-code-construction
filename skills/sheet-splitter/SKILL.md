---
name: sheet-splitter
description: >
  Split a bound drawing set PDF into individual sheet PDFs. Extracts sheet
  numbers from title blocks via vision, renames files, and records where the
  cover sheet's drawing index disagrees with the set, logging the ones that need
  an RFI for rfi-drafter. Triggers: 'split
  drawings', 'break up the drawing set', 'separate sheets'. Run after
  /project-setup.
argument-hint: "<drawing_set.pdf> [--output-dir <path>]"
disable-model-invocation: true
---

# Sheet Splitter

Splits a bound drawing set PDF into individual page PDFs. Mirrors what spec-splitter does for specifications.

## Pipeline Position
Run after `/project-setup` identifies bound drawing sets. Produces split PDFs and `sheet_index.yaml` consumed by `/schedule-extractor` and all drawing analysis skills.

This is valuable for:
- **Project teams**: Navigate drawings by sheet number instead of scrolling a multi-page PDF
- **Other skills**: schedule-extractor, tag-audit-and-takeoff, pe-review and every other drawing analysis skill work better with individual sheet files

In an AgentCM project the app splits drawing sets (Split & Rename), and this skill only says so (Step 1).

## Workflow

```
Sheet Split Progress:
- [ ] Step 1: Check the mode, and whether drawings are already split
- [ ] Step 2: Locate the bound drawing set
- [ ] Step 3: Split into individual page PDFs
- [ ] Step 4: Extract sheet numbers from title blocks, rename files with sheet number + title
- [ ] Step 5: Check the sheets against the drawing index
- [ ] Step 6: Write the sheet index
- [ ] Step 7: Update project context
```

### Step 1: Check the Mode, and Whether Drawings Are Already Split

First read `.construction/project.yaml`. If it exists, AgentCM manages this folder: do not split, rename or index anything.

- Read `.construction/index/sheet_index.yaml`. When its entries carry AgentCM's sheet ids (a `sheets:` list whose entries each have an `id:`), report how many sheets AgentCM holds and tell the PE that a new or reissued bound set is split with **Split & Rename** in AgentCM, which keeps every sheet's id. A split made here writes PDFs AgentCM never registers, and its Rescan would index them as a second drawing set. Then stop.
- When that file is missing, or its entries have no `id` (an older sheet-splitter wrote a `pages:` list with `filename` and `page_index`), say which, say that this skill does not guess sheet ids, and stop. Do not edit the file.

Without `.construction/project.yaml`, drawings are already split if:
- Multiple PDFs exist with sheet number patterns in filenames (e.g., `A-1.1 - FLOOR PLAN.pdf`)
- A `sheet_index.yaml` exists in the drawings directory

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
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_SKILL_DIR}/scripts/split_drawing_set.py" \
  "{drawing_set.pdf}" \
  --output-dir "{drawings_directory}/sheets"
```

The script splits each page into its own PDF: `page_001.pdf`, `page_002.pdf`, etc. It does NOT attempt to read sheet numbers — that's unreliable across different title block formats.

### Step 4: Identify Sheets via Vision

After splitting, read each page to identify sheet numbers and titles:

Use PDF bookmarks and the title-block text layer only as candidates — they are often abbreviated or stale (e.g. a bookmark "Site Grading Plan" on a sheet printed "Proposed Site Plan"). The printed title block wins. Read the title block by vision whenever there is no candidate, the candidate disagrees with the title-block text, or the sheet number carries a suffix (e.g. `C9.04H`, `K-1.1`).

1. Rasterize the title block region of each page, from the project folder:
```bash
mkdir -p ".construction/skills/sheet-splitter/pages"
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/pdf/rasterize_page.py" "{sheets_dir}/page_NNN.pdf" 1 --dpi 200 --output ".construction/skills/sheet-splitter/pages/tb_NNN.png"
```
Title-block images are working data: keep them under `.construction/skills/sheet-splitter/pages/`. Never put them in the sheets folder, where the PE's split sheets are, and never in `/tmp` or any other folder outside the project.

2. Use vision on the rasterized title block: "Read the title block on this construction drawing. What is the sheet number and sheet title?"

3. Rename the file: `page_001.pdf` → `A-1.1 - FLOOR PLAN.pdf`

4. Update `sheet_index.yaml` with the identified sheet number, title, and discipline. When a bookmark title differs from the printed title, keep it as `bookmark_title`.

**Title blocks vary significantly across firms** — they can be on the east side, south side, or bottom-center. Some use VA standard forms, some use firm-specific formats. Vision handles all these variations.

### Step 5: Check the Sheets Against the Drawing Index

The cover or title sheet usually lists every sheet in a drawing index (also called a sheet index or list of drawings). When the set has one, compare it with the title blocks read in Step 4. The title blocks still name the files; the index only shows where the set disagrees with itself.

1. Read the index sheet's text, from the project folder:
```bash
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/pdf/pdf_text.py" "{sheets_dir}/{index sheet}.pdf"
```
If the page shows VISION, rasterize the index's area (`--crop x1,y1,x2,y2`, percentages of the page) and read it by vision:
```bash
mkdir -p ".construction/skills/sheet-splitter/pages"
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/pdf/rasterize_page.py" "{sheets_dir}/{index sheet}.pdf" 1 --dpi 200 --crop "x1,y1,x2,y2" --output ".construction/skills/sheet-splitter/pages/index.png"
```
An index can run onto a second sheet, and an index often lists the whole project, every discipline, including sets kept in other PDFs (see **not in set** below).

2. Compare row by row. Each of these is a mismatch:
   - **number**: the index writes the number differently from the title block (`M2.01` in the index, `M-2.01` in the title block; `P 1.1` against `P-1.1`)
   - **title**: the index gives the sheet a different title. Abbreviation, punctuation and case alone are not a difference (`ELEC` for `ELECTRICAL`)
   - **not in set**: the index lists a sheet that no drawing PDF in the project folder carries. Look across the folder, not only at the set you split: a sheet is present when it was split in this run, when a PDF in the folder is named by its number (any spacing or punctuation: `E201.pdf`, `E-201 - LIGHTING PLAN.pdf`), or when a page of another bound drawing set prints it in its title block (read that set with `pdf_text.py`; a number that appears only in a note, a reference such as `SEE E-201`, or a drawing index does not count)
   - **not in index**: a title block carries a sheet the index does not list

   A bookmark is not the index: a bookmark that differs goes in `bookmark_title` (Step 4), not here.

3. Which mismatches get a suggested RFI, the question for the design team:
   - **title differs:** always. *The drawing index on {index sheet} lists {sheet} as {index title}; its title block reads {title block title}. Please confirm the correct title and which document will be revised.*
   - **not in set:** group the missing sheets by discipline, the letters before the number (`E` in `E-201`, `FP` in `FP-101`).
     - A discipline with none of its sheets in the folder gets one note in place of its sheets' entries, `{discipline} sheets not in the folder: not checked`, with no RFI and no issue. The folder likely holds only part of the project.
     - A missing sheet whose discipline is otherwise in the folder (another of its listed sheets is present) gets a suggested RFI: *The drawing index on {index sheet} lists {sheet} {index title}, but the set does not include it. Please issue the sheet or confirm that it is removed from the index.* When more than 3 sheets qualify, they share one summary RFI instead: *The drawing index on {index sheet} lists {N} sheets the set does not include: {sheets}. Please issue them or confirm that they are removed from the index.*
   - **number** written differently and **not in index**: notes, with no RFI and no issue.

   Log each suggested RFI in the issue registry (one per title that differs and per missing sheet, or the one summary for the missing sheets), so `/construction:rfi-drafter` picks it up:
```bash
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/issue_manager.py" add \
  --source-skill "sheet-splitter" --severity {conflict|warning} --confidence high \
  --description "{the suggested RFI}" \
  --sheets "{index sheet},{sheet, or each sheet of the summary}" \
  --context "sheet-splitter drawing index check: the index on {index sheet} against the title blocks" \
  --rfi-subject "Drawing index: {sheet} {title differs|not in the set}, or {N} sheets not in the set"
```
   `--severity conflict` for a title that differs (two documents disagree), `warning` for missing sheets. The script prints the issue as JSON: keep its `id`.

4. When there is at least one mismatch, write them all, notes included, as one finding in `.construction/skills/sheet-splitter/findings/`:
```bash
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/graph/write_finding.py" \
  --skill "sheet-splitter" --type "drawing_index_mismatch" \
  --title "Drawing index vs title blocks: {N} mismatches" \
  --source-sheets '["{index sheet}", "{each sheet with a mismatch}"]' \
  --data '{"index_sheet": "{index sheet}", "mismatches": [{"sheet": "{the number as the title block prints it}", "kind": "number|title|not_in_set|not_in_index", "title_block": {"number": "...", "title": "..."}, "index": {"number": "...", "title": "..."}, "suggested_rfi": "...", "issue_id": "..."}]}'
```
   One entry per mismatch. For a sheet only the index lists, `sheet` is the index's number and `title_block` is `null`; for a sheet the index does not list, `index` is `null`. `suggested_rfi` and `issue_id` come from step 3, and are `null` on a note; sheets under a summary RFI each carry the summary's. A discipline not in the folder is one entry: `{"kind": "discipline_not_in_folder", "discipline": "E", "sheets": ["E-101", "E-201"], "note": "E sheets not in the folder: not checked", "suggested_rfi": null, "issue_id": null}`. Inside `--data`, write an apostrophe as `\u0027`.

5. The script prints `OK: Finding written → <path>`. Name that file in the report to the user, with each mismatch and the issue ids. When the set has no drawing index, or every row matches, say so in the report and write no finding.

### Step 6: Write Sheet Index

After identifying all sheets, write `{drawings_directory}/sheets/sheet_index.yaml` (shown below). Never write `.construction/index/` — that folder belongs to AgentCM; only read it.

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

### Step 7: Update Project Context

After splitting and identifying, update `.construction/skills/project_context.yaml` with:
- `documents.drawing_count`: number of sheets
- `documents.disciplines`: list of unique discipline prefixes found

The `sheet_index.yaml` in the sheets folder is the record of the split.

### Multi-Set Projects

When a project has multiple drawing set PDFs (e.g., Architectural, MEP, Civil as separate files), use the source PDF name as a subdirectory to avoid filename collisions:

```
sheets/
  Architectural_Bid_Set/
    page_001.pdf ... page_050.pdf
  MEP_Bid_Set/
    page_001.pdf ... page_030.pdf
  sheet_index.yaml  ← merged from all sets
```

Pass `--output-dir "{drawings_directory}/sheets/{source_pdf_stem}"` to the split script for each set. The `sheet_index.yaml` merge logic combines entries from all subdirectories into a single index.

Report to user: number of pages split, how many identified via vision, output location, and the drawing index check (Step 5): the finding's file, its mismatches and the issues logged, or that the index matched or the set has none.

## File Safety
Never overwrite existing split sheet PDFs. If `sheets/` directory already contains files, check for conflicts before writing. The `sheet_index.yaml` merge uses additive logic — existing entries are preserved.

---

## Allowed Scripts

**Allowed scripts — exhaustive list.** Only execute these scripts during this skill:
- `scripts/split_drawing_set.py` — split bound PDF into per-page PDFs
- `${CLAUDE_PLUGIN_ROOT}/scripts/pdf/rasterize_page.py` — rasterize PDF pages for vision identification
- `${CLAUDE_PLUGIN_ROOT}/scripts/pdf/pdf_text.py` — the drawing index's text (Step 5)
- `${CLAUDE_PLUGIN_ROOT}/scripts/graph/write_finding.py` — the drawing index mismatches, one finding in `.construction/skills/sheet-splitter/findings/` (Step 5)
- `${CLAUDE_PLUGIN_ROOT}/scripts/issue_manager.py` — each mismatch with a suggested RFI, in the issue registry for rfi-drafter (Step 5)
