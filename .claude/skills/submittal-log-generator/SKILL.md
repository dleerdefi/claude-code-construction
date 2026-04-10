---
name: submittal-log-generator
description: >
  Extract all submittal requirements from specification sections and generate
  a comprehensive submittal register in Excel. Triggers: 'submittal log',
  'extract submittals', 'submittal register'. Requires /spec-splitter output.
argument-hint: "[spec_range: all|div_08|div_09]"
disable-model-invocation: true
---

# Submittal Log Generator

Long-running skill that processes every specification section to extract submittal requirements and produces a professional submittal register in Excel. Designed to handle full project manuals (200+ spec sections) with state persistence.

**Prerequisite:** This skill depends on `/spec-splitter` to provision clean, per-section `.txt` files at `.construction/spec_text/`. The spec-splitter owns all text quality — extraction, repair, and quality assessment. This skill reads those `.txt` files and focuses on identifying submittal items.

## Design Philosophy: Scripts for Structure, Claude for Judgment

This skill uses a three-tier approach:

- **RIGID** (scripted, deterministic): File I/O, Excel output schema, directory structure, naming conventions. Follow these exactly. Do not improvise.
- **GUIDED** (decision tree, Claude picks the branch): Confidence scoring, output location discovery. Follow the decision logic; adapt thresholds to what you observe.
- **FLEXIBLE** (domain knowledge, Claude thinks): Identifying what is actually a submittal item, distinguishing submittals from boilerplate, resolving ambiguity, handling non-standard spec formats. Use your understanding of construction documents and the domain knowledge below.

**Allowed scripts — exhaustive list.** Only execute these scripts during this skill:
- `export_submittal_log.py` — Excel output from assembled JSON (Step 4)
- `write_finding.py` — graph entry (Step 5)
Do not create, generate, or write any `.py`, `.sh`, or other script files. All data assembly is Claude writing JSON directly.

## Current Submittal State
!`cat .construction/submittal_extraction_state.yaml 2>/dev/null || echo "No prior extraction — starting fresh"`

---

## Output Schema — RIGID

The Excel submittal log MUST contain these columns in this order. Do not rename, reorder, or omit columns.

| Column | Description | Example |
|---|---|---|
| Spec Section | CSI section number | 03 30 00 |
| Spec Title | Section title | Cast-in-Place Concrete |
| Submittal No. | Sequential ID: `[Section]-[###]` | 03 30 00-001 |
| Submittal Type | Categorized type (see taxonomy below) | Product Data |
| Submittal Description | The actual submittal requirement, cleaned | Submit product data for each concrete mix design including compressive strength, admixtures, and mix proportions |
| Article Reference | Where found in the spec | 1.3.A.1 |
| Action/Informational | Action or Informational | Action |
| Confidence | HIGH / MEDIUM / LOW / FLAGGED | HIGH |
| Flag Reason | Empty if HIGH; explanation otherwise | Possible boilerplate — verify intent |
| Extraction Method | pdfplumber / vision / hybrid | pdfplumber |
| Notes | Any context Claude thinks the PE should know | Referenced mix designs in 03 31 00 |

### Formatting

Use the rigid export script for all Excel output. The script handles:
- Header row: Bold, dark background (RGB 44,62,80), white text, freeze panes
- Alternating row shading for readability
- Auto-filter on all columns
- Column widths sized to content (Submittal Description gets the widest)
- Conditional formatting on Confidence column: HIGH=green, MEDIUM=yellow, LOW=orange, FLAGGED=red
- Summary sheet with counts by section, type, and confidence level
- Extraction QA sheet with per-section quality metrics

---

## Workflow — RIGID Structure, GUIDED Decisions

```
Submittal Log Progress:
- [ ] Step 0: Ensure spec text is available (invoke /spec-splitter if needed)
- [ ] Step 1: Submittal identification (per section, Claude intelligence)
- [ ] Step 2: Confidence scoring & flagging
- [ ] Step 3: Assembly & deduplication
- [ ] Step 4: Excel output (rigid script)
- [ ] Step 5: Write graph entry
```

