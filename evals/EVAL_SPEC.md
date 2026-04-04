# Evaluation Specification for Construction Skills

## Overview

This document defines the test cases and evaluation framework for validating each construction skill against real project documents. Test cases use actual construction documents (provided separately) and are structured for repeatable evaluation.

## Evaluation Architecture

```
evals/
├── EVAL_SPEC.md              ← this file
├── test_docs/                ← user provides real construction PDFs, specs here
│   ├── drawings/
│   ├── specs/
│   └── project_manual.pdf
├── cases/
│   ├── project-setup/
│   │   ├── case_01.json
│   │   └── expected/
│   ├── schedule-extractor/
│   │   ├── case_01_door_schedule.json
│   │   ├── case_02_finish_schedule.json
│   │   └── expected/
│   ├── submittal-log-generator/
│   │   ├── case_01.json
│   │   └── expected/
│   ├── bid-tabulator/
│   │   ├── case_01_single_scope.json
│   │   ├── case_02_scanned_bids.json
│   │   ├── case_03_alternates_unit_prices.json
│   │   └── expected/
│   ├── bid-evaluator/
│   │   ├── case_01_flooring_eval.json
│   │   └── expected/
│   ├── code-researcher/
│   │   ├── case_01_egress.json
│   │   ├── case_02_accessibility.json
│   │   ├── case_03_fire_protection.json
│   │   └── expected/
│   ├── subcontract-writer/
│   │   ├── case_01_with_template.json
│   │   ├── case_02_no_template.json
│   │   ├── case_03_pdf_template.json
│   │   └── expected/
│   └── pe-review/
│       ├── case_01_ab_test.json
│       ├── scoring_rubric.md
│       └── test_queries.md
├── runners/
│   ├── run_eval.py           ← orchestrates a single test case
│   ├── run_suite.py          ← runs all cases for a skill
│   └── score.py              ← scoring logic
└── results/
    └── {timestamp}_{skill}.json
```

## Test Case Format

Each test case is a JSON file:

```json
{
  "id": "schedule-extractor-01",
  "skill": "schedule-extractor",
  "name": "Door schedule extraction from A-0.01",
  "description": "Extract the door schedule from the architectural schedule sheet",

  "inputs": {
    "files": ["test_docs/drawings/A-0.01.pdf"],
    "page": 1,
    "user_prompt": "Extract the door schedule from sheet A-0.01 and output to Excel"
  },

  "expected_behavior": [
    "Locates the door schedule region on the sheet",
    "Correctly identifies column headers (MARK, WIDTH, HEIGHT, TYPE, FRAME, HARDWARE SET)",
    "Extracts all rows without missing any entries",
    "Produces a valid .xlsx file",
    "Writes a graph finding entry"
  ],

  "expected_outputs": {
    "excel_file": true,
    "graph_entry_type": "schedule_extracted",
    "min_rows": 10,
    "required_columns": ["MARK", "WIDTH", "HEIGHT", "TYPE"]
  },

  "scoring": {
    "completeness": {
      "weight": 0.4,
      "metric": "row_count_accuracy",
      "description": "Percentage of actual rows captured (expected/actual)"
    },
    "accuracy": {
      "weight": 0.4,
      "metric": "cell_value_accuracy",
      "description": "Percentage of cell values that match ground truth"
    },
    "format": {
      "weight": 0.2,
      "metric": "output_format_valid",
      "description": "Valid xlsx with correct headers and formatting"
    }
  }
}
```

## Test Cases by Skill

### P0: project-setup

| Case | Input | Validates |
|---|---|---|
| 01 | Full project folder with drawings, specs, RFIs | File classification accuracy, discipline detection, folder structure recognition |
| 02 | Minimal folder (just a bound drawing set PDF) | Handles single-file projects, detects bound set, triggers sheet indexing |
| 03 | Messy folder (mixed naming, nested subfolders) | Robustness with non-standard organization |

