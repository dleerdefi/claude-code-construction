---
name: code-researcher
description: "Scope-specific code gap analysis for engineers and architects — extracts referenced codes, researches what should apply, surfaces the delta. Triggers on 'code research', 'what codes apply', 'am I missing any requirements', 'code check', 'ADA requirements', 'egress', 'fire code', 'code gap analysis'. Use when an engineer or architect wants to know if they are missing any code requirements for a specific scope of work. Does not trigger for general code questions without a project scope. Output: structured gap report with confidence levels and direct references to plans and specs."
argument-hint: "<scope_or_question> e.g. 'Section 09 67 23 resinous flooring' or 'egress from the kitchen complex'"
---

# Code Researcher — Scope-Specific Gap Analysis

## What This Skill Does

An engineer managing one or more scopes asks: *"Are there any code requirements
for this scope that I'm missing?"*

This skill answers that question in three passes:

**Pass 1 — What the scope already addresses**
Read the actual project documents — spec sections, drawings, schedules — and
extract every code citation, standard reference, and requirement already
incorporated by the design team.

**Pass 2 — What should apply**
Research all codes and standards that apply to this type of work in this
jurisdiction, regardless of what the project documents say.

**Pass 3 — The gap**
Diff Pass 1 against Pass 2. Present only what's in Pass 2 but absent from
Pass 1, with confidence levels and specific source citations from both the
code and the project documents.

**This is a gap finder, not a code summary.** If the spec already addresses a
requirement correctly, it does not appear in the output. The engineer's time is
spent only on things that may actually be missing.

---

## Framing Rule (Non-Negotiable)

Every finding is framed as:
> *"Code [X] requires [Y]. The project documents [address this at / do not
> appear to address this]. Confidence: [level]. Recommended action: [action]."*

Never frame findings as COMPLIANT / NON-COMPLIANT. The licensed design
professional makes compliance determinations. This skill provides research.

---

## Research Philosophy

This skill uses a document-grounded research approach:
- **Construction documents are ground truth.** Every claim about what the project does or does not address must trace to a specific document read in Pass 1. Never infer project status from memory or assumption.
- **Claude's domain knowledge drives topic discovery.** Use your training knowledge of construction codes, standards, and regulatory frameworks to identify what requirements SHOULD apply to this scope. The documents tell you what IS addressed; your knowledge tells you what to check for.
- **Web research confirms jurisdiction-specific requirements.** Building codes vary by jurisdiction and edition. Use web search to confirm which edition is adopted, retrieve exact code language, and discover jurisdiction-specific overlays. Do not rely on training knowledge alone for specific code section numbers or thresholds — verify via web.
- **Reference files verify numeric thresholds.** Shared reference files at `${CLAUDE_SKILL_DIR}/../../reference/` contain structured ADA and IBC data useful for quick verification of specific dimensions and capacities during research.

---

## Workflow Overview

```
Phase 1 — Context and Scope Definition
  1a  Gather project context (jurisdiction, occupancy, construction type)
  1b  Define the research scope (which spec sections, which question)
  1c  USER CHECKPOINT — confirm scope before any research begins

Phase 2 — Project Document Extraction (Pass 1)
  2a  Read all project documents in scope
  2b  Extract every code citation, standard reference, requirement
  2c  Build the "already addressed" inventory

Phase 3 — Code Research (Pass 2)
  3a  Research jurisdiction and adopted code editions
  3b  Research applicable requirements for this scope and work type
  3c  USER CHECKPOINT — interim findings, confirm continuation

Phase 4 — Gap Analysis (Pass 3)
  4a  Diff research findings against project document inventory
  4b  Classify each gap by severity and confidence
  4c  USER CHECKPOINT — review gaps before report is written

Phase 5 — Report
  5a  Generate structured gap report
  5b  Write graph entry
```

**Human checkpoints at 1c, 3c, and 4c.** Do not skip them.

---

## Phase 1 — Context and Scope Definition

### 1a — Gather Project Context

Collect minimum required project parameters. Check in this order:

**AgentCM project files (if `.construction/` exists):**
- `.construction/project.yaml` — location, occupancy, construction type
- `.construction/index/sheet_index.yaml` — drawing set composition
- `.construction/graph/navigation_graph.json` — rooms, elements

**Project documents (read directly):**
- Architectural title block — project name, location, jurisdiction
- Spec Section 01 10 00 (Summary of Work) — occupancy, construction type,
  project description
