---
name: project-setup
user-invocable: true
description: "Set up a construction project for Claude Code — inventories files, classifies document types (drawings, specs, schedules, registers), detects AgentCM mode, and appends construction context to CLAUDE.md. Triggers on 'set up project', 'construction setup', 'classify project documents', 'what's in this project'. Use after /init to enrich the project with construction-specific paths and metadata."
argument-hint: "[project-directory]"
---

# Project Setup

Set up a construction project directory for use with Claude Code construction skills. This skill inventories all files, classifies construction document types, and appends construction-specific context to the project's CLAUDE.md.

Run this **after** `/init` has created the base CLAUDE.md.

## Pipeline Position
```
/init (built-in) → THIS SKILL → /spec-splitter, /sheet-splitter → /submittal-log-generator
```
Runs once per project. Identifies which Builder skills should run next.

## Workflow

```
Project Setup Progress:
- [ ] Step 1: Detect operational mode
- [ ] Step 2: Inventory and classify files
- [ ] Step 3: Present summary and recommend next actions
- [ ] Step 4: Amend project CLAUDE.md
```

### Step 1: Detect Operational Mode

Check for `.construction/` directory at the project root.

**If present (AgentCM mode):**
1. Read `.construction/CLAUDE.md` for project navigation context
2. Read `.construction/graph/graph_summary.yaml` for entity counts
3. Read `.construction/index/sheet_index.yaml` for drawing inventory
4. Skip to Step 3 with instant summary — no file scanning needed

**If absent (Flat File mode):**
Continue to Step 2.

### Step 2: Inventory and Classify Files

Scan the project directory. No vision calls — use filename and folder pattern matching only.

**Classification rules:**

| Document Type | Detection Pattern |
|---|---|
| **Drawing sets** | PDFs in `drawings/`, `plans/`, or root with discipline prefixes (A-, S-, M-, E-, P-, C-, L-). PDFs > 2MB with keywords: "plan", "drawing", "bid set", "dwg". |
| **Specifications** | Folders named `Specifications/`, `specs/`, `02 - Specifications/`. PDFs with "project manual", "spec", "volume". CSI section number patterns in filenames. |
| **Schedules** | Excel/CSV files with "schedule", "CPM", "lookahead", "milestone" in name. |
| **Submittal log** | Excel files with "submittal" in name, typically in `Submittals/` or `06 - Submittals/`. |
| **RFI log** | Excel files with "RFI" in name, typically in `RFIs/` or logs folder. |
| **Change orders** | Excel/PDF files with "change order", "CO", "PCO" in name. |
| **Other** | Correspondence, photos, reports, geotechnical, environmental. |

**Also check for existing indexes:**
- `sheet_index.yaml` → drawings already indexed
- `spec_index.yaml` → specs already split
- `.construction/spec_text/manifest.json` → spec text already extracted

### Step 3: Present Summary and Recommend Next Actions

Report what was found:

```
## Project Summary
- Drawing sets: {count} PDFs ({disciplines found})
- Specifications: {bound manual / split sections / not found}
- Schedules: {list}
- Registers: {RFI log, submittal log, CO log — found or not found}
- Other: {count} files

## Recommended Next Actions
```

**Recommendations by mode:**

| Condition | Recommendation |
|---|---|
| Bound spec manual found, not yet split | "Run `/spec-splitter` to split the project manual into individual sections and extract searchable text." |
| Bound drawing set found, flat file mode | "Run `/sheet-splitter` to split the drawing set into individual sheet PDFs and identify sheet numbers." |
| Bound drawing set found, AgentCM mode | "Split sheets via the AgentCM UI for zero-vision-cost splitting using labeled OCR data." |
| Specs already split but no text extracted | "Run `/spec-splitter` — specs are split but text extraction hasn't been done yet." |
| Submittal log needed | "Run `/submittal-log-generator` after spec text is available." |
| Specs split and text extracted | "Would you like to generate a submittal log from the specification sections? Run `/submittal-log-generator`." |

### Step 4: Amend Project CLAUDE.md

Append construction-specific context to the **project root's CLAUDE.md** (the file created by `/init`). Do NOT modify the construction skills directory CLAUDE.md.

**Append format:**

```markdown
## Construction Project Context

### Document Locations
- Drawing set: {path} ({N} sheets, disciplines: {list})
- Specifications: {path} ({N} sections or "bound manual, not yet split")
- Schedule: {path or "not found"}
- RFI log: {path or "not found"}
- Submittal log: {path or "not found"}

### Status
- Operational mode: {AgentCM / Flat File}
- Sheets indexed: {yes/no}
- Specs split: {yes/no}
- Spec text extracted: {yes/no}
```

Only append — never overwrite existing CLAUDE.md content.

### What This Skill Does NOT Do

- **Does not split PDFs** — recommends `/spec-splitter` and `/sheet-splitter` instead
- **Does not use vision** — all classification is filename/folder pattern matching
- **Does not create .construction/ directory** — that's AgentCM's job
- **Does not replace /init** — `/init` creates the base CLAUDE.md, this skill enriches it