**Key metrics:**
- File type classification accuracy (% correct)
- Discipline detection accuracy
- Document type detection accuracy
- Time to complete indexing

### P1: schedule-extractor

| Case | Input | Validates |
|---|---|---|
| 01 | Door schedule (standard format) | Column detection, row extraction, cell value accuracy |
| 02 | Window schedule | Different column structure, handling merged headers |
| 03 | Room finish schedule | Finish code interpretation, multi-column layout |
| 04 | Panel schedule (electrical) | Dense numerical data, circuit/load extraction |
| 05 | Schedule across page break | Detecting continuation, merging results |

**Key metrics:**
- Column header detection (exact match)
- Row count accuracy (within ±5%)
- Cell value accuracy per column (% exact match)
- Excel output validity (opens correctly, data in right cells)

**Ground truth creation:** Manually transcribe 100% of the schedule into a reference spreadsheet. Compare extracted values cell-by-cell.

### P1: submittal-log-generator

| Case | Input | Validates |
|---|---|---|
| 01 | 5 individual spec section PDFs | Submittal paragraph detection, item parsing, type classification |
| 02 | Bound project manual (50+ sections) | TOC parsing, section boundary detection, long-running stability |
| 03 | Specs with addenda modifications | Addendum detection, submittal requirement updates |

**Key metrics:**
- Submittal item detection recall (% of actual items found)
- Submittal type classification accuracy
- Spec section/paragraph reference accuracy
- Excel output validity and completeness
- Comparison against manually-created submittal log

### P1: bid-tabulator

| Case | Input | Validates |
|---|---|---|
| 01 | 8 bid PDFs for single scope (text-layer) | Bidder detection, base bid extraction, line item capture, exclusions/qualifications, scope gap flagging |
| 02 | Scanned bid PDFs (no text layer) | Vision fallback, data extraction from rasterized pages, [unclear] flagging |
| 03 | Bids with alternates, unit prices, allowances | Alternate extraction (add/deduct), unit price capture with units, cross-bidder alignment |

**Key metrics:**
- Base bid amount accuracy (within $1 tolerance)
- Line item recall (% of actual items captured per bidder)
- Exclusion/qualification recall
- Scope gap detection (items in some bids but not others)
- No normalization of as-submitted data (engineer handles this)
- Excel output validity (all required tabs, low bid highlighted)

**Ground truth:** Manually extract all data from each bid PDF — base amounts, line items, exclusions, qualifications, alternates, unit prices.

### P1: bid-evaluator

| Case | Input | Validates |
|---|---|---|
| 01 | bid-tabulator output + specs + drawings — flooring scope | Scope gap detection, risk scoring, unit price benchmarking, recommendation quality |

**Key metrics:**
- Scope gap detection (items in specs/drawings not covered by any bidder)
- Risk factor identification (exclusions, qualifications, allowances)
- Recommendation quality (human-rated: PE/PM reviews recommendation memo)
- Excel output validity (risk matrix, comparison tabs)

**Ground truth:** PM/PE reviews generated evaluation against their own bid analysis for the same scope.

### P1: code-researcher

| Case | Input | Validates |
|---|---|---|
| 01 | Floor plan — egress research | Jurisdiction identification, IBC egress section citations, research framing (not compliance) |
| 02 | Floor plan — accessibility research | Multi-standard coverage (ADA + ANSI A117.1 + state), layered requirements |
| 03 | Floor plans — fire protection research | IBC Chapter 7 + NFPA 13/72/101 citations, construction type table references |

**Key metrics:**
- Jurisdiction accuracy (correct state/local code edition identified)
- Code citation accuracy (correct IBC/NFPA/ADA section references)
- Topic coverage (% of relevant research topics included)
- Research framing (zero COMPLIANT/NON-COMPLIANT determinations — all informational)
- Uncertainty handling (findings tagged confirmed/needs_review/uncertain appropriately)
- Human-in-the-loop (outline presented for user confirmation before deep research)