### Step 0: Ensure Spec Text Is Available — RIGID

This skill reads from `.construction/spec_text/*.txt` files provisioned by `/spec-splitter`. Check whether they exist and invoke spec-splitter if needed.

**Branch A — Text already extracted:**
1. Check `.construction/spec_text/manifest.json`
2. If present with corresponding `.txt` files → inventory them, build the processing queue, proceed to Step 1
3. Note any sections with `quality_rating: "POOR"` in the manifest — items extracted from these sections will receive a minimum confidence of MEDIUM

**Branch B — No text extracted:**
1. Invoke `/spec-splitter` — it will handle everything: locating or splitting spec PDFs, extracting text, and repairing quality issues
2. After `/spec-splitter` completes, read `.construction/spec_text/manifest.json` and proceed to Step 1

**Important:** Always invoke `/spec-splitter` as a skill — do not call `extract_spec_text.py` or `split_spec_manual.py` directly. The spec-splitter skill manages directory discovery, naming conventions, text extraction, and text repair.

**Build processing queue from manifest:**
1. Read all section keys from `manifest.json`
2. For each section, verify the corresponding `.txt` file exists
3. Sort by CSI section number
4. Build the queue

Initialize state file:
```yaml
# .construction/submittal_extraction_state.yaml
run_id: "uuid"
started: "ISO-8601"
status: "in_progress"
total_sections: 48
processed: 0
current_section: null
queue_remaining: ["03 30 00", "04 20 00", ...]
submittals_found: 0
errors: []
```

### Step 1: Submittal Identification — FLEXIBLE (Claude Intelligence)

For each section in the queue, read the `.txt` file from `.construction/spec_text/` and identify submittal items.

This is where your understanding of construction specifications matters most.
Do not follow a rigid script here — use the domain knowledge below to identify
every legitimate submittal requirement while filtering boilerplate.

#### Where Submittals Live

**Primary location** (check first):
- PART 1 - GENERAL
  - Article 1.3 ACTION SUBMITTALS
  - Article 1.4 INFORMATIONAL SUBMITTALS
  - Sometimes combined as Article 1.3 SUBMITTALS with sub-articles

**Secondary locations** (always check these too):
- PART 1 - GENERAL, other articles:
  - QUALITY ASSURANCE (may contain test report/certification submittals)
  - DESIGN CRITERIA (may contain design data/calculation submittals)
  - REGULATORY REQUIREMENTS (may contain permit/approval submittals)
  - CLOSEOUT SUBMITTALS (O&M manuals, warranties, as-builts)
- PART 2 - PRODUCTS:
  - Individual product articles sometimes contain submittal requirements
    embedded with product descriptions ("Submit manufacturer's data for...")
  - These are REAL submittals — do not skip them because they're in Part 2
- PART 3 - EXECUTION:
  - Field test reports, installation certifications
  - Mock-up submittals
  - Pre-installation meeting documentation

**Spec sections that are ENTIRELY about submittals:**
- 01 33 00 - Submittal Procedures: This defines the process, not individual
  submittals. Extract any specific submittal requirements it contains (like
  submittal schedule format requirements) but do not treat procedural
  instructions as submittal items.
- 01 78 00 - Closeout Submittals: This DOES contain real submittal items.
  Extract them all.

#### Submittal Type Taxonomy

Categorize every extracted item into one of these types. Use your judgment
for edge cases — the descriptions below are guidance, not rigid rules.

**Action Submittals** (require Architect/Engineer review and response):

