---
name: spec-splitter
description: >
  Split a bound project manual PDF into individual spec section PDFs and
  extract searchable text. Triggers: 'split specs', 'break up the project
  manual', 'separate spec sections', 'extract spec text'. Prerequisite
  for /submittal-log-generator.
argument-hint: "<project_manual.pdf> [--output-dir <path>]"
---

# Spec Splitter

Two functions for specification processing:

1. **Split**: Break a bound project manual PDF into individual spec section PDFs — navigable files the project team can use directly
2. **Extract**: Pull searchable text from each section PDF into persistent `.txt` files — enables downstream skills (submittal-log-generator, submittal-review, bid-evaluator) to work from text without re-extracting from PDFs

## Pipeline Position
Run after `/project-setup` identifies bound spec manuals. Produces split PDFs, `spec_index.yaml`, and extracted text consumed by `/submittal-log-generator` and `/code-researcher`.

Either function can run independently. For example, specs may already be split but text has not yet been extracted.

In an AgentCM project, AgentCM has already read the manuals: each section's text is in `.construction/specs/`, listed in `.construction/INDEX.md`. There this skill does only what AgentCM could not (Step 1).

## Workflow

```
Spec Split Progress:
- [ ] Step 1: Check the mode, then the current state (split? text extracted?)
- [ ] Step 2: Discover Specifications directory
- [ ] Step 3: Find ALL spec PDFs (bound manuals)
- [ ] Step 4-5: Split PDF into individual section files
- [ ] Step 6: Write spec index
- [ ] Step 7: Extract text from all sections
- [ ] Step 8: Repair degraded/poor text quality
```

### Step 1: Check the Mode, Then the Current State

Read `.construction/project.yaml` first.

**AgentCM mode** (the file exists). AgentCM has read the project manuals' text layer: every section it found has its text in `.construction/specs/<section>.txt` (`08-71-00.txt` for 08 71 00), each line prefixed with its page. Never split or extract a manual AgentCM has read; the other skills read `specs/` here. Read `.construction/INDEX.md`; if it is missing, say that AgentCM has not written its index for this folder, and stop.

1. **`## Specification sections (N)`**, a table of Section | Title | Division | Agent file | PDF | Pages: report how many sections AgentCM holds, by division and manual, and that their text is in `.construction/specs/`.
2. **`## Spec manuals not read (N)`**, when present, a table of PDF | Pages | Why (a scan with no text layer, or no SECTION headings): for each manual listed there, and only those, run Steps 2–8 for that manual alone, and say so: "AgentCM could not read {PDF} ({Why}), so I am splitting and extracting it here. Its section PDFs go to the specs folder, which AgentCM's Rescan will index; its text goes to `.construction/skills/spec_text/`." Its boundaries come from [Boundaries without SECTION headings](#boundaries-without-section-headings): what AgentCM reports means the split script cannot find them itself.
3. **Section PDFs of a manual AgentCM has read**, only when the PE asks for those files: build them from AgentCM's list, as [Section PDFs from AgentCM's list](#section-pdfs-from-agentcms-list) says. No text extraction: the text is AgentCM's.

Then stop. Nothing else in this skill runs in AgentCM mode.

**Flat-file mode** (no `.construction/project.yaml`). Check what already exists:

**Split PDFs present?**
- Look for individual spec section PDFs with CSI section numbers in filenames (e.g., `03 30 00 - Cast-in-Place Concrete.pdf`)
- Check for `spec_index.yaml`
- If found, report count and skip to Step 7 (text extraction)

**Text already extracted?**
- Check `.construction/skills/spec_text/manifest.json`. Older versions wrote it to `.construction/spec_text/`: if only that exists, copy the folder to `.construction/skills/spec_text/` and leave the old one as it is
- If manifest exists and covers all sections, report and skip Step 7

### Step 2: Discover Specifications Directory

Determine where split spec PDFs should go. Search for an existing Specifications directory (case-insensitive):
1. `02 - Specifications/` (numbered project folder convention)
2. `Specifications/`
3. Any folder with "specification" in the name

**Output directory resolution:**
- If Specifications directory found → output to `{specs_dir}/Specification Sections/`
- If not found → output to `Specification Sections/` in project root

### Step 3: Find ALL Spec PDFs

Search the project directory for ALL PDFs that are specifications. Many projects have multiple spec PDFs:
- **Multi-volume**: Volume 1.pdf, Volume 2.pdf (split by CSI division range)
- **Single bound manual**: one large PDF with all sections
- **Attachment-based**: Attachment-E-Specs.pdf (government projects)

Search in:
- The Specifications directory discovered in Step 2
- The project root (some projects have no folder structure)
- Look for PDFs > 1MB with keywords: "spec", "manual", "volume", "attachment" + spec-related terms

Process EACH PDF found. All split sections go to the same output directory.

If the user specifies a single file (`/spec-splitter path/to/specific-volume.pdf`), process only that file.

### Steps 4-6: Split and Index

Run the split script with the resolved output directory:

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_SKILL_DIR}/scripts/split_spec_manual.py" \
  "{project_manual.pdf}" \
  --output-dir "{resolved_spec_sections_dir}"