- Spec Section 01 40 00 (Quality Requirements) — codes the design team has
  already identified as applicable
- Spec Section 01 35 13 or 01 35 14 — special project requirements, authority
  having jurisdiction contacts

Minimum required context — write to `.construction/code_research/project_context.yaml` using the schema at:
→ `${CLAUDE_SKILL_DIR}/references/schemas.yaml` § project_context

If any required field cannot be found in the documents, ask the user before
proceeding. Do not assume occupancy group or construction type — these
determine which code provisions apply and an incorrect assumption cascades
through the entire analysis.

### 1b — Define the Research Scope

Parse the user's question to identify:

1. **Target scope** — which spec sections, drawing sheets, systems, or elements
   the engineer wants checked. Examples:
   - A spec section: "Section 09 67 23 Resinous Flooring"
   - A system: "all egress paths from the kitchen complex"
   - A trade package: "mechanical scope, Sections 23 00 00 through 23 80 00"
   - A code topic: "accessibility requirements for the toilet rooms"

2. **Research question** — what specifically the engineer is worried about.
   Examples:
   - "Am I missing any code requirements?"
   - "Does the spec cover the slip resistance requirements?"
   - "Are there fire separation requirements I haven't addressed?"

3. **Scopes in scope** — if the engineer is managing multiple scopes (e.g.,
   scopes A through C), confirm which ones this research covers.

Write to `.construction/code_research/scope_definition.yaml` using the schema at:
→ `${CLAUDE_SKILL_DIR}/references/schemas.yaml` § scope_definition

Research topics are generated from the combination of:
- The work type (resinous flooring → surface profile requirements, slip
  resistance, chemical resistance, substrate preparation)
- The occupancy group (kitchen/food service → USDA/FDA/health department overlay)
- The project type (renovation → existing conditions, special inspections)
- The question framing (gap analysis → broader research than targeted check)

**Use your full domain knowledge** to identify research topics. You know what
code requirements typically apply to each type of construction work, which
regulatory authorities have jurisdiction, and what gaps commonly appear in
specifications. The project documents tell you what the engineer has already
addressed — your job is to identify everything they should have considered.

### 1c — USER CHECKPOINT: Confirm Scope

Present to the user:

```
I have enough context to start. Before I begin research, here's what I'm planning:

PROJECT
  Name:          [project_name]
  Location:      [city, state]
  Occupancy:     [group]
  Type:          [construction type]
  Sprinklered:   [yes/no/unknown]
  Code year:     [inferred from drawing date]

SCOPE I'LL RESEARCH
  Spec sections: [list]
  Sheets:        [list, or "none specified — I'll search for relevant sheets"]
  Your question: [restated in plain language]

RESEARCH TOPICS I'VE IDENTIFIED
  1. [topic] — because [reason derived from scope]
  2. [topic] — because [reason derived from scope]
  3. [topic] — because [reason derived from scope]
  [...]

TOPICS I'M NOT INCLUDING (and why)
  • [topic] — not applicable to this occupancy/type
  • [topic] — already confirmed complete by Spec 01 40 00

Before I spend time researching, please confirm:
  • Is the project context correct?
  • Should I add or remove any research topics?
  • Are there specific code concerns you already have that I should prioritize?
```

**Do not begin Phase 2 until the user responds.**

---

## Phase 2 — Project Document Extraction (Pass 1)

This phase reads what the project documents already say. It runs before web
research so the gap analysis has a firm baseline.

### 2a — Read All In-Scope Documents

For each spec section in scope:
- Read the full section (all parts — General, Products, Execution)
- Use pdfplumber for text-layer PDFs; use vision for scanned or image-heavy pages

For drawing sheets:
- Read title block, notes, schedules, and details relevant to the scope
- Use vision for plan sheets; extract text from schedules if text-layer

For referenced standards within spec sections:
- Note every standard cited (ASTM, ANSI, NFPA, UL, SMACNA, etc.) with its
  edition year as cited in the spec

### 2b — Extract All Code and Standard Citations

For each document read, extract every code reference, standard citation, and
requirement into a structured inventory. Write to `.construction/code_research/pass1_project_inventory.yaml` using the schema at:
→ `${CLAUDE_SKILL_DIR}/references/schemas.yaml` § pass1_project_inventory

**Critical extraction discipline:**
- Record what IS there (citations found, requirements stated)
- Also record what is ABSENT that you would expect to find
- Do not interpret absence as compliance — absence is a potential gap
- Note edition years as specified — a correct requirement cited against the
  wrong edition is a potential gap

