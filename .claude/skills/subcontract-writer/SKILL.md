---
name: subcontract-writer
description: Generate a complete subcontract document for a scope of work. Takes a firm's subcontract template (PDF or Word) and the awarded bid, populates every article with scope-specific language from project drawings, specifications, and bid data. Outputs a Word document. Use when asked to write a subcontract, draft a sub agreement, or prepare contract documents for a trade. Triggers on 'subcontract', 'sub agreement', 'write contract', 'draft subcontract', or 'trade contract'.
argument-hint: "<scope_of_work>"
---

# Subcontract Writer

Generates a complete, execution-ready subcontract agreement from a firm's template, the awarded bid, and project specifications. **You are the intelligence layer** — you read every document, extract all data, generate every article's text, make legal/commercial judgments, and write fully-populated JSON files. The Python formatter is a thin rendering utility that makes no content decisions.

**Output:** Word document (.docx) matching the firm's template structure.

**Dependency:** Requires `python-docx` in the construction Python environment.

**Key principle:** The bid document is the PRIMARY input. It establishes what was priced, at what rates, with what inclusions and exclusions. Specifications inform scope descriptions and technical requirements. The template provides article structure and standard boilerplate.

---

## Pipeline Position
This skill can be invoked directly when the user has an awarded bid and wants to generate a subcontract, or as the final step of the bid pipeline:
```
/bid-tabulator → /bid-evaluator → user confirms → THIS SKILL
```
Either way, the awarded bid document (Slot B) is the mandatory input.

## Mode Detection
Check for `.construction/` directory at the project root.
- **AgentCM mode**: Read specs from `.construction/spec_text/{section}.txt`. Use sheet index from `.construction/index/sheet_index.yaml` for drawing references. Read project metadata from `.construction/CLAUDE.md`.
- **Flat File mode**: Discover spec PDFs via project `CLAUDE.md` paths or directory search. Read drawing sheets directly from PDF.

---

## Architecture: Five Phases in Order

Execute in five sequential phases. Each phase has a defined output that must be completed before the next begins. **Do not skip phases or combine them.** The most common failure mode is attempting Phase 4 (writing) before Phase 3 (validation) is complete.

```
Subcontract Writer Progress:
Phase 1  →  Phase 2  →  Phase 3  →  USER CHECKPOINT  →  Phase 4  →  Phase 5
Triage     Extract     Validate      Confirm data         Write       Verify
```

---

## Phase 1 — Document Triage and Slot Assignment

Before reading any document substantively, assign each uploaded file to its slot. State the assignments to the user before proceeding.

| Slot | Role | Source | What It Provides |
|------|------|--------|-----------------|
| A | Template | Subcontract PDF/DOCX | Article structure, boilerplate language, required sections |
| B | Awarded bid | Subcontractor bid PDF | **Contract sum, quantities, unit rates, inclusions, exclusions, VE alternates** |
| C | Specifications | Spec section PDFs | Scope descriptions, submittal requirements, warranty clauses, installer qualifications |
| D | Drawings | Finish schedule, floor plans | Room codes, area takeoffs, scope boundaries |

**Slot B is mandatory.** If missing, stop and output:
```
I need the awarded subcontractor's bid document before I can generate this
subcontract. The bid is the source of truth for the contract sum, quantities,
and unit rates. Which file is the awarded bid?
```

Read Slot A first to understand the required article structure. Note every article heading. Flag any article that requires project-specific content (not just boilerplate) — these become required extraction targets in Phase 2.

If no template is provided, ask: "Do you have a standard subcontract template?" If none available, use AIA A401-style structure as fallback.

---

## Phase 2 — Structured Extraction, One Slot at a Time

Run a separate extraction pass for each slot. Write extracted data to `scope_data.json` incrementally. Do not combine slots in a single read.

### Slot B Extraction (Bid Document) — Run First

Read the bid PDF using vision. Extract every field below. Mark any field not found as `MISSING` — do not infer or estimate.

**Commercial data:**
- Subcontractor company name (exact legal name from letterhead)
- Address, phone, email
- License/registration number
- Estimator/contact name
- Proposal number and date
- Bid validity period (if stated)
- Total contract sum (exact dollar amount)