```

The script:
1. Scans ALL pages for `SECTION XX XX XX` headers to find exact page boundaries — this is the primary method and does NOT depend on a Table of Contents
2. Scans all pages for Table of Contents entries to enrich section titles (optional, best-effort)
3. For sections without ToC titles, extracts titles directly from the section header page
4. Splits into individual PDFs named `{section_number} - {SECTION TITLE}.pdf`
5. Writes `spec_index.yaml` with section metadata

**ToC edge cases handled:**
- **ToC located deep in the document** (e.g., page 60+): Common when front matter (transmittals, addenda) precedes the project manual. The script scans all pages, not just the first few.
- **No ToC at all**: Section boundaries are found by scanning every page for `SECTION` headers. Titles are extracted directly from each section's title page. The split still succeeds — titles may be slightly less polished than ToC-enriched versions.

If the script stops with `No SECTION headers found` (a scan, or headings in another form), find the boundaries as [Boundaries without SECTION headings](#boundaries-without-section-headings) says, and split from a sections file.

### Step 7: Extract Text

After splitting (or if specs are already split), extract searchable text from every section:

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_SKILL_DIR}/scripts/extract_spec_text.py" \
  --specs-dir "{resolved_spec_sections_dir}" \
  --output-dir ".construction/skills/spec_text"
```

The script:
- Extracts text from each section PDF via pdfplumber
- Assesses extraction quality (GOOD / DEGRADED / POOR)
- Writes one `.txt` file per section to `.construction/skills/spec_text/`
- Writes `manifest.json` with quality metadata per section
- Incremental: skips sections that already have `.txt` files (use `--force` to re-extract all)

### Step 8: Text Repair — GUIDED

After extraction, check `manifest.json` for sections rated DEGRADED or POOR. Spec-splitter owns text quality — downstream skills (submittal-log-generator, submittal-review, bid-evaluator) expect clean, repaired text.

**For DEGRADED sections** — attempt repair:

1. Read the `.txt` file and identify failure modes from the manifest
2. **Split word repair**: Scan for sequences of short tokens (≤2 chars) not in known abbreviation lists (GC, CM, PE, QA, SF, LF, etc.). Attempt progressive concatenation of adjacent tokens. Validate against construction vocabulary. Merge if valid; leave as-is if not.
3. **Merged word repair**: Tokens >25 characters that contain multiple dictionary words — insert spaces at word boundaries
4. **Garbled character repair**: Replace known encoding artifacts (e.g., `Ã©` → `é`, ligature breakage)
5. After repair, re-assess quality. If improved, overwrite the `.txt` file and update the manifest with `"repair_attempted": true` and the new quality rating.
6. If repair made things worse, discard repairs and fall back to vision.

**For POOR sections** — vision extraction fallback. A scanned manual is POOR on every page, and this reads every page of it: before reading the pages of a scan, tell the PE how many pages that is and the rough cost (each page image at 200 DPI is about 1,600 tokens), offer to extract only the sections they need, and wait for a yes.

1. Render each page of the section PDF as an image:
   ```bash
   "${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/pdf/rasterize_page.py" "{section.pdf}" {page} --dpi 200 --output spec_page.png
   ```
2. Process each page image through vision:
   ```
   Extract all text from this construction specification page.
   Preserve paragraph structure, numbering (A, B, C, 1, 2, 3),
   and indentation hierarchy. This is CSI-formatted specification
   section [SECTION NUMBER] - [SECTION TITLE].
   ```
3. Concatenate extracted text in page order
4. Write the vision-extracted text to `.construction/skills/spec_text/`, overwriting the POOR pdfplumber output
5. Update manifest: `"extraction_method": "vision"`, `"repair_attempted": true`, new quality rating

**Known abbreviation preservation list** (do not merge these during repair):
- Standard: A, I, or, an, as, at, be, by, do, if, in, is, it, no, of, on, so, to, up, we
- Construction: GC, CM, PE, QA, QC, SF, LF, CY, EA, LS, GA, MIL, PSI, KSI, CFM, GPM
- Section refs: A, B, C, D (as paragraph identifiers)

## Sections Files