### 2c — Build the "Already Addressed" Inventory

Summarize Pass 1 into a flat inventory used for gap diffing in Phase 4. Write to `.construction/code_research/pass1_summary.yaml` using the schema at:
→ `${CLAUDE_SKILL_DIR}/references/schemas.yaml` § pass1_summary

---

## Phase 3 — Code Research (Pass 2)

### 3a — Research Jurisdiction and Adopted Codes

Before researching requirements, establish which edition of each code is
adopted by the jurisdiction. This is non-negotiable — code requirements
vary significantly between editions.

Search for:
```
"{state} building code adopted edition {year}"
"{city} {state} local building code amendments"
"{state} IBC adoption effective date"
"{state} fire code adopted edition"
"{state} accessibility code requirements"
```

Write to `.construction/code_research/jurisdiction.yaml` using the schema at:
→ `${CLAUDE_SKILL_DIR}/references/schemas.yaml` § jurisdiction

If jurisdiction code adoption cannot be confirmed via web search, mark as
`uncertain` and note this prominently in the report. Do not assume the latest
published edition is what's adopted.

### 3b — Research Requirements for Each Topic

For each topic in the confirmed research outline, research what the applicable
codes require. Organize research by logical topic clusters, not fixed batch sizes.

**For each topic, establish these three things:**

1. **What the code requires** — the specific section, edition, and requirement
   language from the applicable code (IBC, ADA, NFPA, state code, etc.). Verify
   via web search; do not rely on paraphrases or training memory for exact
   language.
2. **What referenced standards apply** — codes reference downstream standards
   (ASTM, ANSI, UL, etc.) that contain the actual test methods and acceptance
   criteria.
3. **What jurisdiction-specific overlays exist** — state amendments, local
   amendments, and non-building-code authorities (health department, fire
   marshal, USDA/FDA for food service, etc.) that operate independently.

Use shared reference files at `${CLAUDE_SKILL_DIR}/../../reference/` to verify
specific numeric thresholds (clearances, load factors, occupant capacities)
during research.

Write to `.construction/code_research/topics/{slug}.yaml` using the schema at:
→ `${CLAUDE_SKILL_DIR}/references/schemas.yaml` § topic_findings

**Adaptive scope expansion:** If research reveals that a code requirement likely
applies but may be addressed in a spec section or drawing not yet read in Pass 1,
read that document before classifying the topic as a gap. Update the Pass 1
inventory with any new citations found. Note the additional documents read when
reporting to the user at checkpoint 3c.

### 3c — USER CHECKPOINT: Interim Findings

After completing a cluster of related topics, report to the user:

```
Completed research on [topic 1], [topic 2], and [topic 3].

PRELIMINARY GAPS IDENTIFIED SO FAR
  ⚠  HIGH   Slip resistance — no COF requirement found in spec; IBC §1210.3
             and ADA require slip-resistant floors in kitchens and ADA paths
  ⚠  HIGH   Health department overlay — kitchen complex may be subject to
             Maryland Dept. of Health food service regs; not mentioned in scope
  ○  MEDIUM  VOC content — 09 67 23 does not cite VOC limits; Division 01
             may address this globally (will check)

NO GAP (already addressed in spec)
  ✓  Moisture testing — ASTM F 1869 and F 2170 both required (§3.1-B)
  ✓  Compressive strength — ASTM C 579 requirement at 7,700 psi (§2.1-D)
  ✓  Bond strength — ACI 503R at 400 psi (§2.1-D-10)

UNCERTAIN (couldn't confirm code language)
  ?  Baltimore City amendments to IBC §1210 — could not confirm if local
     amendments modify the slip resistance requirement

Continuing with [next batch]: [topic 4], [topic 5].
Do you want me to dig deeper on any of these before continuing, or shall I proceed?
```

---

## Phase 4 — Gap Analysis (Pass 3)

### 4a — Diff Research Against Project Inventory

Compare every research finding from Phase 3 against the Pass 1 project
inventory. Write to `.construction/code_research/gap_analysis.yaml` using the schema at:
→ `${CLAUDE_SKILL_DIR}/references/schemas.yaml` § gap_analysis

Classify each finding into one of: `gaps` (with severity + confidence), `already_addressed`, or `uncertain`.

### 4b — Classify Each Gap

Each gap gets a severity and confidence rating:

**Severity:**
- `HIGH` — a code requirement clearly applies, is not addressed in the project
  documents, and creates regulatory or safety risk if unresolved
- `MEDIUM` — a code requirement likely applies but may be addressed elsewhere
  (e.g., in a Division 01 section not yet reviewed) or its applicability
  depends on a condition that hasn't been confirmed
- `LOW` — a code reference that could be added for completeness but whose
  absence is unlikely to cause a compliance issue

**Confidence:**
- `confirmed` — the code requirement is definitively established (correct
  jurisdiction, correct edition, correct applicability) and the project
  document status is definitively established (read the full section)
- `needs_review` — the requirement likely applies but requires information
  not available in the current documents (AHJ confirmation, additional spec
  sections not provided, etc.)
- `uncertain` — conflicting sources, could not confirm jurisdiction's
  adopted code edition, or the code's applicability to this specific scope
  is genuinely ambiguous

### 4c — USER CHECKPOINT: Review Gaps Before Report

Before generating the report, present the gap summary:

```
GAP ANALYSIS COMPLETE

HIGH-CONFIDENCE GAPS (take action)
  GAP-001 ⚠ HIGH    Slip resistance — no COF requirement in 09 67 23
                     IBC §1210.3 requires 0.60 COF in commercial kitchens
                     Recommended action: add COF requirement and test method

  GAP-002 ⚠ HIGH    Health department — kitchen complex not addressed
                     Maryland COMAR 10.15.03 may apply; needs AHJ confirmation
                     Recommended action: confirm with Owner whether food
                     service permit required

MEDIUM-CONFIDENCE GAPS (confirm and close)
  GAP-003 ○ MEDIUM   VOC content — 09 67 23 may need cross-ref to 01 61 16
                      Likely covered globally; confirm and add cross-reference

UNCERTAIN (need more information)
  ?  Baltimore City amendments to slip resistance — couldn't confirm locally

ALREADY ADDRESSED (no action needed)
  ✓  Moisture vapor emission testing — well covered, both test methods
  ✓  Substrate preparation — shot-blast, priming, patching all specified
  ✓  Compressive strength — ASTM C 579 at 7,700 psi
  ✓  Bond strength — ACI 503R at 400 psi
  ✓  Installer qualification — manufacturer written cert required

Before I write the report:
  • Are any of these gaps ones you were already aware of and have addressed
    outside the documents I reviewed?
  • Should I research any topic further before finalizing?
  • Any gaps you want to remove from the report?
```

---

## Phase 5 — Report

### 5a — Generate Gap Report

Write to `.construction/code_research/report_{scope}_{date}.md` using the template at:
→ `${CLAUDE_SKILL_DIR}/references/gap_report_template.md`

Populate all placeholder fields from the gap_analysis.yaml and jurisdiction.yaml data. The report must include: applicable codes table, all gaps (action required + confirm and close), uncertain items, already addressed items, documents reviewed, and the disclaimer.

### 5b — Write Graph Entry

```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python \
  ${CLAUDE_SKILL_DIR}/../../scripts/graph/write_finding.py \
  --type "code_gap_analysis" \
  --title "Code gap analysis: {scope} — {n_gaps} gaps identified" \
  --data '{
    "scope": "[spec sections or topic]",
    "topics_researched": 0,
    "already_addressed": 0,
    "gaps_high": 0,
    "gaps_medium": 0,
    "gaps_low": 0,
    "uncertain": 0,
    "jurisdiction_confirmed": true
  }'
```

---

## Resumption

Check for `.construction/code_research/` before starting:

| Files Present | State | Action |
|---------------|-------|--------|
| Nothing | Fresh start | Begin Phase 1 |
| `scope_definition.yaml` only | Scope confirmed, research not started | Begin Phase 2 |
| `pass1_summary.yaml` | Project extraction done | Begin Phase 3 |
| `topics/` partial | Research in progress | Resume from next unresearched topic |
| All topics complete, no `gap_analysis.yaml` | Research done | Begin Phase 4 |
| `gap_analysis.yaml` exists | Gaps identified | Present to user, go to Phase 5 |
| `report_*.md` exists | Complete | Offer to update or re-run |

---

## Discipline Notes

PE discipline guidance for jurisdiction research, scope boundaries, regulatory overlays, and confidence levels:
→ `${CLAUDE_SKILL_DIR}/references/discipline_notes.md`

## File Safety
Never overwrite an existing gap report. Version output files (`_v2`, `_v3`) if a prior version exists at the target path.