| Type | What It Is | Signal Phrases |
|---|---|---|
| Shop Drawings | Contractor-prepared drawings showing fabrication/installation details | "shop drawings showing/indicating/detailing", "installation drawings" |
| Product Data | Manufacturer's published literature, cut sheets, specs | "product data for/including", "manufacturer's data", "technical data", "catalog data", "cut sheets" |
| Samples | Physical samples of materials, colors, finishes | "samples of/for", "color samples", "finish samples", "material samples", "sample panels", "mock-ups" |
| Design Data | Engineering calculations, analysis, design documentation | "design data", "structural calculations", "engineering analysis", "seismic calculations", "load calculations" |
| Test Reports | Results from testing performed on products/materials | "test reports", "laboratory test results", "fire test reports", "independent testing" |
| Certificates | Third-party certifications of products/installers | "certificates", "certification", "ICC-ES report", "UL listing", "FM approval", "installer certification" |
| Delegated Design | PE-stamped submittals for contractor-designed portions | "delegated design", "deferred submittal", "professional engineer stamp", "PE-sealed" |

**Informational Submittals** (for record, no formal review/approval):

| Type | What It Is | Signal Phrases |
|---|---|---|
| Manufacturer's Instructions | Installation/application instructions | "manufacturer's instructions", "installation instructions", "written instructions" |
| Manufacturer's Field Reports | Field service reports from manufacturer's rep | "manufacturer's field report", "field service report" |
| Qualification Statements | Installer/manufacturer qualification documentation | "qualification statements", "qualifications for/of", "experience list", "project references" |
| Warranty | Warranty documentation | "warranty", "special warranty", "manufacturer's warranty" |
| O&M Data | Operation and maintenance manuals | "operation and maintenance", "O&M manual", "maintenance data" |
| LEED Submittals | LEED/green building documentation | "LEED", "sustainable design", "environmental product declaration", "EPD", "HPD" |
| Record Documents | As-built drawings, record drawings | "record documents", "record drawings", "as-built", "as-constructed" |
| Schedule | Submittal schedule, progress schedule | "submittal schedule", "progress schedule" |

If an item doesn't clearly fit a type, use "Product Data" as the default
for action submittals and "Manufacturer's Instructions" as the default for
informational submittals, but add a note explaining the ambiguity.

#### Boilerplate vs. Real Submittals — CRITICAL

**This is the hardest judgment call in the entire skill.** Project Manuals
contain enormous amounts of text that sounds like it could be a submittal
requirement but isn't. Your job is to distinguish real, actionable submittal
requirements from procedural boilerplate.

**REAL submittal items have ALL of these characteristics:**
1. They specify a THING to be submitted (drawings, data, samples, reports)
2. They relate to a SPECIFIC product, system, or material in the spec
3. They create an OBLIGATION on the contractor ("submit", "provide", "furnish")

**BOILERPLATE has one or more of these characteristics:**
- Describes the submittal PROCESS, not a specific item
  - "Submit in accordance with Section 01 33 00"
  - "Submittals shall include Contractor's certification"
  - "Provide electronic submittals in PDF format"
- Is a GENERAL REQUIREMENT repeated across many sections verbatim
  - "Comply with requirements in Section 01 33 00"
  - "Submit under provisions of Section 01 33 00"
  - "Action Submittals: Submit the following"  (header, not item)
- References OTHER sections without adding a new requirement
  - "Refer to Section 09 91 00 for painting submittals"
  - "As specified in Division 01 requirements"
- Is a QUALIFIER on how to prepare submittals, not what to submit
  - "Include [x] copies of each submittal"
  - "Mark submittals with project name and spec section"
  - "Submit within 30 days of Notice to Proceed"

**THE CRITICAL RULE: When in doubt, INCLUDE the item and FLAG it.**

Never silently discard something that might be a real submittal. The cost
of a PE reviewing a flagged item for 10 seconds is infinitely lower than
the cost of missing a submittal entirely. Use the confidence/flagging
system described below.

### Step 2: Confidence Scoring & Flagging — GUIDED

Every extracted item gets a confidence score. This is the safety net that
lets Claude aggressively identify submittals without fear of false positives
polluting the final log.

#### Confidence Levels

