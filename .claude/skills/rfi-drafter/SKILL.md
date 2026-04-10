---
name: rfi-drafter
description: >
  Draft RFIs and manage the ambient issue registry. Reviews issues surfaced
  by other skills, escalates to formal RFIs. Triggers: 'draft RFI', 'write
  RFI', 'drawing conflict', 'review issues', 'issue queue'.
allowed-tools:
  - Bash(${CLAUDE_SKILL_DIR}/scripts/rfi_export.py *)
  - Bash(${CLAUDE_SKILL_DIR}/../../scripts/issue_manager.py *)
  - Bash(${CLAUDE_SKILL_DIR}/../../scripts/rfi/generate_rfi_pdf.py *)
  - Bash(${CLAUDE_SKILL_DIR}/../../scripts/pdf/rasterize_page.py *)
  - Bash(${CLAUDE_SKILL_DIR}/../../scripts/pdf/crop_region.py *)
---

# RFI Drafter

## Purpose

Two responsibilities: (1) draft formal RFIs from identified issues, and
(2) manage the issue detection registry where potential problems surface
during other skill workflows. Detection is ambient. Drafting is user-
triggered. No RFI is ever created without explicit user instruction.

**Design**: RIGID output format and quality checks. GUIDED research
sequence before drafting. FLEXIBLE across any trade, CSI division, or
document conflict type.

Does NOT: autonomously discover issues and write RFIs, send RFIs
without user review, or determine whether an issue is actually an
error vs. intentional design.

## Permitted Scripts

| Script | Location | Purpose |
|--------|----------|---------|
| `rfi_export.py` | `${CLAUDE_SKILL_DIR}/scripts/rfi_export.py` | Populate firm's .docx template or generate generic RFI |
| `issue_manager.py` | `${CLAUDE_SKILL_DIR}/../../scripts/issue_manager.py` | CRUD for issue registry (.construction/issues/) |
| `generate_rfi_pdf.py` | `${CLAUDE_SKILL_DIR}/../../scripts/rfi/generate_rfi_pdf.py` | Generate PDF RFI (alternative format) |
| `rasterize_page.py` | `${CLAUDE_SKILL_DIR}/../../scripts/pdf/rasterize_page.py` | Rasterize drawing pages for vision reading |
| `crop_region.py` | `${CLAUDE_SKILL_DIR}/../../scripts/pdf/crop_region.py` | Crop regions for targeted reading |

Do NOT create custom scripts during execution. All output goes through the scripts above.

---

## Mode 1: User-Initiated RFI Drafting

The user identifies an issue and instructs Claude to draft an RFI.
This is the primary workflow — a 30-minute task compressed to minutes.

### Step 0: Gather RFI Template (first RFI per project)

Before the first RFI, ask the user for their firm's RFI form template.
Construction teams have a branded template they use for all official
RFIs — the output MUST match their format exactly.

**If .docx template provided:**
1. Read with python-docx to identify field locations (table cells,
   placeholders like `[PROJECT NAME]`, content controls)
2. Build a field mapping JSON linking each RFI data field to its
   location in the template
3. Store mapping at `.construction/rfi_template_map.json`
4. Store a SHA-256 hash of the template for change detection

**If PDF template provided:**
1. Rasterize each page at 200 DPI
2. Read with vision to understand field layout and structure
3. Build the mapping JSON from visual analysis
4. Store at `.construction/rfi_template_map.json`

**If no template available:**
Fall back to the generic format built into `rfi_export.py`. Inform
the user that providing their template is recommended for production
RFIs.

On subsequent RFIs, reuse the stored mapping. If the template file
hash differs from the stored hash, re-map.

### Step 1: Understand the Issue

Gather from the user (or from an issue registry record if escalating):
- **What**: the conflict, ambiguity, or missing information
- **Where**: sheet number(s), grid location, room/area, detail ref
- **Between what**: which documents disagree (plan vs detail, arch vs
  structural, drawing vs spec, etc.)

If the user's description is vague, ask clarifying questions. Never
draft from ambiguous input — an RFI that doesn't clearly state the
problem wastes everyone's time.

### Step 2: Research Context

Before drafting, systematically gather evidence. Read
`references/research-checklist.md` for the full checklist.

**Minimum research before any RFI:**
1. Read the specific area on the source sheet(s)
2. Check related details/sections for the same condition
3. Check the relevant spec section for requirements
4. Check if general notes address the condition
5. Check addenda and ASIs for superseding changes
6. Check existing RFI log for duplicates (if available)

If AgentCM data is available (`.construction/` exists), query the
database for cross-references to the affected area. See
`references/research-checklist.md` for concrete query examples.

If research reveals the issue is already resolved (by addendum, ASI,
or existing RFI response), inform the user — no RFI needed.

### Step 3: Draft the RFI

Use the format in `references/rfi-format.md`. Every RFI must include:
- Project identification (name, number, RFI number)
- Addressee (the design professional who owns the document)
- Specific drawing/spec references with grid locations
- Clear description of the issue
- Suggested resolution (always — accelerates response)
- Schedule impact statement
- Attachment list

