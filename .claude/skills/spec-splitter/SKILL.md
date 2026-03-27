---
name: spec-splitter
description: Split a bound project manual PDF into individual specification section PDFs. Creates a navigable folder of per-section files from a single large project manual. Use when specs are in a single bound PDF and need to be split, or as a prerequisite for submittal-log-generator or spec-parser. Triggers on "split specs", "break up the project manual", "separate spec sections", or when a bound manual is detected by another skill.
argument-hint: "<project_manual.pdf> [--output-dir <path>]"
---

!`mkdir -p ~/.construction-skills/analytics 2>/dev/null; echo "{\"skill\":\"spec-splitter\",\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"repo\":\"$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")\"}" >> ~/.construction-skills/analytics/skill-usage.jsonl 2>/dev/null || true`



# Spec Splitter

Splits a bound project manual PDF into individual specification section PDFs. This is valuable for:
- **Project teams**: Navigate specs by section instead of scrolling a 500+ page PDF
- **Other skills**: `submittal-log-generator` and `spec-parser` work more precisely on individual section files
- **AgentCM**: Split files become the basis for `.construction/specs/`

## Workflow

```
Spec Split Progress:
- [ ] Step 1: Check if specs are already split
- [ ] Step 2: Locate the bound project manual
- [ ] Step 3: Parse Table of Contents
- [ ] Step 4: Find section page boundaries
- [ ] Step 5: Split PDF into individual section files
- [ ] Step 6: Write spec index
```

### Step 1: Check if Specs Are Already Split

Look for individual spec section PDFs. Specs are already split if:
- Multiple PDFs exist with CSI section numbers in filenames (e.g., `03 30 00 - Cast-in-Place Concrete.pdf`)
- A `spec_index.yaml` exists

If already split, report the count and skip.

### Step 2: Find ALL Spec PDFs

Search the project directory for ALL PDFs that are specifications. Many projects have multiple spec PDFs:
- **Multi-volume**: Volume 1.pdf, Volume 2.pdf (split by CSI division range)
- **Single bound manual**: one large PDF with all sections
- **Attachment-based**: Attachment-E-Specs.pdf (government projects)

Search in:
- Folders named `specifications/`, `specs/`, `02 - Specifications/`, or similar (case-insensitive)
- The project root (some projects have no folder structure)
- Look for PDFs > 1MB with keywords: "spec", "manual", "volume", "attachment" + spec-related terms

Process EACH PDF found. All split sections go to the same `specs/` output directory.

If the user specifies a single file (`/spec-splitter path/to/specific-volume.pdf`), process only that file.

### Step 3-6: Split

Run the split script:

```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/../../scripts/pdf/split_spec_manual.py \
  "{project_manual.pdf}" \
  --output-dir "{specs_directory}/specs"
```

The script:
1. Parses the Table of Contents from the first 10-15 pages
2. Searches for `SECTION XX XX XX` headers throughout the PDF to find exact page boundaries
3. Splits into individual PDFs named `{section_number} - {SECTION TITLE}.pdf`
4. Writes `spec_index.yaml` with section metadata

### Output

```
specs/
  01 10 00 - SUMMARY.pdf
  03 30 00 - CAST-IN-PLACE CONCRETE.pdf
  08 71 00 - DOOR HARDWARE.pdf
  ...
  spec_index.yaml
```

Report to user: number of sections split, total pages, output location.
