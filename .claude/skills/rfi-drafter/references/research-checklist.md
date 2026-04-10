# Research Checklist — Pre-Draft Investigation

## Purpose

Every RFI must be backed by research. An RFI that asks a question
already answered by the documents wastes the design team's time and
damages the GC's credibility. This checklist ensures systematic
investigation before any draft is written.

## Mandatory Checks (every RFI)

### 1. Primary Source Review
- Read the specific area on the source sheet at the identified location

**With AgentCM** (`.construction/` exists):
```bash
# Read database.yaml for query_command, then:
{query_command} -c "SELECT * FROM v_sheet_contents WHERE sheet_number = '{sheet}'"
# Rasterize + crop to the conflict zone for vision reading:
python ${CLAUDE_SKILL_DIR}/../../scripts/pdf/rasterize_page.py "{pdf}" {page} --dpi 200 --output /tmp/page.png
python ${CLAUDE_SKILL_DIR}/../../scripts/pdf/crop_region.py /tmp/page.png --box x1,y1,x2,y2 --normalized --output /tmp/conflict_area.png
```

**Without AgentCM**:
- Rasterize the source sheet at 200 DPI, crop to conflict area, read with vision
- Read title block for revision date and project info

### 2. Related Views
- Check all details, sections, and elevations that reference or are
  referenced from the conflict area
- Large-scale drawings govern small-scale — if a detail shows
  different info than the plan, note which governs

**With AgentCM**:
```bash
{query_command} -c "SELECT * FROM v_cross_references WHERE source_sheet = '{sheet}' OR dest_sheet = '{sheet}'"
```

**Without AgentCM**:
- Search the source sheet visually for detail callouts, section marks, and elevation markers
- Rasterize each referenced sheet and read the referenced view

### 3. Specification Review
- Identify the relevant spec section(s) for the scope in question
- Check Part 1 (General), Part 2 (Products), and Part 3 (Execution)
  for any language addressing the condition
- Check Division 01 general requirements for any overriding provisions

**With AgentCM**: Check `.construction/index/file_manifest.yaml` for spec files, or query spec text if extracted.

**Without AgentCM**: Search the project directory for spec PDFs. Use pdfplumber to extract text from relevant sections.

### 4. Addenda and ASI Check
- Review all addenda issued after the original drawing date
- Check if any ASI (Architect's Supplemental Instruction) addresses
  this condition
- If an addendum supersedes the drawing/spec in question, the issue
  may already be resolved — inform the user, no RFI needed

**With AgentCM**: Query `file_manifest.yaml` for `type: addendum` or `type: asi` files.

**Without AgentCM**: Search the project directory for addenda/ASI documents. Read title pages for affected sheets/sections.

### 5. General Notes Review
- Check the general notes sheet(s) for the relevant discipline
- Many apparent conflicts are addressed by general notes that
  establish default conditions or clarify conventions

**With AgentCM**:
```bash
{query_command} -c "SELECT sheet_number, sheet_title FROM sheets WHERE project_id = '{id}' AND sheet_title ILIKE '%general%note%'"
```

**Without AgentCM**: Check `.01` sheets for each discipline (e.g., A-0.01, S-0.01, M-0.01) — these typically contain general notes.

### 6. Existing RFI Check
- If an RFI log is available, search for existing RFIs addressing
  the same condition, area, or spec section
- If a prior RFI response resolves this issue, inform the user
  and reference the prior RFI number
- If a prior RFI is related but doesn't fully resolve, reference
  it in the new RFI

**With AgentCM**: Query `file_manifest.yaml` for `type: rfi` files. Also check the issue registry:
```bash
python ${CLAUDE_SKILL_DIR}/../../scripts/issue_manager.py list --table
```

**Without AgentCM**: Search the project directory for RFI logs (Excel/PDF). Ask the user if an RFI log exists.

## Conditional Checks (when applicable)

### 7. Cross-Discipline Check
When the issue spans multiple disciplines:
- Pull the same area on each discipline's drawings
- Note discrepancies in dimensions, element locations, or clearances
- Identify which discipline's drawing likely governs

### 8. Code Check
When the issue may involve building code compliance:
- Identify the applicable code section (IBC, ADA, NFPA, local)
- State the code requirement alongside the drawing condition
- Do NOT assert a code violation — frame as "appears to conflict
  with [code section], please clarify"

### 9. Manufacturer Data Check
When the issue involves product compatibility or installation:
- Check submitted/approved product data if available
- Reference manufacturer's published installation requirements
- Note if the specified product can physically accommodate the
  shown condition

### 10. Schedule Cross-Reference
When the issue relates to quantities or locations:
- Check the relevant schedule (door, fixture, finish, equipment)
- Note any discrepancies between schedule data and drawing
- Schedules often contain notes that clarify apparent conflicts

## Research Outcome Decision

After completing research, one of three outcomes:

**Issue confirmed** → Proceed to draft. Document all research
findings as evidence in the RFI description.

**Issue resolved by existing document** → Inform the user which
document resolves it (addendum #, RFI response #, general note).
No RFI needed. Optionally log as resolved issue in registry.

**Issue unclear** → Present findings to user. The user may still
want to draft an RFI for clarification even if the evidence is
ambiguous — that's their judgment call.