**Scope data:**
- Line items with: spec section, description, quantity, unit, unit rate, extended amount
- Inclusions list (verbatim from bid)
- Exclusions list (verbatim from bid — critical for scope gap prevention)
- Value engineering alternates with VE ID, description, and deduct amount
- Qualifications or clarifications

**Verify:** Line item amounts must sum to the total contract sum. If they don't, flag the discrepancy.

### Slot A Extraction (Template)

**If .docx template:** Use python-docx to read headings, paragraphs, and identify article structure.

**If PDF template:** Use vision to read the template. Rasterize pages if needed:
```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/../../scripts/pdf/rasterize_page.py template.pdf {page} --dpi 200 --output template_page_{page}.png
```

Extract the list of required articles and any fill-field placeholders (`[DATE]`, `[CONTRACT SUM]`, `[SUBCONTRACTOR]`).

For each article, determine:
- `number` and `title` (exactly as shown in template)
- `content_type`: one of:
  - `"preserve"` — standard boilerplate (payment terms, insurance, dispute resolution, indemnity, safety, default/termination, general provisions). Transcribe the EXACT text verbatim.
  - `"generate"` — scope-specific content (scope of work, contract documents, schedule, submittals, warranty). You will write this from extracted data.
  - `"fill-in"` — project-specific values (contract sum, dates). You will populate from the Data Model.

**Critical:** Transcribe ALL preserved article text verbatim. Do not summarize or paraphrase template boilerplate.

### Slot C Extraction (Specifications)

For each specification section listed in the bid scope, read the PDF and extract Part 1 requirements. One extraction block per section.

Extract per spec section:
- **§1.3 / §1.4 — Submittal requirements:** shop drawings, product data, samples, certifications, LEED docs
- **§1.5 — Quality assurance:** installer qualifications, manufacturer certifications, mockups, testing
- **§1.6 / §1.8 — Warranty provisions:** general warranty period, extended warranties, joint manufacturer/installer warranties
- **§1.7 — Special conditions:** environmental requirements (temperature, humidity, cure times), substrate conditions
- **§3.x — Execution requirements:** installation methods, tolerances, protection requirements

Also check Division 01 for project-wide requirements: MBE/WBE goals, prevailing wage, LEED, closeout documents.

### Slot D Extraction (Drawings/Finish Schedule) — If Provided

Extract room/area codes relevant to scope boundaries. Identify explicit exclusions (rooms marked "by others" or scoped to a different trade). This extraction is scope-dependent — only extract data relevant to the trade being contracted.

---

## Phase 3 — Data Validation

Before surfacing anything to the user, validate the extracted data. Every `MISSING` field in a required category is a blocking error.

### Required Fields (blocking — cannot proceed if absent)

| Field | Source | Why Required |
|-------|--------|--------------|
| `subcontractor.company_name` | Slot B letterhead | Legal party identification |
| `subcontractor.license_number` | Slot B letterhead/footer | Regulatory compliance |
| `subcontractor.proposal_number` | Slot B header | Bid traceability |
| `contract_sum.formatted` | Slot B | Must include $ and comma formatting |
| `contract_sum.written_words` | Computed | Required for legal enforceability |
| `schedule_of_values` (≥1 entry) | Slot B | Quantities from bid only |
| `exclusions` (non-empty) | Slot B | Scope gap prevention |
| Per-spec submittal requirements | Slot C §1.3/1.4 | Cannot leave Article 8 as placeholder |
| Per-spec warranty provisions | Slot C §1.6/1.8 | Cannot leave Article 11 as placeholder |

Spec-specific requirements are conditional — only required if that spec section appears in the bid scope.

### Legal Completeness Checks

- Contract sum written words matches numeral mathematically
- Schedule of values quantities match bid document (not master scope estimates)
- No quantity in SOV differs from the bid by more than 2%
- VE alternates list is complete (check all bid pages — VE alternates often appear on page 2+)
- Exclusions cross-checked against drawings (if Slot D provided)

### Compute Derived Fields