**HIGH** — Clear, unambiguous submittal requirement
- Appears in a submittal article (1.3 or 1.4)
- Uses explicit submittal language ("Submit product data for...")
- References a specific product/system in the spec
- Flag Reason: (empty)

**MEDIUM** — Probable submittal, minor ambiguity
- Appears in a submittal article but language is slightly vague
- OR appears outside submittal articles but is clearly a submittal
- OR the source section had `quality_rating: "POOR"` or `"DEGRADED"` in the manifest
- Flag Reason: Describe the specific ambiguity
  - "Found in Part 2, not in submittal article"
  - "Source section had degraded text quality — verify wording"
  - "Vague language — may be general requirement"

**LOW** — Possible submittal, significant ambiguity
- Embedded in execution or product paragraphs without clear submittal language
- OR could be a cross-reference to another section's submittal
- OR uses passive voice that obscures whether it's a requirement
- Flag Reason: Describe why this needs PE review
  - "Passive voice — unclear if contractor obligation"
  - "May be a reference to Section XX XX XX submittals"
  - "Submittal type unclear — could be product data or shop drawings"

**FLAGGED** — Probably NOT a submittal but included for safety
- Likely boilerplate but contains submittal keywords
- OR is a process description that a reasonable person might read as a requirement
- OR is a submittal from a different section referenced here
- Flag Reason: Explain why this is probably not a submittal
  - "Appears to be procedural boilerplate — 'submit in accordance with 01 33 00'"
  - "Header text, not a submittal item"
  - "General qualification, not section-specific requirement"

#### Decision Matrix

```
Clear submittal language + in submittal article    → HIGH
Clear submittal language + NOT in submittal article → MEDIUM
Unclear language + in submittal article             → MEDIUM
Unclear language + NOT in submittal article          → LOW
Looks like boilerplate but has submittal keywords   → FLAGGED
Definitively boilerplate (headers, cross-refs)      → EXCLUDE (do not include)
```

Items scored FLAGGED are included in the log but should be visually
distinct (red conditional formatting) so the PE can quickly scan and
remove them. This is better than Claude guessing wrong.

**Things to EXCLUDE entirely (do not even flag):**
- Article headers and sub-headers ("ACTION SUBMITTALS:", "A. Product Data:")
  when they are just labels, not requirements
- "Submit in accordance with Section 01 33 00" (pure process reference)
- Page headers/footers, spec section identifiers
- "END OF SECTION" markers
- Table of contents entries

### Step 3: Assembly & Deduplication — GUIDED

Before writing to Excel:

1. **Sort** by Spec Section (numerical), then by Article Reference
2. **Deduplicate**: If the same submittal appears in multiple places
   (e.g., "submit product data for concrete" in both 03 30 00 and 03 31 00),
   keep both entries — they may be intentionally separate requirements.
   Only deduplicate if the EXACT same text appears in the SAME section.
3. **Cross-reference check**: If a submittal references another section
   ("as specified in Section 07 92 00"), note this in the Notes column.
   Do not attempt to resolve cross-references — that's the PE's job.
4. **Number sequentially**: Assign Submittal No. within each section
   (03 30 00-001, 03 30 00-002, etc.)

Write the assembled data to: `.construction/submittal_extraction_items.json`

This JSON file is the data contract between Claude's intelligence and the rigid export script. Schema:
```json
{
  "project_info": {
    "project_name": "...",
    "project_number": "...",
    "owner": "...",
    "extracted_date": "ISO-8601"
  },
  "submittal_items": [
    {
      "spec_section": "03 30 00",
      "spec_title": "Cast-in-Place Concrete",
      "submittal_no": "03 30 00-001",
      "submittal_type": "Product Data",
      "description": "...",
      "article_ref": "1.3.A",
      "action_informational": "Action",
      "confidence": "HIGH",
      "flag_reason": "",
      "extraction_method": "pdfplumber",
      "notes": ""
    }
  ],
  "qa_sections": [
    {
      "spec_section": "03 30 00",
      "spec_title": "Cast-in-Place Concrete",
      "extraction_method": "pdfplumber",
      "quality_rating": "GOOD",
      "failure_modes": "None",
      "repair_attempted": "N",
      "items_extracted": 4,
      "flagged_items": 0
    }
  ]
}
```