**Important:** This is a RESEARCH tool, not a compliance checker. Eval measures whether the skill identifies the right codes and requirements, not whether it makes compliance determinations. All findings must be framed as informational research for PE/architect review.

**Ground truth:** Licensed PE/architect documents applicable codes, editions, jurisdiction amendments, and code section references for each research topic.

### P1: subcontract-writer

| Case | Input | Validates |
|---|---|---|
| 01 | .docx template + specs — finishes scope | Template parsing, template preservation, spec section references, drawing references |
| 02 | No template — structural steel scope | Fallback document generation, article structure, Division 05 references, placeholder handling |
| 03 | PDF template + specs — HVAC scope | PDF template parsing, trade-specific language, multi-discipline drawing references |

**Key metrics:**
- Template preservation (standard clauses unchanged)
- Spec section reference accuracy (correct CSI sections for scope)
- Drawing sheet reference accuracy
- Contract documents list completeness and order
- Professional language quality (human-rated)
- .docx output validity

**Ground truth:** PM reviews generated subcontract against firm template and project documents. Scores on scope reference completeness, template fidelity, and language quality.

## Scoring Framework

### Per-Case Score

Each case produces a score from 0.0 to 1.0 based on weighted metrics defined in the case JSON.

### Per-Skill Score

Average of all case scores for that skill, weighted by case complexity:
- Simple cases (single file, single operation): weight 1.0
- Medium cases (multiple files, multi-step): weight 1.5
- Complex cases (long-running, cross-document): weight 2.0

### Overall Score

Weighted average of per-skill scores:
- P0 skills: weight 3.0 (foundational — everything depends on these)
- P1 skills: weight 2.0 (core value — these are the money skills)
- P2 skills: weight 1.5
- P3 skills: weight 1.0

### Score Interpretation

| Score | Interpretation |
|---|---|
| 0.9+ | Production-ready for this task |
| 0.7-0.9 | Useful with human review of outputs |
| 0.5-0.7 | Needs iteration — skill instructions need refinement |
| <0.5 | Fundamental approach needs rework |

## Ground Truth Creation Guide

When providing construction documents for evals, also create ground truth for each test case:

### For schedule extraction:
- Manually transcribe the full schedule into a CSV/XLSX
- Note merged cells, multi-line entries, and special characters

### For submittal log:
- Manually extract all submittal items from spec sections
- Note the spec paragraph reference, type, and description for each

### For bid tabulation:
- Manually extract from each bid PDF: company name, base bid amount, all line items (as-submitted), exclusions, qualifications, alternates (with add/deduct), unit prices (with units)
- Create per-bidder CSVs with exact values from the documents

### For bid evaluation:
- PM/PE independently evaluates the same bids against specs and drawings
- Record scope gaps, risk factors, and overall recommendation
- Compare generated evaluation memo against PM/PE analysis

### For code research:
- Licensed PE/architect documents applicable codes, correct editions, jurisdiction amendments
- Record code section references for each research topic
- Note which requirements are federal baseline vs state/local additions

### For subcontract writing:
- PM reviews generated document against firm template and project specs
- Verify correct spec sections referenced for the trade scope
- Verify template standard clauses preserved unchanged
- Rate language quality on 1-5 scale

## Running Evals

```bash
# Run a single case
python evals/runners/run_eval.py --case evals/cases/schedule-extractor/case_01.json

# Run all cases for a skill
python evals/runners/run_suite.py --skill schedule-extractor

# Run everything
python evals/runners/run_suite.py --all

# Results written to evals/results/{timestamp}_{skill}.json
```

## Iteration Process

1. **Baseline**: Run all cases without any skill modifications → establish baseline scores
2. **Identify gaps**: Find the lowest-scoring cases → these reveal skill weaknesses
3. **Iterate**: Modify SKILL.md instructions, scripts, or prompts → re-run failed cases
4. **Regression check**: Re-run full suite to ensure fixes don't break other cases
5. **Expand**: Add edge cases discovered during iteration
6. **Document**: Record what changes improved scores and why