After validation, compute fields the user will need to confirm:

| Derived Field | How to Compute |
|---------------|----------------|
| `subcontract_number` | `{GC_initials}-{architect_project_no}-{trade_code}-{seq}` or `[GC TO ASSIGN]` |
| `completion_date` | Extract from project schedule or bid if stated |
| `ld_rate` | Extract from prime contract reference in bid or template |
| `bond_amount` | = contract sum (100% P&P bond for public works) |
| `mbe_goal` / `wbe_goal` | Extract from prime contract or template |
| `governing_state` | Infer from project address |
| `prevailing_wage_statute` | Infer from state (e.g., Maryland = L&E Article §17-201) |

---

## USER CHECKPOINT — Show Data Model, Wait for Confirmation

**This is the most important step in the skill. Do not skip it.**

After Phase 3 validation passes, surface the complete extracted data to the user in readable format before writing any contract prose. The user must explicitly confirm or correct the data.

Format the checkpoint output:

```
I've read all [N] documents. Here's what I extracted — please review before
I generate the subcontract.

━━━ SUBCONTRACTOR ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Company:       [company_name]
  License:       [license_number]
  Proposal:      [proposal_number]  (dated [bid_date])
  Estimator:     [estimator_name]  ·  [email]  ·  [phone]

━━━ CONTRACT SUM ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Amount:        [formatted]
  Written:       [written_words]

━━━ SCHEDULE OF VALUES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  [spec]  [description]              [qty] [unit] @ [unit_cost] = [extended]
  [spec]  [description]              [qty] [unit] @ [unit_cost] = [extended]
  ...
  TOTAL:  [formatted]

━━━ INCLUSIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • [inclusion 1]
  • [inclusion 2]

━━━ EXCLUSIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • [exclusion 1]
  • [exclusion 2]

━━━ VALUE ENGINEERING ALTERNATES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  [id]  [description]    [amount]

━━━ SPEC REQUIREMENTS (will appear in Articles 8 and 11) ━━━━
  [spec section]:
    Installer cert required:  [yes/no — source]
    Mockup required:          [yes/no — details]
    Warranty:                 [duration and form]
    Key submittals:           [list]

━━━ GAPS / ITEMS NEEDING YOUR INPUT ━━━━━━━━━━━━━━━━━━━━━━━━━
  ⚠  [any MISSING or derived fields needing confirmation]

Is any of this wrong or missing? Correct me now and I'll update the data
before writing. Once you confirm, I'll generate the subcontract.
```

**Do not proceed until the user responds with explicit confirmation.**

Accepted confirmation signals:
- "Looks good, go ahead"
- "That's correct"
- "Add [X] and proceed"
- Any correction followed by "proceed" or "continue"

If the user makes a correction, update the extracted data, echo the specific change back to confirm it was applied, and ask if they are ready to proceed. Do not re-show the entire data model unless another correction is made.

---

## Phase 4 — Article Generation in Three Groups

Generate the contract in three groups. After each group, show the drafted articles and wait for confirmation before continuing to the next group.

### Generation Rules

**Rule 1: Every number comes from the Data Model — never from training data.** If a number appears in the contract prose, it must be traceable to extracted data. If a field is missing and the number cannot be derived, use `[GC TO CONFIRM]` as the placeholder — not a guessed value.

**Rule 2: No article is left as a generic placeholder.** If an article has placeholder text, it means Phase 2 extraction for the relevant spec section was incomplete. Stop, re-run extraction, and update the data before writing that article.

**Rule 3: The template provides structure, the Data Model provides content.** Do not copy boilerplate from the template that contains the wrong party names, wrong amounts, or wrong scope. Boilerplate means language structure only — specific values always come from the Data Model.

**Rule 4: Scope quantities come from the bid, not the specs.** The specs describe what the product must be. The bid describes how much of it was priced. These are different numbers. Use bid quantities in the contract.

---

### Group 1: Identity and Scope (show → confirm → continue)