**Assembly rules:**
- Write `submittal_extraction_items.json` yourself — you have the schema above, write the JSON directly.
- If you parallelized via batch files, merge them with `jq` (see Per-Section Processing Pattern) — do not write a Python script to merge.
- The only scripts you execute are `export_submittal_log.py` (Step 4) and `write_finding.py` (Step 5).

### Step 4: Excel Output — RIGID

Discover the output location before running the export script:

1. Search for an existing Submittals directory (case-insensitive): `06 - Submittals/`, `Submittals/`, or similar
2. If found → `--output "{submittals_dir}/Submittal_Log.xlsx"`
3. If not found → `--output "Submittal_Log.xlsx"` (project root)

```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python \
  ${CLAUDE_SKILL_DIR}/scripts/export_submittal_log.py \
  --data ".construction/submittal_extraction_items.json" \
  --output "{resolved_output_path}"
```

The script produces three sheets:
- **Sheet 1: "Submittal Log"** — All items, formatted per the schema
- **Sheet 2: "Summary"** — Pivot-style summary: count by section, type, confidence level, extraction method
- **Sheet 3: "Extraction QA"** — One row per spec section with quality metrics

The script uses `safe_output_path()` — if a file already exists at the target location, it auto-versions (e.g., `Submittal_Log_v2.xlsx`).

### Step 5: Write Graph Entry — RIGID

```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/../../scripts/graph/write_finding.py \
  --type "submittal_log_generated" \
  --title "Submittal register: {N} items from {M} spec sections" \
  --output-file "{resolved_output_path}" \
  --data '{"total_submittals": 142, "sections_parsed": 48, "by_type": {"Product Data": 55, "Shop Drawings": 30}}'
```

Update state file:
```yaml
status: "complete"
completed: "ISO-8601"
submittals_found: 142
output_file: "{resolved_output_path}"
```

### Per-Section Processing Pattern — RIGID

The accumulator is `.construction/submittal_extraction_items.json`. Claude writes this file directly as JSON — no scripts, no intermediate tooling.

**Sequential processing:**
For each section in the queue, perform Steps 1-2 as a unit:
1. Read `.txt` from `.construction/spec_text/`
2. Check `quality_rating` in manifest — if POOR or DEGRADED, minimum confidence = MEDIUM
3. Identify submittals (Step 1)
4. Score confidence (Step 2)
5. Append extracted items to your in-memory accumulator (the JSON array you are building)
6. Update state file (increment processed, update queue_remaining)
7. **Compact**: Release the section text from context. Only carry forward the state file path, running item count, and next section in queue.

**Parallel processing (recommended for 60+ sections):**
Sub-agents can process section batches simultaneously. Each agent MUST write its results directly to a numbered batch file on disk:
- `.construction/submittal_batch_{NN}.json` — a bare JSON array of submittal items (no wrapper)
- After all agents complete, merge batches with a single inline command:
  `jq -s 'add' .construction/submittal_batch_*.json > .construction/submittal_items_merged.json`
- Then wrap with `project_info` and `qa_sections` to produce the final `submittal_extraction_items.json`

**Anti-pattern — never do this:** Do not have agents return JSON in their response text and then parse it from conversation logs (JSONL). This is fragile and leads to data corruption. If an agent's batch file is missing, re-run that agent.

After all sections are processed, write the final `submittal_extraction_items.json` per the schema in Step 3.

---

## Resumption

Check for `.construction/submittal_extraction_state.yaml`. If `status: in_progress`, resume from `queue_remaining`. Load previously extracted items from `.construction/submittal_extraction_items.json`.

---

## Quality Validation and Review