Read `references/rfi-format.md` for the full template, field-by-field
guidance, and an example RFI.

### Step 4: Quality Check

Before presenting to user, verify against the checklist in
`references/quality-checks.md`. Key gates:
- Specific sheet numbers and grid locations cited (never "the plan")
- Issue clearly described (a stranger could understand it)
- Suggested resolution provided
- Schedule impact stated with a needed-by date
- Spec section referenced if applicable
- No duplicate of an existing RFI
- Addressee is the correct design professional for this scope

### Step 5: Present for Review

Present the draft RFI to the user in conversation. The user may:
- **Approve and export** — populate their template and generate .docx
- **Edit and refine** — iterate on language, add context
- **Reject** — issue isn't actually an issue
- **Defer** — log it back to the issue registry for later

**On export**, write the RFI data to a JSON file, then invoke:
```bash
# Template mode (preferred — matches firm's format):
python ${CLAUDE_SKILL_DIR}/scripts/rfi_export.py \
  --template path/to/firm_rfi_form.docx \
  --mapping .construction/rfi_template_map.json \
  --data rfi_draft.json \
  --output RFI-026.docx

# Generic mode (fallback — no template):
python ${CLAUDE_SKILL_DIR}/scripts/rfi_export.py \
  --data rfi_draft.json \
  --output RFI-026.docx
```

Output is always .docx so the user can make final edits before sending.
The script uses `safe_output_path()` — never overwrites existing files.

---

## Mode 2: Issue Detection Registry

Other skills (tag-audit-and-takeoff, pe-review, spec-parser, etc.)
surface potential issues during their normal work. These issues
accumulate in `.construction/issues/` as JSON records, NOT as RFIs.

### How Issues Get Created

Any skill can write an issue record. Read `references/issue-schema.md`
for the full schema. An issue record contains:
- Source skill that found it
- Severity (info / warning / conflict / safety)
- Description of what was observed
- Affected sheets, spec sections, elements
- Confidence level
- Timestamp

**Critical rule: no skill writes an RFI directly.** Skills write
issue records. The user reviews the queue. The user decides which
issues become RFIs.

### Reviewing the Issue Queue

When the user asks to review issues ("check the issues list", "what
issues have been found", "any problems detected"):

1. Load issues from `.construction/issues/`
2. Sort by severity (safety > conflict > warning > info), then
   by confidence (high > medium > low)
3. Present a summary table: severity, source skill, description,
   affected sheets, confidence
4. For each issue the user wants to escalate: switch to Mode 1
   drafting with the issue record as input context

```bash
# List all open issues (sorted by severity, then confidence)
python ${CLAUDE_SKILL_DIR}/../../scripts/issue_manager.py list

# List with human-readable table format
python ${CLAUDE_SKILL_DIR}/../../scripts/issue_manager.py list --table

# Filter by severity or source skill
python ${CLAUDE_SKILL_DIR}/../../scripts/issue_manager.py list --severity conflict
python ${CLAUDE_SKILL_DIR}/../../scripts/issue_manager.py list --source-skill "pe-review"

# Get a specific issue
python ${CLAUDE_SKILL_DIR}/../../scripts/issue_manager.py get --id ISS-2026-0001

# Escalate an issue to RFI
python ${CLAUDE_SKILL_DIR}/../../scripts/issue_manager.py update \
  --id ISS-2026-0001 --status escalated --rfi-number RFI-026

# Summary statistics
python ${CLAUDE_SKILL_DIR}/../../scripts/issue_manager.py stats
```

### Writing Issues from Other Skills

If you are running a skill OTHER than rfi-drafter and you notice a
potential issue (schedule conflict, missing reference, spec/drawing
mismatch), write it to the registry:

```bash
python ${CLAUDE_SKILL_DIR}/../../scripts/issue_manager.py add \
  --source-skill "tag-audit-and-takeoff" \
  --severity "warning" \
  --description "Door D-142 references HW set 7, not found in 08 71 00" \
  --sheets "A3.1" \
  --spec-sections "08 71 00" \
  --confidence "medium"
```

Do NOT interrupt the current workflow to draft an RFI. Log and continue.

See `references/common-issue-types.md` for the pattern vocabulary of
what to watch for across skills.

---

## Output

**RFI documents** are produced as Word (.docx) via `scripts/rfi_export.py`.
Two modes:
- **Template mode** (default): Clones the firm's .docx template and
  populates fields per the stored mapping. Output matches the firm's
  branded format exactly.
- **Generic mode** (fallback): Builds a standard RFI from scratch
  when no template is available.

Output is always .docx — the user must be able to edit before sending.
Read `references/rfi-format.md` for field-by-field content guidance.

**Template mapping** is stored at `.construction/rfi_template_map.json`.
Created on first RFI, reused for all subsequent RFIs in the project.

**Issue records** are JSON files in `.construction/issues/`.
Managed via `../../scripts/issue_manager.py`.