**Cover Page** — Write a `cover_page` section with:
- `info_table` block with all identification fields: subcontract number, project name and address, owner, architect and project number, prime contract number, contractor name and address, subcontractor name/address/phone/email, license number, proposal reference (number and date), date of agreement (leave blank for execution), contract sum in BOTH numerals (`$X,XXX,XXX.XX`) AND written words

**Article 1 — Subcontract Documents** — Document hierarchy from template with prime contract number and date injected. All spec sections listed. Order of precedence stated. Division 01 applies to ALL subcontractors — always include.

**Article 2 — Scope of Work** — Three components:
1. Scope description: "The Subcontractor shall furnish all labor, materials, equipment..."
2. `table` block: line items from the bid — Spec, Description, Qty, Unit, Rate, Amount
3. `bullet_list` block: inclusions (from bid inclusions + spec special requirements)
4. `bullet_list` block: exclusions (from bid exclusions — MUST include specific room/area references where applicable)
5. `table` block: VE alternates with ID, description, deduct amount (marked as available by Change Order)

After showing Group 1, ask: *"Does the scope and identification look right? Any corrections before I continue to schedule and commercial terms?"*

---

### Group 2: Commercial Terms (show → confirm → continue)

**Article 3 — Schedule** — NTP commencement period (days from written NTP). Substantial completion date. Time is of the essence language. **LD flow-down** with specific rate (e.g., "$X per calendar day"). If the LD rate is unknown, use `[GC TO CONFIRM]`. Include special environmental conditions from specs if applicable (e.g., cure times, ambient temperature/humidity requirements).

**Article 4 — Contract Sum** — Contract sum in both forms (`$X,XXX,XXX.XX` + written words). `table` block: Schedule of Values grouped by spec section with line amounts. Tax exemption note if applicable (government projects). Unit price reference to Exhibit A.

**Article 5 — Progress Payments** — G703 form, monthly cutoff date, conditional + unconditional lien waiver requirement. Retainage schedule with reduction conditions. Pay-when-paid with owner non-payment backstop (time-certain trigger — required in most states). Final payment conditions including closeout documents.

**Article 6 — Changes** — Written CO required. Markup rates (self-performed, sub-tier, equipment). Claim notice period. Unit price reference.

After showing Group 2, ask: *"Do the commercial terms look right — schedule, money, payments?"*

---

### Group 3: Legal and Closeout (show → confirm → write .docx)

**Article 7 — Insurance and Bonds** — Insurance table with all coverages and limits from template. Additional Insured endorsement naming both Contractor and Owner by name. P&P bond: 100% of contract sum (insert formatted amount), surety rating requirement, certificate deadline.

**Article 8 — Submittals** — Submittal schedule deadline (e.g., 15 days from execution). For each spec section in scope, list all required submittals extracted from Part 1. Include installer qualifications and manufacturer certifications where required by spec. LEED documentation requirements. **Do not leave this article as a placeholder under any circumstances.**

**Article 9 — Prevailing Wages and Labor** — Statute citation for governing state. Certified payroll requirements. MBE/WBE goals with percentages. E-Verify requirement.

**Article 10 — Indemnification** — Intermediate-form indemnity. Indemnitees named: Contractor, Owner, Architect, and their officers/directors/employees. **Carve-out must use "sole negligence" — not just "negligence."** This is a legal requirement in Maryland and most states. If the template omits "sole", FIX IT and set `content_type: "review"` with a `legal_flags` entry.

**Article 11 — Warranty** — General warranty (1 year from Substantial Completion or longer per specs). Extended warranty table: one row per spec section with extended warranty requirement from the Data Model. Warranty response obligations. **Do not leave this article as a placeholder under any circumstances.**

**Articles 12–15** — Template boilerplate with project-specific values injected. Include scope-specific closeout requirements derived from specs (e.g., care guides, certification letters) in Article 15 or scope.

**Exhibits list** — Minimum:
- Exhibit A: Unit Price Schedule
- Exhibit B: MBE/WBE Participation Plan
- Exhibit C: Schedule of Values (due within 10 days)
- Exhibit D: Project Schedule
- Exhibit E: Subcontractor's Bid Proposal (mark as "informational only — does not govern scope")
- Exhibit F: Prevailing Wage Rate Schedule

