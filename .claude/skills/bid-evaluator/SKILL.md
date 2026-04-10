---
name: bid-evaluator
description: >
  Evaluate tabulated subcontractor bids against specs and drawings — scope
  gap analysis, exclusion risk scoring, award recommendation. Triggers:
  'evaluate bids', 'bid evaluation', 'lowest responsible bidder'.
argument-hint: "<tabulated_bids_dir> [scope_description]"
disable-model-invocation: true
---

# Bid Evaluator

Evaluate tabulated subcontractor bids against construction documents.
This skill does NOT make the award decision — it builds the analytical
foundation so the PE/PM can decide quickly and confidently.

## Pipeline & Disambiguation

```
/bid-tabulator → THIS SKILL → user confirms → /subcontract-writer
```

**This skill requires tabulated bids as input.** If the user has raw bid PDFs that haven't been tabulated yet, run `/bid-tabulator` first to produce the per-bidder JSON files and comparison Excel. This skill consumes that output.

- User has **bid PDFs** → `/bid-tabulator` (data capture) → then offer this skill
- User has **tabulated bids** and wants analysis → this skill directly
- User says "compare bids" or "buyout" → check if bids are already tabulated; if not, start with `/bid-tabulator`

## Tier System

- **RIGID**: Output schema, scoring tables, file naming
- **GUIDED**: Dialogue sequencing, scope assembly, scoring thresholds
- **FLEXIBLE**: Bid interpretation, scope coverage, risk assessment

## Required Inputs

1. Tabulated bids (from /bid-tabulator or equivalent)
2. Relevant specification sections
3. Relevant drawing sheets (Claude reviews via vision)
4. Scope context (from user dialogue)

Optional: bid form/ITB, schedule, owner requirements, budget estimate,
past experience with bidders.

---

## Step 1: Scope Assembly

**Complete before analyzing any bids.**

### Mode Detection
Check for `.construction/` directory at the project root.
- **AgentCM mode**: Read specs from `.construction/spec_text/{section}.txt`. Use sheet index from `.construction/index/sheet_index.yaml` for drawing identification.
- **Flat File mode**: Discover spec PDFs via `CLAUDE.md` paths or directory search (`Specifications/`, `Specification Sections/`). Read drawing sheets directly from PDF.

### 1a. Spec Review
Extract from each spec section: work included (Parts 1-3), work by
others (GC/NIC/Owner), related section cross-references, performance
requirements, coordination and temporary requirements.

### 1b. Drawing Review
Load `references/drawing-review.md` for guidance on what to look for
per drawing type. Vision-read key sheets to identify scope items,
conditions, and quantities not apparent from specs. Track drawing-
derived items separately — they differentiate thorough bidders.
Offload reference after completing drawing review.

### 1c. User Dialogue
Ask targeted questions to fill gaps documents can't answer. Do not
dump a questionnaire — ask conversationally, skip what you already
know.

**Always ask:** package definition (which specs/drawings), GC-provided
items, bid count and format, drawing confirmation if provided.

**Ask when relevant:** multi-trade splits, alternates/allowances,
qualification requirements, budget reference, schedule constraints.

Confirm assembled scope with user before proceeding.

### 1d. Build Scope Baseline
Produce internal baseline document: items in sub scope (with source),
drawing-identified scope, GC/owner exclusions, allowances, alternates,
qualifications, schedule constraints.

---

## Step 2: Bid Analysis

Load `references/buyout-domain.md` for domain knowledge on bid
language interpretation, common scope splits, red flags, trade-
specific evaluation notes, and non-price factors. Keep loaded
through Steps 2a-2d, then offload.

### 2a. Normalize Pricing
```
Adjusted Base = Submitted Base
              + Excluded spec-required items
              - Included GC-provided items
              + Accepted alternates ± Allowance adjustments
```
Valuation order: other bidder's line item → budget estimate → professional
judgment (flagged) → qualitative risk if unknown.
Document every adjustment. No silent price changes.
Flag unit price outliers (>2x median). Calculate exposure ranges.

### 2b. Scope Coverage Mapping
Map each bidder against every scope baseline item using five statuses:

| Status | Meaning |
|---|---|
| INCLUDED | Explicitly includes |
| EXCLUDED | Explicitly excludes |
| SILENT | Not addressed — **most dangerous** |
| PARTIAL | Includes with limitations |
| DIFFERENT | Offers substitution |

Flag all SILENT items on spec-required scope. Drawing-derived SILENT
items suggest incomplete document review by that bidder.

### 2c. Exclusion Risk Scoring

| Level | Criteria |
|---|---|
| CRITICAL | Spec-required, uncarried, >1% bid or >$5K |
| SIGNIFICANT | Implied by spec/practice, $2K-$5K |
| MINOR | Common GC-provided, <$2K |
| INFO | Clarification only, no cost impact |

### 2d. Qualification & Responsibility
Assess per bidder: bonding, insurance, licensing, experience,
capacity, DBE/MBE, bid completeness.
**Bust detection:** >20-30% below field + scope gaps + incomplete
submission. Flag for verification, never call it a bust.

---

## Step 3: Output

Build JSON per schema in `scripts/sample_input.json`, then run:
```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/scripts/export_bid_evaluation.py input.json output.xlsx
```

The script produces 5 sheets: Bid Comparison, Price Summary,
Exclusion Detail, Qualification Summary, Recommendation.

---

## Step 4: Handoff

1. Lead with the recommendation — don't make them hunt for it
2. Highlight items needing PE attention
3. Ask for explicit confirmation: selected bidder, scope adjustments,
   alternates, special conditions

**Do NOT proceed to /subcontract-writer without user confirmation.**

---

## Step 5: Write Graph Entry

If `.construction/` directory exists (AgentCM mode), record the evaluation:

```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/../../scripts/graph/write_finding.py \
  --type "bid_evaluation_complete" \
  --title "Bid evaluation: {scope} — {N} bidders, recommended {company}" \
  --output-file "{output.xlsx}" \
  --data '{"scope": "...", "bidder_count": N, "recommended": "...", "adjusted_amount": ..., "pe_attention_items": [...]}'
```

If no `.construction/` directory exists, skip — the Excel workbook is the deliverable.

---

## Context Needs Chart

| Step | Resource | Load Trigger | Offload After |
|---|---|---|---|
| 1b | `references/drawing-review.md` | Drawing sheets provided | Step 1b complete |
| 2 | `references/buyout-domain.md` | Entering bid analysis | Step 2d complete |
| 3 | `scripts/sample_input.json` | Building output JSON | Step 3 complete |
| 5 | `../../scripts/graph/write_finding.py` | AgentCM mode detected | Step 5 complete |

## Error Handling

- Uneven formats: note difficulty, don't penalize lump-sum bids
- <3 bids: note limited field, suggest re-bid if appropriate
- Budget mixed with hard bids: segregate with caveat
- Math errors: flag discrepancy, don't correct
- Scope too complex: focus on highest cost-impact items

## What This Skill Does NOT Do

- Contact subs, execute awards, or negotiate pricing
- Replace PE judgment on responsibility
- Produce subcontracts (use /subcontract-writer)
- Perform quantity takeoffs from drawings

## File Safety
Never overwrite an existing bid evaluation. The export script uses `safe_output_path()` which appends `_v2`, `_v3`, etc. automatically.

---

## Allowed Scripts

- `${CLAUDE_SKILL_DIR}/../../bin/construction-python`
- `${CLAUDE_SKILL_DIR}/scripts/export_bid_evaluation.py`
- `${CLAUDE_SKILL_DIR}/../../scripts/graph/write_finding.py`