After generating the register, perform a review pass before presenting to the engineer:

### Content Review
Read each item and assess whether it describes an **actual deliverable** or a **procedural instruction**:
- **Keep**: Product data, shop drawings, samples, test reports, certificates, warranties, LEED documentation, O&M manuals — these are real submittal items
- **Flag for review**: Cross-references to other sections, descriptions of the submittal process itself, general administrative language — add flag reason: "Appears to be a procedural reference — recommend removal"

### Present Findings
Tell the engineer: "I generated a submittal register with [N] items from [M] spec sections. [Y] items appear to be procedural references rather than submittal requirements — these are flagged. Would you like to review the flagged items?"

The engineer makes the final decision on what to keep or remove.

### Sanity Checks
- Total count sanity: 3-8 submittals per spec section is typical
- Full institutional project: 250-1000 total submittal items

---

## Error Handling

- **No spec text available and /spec-splitter fails**: Notify the user. Cannot proceed without per-section text.
- **Missing TOC / unbookmarked PDF**: `/spec-splitter` handles this — it detects section title pages via pattern matching.
- **Encrypted PDF**: Notify the user. Cannot proceed without the password.
- **Empty sections**: Some specs have sections with "NOT USED" or similar. Log these in the QA sheet but produce no submittal items.
- **Non-English specs**: Flag and notify user. This skill assumes English-language specifications.

---

## What This Skill Does NOT Do

- Does not extract or repair spec text — that is `/spec-splitter`'s responsibility
- Does not split combined PDFs into per-section files — that is `/spec-splitter`'s responsibility
- Does not assign submittal status (approved, rejected, revise & resubmit)
- Does not populate contractor/vendor/manufacturer fields
- Does not create a transmittal or submission package
- Does not validate submittals against 01 33 00 requirements
- Does not replace PE review — the flagging system is designed to SUPPORT human review, not eliminate it
- Does not require custom scripts — all data assembly is Claude writing JSON directly; only `export_submittal_log.py` and `write_finding.py` are executed

## File Safety
Never overwrite an existing submittal log. The export script uses `safe_output_path()` which appends `_v2`, `_v3`, etc. automatically.

---

## Example: What Good Output Looks Like

For a spec section 07 92 00 - Joint Sealants that contains:

```
1.3 ACTION SUBMITTALS

A. Product Data: For each joint-sealant product indicated.

B. Samples for Initial Selection: For each type of joint sealant
   and for each color required.

C. Joint-Sealant Schedule: Include the following information:
   1. Joint identification number for each joint indicated.
   2. Joint-sealant product for each joint.
   3. Joint-sealant color for each joint.

1.4 INFORMATIONAL SUBMITTALS

A. Qualification Data: For Installer.

B. Product test reports.
```

The output should be:

| Spec Section | Submittal No. | Submittal Type | Submittal Description | Article Ref | A/I | Confidence |
|---|---|---|---|---|---|---|
| 07 92 00 | 07 92 00-001 | Product Data | Product data for each joint-sealant product indicated | 1.3.A | Action | HIGH |
| 07 92 00 | 07 92 00-002 | Samples | Samples for initial selection for each type of joint sealant and for each color required | 1.3.B | Action | HIGH |
| 07 92 00 | 07 92 00-003 | Schedule | Joint-sealant schedule including joint identification number, joint-sealant product, and joint-sealant color for each joint | 1.3.C | Action | HIGH |
| 07 92 00 | 07 92 00-004 | Qualification Statements | Qualification data for installer | 1.4.A | Informational | HIGH |
| 07 92 00 | 07 92 00-005 | Test Reports | Product test reports | 1.4.B | Informational | HIGH |

Note: The sub-items under 1.3.C (1, 2, 3) are rolled into the parent
submittal item's description. They describe what the schedule includes,
not separate submittals. Use judgment for this — sometimes numbered
sub-items ARE separate submittals (especially when each starts with
"Submit..." or describes a different product/system).