### Preserved Article Legal Review

For each preserved article, review the template text for legal adequacy:

**Indemnity:** Verify "sole negligence or willful misconduct" carve-out. Broad-form indemnity is unenforceable in most states (e.g., Maryland Code CJP §5-401). If the template says "negligence" without "sole", FIX IT and set `content_type: "review"`.

**Insurance:** Verify limits are adequate for project size. CGL $1M/$2M, Auto $1M, Umbrella $5M is standard for commercial.

**Bonds:** Verify bond amount matches contract sum. Public works projects over $100K typically require P&P bonds.

**Pay-when-paid:** Verify backstop language exists. Most states require a time-certain backstop (e.g., 75 days).

**LD:** If preserved text lacks LD flow-down, add it to the Schedule article.

If you find and fix an issue, change `content_type` from `"preserve"` to `"review"` and add a `legal_flags` entry:
```json
{"severity": "critical", "issue": "Missing 'sole' before 'negligence'", "recommendation": "Add per state statute", "fixed": true}
```

After showing Group 3, ask: *"Any final changes? Once confirmed I'll write the Word document."*

---

## Phase 4 Output — Write JSON Files

After all three groups are confirmed, write two files to the output directory:

### scope_data.json

Raw structured data for downstream use and eval scoring:
```json
{
  "project_name": "...",
  "project_address": "...",
  "owner": "...",
  "contractor_name": "...",
  "subcontractor": {"company_name": "...", "license": "...", ...},
  "contract_value": 1392618,
  "spec_sections": [{"number": "09 30 00", "title": "Tiling"}, ...],
  "line_items": [{"spec": "...", "quantity": 9200, "unit": "SF", "rate": 13.90, "amount": 127880}, ...],
  "exclusions": ["..."],
  "value_engineering_alternates": [{"id": "VE-1", "description": "...", "amount": -14200}, ...],
  "submittal_requirements": ["..."],
  "warranty": "...",
  "special_conditions": ["..."]
}
```

Keep numeric values as raw numbers in scope_data.json (eval scorer uses these).

### template_data.json

Fully-populated document structure:
```json
{
  "cover_page": {
    "text": "SUBCONTRACT AGREEMENT\n\nThis Agreement is entered into...",
    "blocks": [
      {"type": "info_table", "rows": [
        {"label": "Project", "value": "..."},
        {"label": "Contract Sum", "value": "$X,XXX,XXX.XX (Written Words...)"}
      ]}
    ]
  },
  "articles": [
    {
      "number": 2,
      "title": "Scope of Work",
      "content_type": "generate",
      "text": "2.1 The Subcontractor shall furnish all labor...",
      "blocks": [
        {"type": "table", "label": "Scope Description Table",
         "headers": ["Spec", "Description", "Qty", "Unit", "Rate", "Amount"],
         "rows": [["03 35 13", "...", "13,800", "SF", "$1.80", "$24,840"]]},
        {"type": "bullet_list", "label": "The Work includes:", "items": ["..."]},
        {"type": "bullet_list", "label": "Exclusions:", "items": ["..."]},
        {"type": "table", "label": "VE Alternates",
         "headers": ["VE #", "Description", "Amount"], "rows": [["VE-1", "...", "-$14,200"]]}
      ],
      "legal_flags": []
    }
  ],
  "exhibits": [
    {"letter": "A", "title": "Unit Price Schedule"},
    {"letter": "E", "title": "Bid Proposal (informational only; does not govern scope)"},
    {"letter": "F", "title": "Prevailing Wage Rate Schedule"}
  ]
}
```

Block types: `table` (headers + rows), `bullet_list` (label + items), `numbered_list` (label + items), `info_table` (rows with label + value).

All display values in blocks must be pre-formatted strings (e.g., `"$1,392,618.00"` not `1392618`).

### Produce Word Document

Call the thin formatter:
```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/scripts/generate_subcontract_docx.py \
  --template template_data.json \
  --scope scope_data.json \
  --output Subcontract_[SubName]_[SCNumber].docx
```

The formatter renders your pre-populated content into .docx format. It makes no content decisions.

