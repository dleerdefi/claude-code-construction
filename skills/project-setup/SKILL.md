---
name: project-setup
description: >
  Set up a construction project — inventories files, classifies
  drawings/specs/schedules/registers and appends construction context to
  CLAUDE.md; in an AgentCM project, prints AgentCM's orientation instead.
  Triggers: 'set up project', 'construction setup', 'classify documents'.
argument-hint: "[project-directory]"
disable-model-invocation: true
---

# Project Setup

Set up a construction project directory for use with Claude Code construction skills. Without AgentCM, this skill inventories all files, classifies construction document types, and appends construction-specific context to the project's CLAUDE.md. With AgentCM, which has already indexed the folder and keeps the one map of it in CLAUDE.md, it only reports AgentCM's orientation (Step 1).

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

Check for AgentCM: `.construction/project.yaml` at the project root.

**If present (AgentCM mode)**, AgentCM has indexed the folder and written its own navigation block into CLAUDE.md. Report its orientation and stop:

1. Say that the construction plugin is installed, with its version from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`. Read `contract_version` in `.construction/project.yaml`; if it is missing (AgentCM older than contract 1) or above 1, say which.
2. Read `.construction/INDEX.md`. If it is missing, say that AgentCM has not written its index for this folder yet, and stop. Otherwise report, from its sections:
   - **Drawing sheets**: how many, by discipline, and how many are still under "Pages not yet named"; any sheet whose Text is `partial`, `pending` or `failed`
   - **Specification sections**: how many, by division; and every manual under "Spec manuals not read", with its reason (`/construction:spec-splitter` splits and extracts those, and only those)
   - **Schedules and legends**: how many, by kind
   - **Rooms**: how many are known and how they were found, as INDEX.md states it
3. If `.construction/pending.tsv` exists, list the sheets it names (queued for a refresh, or failed with a reason): their files may be out of date until AgentCM catches up.

Then stop. In AgentCM mode this skill inventories no files, recommends no splitting and does not touch CLAUDE.md.

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
- `.construction/skills/spec_text/manifest.json` → spec text already extracted (an older version's `.construction/spec_text/` counts too: copy it to `.construction/skills/spec_text/` and leave the old one as it is)

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
| Bound drawing set found | "Run `/sheet-splitter` to split the drawing set into individual sheet PDFs and identify sheet numbers." |
| Specs already split but no text extracted | "Run `/spec-splitter` — specs are split but text extraction hasn't been done yet." |
| Submittal log needed | "Run `/submittal-log-generator` after spec text is available." |
| Specs split and text extracted | "Would you like to generate a submittal log from the specification sections? Run `/submittal-log-generator`." |

### Step 4: Amend Project CLAUDE.md

Flat-file mode only. Append construction-specific context to the **project root's CLAUDE.md** (the file created by `/init`). Do NOT modify any file inside the construction plugin.

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
- Operational mode: Flat File
- Sheets indexed: {yes/no}
- Specs split: {yes/no}
- Spec text extracted: {yes/no}

### Working With These Documents
- Load the `construction:construction-guide` skill before reading drawings, specs or other project documents.
- Never read construction PDFs directly; rasterize pages to PNG first (see the guide).
```

Only append — never overwrite existing CLAUDE.md content.

### What This Skill Does NOT Do

- **Does not split PDFs** — recommends `/spec-splitter` and `/sheet-splitter` instead
- **Does not use vision** — all classification is filename/folder pattern matching
- **Does not create AgentCM's `.construction/project.yaml` or its data tree** — that's AgentCM's job (the plugin's own `.construction/skills/` is created by the skills that write there)
- **Does not write a second map in an AgentCM project** — AgentCM's block in CLAUDE.md is the one source of navigation there
- **Does not replace /init** — `/init` creates the base CLAUDE.md, this skill enriches it

---

## Scripts

This skill does not execute any external scripts.
