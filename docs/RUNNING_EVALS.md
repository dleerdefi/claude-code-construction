# Running Evals

The eval framework validates that skills produce correct outputs against real construction documents.

## Get Test Documents

Download the Holabird Academy project documents:

| Document | Download |
|----------|----------|
| Architectural & Structural Plans | [Download](https://share.google/974f3GuyBiVFifupM) |
| MEP Plans | [Download](https://share.google/5bvL5qZwufaLO4TDp) |
| Civil & Landscape Plans | [Download](https://share.google/MXeIT7TAyvz5d4jCy) |
| Project Manual (Specs Vol 1) | [Download](https://share.google/mawQzc0ckZDOeq0zp) |

Place downloaded files in the corresponding directories:
```
evals/test_docs/Holabird-Academy/
  01 - Drawings/
    Architectural & Structural/    ← place arch+struct PDFs here
    Civil & Landscape/             ← place civil PDFs here
    MEP/                           ← place MEP PDFs here
  02 - Specifications/             ← place project manual here
```

The remaining project files (RFIs, submittals, meeting minutes, etc.) are already included in the repo.

## List Available Evals

```bash
python evals/runners/run_suite.py --list
```

Shows all skills with eval cases, their priority, and case count.

## Run a Single Eval

```bash
python evals/runners/run_skill.py --case evals/cases/schedule-extractor/case_01_door_schedule.json
```

This will:
1. Execute the skill's extraction pipeline against the test document
2. Compare output against ground truth
3. Score each metric
4. Save all artifacts (Excel, CSV, YAML, PNGs) to `evals/results/`

## Run All Evals for a Skill

```bash
python evals/runners/run_suite.py --skill schedule-extractor
```

## Run All Evals

```bash
python evals/runners/run_suite.py --all
```

## View Results

Each eval run creates a timestamped directory in `evals/results/`:

```
evals/results/20260325_081037_schedule-extractor-01/
  extracted_data.csv      # Raw extraction output
  output.xlsx             # Excel file (the skill's deliverable)
  graph_entry.yaml        # Knowledge graph entry
  result.json             # Scores and metadata
```

## Score Results

Score a single result:
```bash
python evals/runners/score.py evals/results/20260325_081037_schedule-extractor-01/result.json
```

View all results:
```bash
python evals/runners/score.py --summary
```

## Understanding Scores

Each eval case has weighted metrics. The overall score is 0.0-1.0:

| Score | Grade | Meaning |
|-------|-------|---------|
| 0.9+ | Production-ready | Skill output matches ground truth with high accuracy |
| 0.7-0.9 | Useful | Output is valuable but may have some gaps |
| 0.5-0.7 | Needs iteration | Core functionality works but needs improvement |
| <0.5 | Rework needed | Significant issues with the skill's approach |

## Using Your Own Documents

You can run evals against your own construction documents:

1. Place your PDFs in a project directory
2. Create a case JSON file in `evals/cases/<skill>/` (copy an existing one as a template)
3. Update the `inputs.files` paths to point to your documents
4. Run the eval

Ground truth is optional — without it, the eval still produces output artifacts you can review manually.

## Eval Cases

| Case | Skill | What It Tests |
|------|-------|---------------|
| schedule-extractor-01 | schedule-extractor | Door schedule extraction (pdfplumber) |
| schedule-extractor-02 | schedule-extractor | Finish schedule extraction (pdfplumber + vision fallback) |
| project-onboarding-01 | project-onboarding | File classification across all document types |
| sheet-index-builder-01 | sheet-index-builder | Title block reading from 10 sheets |
| submittal-log-generator-01 | submittal-log-generator | Submittal extraction from specs (SUBMITTALS heading parsing) |
| cross-reference-navigator-01 | cross-reference-navigator | Tracing detail callouts between sheets |
| code-compliance-checker-01 | code-compliance-checker | IBC egress analysis |
| code-compliance-checker-02 | code-compliance-checker | ADA accessibility analysis |
