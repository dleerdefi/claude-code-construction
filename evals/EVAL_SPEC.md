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
│   ├── project-onboarding/
│   │   ├── case_01.json
│   │   └── expected/
│   ├── sheet-index-builder/
│   │   ├── case_01.json
│   │   └── expected/
│   ├── schedule-extractor/
│   │   ├── case_01_door_schedule.json
│   │   ├── case_02_finish_schedule.json
│   │   └── expected/
│   ├── submittal-log-generator/
│   │   ├── case_01.json
│   │   └── expected/
│   ├── code-compliance-checker/
│   │   ├── case_01_egress.json
│   │   ├── case_02_ada.json
│   │   └── expected/
│   └── cross-reference-navigator/
│       ├── case_01.json
│       └── expected/
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

### P0: project-onboarding

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

### P0: sheet-index-builder

| Case | Input | Validates |
|---|---|---|
| 01 | 10 individual sheet PDFs with standard title blocks | Sheet number, title, scale, discipline extraction accuracy |
| 02 | Bound set (100+ page PDF) | Multi-page PDF handling, page-to-sheet mapping |
| 03 | Non-standard title blocks (different firms) | Robustness with varied title block formats |

**Key metrics:**
- Sheet number extraction accuracy (% exact match)
- Sheet title accuracy (fuzzy match, >90% character accuracy)
- Scale extraction accuracy
- Discipline classification accuracy

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

### P1: code-compliance-checker

| Case | Input | Validates |
|---|---|---|
| 01 | Floor plan — egress review | Occupant load calc, exit count, travel distance, corridor width |
| 02 | Floor plan — ADA review | Door clearances, accessible routes, restroom layout |
| 03 | Section/detail — fire rating review | Wall ratings, opening protectives, rated assembly continuity |

**Key metrics:**
- Code section citation accuracy (correct IBC/ADA section referenced)
- Finding validity (human review: true positive / false positive / missed)
- Jurisdiction identification (correct state/local code edition)
- Severity classification appropriateness

**Important:** Code compliance findings must be validated by a licensed professional. Eval measures whether the skill flags the right areas, not whether its determination is final.

### P2: cross-reference-navigator

| Case | Input | Validates |
|---|---|---|
| 01 | Follow 5 detail callouts from a floor plan | Target sheet/detail resolution accuracy |
| 02 | Batch resolve all references on one sheet | Completeness of reference detection |
| 03 | Follow a chain (plan → section → detail) | Multi-hop traversal |

**Key metrics:**
- Reference detection recall
- Target resolution accuracy (correct sheet + detail number)
- Chain traversal completeness

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

### For sheet index:
- Manually record sheet number, title, discipline, and scale for each sheet

### For code compliance:
- Have a licensed architect/PE review the drawings and note actual compliance issues
- Record code section references for each finding

### For quantity takeoff:
- Manually count the target items on each sheet
- Note the exact count and any ambiguous items

### For cross-references:
- Manually trace all callouts and record source → target mappings

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
