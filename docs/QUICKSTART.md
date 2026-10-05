# Quickstart: Your First 5 Minutes

## What This Is

Construction skills for Claude Code that let you navigate drawings, extract schedules, parse specs, tabulate bids, and generate subcontracts — all from your terminal or IDE. See the [README](../README.md#skills) for the full list of skills.

**These skills work standalone** with any construction PDFs. They rasterize PDF pages with the plugin's own scripts and read the resulting images; they never read a PDF directly. No additional platform is required. AgentCM, a separate project-data tool, is optional; the skills work without it and use its pre-indexed data when it is present.

## Prerequisites

- [Claude Code](https://claude.ai/code) installed
- Python 3.10+ and, on Windows, [Git for Windows](https://git-scm.com/download/win) (run the commands in Git Bash). See the [README prerequisites](../README.md#prerequisites) for details per operating system.
- Construction project PDFs (drawings and/or specs)

## Install

Follow [Setup in the README](../README.md#setup), then check the install with [Validating your install](VALIDATING.md).

## Try It: Index Your Project

Open Claude Code in a folder with construction documents and type:

```
/construction:project-setup
```

Claude will:
1. Scan the directory for all PDFs, drawings, specs, and project files
2. Classify each file by type (Drawing, Specification, RFI, Submittal, etc.)
3. Detect operational mode (AgentCM vs. Flat File) and establish context
4. Report a summary of what was found

## Try It: Extract a Schedule

If you have a drawing sheet with a door, finish, or equipment schedule:

```
/construction:schedule-extractor A-3.2
```

Claude will:
1. Open the PDF and locate the schedule table
2. Extract every row using pdfplumber (with vision fallback if table detection fails)
3. Save the data to an Excel (.xlsx) workbook
4. Report the extraction quality (row count, column count)

## Try It: Read a Drawing

Point Claude at any drawing sheet and ask about it — drawing reading is built into the core skills:

> "Read sheet A-1.1 and tell me what rooms are shown"

Claude will rasterize the sheet to a PNG and use vision to describe what's on it — room layouts, door tags, section cuts, detail callouts, and more.

## Try It: Split Your Specs

If you have a bound project manual (one large PDF with all spec sections):

```
/construction:spec-splitter
```

Claude will:
1. Parse the Table of Contents
2. Find section boundaries in the PDF
3. Split into individual PDFs in a `Specification Sections/` folder (inside your specs folder): `03 30 00 - CAST-IN-PLACE CONCRETE.pdf`, etc.
4. Create a spec index YAML
5. Extract each section's text to `.construction/skills/spec_text/`, with a quality rating per section

## Try It: Generate a Submittal Log

Run this on a project with specs. If spec text has not been extracted yet, the skill runs spec-splitter itself first.

```
/construction:submittal-log-generator
```

Claude will:
1. Read the extracted text of each spec section
2. Find submittal requirements in Part 1 (the SUBMITTALS articles, quality assurance, closeout and similar articles) and in Parts 2 and 3 where a product or execution article calls for one
3. Score each item's confidence and flag uncertain ones
4. Generate `Submittal_Log.xlsx` with three sheets: "Submittal Log", "Summary" and "Extraction QA"

## What Gets Created

Skills save deliverables in your project folder, where you can open them, and keep their working data in a hidden `.construction/skills/` folder:

```
your-project/
  drawings/                         # Your PDFs
    sheets/                         # Split sheet PDFs + sheet_index.yaml (sheet-splitter)
  specs/Specification Sections/     # Split spec PDFs + spec_index.yaml (spec-splitter; goes in your specs folder)
  Submittal_Log.xlsx                # Excel/Word deliverables (or in a matching folder, e.g. Submittals/)
  .construction/                    # Hidden on Mac/Linux; you don't need to open it
    skills/                         # Skills' working data: spec text, issue registry, progress
```

In projects that use AgentCM (marked by `.construction/project.yaml`), `.construction/` also holds AgentCM's project data, and skills record their findings in `.construction/agent_findings/`.

## Running Evals

Want to verify the skills work? See [Running Evals](RUNNING_EVALS.md) for how to test against sample construction documents.

## Troubleshooting

See [Troubleshooting](TROUBLESHOOTING.md) for common issues and fixes.

For the full list of skills, see the [README skill table](../README.md#skills). Drawing reading and construction conventions live in the `construction-guide` skill, which Claude loads when you work with construction documents.
