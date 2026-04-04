# Quickstart: Your First 5 Minutes

## What This Is

Construction skills for Claude Code that let you navigate drawings, extract schedules, parse specs, tabulate bids, and generate subcontracts — all from your terminal or IDE.

**These skills work standalone** with any construction PDFs using Claude Code's built-in vision and PDF tools. No additional platform required. AgentCM integration is optional and makes skills faster with pre-indexed data.

## Prerequisites

- [Claude Code](https://claude.com/claude-code) installed (CLI, VS Code extension, or web)
- Python 3.10+
- Construction project PDFs (drawings and/or specs)

## Install

```bash
# Clone into your Claude Code skills directory
git clone https://github.com/dleerdefi/claude-code-construction ~/.claude/skills/construction

# Run setup (creates Python venv, registers skills)
cd ~/.claude/skills/construction
./setup --global
```

Then add to your project's `CLAUDE.md`:
```
@~/.claude/skills/construction/.claude/skills/CLAUDE.md
```

## Try It: Index Your Project

Open Claude Code in a folder with construction documents and type:

```
/project-setup
```

Claude will:
1. Scan the directory for all PDFs, drawings, specs, and project files
2. Classify each file by type (Drawing, Specification, RFI, Submittal, etc.)
3. Detect operational mode (AgentCM vs. Flat File) and establish context
4. Report a summary of what was found

## Try It: Extract a Schedule

If you have a drawing sheet with a door, finish, or equipment schedule:

```
/schedule-extractor A-3.2
```

Claude will:
1. Open the PDF and locate the schedule table
2. Extract every row using pdfplumber (with vision fallback if table detection fails)
3. Save the data to Excel (.xlsx) and CSV
4. Report the extraction quality (row count, column count)

## Try It: Read a Drawing

Point Claude at any drawing sheet and ask about it — drawing reading is built into the core skills:

> "Read sheet A-1.1 and tell me what rooms are shown"

Claude will rasterize the sheet to a PNG and use vision to describe what's on it — room layouts, door tags, section cuts, detail callouts, and more.

## Try It: Split Your Specs

If you have a bound project manual (one large PDF with all spec sections):

```
/spec-splitter
```

Claude will:
1. Parse the Table of Contents
2. Find section boundaries in the PDF
3. Split into individual PDFs: `03 30 00 - CAST-IN-PLACE CONCRETE.pdf`, etc.
4. Create a spec index YAML

## Try It: Generate a Submittal Log

After splitting specs (or if specs are already individual PDFs):

```
/submittal-log-generator
```

Claude will:
1. Read each spec section
2. Find the SUBMITTALS heading in Part 1
3. Parse every lettered submittal item
4. Generate an Excel register with trade vs. general tabs, status dropdowns, and date columns

## What Gets Created

Skills save their work to a `.construction/` directory in your project:

```
your-project/
  .construction/
    index/
      sheet_index.yaml     # Drawing sheet catalog
    specs/
      spec_index.yaml      # Spec section catalog
    agent_findings/        # Structured findings from all skills
  drawings/                # Your PDFs
  specs/                   # Your specs (split or individual)
```

## Running Evals

Want to verify the skills work? See [Running Evals](RUNNING_EVALS.md) for how to test against sample construction documents.

## Troubleshooting

See [Troubleshooting](TROUBLESHOOTING.md) for common issues and fixes.

## Available Skills

| Skill | What it does |
|-------|-------------|
| `/project-setup` | Set up project: inventory files, classify documents, establish context |
| `/sheet-splitter` | Split bound drawing set into individual sheet PDFs |
| `/spec-splitter` | Split bound project manual into individual spec PDFs |
| `/schedule-extractor` | Extract schedule data from drawings to Excel |
| `/submittal-log-generator` | Extract submittal requirements from specs to Excel |
| `/bid-tabulator` | Tabulate multiple subcontractor bids into comparison spreadsheet |
| `/bid-evaluator` | Evaluate tabulated bids: scope gaps, risk scoring, recommendation |
| `/code-researcher` | Deep research on building codes and jurisdiction requirements |
| `/subcontract-writer` | Generate scope-specific subcontract from firm's template |

Drawing reading and construction domain conventions are built into the core skill set and apply automatically when you work with construction documents.