A sections file tells the split script exactly where each section is, so it reads nothing from the pages. It is tab-separated text, the same format the script's docstring defines:

```
# manual: 02 - Specifications/Project Manual VOL-2.pdf
# pages: 1-based
section	title	first	last
08 71 00	DOOR HARDWARE	412	431
09 65 13	RESILIENT BASE AND ACCESSORIES	455	460
```

- `# manual:` names the PDF being split; `# pages: 1-based` states the page base. Page 1 is the manual's first page, as INDEX.md and `specs/` give pages; convert nothing.
- One line per section: number, title, first page, last page (inclusive). Gaps are allowed.
- Write it with the Write tool to `.construction/skills/spec-splitter/sections-{manual file stem}.tsv`. It is a data file, not a script.
- The script refuses a file whose pages overlap, run backwards or fall outside the manual, or that lacks the page base, and says why: correct the file.

Split from it:

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_SKILL_DIR}/scripts/split_spec_manual.py" \
  "{manual.pdf}" \
  --sections-file ".construction/skills/spec-splitter/sections-{manual file stem}.tsv" \
  --output-dir "{resolved_spec_sections_dir}"
```

### Section PDFs from AgentCM's List

AgentCM mode, only when the PE asks for section PDFs of a manual AgentCM has read. Build the sections file from the rows of INDEX.md's `## Specification sections` table whose PDF is that manual: Section, Title and Pages (`412-431`, or `412` for a one-page section; 1-based). Take only the sections the PE asked for, or all of them if they asked for all. A row with no Pages cannot be split from the index: list it for the PE and leave it out. Read no pages and use no vision. After the split, tell the PE where the files are and that AgentCM's Rescan will index them.

### Boundaries without SECTION headings

For a manual AgentCM lists as not read, or one the split script found no headings in. First see what the manual holds:

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/pdf/pdf_text.py" "{manual.pdf}" --summary
```

- **Pages marked TEXT** (a text layer whose headings take another form, such as `SECTION 08710`, or only footers like `08 71 00 - 1`): dump the text with `pdf_text.py "{manual.pdf}" --pages {range}` and find each section's first page from its heading, its footer's page 1 or the Table of Contents.
- **Pages marked VISION** (a scan): before reading any page image, tell the PE the manual's page count and the rough cost (one footer or header strip per page, each a small image of about 125 tokens at 100 DPI), and wait for a yes. Never read every page of a large scan unasked. With a yes, read the strip where the section number and page number print, usually the footer:
  ```bash
  "${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/pdf/rasterize_page.py" "{manual.pdf}" {page} --dpi 100 --crop 0,90,100,100 --output ".construction/skills/spec-splitter/strip.png"
  ```
  `--crop` is x1,y1,x2,y2 in percent of the page (`0,0,100,8` for the header). A section starts on its page 1 (`08 71 00 - 1`), which also carries its title.

Write what you found as a sections file, show the PE the list, and split from it.

## Output

```
{Specifications dir}/Specification Sections/
  01 10 00 - SUMMARY.pdf
  03 30 00 - CAST-IN-PLACE CONCRETE.pdf
  08 71 00 - DOOR HARDWARE.pdf
  ...
  spec_index.yaml

.construction/skills/spec_text/
  01_10_00.txt
  03_30_00.txt
  08_71_00.txt
  ...
  manifest.json

.construction/skills/spec-splitter/
  sections-{manual file stem}.tsv   ← only when a split used a sections file
```

The `spec_index.yaml` and `manifest.json` files are the record of the split and the extraction.

Report to user: number of sections split, total pages, text extraction quality summary (GOOD/DEGRADED/POOR counts), and output locations.

## File Safety
Never overwrite existing split spec PDFs or extracted text. The split script skips existing sections. Text extraction overwrites only with `--force`. The `spec_index.yaml` merge is additive.

---

## Allowed Scripts

**Allowed scripts — exhaustive list.** Only execute these scripts during this skill:
- `scripts/split_spec_manual.py` — split bound PDF into per-section PDFs, from SECTION headings or a sections file
- `scripts/extract_spec_text.py` — extract searchable text from section PDFs
- `${CLAUDE_PLUGIN_ROOT}/scripts/pdf/pdf_text.py` — see which pages have a text layer, and read it, to find section boundaries
- `${CLAUDE_PLUGIN_ROOT}/scripts/pdf/rasterize_page.py` — rasterize pages for the vision fallback and for a scan's footer strips
- `${CLAUDE_PLUGIN_ROOT}/scripts/issue_manager.py` — log a referenced spec section that does not exist to the Issue Registry (command and severity mapping in construction-guide)
