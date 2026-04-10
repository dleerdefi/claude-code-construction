---
name: spec-splitter
description: >
  Split a bound project manual PDF into individual spec section PDFs and
  extract searchable text. Triggers: 'split specs', 'break up the project
  manual', 'separate spec sections', 'extract spec text'. Prerequisite
  for /submittal-log-generator.
argument-hint: "<project_manual.pdf> [--output-dir <path>]"
disable-model-invocation: true
---

# Spec Splitter

Two functions for specification processing:

1. **Split**: Break a bound project manual PDF into individual spec section PDFs — navigable files the project team can use directly
2. **Extract**: Pull searchable text from each section PDF into persistent `.txt` files — enables downstream skills (submittal-log-generator, spec-parser) to work from text without re-extracting from PDFs

## Pipeline Position
Run after `/project-setup` identifies bound spec manuals. Produces split PDFs, `spec_index.yaml`, and extracted text consumed by `/submittal-log-generator` and `/code-researcher`.

Either function can run independently. For example, specs may already be split but text has not yet been extracted.

## Workflow

```
Spec Split Progress:
- [ ] Step 1: Check current state (split? text extracted?)
- [ ] Step 2: Discover Specifications directory
- [ ] Step 3: Find ALL spec PDFs (bound manuals)
- [ ] Step 4-5: Split PDF into individual section files
- [ ] Step 6: Write spec index
- [ ] Step 7: Extract text from all sections
- [ ] Step 8: Repair degraded/poor text quality
- [ ] Step 9: Write graph entry (AgentCM only)
```

### Step 1: Check Current State

Check what already exists:

**Split PDFs present?**
- Look for individual spec section PDFs with CSI section numbers in filenames (e.g., `03 30 00 - Cast-in-Place Concrete.pdf`)
- Check for `spec_index.yaml`
- If found, report count and skip to Step 7 (text extraction)

**Text already extracted?**
- Check `.construction/spec_text/manifest.json`
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
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/scripts/split_spec_manual.py \
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

### Step 7: Extract Text

After splitting (or if specs are already split), extract searchable text from every section:

```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/scripts/extract_spec_text.py \
  --specs-dir "{resolved_spec_sections_dir}" \
  --output-dir ".construction/spec_text"
```

The script:
- Extracts text from each section PDF via pdfplumber
- Assesses extraction quality (GOOD / DEGRADED / POOR)
- Writes one `.txt` file per section to `.construction/spec_text/`
- Writes `manifest.json` with quality metadata per section
- Incremental: skips sections that already have `.txt` files (use `--force` to re-extract all)

### Step 8: Text Repair — GUIDED

After extraction, check `manifest.json` for sections rated DEGRADED or POOR. Spec-splitter owns text quality — downstream skills (submittal-log-generator, spec-parser) expect clean, repaired text.

**For DEGRADED sections** — attempt repair:

1. Read the `.txt` file and identify failure modes from the manifest
2. **Split word repair**: Scan for sequences of short tokens (≤2 chars) not in known abbreviation lists (GC, CM, PE, QA, SF, LF, etc.). Attempt progressive concatenation of adjacent tokens. Validate against construction vocabulary. Merge if valid; leave as-is if not.
3. **Merged word repair**: Tokens >25 characters that contain multiple dictionary words — insert spaces at word boundaries
4. **Garbled character repair**: Replace known encoding artifacts (e.g., `Ã©` → `é`, ligature breakage)
5. After repair, re-assess quality. If improved, overwrite the `.txt` file and update the manifest with `"repair_attempted": true` and the new quality rating.
6. If repair made things worse, discard repairs and fall back to vision.

**For POOR sections** — vision extraction fallback:

1. Render each page of the section PDF as an image:
   ```bash
   ${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/../../scripts/pdf/rasterize_page.py "{section.pdf}" {page} --dpi 200 --output spec_page.png
   ```
2. Process each page image through vision:
   ```
   Extract all text from this construction specification page.
   Preserve paragraph structure, numbering (A, B, C, 1, 2, 3),
   and indentation hierarchy. This is CSI-formatted specification
   section [SECTION NUMBER] - [SECTION TITLE].
   ```
3. Concatenate extracted text in page order
4. Write the vision-extracted text to `.construction/spec_text/`, overwriting the POOR pdfplumber output
5. Update manifest: `"extraction_method": "vision"`, `"repair_attempted": true`, new quality rating

**Known abbreviation preservation list** (do not merge these during repair):
- Standard: A, I, or, an, as, at, be, by, do, if, in, is, it, no, of, on, so, to, up, we
- Construction: GC, CM, PE, QA, QC, SF, LF, CY, EA, LS, GA, MIL, PSI, KSI, CFM, GPM
- Section refs: A, B, C, D (as paragraph identifiers)

## Output

```
{Specifications dir}/Specification Sections/
  01 10 00 - SUMMARY.pdf
  03 30 00 - CAST-IN-PLACE CONCRETE.pdf
  08 71 00 - DOOR HARDWARE.pdf
  ...
  spec_index.yaml

.construction/spec_text/
  01_10_00.txt
  03_30_00.txt
  08_71_00.txt
  ...
  manifest.json
```

### Step 9: Write Graph Entry (AgentCM only)

If `.construction/` directory exists, write a graph entry:

```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/../../scripts/graph/write_finding.py \
  --type "specs_split" \
  --title "Spec sections split: {N} sections from {source_pdf}" \
  --data '{"section_count": N, "source_pdf": "...", "output_dir": "...", "quality_summary": {"good": X, "degraded": Y, "poor": Z}}'
```

If no `.construction/` directory exists, skip this step — the `spec_index.yaml` and `manifest.json` files serve as the local record.

Report to user: number of sections split, total pages, text extraction quality summary (GOOD/DEGRADED/POOR counts), and output locations.

## File Safety
Never overwrite existing split spec PDFs or extracted text. The split script skips existing sections. Text extraction overwrites only with `--force`. The `spec_index.yaml` merge is additive.

---

## Allowed Scripts

**Allowed scripts — exhaustive list.** Only execute these scripts during this skill:
- `scripts/split_spec_manual.py` — split bound PDF into per-section PDFs
- `scripts/extract_spec_text.py` — extract searchable text from section PDFs
- `../../scripts/pdf/rasterize_page.py` — rasterize PDF pages for vision fallback
- `../../scripts/graph/write_finding.py` — graph entry (Step 9)
