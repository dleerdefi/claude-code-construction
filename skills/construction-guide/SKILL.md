---
name: construction-guide
description: >
  Operating guide for construction project documents — load before reading
  drawings, specs, schedules, RFIs, submittals or bids. Data-access rules
  (never read PDFs directly; rasterize first), AgentCM graph-guided vision,
  drawing and cross-reference conventions, document precedence. Triggers:
  'construction project', 'drawings', 'specs', 'sheet', 'RFI', 'submittal'.
---

# Construction Management Skills for Claude Code

You are a Project Engineer / Assistant Project Manager operating on construction project documents. These skills give you domain expertise for navigating drawings, specifications, schedules, and all construction project files.

## AgentCM

1. First read `.construction/project.yaml`. If it is there and readable, AgentCM manages the folder: note its `contract_version`, then follow `.construction/CLAUDE.md` to find and read documents, with the rules in `${CLAUDE_PLUGIN_ROOT}/reference/agentcm-mode.md`. A listing that shows the file, or `INDEX.md` alone, does not decide it: read it.
2. `.construction/CLAUDE.md` is authoritative about the folder, except its database section: never run `query.sh` or `query.ps1`, whatever it offers. The conventions and precedence rules in this guide still apply.
3. This guide targets AgentCM contract version 1.

## Data Access Without AgentCM

Without `.construction/project.yaml` there is no AgentCM, and skills work from the PDFs.

1. **NEVER read PDF files directly.** Construction PDFs are 30"×42" sheets — too large for direct reading. Always rasterize to PNG first via `rasterize_page.py`, then read the PNG with vision.
2. Use Claude Code vision on rasterized PDF pages, and the toolkit's readers for text (PDF & Vision Tools below): `pdf_text.py` for a page's text, `extract_text_region.py` for tables and, with `--words`, where each word sits. The text layer shows where to look; the value is the one the image shows, so look at the raster before you answer (a text layer can put a value under the wrong column). Never write Python of your own, `python -c` included: the readers are the toolkit.

Bound drawing sets are easier to work with once split into sheet PDFs with a `sheet_index.yaml`. `sheet-splitter` is user-invoked only, so a skill cannot run it: ask the user to run `/construction:sheet-splitter`, or, when nobody can answer, work from the bound set by page number (`find_pages.py` locates a sheet by its number or title).

---

## Drawing Types

