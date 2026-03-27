# Quickstart: Your First 5 Minutes

## What This Is

Construction skills for Claude Code that let you navigate drawings, extract schedules, parse specs, and check code compliance — all from your terminal or IDE.

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
/project-onboarding
```

Claude will:
1. Scan the directory for all PDFs, drawings, specs, and project files
2. Classify each file by type (Drawing, Specification, RFI, Submittal, etc.)
3. Create a `.construction/` directory with a project context file
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

Point Claude at any drawing sheet:

```
/drawing-reader A-1.1
```

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
| `/project-onboarding` | Index and classify all project files |
| `/sheet-index-builder` | Build a drawing sheet index from title blocks |
| `/drawing-reader` | Read and interpret a specific drawing sheet |
| `/spec-splitter` | Split bound project manual into individual spec PDFs |
| `/spec-parser` | Parse a spec section and extract requirements |
| `/schedule-extractor` | Extract schedule data from drawings to Excel |
| `/submittal-log-generator` | Extract submittal requirements from specs to Excel |
| `/cross-reference-navigator` | Trace detail callouts and section references between sheets |
| `/code-compliance-checker` | Preliminary IBC/ADA code screening (not a PE substitute) |

`drawing-conventions` runs automatically in the background — it provides Claude with construction domain knowledge (sheet numbering, symbols, abbreviations) whenever you're working with drawings.