---

## Phase 5 — Post-Generation Verification

After writing the `.docx`, run the following checks against the generated file. If any check fails, fix the specific issue in the JSON, regenerate the .docx, and re-verify. Do not present a document with known failures.

### Verification Checks

**Identity:**
- Contract sum line contains `$` and `,` formatting
- Written words for contract sum present and matches numeral
- Subcontract number present in document
- Subcontractor license number present

**No placeholders:**
- No `[Generated content` strings
- No `review and customize` strings
- No `[placeholder]` or `[INSERT]` strings
- Any `[GC TO CONFIRM]` fields have been approved by user

**Scope completeness:**
- All bid quantities appear in Article 2
- Exclusions list present with specific references
- All spec sections from bid are referenced in scope

**Legal elements:**
- `sole negligence` appears in indemnity article
- `liquidated damages` flow-down present
- LD rate stated (if known)
- Prevailing wage statute cited (if applicable to governing state)

**Article completeness:**
- Article 8 contains spec-specific submittal requirements (not placeholder)
- Article 11 contains spec-specific warranty provisions (not placeholder)
- Extended warranties from specs appear in Article 11

If all checks pass, present the file and state which checks passed. If any check fails, fix the specific issue, regenerate, and note the fix.

### Present for Review

Present a summary:
- Articles generated vs. preserved vs. reviewed
- Any legal flags raised (with severity and what was fixed)
- Verification check results
- Scope highlights: spec section count, line item count, total contract sum
- **Remind the user:** "Contract documents require professional review before execution."

Write graph entry:
```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/../../scripts/graph/write_finding.py \
  --type "subcontract_generated" \
  --title "Subcontract: {scope} — {subcontractor}" \
  --output-file "{output_path}" \
  --data '{"scope": "...", "subcontractor": "...", "contract_sum": ..., "spec_sections": ..., "line_items": ..., "legal_flags": ...}'
```

---

## Targeted Correction Workflow

When the user requests a change to the generated document after Phase 5:

1. **Identify the affected Data Model field(s)** — every contract element traces back to extracted data
2. **Update the JSON files** — make the change at the data layer
3. **Identify the affected article(s)** — typically one or two articles maximum
4. **Regenerate only those articles** — do not rewrite the entire document
5. **Show the changed paragraphs specifically** — not the full article
6. **Confirm the change** before writing the updated `.docx`

**Do not regenerate the full document for single-article changes.**

---

## Common Failure Modes

| Failure | Cause | Prevention |
|---------|-------|------------|
| Wrong contract sum | Reading specs instead of bid | Slot B extraction runs first; validate numeral against bid PDF directly |
| Placeholder articles | Skipping spec extraction | Phase 3 validation blocks generation if spec fields are MISSING |
| Missing quantities | Using master scope estimates | Quantities come from bid SOV, not spec sections |
| Wrong subcontractor info | Using template example info | Always extract company name, address, license from Slot B, not Slot A |
| Inconsistent amounts | Generating prose without Data Model | All numbers inject from extracted data — never hardcoded |
| Missing exclusions | Only reading inclusions | Explicitly extract exclusions section from bid; cross-check against drawings |
| VE alternates missing | Bid spans multiple pages | Read all pages of the bid; VE alternates typically on page 2+ |
| Indemnity too broad | Using template language verbatim | Always include "sole negligence" in carve-out; verify post-generation |

---

## File Safety

Never overwrite an existing subcontract. The formatter uses `safe_output_path()` which appends `_v2`, `_v3`, etc. automatically.

## Tips

- "Furnish and install" is the standard scope phrase unless the sub is furnish-only or install-only
- Division 01 applies to ALL subcontractors — always include in contract documents list
- Watch for scope gaps between trades (e.g., blocking, fire caulking, temporary protection) — flag for user
- Detect template placeholder patterns (`<<SCOPE>>`, `[INSERT]`, `{FIELD}`) and replace them
- Some firms use AIA A401, ConsensusDocs 750, or custom forms — adapt to whatever is provided
- For large contracts (many spec sections), generate JSON incrementally — don't try to hold all article text in a single response