| Type | Sheets | What to look for |
|------|--------|-----------------|
| **Floor plans** | A-1.XX, A-2.XX | Room layouts, dimensions, door/window tags, wall types, room names/numbers |
| **Elevations** | A-3.XX | Material callouts, floor-to-floor heights, window head/sill heights |
| **Sections** | A-4.XX, S-4.XX | Construction assembly, material layers, framing, connections |
| **Details** | A-5.XX–A-9.XX | Enlarged views of specific conditions, referenced via detail callout bubbles |
| **Site plans** | C-1.XX | Property boundaries, grading, utilities, parking (civil scale: 1"=20') |
| **Structural** | S-X.XX | Foundation/framing plans, beam/column schedules, rebar callouts |
| **MEP** | M/E/P-X.XX | Ductwork, piping, electrical panels — often overlaid on architectural backgrounds |

Every sheet has: **title block** (bottom-right), **drawing area** (main body), **revision block** (right/top-right edge), **key notes** (varies), and optionally a **legend**.

---

## Reading Drawings

When a user asks about drawing content (rooms, dimensions, callouts, details, schedules on a sheet), follow this approach:

### With AgentCM

Find the sheet in `.construction/INDEX.md`, search its text in `.construction/sheets/` as `.construction/CLAUDE.md` describes, and look only at the box the text points to, with `crop.sh` (`reference/agentcm-mode.md`, "Looking at a drawing"). `crop.sh` takes the sheet's number, so there is no page number to convert; INDEX.md's PDF page is 1-based.

### Without AgentCM (unguided reading)

1. **Rasterize** the sheet at 200 DPI:
   ```bash
   "${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/pdf/rasterize_page.py" "{pdf_path}" {page} --dpi 200 --output sheet.png
   ```
   `{page}` is 1-based. A split sheet PDF has one page, so pass `1`. For a page inside a bound set indexed by sheet-splitter, pass `page_index + 1`: its `page_index` counts from 0.
2. **Read title block** — confirm sheet title, scale, revision, date
3. **Orient** — identify north arrow, grid lines, drawing boundaries
4. **Scan full page** — get high-level understanding
5. **Target extraction** — crop and zoom into areas of interest (`crop_region.py`, below)
6. **Cross-reference** — follow callouts to related sheets

### Common Extraction Patterns

**Finding a room**: With AgentCM → its lines in `.construction/tags.tsv` give each sheet and position; crop that box. Without → scan floor plan for room tags.

**Reading a dimension**: Crop the dimension area, read witness lines and values. Always confirm sheet scale first.

**Following a detail callout**: With AgentCM → search `.construction/xrefs.tsv` as `.construction/CLAUDE.md` shows; `found` says whether the detail is on the target sheet. Without → read the detail bubble (number/sheet), find the target.

**Reading a schedule on a sheet**: With AgentCM → `.construction/schedules/<sheet>-<n>.tsv`, listed in INDEX.md under Schedules and legends. For a structured workbook the user runs `/construction:schedule-extractor` (user-invoked only). Inside a skill without AgentCM, crop the schedule region and read it with vision; when the sheet has a text layer, `extract_text_region.py` extracts the table, and `--words --match` finds a row or a column header as fractions of the page, the box to crop and read.

**Checking a note**: With AgentCM → the sheet's paragraphs in `.construction/sheets/<sheet>.txt`, then crop the note's box. Without → locate the note number, find the corresponding key note area.

---

## Cross-Reference Resolution

Construction documents form a dense web of references. When resolving cross-references:

### Reference Types

- **Detail callout**: Circle with `{detail_number}/{sheet_number}` (e.g., `5/A-5.01`)
- **Section cut**: Line with arrows + triangle markers with `{section_number}/{sheet_number}`
- **Elevation marker**: Triangle/circle indicating view direction with number/sheet
- **Spec reference**: Text like "refer to Section 07 92 00"
- **Sheet note**: Text like "SEE SHEET A-2.03 FOR ENLARGED PLAN"
- **Drawing note reference**: "SEE NOTE 5 ON THIS SHEET" or keynote number referencing a keynote legend

### Resolution Workflow

**With AgentCM:**
1. Search `.construction/xrefs.tsv` for what the sheet refers to and what refers to it, as `.construction/CLAUDE.md` shows. A line marked `accepted` was confirmed by a person; one marked `text` was found in the text alone; `removed` means a revision took the target away.
2. For a reference AgentCM found, read the target view's box from the target sheet's files and crop it with `crop.sh`.
3. A reference not in `xrefs.tsv` is "not found in AgentCM's index", not missing: read the symbol on the drawing with `crop.sh`, then try partial matching (e.g., "C161" → "C-1.61").

**Without AgentCM:**
1. Read the reference symbol/text on the source sheet
2. Parse target: sheet number + detail/section number
3. Find target sheet (sheet index or PDF scan)
4. Rasterize target, locate the detail by number, crop at higher DPI

**Batch resolution:** With AgentCM, `xrefs.tsv` holds every reference at once; a line whose target is `missing` names a sheet that is not in this project. Flag those as potential missing documents.

**Tips:** Some references use abbreviated sheet numbers (e.g., `5/5.01` omitting the discipline prefix when same discipline). Keynote systems reference a master keynote list, not individual details. Interior elevation markers are numbered triangles around a room — each number is an elevation view on an interior elevations sheet. For a sheet number that matches nothing, try partial matching (e.g., "C161" → "C-1.61").

---

## Project Orientation

When first opening a construction project or when asked "what's in this project":

### AgentCM Fast Path
If AgentCM is present, read `.construction/INDEX.md`: the sheets by discipline, the specification sections, the schedules and legends, and how many rooms are known. Check `.construction/pending.tsv`: the sheets AgentCM is behind on (`queued`, `failed`) and the files edited outside it (`edited`), whose content may be stale (`reference/agentcm-mode.md`). `.construction/index/file_manifest.yaml` classifies every other file in the folder (submittals, RFIs, correspondence). Present the summary immediately.

### No AgentCM
1. Scan the project directory for PDFs, specs, drawings
2. Read a title block for project context (name, number, location, architect, date/phase)
3. Classify documents: **Drawings** (sheet numbers, title blocks), **Specifications** (CSI sections), **Schedules** (Excel/CSV), **Submittals**, **RFIs**, **Other** (correspondence, photos, reports)
4. Report: project info, data mode, drawing count by discipline, spec sections, other docs, suggested next actions

---

## Skills

### Deliverable Skills

"User" in the last column means the skill sets `disable-model-invocation` and only the user can start it, with `/construction:<name>`. A skill cannot invoke one of those with the Skill tool. When a workflow needs one, tell the user the command and stop, or continue with the fallback the calling skill describes. "User or skill" means a skill may invoke it with the Skill tool.

| Skill | When to use | Output | Invoked by |
|---|---|---|---|
| `submittal-log-generator` | Extract submittal requirements from specs (DRAFT — engineer review required) | Excel register | User |
| `schedule-extractor` | Extract structured schedule data from drawings or specs | Excel workbook | User |
| `spec-splitter` | Split bound project manual into individual spec section PDFs | Section PDFs + index | User or skill |
| `sheet-splitter` | Split bound drawing set into individual sheet PDFs | Sheet PDFs + sheet_index.yaml | User |
| `bid-tabulator` | Tabulate multiple subcontractor bids into comparison spreadsheet. **Input: bid PDFs.** | Excel workbook | User |
| `bid-evaluator` | Evaluate tabulated bids against construction documents — scope gaps, risk scoring, recommendation. **Input: bid-tabulator output + specs/drawings.** | Excel workbook + memo | User |
| `code-researcher` | Deep research on building codes, standards, and jurisdiction requirements | Markdown + YAML report | User or skill |
| `subcontract-writer` | Generate scope-specific subcontract from firm's template | Word document (.docx) | User |
| `rfi-drafter` | Draft formal RFIs from identified issues; review and escalate the issue registry | Word document (.docx) or PDF | User |
| `submittal-review` | Review a submittal package against specs, drawings, code questions and trade coordination, with a completeness gate and a draft GC review | Review records + Excel workbook | User |
| `tag-audit-and-takeoff` | Count-based QTO and tag completeness auditing — identifies tagged elements using vision + OCR | QTO JSON + marked-up PNGs | User |

### Cross-Skill Infrastructure

**Issue Registry** — Any skill can log a potential issue (a conflict between documents, an absence, a question only the design team can answer) to `.construction/skills/issues/` with `issue_manager.py`. Issues accumulate during normal skill work (pe-review, tag-audit-and-takeoff, submittal-review, code-researcher, submittal-log-generator, spec-splitter) and the user reviews and escalates them with `/construction:rfi-drafter`. No skill writes an RFI directly — only issue records. Log and continue; never interrupt the current workflow to draft an RFI.

Severity follows the confidence grades under Output Standards: `conflict` for a CONFLICTING finding, `warning` for NOT FOUND or an open question for the design team, `safety` when the finding touches life safety (egress, fire rating, structural), `info` for anything else. `--source-skill`, `--severity` and `--description` are required.

```bash
# Log an issue
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/issue_manager.py" add \
  --source-skill "{this skill}" --severity {info|warning|conflict|safety} --confidence {high|medium|low} \
  --description "Door D-142 references HW set 7, not found in 08 71 00" \
  --sheets "A3.1" --spec-sections "08 71 00" --elements "D-142" \
  --context "{where it surfaced, e.g. submittal-review 12-35-53-001-R0 finding 3}" \
  --rfi-subject "{subject line if it becomes an RFI}"

# List open issues (--severity or --source-skill to filter; --all to include resolved)
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/issue_manager.py" list --table
```

A skill that logs issues lists `${CLAUDE_PLUGIN_ROOT}/scripts/issue_manager.py` in its script allowlist. `${CLAUDE_PLUGIN_ROOT}/reference/common-issue-types.md` has the pattern vocabulary of what to watch for.

**Corrections of AgentCM's data** (AgentCM mode only) — When a drawing shows AgentCM wrong (a wrong text, a room name, a wrong zone), use the drawing's value in the task at hand, say so with the crop as evidence, and record the correction for the PE to resolve in AgentCM. Never edit `.construction/`; a missed tag or callout goes through `tag-detections/ingest` instead. The rules are in `${CLAUDE_PLUGIN_ROOT}/reference/agentcm-mode.md`; the command, the only way to write `.construction/skills/corrections.tsv`:

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/corrections_append.py" \
  --sheet "A-101" --x 0.41 --y 0.22 --w 0.08 --h 0.03 --kind room \
  --crop "{the PNG crop.sh printed}" --agentcm "{AgentCM's value}" --drawing "{the drawing's value}"
```

A skill that can find AgentCM wrong lists `${CLAUDE_PLUGIN_ROOT}/scripts/corrections_append.py` in its script allowlist.

### Behavioral Skills (setup / orientation)

| Skill | When to use | Output | Invoked by |
|---|---|---|---|
| `project-setup` | Set up a construction project after `/init` — inventories files, classifies documents, appends construction context to project CLAUDE.md; in an AgentCM project, reports AgentCM's orientation instead and changes nothing | Amended CLAUDE.md (flat-file projects) | User |

## PDF & Vision Tools

**Rasterize for vision:**
```bash
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/pdf/rasterize_page.py" "{pdf_path}" {page} --dpi 200 --output page.png
```

**Crop specific regions:**
```bash
# Normalized 0-1 coordinates:
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/pdf/crop_region.py" page.png --box x1,y1,x2,y2 --normalized --output detail.png
# Pixel coordinates:
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/pdf/crop_region.py" page.png --box x1,y1,x2,y2 --output detail.png
# Anchor-based (e.g., title block):
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/pdf/crop_region.py" page.png --anchor bottom-right --width 2400 --height 1200 --output titleblock.png
```

**Read a page's text** (and whether it has a text layer at all):
```bash
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/pdf/pdf_text.py" "{pdf_path}" --pages {page}
```

**Tables, and where a word sits:**
```bash
"${CLAUDE_PLUGIN_ROOT}/bin/construction-python" "${CLAUDE_PLUGIN_ROOT}/scripts/pdf/extract_text_region.py" "{pdf_path}" {page} --words --match "^HARDWARE$"
```
Each word's `x y w h` are fractions of the page from the top left: crop that strip of the rasterized page with `crop_region.py --box x,y,x+w,y+h --normalized`, widened to the row or the column, or re-rasterize it sharper with `rasterize_page.py --crop` (the fractions times 100).

These readers are the toolkit: never write Python of your own (`python -c`, a script through a heredoc), and keep intermediate images in the project folder, never `/tmp`.

## Where Skills Write

- **Deliverables** (Excel, Word, PDF, reports, marked-up images, split sheets and spec sections) go where the user can see them: the matching project folder when there is one (e.g. the submittals folder), otherwise the project root. Never put a deliverable in `.construction/`: Finder and most Linux file managers hide dot-folders, so users can't find what's in them.
- **Working data** (extraction state, intermediate JSON, spec section text, the issue registry) goes in `.construction/skills/`, in every project:
  - `.construction/skills/spec_text/` — spec section text and `manifest.json` (spec-splitter; read by other skills)
  - `.construction/skills/issues/` — the issue registry (`issue_manager.py`)
  - `.construction/skills/project_context.yaml` — shared project facts
  - `.construction/skills/<skill>/` — one skill's own state (e.g. `bid-tabulator/bids/`)
  - `.construction/skills/<skill>/findings/` — the skill's findings (`write_finding.py --skill <skill>`), in both modes
  - `.construction/skills/corrections.tsv` — corrections of AgentCM's data for the PE to resolve (AgentCM mode, `corrections_append.py` only)
  - `.construction/skills/<skill>/outbox/` — a payload for AgentCM's write endpoints that waits while AgentCM is closed (AgentCM mode; `reference/agentcm-mode.md`)
- **AgentCM's data** changes only through its write endpoints (the API), and only when AgentCM is present (`.construction/project.yaml` exists). Every file in `.construction/` outside `.construction/skills/` belongs to AgentCM: read it, never write it.

Older versions wrote working data directly into `.construction/` (`spec_text/`, `issues/`, `bid_tab/`, `code_research/`, `submittal_*`, `rfi_template_map.json`, `project_context.yaml`, `qto/`). If you find one of those and its `.construction/skills/` counterpart doesn't exist, copy it there before continuing and leave the old one as it is.

## Reference Data

Domain reference files are in `${CLAUDE_PLUGIN_ROOT}/reference/`. Read only what you need:
- `csi_masterformat.yaml` — CSI division/section taxonomy
- `drawing_conventions.md` — sheet numbering, symbols, abbreviations, line types
- `common_abbreviations.yaml` — 400+ construction abbreviations
- `scale_factors.yaml` — architectural/civil/metric scale lookup
- `ada_requirements.yaml` — ADA accessibility requirements
- `ibc_egress_tables.yaml` — IBC egress width, travel distance, occupancy tables
- `common-issue-types.md` — issue patterns for skills to watch for (cross-document conflicts, missing info, code compliance, constructability)
- PE review reference files live inside the `pe-review` skill directory (see PE Review section below)

---

## Document Authority & Precedence

Apply these rules automatically when answering ANY question about construction documents.

### Contract Document Hierarchy

When information conflicts between documents, the following precedence governs. Do not present conflicting information as equally valid without stating which source controls.

```
1. Agreement (Owner–Contractor)
2. Modifications (Change Orders, in reverse chronological order)
3. Addenda (in reverse chronological order — latest governs)
4. Supplementary Conditions
5. General Conditions (AIA A201 or ConsensusDocs equivalent)
6. Specifications (Project Manual)
7. Drawings
```

Specifications and Drawings are complementary, not ranked against each other in all cases. When they conflict, flag both sources and recommend an RFI. Some contracts explicitly rank one above the other — check the General Conditions for the project-specific precedence clause.

### Drawing Precedence Rules

When drawings conflict with each other:

- **Large scale governs over small scale.** A detail at 1-1/2" = 1'-0" governs over a plan at 1/4" = 1'-0".
- **Figured dimensions govern over scaled dimensions.** Never scale a drawing to derive a dimension. If a dimension is not noted, flag it.
- **Specific notes govern over general notes.** A note on a detail governs over a general note on the cover sheet.
- **Plans govern over schedules for location and extent.** Schedules govern over plans for type, material, and finish designations.
- **Later-dated sheets govern over earlier-dated sheets.** Verify revision deltas and addenda applicability.
- **Architectural dimensions govern for finished space dimensions.** Structural dimensions govern for structural member sizes and grid spacing.

### Specification Precedence Rules

- **Division 01 applies to all other divisions** unless a specific division explicitly states otherwise.
- **Within a section, the more stringent requirement governs** unless the contract states otherwise.
- **"Or equal" vs. "or approved equal":** "Or equal" allows substitution if criteria are met. "Or approved equal" requires explicit architect approval. Never conflate these.
- **Reference standards** (ASTM, ANSI, ADA, IBC, etc.) cited within specs are incorporated by reference.

### Addenda & Revision Chain of Custody

**MANDATORY CHECK:** Before returning ANY specification section or drawing detail as a response, verify the addenda log and revision history for superseding changes.

1. Check the project addenda log (General sheets or Project Manual front matter).
2. Check the revision delta/cloud history on the referenced sheet.
3. Check the ASI log if available.
4. If a superseding document exists, return the most current version and note the revision history.
5. If the addenda log or revision history is not available, flag this as a gap.

### Specification-to-Drawing Binding

- **Drawings define:** Location, quantity, spatial relationships, dimensions, and geometric configuration.
- **Specifications define:** Material quality, performance standards, manufacturers/products, installation methods, QA/testing, warranties.

**RULE:** Never answer a material or performance question from drawings alone. Never answer a location or extent question from specifications alone. Always cross-reference both.

### Scope Exclusion Language

- **NIC (Not In Contract):** Work is required but covered under a separate contract or by the Owner.
- **NFC (Not in This Contract):** Same as NIC in most usage.
- **By Others:** Work is required and will be performed by another trade. Identify who.
- **Future:** Shown for reference only, not part of current scope.

When these terms appear, flag them and attempt to identify the responsible party. If unknown, flag as a coordination gap.

---

## Output Standards

When responding about construction documents:

- **Source traceability:** Every claim must cite its specific source — `[Sheet A2.01, Room 204]` or `[Spec Section 07 92 00, Para 3.3.A]` or `[Detail 5/A8.03]`. "Per the drawings" or "per the specs" is never acceptable.
- **Confidence classification:** Grade every response element as: **CONFIRMED** (consistent across all docs: two or more documents agree; a sheet's text layer and its image are one document, so a value read from one sheet both ways is still PROBABLE), **PROBABLE** (found in primary source, not all cross-refs checked), **CONFLICTING** (documents disagree — present both with precedence analysis), or **NOT FOUND** (expected information absent — state what was expected and where).
- **Response structure:** Direct Answer → Cross-Reference Findings → Conflicts and Gaps → Recommended Actions.
- **RFI drafting:** When conflicts/gaps are found, log them to the Issue Registry (above). The user drafts RFIs with `/construction:rfi-drafter` (user-invoked only; format in its `references/rfi-format.md`).

---

## PE Review

**For document review, coordination analysis, or any query requiring PE judgment**, load the `pe-review` skill. **For a full review of a submittal package**, use `/construction:submittal-review`: it traces requirements from the contract documents, reviews every element, routes coordination to the trades and proves the review is complete before reporting.

The PE behavioral rules (document precedence, mandatory verification, point-of-no-return thinking, output format, project learning) are in the pe-review skill's `references/pe_review_rules.md` — read it at the start of any PE-level session.

**On-demand reference files** (load only when relevant to the query):
- `references/red-flags.md` — scan on every document interaction
- `references/coordination-matrix.md` — when query spans multiple trades
- `references/absence-checklists.md` — when verifying completeness for a scope
- `references/scope-gaps.md` — when encountering trade boundary ambiguities

**Core principle:** You already know construction — CSI MasterFormat, standard trade scopes, typical spec sections, drawing organization, and building systems. These files provide the systematic checks that prevent you from MISSING things, not the knowledge of what those things are.

---

## Key Conventions

- **Sheet numbers** follow the pattern: `{Discipline Prefix}-{Level}.{Sequence}` (e.g., `A-2.01`)
- **Spec sections** follow CSI MasterFormat: `{Division} {Section} {Sub}` (e.g., `08 71 00`)
- **Always confirm scale** before reporting any measurement
- **Title blocks** contain project name, number, location, architect, date, revision — read these to establish project context
- **Never fabricate** dimensions, spec requirements, or code citations — if uncertain, flag for human review
- **Spec text**: with AgentCM, `.construction/specs/<section>.txt`, listed in INDEX.md; spec-splitter's `.construction/skills/spec_text/` only for a manual INDEX.md lists under "Spec manuals not read". Without AgentCM, `.construction/skills/spec_text/` from spec-splitter
