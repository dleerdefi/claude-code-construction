# Quickstart: Your First 5 Minutes

## What This Is

Construction skills for Claude Code that let you navigate drawings, extract schedules, parse specs, tabulate bids, and generate subcontracts — all from your terminal or IDE.

**These skills work standalone** with any construction PDFs using Claude Code's built-in vision and PDF tools. No additional platform required. AgentCM integration is optional and makes skills faster with pre-indexed data.

## Prerequisites

- [Claude Code](https://claude.com/claude-code) installed (CLI, VS Code extension, or web)
- Python 3.10+ (on macOS, Apple's built-in `python3` is 3.9 — install a newer one from python.org or Homebrew)
- On Windows: [Git for Windows](https://git-scm.com/download/win) (run the commands below in Git Bash)

See the [README prerequisites](../README.md#prerequisites) for details per operating system.
- Construction project PDFs (drawings and/or specs)

## Install

```bash
# Clone into your Claude Code skills directory; Claude Code loads it as the "construction" plugin
git clone https://github.com/dleerdefi/claude-code-construction ~/.claude/skills/construction

# Run setup (creates the Python venv)
cd ~/.claude/skills/construction
./setup
```

Prefer the marketplace? Inside Claude Code run `/plugin marketplace add dleerdefi/claude-code-construction`, then `/plugin install construction@construction-skills`. See the [README](../README.md#setup) for per-project installs, and [Validating your install](VALIDATING.md) to check everything works.

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
3. Save the data to Excel (.xlsx) and CSV
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
3. Split into individual PDFs: `03 30 00 - CAST-IN-PLACE CONCRETE.pdf`, etc.
4. Create a spec index YAML

## Try It: Generate a Submittal Log

After splitting specs (or if specs are already individual PDFs):

```
/construction:submittal-log-generator
```

Claude will:
1. Read each spec section
2. Find the SUBMITTALS heading in Part 1
3. Parse every lettered submittal item
4. Generate an Excel register with trade vs. general tabs, status dropdowns, and date columns

## What Gets Created

Skills save deliverables in your project folder, where you can open them, and keep their working data in a hidden `.construction/skills/` folder:

```
your-project/
  drawings/                         # Your PDFs
    sheets/                         # Split sheet PDFs + sheet_index.yaml (sheet-splitter)
  Specification Sections/           # Split spec PDFs + spec_index.yaml (spec-splitter)
  Submittal_Log.xlsx                # Excel/Word deliverables (or in a matching folder, e.g. Submittals/)
  .construction/                    # Hidden on Mac/Linux; you don't need to open it
    skills/                         # Skills' working data: spec text, issue registry, progress
```

With [AgentCM](https://github.com/dleerdefi/AgentCM), `.construction/` also holds AgentCM's project data, and skills record their findings there.

## Running Evals

Want to verify the skills work? See [Running Evals](RUNNING_EVALS.md) for how to test against sample construction documents.

## Troubleshooting

See [Troubleshooting](TROUBLESHOOTING.md) for common issues and fixes.

## Available Skills

| Skill | What it does |
|-------|-------------|
| `/construction:project-setup` | Set up project: inventory files, classify documents, establish context |
| `/construction:sheet-splitter` | Split bound drawing set into individual sheet PDFs |
| `/construction:spec-splitter` | Split bound project manual into individual spec PDFs |
| `/construction:schedule-extractor` | Extract schedule data from drawings to Excel |
| `/construction:submittal-log-generator` | Extract submittal requirements from specs to Excel |
| `/construction:bid-tabulator` | Tabulate multiple subcontractor bids into comparison spreadsheet |
| `/construction:bid-evaluator` | Evaluate tabulated bids: scope gaps, risk scoring, recommendation |
| `/construction:code-researcher` | Deep research on building codes and jurisdiction requirements |
| `/construction:subcontract-writer` | Generate scope-specific subcontract from firm's template |
| `/construction:construction-guide` | Operating guide: data-access rules, drawing conventions, document precedence |

Drawing reading and construction domain conventions live in the `construction-guide` skill, which Claude loads automatically when you work with construction documents.
