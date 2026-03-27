---
name: project-onboarding
description: Index and classify a construction project's files on first contact. Use when opening a new project folder, when asked to explore or inventory project documents, or when no sheet index exists yet. Triggers on phrases like "new project", "what is in this project", "index the drawings", or "set up the project".
disable-model-invocation: true
---

!`mkdir -p ~/.construction-skills/analytics 2>/dev/null; echo "{\"skill\":\"project-onboarding\",\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"repo\":\"$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")\"}" >> ~/.construction-skills/analytics/skill-usage.jsonl 2>/dev/null || true`



# Project Onboarding

Meta-skill that runs on first contact with a construction project. Produces a project context file, file inventory, and triggers downstream indexing.

## Current Project Files
!`ls *.pdf drawings/ specs/ plans/ Drawings/ Specifications/ 2>/dev/null | head -30 || echo "No standard directories found"`

## Workflow

```
Onboarding Progress:
- [ ] Step 1: Detect data mode
- [ ] Step 2: Read or build project context
- [ ] Step 3: Inventory all files
- [ ] Step 4: Classify documents
- [ ] Step 5: Build sheet index (trigger sheet-index-builder)
- [ ] Step 6: Report summary to user
- [ ] Step 7: Write graph entry
```

### Step 1: Detect Data Mode

### Data Mode Detection

Check for `.construction/` directory in the project root:

**AgentCM present**: Read structured data from `.construction/` — pre-indexed sheets, parsed specs, OCR annotations, resolved cross-references. Fast and token-efficient.

**Vision fallback**: Use Claude Code vision on rasterized PDFs plus `pdfplumber` for text extraction:
```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/../../scripts/pdf/rasterize_page.py {pdf_path} {page} --dpi 200 --output page.png
```


**If AgentCM present**: Read `.construction/CLAUDE.md` and `.construction/index/file_manifest.yaml`. Skip to Step 6 — the platform has already indexed everything.

**If no AgentCM**: Continue with vision-based onboarding below.

### Step 2: Read or Build Project Context

Look for a title block on the first drawing sheet you find (any PDF in a `drawings/` or `plans/` folder). Extract:
- Project name
- Project number
- Location (city, state — needed for code compliance)
- Architect / Engineer names
- Date / phase (e.g., "100% CD", "Bid Set", "Addendum 2")

Write to `.construction/project_context.yaml` using the template at `${CLAUDE_SKILL_DIR}/../../templates/project_context.yaml`.

### Step 3: Inventory All Files

Scan the project directory recursively. Catalog every file with:
- File path
- File type (PDF, DWG, DOCX, XLS, etc.)
- File size
- Parent folder name (used for classification)

### Step 4: Classify Documents

Classify each file into categories:
- **Drawings**: PDFs with sheet numbers in filenames or containing title blocks
- **Specifications**: PDFs/DOCX in `Specs/` folders or with CSI section numbers in filenames
- **Schedules**: Excel/CSV files with schedule data
- **Submittals**: PDFs in submittal folders
- **RFIs**: Documents in RFI folders
- **Other**: Correspondence, photos, reports, etc.

### Step 5: Build Sheet Index

Trigger the `sheet-index-builder` skill to create `.construction/index/sheet_index.yaml`.

### Step 6: Report Summary

Present to user:
- Project name, number, location
- Document counts by category
- Drawing count by discipline
- Spec sections identified
- Any issues found (missing sheets, unreadable files)

### Step 7: Write Graph Entry

```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/../../scripts/graph/write_finding.py \
  --type "project_onboarded" \
  --title "Project onboarding completed" \
  --data '{"drawings": N, "specs": N, "disciplines": ["A","S","M","E","P"]}'
```
